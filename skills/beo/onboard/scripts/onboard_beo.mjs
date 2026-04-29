import path from 'node:path'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  mkdir,
  readFile,
  stat,
  writeFile,
} from 'node:fs/promises'

const MANAGED_START = '<!-- BEO:START -->'
const MANAGED_END = '<!-- BEO:END -->'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const SKILL_ROOT = path.resolve(__dirname, '..')
const TEMPLATE_PATH = path.join(SKILL_ROOT, 'assets', 'AGENTS.template.md')
const METADATA_PATH = path.join(SKILL_ROOT, 'assets', 'onboarding-metadata.json')
const ONBOARDING_METADATA = JSON.parse(readFileSync(METADATA_PATH, 'utf8'))
const VERSION = ONBOARDING_METADATA.version
const MANAGED_STARTUP_CONTRACT_VERSION = ONBOARDING_METADATA.managed_startup_contract_version

function parseArgs(argv) {
  const args = { repoRoot: '', apply: false }

  for (let i = 2; i < argv.length; i += 1) {
    const value = argv[i]
    if (value === '--repo-root') {
      args.repoRoot = argv[i + 1] || ''
      if (args.repoRoot.startsWith('--')) {
        throw new Error(`Invalid --repo-root value: "${args.repoRoot}" looks like a flag, not a path`)
      }
      i += 1
    } else if (value === '--apply') {
      args.apply = true
    }
  }

  if (!args.repoRoot) {
    throw new Error('Missing required --repo-root <path>')
  }

  return args
}

async function pathExists(targetPath) {
  try {
    await stat(targetPath)
    return true
  } catch (error) {
    if (error.code === 'ENOENT') return false
    throw error
  }
}

async function isDirectory(targetPath) {
  try {
    return (await stat(targetPath)).isDirectory()
  } catch (error) {
    if (error.code === 'ENOENT') return false
    throw error
  }
}

async function readTextIfExists(targetPath) {
  try {
    return await readFile(targetPath, 'utf8')
  } catch (error) {
    if (error.code === 'ENOENT') return null
    throw error
  }
}

async function readJsonIfExists(targetPath) {
  const content = await readTextIfExists(targetPath)
  if (!content) return null
  try {
    return JSON.parse(content)
  } catch {
    return null
  }
}

function normalizeManagedBlock(content) {
  if (!content) return null
  const match = content.match(/<!-- BEO:START -->[\s\S]*?<!-- BEO:END -->/)
  return match ? match[0].trim() : null
}

async function loadTemplate() {
  return readFile(TEMPLATE_PATH, 'utf8')
}

async function readOnboardingJson(repoRoot) {
  const onboardingPath = path.join(repoRoot, '.beads', 'onboarding.json')
  return readJsonIfExists(onboardingPath)
}

