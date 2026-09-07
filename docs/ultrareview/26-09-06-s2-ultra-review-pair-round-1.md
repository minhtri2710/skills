# Ultra Review: s2-ultra-review-pair Round 1

Date: 26-09-06
Review name: s2-ultra-review-pair
Round: 1
Scope: skills/ultra-review and skills/ultra-review-receive at 038dc27: 2 SKILL.md, create_ultra_review_report.py, 2 agents/openai.yaml
Report path: docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1.md
Scouts: 10 logical, 10 returned, 0 revived
Scout model: `sonnet`; subagent kind `Explore`; coordinator runs Opus 5
Review brief: `skills/ultra-review-workspace/campaign-01/S2-BRIEF.md`, sha256 `bf8fa48164b2305293dac8b43c03e3fa3198263574f5e4b5eb05bca6d8a4e4a2`
Directives: 10 concerns G01-G10 across 10 scouts, not one each — scout-03 carried G03 and G08, scout-10 carried none (F046)
Mode: verification-only campaign; no source edit in this phase

Those five metadata lines below `Report path:` — Scouts, Scout model, Review brief, Directives, Mode
— are added by the coordinator; the script writes only the five above them, Date through Report path. F036 is the finding about why they had to be added by hand, and adding them here rather
than as a paragraph below the header is this report's answer to F036's S1 instance — the contract
names a "Metadata header" and does not enumerate its fields, so extending it is the least invented
placement available. That judgement is disclosed, not asserted as compliance.

**Severity scale, extended for this slice and disclosed.** S1 used: P1 a record already written is
false or a mandatory gate is unsatisfiable; P2 a rule cannot be executed as written or the instrument
cannot measure what it claims; P3 clarity, robustness, dead surface. S2 adds one clause to P1: **or a
mandatory gate is satisfiable without doing its work.** F001 and F002 are gates that fail open rather
than gates that cannot be met, and the S1 wording has no room for them. Whether any S1 finding moves
under the extended P1 was not re-examined here; that belongs to the Phase A ranking, not to this
report.

**Raw material.** 122 enumerated candidate rows: 4 coordinator (C-01 to C-04) and 118 scout —
scout-01 10, scout-02 13, scout-03 12, scout-04 16, scout-05 10, scout-06 8, scout-07 14, scout-08 12,
scout-09 8, scout-10 15. Plus 29 separately-listed scout-declared negatives (scout-01 2, scout-02 6,
scout-07 5, scout-08 4, scout-10 12). Every one of the 122 is carried into a finding below; none was filtered for
being speculative, low-confidence, duplicated, self-referential, or inconvenient to this run. The rows
themselves live in `skills/ultra-review-workspace/campaign-01/S2-CANDIDATES.md`, which is gitignored
custody and is itself F003.

**Findings pointing outside the declared Scope are marked `[out of Scope]`.** Nothing in either skill
requires that mark or forbids the findings — that absence is F026 — and this report applies the mark
to its own contents rather than waiting for the rule to exist.

## Prior Round Guard

Previous reports read:
- none. This is round 1 of `s2-ultra-review-pair`. `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md` exists but is a different review name and is not a prior round of this one — see F010, under which a differently-named future review could wrongly pick it up.

Scout-declared negative results, carried so a later round does not re-litigate them. These are the
scouts' own verdicts of "checked, no defect," not the coordinator's rejection of anyone's candidate;
every bug candidate is F-numbered below.

- Round 10 sorts after round 2 (`int()` and numeric sort, script `:36-37`). Two rounds on the same day number sequentially. `mkdir` and `write_text` encoding are correct on the normal path. The single-invocation overwrite refusal is clean and exits 3 with no silent clobber. All six documented arguments are accepted as named. (scout-02)
- The generated scaffold matches `SKILL.md`'s Report Shape exactly: every heading in order, the eight `F001` stub fields, and the closing sentence verbatim modulo path substitution. (scout-02, scout-10)
- Every CLI flag at `SKILL.md:95` resolves to an identically-named argparse argument; the script path at `:98` exists; the printed JSON at `:180` carries `report_path`; the TODO placeholders and the `No candidates reported.` string match the template verbatim; the five dispositions appear identically and in order in `receive/agents/openai.yaml:4`; `ultra-review/agents/openai.yaml:4`'s path template matches the generated pattern; "weak-foundation accommodation lens" resolves to a real named lens at `SKILL.md:80`. (scout-10)
- The `F001` ID scheme, the `P0`-`P3` and high/medium/low vocabularies, and all finding subfield names match across producer, script and consumer. (scout-01)
- `receive:36`'s audit-only base case is completely specified; `ultra-review:100-101`'s no-candidates base case is genuinely named; the script's `:160-162` overwrite refusal is a correctly owned, fully bounded terminating condition; neither `openai.yaml` contains any rule, loop or retry. (scout-08)
- `:36`'s "Verification does not imply write permission," `:47`'s bar on editing source for the four non-CONFIRMED dispositions, and `:55`'s bar on automatic staging or committing are each unambiguous in isolation. (scout-07)
- `agents/openai.yaml` is a repo-wide manifest convention (scout-05 5.9), structurally identical to `repo-refresh`'s, and declares no provider. (scout-05)
- `architecture-premise-audit`, `repo-refresh` and `beo-review` each carry an explicit self-exclusion (scout-09 9.7) and none collides with `ultra-review`'s trigger wording. (scout-09)
- Restart Recovery steps 3 and 5 are coherent at the ID-naming level (scout-04 4.16) and correctly forbid duplicate and overflow IDs; `:56` states the right intent. The naming level is fine; the liveness level is F015. (scout-04)

## Findings

### F001 [P1] The producer generates remediation authorization into every report, and the consumer's write gate can be satisfied by handing that text back

Severity: P1 | Confidence: high
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:100-102` = `skills/ultra-review/SKILL.md:129-133` vs `skills/ultra-review-receive/SKILL.md:34-36`
Evidence:
- Script `:102` appends, unconditionally and with no flag, no `--audit-only` and no branch: "Use $ultra-review-receive to verify `<report path>` and implement confirmed owner-clean fixes." `SKILL.md:131-133` mandates that exact string as the report's closing text. (scout-01 1.5, scout-07 7.1)
- `receive/SKILL.md:36` gates every source write on "apply a fix only when the current request explicitly authorizes remediation," and states "Verification does not imply write permission." The section of the artifact titled **Next Receive Prompt** is the text a caller pastes as the current request, and it already contains the authorizing language, produced by a script rather than by a principal weighing consequences.
- Two producer surfaces disagree about the safe wording. `receive/agents/openai.yaml:4` hedges — "implement **only explicitly authorized** owner-clean fixes," with the disposition vocabulary spelled out. The version actually written to disk has no qualifier. The safer wording is the one that never reaches the artifact. (scout-01 1.6)
- `receive:36`'s gate references two inputs it never defines: "the caller's writable scope," which appears nowhere else and is not among Required Input at `:12`, and "the current request," which is never required to have a human principal. The second is what the generated prompt exploits. (scout-07 7.13)
- The skill offers no conditional form of the closing sentence, so a caller who was granted review and not remediation cannot both comply with `:131-133` and describe their grant honestly. (scout-10 10.12)
- Countervailing, kept: the closing block interpolates only `report_path` and no scout-supplied content, so a scout cannot inject text into it at scaffold time. The guarantee is prompt-level, not structural. (scout-06 6.5)
- **First-party, live instance.** The S1 report of this same campaign, `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md:802-810`, does not carry the mandated sentence. Its coordinator replaced it with "**Verification only.** The Human granted a review of the project's skills, not remediation." Scout-10 proved the alteration byte-for-byte against this report's own untouched scaffold, produced by the same script minutes earlier. Three facts stand together and none may be dropped: the canned prompt is a defect; the substitution was correct on the merits, because inviting fixes would have misstated the Human's grant; and the substitution was an undisclosed deviation from a contract-supplied fixed string that no rule authorized. A dated note has been added to S1 recording the third fact.
Contract violated:
- `SKILL.md:131-133` mandates fixed text that pre-supplies the authorization `receive:36` requires the caller to supply, which makes `:36` a gate that a compliant producer satisfies on the caller's behalf.
Plausible failure mode:
- A user pastes the report's own closing line, unedited, as the receive invocation. `receive:36` reads "the current request" — that line — finds the words "implement confirmed owner-clean fixes," and treats the write gate as passed. Every CONFIRMED finding in a ten-scout report becomes writable without any principal having decided to authorize a single edit. The `allow_implicit_invocation: false` flag on receive (F042) blocks automatic chaining but not a human paste.
Durable solution hypothesis:
- Make the closing sentence conditional on an explicit producer-side mode: a verification-only run emits a closing line that names the report and asks for dispositions and nothing else, and a remediation-authorized run emits the current text. Independently, `receive:36` should require the authorization to be identifiable as coming from a principal rather than from the artifact under review, and should define "the caller's writable scope" as a Required Input at `:12`.
Disconfirming check:
- Read-only. `sed -n '95,133p' skills/ultra-review/SKILL.md`, `sed -n '96,104p' skills/ultra-review/scripts/create_ultra_review_report.py`, `sed -n '30,40p' skills/ultra-review-receive/SKILL.md`, and `sed -n '1,6p' skills/ultra-review-receive/agents/openai.yaml`. The finding is false if any of them carries a conditional, a mode flag, or a requirement that the authorization originate outside the report.

### F002 [P1] Four parameters are required and validated at launch, and none of them reaches the artifact; `--mode`'s help text says it does

Severity: P1 | Confidence: high
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:43-55` signature vs `:57-103` body, help text at `:119-122`, call site at `:164-175`
Evidence:
- `mode`, `review_brief_sha256`, `scout_count` and `directive_count` are declared parameters of `markdown_template()` and are all passed in from `main()`. None appears in the returned f-string. Verified by grep: `mode` occurs only at `:49` and `:169`; the other three only at `:52-54` and `:172-174`. (C-01, scout-01 1.2/1.3/1.4, scout-02 2.5, scout-03 3.6, scout-04 4.2, scout-05 5.5, scout-06 6.4, scout-08 8.3, scout-10 10.1 — eight of ten scouts, 07 and 09 not among them, plus three coordinator candidates: C-01 here, C-02 and C-04 below)
- `--mode`'s own help text at `:121` reads "Review execution mode recorded in the artifact." That is false as written; the mode is not in the artifact and is not even in the stdout JSON. (scout-08 calls it affirmatively false)
- Corroborated against output rather than source: neither the S1 report nor this one contains the string "sha256" or "brief" anywhere. (scout-10)
- **The digest is validated against nothing.** No argument names the brief file, so the script cannot hash it and cannot compare. The coordinator proved this by accident on this very slice: the value passed at scaffold time was `bf8fa48164b2305393dac8b43c03e3fa3198263574f5e4b5eb05bca6d8a4e4a2`, one character off the real `...52 93...`, and the script accepted it. A required custody field that is unvalidated and unrecorded is worse than no field: it looks like proof and is a typed string. (C-02, first-party)
- Consequence at the consumer: `receive` cannot know which brief version produced the report it is verifying, nor in which mode. (C-04)
- Provenance consequence: the digest is the one field purpose-built for provenance, so a hand-edited report is indistinguishable from a generated one at the content level. (scout-06 6.4)
Contract violated:
- `SKILL.md:95`'s Artifact Contract presents all four as record-keeping inputs the caller must supply. The script's own docstring states it exists "so agents do not improvise artifact names or section layout." A required input that is discarded is neither validation nor record.
Plausible failure mode:
- A reader of a finished report — human or `ultra-review-receive` — cannot determine which brief the scouts were given, how many returned, or in which mode the review ran, and has no way to detect a wrong digest, because nothing was ever checked and nothing was ever written. A tampered or improvised report presents identically to a generated one.
Durable solution hypothesis:
- Interpolate all four into the metadata header, and take the brief **path** rather than a typed digest so the script hashes the file itself and compares. If any of the four is genuinely launch-time-only, delete the parameter and say so, and fix `--mode`'s help text to match whichever choice is made. A `--model` added later (F009) is eaten by the same plumbing unless this is fixed first.
Disconfirming check:
- Read-only. `awk 'NR>=56 && NR<=103' skills/ultra-review/scripts/create_ultra_review_report.py | grep -n 'mode\|sha256\|scout_count\|directive_count'` — zero hits is the defect. Then `grep -c 'sha256' docs/ultrareview/*.md`.

