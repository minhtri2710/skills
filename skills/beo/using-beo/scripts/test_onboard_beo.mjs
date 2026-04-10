import test from 'node:test'
import assert from 'node:assert/strict'
import os from 'node:os'
import path from 'node:path'
import { mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'

import { applyRepo, checkRepo } from './onboard_beo.mjs'

const execFileAsync = promisify(execFile)

async function makeRepo(name) {
  return mkdtemp(path.join(os.tmpdir(), `${name}-`))
}

test('applyRepo creates full onboarding on an empty repo', async () => {
  const repoRoot = await makeRepo('beo-onboard-empty')

  await applyRepo(repoRoot)

  const agents = await readFile(path.join(repoRoot, 'AGENTS.md'), 'utf8')
  const statusScript = await readFile(path.join(repoRoot, '.beads', 'beo_status.mjs'), 'utf8')
  const state = await readFile(path.join(repoRoot, '.beads', 'STATE.md'), 'utf8')
  const onboarding = JSON.parse(await readFile(path.join(repoRoot, '.beads', 'onboarding.json'), 'utf8'))

  assert.match(agents, /<!-- BEO:START -->/)
  assert.match(agents, /<!-- BEO:END -->/)
  assert.match(statusScript, /ONBOARDING_VERSION/)
  assert.match(state, /^# Beo State/m)
  assert.equal(onboarding.status, 'complete')
})

test('applyRepo appends the managed block to an existing AGENTS.md', async () => {
  const repoRoot = await makeRepo('beo-onboard-append')
  await writeFile(path.join(repoRoot, 'AGENTS.md'), '# Existing\n\nKeep this content.\n')

  await applyRepo(repoRoot)

  const agents = await readFile(path.join(repoRoot, 'AGENTS.md'), 'utf8')
  assert.match(agents, /# Existing/)
  assert.match(agents, /Keep this content\./)
  assert.match(agents, /<!-- BEO:START -->/)
  assert.match(agents, /<!-- BEO:END -->/)
})

test('applyRepo replaces a stale managed block and preserves surrounding content', async () => {
  const repoRoot = await makeRepo('beo-onboard-replace')
  await writeFile(
    path.join(repoRoot, 'AGENTS.md'),
    '# Before\n\n<!-- BEO:START -->\nold managed block\n<!-- BEO:END -->\n\n# After\n'
  )

  await applyRepo(repoRoot)

  const agents = await readFile(path.join(repoRoot, 'AGENTS.md'), 'utf8')
  assert.match(agents, /# Before/)
  assert.match(agents, /# After/)
  assert.doesNotMatch(agents, /old managed block/)
  assert.match(agents, /beo-router -> beo-exploring -> beo-planning -> beo-validating/)
})

test('checkRepo reports needs_onboarding for a fresh repo', async () => {
  const repoRoot = await makeRepo('beo-onboard-check')

  const result = await checkRepo(repoRoot)

  assert.equal(result.status, 'needs_onboarding')
  assert.ok(result.actions.includes('create_AGENTS.md'))
  assert.ok(result.actions.includes('create_.beads/onboarding.json'))
  assert.ok(result.actions.includes('create_.beads/beo_status.mjs'))
  assert.ok(result.actions.includes('create_.beads/artifacts/'))
  assert.ok(result.actions.includes('create_.beads/learnings/'))
})

test('checkRepo reports up_to_date for a fully onboarded repo', async () => {
  const repoRoot = await makeRepo('beo-onboard-current')
  await applyRepo(repoRoot)

  const result = await checkRepo(repoRoot)

  assert.equal(result.status, 'up_to_date')
  assert.deepEqual(result.actions, [])
})

test('applyRepo is idempotent when run twice', async () => {
  const repoRoot = await makeRepo('beo-onboard-idempotent')
  await applyRepo(repoRoot)

  const firstAgents = await readFile(path.join(repoRoot, 'AGENTS.md'), 'utf8')
  const firstOnboarding = await readFile(path.join(repoRoot, '.beads', 'onboarding.json'), 'utf8')

  await applyRepo(repoRoot)

  const secondAgents = await readFile(path.join(repoRoot, 'AGENTS.md'), 'utf8')
  const secondOnboarding = await readFile(path.join(repoRoot, '.beads', 'onboarding.json'), 'utf8')

  assert.equal(secondAgents, firstAgents)
  assert.equal(secondOnboarding, firstOnboarding)
})

test('installed beo_status script reports onboarding, state, and optional handoff', async () => {
  const repoRoot = await makeRepo('beo-status-report')
  await applyRepo(repoRoot)

  await writeFile(
    path.join(repoRoot, '.beads', 'HANDOFF.json'),
    `${JSON.stringify(
      {
        schema_version: 1,
        phase: 'executing',
        skill: 'beo-executing',
        feature: 'br-123',
        feature_name: 'status-check',
        next_action: 'Resume the worker loop',
        in_flight_beads: ['br-123.1'],
        timestamp: '2026-04-07T00:00:00.000Z',
      },
      null,
      2
    )}\n`,
    'utf8'
  )

  const { stdout } = await execFileAsync('node', ['.beads/beo_status.mjs', '--json'], {
    cwd: repoRoot,
  })
  const status = JSON.parse(stdout)

  assert.equal(status.onboarding.exists, true)
  assert.equal(status.onboarding.current, true)
  assert.equal(status.state_md.exists, true)
  assert.equal(status.state_md.phase, 'idle')
  assert.equal(status.handoff.exists, true)
  assert.equal(status.handoff.skill, 'beo-executing')
  assert.ok(status.next_reads.includes('AGENTS.md'))
  assert.ok(status.next_reads.includes('.beads/STATE.md'))
  assert.ok(status.next_reads.includes('.beads/HANDOFF.json'))
})