function statusScriptContent() {
  const templateBlock = normalizeManagedBlock(readFileSync(TEMPLATE_PATH, 'utf8'))
  return [
    "#!/usr/bin/env node",
    '',
    "import path from 'node:path'",
    "import { fileURLToPath } from 'node:url'",
    "import { readFileSync, existsSync } from 'node:fs'",
    '',
    'function readTextIfExists(targetPath) {',
    '  try {',
    "    return readFileSync(targetPath, 'utf8')",
    '  } catch {',
    '    return null',
    '  }',
    '}',
    '',
    'function readJsonIfExists(targetPath) {',
    '  const content = readTextIfExists(targetPath)',
    '  if (!content) return null',
    '  try {',
    '    return JSON.parse(content)',
    '  } catch {',
    '    return null',
    '  }',
    '}',
    '',
    normalizeManagedBlock.toString(),
    '',
    'function buildStatus(repoRoot) {',
    "  const agentsPath = path.join(repoRoot, 'AGENTS.md')",
    "  const beadsRoot = path.join(repoRoot, '.beads')",
    "  const onboardingPath = path.join(beadsRoot, 'onboarding.json')",
    "  const statePath = path.join(beadsRoot, 'STATE.json')",
    "  const handoffPath = path.join(beadsRoot, 'HANDOFF.json')",
    "  const criticalPatternsPath = path.join(beadsRoot, 'critical-patterns.md')",
    `  const expectedManagedBlock = ${JSON.stringify(templateBlock)}`,
    '',
    '  const agentsContent = readTextIfExists(agentsPath)',
    '  const managedBlock = normalizeManagedBlock(agentsContent)',
    '  const onboarding = readJsonIfExists(onboardingPath)',
    '  const stateJson = readJsonIfExists(statePath)',
    '  const handoffExists = existsSync(handoffPath)',
    '  const handoff = readJsonIfExists(handoffPath)',
    '',
    "  const requiredReads = ['.beads/STATE.json']",
    '  const conditionalReads = []',
    '  if (existsSync(criticalPatternsPath)) {',
    "    conditionalReads.push('.beads/critical-patterns.md')",
    '  }',
    '  if (handoffExists) {',
    "    conditionalReads.push('.beads/HANDOFF.json')",
    '  }',
    "  if (stateJson?.feature_slug) {",
    "    conditionalReads.push(`.beads/artifacts/${stateJson.feature_slug}/CONTEXT.md`)",
    "    conditionalReads.push(`.beads/artifacts/${stateJson.feature_slug}/PLAN.md`)",
    '  }',
    "  const managedBlockCurrent = Boolean(managedBlock) && managedBlock === expectedManagedBlock",
    "  const onboardingStatus = !onboarding ? 'missing' : onboarding.plugin === 'beo' && onboarding.plugin_version === " + JSON.stringify(VERSION) + " && onboarding.managed_startup_contract_version === " + JSON.stringify(MANAGED_STARTUP_CONTRACT_VERSION) + " && managedBlockCurrent ? 'up_to_date' : 'stale'",
    "  const approvalStatus = stateJson?.approval_ref ? 'referenced_unverified' : 'missing'",
    "  const handoffFreshness = handoffExists ? 'present_unverified' : 'none'",
    "  const handoffVerificationRequired = handoffExists",
    "  const dependencyPosture = {",
    "    source: 'onboarding_cache',",
    "    checked_at: onboarding?.tooling?.checked_at ?? onboarding?.agent_mail?.checked_at ?? null,",
    "    stale_possible: true,",
    "    beads_cli: onboarding?.tooling?.br ?? 'unknown',",
    "    beads_viewer: onboarding?.tooling?.bv ?? 'unknown',",
    "    agent_mail: onboarding?.agent_mail?.available === true ? 'available' : onboarding?.agent_mail?.available === false ? 'unavailable' : 'unknown',",
    '  }',
    '',
    '  return {',
    "    scout_schema_version: '1.0',",
    '    read_only: true,',
    '    onboarding: {',
    '      status: onboardingStatus,',
    '      live_check_required: true,',
    "      live_check_command: 'node <installed-beo-onboard-root>/scripts/onboard_beo.mjs --repo-root <absolute-repo-root>',",
    '    },',
    '    state: {',
    '      exists: Boolean(stateJson),',
    "      schema_version: stateJson?.schema_version ?? null,",
    "      current_owner: stateJson?.current_owner ?? null,",
    "      operator_view: stateJson?.operator_view ?? null,",
    '    },',
    '    handoff: {',
    '      exists: handoffExists,',
    '      freshness: handoffFreshness,',
    '      verification_required: handoffVerificationRequired,',
    '      auto_resume_allowed: false,',
    '    },',
    '    approval: {',
    '      status: approvalStatus,',
    "      approval_ref: stateJson?.approval_ref ?? null,",
    "      current_claim: false,",
    "      verification_required: Boolean(stateJson?.approval_ref),",
    '    },',
    '    readiness: {',
    "      value: stateJson?.readiness ?? null,",
    "      execution_mode: stateJson?.execution_mode ?? null,",
    '    },',
    '    reads: {',
    '      required: requiredReads,',
    '      conditional: conditionalReads,',
    '    },',
    '    dependencies: dependencyPosture,',
    '    orientation: {',
    "      state_owner: stateJson?.current_owner ?? null,",
    "      route_required_if: ['stale handoff', 'artifact contradiction', 'approval stale'],",
    "      hint: stateJson?.current_owner ? 'state owner is an orientation hint only; route from live artifacts when anything contradicts it' : 'owner missing; route from live artifacts',",
    '    },',
    '    warnings: [',
    "      ...(managedBlockCurrent ? [] : ['managed AGENTS.md block missing or stale']),",
    "      ...(dependencyPosture.stale_possible ? ['dependency posture is cached orientation; rerun live onboarding check for current capability'] : []),",
    '    ],',
    '  }',
    '}',
    '',
    'const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")',
    "const status = buildStatus(repoRoot)",
    "const args = new Set(process.argv.slice(2))",
    '',
    "if (args.has('--json')) {",
    "  process.stdout.write(`${JSON.stringify(status, null, 2)}\\n`)",
    '} else {',
    '  const lines = [',
    "    `read_only: ${status.read_only}` ,",
    "    `onboarding: ${status.onboarding.status}` ,",
    "    `state: ${status.state.current_owner ?? 'missing'}` ,",
    "    `handoff: ${status.handoff.exists ? status.handoff.freshness : 'none'}` ,",
    "    `reads.required: ${status.reads.required.join(', ') || 'none'}` ,",
    "    `reads.conditional: ${status.reads.conditional.join(', ') || 'none'}` ,",
    '  ]',
    "  process.stdout.write(`${lines.join('\\n')}\\n`)",
    '}',
    '',
  ].join('\n')
}

