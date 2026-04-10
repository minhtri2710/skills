import path from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  mkdir,
  readFile,
  stat,
  writeFile,
} from 'node:fs/promises'

const VERSION = '1.1.0'
const MANAGED_START = '<!-- BEO:START -->'
const MANAGED_END = '<!-- BEO:END -->'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const SKILL_ROOT = path.resolve(__dirname, '..')
const TEMPLATE_PATH = path.join(SKILL_ROOT, 'assets', 'AGENTS.template.md')

function parseArgs(argv) {
  const args = { repoRoot: '', apply: false }

  for (let i = 2; i < argv.length; i += 1) {
    const value = argv[i]
    if (value === '--repo-root') {
      args.repoRoot = argv[i + 1] || ''
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
  } catch {
    return false
  }
}

async function isDirectory(targetPath) {
  try {
    return (await stat(targetPath)).isDirectory()
  } catch {
    return false
  }
}

async function readTextIfExists(targetPath) {
  try {
    return await readFile(targetPath, 'utf8')
  } catch {
    return null
  }
}

function normalizeManagedBlock(content) {
  const match = content.match(/<!-- BEO:START -->[\s\S]*?<!-- BEO:END -->/)
  return match ? match[0].trim() : null
}

async function loadTemplate() {
  return readFile(TEMPLATE_PATH, 'utf8')
}

async function readOnboardingJson(repoRoot) {
  const onboardingPath = path.join(repoRoot, '.beads', 'onboarding.json')
  const content = await readTextIfExists(onboardingPath)
  if (!content) return null

  try {
    return JSON.parse(content)
  } catch {
    return null
  }
}

function statusScriptContent() {
  return [
    "#!/usr/bin/env node",
    '',
    "import path from 'node:path'",
    "import { fileURLToPath } from 'node:url'",
    "import { readFileSync, existsSync } from 'node:fs'",
    '',
    `const ONBOARDING_VERSION = '${VERSION}'`,
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
    'function extractStateField(content, label) {',
    "  const match = content?.match(new RegExp(`^- ${label}: (.+)$`, 'm'))",
    '  return match ? match[1] : null',
    '}',
    '',
    'function buildStatus(repoRoot) {',
    "  const beadsRoot = path.join(repoRoot, '.beads')",
    "  const onboardingPath = path.join(beadsRoot, 'onboarding.json')",
    "  const statePath = path.join(beadsRoot, 'STATE.md')",
    "  const handoffPath = path.join(beadsRoot, 'HANDOFF.json')",
    "  const criticalPatternsPath = path.join(beadsRoot, 'critical-patterns.md')",
    '',
    '  const onboarding = readJsonIfExists(onboardingPath)',
    '  const stateText = readTextIfExists(statePath)',
    '  const handoff = readJsonIfExists(handoffPath)',
    '',
    '  const nextReads = [\'AGENTS.md\']',
    "  if (existsSync(criticalPatternsPath)) nextReads.push('.beads/critical-patterns.md')",
    "  if (stateText) nextReads.push('.beads/STATE.md')",
    "  if (handoff) nextReads.push('.beads/HANDOFF.json')",
    '',
    '  return {',
    '    repo_root: repoRoot,',
    '    onboarding: {',
    '      exists: Boolean(onboarding),',
    `      current: onboarding?.plugin === 'beo' && onboarding?.plugin_version === ONBOARDING_VERSION,`,
    "      plugin: onboarding?.plugin ?? null,",
    "      plugin_version: onboarding?.plugin_version ?? null,",
    '    },',
    '    state_md: {',
    '      exists: Boolean(stateText),',
    "      phase: extractStateField(stateText, 'Phase') ?? null,",
    "      feature: extractStateField(stateText, 'Feature') ?? null,",
    "      next: extractStateField(stateText, 'Next') ?? null,",
    '    },',
    '    handoff: {',
    '      exists: Boolean(handoff),',
    "      skill: handoff?.skill ?? null,",
    "      next_action: handoff?.next_action ?? null,",
    "      feature: handoff?.feature ?? null,",
    "      feature_name: handoff?.feature_name ?? null,",
    "      timestamp: handoff?.timestamp ?? null,",
    '    },',
    '    critical_patterns: {',
    `      exists: existsSync(criticalPatternsPath),`,
    '    },',
    '    next_reads: nextReads,',
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
    '    `repo_root: ${status.repo_root}`,',
    "    `onboarding: ${status.onboarding.exists ? (status.onboarding.current ? 'current' : 'stale') : 'missing'}` ,",
    "    `state: ${status.state_md.exists ? (status.state_md.phase ?? 'present') : 'missing'}` ,",
    "    `handoff: ${status.handoff.exists ? (status.handoff.skill ?? 'present') : 'none'}` ,",
    "    `next_reads: ${status.next_reads.join(', ')}` ,",
    '  ]',
    "  process.stdout.write(`${lines.join('\\n')}\\n`)",
    '}',
    '',
  ].join('\n')
}

function buildActions(details, blockIsCurrent) {
  const actions = []

  if (!details.agents_md_exists) {
    actions.push('create_AGENTS.md')
  } else if (!details.has_beo_managed_block) {
    actions.push('append_beo_managed_block')
  } else if (!blockIsCurrent || !details.onboarding_version_match) {
    actions.push('update_beo_managed_block')
  }

  if (!details.onboarding_json_exists || !details.onboarding_version_match) {
    actions.push('create_.beads/onboarding.json')
  }
  if (!details.status_script_exists) actions.push('create_.beads/beo_status.mjs')
  if (!details.state_md_exists) actions.push('create_.beads/STATE.md')
  if (!details.critical_patterns_exists) actions.push('create_.beads/critical-patterns.md')
  if (!details.artifacts_dir_exists) actions.push('create_.beads/artifacts/')
  if (!details.learnings_dir_exists) actions.push('create_.beads/learnings/')

  return actions
}

export async function checkRepo(repoRoot) {
  const absoluteRepoRoot = path.resolve(repoRoot)
  const template = await loadTemplate()

  const agentsPath = path.join(absoluteRepoRoot, 'AGENTS.md')
  const onboardingPath = path.join(absoluteRepoRoot, '.beads', 'onboarding.json')
  const statusScriptPath = path.join(absoluteRepoRoot, '.beads', 'beo_status.mjs')
  const statePath = path.join(absoluteRepoRoot, '.beads', 'STATE.md')
  const criticalPatternsPath = path.join(absoluteRepoRoot, '.beads', 'critical-patterns.md')
  const artifactsDir = path.join(absoluteRepoRoot, '.beads', 'artifacts')
  const learningsDir = path.join(absoluteRepoRoot, '.beads', 'learnings')

  const agentsContent = await readTextIfExists(agentsPath)
  const onboarding = await readOnboardingJson(absoluteRepoRoot)
  const templateBlock = normalizeManagedBlock(template)
  const currentBlock = agentsContent ? normalizeManagedBlock(agentsContent) : null

  const details = {
      agents_md_exists: Boolean(agentsContent),
      has_beo_managed_block: Boolean(currentBlock),
      onboarding_json_exists: Boolean(onboarding),
      onboarding_version_match: onboarding?.plugin_version === VERSION,
      status_script_exists: await pathExists(statusScriptPath),
      state_md_exists: await pathExists(statePath),
      critical_patterns_exists: await pathExists(criticalPatternsPath),
      artifacts_dir_exists: await isDirectory(artifactsDir),
      learnings_dir_exists: await isDirectory(learningsDir),
    }

  const blockIsCurrent = currentBlock === templateBlock
  const actions = buildActions(details, blockIsCurrent)

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

  if (existingContent.includes(MANAGED_START) && existingContent.includes(MANAGED_END)) {
    const content = existingContent.replace(/<!-- BEO:START -->[\s\S]*?<!-- BEO:END -->/, template.trim())
    return { content: content.endsWith('\n') ? content : `${content}\n`, mode: 'updated_managed_block' }
  }

  const separator = existingContent.endsWith('\n') ? '\n' : '\n\n'
  const content = `${existingContent}${separator}${template.trim()}\n`
  return { content, mode: 'appended_managed_block' }
}

function defaultStateContent() {
  return [
    '# Beo State',
    '- Phase: idle',
    '- Feature: none',
    '- Tasks: none',
    '- Next: load beo-router',
    '',
  ].join('\n')
}

function defaultCriticalPatternsContent() {
  return [
    '# Critical Patterns',
    '',
    'Approved cross-feature patterns belong here.',
    '',
  ].join('\n')
}

export async function applyRepo(repoRoot) {
  const absoluteRepoRoot = path.resolve(repoRoot)
  const currentState = await checkRepo(absoluteRepoRoot)
  if (currentState.status === 'up_to_date') {
    return readOnboardingJson(absoluteRepoRoot)
  }

  const template = await loadTemplate()
  const agentsPath = path.join(absoluteRepoRoot, 'AGENTS.md')
  const beadsDir = path.join(absoluteRepoRoot, '.beads')
  const artifactsDir = path.join(beadsDir, 'artifacts')
  const learningsDir = path.join(beadsDir, 'learnings')
  const statusScriptPath = path.join(beadsDir, 'beo_status.mjs')
  const statePath = path.join(beadsDir, 'STATE.md')
  const criticalPatternsPath = path.join(beadsDir, 'critical-patterns.md')
  const onboardingPath = path.join(beadsDir, 'onboarding.json')

  await mkdir(absoluteRepoRoot, { recursive: true })

  const existingAgents = await readTextIfExists(agentsPath)
  const mergedAgents = replaceManagedBlock(existingAgents, template)
  await writeFile(agentsPath, mergedAgents.content, 'utf8')

    await mkdir(beadsDir, { recursive: true })
    await mkdir(artifactsDir, { recursive: true })
    await mkdir(learningsDir, { recursive: true })
    await writeFile(statusScriptPath, statusScriptContent(), 'utf8')

    if (!(await pathExists(statePath))) {
      await writeFile(statePath, defaultStateContent(), 'utf8')
  }

  if (!(await pathExists(criticalPatternsPath))) {
    await writeFile(criticalPatternsPath, defaultCriticalPatternsContent(), 'utf8')
  }

  const onboarding = {
    schema_version: '1.0',
    plugin: 'beo',
    plugin_version: VERSION,
    installed_at: new Date().toISOString(),
      status: 'complete',
      managed_assets: {
        agents_mode: mergedAgents.mode,
        status_script: '.beads/beo_status.mjs',
        state_md: '.beads/STATE.md',
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

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    process.stderr.write(`${error.message}\n`)
    process.exitCode = 1
  })
}
