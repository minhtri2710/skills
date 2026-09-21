import { mkdir, mkdtemp, readFile, readdir, realpath, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import compactionReinject, {
	COMPACTION_THRESHOLD,
	RUN_ID,
	STATE_VERSION,
	buildReprimeBlock,
	stateFilePath,
} from "./compaction-reinject.ts";

interface Handler {
	(event: Record<string, unknown>, ctx: { cwd: string }): Promise<unknown> | unknown;
}

interface TestPaths {
	root: string;
	cwd: string;
	home: string;
}

interface Harness {
	root: string;
	cwd: string;
	home: string;
	stateRoot: string;
	handlers: Map<string, Handler>;
	compact(): Promise<void>;
	beforeAgentStart(systemPrompt: string): Promise<unknown>;
}

async function makeTestPaths(): Promise<TestPaths> {
	const root = await mkdtemp(join(tmpdir(), "compaction-reinject-"));
	const cwd = join(root, "beo-skills");
	const home = join(root, "home");
	await mkdir(cwd);
	await mkdir(home);
	return { root, cwd, home };
}

async function makeHarness(paneId: string, paths?: TestPaths): Promise<Harness> {
	const { root, cwd, home } = paths ?? await makeTestPaths();

	const handlers = new Map<string, Handler>();
	const pi = {
		on(event: string, handler: Handler) {
			handlers.set(event, handler);
			return () => handlers.delete(event);
		},
	};
	const previousHome = process.env.HOME;
	process.env.HOME = home;
	compactionReinject(pi as never);
	if (previousHome === undefined) delete process.env.HOME;
	else process.env.HOME = previousHome;

	const stateRoot = join(home, ".herdr", "projects", "beo-skills", "runs", "coordination");
	const context = { cwd };
	return {
		root,
		cwd,
		home,
		stateRoot,
		handlers,
		compact: async () => {
			const previousHomeValue = process.env.HOME;
			const previousPane = process.env.HERDR_PANE_ID;
			process.env.HOME = home;
			process.env.HERDR_PANE_ID = paneId;
			try {
				await handlers.get("session_before_compact")?.({ type: "session_before_compact" }, context);
			} finally {
				if (previousHomeValue === undefined) delete process.env.HOME;
				else process.env.HOME = previousHomeValue;
				if (previousPane === undefined) delete process.env.HERDR_PANE_ID;
				else process.env.HERDR_PANE_ID = previousPane;
			}
		},
		beforeAgentStart: async (systemPrompt: string) => {
			const previousHomeValue = process.env.HOME;
			const previousPane = process.env.HERDR_PANE_ID;
			process.env.HOME = home;
			process.env.HERDR_PANE_ID = paneId;
			try {
				return await handlers.get("before_agent_start")?.({ systemPrompt }, context);
			} finally {
				if (previousHomeValue === undefined) delete process.env.HOME;
				else process.env.HOME = previousHomeValue;
				if (previousPane === undefined) delete process.env.HERDR_PANE_ID;
				else process.env.HERDR_PANE_ID = previousPane;
			}
		},
	};
}

async function dispose(harness: Harness): Promise<void> {
	await rm(harness.root, { recursive: true, force: true });
}

async function stateFor(harness: Harness, paneId: string): Promise<Record<string, unknown>> {
	const file = await stateFilePath(harness.cwd, paneId, harness.home);
	assert.ok(file);
	return JSON.parse(await readFile(file, "utf8")) as Record<string, unknown>;
}

async function stateFiles(harness: Harness): Promise<string[]> {
	return (await readdir(harness.stateRoot)).filter((name) => name.endsWith(".json")).sort();
}

test("uses the Pi 0.86.1 lifecycle seams and validates safe derived state paths", async () => {
	const harness = await makeHarness("seat-A:window-1");
	try {
		assert.equal(COMPACTION_THRESHOLD, 4);
		assert.equal(STATE_VERSION, 1);
		assert.match(buildReprimeBlock(harness.cwd, harness.home), /context-pack\.md/);

		const expectedDigest = createHash("sha256").update("seat-A:window-1").digest("hex");
		const file = await stateFilePath(harness.cwd, "seat-A:window-1", harness.home);
		assert.ok(file);
		assert.equal(await realpath(dirname(file)), await realpath(harness.stateRoot));
		assert.equal(file, join(await realpath(harness.stateRoot), `${expectedDigest}.json`));
		assert.ok(file.startsWith(`${await realpath(harness.stateRoot)}/`));
		assert.equal(file.includes("seat-A:window-1"), false);
		assert.equal(await stateFilePath(harness.cwd, "../other-seat", harness.home), null);
		assert.equal(await stateFilePath(harness.cwd, " seat-A", harness.home), null);
		assert.equal(await stateFilePath(harness.cwd, "", harness.home), null);
	} finally {
		await dispose(harness);
	}
});

test("counts durably per seat, has no early injection, and preserves the system prompt", async () => {
	const harness = await makeHarness("seat-A");
	try {
		for (let count = 1; count < COMPACTION_THRESHOLD; count += 1) {
			await harness.compact();
			assert.deepEqual(await harness.beforeAgentStart("BASE SYSTEM PROMPT"), undefined);
			assert.equal((await stateFor(harness, "seat-A")).count, count);
		}

		await harness.compact();
		const reloaded = await makeHarness("seat-A", { root: harness.root, cwd: harness.cwd, home: harness.home });
		const first = await reloaded.beforeAgentStart("BASE SYSTEM PROMPT");
		assert.ok(first && typeof first === "object");
		assert.equal((first as { systemPrompt: string }).systemPrompt.startsWith("BASE SYSTEM PROMPT"), true);
		assert.match((first as { systemPrompt: string }).systemPrompt, /<durable-compaction-reprime>/);
		assert.equal((await stateFor(reloaded, "seat-A")).injectNext, false);

		assert.equal(await reloaded.beforeAgentStart("BASE SYSTEM PROMPT"), undefined);
		assert.equal((await stateFor(reloaded, "seat-A")).count, COMPACTION_THRESHOLD);

		for (let count = COMPACTION_THRESHOLD + 1; count <= COMPACTION_THRESHOLD * 2; count += 1) {
			await reloaded.compact();
		}
		assert.equal((await stateFor(reloaded, "seat-A")).count, COMPACTION_THRESHOLD * 2);
		const second = await reloaded.beforeAgentStart("BASE SYSTEM PROMPT");
		assert.ok(second && typeof second === "object");
		assert.equal((second as { systemPrompt: string }).systemPrompt.startsWith("BASE SYSTEM PROMPT"), true);
		assert.equal((await stateFor(reloaded, "seat-A")).injectNext, false);
	} finally {
		await dispose(harness);
	}
});

test("isolates durable counts and state files between seats", async () => {
	const paths = await makeTestPaths();
	const seatA = await makeHarness("seat-A", paths);
	const seatB = await makeHarness("seat-B", paths);
	try {
		for (let i = 0; i < COMPACTION_THRESHOLD; i += 1) await seatA.compact();
		assert.equal((await stateFor(seatA, "seat-A")).count, COMPACTION_THRESHOLD);
		const injection = await seatA.beforeAgentStart("A SYSTEM");
		assert.ok(injection && typeof injection === "object");
		assert.equal(typeof (injection as { systemPrompt?: unknown }).systemPrompt, "string");
		assert.match((injection as { systemPrompt: string }).systemPrompt, /<durable-compaction-reprime>/);

		await seatB.compact();
		assert.equal((await stateFor(seatB, "seat-B")).count, 1);
		assert.equal(await seatB.beforeAgentStart("B SYSTEM"), undefined);
		const files = await stateFiles(seatA);
		assert.equal(files.length, 2);
		assert.equal(new Set(files).size, 2);
	} finally {
		await Promise.all([dispose(seatA), dispose(seatB)]);
	}
});

test("ignores an invalid pane id without creating state", async () => {
	const harness = await makeHarness("seat-A/unsafe");
	try {
		await harness.compact();
		assert.deepEqual(await readdir(harness.stateRoot).catch(() => []), []);
		assert.equal(await harness.beforeAgentStart("SYSTEM"), undefined);
	} finally {
		await dispose(harness);
	}
});

test("fails closed for malformed or mismatched state", async () => {
	const harness = await makeHarness("seat-A");
	try {
		const file = await stateFilePath(harness.cwd, "seat-A", harness.home);
		assert.ok(file);
		await writeFile(file, "not json\n");
		await harness.compact();
		assert.equal(await harness.beforeAgentStart("SYSTEM"), undefined);
		assert.equal(await readFile(file, "utf8"), "not json\n");

		await writeFile(file, JSON.stringify({
			version: STATE_VERSION,
			paneId: "seat-B",
			count: COMPACTION_THRESHOLD,
			injectNext: true,
		}) + "\n");
		assert.equal(await harness.beforeAgentStart("SYSTEM"), undefined);
		assert.match(await readFile(file, "utf8"), /seat-B/);
	} finally {
		await dispose(harness);
	}
});

test("rejects a derived target that resolves outside the coordination root", async () => {
	const harness = await makeHarness("seat-A");
	try {
		const file = await stateFilePath(harness.cwd, "seat-A", harness.home);
		assert.ok(file);
		const outside = join(harness.home, "outside-state.json");
		await writeFile(outside, "outside\n");
		await rm(file, { force: true });
		await symlink(outside, file);
		assert.equal(await stateFilePath(harness.cwd, "seat-A", harness.home), null);
		await harness.compact();
		assert.equal(await harness.beforeAgentStart("SYSTEM"), undefined);
		assert.equal(await readFile(outside, "utf8"), "outside\n");
	} finally {
		await dispose(harness);
	}
});

test("re-prime block points to durable coordination and current-phase doctrine sections", async () => {
	const harness = await makeHarness("seat-A");
	try {
		const block = buildReprimeBlock(harness.cwd, harness.home);
		for (const pointer of [
			"context-pack.md",
			"gates.md",
			"supervisor-notebook.md",
			`${RUN_ID}/intake-record.md`,
			`${RUN_ID}/plan.md`,
			"references/lead.md#seat-identity-and-continuity",
			"references/lead.md#delivery-sequence",
			"references/lead.md#gates-and-ledger",
			"references/supervisor.md#handoff",
			"references/closeout.md#acceptance-custody",
		]) {
			assert.match(block, new RegExp(pointer.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
		}
		assert.doesNotMatch(block, /mailbox|notebook.*content|gate.*content/i);
	} finally {
		await dispose(harness);
	}
});
