import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, realpath, rename, unlink, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { basename, dirname, join, resolve, sep } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export const COMPACTION_THRESHOLD = 4;
export const STATE_VERSION = 1;
export const RUN_ID = "compaction-reinject-2026-09-21";

export interface CompactionState {
	version: 1;
	paneId: string;
	count: number;
	injectNext: boolean;
}

type LoadStateResult =
	| { kind: "missing" }
	| { kind: "valid"; state: CompactionState }
	| { kind: "invalid" }
	| { kind: "unavailable" };

const PANE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
const PROJECT_SLUG_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;

function currentHomeDir(): string {
	return process.env.HOME || homedir();
}

function isContained(parent: string, child: string): boolean {
	return child !== parent && child.startsWith(`${parent}${sep}`);
}

export function validatePaneId(value: unknown): value is string {
	return typeof value === "string" && PANE_ID_PATTERN.test(value) && value === value.trim();
}

function projectSlugFromPath(projectPath: string): string | null {
	const slug = basename(projectPath);
	return PROJECT_SLUG_PATTERN.test(slug) ? slug : null;
}

function paneDigest(paneId: string): string {
	return createHash("sha256").update(paneId, "utf8").digest("hex");
}

async function makeVerifiedStateRoot(homePath: string, lexicalRoot: string): Promise<string | null> {
	let existing = lexicalRoot;

	while (true) {
		try {
			const resolvedExisting = await realpath(existing);
			if (resolvedExisting !== homePath && !isContained(homePath, resolvedExisting)) return null;
			await mkdir(lexicalRoot, { recursive: true, mode: 0o700 });
			const resolvedRoot = await realpath(lexicalRoot);
			return isContained(homePath, resolvedRoot) ? resolvedRoot : null;
		} catch (error) {
			if (!isNotFound(error)) return null;
			const parent = dirname(existing);
			if (parent === existing) return null;
			existing = parent;
		}
	}
}

/**
 * Resolve and verify the only durable state location used by this extension.
 * The pane id is validated and only its SHA-256 digest becomes a filename.
 */
export async function stateFilePath(
	cwd: string,
	paneId: string,
	homeDir = currentHomeDir(),
): Promise<string | null> {
	if (!validatePaneId(paneId) || typeof cwd !== "string" || typeof homeDir !== "string") return null;

	try {
		const projectPath = await realpath(resolve(cwd));
		const homePath = await realpath(resolve(homeDir));
		const projectSlug = projectSlugFromPath(projectPath);
		if (!projectSlug) return null;

		const stateRoot = resolve(homePath, ".herdr", "projects", projectSlug, "runs", "coordination");
		const resolvedRoot = await makeVerifiedStateRoot(homePath, stateRoot);
		if (!resolvedRoot) return null;

		const target = resolve(resolvedRoot, `${paneDigest(paneId)}.json`);
		if (!isContained(resolvedRoot, target)) return null;

		try {
			const resolvedTarget = await realpath(target);
			if (!isContained(resolvedRoot, resolvedTarget)) return null;
		} catch (error) {
			if (!isNotFound(error)) return null;
		}

		return target;
	} catch {
		return null;
	}
}

function isNotFound(error: unknown): boolean {
	return (
		error instanceof Error &&
		"code" in error &&
		(error as { code?: unknown }).code === "ENOENT"
	);
}

function isStateRecord(value: unknown, paneId: string): value is CompactionState {
	if (value === null || typeof value !== "object") return false;
	const record = value as Record<string, unknown>;
	return (
		Object.keys(record).length === 4 &&
		record.version === STATE_VERSION &&
		record.paneId === paneId &&
		typeof record.count === "number" &&
		Number.isSafeInteger(record.count) &&
		record.count >= 0 &&
		typeof record.injectNext === "boolean"
	);
}

async function loadState(cwd: string, paneId: string, homeDir: string): Promise<LoadStateResult> {
	const file = await stateFilePath(cwd, paneId, homeDir);
	if (!file) return { kind: "unavailable" };

	let text: string;
	try {
		text = await readFile(file, "utf8");
	} catch (error) {
		if (isNotFound(error)) return { kind: "missing" };
		return { kind: "unavailable" };
	}

	try {
		const parsed: unknown = JSON.parse(text);
		return isStateRecord(parsed, paneId) ? { kind: "valid", state: parsed } : { kind: "invalid" };
	} catch {
		return { kind: "invalid" };
	}
}