### F003 [P1] `SKILL.md:52` forbids the persistence that the skill's own scale and its own recovery protocol require

Severity: P1 | Confidence: high
Source pointer: `skills/ultra-review/SKILL.md:52`, against `:16`, `:12`, `:63`, `:106`, `:86-88`
Evidence:
- `:52` reads: "The coordinator may create exactly one report under `docs/ultrareview/` and no other workspace artifact." Read plainly this is a prohibition, not a silence. (scout-10 10.13)
- `:16` fixes the scout count at ten and `:107` requires every candidate preserved. Ten scouts at a dozen six-field write-ups each is 60 to 120 candidate blocks the coordinator must hold live with no permitted intermediate persistence. This slice returned 122. (scout-03 3.8)
- Consolidation is a single non-resumable act, and Restart Recovery covers subagent stoppage while saying nothing about the coordinator's own context ending mid-write. (scout-03 3.9)
- The Prior Round Guard is a real custody mechanism **across** rounds and there is no equivalent **within** one, because nothing is persisted until the report is written. (scout-03 3.10)
- "Capture every candidate" plus "read the whole report" is an unbounded-size contract on both sides of the handoff, with no size ceiling and no batching instruction. (scout-03 3.11)
- scout-03 recorded that it could not verify from inside the run whether its own coordinator would hit 3.3 or 3.9, and declined to soften the point for being self-referential. (3.12)
- **First-party breach, disclosed in full and not retroactively authorized.** This coordinator created seven artifacts where one is permitted. Enumerated, not counted: `INTAKE.md`, `S1-BRIEF.md`, `S2-BRIEF.md`, `S1-CANDIDATES.md`, `S2-CANDIDATES.md` under `skills/ultra-review-workspace/campaign-01/`, plus the two reports under `docs/ultrareview/`. Five of the seven are unauthorized by the skill as written. Scout-10 independently found the same five by `find`, and flagged a sixth directory, `delivery-01/`, as adjacent evidence of less certain provenance.
- **And the run is the evidence the rule is wrong.** This coordinator's context did run out mid-campaign. The candidates from scouts 01, 05, 06, 09 and 10 survived compaction for exactly one reason: they had been written to the file `:52` forbids. Under the rule as written that work would have been lost, and — per F002 and F008 — the resulting report would still have claimed ten scouts, with no field able to record the loss and no check able to detect it.
Contract violated:
- `:52` against `:16`, `:63` and `:107`. The skill mandates a scale, forbids the persistence that scale requires, provides no recovery for the failure the persistence prevents, and (`:12`, `:106`) bans the report section that would disclose it.
Plausible failure mode:
- A compliant coordinator loses its context after nine of ten scouts return, has nothing on disk but a TODO scaffold, and either abandons the review or reconstructs it from memory — which F002 and F008 guarantee will be indistinguishable, in the finished artifact, from a clean ten-scout run.
Durable solution hypothesis:
- Name a bounded exception: one gitignored raw-candidate custody file per review, under the workspace, explicitly permitted and explicitly excluded from the tracked artifact. That is the shape this campaign already needed and disclosed. The alternative — have the script accept staged raw candidates and fold them in — removes the out-of-band file but couples the script to the consolidation step.
Disconfirming check:
- Read-only. `sed -n '52p;12p;106p;16p;63p' skills/ultra-review/SKILL.md` and `find skills/ultra-review-workspace/campaign-01 -type f`. The finding is false if `:52` carries any exception clause for gitignored custody.

### F004 [P1] Restart Recovery consumes state that nothing in the skill persists

Severity: P1 | Confidence: high
Source pointer: `skills/ultra-review/SKILL.md:54-65`, against `:52`, `:12`, `:106`, `:33`
Evidence:
- Step 1 must freeze the roster, the concern allocation, the report path and the brief digest; step 2 must inventory per-scout status; `:65` requires working from persisted state. `:52` permits exactly one artifact, and `:12` and `:106` forbid that artifact from holding Raw Candidate Ledgers, Execution Receipts or "Scout preservation counters" — that is, exactly this bookkeeping. Recovery depends on state the same file forbids persisting anywhere. (scout-04 4.1, three-way intra-file contradiction; scout-08 8.2)
- Confirmed empirically against this run's own scaffold, which scout-04 read: 48 lines, all TODO, no roster, no concern map, no digest, no status. There is nothing to freeze into.
- Step 4 instructs reviving "on the model the original batch ran on." Since `557a137` the skill names no model, and per F002 the artifact records none. `grep -n model create_ultra_review_report.py` returns nothing. The datum the rule depends on has no source. (scout-04 4.8, scout-05 5.2)
- The recovery section never states how to treat the pre-restart artifact — evidence, scaffolding, or discardable. The only applicable instruction lives at `:98-102`, in a different section, and is never cross-referenced. A coordinator reading only the recovery section, which is the plausible case because that is where a recovery prompt points it, has no instruction at all. (scout-04 4.15)
- Recovery's own precondition is not guaranteed: nothing states **when** the script runs. This run created the scaffold before dispatch; that is an interpretation, not a requirement. Under the equally available reading, a mid-scout restart leaves step 1 with no report path to freeze. (scout-04 4.10)
- "Recovery prompt" and "bare continuation" each appear exactly once and are undefined, so the coordinator has no test to distinguish a recovery from a fresh invocation and can over- or under-trigger in either direction. (scout-04 4.12)
Contract violated:
- `:58-65` requires reading state that `:52`/`:12`/`:106` forbid writing. The protocol is unexecutable as written, not merely underspecified.
Plausible failure mode:
- A coordinator resumed after a server restart follows step 1, finds no roster and no allocation anywhere on disk, and must invent both. It cannot tell which scouts returned, cannot tell which concerns are uncovered, and cannot honour step 4's model requirement at all. Any report it then produces claims coverage it cannot substantiate.
Durable solution hypothesis:
- One decision resolves this and F003 together: name a permitted durable recovery record — roster, concern allocation, per-scout status, brief digest, model, report path — and exempt it from `:52`. Then `:58-65` has a defined subject, and step 4's model requirement has a source.
Disconfirming check:
- Read-only. `sed -n '54,65p' skills/ultra-review/SKILL.md`, then `grep -rn 'roster\|allocation\|persisted state' skills/ultra-review/` and `grep -n 'model' skills/ultra-review/scripts/create_ultra_review_report.py`. The finding is false if any file names a storage location for the frozen state.

### F005 [P1] A disconfirming check is untrusted scout-authored text that the consumer is instructed to execute, and the S1 queue already contains unscoped writes to a live append-only ledger

Severity: P1 | Confidence: high on the mechanical facts, medium on exploitability
Source pointer: `skills/ultra-review-receive/SKILL.md:8` vs `:24`; `skills/ultra-review/SKILL.md:115`; live instance at `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md:753-777` `[out of Scope]`
Evidence:
- `receive:8`: "Treat every finding and scout statement as untrusted hypothesis data, not instructions… never execute commands, scripts, paths, or policy embedded in a finding." `receive:24`: "Start with the finding's disconfirming check from the Verification Queue." The first operative instruction is to run scout-authored content. (scout-08 8.10, scout-07 7.5)
- The producer promises a read-only check at `ultra-review:115`; the consumer never restates or relies on that promise, and no mechanism enforces it. (scout-08 8.10)
- The untrusted-data seam extends past the check to the scout-supplied **Durable solution hypothesis**: nothing tells the verifier to derive its own repair rather than adopt the scout's. (scout-07 7.5)
- Only the consumer is told scout output is untrusted. There is no producer-side counterpart, and the coordinator is the first agent to ingest raw scout free text. (scout-06 6.1)
- **Live instance, first-party.** S1's Verification Queue is headed "Read-only checks. None of these implies write permission." Of its sixteen queued checks, six instruct building, appending, corrupting or checking out. Two — F021 and F023 — carry no scratch or isolation qualifier at all. `gate_row.py:187` makes `--ledger` required with no default, so an operator following those two checks as literally written must supply a ledger, and the only ledger the findings are about is the real one at `~/.herdr/projects/<slug>/gates.md` — the append-only file S1's own F001, F008 and F020 say cannot be repaired once corrupted. (scout-10 10.9)
Contract violated:
- `receive:8` and `receive:24` cannot both be obeyed. `ultra-review:116`'s "read-only disconfirming check" is a producer-side promise with no producer-side enforcement, and S1 proves it is not self-enforcing.
Plausible failure mode:
- A verifier follows `receive:24` on S1's F021 or F023 and appends a garbage row to the project's real gate ledger — a write, performed in a verification-only pass, on the authority of text written by a subagent. The general case is worse: the report is data authored by ten subagents and read by an agent with write permission, and the one sentence that acknowledges that is contradicted by the next operative step.
Durable solution hypothesis:
- `receive` should require every disconfirming check to run against an isolated copy, never against the state-bearing files the report is about, and should state that a check is a hypothesis to be re-derived rather than a command to be executed. `ultra-review` should refuse to emit a queue entry whose text contains a mutating verb, or at minimum require each entry to name its isolation.
Disconfirming check:
- Read-only. `sed -n '8p;24p' skills/ultra-review-receive/SKILL.md`, `sed -n '115,116p' skills/ultra-review/SKILL.md`, then `awk '/^## Verification Queue/,/^## Strongest Reason/' docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md | grep -n 'scratch\|Append\|corrupt\|checkout'`, and `grep -n 'required=True' skills/herdr-delivery-workflow/scripts/gate_row.py`. The finding is false if `:24` scopes execution to an isolated copy.

### F006 [P1] The S1 report's Verification Queue omits 12 of its 28 findings `[out of Scope]`

Severity: P1 | Confidence: high, exact grep-counted
Source pointer: `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md:751-780` vs its own `### F` headers
Evidence:
- `grep -c '^### F[0-9]'` returns 28. The Verification Queue holds 16 `F`-prefixed bullets — F001-F012, F015, F020, F021, F023 — plus one `C-01`. The twelve absent are F013, F014, F016, F017, F018, F019, F022, F024, F025, F026, F027, F028. Each except F027 (see F007) carries its own `Disconfirming check:` inside the Findings section that was simply never copied across. (scout-10 10.7)
Contract violated:
- `ultra-review/SKILL.md:116` requires a Verification Queue containing **every** finding and its read-only disconfirming check.
Plausible failure mode:
- `receive:24` names the queue as the mandated entry point to verification. For 43% of S1's findings that entry point does not exist, so a verifier either skips them, or improvises an entry from the finding body — which is the untrusted-content path F005 is about. The report is a record that presents itself as complete and is not.
Durable solution hypothesis:
- Derive the Verification Queue mechanically from the Findings section, one bullet per `### F\d+` block pulled from that block's own `Disconfirming check:` field, so omission becomes impossible. The generating script is the natural owner.
Disconfirming check:
- Read-only. `grep -c '^### F[0-9]' <s1>` against `awk '/^## Verification Queue/,/^## Strongest Reason/' <s1> | grep -c '^- \*\*F'`. Equal counts falsify the finding.