function buildActions(details) {
  const actions = []

  if (!details.agents_md_exists) {
    actions.push('create_AGENTS.md')
  } else if (!details.has_beo_managed_block) {
    actions.push('append_beo_managed_block')
  } else if (!details.managed_block_current) {
    actions.push('update_beo_managed_block')
  }

  const needsOnboardingRefresh =
    !details.onboarding_json_exists ||
    !details.plugin_match ||
    !details.plugin_version_match ||
    !details.managed_startup_contract_version_match

  if (needsOnboardingRefresh) {
    actions.push('create_.beads/onboarding.json')
  }

  if (
    !details.status_script_exists ||
    !details.plugin_match ||
    !details.plugin_version_match ||
    !details.managed_startup_contract_version_match ||
    !details.managed_block_current
  ) {
    actions.push('create_.beads/beo_status.mjs')
  }

  if (!details.state_json_exists) {
    actions.push('create_.beads/STATE.json')
  }
  // If STATE.json exists but is not parseable, do NOT auto-recreate it.
  // A malformed STATE.json may contain in-flight feature state. Leave the file
  // in place and let the human repair it manually.

  if (!details.critical_patterns_exists) actions.push('create_.beads/critical-patterns.md')
  if (!details.artifacts_dir_exists) actions.push('create_.beads/artifacts/')
  if (!details.learnings_dir_exists) actions.push('create_.beads/learnings/')

  return actions
}

function validateSentinels(content) {
  const startCount = (content.match(/<!-- BEO:START -->/g) || []).length
  const endCount = (content.match(/<!-- BEO:END -->/g) || []).length
  if (startCount !== endCount || startCount > 1) {
    throw new Error(
      `AGENTS.md has ${startCount} start and ${endCount} end sentinel(s). Expected 0 or exactly 1 of each. Manual repair required.`
    )
  }
  return { startCount, endCount }
}

/**
 * Inspect a repository and return the current onboarding status without writing any files.
 *
 * @param {string} repoRoot - Absolute or relative path to the repository root.
 * @returns {Promise<{status: 'up_to_date'|'needs_onboarding'|'invalid_state_json', actions: string[], details: object}>}
 *   status: 'up_to_date' — all managed surfaces are current
 *   status: 'needs_onboarding' — one or more actions required
 *   status: 'invalid_state_json' — STATE.json exists but is not parseable; manual repair required
 * @throws {Error} If `repoRoot` is not a directory, or if `AGENTS.md` contains mismatched
 *   or duplicate BEO sentinel comments (manual repair required before onboarding can proceed).
 */
