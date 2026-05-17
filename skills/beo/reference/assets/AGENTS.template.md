<!-- BEO:MANAGED START -->
Authority: advisory only.

Start here:
<!-- beo:agents:start-cockpit -->
1. Operator cockpit: `beo-reference -> references/operator-cockpit.md`
2. Protocol core: `beo-reference -> references/protocol-core.md`
3. Current owner contract: active owner `SKILL.md`
4. Canonical transitions: `beo-reference -> registry/pipeline.json`

Startup:
1. Read `.beads/STATE.json` if present.
2. Load `FEATURE.json` and current required artifacts.
3. Resolve current owner from artifacts; STATE/HANDOFF are mirrors only.
4. Normal resume uses `beo-reference -> references/resume-resolution.md`.
5. Route is only for unsafe owner/feature identity repair.
6. New feature delivery starts through `beo-explore`.
7. Direct setup/usage requests use `beo-setup`.

Normal path:
`beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.

Runtime authority comes from current artifacts, loaded owner contract, canonical references, and pipeline.
<!-- BEO:MANAGED END -->