### F007 [P1] The S1 report's F027 is missing four of the seven mandatory subfields and bundles 17 unrelated defects under one disposition `[out of Scope]`

Severity: P1 | Confidence: high
Source pointer: `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md:666-712`
Evidence:
- F027 carries `Severity:`, `Source pointer:` and a 17-bullet `Evidence:` list spanning `lead-policy.md`, `herdr-cli.md`, `SKILL.md`, `project-config.md`, `peer-policy.md`, `human-gates-and-closeout.md` and `gate_row.py` — and then nothing. It is the only one of 28 findings with no `Contract violated:`, no `Plausible failure mode:`, no `Durable solution hypothesis:` and no `Disconfirming check:`. Counted: 28 finding headers against 27 occurrences of each of those four labels. (scout-10 10.8)
- Its 17 bullets share no root cause; they are leftovers.
Contract violated:
- `ultra-review/SKILL.md:108-115` makes all seven subfields mandatory per finding, and `:106` requires grouping by root cause. `receive:24`'s "assign exactly one disposition" cannot be honestly satisfied across 17 independent claims — the dead-guard bullet is likely CONFIRMED while the ambiguous-antecedent bullet may be DEFERRED, and one value cannot represent both.
Plausible failure mode:
- The verifier either invents per-bullet dispositions the report's structure does not support, or forces one disposition onto 17 claims and silently over- or under-confirms several. F027 is also the direct cause of one of F006's twelve queue gaps: there is no disconfirming check to copy.
Durable solution hypothesis:
- Split F027 into one finding per root cause, each with a complete seven-field block, as the other 27 already are. More durably: have the generating script or a check reject a Findings section in which any `### F` block lacks one of the seven labels.
Disconfirming check:
- Read-only. `grep -c '^### F[0-9]' <s1>` against `grep -c '^Contract violated:' <s1>` and the same for the other three labels; then `sed -n '666,712p' <s1>`.

### F008 [P1] The ten-scout claim is unmeasurable, and the report section that would disclose a shortfall is banned

Severity: P1 | Confidence: high
Source pointer: `skills/ultra-review/SKILL.md:16`, `:95`, `:106`, and `create_ultra_review_report.py:116-117`, `:147-149`
Evidence:
- `--scout-count 10` is a literal in the documented invocation, not a placeholder, and the script validates it only as `> 0` — never against findings, scout attributions, or anything measured. Per F002 it is then not rendered at all, so nothing downstream can cross-check it against the roster that actually reported. (scout-03 3.3, scout-08 8.12)
- The gate "wait for all ten before consolidating" exists only inside the restart-recovery branch at `:63`. The common path reaches Finding Consolidation with no stated count gate. (scout-03 3.4)
- Concern-ID traceability dies at consolidation: scouts are assigned concern IDs, directives require at least three scouts each, and no finding field records which concern produced it, so coverage can never be audited from the artifact. (scout-01 1.10)
- "At least three scouts per directive" against a hard ten, with no ceiling on directive count and the script bounding `--directive-count` only at `>= 0`, is arithmetically unsatisfiable above three directives. This slice ran ten concerns against ten scouts, and still not one each: scout-03 carried G03 and G08 and scout-10 carried no concern ID at all (F046). (scout-03 3.7)
Contract violated:
- `:16` states the count as a property of every run; nothing measures it, records it, or can detect its violation. `:106`'s ban on "Scout preservation counters" removes the one section that would have disclosed a shortfall.
Plausible failure mode:
- A run in which three scouts die reports as a ten-scout review, because the count is a launch-time literal and the artifact has no field for the returned count, no field for concern coverage, and a banned section for the discrepancy. F004's recovery gap makes this the expected outcome of a restart rather than an edge case.
Durable solution hypothesis:
- Record returned-scout count and per-concern coverage in the metadata header (the same plumbing fix as F002), tag each finding with the concern IDs that produced it, and either raise the "three scouts per directive" rule to a computed constraint against the scout count or delete it.
Disconfirming check:
- Read-only. `sed -n '16p;95p;106p' skills/ultra-review/SKILL.md`, `sed -n '116,117p;147,149p' skills/ultra-review/scripts/create_ultra_review_report.py`, and `grep -n 'concern' skills/ultra-review/SKILL.md | sed -n '1,20p'`. The finding is false if any finding subfield records a concern ID.

### F009 [P2] "One model, chosen by the caller" has no channel, no recorder, and no consumer

Severity: P2 | Confidence: high
Source pointer: `skills/ultra-review/SKILL.md:33`, with `:16`, `:41-51`, `:118-122`, `:106`
Evidence:
- `:33` requires every scout and sub-agent to run on one model "chosen by the caller: this skill names none." There is no channel for the choice, no timing, no owner, and no default. The review brief carries scope, digest and directives and has no model field, so nothing distinguishes a deliberate choice from a silent tool default. (scout-05 5.1)
- The Report Shape contract at `:118-122` omits model from the Metadata header, so the gap is contractual and not merely a script bug. (scout-05 5.6)
- The Scout Packet contract at `:41-51` has no item telling a scout what model a child must use, so the rule has no lever at the level it claims to bind. (scout-05 5.4)
- The rule binds "every scout and sub-agent" and not the coordinator, which does the judgement-heavy clustering where model bias matters most. This run is a live instance: scouts ran `sonnet`, the coordinator runs Opus 5. (scout-05 5.3)
- **The rule's stated rationale has no consumer.** `557a137` justified homogeneity by making cross-scout overlap meaningful, and no downstream rule consumes agreement as confidence: `:106` groups by root cause and discards multiplicity, and `receive:32` forbids confirming from scout count. Reported by scout-05 as a negative result that undercuts the rule it was assigned to audit. (5.8)
- scout-05 records that `557a137`'s intent — "No config key, no default, no example model" — is sound and deliberate, and that 5.1, 5.2, 5.5 and 5.6 are its untraced consequences rather than contradictions of it. (5.10)
- **First-party correction.** `INTAKE.md:92-94` claimed `SKILL.md:33` asks the caller to name the model "in each report's metadata." It does not; `:33` names no metadata and no recording obligation, and per F002 the metadata has no field for one. See F038; `INTAKE.md` has been corrected. (scout-10 10.11)
Contract violated:
- `:33` states a constraint on every scout and sub-agent with no mechanism to express, record, propagate, or verify it.
Plausible failure mode:
- A future run's ten scouts run on three different models and nothing notices, because there is no field to check against; and per F004, a restart cannot honour "revive on the model the original batch ran on" because that datum was never captured.
Durable solution hypothesis:
- Add `--model` to the script and a `Model:` line to the Metadata header (the same plumbing as F002), add a model item to the Scout Packet contract, and state whether the coordinator is bound by the homogeneity rule. Either give the homogeneity rationale a consumer or restate the rationale.
Disconfirming check:
- Read-only. `sed -n '33p;41,51p;118,122p' skills/ultra-review/SKILL.md` and `grep -rn 'model' skills/ultra-review/`. The finding is false if any of them names where the choice is recorded.

### F010 [P2] Round detection is keyed on the review name alone and is not anchored, so one review silently continues another

Severity: P2 | Confidence: high on the mechanism, medium on likelihood
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:18`, `:29-40`
Evidence:
- `ROUND_RE_TEMPLATE = r".*-{name}-round-(\d+)\.md$"` escapes regex metacharacters and never anchors the name to a path-component boundary. Two scouts reproduced this independently with isolated read-only `python3 -c` re-implementations: `review_name="fix"` captures round 3 from `26-01-01-auth-fix-round-3.md` (scout-02 2.2), and `name="foo"` matches `2026-01-01-bar-foo-round-1.md` (scout-10 10.2). The `glob(f"*-{review_name}-round-*.md")` prefilter agrees with the regex on the false match, so neither catches the other.
- The round/history dedup key is the review name only. `scope` and `review_brief_sha256` are known to the caller and never consulted, so two campaigns sharing a slug interleave rounds and the Prior Round Guard feeds one review's adjudicated findings to another. (scout-02 2.1)
- It also corrupts the round number that Restart Recovery freezes as "the report path." (scout-04 4.14)
- **First-party exposure.** This repository's own naming scheme is the precondition. Both live review names — `s1-herdr-delivery-workflow` and `s2-ultra-review-pair` — end in a natural shorter name, so a later review named `herdr-delivery-workflow` or `ultra-review-pair`, both plausible for the Phase B rounds this campaign anticipates, starts at round 2 and lists this campaign's round-1 report as a prior round of itself. (scout-10 10.14)
Contract violated:
- Path derivation and round increment. A review named `X` must not be treated as a continuation of a review named `Y-X`.
Plausible failure mode:
- A first-ever review silently starts at round 4, its Prior Round Guard lists another review's report as its own prior round, and any warnings drawn from it are nonsensical because they belong to a different review by a different owner.
Durable solution hypothesis:
- Match the full basename with an anchored pattern treating the name as a required whole segment — `re.fullmatch(rf"\d{{2}}-\d{{2}}-\d{{2}}-{re.escape(review_name)}-round-(\d+)", path.stem)` — and tighten the glob to match. Consider keying history on name plus scope so two campaigns sharing a slug do not interleave.
Disconfirming check:
- Read-only. `python3 -c` re-implementing the template against a synthetic filename list, in a scratch process that touches no file. Zero false matches falsifies the finding.

### F011 [P2] `slugify` collapses distinct review names onto one slug, and the resolved slug is never echoed before the round number is committed

Severity: P2 | Confidence: high, verified
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:21-26`, call site `:143`
Evidence:
- `"Auth Fix"`, `"AUTH-FIX"`, `"Auth/Fix"` and `"auth-fix"` all collapse to `auth-fix`, reproduced in an isolated read-only probe. (scout-02 2.3)
Contract violated:
- The caller believes they named a fresh review; the script folds them into an existing sequence and never shows the resolved slug before deriving the round.
Plausible failure mode:
- A caller runs "Auth Fix" believing it new, gets round 4 of someone else's `auth-fix`, and inherits its Prior Round Guard.
Durable solution hypothesis:
- Echo the resolved slug and the computed round in the stdout JSON before writing, and refuse when the slug already exists under a different declared scope.
Disconfirming check:
- Read-only. Re-implement `slugify` in a scratch `python3 -c` over the four inputs. Four distinct outputs falsifies the finding.

### F012 [P2] `slugify` is the only unguarded validation in `main()` and exits outside the script's own error vocabulary

