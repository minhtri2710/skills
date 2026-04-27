# Coordination

## Agent Mail availability predicate

| Field | Rule | Writer |
| --- | --- | --- |
| `agent_mail_available` | required command/tool responds during onboarding check | beo-onboard cache |

## Dispatch / report command forms

| Purpose | Command form |
| --- | --- |
| dispatch worker | Agent Mail send with bead id, payload, reservation, return channel |
| worker report | Agent Mail reply with status, files, tests, blockers |