export async function checkRepo(repoRoot) {
  const absoluteRepoRoot = path.resolve(repoRoot)

  if (!(await isDirectory(absoluteRepoRoot))) {
    throw new Error(`Repository root does not exist or is not a directory: ${absoluteRepoRoot}`)
  }

  const template = await loadTemplate()

  const agentsPath = path.join(absoluteRepoRoot, 'AGENTS.md')
  const onboardingPath = path.join(absoluteRepoRoot, '.beads', 'onboarding.json')
  const statusScriptPath = path.join(absoluteRepoRoot, '.beads', 'beo_status.mjs')
  const statePath = path.join(absoluteRepoRoot, '.beads', 'STATE.json')
  const criticalPatternsPath = path.join(absoluteRepoRoot, '.beads', 'critical-patterns.md')
  const artifactsDir = path.join(absoluteRepoRoot, '.beads', 'artifacts')
  const learningsDir = path.join(absoluteRepoRoot, '.beads', 'learnings')

  const agentsContent = await readTextIfExists(agentsPath)

  if (agentsContent) {
    validateSentinels(agentsContent)
  }

  const onboarding = await readOnboardingJson(absoluteRepoRoot)
  const stateFileExists = await pathExists(statePath)
  const stateJson = stateFileExists ? await readJsonIfExists(statePath) : null
  const templateBlock = normalizeManagedBlock(template)
  const currentBlock = agentsContent ? normalizeManagedBlock(agentsContent) : null

  const details = {
    agents_md_exists: Boolean(agentsContent),
    has_beo_managed_block: Boolean(currentBlock),
    managed_block_current: currentBlock === templateBlock,
    onboarding_json_exists: Boolean(onboarding),
    plugin_match: onboarding?.plugin === 'beo',
    plugin_version_match: onboarding?.plugin_version === VERSION,
    managed_startup_contract_version_match:
      onboarding?.managed_startup_contract_version === MANAGED_STARTUP_CONTRACT_VERSION,
    status_script_exists: await pathExists(statusScriptPath),
    state_json_exists: stateFileExists,
    state_json_parseable: stateFileExists && stateJson !== null,
    critical_patterns_exists: await pathExists(criticalPatternsPath),
    artifacts_dir_exists: await isDirectory(artifactsDir),
    learnings_dir_exists: await isDirectory(learningsDir),
  }

  const actions = buildActions(details)

  // A parseable STATE.json is required for safe downstream routing.
  // If the file exists but cannot be parsed, declare invalid_state_json so
  // beo-route stops and surfaces the problem rather than proceeding on corrupt state.
  if (details.state_json_exists && !details.state_json_parseable) {
    return {
      status: 'invalid_state_json',
      actions,
      details,
    }
  }

  return {
    status: actions.length === 0 ? 'up_to_date' : 'needs_onboarding',
    actions,
    details,
  }
}

function replaceManagedBlock(existingContent, template) {
  if (!existingContent) {
    return { content: `${template.trimEnd()}\n`, mode: 'created_from_template' }
  }

  const { startCount, endCount } = validateSentinels(existingContent)

  const hasStart = startCount === 1
  const hasEnd = endCount === 1

  if (hasStart && hasEnd) {
    const content = existingContent.replace(/<!-- BEO:START -->[\s\S]*?<!-- BEO:END -->/, template.trim())
    return { content: content.endsWith('\n') ? content : `${content}\n`, mode: 'updated_managed_block' }
  }

  const separator = existingContent.endsWith('\n') ? '\n' : '\n\n'
  const content = `${existingContent}${separator}${template.trim()}\n`
  return { content, mode: 'appended_managed_block' }
}

function defaultStateContent() {
  return JSON.stringify({
    schema_version: '1.1',
    operator_view: {
      feature: null,
      current_owner: 'beo-route',
      why_here: 'Managed onboarding created the initial live state and returned control to routing.',
      next_expected_owner: 'beo-route',
      blocked: false,
      human_action_needed: null,
      last_decision: 'Initial managed startup surfaces created; route the next owner from live state and artifacts.',
    },
    current_owner: 'beo-route',
    status: 'routing',
    evidence: {},
    updated_at: new Date().toISOString(),
  }, null, 2) + '\n'
}

function defaultCriticalPatternsContent() {
  return [
    '# Critical Patterns',
    '',
    'This file is not startup-critical unless `beo-references -> learning.md` records a repo-policy designation.',
    'Use targeted consultation by default.',
    '',
    'Approved cross-feature patterns belong here.',
    '',
  ].join('\n')
}