Severity: P2 | Confidence: high, verified
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:143` against `:139-141`, `:144-146`, `:147-149`, `:150-153`, `:160-162`
Evidence:
- Every sibling check uses `print(..., file=sys.stderr); return N`. `slugify()` alone raises: `"日本語レビュー"`, `"!!!"` and `"   "` each produce a bare traceback and exit 1, outside the script's 2/3 exit vocabulary. (scout-02 2.4)
Contract violated:
- The script's own error convention, applied consistently at five other call sites.
Plausible failure mode:
- A non-Latin or punctuation-only review name gives a stack trace instead of a message, and a caller scripting against the documented exit codes sees an undocumented 1.
Durable solution hypothesis:
- Validate the slug at the same point as the other five and return the same class of error with the same exit code.
Disconfirming check:
- Read-only. `sed -n '21,26p;139,162p' skills/ultra-review/scripts/create_ultra_review_report.py`, then re-implement `slugify` over the three inputs in a scratch process.

### F013 [P2] Re-running the script during recovery produces a fresh round instead of refusing

Severity: P2 | Confidence: high
Source pointer: `skills/ultra-review/SKILL.md:56` vs `create_ultra_review_report.py:29-40`, `:160-162`
Evidence:
- `:56` states that a restart notice is "not permission to restart from scratch." `next_round()` always returns max+1, and the overwrite guard fires only on the already-incremented path, so a recovering coordinator that re-runs the script gets a clean new round file with a fresh TODO scaffold — the exact outcome `:56` disclaims — instead of a loud failure. Recovery never says not to re-run the script. (scout-04 4.3)
- The spurious round file is then permanent Prior Round Guard input for every later round, which must read it as a prior report though it holds no findings. (scout-04 4.13)
Contract violated:
- `:56`'s intent is defeated by the script's default behaviour, and nothing bridges the two.
Plausible failure mode:
- A recovery produces round 2 of a review whose round 1 is a half-written scaffold; both persist, both are read by round 3, and the artifact history claims two rounds where one review happened.
Durable solution hypothesis:
- Give the script an explicit "resume this round" mode that refuses to increment, and have `:58-65` name it. The overwrite guard should fire on the frozen round, not the incremented one.
Disconfirming check:
- Read-only. `sed -n '56p;54,65p' skills/ultra-review/SKILL.md` and `sed -n '29,40p;160,162p' skills/ultra-review/scripts/create_ultra_review_report.py`. The finding is false if any of them names a resume mode.

### F014 [P2] Consolidation is gated on "all ten complete" with no cap, timeout, or escape, and only one non-completion path is defined

Severity: P2 | Confidence: high
Source pointer: `skills/ultra-review/SKILL.md:54-65`, gate at `:63`
Evidence:
- `:63`'s "after all ten logical scouts complete" is the only gate, and there is no retry cap, no timeout budget, no authorized fallback below ten and no escape if one scout is permanently unrevivable. A scout that can never complete blocks the review forever or forces the coordinator to invent an unauthorized termination rule. (scout-04 4.6, scout-03 3.2, scout-08 8.1)
- The only defined non-completion path is a server restart. A scout that times out, errors, is silently killed, or returns a refusal has zero handling, and an empty return is indistinguishable from a thorough scout finding nothing. (scout-03 3.1)
- The trigger at `:56` names only the server-restart notice, while the runtime has three failure modes — fail, time out, killed — and two of them have no named recovery path. (scout-04 4.11)
- "Revive" is not executable under the stated runtime: a killed subagent's partial work has no resume mechanism. "Restart" is coherent; "revive" implies a capability that does not exist. (scout-04 4.9)
Contract violated:
- A rule with no base case and no terminating condition, gating the review's only irreversible step.
Plausible failure mode:
- Scout 7 dies in a way the harness does not report. The coordinator waits, restarts, waits again, and either never consolidates or terminates on a rule it made up — with no field in the artifact (F008) able to record which happened.
Durable solution hypothesis:
- State a revival cap and a per-scout timeout, define what an empty return means, and authorize consolidation below ten with the shortfall recorded in the metadata header. Replace "revive" with "relaunch" and say what happens to the dead scout's partial work.
Disconfirming check:
- Read-only. `sed -n '54,65p' skills/ultra-review/SKILL.md` and `grep -n 'cap\|timeout\|attempt' skills/ultra-review/SKILL.md`. Any named bound falsifies the finding.

### F015 [P2] "Logical scout" and "missing" are undefined, there is no tie-break, and a late report has no path into the artifact

Severity: P2 | Confidence: medium-high
Source pointer: `skills/ultra-review/SKILL.md:58-63`, against `:10`
Evidence:
- "Logical scout" versus launched agent is never defined and "missing" has no predicate. Step 4 revives missing scouts with no liveness test; step 5 forbids an eleventh ID but says nothing about two live agents under one ID; step 3's "preserve every completed report exactly once" supplies no tie-break when both return. (scout-04 4.4, scout-03 3.5)
- A late report from a scout already replaced has no path into the artifact once "consolidate once" has fired. `:10`'s never-filter rule is then violated by omission while the report still claims full ten-scout coverage. (scout-04 4.5)
Contract violated:
- `:62`'s "exactly once" asserts an outcome and names no mechanism; `:10` is violated by a case the protocol creates.
Plausible failure mode:
- Two agents return under scout ID 6 with different candidate sets. The coordinator picks one on no stated basis, or merges them and double-counts. Either way the artifact cannot say which happened.
Durable solution hypothesis:
- Define a logical scout as a concern allocation, define missing as no report by a stated deadline, make the first complete report for an ID authoritative, and state that a late report reopens consolidation for that ID rather than being dropped.
Disconfirming check:
- Read-only. `sed -n '58,63p' skills/ultra-review/SKILL.md` and `grep -n 'logical scout\|missing' skills/ultra-review/SKILL.md`.

### F016 [P2] Dispositions have no durable carrier the next round can read, so the producer/consumer loop does not close

Severity: P2 | Confidence: high
Source pointer: `skills/ultra-review/SKILL.md:86-88` vs `skills/ultra-review-receive/SKILL.md:47`, `:53`, and `create_ultra_review_report.py:29-40`
Evidence:
- Round 2 must incorporate round 1's confirmed fixes and rejected false positives. The disposition record is optional — `receive:47` says "if a durable receive record is requested" — the original report is normally never rewritten, and dispositions otherwise live only in the agent's chat reply. (scout-01 1.1)
- `grep -rn "receive.md"` across both `SKILL.md` files returns exactly one hit, at `receive:47`, and only as an output. Neither skill ever reads it. `next_round()`'s regex cannot match `<stem>-receive.md`, so it is excluded from `prior_reports` and never appears in the next round's "Previous reports read"; `SKILL.md:88` tells the guard to read earlier **reports**, not receive records. (scout-10 10.10)
- scout-08 verified the same regex fact from the opposite direction and recorded it as safe — the round detector will not mistake a receive record for a round. Both readings are true; the safety is what makes the invisibility total. (8.11)
Contract violated:
- A handoff artifact one skill writes and the other never promises to consume, inverted: the consumer writes it and the producer's own guard has no way to read it back.
Plausible failure mode:
- Round 2 re-surfaces findings already dispositioned DISPROVEN, with no warning to the fresh scout batch, because the one durable record of that disposition is structurally invisible to the mechanism built to prevent exactly this.
Durable solution hypothesis:
- Make the receive record mandatory rather than conditional, bring `<stem>-receive.md` into `next_round()`'s discovery scope alongside prior reports, and have `:88` instruct reading it when present.
Disconfirming check:
- Read-only. `grep -rn 'receive.md' skills/ultra-review/SKILL.md skills/ultra-review-receive/SKILL.md skills/ultra-review/scripts/create_ultra_review_report.py`. A second hit as an input falsifies the finding.

### F017 [P2] The receive record is an ungated, unshaped, un-versioned write

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review-receive/SKILL.md:47`, against `:36`
Evidence:
- The receive record is a tracked file under `docs/ultrareview/`, written on "if requested," with no authorization gate of its own. `:36`'s write gate governs source edits; nothing governs this one, so a write happens in a verification-only pass through an unguarded second trigger. (scout-07 7.12)
- It has no template, no required fields and no named consumer, and no round discipline, so a second pass silently clobbers the first's disposition history. (scout-08 8.11, scout-07 7.12)
Contract violated:
- `:36` establishes that verification does not imply write permission, and `:47` authorizes a write without referring to it.
Plausible failure mode:
- A verification-only pass writes a tracked file the caller did not authorize, and a later pass overwrites the first pass's dispositions with no version, no date and no diff.
Durable solution hypothesis:
- Give the record a template and required fields, put it under the same authorization gate as any other write, and give it round discipline so a second pass appends or increments rather than clobbers.
Disconfirming check:
- Read-only. `sed -n '36p;47p' skills/ultra-review-receive/SKILL.md` and `grep -n 'receive record' skills/ultra-review-receive/SKILL.md`.

### F018 [P2] "Assign exactly one disposition" contradicts the mandated CONFIRMED-to-BLOCKED transition

Severity: P2 | Confidence: high
Source pointer: `skills/ultra-review-receive/SKILL.md:24` vs `:42`
Evidence:
- `:24` requires exactly one disposition per finding. `:42` sits inside the already-dispositioned CONFIRMED branch and instructs a transition to BLOCKED. No legal-transition graph exists. (scout-07 7.2)
Contract violated:
- Either dispositions are frozen and `:42` is unexecutable, or they change freely and `:24` constrains nothing.
Plausible failure mode:
- A finding confirmed and then blocked carries whichever value the agent wrote last, and a reader cannot tell a never-confirmed BLOCKED from a confirmed-then-blocked one — the distinction F019 shows is already lost.
Durable solution hypothesis:
- State the legal transitions explicitly, or add a terminal-state field distinct from the initial disposition.
Disconfirming check:
- Read-only. `sed -n '24p;42p' skills/ultra-review-receive/SKILL.md`.

### F019 [P2] The five dispositions are not exhaustive

Severity: P2 | Confidence: high
Source pointer: `skills/ultra-review-receive/SKILL.md:26-30`
Evidence:
- True-but-no-in-scope-owner fails CONFIRMED by definition and is not DISPROVEN, so it collapses into BLOCKED — conflating "certain it is true, cannot act here" with "lack evidence to decide," which are opposite epistemic states under one label. Also unhomed: true only under an unreachable condition; and partly-true or confirmed-but-narrower, which forces either overclaiming CONFIRMED or losing a real defect. (scout-07 7.3)
Contract violated:
- A closed vocabulary that cannot express outcomes the workflow produces.
Plausible failure mode:
- A verifier certain a defect is real but unable to act marks it BLOCKED; a later reader treats BLOCKED as unresolved evidence and re-verifies from scratch, or drops it as unproven.
Durable solution hypothesis:
- Split BLOCKED into "confirmed, not actionable here" and "insufficient evidence," and add a narrowing note field so a partly-true finding can be confirmed at its true scope.
Disconfirming check:
- Read-only. `sed -n '26,30p' skills/ultra-review-receive/SKILL.md`.

### F020 [P2] DUPLICATE has no canonicalization rule, no cycle prevention, and no severity-conflict rule

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review-receive/SKILL.md:28`, with `:12` and `:47`
Evidence:
- Nothing names which of two duplicates is canonical, nothing prevents A-duplicates-B and B-duplicates-A, and nothing says what happens when duplicates carry different severities. Worst case: a finding-ID restriction to `F003` resolves DUPLICATE of an unselected `F007`; `:47` forbids modifying source for DUPLICATE, `F007` was never in scope, and the real defect goes unaddressed with no signal. (scout-07 7.6)
Contract violated:
- A disposition that discharges a finding by pointing at another, with no rule that the other is actually handled.
Plausible failure mode:
- Two real defects, both closed, neither fixed, and the completion table shows no gap.
Durable solution hypothesis:
- Require a DUPLICATE to name its canonical ID, require that ID to be in scope for the same pass, and reject a cycle.
Disconfirming check:
- Read-only. `sed -n '12p;28p;47p' skills/ultra-review-receive/SKILL.md`.

### F021 [P2] There is no post-remediation state and no severity in the completion row

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review-receive/SKILL.md:53`, `:55`, against `:26-30`
Evidence:
- `:55`'s "never claim a confirmed finding is fixed" presupposes a state the vocabulary does not contain. Post-remediation outcome is recoverable only from free-text columns, so a later pass cannot distinguish CONFIRMED-untouched from CONFIRMED-fixed-and-validated. (scout-07 7.7)
- The completion row has no severity field, so a verifier who finds the true severity differs from the scout's has nowhere structured to say so, and downstream prioritization runs on unverified scout severity forever. (scout-07 7.11)
Contract violated:
- `:53`'s completion record cannot express two outcomes the workflow produces.
Plausible failure mode:
- Phase B ranking runs on scout-assigned severities that verification already contradicted, and a second receive pass re-verifies findings that were fixed in the first.
Durable solution hypothesis:
- Add a verified-severity column and a remediation-outcome column to the completion table, distinct from the disposition.
Disconfirming check:
- Read-only. `sed -n '53,55p;26,30p' skills/ultra-review-receive/SKILL.md`.