async function saveState(
	cwd: string,
	paneId: string,
	homeDir: string,
	state: CompactionState,
): Promise<boolean> {
	if (!isStateRecord(state, paneId)) return false;
	const file = await stateFilePath(cwd, paneId, homeDir);
	if (!file) return false;

	const temporary = join(dirname(file), `.${basename(file)}.${randomUUID()}.tmp`);
	try {
		await writeFile(temporary, `${JSON.stringify(state)}\n`, {
			encoding: "utf8",
			flag: "wx",
			mode: 0o600,
		});
		await rename(temporary, file);
		return true;
	} catch {
		return false;
	} finally {
		await unlink(temporary).catch(() => undefined);
	}
}

async function recordCompaction(cwd: string, paneId: string, homeDir: string): Promise<void> {
	const loaded = await loadState(cwd, paneId, homeDir);
	if (loaded.kind === "invalid" || loaded.kind === "unavailable") return;

	const previous = loaded.kind === "valid"
		? loaded.state
		: { version: STATE_VERSION, paneId, count: 0, injectNext: false } satisfies CompactionState;
	if (previous.count === Number.MAX_SAFE_INTEGER) return;

	const count = previous.count + 1;
	await saveState(cwd, paneId, homeDir, {
		version: STATE_VERSION,
		paneId,
		count,
		injectNext: previous.injectNext || count % COMPACTION_THRESHOLD === 0,
	});
}

async function consumePending(cwd: string, paneId: string, homeDir: string): Promise<boolean> {
	const loaded = await loadState(cwd, paneId, homeDir);
	if (loaded.kind !== "valid" || !loaded.state.injectNext) return false;

	return saveState(cwd, paneId, homeDir, {
		...loaded.state,
		injectNext: false,
	});
}

function safeProjectSlug(cwd: string): string | null {
	return projectSlugFromPath(resolve(cwd));
}

export function buildReprimeBlock(cwd: string, homeDir = currentHomeDir()): string {
	const projectSlug = safeProjectSlug(cwd);
	if (!projectSlug) return "";

	const projectRoot = resolve(homeDir, ".herdr", "projects", projectSlug);
	const doctrineRoot = resolve(homeDir, ".agents", "skills", "herdr-delivery-workflow", "references");
	const runRoot = join(projectRoot, "runs", RUN_ID);
	const leadDoctrine = join(doctrineRoot, "lead.md");

	return [
		"<durable-compaction-reprime>",
		"A compaction threshold was reached. Re-read authoritative durable records before continuing; do not reconstruct record content from memory.",
		`- Context pack: ${join(projectRoot, "context-pack.md")}`,
		`- Gate ledger: ${join(projectRoot, "gates.md")}`,
		`- Supervisor notebook: ${join(projectRoot, "supervisor-notebook.md")}`,
		`- Current run record: ${join(runRoot, "intake-record.md")}`,
		`- Current run plan: ${join(runRoot, "plan.md")}`,
		`- Recovery doctrine: ${leadDoctrine}#seat-identity-and-continuity`,
		`- Delivery doctrine: ${leadDoctrine}#delivery-sequence`,
		`- Gate doctrine: ${leadDoctrine}#gates-and-ledger`,
		`- Supervisor handoff doctrine: ${join(doctrineRoot, "supervisor.md")}#handoff`,
		`- Closeout doctrine: ${join(doctrineRoot, "closeout.md")}#acceptance-custody`,
		"Reconcile those sources for the current phase before acting.",
		"</durable-compaction-reprime>",
	].join("\n");
}

export default function compactionReinject(pi: ExtensionAPI): void {
	// Pi 0.86.1's SessionStart:compact wording maps to session_before_compact.
	pi.on("session_before_compact", async (_event, ctx) => {
		const paneId = process.env.HERDR_PANE_ID;
		if (!validatePaneId(paneId)) return;
		await recordCompaction(ctx.cwd, paneId, currentHomeDir());
	});

	pi.on("before_agent_start", async (event, ctx) => {
		const paneId = process.env.HERDR_PANE_ID;
		if (!validatePaneId(paneId)) return;
		const homeDir = currentHomeDir();
		const block = buildReprimeBlock(ctx.cwd, homeDir);
		if (!block || !(await consumePending(ctx.cwd, paneId, homeDir))) return;
		return { systemPrompt: `${event.systemPrompt}\n\n${block}` };
	});
}