const AGENTS_ACTIONS = new Set([
  'create_AGENTS.md',
  'append_beo_managed_block',
  'update_beo_managed_block',
])

const VALID_AGENTS_MODES = new Set([
  'created_from_template',
  'updated_managed_block',
  'appended_managed_block',
  'retained_existing_managed_block',
])

function normalizeAgentsMode(value) {
  return VALID_AGENTS_MODES.has(value) ? value : 'retained_existing_managed_block'
}

export async function applyRepo(repoRoot) {
  const absoluteRepoRoot = path.resolve(repoRoot)

  const currentState = await checkRepo(absoluteRepoRoot)
  if (currentState.status === 'up_to_date') {
    return readOnboardingJson(absoluteRepoRoot)
  }
  if (currentState.status === 'invalid_state_json') {
    throw new Error(
      '.beads/STATE.json exists but contains invalid JSON. Manual repair is required before onboarding can proceed. ' +
      'Do not overwrite STATE.json automatically — it may contain in-flight feature state.'
    )
  }

  const currentOnboarding = await readOnboardingJson(absoluteRepoRoot)
  const actions = new Set(currentState.actions)
  const needsAgentsUpdate = currentState.actions.some((action) => AGENTS_ACTIONS.has(action))
  const agentsPath = path.join(absoluteRepoRoot, 'AGENTS.md')
  const beadsDir = path.join(absoluteRepoRoot, '.beads')
  const artifactsDir = path.join(beadsDir, 'artifacts')
  const learningsDir = path.join(beadsDir, 'learnings')
  const statusScriptPath = path.join(beadsDir, 'beo_status.mjs')
  const statePath = path.join(beadsDir, 'STATE.json')
  const criticalPatternsPath = path.join(beadsDir, 'critical-patterns.md')
  const onboardingPath = path.join(beadsDir, 'onboarding.json')
  let agentsMode = currentState.details.plugin_match
    ? normalizeAgentsMode(currentOnboarding?.managed_assets?.agents_mode)
    : 'retained_existing_managed_block'

  await mkdir(absoluteRepoRoot, { recursive: true })

  if (needsAgentsUpdate) {
    const template = await loadTemplate()
    const existingAgents = await readTextIfExists(agentsPath)
    const mergedAgents = replaceManagedBlock(existingAgents, template)
    await writeFile(agentsPath, mergedAgents.content, 'utf8')
    agentsMode = mergedAgents.mode
  }

  await mkdir(beadsDir, { recursive: true })
  if (actions.has('create_.beads/artifacts/')) {
    await mkdir(artifactsDir, { recursive: true })
  }
  if (actions.has('create_.beads/learnings/')) {
    await mkdir(learningsDir, { recursive: true })
  }
  if (actions.has('create_.beads/beo_status.mjs')) {
    await writeFile(statusScriptPath, statusScriptContent(), 'utf8')
  }

  if (actions.has('create_.beads/STATE.json')) {
    await writeFile(statePath, defaultStateContent(), 'utf8')
  }

  if (actions.has('create_.beads/critical-patterns.md')) {
    await writeFile(criticalPatternsPath, defaultCriticalPatternsContent(), 'utf8')
  }

  const onboarding = {
    schema_version: '1.0',
    plugin: 'beo',
    plugin_version: VERSION,
    managed_startup_contract_version: MANAGED_STARTUP_CONTRACT_VERSION,
    installed_at: new Date().toISOString(),
    status: 'complete',
    agent_mail: {
      available: null,
      checked_at: null,
      evidence: 'Set by onboarding/runtime capability check when Agent Mail probing is available.',
    },
    managed_assets: {
      agents_mode: agentsMode,
      status_script: '.beads/beo_status.mjs',
      state_json: '.beads/STATE.json',
      critical_patterns: '.beads/critical-patterns.md',
    },
  }

  await writeFile(onboardingPath, `${JSON.stringify(onboarding, null, 2)}\n`, 'utf8')
  return onboarding
}

async function main() {
  const { repoRoot, apply } = parseArgs(process.argv)
  const result = apply ? await applyRepo(repoRoot) : await checkRepo(repoRoot)
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch((error) => {
    process.stderr.write(`${error.message}\n`)
    process.exitCode = 1
  })
}