### F022 [P2] The independent-review gate is stated twice with two different triggers, and there is no arbitration when it disagrees

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review-receive/SKILL.md:20` vs `:51`
Evidence:
- `:20` triggers independent review on "materially disputed or high-risk"; `:51` triggers it on an enumerated P0/P1/security list. The two are never cross-referenced, no reviewer identity is specified, and no rule covers a conflicting verdict. An agent can satisfy the narrow reading and skip review on a P0. (scout-08 8.8)
- When the required reviewer disagrees with the primary, one row carries one disposition, so whoever writes last silently overwrites the other — on a P0. (scout-07 7.9)
- The "one focused independent reviewer" has no model constraint and no recording requirement. Whether it should deliberately differ from the primary is unstated, which is itself the finding. (scout-05 5.7)
Contract violated:
- One gate with two triggers and no reconciliation is two gates, and the weaker one is satisfiable alone.
Plausible failure mode:
- A P0 finding is dispositioned by a single agent that read `:20` and judged it undisputed, and the record shows a completed pass.
Durable solution hypothesis:
- State the gate once, in one place, with one trigger; name who the reviewer must be and how it must differ; and require both verdicts to be recorded with an explicit arbitration rule when they differ.
Disconfirming check:
- Read-only. `sed -n '20p;51p' skills/ultra-review-receive/SKILL.md` and `grep -n 'independent' skills/ultra-review-receive/SKILL.md`.

### F023 [P2] "Escalate" names no recipient and presupposes a dispute the workflow cannot produce

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review-receive/SKILL.md:42`, `:20`
Evidence:
- `:42`'s "mark it `BLOCKED` and escalate" has no recipient, no mechanism and no completion condition; the agent can satisfy half the sentence with the table row and stop. scout-08 recorded it as the brief's literal example of the ownerless-rule class. (8.4)
- "Materially disputed" at `:20` presupposes a dispute in a workflow that describes a single verifier acting alone, so the clause may never fire at all. (scout-07 7.8)
Contract violated:
- A mandatory action with no owner and no completion test.
Plausible failure mode:
- Every BLOCKED finding is recorded and none is escalated, and the record is complete by its own terms.
Durable solution hypothesis:
- Name the recipient (the requesting principal), the mechanism (a line in the completion record plus a statement in the reply), and the completion condition. Define what produces a dispute given a single verifier, or delete the trigger in favour of `:51`'s list.
Disconfirming check:
- Read-only. `sed -n '20p;42p' skills/ultra-review-receive/SKILL.md` and `grep -n 'escalat' skills/ultra-review-receive/SKILL.md`.

### F024 [P2] There is no rule for a defect the verifier discovers, and no protocol for declaring a report void

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review-receive/SKILL.md:18`, `:32`, `:51`
Evidence:
- `:18` directs the verifier to reconstruct the finding's context, which is the activity most likely to surface a defect not in the report. Remediation is scoped to an existing CONFIRMED entry, so the verifier either fixes something never authorized or drops the observation. There is no third path. (scout-07 7.10)
- There is also no protocol for declaring a whole report void when verification shows it is unsound.
Contract violated:
- A workflow that induces a discovery it forbids recording.
Plausible failure mode:
- A verifier finds a P0 the scouts missed and has nowhere to put it, so it goes into prose that no downstream step reads.
Durable solution hypothesis:
- Permit the verifier to append new findings to the receive record with a distinct provenance marker, never to the report, and define a void disposition for the report as a whole.
Disconfirming check:
- Read-only. `sed -n '18p;32p;51p' skills/ultra-review-receive/SKILL.md`.

### F025 [P2] The consumer has no restart recovery, though it runs long write-capable passes

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review-receive/SKILL.md` whole file vs `skills/ultra-review/SKILL.md:54-65`
Evidence:
- The producer has a full Restart Recovery protocol. The consumer, which is at least as failure-prone and unlike the producer may hold write authority, has none: no rule on half-written source, no rule on whether a resumed pass re-verifies, no definition of "finished." The asymmetry is the finding. (scout-07 7.14)
Contract violated:
- The pair shares a failure mode and only one half addresses it.
Plausible failure mode:
- A receive pass dies after editing three of eleven confirmed findings. The resumed pass cannot tell which three, re-verifies nothing, and either repeats edits or skips them.
Durable solution hypothesis:
- Give receive the same protocol shape: freeze the report path and the finding list, record per-finding status durably as it goes, and define resumption against that record. F017's template is the natural place for it.
Disconfirming check:
- Read-only. `grep -n 'restart\|resume\|recovery' skills/ultra-review-receive/SKILL.md` — no hits is the defect.

### F026 [P2] Nothing bounds a finding's `file:line` to the declared Scope, and read scope is unbounded on both sides

Severity: P2 | Confidence: medium-high
Source pointer: `skills/ultra-review-receive/SKILL.md:14`, `:18`, `:26`, `:32`, `:36`; `skills/ultra-review/SKILL.md:35`, `:46-47`, `:52`
Evidence:
- Every scope check on the receive side is document-level or tied to the caller's writable scope; none asks whether an individual finding points inside the review. Under a broad remediation grant the only remaining gate says nothing about the review's scope. (scout-06 6.3)
- Scout **read** scope has no boundary at all: the runtime's tool-list distinction governs writes only, "inside scope" is prose, and `:47` actively pushes scouts past the visible diff. (scout-06 6.7)
- The verifier has no read-only restriction of any kind, unlike the scout side at `:52`, and `:32`'s naming of "compilation alone" as insufficient implies execution is available. `:8` bounds only finding-sourced content. Some bug classes are provable only by a side-effecting action and there is no procedure for that case. (scout-07 7.4)
- This report is a live instance in both directions: five of its findings point outside the declared Scope at the heading, and two more — F005 and F036 — are in-Scope findings whose source pointer cites out-of-Scope evidence and is tagged there; it marks all seven itself, because no rule required the mark; and three of its scouts read files outside the Scope line — the S1 artifact, `INTAKE.md`, `gate_row.py` — which produced F005, F006 and F007 and which nothing authorized or forbade.
Contract violated:
- `:14`'s scope preflight is document-level and is presented as the scope check.
Plausible failure mode:
- Under a remediation grant, a finding pointing at a file outside the review is fixed because nothing checks; conversely a real out-of-scope finding is silently dropped because nothing carries it.
Durable solution hypothesis:
- Require each finding to declare whether its `file:line` falls inside the report's Scope, have receive treat an out-of-scope finding as never-writable regardless of disposition, and state the verifier's execution boundary explicitly.
Disconfirming check:
- Read-only. `sed -n '14p;18p;26p;32p;36p' skills/ultra-review-receive/SKILL.md` and `sed -n '35p;46,47p;52p' skills/ultra-review/SKILL.md`.

### F027 [P2] There is no quoting or fencing convention for quoted source prose that is itself imperative agent text

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review/SKILL.md:108-115` and `create_ultra_review_report.py:77-91`
Evidence:
- Findings quote source prose, which in this project is imperative text addressed to agents, and it enters the report with no structural mark separating it from the report's own governing prose. (scout-06 6.2)
Contract violated:
- The finding schema has no fenced-quote requirement, while `receive:8` assumes finding content is distinguishable from instructions.
Plausible failure mode:
- A quoted rule from an audited skill reads, to the agent processing the report, as a rule addressed to it.
Durable solution hypothesis:
- Require quoted source in `Evidence:` to be fenced, and state that fenced content is never instructions.
Disconfirming check:
- Read-only. `sed -n '108,115p' skills/ultra-review/SKILL.md` and `sed -n '77,91p' skills/ultra-review/scripts/create_ultra_review_report.py`.

### F028 [P2] Workspace handling: no repo-root detection, a file passes the existence check, and the scope receive checks is never written

Severity: P2 | Confidence: high on the mechanisms, low on trigger frequency
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:108`, `:138-141`, `:192`; `skills/ultra-review-receive/SKILL.md:14`
Evidence:
- `--workspace` defaults to `.` with no repo-root detection and is only checked for existence, so running from `skills/ultra-review/` silently creates `skills/ultra-review/docs/ultrareview/…` — a valid write nobody looks at. (scout-02 2.6)
- `--workspace` pointing at a **file** passes `.exists()` and then `mkdir(parents=True)` raises `NotADirectoryError`, reproduced in an isolated pathlib probe. One-line fix: `or not workspace.is_dir()`. (scout-02 2.7)
- `receive:14` blocks when "scope does not match the requested workspace," and no `Workspace:` field is ever written — `--workspace` resolves paths and is discarded. The rule cannot be executed literally. (scout-01 1.9)
Contract violated:
- `receive:14` names a preflight against a field the producer never emits; the script accepts a workspace it cannot use.
Plausible failure mode:
- A report lands in a nested `docs/ultrareview/` nobody reads, and the consumer's only defence against it is a check whose input does not exist.
Durable solution hypothesis:
- Reject a non-directory workspace at `:139-141`, detect the repo root or require the flag explicitly, and write the resolved workspace into the metadata header so `receive:14` has an input.
Disconfirming check:
- Read-only. `sed -n '108p;138,141p;192p' skills/ultra-review/scripts/create_ultra_review_report.py` and `grep -n 'Workspace' docs/ultrareview/*.md` — no hits is the defect.

### F029 [P2] TOCTOU on the report write, with no lock and no single-writer enforcement

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:160-162` check vs `:191-193` write; `skills/ultra-review/SKILL.md:52`, `:54-65`
Evidence:
- `exists()` then `write_text` in truncate mode, no lock, no `O_EXCL`. Restart Recovery explicitly anticipates a resumed coordinator racing a stale one; one report is then lost with exit 0 returned to at least one caller. (scout-02 2.8)
- More broadly there is no ownership claim and no single-writer enforcement, so two coordinator instances both told at `:65` to inspect persisted state can both revive scouts and both consolidate into the same file. (scout-04 4.7)
Contract violated:
- The overwrite guard is the script's stated protection against clobbering and does not hold under the concurrency the skill's own recovery section anticipates.
Plausible failure mode:
- Two coordinators after a restart write the same path; the second truncates the first, and both report success.
Durable solution hypothesis:
- Create with `O_EXCL` so the guard and the write are one operation, and have the recovery protocol record an owner so a stale instance can detect it lost the claim.
Disconfirming check:
- Read-only. `sed -n '160,162p;191,193p' skills/ultra-review/scripts/create_ultra_review_report.py` — an `open(..., 'x')` or `O_EXCL` falsifies the finding.

### F030 [P2] `--scope` is interpolated unescaped into the block the consumer parses

Severity: P2 | Confidence: low-medium
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:62` template vs `:168`
Evidence:
- `--scope` is `.strip()`-ed and interpolated raw into the metadata header. A scope containing `\n\n## Findings` grows a spurious heading in the block `receive` parses. Caller-supplied, so a lower trust-boundary severity than F005's concern, but a real templating defect. (scout-02 2.12)
Contract violated:
- The script exists so agents do not improvise section layout, and a caller-supplied string can create a section.
Plausible failure mode:
- A pasted multi-line scope produces a report with two `## Findings` headings, and `receive` reads the wrong one.
Durable solution hypothesis:
- Reject or escape newlines and leading `#` in `--scope` at validation time.
Disconfirming check:
- Read-only. `sed -n '62p;168p' skills/ultra-review/scripts/create_ultra_review_report.py`.

### F031 [P2] The documented invocation uses `python`, which does not exist on the host this skill runs on, and no minimum interpreter is declared

Severity: P2 | Confidence: high on the host fact, low on the version fact
Source pointer: `skills/ultra-review/SKILL.md:95` vs `create_ultra_review_report.py:1`, `:171`, `:182`, `:193`
Evidence:
- `SKILL.md:95` invokes bare `python`; the shebang is `#!/usr/bin/env python3`. Measured on this exact frozen host: `which python` returns not-found and exits 1; `which python3` returns `/opt/homebrew/bin/python3` and exits 0. (scout-10 10.3, scout-02 2.10)
- `is_relative_to` at `:171` and `:182` requires Python 3.9 and `write_text(newline=)` at `:193` requires 3.10; the shebang is bare and there is no `requires-python`. Both scouts flagged their own confidence limit: the version facts come from documented history, not from testing an old interpreter, and this host's `python3` is modern. (scout-02 2.9, scout-10 10.4)
Contract violated:
- A rule that cannot be satisfied under the runtime the skill actually runs in — the documented command fails at the shell before any of the script's error handling engages.
Plausible failure mode:
- A coordinator copy-pastes `:95` literally and gets "command not found" on any modern macOS host with no `python` shim, or on a Linux host where `python` is Python 2.
Durable solution hypothesis:
- Change `:95` to `python3`, and state a minimum Python version in the script docstring.
Disconfirming check:
- Read-only. `which python; which python3; python3 --version`, and `sed -n '95p' skills/ultra-review/SKILL.md`.

### F032 [P2] The no-candidates base case leaves the template's `F001` skeleton unaccounted for, and "malformed" has no criterion

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review/SKILL.md:100-102` vs `create_ultra_review_report.py:77-90`, `:94`; `skills/ultra-review-receive/SKILL.md` block rule
Evidence:
- `:101` says to write "No candidates reported." and does not say whether the template's `F001` skeleton and its Verification Queue line are deleted or replaced. Receive then blocks on a "malformed" report with no criterion for whether a leftover TODO `F001` is malformed or a real finding. (scout-08 8.9)
- The seeded `F001 [P?] TODO` stub and the "No candidates reported" convention are prose-only and unenforced; receive's only handling for placeholder residue is the coarse whole-report block. (scout-01 1.8)
Contract violated:
- A base case that specifies the addition and not the removal, handed to a consumer whose rejection criterion is undefined.
Plausible failure mode:
- A zero-candidate report ships with a TODO `F001` still in it; receive either blocks a valid report or dispositions a placeholder.
Durable solution hypothesis:
- State explicitly that the `F001` skeleton and its queue line are deleted in the no-candidates case, and give receive a concrete malformed test — a residual `TODO` or `P?` token.
Disconfirming check:
- Read-only. `sed -n '100,102p' skills/ultra-review/SKILL.md`, `sed -n '70,94p' skills/ultra-review/scripts/create_ultra_review_report.py`, and `grep -n 'malformed' skills/ultra-review-receive/SKILL.md`.

### F033 [P2] "Narrowest adequate validation" and "relevant scouts" are thresholds with no comparator

Severity: P2 | Confidence: low-medium
Source pointer: `skills/ultra-review-receive/SKILL.md:45`; `skills/ultra-review/SKILL.md:88`
Evidence:
- `receive:45`'s "run the narrowest adequate validation, then expand only when boundaries require it" has no comparator; "adequate" is satisfiable by one passing unit test. (scout-08 8.5)
- `ultra-review:88`'s "give relevant scouts concise warnings" has no test for relevance and elides the subject. scout-08 noted the criterion is inferable from the concern map but never written, and called this a softer instance than a pure gap. (8.7)
Contract violated:
- Two thresholds stated as rules with nothing to measure against.
Plausible failure mode:
- A verifier runs one unit test, calls it adequate, and records a validated fix; a coordinator sends prior-round warnings to no one and satisfies `:88`.
Durable solution hypothesis:
- Define adequacy against the finding's own failure mode — the validation must exercise the condition the finding names — and define relevance against the concern map that already exists.
Disconfirming check:
- Read-only. `sed -n '45p' skills/ultra-review-receive/SKILL.md` and `sed -n '86,88p' skills/ultra-review/SKILL.md`.

### F034 [P2] Selection: the sibling `short_description` reverts to mechanism, and receive's third trigger admits a caller its body immediately blocks

Severity: P2 | Confidence: medium
Source pointer: `skills/ultra-review/agents/openai.yaml:3` vs `SKILL.md:3`; `skills/ultra-review-receive/SKILL.md:3` vs `:12`, `:14`
Evidence:
- The `SKILL.md` description is properly trigger-phrased; the sibling `short_description` reads "Artifact-based parallel review pipeline," containing none of the words a user would type. On any surface selecting by the short form, "run an ultra review" would not match. (scout-09 9.1)
- Receive's third trigger clause admits a caller who "asks to verify or triage ultra-review findings" with no path, and the body's first operative step blocks for lack of one. The description promises an entry the body refuses, and there is no fallback that locates the most recent report. (scout-09 9.2)
Contract violated:
- A description that does not select the skill for the cases it is for, and one that selects it for a case it immediately rejects.
Plausible failure mode:
- The skill is not selected when it should be, or is selected and dead-ends on its own preflight.
Durable solution hypothesis:
- Bring the `short_description` in line with the trigger-phrased `SKILL.md` description, and give receive a defined fallback: resolve the most recent report for the named review, or ask for the path.
Disconfirming check:
- Read-only. `sed -n '1,4p' skills/ultra-review/agents/openai.yaml`, `sed -n '3p' skills/ultra-review/SKILL.md`, `sed -n '3p;12p;14p' skills/ultra-review-receive/SKILL.md`.

### F035 [P2] The boundary between the two skills is a filename and heading convention, not a provenance check

Severity: P2 | Confidence: medium-high
Source pointer: `skills/ultra-review-receive/SKILL.md:14`
Evidence:
- Any markdown under `docs/ultrareview/` with the right headings and a well-formed round number is accepted, whether or not `ultra-review` produced it. (scout-09 9.3) With F002 the one field purpose-built for provenance never reaches the file, so there is nothing to check even if a check existed. (scout-06 6.4)
Contract violated:
- The consumer's admission test is a naming convention.
Plausible failure mode:
- A hand-written or hand-edited document is verified and, under a remediation grant, acted on as though ten scouts produced it.
Durable solution hypothesis:
- Write the brief digest and a generator marker into the artifact (the F002 fix), and have `:14` check them.
Disconfirming check:
- Read-only. `sed -n '14p' skills/ultra-review-receive/SKILL.md` and `grep -n 'sha256\|generated' docs/ultrareview/*.md` — no hits is the defect.

### F036 [P2] Run metadata has no contracted home, so every coordinator improvises a different shape

Severity: P2 | Confidence: medium-high on the structural fact
Source pointer: `skills/ultra-review/SKILL.md:118-127` against `:12`, `:106`; instances at `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md:9-13` `[out of Scope]` and this report's own header
Evidence:
- S1 carries an un-headed paragraph between the metadata fields and the first contracted heading, holding scout count, model, subagent kind, the read-only enforcement note and the raw-candidate pointer. `:120-127` names exactly six headings and no seventh slot. scout-10 declined to assert this meets the formal term: `:12` and `:106` name "Execution Receipt" and never define it, so the finding is stated as un-headed content outside the six contracted sections, not as a category match. (10.5)
- The cause is F002: the script gave that content nowhere to go. Two reports from the same skill therefore disagree in shape depending on whether their coordinator improvised — the outcome the script's own docstring says it exists to prevent. (C-03)
- This report is the second instance and chose differently, extending the Metadata header rather than adding a paragraph. Both choices are inventions; neither is contracted.
Contract violated:
- `:12` and `:106` forbid a category they never define, while `:118-127` provides no place for content the review genuinely needs to record.
Plausible failure mode:
- `receive:12` enumerates the sections it reads; improvised content is in none of them, so it is either ignored or misread as authoritative — S1's "read-only was charter-enforced… confirmed by tree comparison" could be taken as an assurance about the report's findings rather than a note about its scout batch.
Durable solution hypothesis:
- Define "Execution Receipt" precisely enough to check mechanically, and enumerate the Metadata header's permitted fields so run metadata has one contracted home. This is the same fix as F002 approached from the contract side.
Disconfirming check:
- Read-only. `sed -n '118,127p;12p;106p' skills/ultra-review/SKILL.md` and `sed -n '1,15p' docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md`.

### F037 [P2] The S1 report performs verification and rejection inside the producer's artifact `[out of Scope]`

Severity: P2 | Confidence: high
Source pointer: `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md:732-749`
Evidence:
- Its "Recorded and not carried as findings" section disposes of six items outside the `F001`-`F028` numbering: one scout claim declared retracted, citation integrity declared clean, "no project-identity leak" declared, two items declared out of scope, and a sixth queued under the non-`F` ID `C-01`. (scout-10 10.6)
Contract violated:
- `ultra-review/SKILL.md:12` reserves verification and rejection for `ultra-review-receive`; `:10` and `:107` forbid filtering a candidate for being speculative, low-confidence or hard to classify.
Plausible failure mode:
- `receive:12` reads `F`-numbered findings and has no defined path to disposition `C-01` or the other five, so a candidate the coordinator itself called speculative — exactly the category `:10` protects — is excluded from the dispositionable list.
Durable solution hypothesis:
- Give every candidate an `F` number, including ones the coordinator believes weak, and let receive assign DISPROVEN or BLOCKED. This report follows that rule: all 122 candidates are F-numbered below, and the only unnumbered material is the scouts' own declared negatives, carried in the Prior Round Guard.
Disconfirming check:
- Read-only. `grep -n '^### F' <s1>` and `sed -n '732,749p' <s1>` — confirms the six items carry no `F` prefix.

### F038 [P2] `INTAKE.md` overstates what `SKILL.md:33` requires `[out of Scope, first-party]`

Severity: P2 | Confidence: high
Source pointer: `skills/ultra-review-workspace/campaign-01/INTAKE.md:92-94` vs `skills/ultra-review/SKILL.md:33`
Evidence:
- `INTAKE.md` stated that naming the model "once here and in each report's metadata is what that line asks of the caller." `:33` reads in full: "run every scout and sub-agent on one model, chosen by the caller: this skill names none, and the overlap it depends on must come from assignment and search angle, never from a difference in model." It names no metadata and no recording obligation, and per F002 the metadata has no field for one. (scout-10 10.11)
Contract violated:
- A campaign record attributing a requirement to a skill text that does not contain it. The practice is defensible on its own merits; presenting it as a reading of `:33` is not.
Plausible failure mode:
- A later coordinator reading `INTAKE.md` believes the skill requires something it does not, or reading only `:33` never discovers the expectation existed.
Durable solution hypothesis:
- Correct `INTAKE.md` to disclose the practice as the coordinator's own addition. Done, dated, in place, as the earlier read-only correction was. The durable half is F009: the skill should say where the choice is recorded.
Disconfirming check:
- Read-only. `sed -n '33p' skills/ultra-review/SKILL.md` and `sed -n '90,96p' skills/ultra-review-workspace/campaign-01/INTAKE.md`.

### F039 [P3] The metadata block is called a "heading" by both skills and rendered as bare lines by the script

Severity: P3 | Confidence: low-medium
Source pointer: `skills/ultra-review/SKILL.md:120-122` and `skills/ultra-review-receive/SKILL.md:12` vs `create_ultra_review_report.py:57-64`
Evidence:
- Both files call the metadata block a "heading" to preserve and to read; the script renders five bare lines under the H1 with no heading at all. (scout-01 1.7)
Contract violated:
- A section named as a heading in two contracts and emitted as unheaded text in the implementation.
Plausible failure mode:
- A consumer parsing by heading finds no metadata section and treats it as absent.
Durable solution hypothesis:
- Either emit a real `## Metadata` heading or call it a metadata block in both contracts. F036 is the same seam from the content side.
Disconfirming check:
- Read-only. `sed -n '120,122p' skills/ultra-review/SKILL.md`, `sed -n '12p' skills/ultra-review-receive/SKILL.md`, `sed -n '57,64p' skills/ultra-review/scripts/create_ultra_review_report.py`.

### F040 [P3] `Evidence:` is free text, and receive's disallowed-basis list omits a finding's own claim to be verified

Severity: P3 | Confidence: low
Source pointer: `skills/ultra-review/SKILL.md:108-115` vs `skills/ultra-review-receive/SKILL.md:24-32`
Evidence:
- The schema has no Disposition field a scout could forge, which is a genuine structural separation. But `Evidence:` is free text, and `:32`'s list of disallowed bases does not name "a finding's own claim to be already verified." (scout-06 6.6)
Contract violated:
- The disallowed-basis list is enumerative and misses the case the free-text field enables.
Plausible failure mode:
- A finding whose `Evidence:` asserts "verified against the running system" is confirmed on that assertion.
Durable solution hypothesis:
- Add "the finding's own claim to have been verified" to `:32`'s disallowed list.
Disconfirming check:
- Read-only. `sed -n '24,32p' skills/ultra-review-receive/SKILL.md`.

### F041 [P3] The handoff exists only as printed suggestion text, with no status anyone owns

Severity: P3 | Confidence: medium
Source pointer: `skills/ultra-review/SKILL.md:129-133`, both `agents/openai.yaml:4`
Evidence:
- No queue, no status field, nothing owns confirming the receive step happened, so `docs/ultrareview/` accumulates reports with no visible actioned-or-not state. (scout-09 9.4)
Contract violated:
- A mandated handoff with no completion record. F016's missing durable carrier is the same gap seen from the round-2 side.
Plausible failure mode:
- Reports pile up and nobody can tell which were verified.
Durable solution hypothesis:
- Make the receive record mandatory (F016) and let its presence be the status.
Disconfirming check:
- Read-only. `grep -rn 'status\|queue' skills/ultra-review/SKILL.md skills/ultra-review-receive/SKILL.md`.

### F042 [P3] The `allow_implicit_invocation` asymmetry is invisible at the prose layer, and the review-to-receive loop's only terminator is the user

Severity: P3 | Confidence: low-medium
Source pointer: `skills/ultra-review-receive/agents/openai.yaml:6` vs `skills/ultra-review/agents/openai.yaml`; `skills/ultra-review-receive/SKILL.md:51`
Evidence:
- `allow_implicit_invocation: false` gates receive to explicit invocation; `ultra-review` carries no `policy` key. "Ultra review this and fix it" auto-selects the first half and silently cannot chain. (scout-09 9.5)
- scout-06 examined the same asymmetry and recorded it as **considered and not a bug**: the authors appear to have seen that a report's own boilerplate could auto-trigger the write-capable skill and disabled it, which is arguably correct since only receive has write authority. scout-07 listed it among its negatives as a correctly-placed guardrail. Both readings are carried. (6.8)
- `receive:51`'s "materially new stable snapshot" has no comparator and is the closest thing to a self-applying review-receive-review loop. **scout-08 downgraded its own candidate**: both `default_prompt`s frame invocation as user-initiated, so the user is the de facto terminator and this is an underspecified human heuristic rather than an unbounded machine loop. Reported anyway under the no-suppression rule. (8.6)
Contract violated:
- Sound design that a reader consulting the prose layer cannot see, and a loop whose terminator is implicit.
Plausible failure mode:
- A user expects "review and fix" to chain, and the second half never runs with no message saying why.
Durable solution hypothesis:
- State the explicit-invocation requirement in receive's `SKILL.md` prose, and name the user as the loop's terminator at `:51`.
Disconfirming check:
- Read-only. `cat skills/ultra-review/agents/openai.yaml skills/ultra-review-receive/agents/openai.yaml` and `grep -n 'implicit' skills/ultra-review-receive/SKILL.md` — a prose statement falsifies the finding.

### F043 [P3] Selection overlap with `test-proof-debt-audit`, and with the installed `code-review` skill's effort level literally named "ultra"

Severity: P3 | Confidence: low-medium
Source pointer: `skills/ultra-review/SKILL.md:79` vs `skills/test-proof-debt-audit/SKILL.md:3`; and, outside the frozen five, the installed `code-review` skill
Evidence:
- Soft overlap: "is this claim actually proven" could launch a ten-scout run instead of the cheap purpose-built audit. `test-proof-debt-audit` is well fenced and should win. (scout-09 9.6)
- The installed `code-review` skill offers an effort level named "ultra: deep multi-agent review in the cloud." "Do an ultra review of my diff" is lexically closer to that than to this skill, and the two produce incompatible artifacts — `ultra-review-receive` can only consume the scout-report shape. scout-09 flagged this as outside its scope rather than suppressing or overclaiming it. (9.8)
- **This is not hypothetical.** It is the same ambiguity this campaign's `INTAKE.md` disclosed to the Supervisor before S1 launched — that the Human's words could have meant the built-in `/code-review ultra` rather than these project skills — reached independently by a scout from the text alone. That raises it from a lexical observation to a selection hazard with a live instance.
Contract violated:
- A description that can be selected for a case another skill owns, and a name that collides with an installed effort level.
Plausible failure mode:
- A user asking for an "ultra review" of a diff gets a ten-scout artifact run, or asks for this skill and gets the cloud review, and in either direction the downstream consumer cannot read the artifact produced.
Durable solution hypothesis:
- Name the collision in `SKILL.md:3`'s description with an explicit "not for reviewing a diff — see `code-review`" exclusion, in the shape `architecture-premise-audit` and `repo-refresh` already use.
Disconfirming check:
- Read-only. `sed -n '3p;79p' skills/ultra-review/SKILL.md`, `sed -n '3p' skills/test-proof-debt-audit/SKILL.md`, and `grep -rn 'ultra' ~/.claude/skills/code-review/SKILL.md` if the skill is installed.

### F044 [P3] `--date` is validated only for shape

Severity: P3 | Confidence: low
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:150-153`
Evidence:
- `99-99-99` passes `\d{2}-\d{2}-\d{2}`. (scout-02 2.11)
Contract violated:
- A validation that admits an impossible date into a filename used for ordering.
Plausible failure mode:
- A typo produces a report that sorts to the end of `docs/ultrareview/` forever.
Durable solution hypothesis:
- Parse with `datetime.strptime('%y-%m-%d')` and return the same error class as the sibling checks.
Disconfirming check:
- Read-only. `sed -n '150,153p' skills/ultra-review/scripts/create_ultra_review_report.py`.

### F045 [P3] Unreachable `else path` branch

Severity: P3 | Confidence: low
Source pointer: `skills/ultra-review/scripts/create_ultra_review_report.py:171`, `:182`
Evidence:
- Every `path` comes from `report_dir.glob()` where `report_dir = workspace/docs/ultrareview`, so the `else path` arm is unreachable. scout-02 reported it under the no-suppression rule rather than judging it worth fixing. (2.13)
Contract violated:
- Dead surface.
Plausible failure mode:
- None. It is dead code that implies a case the caller might believe is handled.
Durable solution hypothesis:
- Delete the branch, or keep it and document why the impossible case is defended.
Disconfirming check:
- Read-only. `sed -n '168,185p' skills/ultra-review/scripts/create_ultra_review_report.py`.

### F046 [P3] A scout in this run was dispatched with no assigned concern ID `[out of Scope, first-party]`

Severity: P3 | Confidence: high
Source pointer: `skills/ultra-review/SKILL.md:45` against this campaign's scout-10 packet
Evidence:
- `:45` requires every Scout Packet to carry "assigned concern IDs and tailored search angles." scout-10's packet gave a free-text angle — mechanical verification and first-party compliance — and no `G0x`. scout-10 found this in its own instructions and reported it. (10.15) The coordinator confirms it: scout-10 is the one scout of ten dispatched without a concern ID, and the omission is the coordinator's, not the skill's.
Contract violated:
- `:45`, by this run.
Plausible failure mode:
- Trivial here — the angle was usable and produced eleven findings. Structurally it is the same no-named-owner class the campaign is auditing for, occurring inside the campaign's own dispatch, and per F008 no field in the artifact would ever have recorded it.
Durable solution hypothesis:
- Assign every scout at least one explicit `G0x` even when its angle is a cross-cutting audit role. The durable half is F008: tag findings with concern IDs so coverage is auditable from the artifact.
Disconfirming check:
- Read-only. `grep -n 'G0' skills/ultra-review-workspace/campaign-01/S2-BRIEF.md` and compare the concern list against the ten dispatched packets.

## Verification Queue

**Every check below is read-only. None implies write permission.** Where a check would otherwise
mutate state, it is stated as an isolated re-implementation in a scratch `python3 -c` process that
opens no project file for writing, and never against `~/.herdr/projects/*/gates.md`, `docs/`, or any
file under `skills/`. That constraint is the direct consequence of F005 and F006: this campaign's own
S1 queue got it wrong, so this one states the isolation on every entry rather than in a header.

- F001: `sed -n '129,133p' skills/ultra-review/SKILL.md`; `sed -n '96,104p' skills/ultra-review/scripts/create_ultra_review_report.py`; `sed -n '30,40p' skills/ultra-review-receive/SKILL.md`; `cat skills/ultra-review-receive/agents/openai.yaml`. False if any carries a conditional closing form or requires the authorization to originate outside the report.
- F002: `awk 'NR>=56 && NR<=103' skills/ultra-review/scripts/create_ultra_review_report.py | grep -n 'mode\|sha256\|scout_count\|directive_count'`. Any hit falsifies it.
- F003: `sed -n '12p;16p;52p;63p;106p' skills/ultra-review/SKILL.md`; `find skills/ultra-review-workspace/campaign-01 -type f`. False if `:52` carries a custody exception.
- F004: `sed -n '54,65p' skills/ultra-review/SKILL.md`; `grep -rn 'roster\|allocation\|persisted state' skills/ultra-review/`; `grep -n 'model' skills/ultra-review/scripts/create_ultra_review_report.py`. False if a storage location is named.
- F005: `sed -n '8p;24p' skills/ultra-review-receive/SKILL.md`; `sed -n '115,116p' skills/ultra-review/SKILL.md`; `awk '/^## Verification Queue/,/^## Strongest Reason/' docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md`; `grep -n 'required=True' skills/herdr-delivery-workflow/scripts/gate_row.py`. Do not run S1's F021 or F023 checks to test this one.
- F006: `grep -c '^### F[0-9]' <s1>` against `awk '/^## Verification Queue/,/^## Strongest Reason/' <s1> | grep -c '^- \*\*F'`. Equal counts falsify it.
- F007: `grep -c '^### F[0-9]' <s1>` against `grep -c '^Contract violated:' <s1>` and the same for the other three labels; `sed -n '666,712p' <s1>`.
- F008: `sed -n '16p;95p;106p' skills/ultra-review/SKILL.md`; `sed -n '116,117p;147,149p' skills/ultra-review/scripts/create_ultra_review_report.py`; `grep -n 'concern' skills/ultra-review/SKILL.md`. False if a finding subfield records a concern ID.
- F009: `sed -n '33p;41,51p;118,122p' skills/ultra-review/SKILL.md`; `grep -rn 'model' skills/ultra-review/`. False if any names where the choice is recorded.
- F010: in a scratch `python3 -c`, rebuild `ROUND_RE_TEMPLATE` and the glob and run them over a synthetic in-memory filename list including `26-01-01-auth-fix-round-3.md` with `name="fix"`. Touch no file. Zero false matches falsifies it.
- F011: in a scratch `python3 -c`, re-implement `slugify` over `"Auth Fix"`, `"AUTH-FIX"`, `"Auth/Fix"`, `"auth-fix"`. Four distinct outputs falsifies it.
- F012: `sed -n '21,26p;139,162p' skills/ultra-review/scripts/create_ultra_review_report.py`, then re-implement `slugify` over `"!!!"`, `"   "`, `"日本語レビュー"` in a scratch process. Do not invoke the script.
- F013: `sed -n '54,65p' skills/ultra-review/SKILL.md`; `sed -n '29,40p;160,162p' skills/ultra-review/scripts/create_ultra_review_report.py`. False if a resume mode exists.
- F014: `sed -n '54,65p' skills/ultra-review/SKILL.md`; `grep -n 'cap\|timeout\|attempt' skills/ultra-review/SKILL.md`. Any named bound falsifies it.
- F015: `sed -n '58,63p' skills/ultra-review/SKILL.md`; `grep -n 'logical scout\|missing' skills/ultra-review/SKILL.md`.
- F016: `grep -rn 'receive.md' skills/ultra-review/SKILL.md skills/ultra-review-receive/SKILL.md skills/ultra-review/scripts/create_ultra_review_report.py`. A second hit as an input falsifies it.
- F017: `sed -n '36p;47p' skills/ultra-review-receive/SKILL.md`; `grep -n 'receive record' skills/ultra-review-receive/SKILL.md`.
- F018: `sed -n '24p;42p' skills/ultra-review-receive/SKILL.md`.
- F019: `sed -n '26,30p' skills/ultra-review-receive/SKILL.md`.
- F020: `sed -n '12p;28p;47p' skills/ultra-review-receive/SKILL.md`.
- F021: `sed -n '26,30p;53,55p' skills/ultra-review-receive/SKILL.md`.
- F022: `sed -n '20p;51p' skills/ultra-review-receive/SKILL.md`; `grep -n 'independent' skills/ultra-review-receive/SKILL.md`.
- F023: `sed -n '20p;42p' skills/ultra-review-receive/SKILL.md`; `grep -n 'escalat' skills/ultra-review-receive/SKILL.md`.
- F024: `sed -n '18p;32p;51p' skills/ultra-review-receive/SKILL.md`.
- F025: `grep -n 'restart\|resume\|recovery' skills/ultra-review-receive/SKILL.md`. Any hit falsifies it.
- F026: `sed -n '14p;18p;26p;32p;36p' skills/ultra-review-receive/SKILL.md`; `sed -n '35p;46,47p;52p' skills/ultra-review/SKILL.md`.
- F027: `sed -n '108,115p' skills/ultra-review/SKILL.md`; `sed -n '77,91p' skills/ultra-review/scripts/create_ultra_review_report.py`.
- F028: `sed -n '108p;138,141p;192p' skills/ultra-review/scripts/create_ultra_review_report.py`; `grep -n 'Workspace' docs/ultrareview/*.md`; `sed -n '14p' skills/ultra-review-receive/SKILL.md`. Do not run the script against a file path to reproduce the `NotADirectoryError`; read the two lines instead, or reproduce pathlib's behaviour in a scratch temp directory.
- F029: `sed -n '160,162p;191,193p' skills/ultra-review/scripts/create_ultra_review_report.py`. An `O_EXCL` or `open(..., 'x')` falsifies it. Do not run two concurrent invocations to reproduce the race.
- F030: `sed -n '62p;168p' skills/ultra-review/scripts/create_ultra_review_report.py`.
- F031: `which python; which python3; python3 --version`; `sed -n '95p' skills/ultra-review/SKILL.md`; `sed -n '1p' skills/ultra-review/scripts/create_ultra_review_report.py`.
- F032: `sed -n '100,102p' skills/ultra-review/SKILL.md`; `sed -n '70,94p' skills/ultra-review/scripts/create_ultra_review_report.py`; `grep -n 'malformed' skills/ultra-review-receive/SKILL.md`.
- F033: `sed -n '45p' skills/ultra-review-receive/SKILL.md`; `sed -n '86,88p' skills/ultra-review/SKILL.md`.
- F034: `sed -n '1,4p' skills/ultra-review/agents/openai.yaml`; `sed -n '3p' skills/ultra-review/SKILL.md`; `sed -n '3p;12p;14p' skills/ultra-review-receive/SKILL.md`.
- F035: `sed -n '14p' skills/ultra-review-receive/SKILL.md`; `grep -n 'sha256\|generated' docs/ultrareview/*.md`. Any provenance field falsifies it.
- F036: `sed -n '12p;106p;118,127p' skills/ultra-review/SKILL.md`; `sed -n '1,15p' docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md`.
- F037: `grep -n '^### F' <s1>`; `sed -n '732,749p' <s1>`.
- F038: `sed -n '33p' skills/ultra-review/SKILL.md`; `sed -n '90,96p' skills/ultra-review-workspace/campaign-01/INTAKE.md`.
- F039: `sed -n '120,122p' skills/ultra-review/SKILL.md`; `sed -n '12p' skills/ultra-review-receive/SKILL.md`; `sed -n '57,64p' skills/ultra-review/scripts/create_ultra_review_report.py`.
- F040: `sed -n '24,32p' skills/ultra-review-receive/SKILL.md`; `sed -n '108,115p' skills/ultra-review/SKILL.md`.
- F041: `grep -rn 'status\|queue' skills/ultra-review/SKILL.md skills/ultra-review-receive/SKILL.md`.
- F042: `cat skills/ultra-review/agents/openai.yaml skills/ultra-review-receive/agents/openai.yaml`; `grep -n 'implicit' skills/ultra-review-receive/SKILL.md`. A prose statement falsifies it.
- F043: `sed -n '3p;79p' skills/ultra-review/SKILL.md`; `sed -n '3p' skills/test-proof-debt-audit/SKILL.md`; `grep -rn 'ultra' ~/.claude/skills/code-review/SKILL.md` if installed.
- F044: `sed -n '150,153p' skills/ultra-review/scripts/create_ultra_review_report.py`.
- F045: `sed -n '168,185p' skills/ultra-review/scripts/create_ultra_review_report.py`.
- F046: `grep -n 'G0' skills/ultra-review-workspace/campaign-01/S2-BRIEF.md`, compared against the ten dispatched packets.

## Strongest Reason Not To Merge Yet

**F001, and it fired in this campaign before anyone knew it was a defect.**

Everything else here is a rule that cannot be executed, a parameter that goes nowhere, or a word with
no owner. F001 is different in kind: a gate that grants write authority is satisfiable by text the
producer generates. `create_ultra_review_report.py:102` appends "implement confirmed owner-clean
fixes" to every report it writes, unconditionally, with no flag and no branch.
`ultra-review-receive/SKILL.md:36` withholds write permission until "the current request explicitly
authorizes remediation." The section of the artifact titled **Next Receive Prompt** is what a caller
pastes as the current request. A script authorizes the write, and nothing in either skill requires a
principal to have decided anything.

The proof is not an argument. The S1 report of this campaign does not carry the mandated sentence,
because its coordinator saw that pasting it would misstate the Human's grant and substituted a
verification-only paragraph instead. That substitution was correct on the merits and it was an
undisclosed deviation from a contract-supplied fixed string that no rule authorized — the coordinator
worked around a defect it had not yet identified, and did not say so. Three scouts arrived at the
same line from three directions: scout-01 by diffing the fields the producer writes against the ones
the consumer reads, scout-07 by auditing the authorization gate, and scout-10 by byte-comparing S1
against this report's own untouched scaffold. The skill offers no conditional closing form, so a
verification-only caller cannot both comply with `:131-133` and describe their grant honestly. That
is the merge blocker: not that the wording is careless, but that the only way to be honest about a
narrow grant is to break the contract, and the only way to keep the contract is to hand a write
authorization to whoever reads the file next.

F005 is the same shape at the other end of the pipe and it is also already live: S1's Verification
Queue is headed "Read-only checks" and two of its sixteen entries, as literally written, append rows
to the project's real append-only gate ledger. F003 is the third: this coordinator's context ran out
mid-campaign and five scouts' work survived only because it had been written to a file `SKILL.md:52`
forbids. Three P1 findings each have a live instance inside the run that produced them.

Nothing here is fixed. Every finding above is a hypothesis for `ultra-review-receive` to disposition,
including the ones about this campaign's own artifacts.

## Next Receive Prompt

Use $ultra-review-receive to verify docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1.md and implement confirmed owner-clean fixes.

**That sentence is fixed text mandated by `ultra-review/SKILL.md:131-133` and generated by
`create_ultra_review_report.py:102`. It is reproduced verbatim and it is not an authorization.**
`:131` says to **end with** it; this report does not, because ending on an unqualified write
authorization is the defect. Reproducing the string and then revoking it below is a deliberate,
disclosed deviation on placement, not compliance. F001 is the finding about exactly this line. The Human granted a review of
this project's skills and did not grant remediation, so this pass is **verification only**: every
finding is dispositioned CONFIRMED / DISPROVEN / DUPLICATE / BLOCKED / DEFERRED, and no source file
is edited. Verification does not imply write permission, and neither does the sentence above.

Fixes are Phase B, opened only after the whole campaign's confirmed findings are ranked. Each is a
separate delivery with a real Engineer and an independent Reviewer on the exact head. C12 forbids an
instrument and the doctrine it measures sharing an iteration, so the `ultra-review` prose, the
`create_ultra_review_report.py` fixes, and any change to `ultra-review-receive` are separate
deliveries; and no fix to either skill may land while this campaign is still using them, because a
review whose instrument changes mid-campaign cannot compare its slices.

Findings F006, F007, F037, F038 and F046 point outside the declared Scope at the heading, at this
campaign's own artifacts and records; F005 and F036 are in-Scope findings whose source pointer cites
out-of-Scope evidence and carries the mark there. Seven marks in all, enumerated here rather than
counted: five headings and two source pointers. They are marked and carried rather than dropped; F026 is the finding about the fact that
no rule required the mark.
