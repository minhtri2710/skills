# Ultra Review Receive: s3a-beo-doctrine Round 1

Report received: `docs/ultrareview/26-09-06-s3a-beo-doctrine-round-1.md`
Report sha256: `e6a03cee3f3200d2efcbcbd4649fce4c5c4888bc1c0dbeabb1981c82ae3c43a8`, 1871 lines
Findings in the report: 94 (`grep -c '^### F'`), ids F001-F094 contiguous, bands F001-F015 P1 / F016-F060 P2 / F061-F094 P3
Verification Queue entries: 94 (`grep -cE '^[0-9]+\. F[0-9]{3} —'`), one per finding, both sets compared by `comm` in Custody
Receiver: `lead-beo-skills`, solo-Lead, no Peer staffed
Mode: **verification only.** No source file is edited by this pass. `Files changed: none` on every row below, and that claim is checked against `git diff -- skills/` in the Custody section.
Date: 26-09-07

**Every count in this record is derived by script on the turn it is written**, per `ultra-review/SKILL.md:117` — the rule this campaign's own delivery-02 added on 2026-09-06 after the S1 receive record restated a count (F027's 16) that disagreed with its own enumeration (17). This record is the first receive pass written under that rule, and it is a producer-side rule: `ultra-review-receive` has no equivalent step, which is carried as a flagged risk in `skills/ultra-review-workspace/delivery-02/HANDOFF.md` rather than fixed here.

**Head and scope check, derived this turn.** The checkout is `main@33eafc5431a265d523241db25b0e455a974f09e3`, two commits ahead of the review base `038dc27b50859cb30542b91683688a1f52ce5d66`. `git diff --stat 038dc27b HEAD -- skills/beo/` is **empty**, so every file in S3a's scope is byte-identical to its blob at the reviewed base and the working tree is the correct read surface for this pass. The two commits on top (`dcf9f2f5` in `skills/ultra-review/`, `33eafc54` in `skills/herdr-delivery-workflow/`) touch nothing S3a asserts about. `AGENTS.md` stands ` M` under G57; per the report's own restriction, any citation that reaches into it is read with `git show 038dc27b:AGENTS.md`, never from the working tree.

**Input contract.** `ultra-review-receive/SKILL.md:12` requires a Metadata header, a Prior Round Guard, findings identified `F001`-style, a Verification Queue, and a Strongest Reason Not To Merge Yet. All five are present at `:1-13`, `:95`, `:175`, `:1730` and `:1845`. `:14` requires blocking a malformed report; this one is not malformed and is not blocked. Three shape observations, none of them malformation:

1. **A sixth section.** S3a carries `## Coverage And Derivation` at `:1833`, which neither the S1 nor the S2 report has — both of those have exactly five `## ` headings and S3a has six. The contract names five required sections and does not forbid a sixth. It is recorded here because it is the section this pass leans on hardest: it is where the report derives its own counts, and it is also where the report discloses that its P3 band was first drafted from a consolidation map held in context rather than from the candidate rows on disk. That disclosure sets the prior for the P3 dispositions below, and each affected row says so.
2. **Five coordinator-added metadata lines** (Scouts, Scout model, Review brief, Directives, Mode) below `Report path:`, disclosed by the report at `:14-16`. Same departure S2 disclosed and accepted on the same reasoning.
3. **The mandated closing sentence is reproduced and then explicitly revoked** at `## Next Receive Prompt` rather than used as the report's last words. Accepted as disclosed. This pass honours the revocation: it is verification-only, it applies no fix, and being CONFIRMED authorizes nothing.

**Prior first-party records cited below**, both written by this seat before this report was opened:
`docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1-receive.md`, sha256 `e3a53b3bcd6671db221050edc22191e915d36e66a93e9b42490ab0267d0ec697`, 995 lines; and
`docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1-receive.md`, sha256 `a39766056780b3f81c4e84c246a84dc25235dc43abe52739a4508c3e93eda658`, 1227 lines.

**Out of scope for every disposition below, and therefore never asserted about:** the 17 helper scripts under `skills/beo/beo-reference/scripts/` and the 9 test modules under `tests/`. S3b owns them. Any finding whose disconfirming check would need a script read to settle is dispositioned `BLOCKED` with S3b named as the owner, not confirmed on the doctrine text alone.

## Dispositions

### F001 [P1] — CONFIRMED on the doctrine surface, with the headline half narrowed by out-of-scope evidence

Checks run, both read-only, both this turn:
`python3 -c "...state.schema.json...print(d['properties']['review']['required']);print(d['properties']['review']['properties']['reviewed_by'])"` → required is `['actor','verdict','route_condition_id','findings','done_criteria_coverage','repair_count','closed_in_br','reviewed_by']` and `reviewed_by` is `{'type':'string','enum':['beo-execute','beo-review']}`. **No null in either place**, so the disconfirming condition is not met.
The asymmetry the finding rests on is confirmed exactly: in the same object `verdict` is `['string','null']`, `actor` is `['string','null']`, `route_condition_id` is `['string','null']`. Three siblings model the not-yet-reviewed state and `reviewed_by` does not. `review` is itself in the schema's top-level `required`, and both the root and the `review` object carry `additionalProperties: false`, so this is a hard validation failure and not a soft one.
`grep -c reviewed_by skills/beo/beo-reference/examples/quick-mode-golden-trace.md` → **0**. The example half is confirmed with no qualification: the key is absent from every snapshot, including the final one showing `verdict: "accept"`, where `lifecycle.md:95` says the field is what distinguishes a real `beo-review` verdict from a `beo-execute` fast-track stub.

**Narrowing, on incidental out-of-scope evidence.** The headline says "no `state.json` can validate before a review exists". `beo_state.py:49-58` — a script, S3b's scope, surfaced by the queue's own `git grep` and read no further than the initializer literal — seeds `review.reviewed_by` with the string `"beo-review"` at initialization, alongside `verdict: None` and `actor: None`. So a script-produced `state.json` **does** validate, and the unsatisfiability claim is narrowed to hand-authored or example-derived state. What the initializer does instead is arguably worse and is not what the finding filed: it asserts a review by `beo-review` on a bead that has not been reviewed, which inverts the discriminator `lifecycle.md:95` defines. **That inversion is asserted about the doctrine only — that the schema admits no honest initial value — and the script's correctness is S3b's to settle.**

Disposition: **CONFIRMED**, schema/example contradiction decisive; unsatisfiability half narrowed as above. Files changed: none.

### F002 [P1] — CONFIRMED on the prose gap; the "which side is defective" half is BLOCKED on S3b, as the report itself states

`git grep -n "phase_sequence_id" -- skills/beo/beo-reference/references skills/beo/*/SKILL.md` → **exit 1, zero hits**. The disconfirming condition ("false if any prose file defines the field's write-time semantics") is not met. A field in the schema's top-level `required` and in `approval.required` has zero occurrences across all ten reference files and all nine skill cards.

The report already marks its own directional evidence `[out of Scope]` and provisional: `beo_state.py:608` stamps the value from the **post**-transition `phase_sequence_id` while `approval-envelope.json:89` defines the predicate against the **pre**-transition one. This pass does not resolve that and does not need to: the durable doctrine defect — a required field whose only semantics anywhere in the 32-file surface is one sentence in a predicate description, contradicted by the bundle's one worked example — is confirmed on the doctrine surface alone, and holds whichever way S3b resolves the script.

Disposition: **CONFIRMED** on the prose gap. The envelope-vs-trace direction is **BLOCKED**, owner S3b. Files changed: none.

### F003 [P1] — CONFIRMED

`git grep -n "reservation_active_and_not_revoked\|human_gate_refs_not_revoked\|external_authorization_refs_not_revoked\|side_effect_contract_unchanged" -- skills/beo` → **4 hits, all in `approval-envelope.json:14-17`**, the declaration itself. The disconfirming condition ("any hit outside `approval-envelope.json` falsifies the finding") is not met; there is no hit outside it, in any card, reference, template, example or other registry file — and none in the scripts either, which is more than the finding claimed and is recorded rather than relied on.

The four strict predicates are declared as conditions of a strict approval's continued validity and are named nowhere else in the bundle. Kernel Hard Invariant #3 gates product mutation on that approval's validity, and no phase evaluates the predicates that define it.

Disposition: **CONFIRMED**. Files changed: none.

### F004 [P1] — CONFIRMED

`grep -n "beo_verify\|verification_run" skills/beo/beo-reference/references/kernel.md skills/beo/beo-reference/registry/profiles.json` → **exit 1, zero hits in either file**. The disconfirming condition ("false if a fast-track-specific requirement to run the helper exists") is not met, and the result is stronger than the finding needed: the machine-enforced verification runner is not named at all in the kernel or in the profile registry that defines the fast-track lane.

Derived alongside: `profiles.json` `modes.quick.fast_track.additional_requires` is exactly `['scope.files.allow_all_explicit', 'fast_track: true in TICKET.json']` — two shape conditions, neither of which touches who produced the verification results. The review-skipping lane's only gate is the acting agent's own attestation, which is the queue's stated confirm criterion.

Disposition: **CONFIRMED**. Files changed: none.

### F005 [P1] — CONFIRMED

`git grep -n "human_gates" -- skills/beo` filtered to non-script hits and searched for any tie to a round-trip, a `br-comment` ref, a `user_review_needed` condition, or an evidence ref → **exit 1, zero hits**. `grep -n "br-comment" skills/beo/beo-reference/references/user-handoff.md` → **one hit, `:45`**, where it is listed as a durable evidence-ref format and is connected to nothing in `human_gates`. The disconfirming condition is not met.

The schema surface confirms the shape half directly: `ticket.schema.json:95` defines `human_gates`, `:166-180` requires its presence for the conditional modes, and `profiles.json:18` lists `human_gates` among strict's `requires` — all presence conditions. Nothing anywhere states that a `resolved` status may be written only after a completed human round-trip.

Disposition: **CONFIRMED** on the missing chain. The exploitability half stays at the report's own medium confidence: this pass verifies that no rule ties status to provenance, not that any real bead has been driven through the gap. Files changed: none.

### F006 [P1] — CONFIRMED

`python3 -c "...approval-envelope.json...print(d['approval_fields']);print(d['computed_projection_fields'])"` → `approval_fields` is the nine `approval.*` leaves and `computed_projection_fields` is exactly `['ticket_file_hash', 'repo_head']`. **Neither records a hash of the approval-bearing contract set**, so the disconfirming condition is not met.

The internal contradiction is confirmed from the same file read this turn: `validity_model.invalidators` includes `machine_readable_safety_contract_changed`, and `contract_hash_policy` states the design intent that "any helper file change invalidates prior `PASS_EXECUTE`". An invalidator with no recorded baseline cannot fire, and `repo_head` catches only a committed change, so an uncommitted in-place edit to a control-plane file between grant and use is invisible to every field the approval carries.

Disposition: **CONFIRMED**. The membership sub-question scout-10 raised (whether `beo_paths.py` belongs in the set) is **moot at this head** for the reason the report gives — there is no recorded hash for membership to matter to — and is not separately dispositioned. Files changed: none.

### F007 [P1] — CONFIRMED, both halves

`python3 -c "...phase-contracts.json...s=d['skills']['beo-execute'];print(s['state_write_fields']);print(s['must_not'])"` → `state_write_fields` is `['phase', 'execution', 'review']` and `must_not` is `['approve', 'validate', 'review', 'close', 'mutate_outside_approved_scope']`. **`review` is a member of both lists in one object.** The first disconfirming condition ("the two lists no longer share a member") is not met.

The second disconfirming condition — "or a definition elsewhere establishes `state_write_fields` as category labels" — is also not met, and this pass ran the check the report says scout-05 could not satisfy. `git grep -n "state_write_fields" -- references/ */SKILL.md` returns **exactly one hit**, `kernel.md:156`, which *names* the key in a list of what per-skill entries record and does not define whether its members are literal state paths or category labels. So the coarse-vs-leaf ambiguity the finding turns on is real: `"review"` is not leaf-qualified, and nothing machine-readable prevents `review.verdict` from being written by the executing phase. The prose narrowing exists only in `beo-execute/SKILL.md:45`, which is not registry-visible.

Disposition: **CONFIRMED**. Files changed: none.

### F008 [P1] — CONFIRMED

`git grep -n "skills/beo" -- skills/beo/beo-reference/registry/profiles.json` → **exit 1, zero hits**. `protected_path_defaults` derived this turn is `['.git/**', '.env', '.env.*', '**/.env', '**/.env.*', 'secrets/**', 'credentials/**', '*.pem', '*.key', '*.p12', '*.pfx', 'id_rsa', 'id_ed25519', '.beads/**']` — fourteen entries, no `skills/**`, no `skills/beo/**`, no CI config path.

`beo-validate/SKILL.md:19-28` read in full this turn: step 4 rejects "dirty approved files, dirty declared generated outputs, unsafe paths, and unauthorized broad globs", and "unsafe" is defined by `profiles.json`, which does not list the bundle. No other in-scope rule restricts `scope.files.allow` from reaching the harness install path. The disconfirming condition is not met.

The asymmetry the finding names is confirmed as stated: `harness-proposal.schema.json` constrains a *proposal's* target to `^skills/beo/`, which is the opposite direction from the one that would stop ordinary ticket scope reaching those files.

Disposition: **CONFIRMED**. Files changed: none.

### F009 [P1] — CONFIRMED on the mechanics; the materiality half is BLOCKED on S3b, as filed

`python3 -c "...runtime-event.schema.json...print(list(d.keys()));print('\$defs' in d)"` → root keys are `['$schema', 'title', 'description', 'type', 'additionalProperties', 'required', 'properties', 'beo_contract_metadata']` and **`$defs` is absent**. `beo_contract_metadata` is a root sibling of `properties`/`required`/`additionalProperties` and is reachable from no applicator keyword, so under JSON Schema 2020-12 it is an annotation with no assertion effect. The disconfirming condition is not met on either branch.

Two corroborations derived this turn rather than restated: `properties.payload` is exactly `{'type': 'object'}`, so the only real constraint on any event payload is that it be an object; and `grep -c '"type": "safe_evidence_ref"'` → **4**, confirming the four subschemas naming a type that is not one of the seven JSON Schema types, with no `$defs` for a `$ref` to have pointed at.

`artifact-boundaries.md:58-68` read in full this turn confirms the textual corroboration scout-01 filed: the bundle itself states that `beo_state.validate_state` "currently does not enforce" the no-approval-mutation rule on intervention entries and calls it "caller discipline only". That is the same class of gap, admitted in the bundle's own prose.

Disposition: **CONFIRMED** on the schema mechanics. Whether `beo_check.py`/`beo_state.py` enforce `payload_contracts` procedurally is **BLOCKED**, owner S3b — and the report already filed that half as `[out of Scope]`. Files changed: none.

### F010 [P1] — CONFIRMED, and the "exists nowhere" half is stronger than filed

`git grep -n "proposals/pending" -- skills/beo` → **3 hits**, quoted at the paths git grep printed: `skills/beo/README.md:69`, and `skills/beo/beo-reference/scripts/beo_propose.py:7` and `:28` (out of scope, cited only as the second documented spelling the check asks about). No second output path is documented, so the disconfirming condition is not met.

Two contradictions derived this turn:
- **Format.** `skills/beo/README.md:69` says the helper "generates `beo-author/proposals/pending/prop-*.md`" — markdown. `command-manifest.md:24` gives the same helper's output column as **`json`**. The bundle's own helper index and its README disagree on the artifact's format.
- **Existence.** `git ls-tree -r --name-only 038dc27b -- skills/beo/beo-author` returns exactly one path, `skills/beo/beo-author/SKILL.md`. `ls -d skills/beo/beo-author/proposals` → *No such file or directory*. The directory the README names as this helper's output location does not exist at the reviewed base, tracked or on disk.

Disposition: **CONFIRMED**. Files changed: none.

### F011 [P1] — CONFIRMED, and this campaign's own brief carries the inherited error

`python3 -c "...approval-envelope.json...print(len(d['contract_hash_policy']['approval_bearing_contracts']))"` → **13**, not 1, so the disconfirming condition is not met. Enumerated rather than counted from memory: eight registry files (`approval-envelope.json`, `profiles.json`, `pipeline.json`, `ticket.schema.json`, `state.schema.json`, `reservation-schema.json`, `runtime-event.schema.json`, `phase-contracts.json`) and five scripts (`beo_check.py`, `beo_approval.py`, `beo_state.py`, `beo_reservation.py`, `beo_verify.py`).

`README.md:60-69` read in full this turn: the section opens "BEO ships advisory helpers … These are owned by the delivery skills that invoke them and **never grant authority**", then singles out `beo_verify.py` as "Added to `approval_bearing_contracts` because it is machine-enforced" — the one-exception framing. Four other scripts are in that same list and the README's own bullets do not say so.

**First-party confirmation of the inheritance half.** `skills/ultra-review-workspace/campaign-01/S3A-BRIEF.md:91-93` reads: "The scripts in `beo-reference/scripts/` are **advisory helpers that never grant authority**, with one stated exception: `beo_verify.py` is in `approval_bearing_contracts` because it is machine-enforced." That is this campaign's own brief, written by this seat, repeating the README's error verbatim into the instructions ten scouts read. Recorded here rather than quietly corrected: the brief is a dated artifact about a named head and is not edited by this pass.

Disposition: **CONFIRMED**, including the inheritance. Files changed: none.

### F012 [P1] — CONFIRMED

`git grep -n "recompile\|scratch\|throwaway" -- skills/beo/beo-reference/references` → **exit 1, zero hits**. No planning-time mutation carve-out exists anywhere in the ten reference files, so the disconfirming condition is not met.

The collision is confirmed from three sites read this turn. `beo-plan/SKILL.md:37` (Do step 14) instructs, for each removal candidate, to "verify the claim independently (**remove the annotation and recompile**, grep for callers, check that the removal condition is currently met)" and closes "This is a planning-time check, not an execution-time check." Removing an annotation is a product-file mutation. `beo-plan/SKILL.md:55-56` (Never) reads "See `beo-reference -> registry/phase-contracts.json` `must_not[]`" and "Do not mutate product files." `phase-contracts.json` carries `mutate_product_files` in beo-plan's `must_not`. The card instructs in its Do what it forbids in its Never, at planning time, before any `PASS_EXECUTE` can exist.

Disposition: **CONFIRMED**. Files changed: none.

### F013 [P1] — CONFIRMED

`git grep -n "allowlist\|denylist" -- skills/beo` → **exactly one hit**, `beo-author/SKILL.md:65`, which is about not adding audit check C9 to an auto-heal allowlist and has nothing to do with verification command content. `sed -n '19,28p' skills/beo/beo-validate/SKILL.md` read in full this turn: step 4 validates ticket fields and mode requirements and "reject[s] dirty approved files, dirty declared generated outputs, unsafe paths, and unauthorized broad globs" — every one of those is a *path* check. **No validation step inspects the text of `scope.verify.commands`.** The disconfirming condition is not met.

The approval side matches: `approval-envelope.json`'s projection hashes the ticket so that a *change* to the commands invalidates the approval, which is a staleness guarantee and not a content guarantee. A command that was malicious when written is hashed as faithfully as one that was not.

Disposition: **CONFIRMED**. The trust-boundary framing is coherent with F004, which this pass also confirmed: F004 is that the fast-track lane trusts self-recorded results, F013 is that the command producing those results is never read. They compound and are filed separately, correctly. Files changed: none.

### F014 [P1] — CONFIRMED, both halves

`git grep -n "cross_check" -- skills/beo/*/SKILL.md skills/beo/beo-reference/references` → **3 hits**: `kernel.md:150`, which *defines* the requirement; and `beo-review/SKILL.md:14` and `:27`, which both *consume* it — `:14` lists `beo_check.py` as the mechanical enforcer and `:27` says a signal "is recorded" in the passive voice without naming who records it. **No card's Do or Write section produces the field**, so the disconfirming condition is not met.

`beo-review/SKILL.md`'s Write section, read in full this turn, is `state.json` "phase and review fields only" — coarse, and it names no producer for `cross_check` any more than the registry does. `phase-contracts.json` gives beo-review `state_write_fields: ['phase','review']`, the same coarse grant, and no skill in the bundle is assigned the second-reviewer role.

The "no schema can require it" half is confirmed independently: `state.schema.json:117` defines `cross_check` with `required: ['reviewer','verdict']` *inside* the object, but `cross_check` is **absent from `review.required`**, and its own description says "Required for strict-mode `verdict_accept`; absent otherwise" — a mode-conditional requirement the schema states in prose and expresses in no `if`/`then`. So the field is required by the kernel, unproduced by any card, and unenforceable by the schema.

Disposition: **CONFIRMED**. Files changed: none.

### F015 [P1] — CONFIRMED

`harness-proposal.schema.json` read this turn: root keys are `['$schema','title','description','type','additionalProperties','required','properties']` — **no `$defs`** — and `properties.target` is `{'type':'string','minLength':1,'pattern':'^skills/beo/'}`. The pattern is anchored only at the start and carries no traversal guard.

Demonstrated rather than asserted, with Python's `re` on the literal pattern: `skills/beo/../../etc/passwd` → **matches**; `skills/beo/../../../.ssh/id_rsa` → **matches**. Both satisfy kernel §10's mechanical guard on the one field in the bundle that names a file to be mutated.

The contrast that makes this a defect rather than an oversight in isolation: `state.schema.json:8-11`, `ticket.schema.json:9-12` and `reservation-schema.json:37` each define a `safe_path` `$def` whose pattern carries an explicit `(?!.*(^|[/\\])\.\.([/\\]|$))` traversal guard, and `$ref` it at every path-typed field. `harness-proposal.schema.json` is the fourth registry file with a path field and the only one without that guard — which is exactly the gap F085 says is *not* one of its three literal `safe_path` copies.

Disposition: **CONFIRMED**. Files changed: none.

## P2 band, F016-F060

### F016 [P2] — CONFIRMED

`git grep -n "AGENTS" -- skills/beo/beo-reference/registry` → **exit 1, zero hits**. The disconfirming condition — any registry entry naming the exception — is not met anywhere in the registry directory, not only in `phase-contracts.json`.

`phase-contracts.json`'s `skills["beo-setup"]` read whole this turn: `must_not` is `['grant_PASS_EXECUTE','review','mutate_product_files','close','make_qmd_or_obsidian_authoritative']` and `artifact_write_authorities` is `['setup_status_output','explicitly_authorized_memory_setup']`, exactly as filed. `state_write_fields` is `[]` — the empty list, which the finding does not mention and which makes the asymmetry sharper: this owner is granted no state writes at all, yet its card documents a repo-root product-file write as routine.

Disposition: **CONFIRMED**. The C8 half is correctly marked out of scope by the scout and stays there; S3b owns it. Files changed: none.

### F017 [P2] — CONFIRMED, both halves

`pipeline.json`'s `reservation_release_on` derived this turn: `['verdict_accept','executed_and_verified','cannot_deliver','abandoned','repair_rescope']` — five triggers, **no validation-failure condition of any spelling**. The disconfirming condition is not met.

The expiry half checked separately rather than taken from the scout's argument: `grep -n "expir\|ttl\|expires" reservation-schema.json` → **exit 1, zero hits**. There is no expiry field to find, so the schema cannot express one, and `kernel.md:29` Hard Invariant #8 "No Expiry" is consistent with the schema rather than contradicted by it. The gap is real and it is deliberate on the expiry side; only the missing release trigger is unintended.

Disposition: **CONFIRMED**. Files changed: none.

### F018 [P2] — CONFIRMED on the sync gap; the ambiguity half stands as filed

`git grep -n "supersede\|superseded" -- skills/beo/*/SKILL.md skills/beo/beo-reference/references` → **5 hits**, every one of which fails to be a cross-issue state write:
- `beo-author/SKILL.md:65` — supersede of a *learning*, not a reservation.
- `kernel.md:49` — "A newer artifact supersedes it", a general staleness principle with no instruction attached.
- `safety.md:35` — the reservation lifecycle sentence the finding already cites as the violated contract.
- `beo-validate/SKILL.md:30` — the create-or-supersede step itself.
- `beo-validate/SKILL.md:37` — the Write authority line, scoped to `.beads/beo-reservations.jsonl` **only**, which is the second, independent confirmation: beo-validate's declared write surface for this operation is the reservation ledger and nothing else, so it has no authority to touch T1's `state.json` even if a card told it to.

The disconfirming condition — any card instructing a cross-issue state write — is not met. Disposition: **CONFIRMED**. The per-actor versus per-(actor, issue) ambiguity is a second-order reading of `:30` and is recorded at the scout's own medium confidence, not raised. Files changed: none.

### F019 [P2] — CONFIRMED; the finding's supporting sentence corrected

The enum break is real. `state.schema.json:17` and `runtime-event.schema.json:11` both carry `phase` as `["planned","approved","executing","executed","reviewing","reviewed","blocked","abandoned"]`; a regex search for the literal `"planning"` in both schema files returns **zero matches in either**. `pipeline.json:95` is the `expected_receiver_phase_after_condition_note`, read whole this turn, and it does instruct writing "a transition state (like blocked or planning)" — `blocked` is an enum member, `planning` is not.

**The finding's evidence sentence is wrong and the correction does not rescue it.** The scout wrote that `grep -n '"planning"'` across the three files "finds it only in that prose note". It does not: there is a second hit, `pipeline.json:68`, `"planning": ["planned","plan_validated","decomposition_recorded"]`. Read in context this turn (`sed -n '60,72p'`), that line is a **key in `route_classes`**, whose members are condition ids, not phases — so it is not an enum member and does not meet the disconfirming condition. The finding survives; its enumeration did not.

That second hit slightly raises the hazard rather than lowering it: the registry uses the token `planning` as a route-class name in one place and as an instruction to write a phase value in another, so an agent that resolves the note by searching the file finds the token and finds it attached to conditions.

Disposition: **CONFIRMED**, evidence corrected. Files changed: none.

### F020 [P2] — CONFIRMED

`git grep -n metadata -- skills/beo/beo-reference/registry/phase-contracts.json` → **exit 1, zero hits**. The disconfirming condition is "false on any hit"; there are none. No owner in the registry is granted `metadata`, and `state.schema.json` requires the object.

Disposition: **CONFIRMED**. Files changed: none.

### F021 [P2] — CONFIRMED as filed, on the scope the finding declares

`git grep -n "initialize" -- skills/beo` → **6 hits**. Exactly one is doctrine: `phase-contracts.json:13`, the sentinel itself. The other five are all in `beo-reference/scripts/` — `beo_run.py:87,89`, `beo_state.py:135,137,519`, `check_skill_bundle.py:250` — which are **S3b's scope, not this pass's**. None of the five elaborates the sentinel; `beo_state.py:519` and `check_skill_bundle.py:250` both hold the bare literal `{"initialize"}` keyed to `beo-plan`, which **replicates** the sentinel into two more files rather than defining it. The disconfirming condition — any file elaborating the meaning — is not met, and the incidental script evidence points the same direction as the finding.

The routed re-entry half is confirmed against `expected_receiver_phase_after_condition`, derived whole this turn: `plan_validated` → `planned`, `validation_failed` → `blocked`, `repair_rescope` → `planned`. Three legs, and the owner of all three has `state_write_fields: ["initialize"]`.

Disposition: **CONFIRMED**. Files changed: none.

### F022 [P2] — CONFIRMED

`git grep -n "repair_count\|debug_count\|diagnosis" -- skills/beo/beo-reference/references skills/beo/*/SKILL.md` → **10 hits, and not one is a `repair_count` or `debug_count` hit at all.** Every hit matches the substring `diagnosis` inside `root_cause_diagnosis_needed` or its prose (`beo-debug:19,29,36`, `beo-execute:33,55`, `kernel.md:141`, `lifecycle.md:106`, `beo-review:29,46,56`). So the two counter tokens appear **zero times** across the whole doctrine surface, and the ten hits that do land are route-condition plumbing — none consumes a counter for a routing decision. The disconfirming condition is not met.

`lifecycle.md:106` is worth naming because it is the closest thing to a bound and is not one: it enumerates beo-review's final routes and explicitly classes `root_cause_diagnosis_needed` as "a non-final diagnostic handoff route" — the doctrine states the loop edge is non-terminal without ever bounding how many times it may be taken.

Disposition: **CONFIRMED**. Files changed: none.

### F023 [P2] — CONFIRMED on the structural claim; **the count in the headline is wrong**

The structural claim holds and is the whole substance: `grep -n '"from": "user"' pipeline.json` → **exit 1, zero hits**, and the parsed `transitions` array filtered for `from == 'user'` returns `[]`. `user` is a pure sink in the machine-readable graph.

**The headline count is not derived.** The finding says "nine incoming edges" and cites six line numbers. Derived this turn: `grep -c '"to": "user"' pipeline.json` → **7 file-wide**, at lines 7, 8, 12, 22, 23, 26 and 50; the parsed `transitions` array holds **6** of them, the seventh being `:50` inside `support_subroutines` (`beo-author -> user_review_needed -> user`). So the correct figures are **6 transition edges, 7 file-wide** — not 9 by either reading. The six line numbers the finding cites (8, 9, 13, 23, 24, 27) are each **exactly one greater** than the six real transition-edge lines, a uniform off-by-one that suggests the pointers were transcribed against a shifted image and never re-derived.

This is the C16 defect class again, and it is the second instance this campaign has caught in a scout report — S1's F027 restated 16 where its own enumeration gave 17. Recorded here rather than downgrading the finding: the defect is in the count and the pointers, not in the claim, and the claim is confirmed on a re-derived enumeration.

Disposition: **CONFIRMED**, count corrected 9 → 6/7 and pointers corrected by −1. Files changed: none.

### F024 [P2] — CONFIRMED, every number re-derived

`list(d['reentry_rules'].keys())` → `['executing']`, one key. `expected_receiver_phase_after_condition` has **17** entries, and `collections.Counter` over its values gives `blocked: 8, planned: 3, reviewed: 2, approved: 1, executed: 1, reviewing: 1, abandoned: 1`. The eight `blocked` conditions enumerated are exactly the eight the finding names: `decomposition_recorded`, `approval_stale_or_invalid`, `harness_change_needed`, `root_cause_diagnosis_needed`, `repair_same_scope`, `cannot_deliver`, `user_review_needed`, `validation_failed`. Every figure in the headline — 8 of 17, one key — matches its own enumeration, which after F023 is worth stating explicitly.

Disposition: **CONFIRMED**. Files changed: none.

### F025 [P2] — CONFIRMED on the doctrine surface; one incidental script hit named and set aside

`git grep -n '"stale"' -- skills/beo` → **3 hits**, none of which is a card instructing the write:
- `state.schema.json:24` — the enum declaration itself, the subject of the finding.
- `beo_state.py:156` — `APPROVAL_STATUSES`, which mirrors the enum into the script layer without adding a writer. S3b scope; recorded because it shows the value propagating without ever acquiring a producer.
- `beo_worktree.py:339` — read in context this turn (`sed -n '330,345p'`). This is **not** an approval status: it is a local `status` variable describing a *worktree* whose registered path is missing, printed in that script's own JSON output. It is a same-token collision, not a producer of `approval.status`, and it does not meet the disconfirming condition.

So no card and no script writes `approval.status: "stale"`. The two-ends-of-the-gap half is confirmed structurally from evidence already derived at F007 and F014: beo-execute's `state_write_fields` is `['phase','execution','review']`, with no `approval`.

Disposition: **CONFIRMED**. The scout's own countervailing note — no consumer reads `approval.status` unpaired with a `phase` check — is preserved and keeps exploitability low. Files changed: none.

### F026 [P2] — CONFIRMED, and the direction the report chose is confirmed with it

Both divergences verified against the files. `reservation_release_on` derived at F017 is `['verdict_accept','executed_and_verified','cannot_deliver','abandoned','repair_rescope']`. `release_reason` in `reservation-schema.json` carries `['verdict_accept','cannot_deliver','abandoned','repair_rescope','human_released', null]` at **three sites** — `:55` (the property), `:95` and `:141` (the `allOf` released branches) — exactly the three the finding cites. `executed_and_verified` is in the trigger list and in none of the three enums; `human_released` is in all three enums and in no trigger list.

The disconfirming check — any path allowing a non-quick bead to fast-track while holding a reservation — returns **six `fast_track` hits and no such path**:
- `kernel.md:124` "opt-in flag for `quick` mode beads only" and `:132` "never allowed for `standard` or `strict` mode beads".
- `ticket.schema.json:185` — read in context this turn (`sed -n '178,200p'`): the `fast_track` `if` is **nested inside** the `{"if": {"mode": {"const": "quick"}}}` branch, so the schema structurally cannot apply fast-track semantics to another mode.
- `profiles.json:7-9` places `fast_track` under `modes.quick`, and its `strict` block at `:17-19` is the only mode whose `external_evidence_requires` is `['current_actor_matching_beo_reservation']`.

That last pair is the first-party form of the report's argument: reservations are required by `strict` only, `fast_track` is permitted by `quick` only, and `executed_and_verified` is emitted only on the fast-track leg (`kernel.md:127`). The trigger is unreachable, so scout-07's direction — the trigger list is the defective side, not the enum — is confirmed on evidence rather than adopted on assertion.

Disposition: **CONFIRMED**, direction confirmed. Files changed: none.

### F027 [P2] — CONFIRMED, stronger than filed

`git grep -n "close" -- phase-contracts.json` → **10 hits**, and the disconfirming condition (an epic-scoped closure authority) is met by none:
- `:76` `br.close_on_verdict_accept` — beo-review's only closure grant, and it is conditioned on a verdict an epic never receives.
- `:27, :51, :69, :97, :106, :153` — the bare atom `close` in six owners' `must_not`, `:27` being **beo-plan**, the skill that authors the checklist item.
- `:121` `close_delivery_issue` and `:90` `close_non_accepted_work`.

`:90` is the strengthening the finding does not claim. beo-review's `must_not` contains **`close_non_accepted_work`**, and an epic is by construction never executed and never accepted — so beo-review, the one skill holding any closure grant at all, is affirmatively **forbidden** from closing the parent, not merely unauthorized by omission. The gap is closed on both sides: nobody is granted it and the only plausible grantee is explicitly barred.

Disposition: **CONFIRMED**. scout-05's human-operator reading is preserved as the resolving hypothesis for Phase B; it does not change the disposition, because the doctrine still names no actor. Files changed: none.

### F028 [P2] — CONFIRMED on the mismatch; the direction stands, un-disconfirmed

The mismatch is confirmed from evidence this pass already holds. `kernel.md:141`, read at F022, is the disjunction verbatim: "route to `beo-review` via `containment_review_needed` or `beo-debug` via `root_cause_diagnosis_needed`". `reentry_rules` has the single key `executing` (derived at F024), and its `emitted_conditions` split the case in two on attributability.

The disconfirming condition is specific and negative: the chosen direction is wrong **if kernel names a criterion for picking between the two routes that the registry lacks**. `kernel.md:141` names none — it offers "or" and stops. So the registry carries a discriminator kernel does not, and the report's adoption of scout-09's direction survives.

Disposition: **CONFIRMED**, direction un-disconfirmed but not independently proven — scout-01's opposite reading is preserved as the report itself preserved it, and Phase B re-tests before either file is edited. Files changed: none.

### F029 [P2] — CONFIRMED

`git grep -n "proposal" -- skills/beo/beo-reference/registry/state.schema.json` → **exit 1, zero hits**. The disconfirming condition is "false on any hit"; there are none. A wider `grep -n "harness" state.schema.json` returns exactly **one** line, `:77`, where `harness_change_needed` sits inside the `route_condition_id` enum — a routing token, not a proposal identity. So kernel §10.4 promises a hash tracked "in state" and `state.json`'s schema has no field of any name capable of holding one.

Disposition: **CONFIRMED**. Files changed: none.

### F030 [P2] — CONFIRMED on the missing else-branch; **the execute-side exploit is disconfirmed**

The disconfirming check resolves against the finding on its stronger half. `sed -n '36,42p' safety.md` reads: "Execution starts after a durable `state.json` update where `phase = executing`, `execution.actor` and `execution.started_at` are set, **and approval validity predicates still hold**." That is an **entry-time** predicate and the section is titled "Execution start" — precisely the condition the scout named as the one that would weaken the finding, and it holds. So the scenario where beo-author invalidates an approval *mid-execution* and beo-execute must react has no stated trigger, and the finding's own "not hypothetical" framing does not survive on the execute side.

What survives is the documentation defect as literally filed: kernel §10.7 states a continuation condition ("if the bead remains valid") with **no else-branch anywhere**, and `beo-review/SKILL.md:37` drops the conditional entirely and says "re-read state and continue review" unconditionally — a stated condition in the canonical file silently deleted in a subordinate card. That asymmetry is confirmed and is the part worth ranking.

Disposition: **CONFIRMED, narrowed**. Severity should fall below the filed P2 in Phase B ranking: the review-side conditional drop is real, the execute-side failure mode is not reachable at this head. Files changed: none.

### F031 [P2] — CONFIRMED

`pipeline.json`'s `maintenance_skills['beo-author']` parsed whole this turn. Its four transitions are exactly as filed: `skill_authored_or_updated`, `reference_or_registry_updated` and `no_change_needed` all `"to": "caller"`; `user_review_needed` alone `"to": "user"`. The object's only other keys are `outcomes` and `harness_proposal_callers: ['beo-execute','beo-review']` — the latter is the thread the finding says is missing and it is **not** one: it names which skills may call, not which one called, and carries no per-invocation identity. The disconfirming condition — a caller thread — is not met.

This compounds with F024, confirmed above: the paused caller sits at `blocked`, which is the one receiver phase with no `reentry_rules` key.

Disposition: **CONFIRMED**. Files changed: none.

### F032 [P2] — CONFIRMED, both halves

`git grep -n "promot\|precedence\|contradict" -- skills/beo` → **3 hits**, and the disconfirming condition (an owner or a precedence rule) is met by none:
- `memory.md:16` — the unowned promote instruction itself.
- `safety.md:6` — read in context this turn: the heading is `## Scope precedence` and its body ranks **path** classes (protected > forbid > allow > generated outputs). It is a scope rule, not a doctrine-precedence rule, and says nothing about memory versus kernel.
- `beo_score_trace.py:93` — a docstring about config override order. S3b scope, unrelated.

So "promote" has exactly one occurrence in the whole bundle and it is the instruction; no file names an owner, a threshold, or a precedence rule for memory content.

Disposition: **CONFIRMED**. Files changed: none.

### F033 [P2] — CONFIRMED; the check returns hits and none of them disconfirms

`git grep -n "relative to" -- skills/beo` → **4 hits**, so the check does not come back empty, and each was read before disposition:
- `beo-author/SKILL.md:63` — the C9 resolution strategy for **evidence refs** at runtime (vault root, repo root, `--learning-repo`).
- `beo-execute/SKILL.md:22` — **worktree** path resolution during execution.
- `harness-proposal.schema.json:24` — the `target` field's base, "relative to repo root, under `skills/beo/`", which is the one place a base *is* declared and it governs a JSON data field, not a citation.
- `check_skill_bundle.py:8` — a script comment. S3b scope.

None is a normative sentence about how a citation inside `beo-reference/references/*.md` resolves. The disconfirming condition — "one normative sentence declares the base" — is not met, and the near-miss at `harness-proposal.schema.json:24` sharpens the finding: the bundle knows how to declare a base and does so exactly once, for a machine-read field, and never for the prose apparatus that carries the doctrine.

The highest-confidence single site verified literally: `doctrine-map.md:6` reads `- [kernel.md](references/kernel.md): Binding hard invariants…` — a real markdown hyperlink in the file the bundle designates as its routing surface, resolving from `beo-reference/references/` to a path that does not exist.

Disposition: **CONFIRMED**. Files changed: none.

### F034 [P2] — CONFIRMED, and the resolution to §2.11 is confirmed on the text

`sed -n '22,33p' kernel.md` read whole this turn. Item **3 is "Approval Gates": "Mutate product files only after `PASS_EXECUTE` is written to `state.json`"** — no audit trail, no parallelization, no subagent. Item **11 is "CLI Surface"**, and it ends "direct writes bypass CLI locking, validation, and the `--actor` **audit trail** that phases rely on" — the literal phrase the card invokes. Item 1 "Atomic Claim" (scout-05's alternative) is about claiming one issue at a time and does not mention audit trails either.

The disconfirming condition — item 3 carrying audit-trail language — is not met. Of the eleven invariants read in full, exactly one contains the phrase "audit trail" and it is #11.

Disposition: **CONFIRMED**, three-way scout ambiguity resolved to §2.11 on first-party text. Files changed: none.

### F035 [P2] — CONFIRMED

`git grep -n "change_request" -- skills/beo` → **3 hits, all inside `runtime-event.schema.json`**: `:10` the top-level `kind` enum, `:54` the payload contract, `:148` beo-review's `may_emit`. Zero hits in any `SKILL.md`, any reference, and any script. The disconfirming condition — any hit outside that schema — is not met anywhere in the bundle, which is a stronger result than the finding's own scope (it checked cards and references; the scripts are clean too).

Disposition: **CONFIRMED** on the documentation gap. The kernel §11 exclusivity half rests on reading the `subtype` enum against §11's scope-change rule and is a judgement about consequence, not a fact check; it is preserved at the scout's medium confidence. Files changed: none.

### F036 [P2] — CONFIRMED, and the scout's incomplete check is closed here

`git grep -n "merge" -- skills/beo/beo-reference/registry` → **exactly one hit**, `profiles.json:21`, and it is the `worktree_isolation.summary` string: "On review accept, the worktree branch is merged; on other routes, the worktree is cleaned up without merging." That is descriptive prose inside a registry, naming no actor and granting no authority; the sibling `additional_requires` is `['worktree_isolation: true in TICKET.json','requires_clean_git_tree','requires_git_worktree_command']`, three preconditions and no ownership.

**This closes the check scout-05 reported incomplete** — whether `profiles.json`'s `worktree_isolation` block already encodes merge-authority ownership. It does not. No `artifact_write_authorities` entry anywhere in `phase-contracts.json` names merge, and no `must_not` forbids it, so the highest-consequence git write in the bundle is unmodeled in both directions.

Disposition: **CONFIRMED**. Files changed: none.

### F037 [P2] — CONFIRMED

`git grep -n "claim" -- phase-contracts.json` → **1 hit**, `:150`, the atom `claim_issues` inside **`beo-reference`'s** `must_not`. There is no `br.claim` grant anywhere in the file, so the disconfirming condition is not met.

`skills['beo-plan']` parsed whole this turn: `artifact_write_authorities` is `['plan_artifact','ticket','br.child_beads','br.dependency_edges','br.decomposition_comments','br.final_route_comments','br.labels.beo_blocked_user']` — **seven** entries, five of them `br.*`-prefixed, and none of them claim. Its `must_not` is `['mutate_product_files','grant_PASS_EXECUTE','review','close']`, four atoms, none claim-related. The asymmetry the finding describes is exact: the owner names five specific `br` capabilities and omits the one its own card calls the precondition for all of them.

Disposition: **CONFIRMED**. Files changed: none.

### F038 [P2] — CONFIRMED, both halves

`git grep -n "labels" -- phase-contracts.json` → **2 hits**, `:21` and `:36`, and both are `br.labels.beo_blocked_user` — beo-plan's and beo-validate's. beo-review's `artifact_write_authorities`, parsed whole, is `['br.final_route_comments','br.close_on_verdict_accept','reservation_release','harness_proposal']`: **no label authority of any kind**. The disconfirming condition is not met.

The label-enumeration half verified independently: `grep -rn "beo:completed\|beo:abandoned" registry/` → **exit 1, zero hits in any registry file**, and `lifecycle.md:123` read in context lists exactly six advisory labels — `beo:atomic`, `beo:quick`, `beo:standard`, `beo:strict`, `beo:blocked-user`, `beo:ready-review` — while `:125` and `:126`, two and three lines later in the same section, instruct applying `beo:completed` and `beo:abandoned`. One file, one section, an enumeration its own next lines contradict.

Disposition: **CONFIRMED**. The C8-visibility consequence is correctly marked out of scope by the scout and stays there. Files changed: none.

### F039 [P2] — CONFIRMED

`sed -n '33,40p' beo-validate/SKILL.md` read this turn. The Write section's first bullet is verbatim "`state.json` phase and approval fields only **for atomic ticket validation**", and the remaining four bullets are the reservation ledger, optional check evidence under `.beads/artifacts/<issue-id>/checks/`, `br` comments and labels, and `runtime-events.jsonl` for `user_stop`. **No epic-level or plan-level `state.json` write is granted anywhere in the section**, so the disconfirming condition is not met and the `plan_validated` transition is produced by a step with no durable state write.

The receiver-phase collision is confirmed from `expected_receiver_phase_after_condition`, derived at F021: `planned → planned` and `plan_validated → planned`, identical values.

Disposition: **CONFIRMED**. Files changed: none.

### F040 [P2] — CONFIRMED, narrowed; **one source pointer in the finding is wrong**

**Pointer defect first.** The finding cites `skills/beo/templates/PLAN.template.md:99` and its disconfirming check greps that path. **That path does not exist.** `find skills/beo -name '*.template.md'` returns exactly two files, both under `skills/beo/beo-reference/templates/` — `AGENTS.template.md` and `PLAN.template.md`. Run as written the check returns nothing for the template half and silently drops a third of the finding's evidence. Re-run against the real path, the quotation verifies exactly: `beo-reference/templates/PLAN.template.md:99` reads "A child agent should be able to **claim**, validate, and implement the child from its Bead description". Same defect class as F023 — the claim is right, the pointer was not re-derived.

**Substance, and the narrowing.** `git grep -n "claim" -- lifecycle.md` → 8 hits, read whole. The three-way conflict is real: `:17`/`:22-24` say beo-plan claims and later phases do not re-claim; `:54` says pre-written tickets let each child "enter validation directly"; the template says a child agent claims. But the finding does not cite **`lifecycle.md:25`**, which is a partial scoping and does bear on its own disconfirming condition: "**Parent claim**: Covers `PLAN.md` authoring, plan handoffs, and child bead creation. Atomic child work follows the one-claimed-atomic-issue invariant." That sentence separates the parent claim from the child's, which removes the sharpest reading of the contradiction — beo-plan's claim was never asserted to cover the children — and makes the template's sentence compatible rather than contradictory.

What survives after that scoping, and it is the operative gap: `:25` says atomic child work follows the one-claimed-atomic-issue invariant and **names no actor who performs the child claim**, while `:24` reserves re-claiming to beo-plan. So a child bead created at decomposition has no stated claimer, and `:54`'s "directly" still meets beo-validate step 4's claim check.

Disposition: **CONFIRMED, narrowed** — from "three statements no two of which agree" to "the child claim has no named actor". Phase B ranking should reflect the narrower claim. Files changed: none.

### F041 [P2] — CONFIRMED

`d['expected_receiver_phase_after_condition']['decomposition_recorded']` → **`blocked`**. The disconfirming condition — that it is not `blocked` — is not met. Read together with the `route_classes.planning` membership confirmed at F019 (`decomposition_recorded` is one of that class's three members) and the `"to": "user"` edge at `pipeline.json:7` confirmed at F023, all three legs of the finding are separately derived.

The compounding is real and now rests on confirmed findings rather than on assertion: F023 (no `from: user` edge, exit 1), F024 (`reentry_rules` has only `executing`) and F027 (no owner may close the parent).

Disposition: **CONFIRMED**. Files changed: none.

### F042 [P2] — CONFIRMED

`sed -n '100,110p' lifecycle.md` read this turn. `:104` is the scoping note — "Repair boundary is canonical in `references/kernel.md` (§11)" — and it scopes the **repair boundary**, not the route enumeration. The next line, `:106`, then makes an unqualified global claim: "`beo-review` emits exactly one route. Final verdict routes are accept, repair same scope, repair rescope, cannot deliver, or abandoned; `root_cause_diagnosis_needed` is a non-final diagnostic handoff route." Six named.

`phase-contracts.json`'s `skills['beo-review']['may_emit_delivery_conditions']` parsed whole: `['verdict_accept','repair_same_scope','repair_rescope','cannot_deliver','abandoned','root_cause_diagnosis_needed','harness_change_needed','user_review_needed']` — **8**. The two absent from the prose are `harness_change_needed` and `user_review_needed`, exactly as filed.

The disconfirming condition — the sentence being scoped rather than global — is not met: the scope note governs the sentence above it, and the enumeration sentence carries no qualifier.

Disposition: **CONFIRMED**, 6 versus 8 re-derived on both sides. Files changed: none.

### F043 [P2] — CONFIRMED as filed, with its declared limit intact

`git grep -n "approved_prestate" -- skills/beo` → **2 hits, both in `approval-envelope.json`**: `:9` the predicate `approved_prestate_unchanged` and `:28` the invalidator `approved_prestate_changed`. No card, no reference, and no other registry file mentions the predicate at all, so **nothing anywhere scopes it to execution start** and the disconfirming condition is not met.

The scout's own limit is preserved and is the honest ceiling on this row: whether a script carve-out exists is `beo_check.py`'s business and is S3b's scope, not this pass's. What is established here is that the *doctrine* states no exemption, and that `pipeline.json:124` exempts only dirty-path classification — a neighbouring exemption that exists, is written down, and does not cover this predicate.

Disposition: **CONFIRMED** on the doctrine surface. The script question is **BLOCKED, owner S3b**. Files changed: none.

### F044 [P2] — CONFIRMED, substantially narrowed; **two of three revocation classes do have a named format**

`git grep -n "revocation\|revoked" -- skills/beo` → **29 hits**, and the disconfirming condition ("a revocation record format is named") is **met for two of the three named invalidators**:

- `strict_reservation_revoked_or_superseded` — `reservation-schema.json:118-130` carries an `if status == "revoked"` branch that **requires** `revoked_by` (non-empty string) and `revocation_ref` (non-empty string) and nulls `superseded_by`. That is a named, schema-enforced revocation record.
- `human_gate_revoked` — `ticket.schema.json:113` gives every entry of `human_gates.gates[]` its own `revocation_ref` field. A location is named.
- `external_authorization_revoked` — **nothing.** Its subject is `strict.authorization_refs` (`ticket.schema.json:125`), an array of opaque non-empty strings with `minItems: 1` and **no revocation field, no status, and no companion structure anywhere**. This is the one class where the finding's "no file says where an explicit revocation lives" holds literally, and it is precisely the class that reaches outside the repository — the same untrusted-external-reference surface F005 flags.

The finding's own redundancy argument survives and applies to the middle case: `revocation_ref` living inside `TICKET.json` means writing one changes `ticket_file_hash` and fires `ticket_file_hash_changed`, so `human_gate_revoked` is a duplicate of the generic hash invalidator rather than an independent check.

The "what makes a `br` comment a revocation" question also survives untouched: `approval-envelope.json:45` forbids inferring revocation from ordinary comments and labels, `user-handoff.md:45` permits `br-comment:<id>` as a durable evidence ref, and no file states a distinguishing convention.

Disposition: **CONFIRMED, narrowed** — from "no file says where an explicit revocation lives" to "one of three invalidators has no record format, and a second is redundant with the hash check". The headline as filed is not supportable. Phase B should re-rank accordingly. Files changed: none.

### F045 [P2] — CONFIRMED on the doctrine surface

`git grep -n "repo_head" -- skills/beo` → **24 hits**. Partitioned by scope: **10 in doctrine** — `approval-envelope.json:8,27,53,72`, `state.schema.json:22,29`, `quick-mode-golden-trace.md:57,98` — and 14 in `scripts/`, which are S3b's. Read across all ten doctrine hits, `repo_head` is declared as a projection field, an invalidator, a schema type (`["string","null"]`) and a trace value, and **not one of them states which HEAD it binds to** under worktree isolation. `kernel.md` §7, read at F036's neighbourhood, creates the worktree before `PASS_EXECUTE` and does not mention `repo_head` at all.

The disconfirming condition — the binding being stated — is not met anywhere in scope.

Disposition: **CONFIRMED**. The scout's deferral of `repo_head_sentinel(root)` is correct and stands: `beo_io.py:45` is S3b's, and the question of what `root` resolves to under a worktree is **BLOCKED, owner S3b**. Files changed: none.

### F046 [P2] — CONFIRMED at its own low-medium confidence

`sed -n '103,115p' kernel.md` read whole this turn. §10 has seven numbered items; item 6 is verbatim "**Invariant preservation**: Harness changes must not weaken the hard invariants in this kernel. `beo-author` must verify this before applying." **No check is named** — not a command, not a script, not a procedure — and none of the other six items supplies one: item 2 restricts the target path, item 3 says only beo-author applies, item 5 forbids authority expansion in the same assert-without-mechanism shape. The disconfirming condition is not met.

The scout's own negative result is preserved and is why this stays low-medium: `harness-proposal.schema.json`, read at F015, carries no approval-shaped fields, so the sharper version of the concern is not realized at this head.

Disposition: **CONFIRMED**. Files changed: none.

### F047 [P2] — CONFIRMED, both halves

`grep -n "command-manifest" doctrine-map.md` → **exit 1, zero hits**, in a file `wc -l` gives as **33 lines**. The routing surface never names the reference that answers "which helper script answers this question", so the disconfirming condition is not met.

`doctrine-map.md:20` read in context: "| Is `PASS_EXECUTE` still valid? | `registry/approval-envelope.json` | Approval validity predicates and invalidation reason | Memory docs |". The Load-exactly cell names one file and the Never-load cell names memory; no script and no computation procedure appears in the row, and `approval-envelope.json` supplies predicate names only — confirmed at F006, where `computed_projection_fields` is `['ticket_file_hash','repo_head']` with no algorithm attached.

Disposition: **CONFIRMED**. Files changed: none.

### F048 [P2] — CONFIRMED

`sed -n '7,16p' beo-execute/SKILL.md` read whole. The `## Read` section has seven bullets: the kernel §17 anchor, `bv` robot output, `br ready --json`, `registry/approval-envelope.json`, `registry/state.schema.json`, `registry/profiles.json`, and `scripts/beo_worktree.py`. **`registry/reservation-schema.json` is not among them**, so the disconfirming condition is not met.

`context-budget.md:44` read in context is the implementation phase's high-risk row: "normal + `references/kernel.md`, `registry/reservation-schema.json`, `beo_worktree.py`". The two files it adds beyond the card are kernel and the reservation schema; the card carries `beo_worktree.py` already. So the divergence is exactly one file, and it is the one the subordinate document marks required.

Disposition: **CONFIRMED**. Files changed: none.

### F049 [P2] — CONFIRMED

`sed -n '73,86p' kernel.md` read whole. §7.5 is verbatim "**Cleanup**: Worktree is always cleaned up on terminal routes (accept, cannot_deliver, abandoned) **and repair routes**" — unconditional, with no preservation, snapshot, or confirmation step anywhere in the seven items. The disconfirming condition is not met.

§7.6 read in the same block sharpens the finding's own solution hypothesis rather than the defect: "If a worktree already exists for the same issue (e.g., agent re-entry), the existing worktree is **reused**." So the bundle already states a reuse rule for re-entry, and §7.5's repair-route cleanup destroys the thing §7.6 would otherwise reuse — the two items are in tension inside one section.

Disposition: **CONFIRMED**. Whether the loss is recoverable turns on `beo_worktree.py cleanup`'s branch handling: **BLOCKED, owner S3b**. Files changed: none.

### F050 [P2] — CONFIRMED

`sed -n '49,68p' artifact-boundaries.md` read whole this turn. The "Validation asymmetry" subsection states, in the bundle's own words: "`beo_state.validate_state` currently does not enforce the 'must not change phase or approval fields' rule on intervention entries", followed by three bullets including verbatim "An intervention touching approval fields is not rejected (**caller discipline only**)" and closing "These are known limitations; callers must exercise discipline". The text still disclaims enforcement, so the disconfirming condition is not met.

The same subsection independently corroborates F050's temporal half — "An intervention with `recorded_at` before the current `phase` started is not rejected" — and the `trace_id` literal-equality claim.

Disposition: **CONFIRMED** on the documented gap. Whether `beo_state.py` in fact checks it, which would make the prose the bug instead, is **BLOCKED, owner S3b**, as the scout marked it. Files changed: none.

### F051 [P2] — CONFIRMED as an inconsistency; the consequence stays unresolved

`protected_path_defaults` derived whole this turn: **14 entries** (the same 14 counted at F008), listed in file order as `.git/**`, `.env`, `.env.*`, `**/.env`, `**/.env.*`, `secrets/**`, `credentials/**`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa`, `id_ed25519`, `.beads/**`.

The asymmetry is exact as filed: `.env` appears in **four** forms — bare, suffixed, and both `**/`-prefixed — while the eight secret patterns that follow (`secrets/**` through `id_ed25519`) have **no `**/` sibling at all**. Whoever wrote the `.env` entries understood that a bare pattern misses nested paths and applied that understanding to one family of nine and not to the other eight.

Disposition: **CONFIRMED** as a list-internal inconsistency. Whether it is exploitable depends entirely on the matcher's semantics in `beo_paths.py`: **BLOCKED, owner S3b**, and the finding's own confidence is medium for that reason. Files changed: none.

### F052 [P2] — CONFIRMED

`git grep -n "glob" -- skills/beo`, filtered to non-script files, → **13 hits**, read individually, and **none defines when a glob is broad**:
- `kernel.md:26` states the gate requirement; `kernel.md:130` and `lifecycle.md:89` require *non*-glob scope for fast track, a different rule.
- `safety.md:21` advises "Prefer exact file paths over broad directory globs" — advice, no threshold — and `:23` gives the runtime error string plus the gate type `broad_scope_authorization`, and defers: "mode requirements are canonical in `registry/profiles.json`".
- `doctrine-map.md:21` routes the decision to `profiles.json`.
- `profiles.json:8` says fast track needs "explicit (non-glob) file scope" and defines nothing about breadth. **The file both `safety.md:23` and `doctrine-map.md:21` name as canonical contains no threshold, no pattern class, and no count rule.**
- `pipeline.json:142` and `state.schema.json:44` carry the condition `unauthorized_broad_glob` as a token; `user-handoff.md:28` routes it; `ticket.schema.json:193` implements the fast-track no-`*`-or-`?` check; `beo-validate/SKILL.md:13,24` consume the rule without stating it.

So the vocabulary exists at nine sites, the enforcement string exists, the routing exists, and the definition exists nowhere. The disconfirming condition is not met.

Disposition: **CONFIRMED**. Files changed: none.

### F053 [P2] — CONFIRMED

`sed -n '8,22p' degraded-tools.md` read whole. The Tool requirements table has **8 rows**: `br` (Required), PyYAML (Required), `bv`, `qmd`, Obsidian, `beo_verify.py`, `beo_score_trace.py`/`beo_score_context.py`, `beo_audit.py`/`beo_propose.py` — the last six all Optional. Counting the scripts named, that is **5 of the bundle's 17**, matching the headline.

`beo_reservation.py`, `beo_worktree.py` and `beo_check.py` appear in **no row**, so the disconfirming condition is not met. All three are load-bearing by their own cards: `beo-validate/SKILL.md:16` and `:30` for worktree creation, `:37` for reservation create/supersede, and `beo-review/SKILL.md:14` for the pre-`verdict_accept` mechanical check.

The pattern in the five rows that *are* classified is worth naming for Phase B: every one of them degrades to "skip and continue". None of the three unclassified scripts can degrade that way without disabling a gate, which is precisely why their absence from the table is not a harmless omission.

Disposition: **CONFIRMED**. Files changed: none.

### F054 [P2] — CONFIRMED, every leg re-derived

The description line read this turn at `beo-author/SKILL.md:3` is verbatim: "Maintain BEO control-plane files: skill cards, references, registries, templates, scripts, and ADRs. Use when modifying BEO workflow rules or contracts. No product delivery authority." No token of scan, audit, drift, triage, or maintenance-scan appears in it.

`kernel.md:95`, read in context, is §9 "Maintenance Scan Policy" and assigns the responsibility explicitly: "`beo-author` owns mechanical maintenance scans of BEO harness files and triages their findings."

`git show ba85daf -- skills/beo/beo-author/SKILL.md | grep -n "^[+-]description"` → **exit 1, no hunk**, confirming the fold commit (`ba85daf refactor(beo): fold beo-climate into beo-author as the single maintenance owner`) never touched the frontmatter description. `grep -rni climate skills/beo/` → **exit 1, zero hits**, so nothing lexical survives of the folded skill and the gap is purely semantic.

This is the memory-recorded Tier 4 outcome of 2026-09-03 leaving a residue, and it is a genuine one-line fix.

Disposition: **CONFIRMED**. Files changed: none.

### F055 [P2] — CONFIRMED

`grep -n "beo-setup" beo-reference/templates/AGENTS.template.md` → **exit 1, zero hits**. `:6` read whole: "- Supporting skills: `beo-debug` (when blocked), `beo-learn` (capture notes), `beo-reference` (read-only lookup), `beo-author` (maintain BEO itself). Load via `skills/beo/<name>/SKILL.md`." Four of nine cards, including the sibling maintenance owner, excluding the one that writes this very file.

Disposition: **CONFIRMED**. The finding correctly keeps itself on the template; `AGENTS.md` is out of scope for this pass by the report's own restriction and was not read from the working tree. Files changed: none.

### F056 [P2] — CONFIRMED

`git grep -n "allow_all_explicit" -- skills/beo/beo-reference/registry` → **exactly 1 hit**, `profiles.json:9`, the `additional_requires` string itself. The token appears in `ticket.schema.json` **zero times**, so the disconfirming condition — the field existing in the schema — is not met, and the precondition names a field the ticket contract cannot carry.

`ticket.schema.json:193`, read at F026, is the mechanism that actually exists: "Fast track requires explicit file paths, no globs", enforced by `{"not": {"pattern": "[\\*\\?]"}}` on each `allow` item. The registry states the precondition in a vocabulary the schema does not use, for a check the schema already implements under a different name.

Disposition: **CONFIRMED**. Files changed: none.

### F057 [P2] — CONFIRMED; the site count corrected upward

`git grep -n "worktree_isolation" -- skills/beo`, scripts excluded, → **9 hits**. One is the schema: `ticket.schema.json:126`, and reading `:119-128` confirms it sits inside `strict`'s `properties` block, so the real path is `strict.worktree_isolation`. The other **eight are prose or registry-prose**, and **not one writes the qualified path**:

`profiles.json:20` (the block key) and `:22` ("worktree_isolation: true in TICKET.json"); `beo-execute/SKILL.md:15` and `:21`; `beo-validate/SKILL.md:16` and `:30`; `beo-review/SKILL.md:12` and `:30`. The disconfirming condition is not met.

The headline says "five prose sites"; the derived count is **eight**, seven of them if `profiles.json:20`'s bare block key is excluded as structural. The finding's own source-pointer line lists seven, so the headline disagrees with the finding's own enumeration — the third instance of the C16 count defect in this report, after F023 and F040's bad path.

Disposition: **CONFIRMED**, count corrected 5 → 8. Files changed: none.

### F058 [P2] — CONFIRMED

Derived from the parsed schema this turn: `execution.properties.verify_results` is `{'type': 'array', 'items': {'type': 'object'}}` and `execution.properties.interventions` is **the identical value**. Neither constrains a single key. The disconfirming condition — items being typed — is not met for either field.

The compounding with F009 is real and correctly noted by the scout: the typed side of the pair lives in `runtime-event.schema.json`, which F009 confirmed has no `$defs` and a bare `{'type': 'object'}` payload, so the "fully typed twin" is itself inert at this head. The defect is therefore weaker than "durable side is looser than the enforced side" — **neither side is enforced** — and stronger as a description of the bundle's overall typing posture.

Disposition: **CONFIRMED**, with the F009 interaction restated. Files changed: none.

### F059 [P2] — CONFIRMED

`grep -l '"\$schema"' registry/*.json` → **5 files, all of them `*.schema.json`**: `harness-proposal`, `runtime-event`, `reservation-schema`, `ticket`, `state`. The four plain-data files — `approval-envelope.json`, `phase-contracts.json`, `pipeline.json`, `profiles.json` — appear in none, so the disconfirming condition is not met.

The observation earns its P2 from this pass's own results rather than from argument: of the 45 findings dispositioned before it, the defects located **inside those four unvalidated files** include F004, F006, F007, F008, F016, F017, F019, F021, F023, F024, F026, F027, F031, F037, F038, F041, F042, F043, F044, F046, F051, F052 and F056. The four files with no machine check of their own are where this campaign is finding most of its contract defects.

Disposition: **CONFIRMED**. Files changed: none.

### F060 [P2] — CONFIRMED

Both enums parsed from `state.schema.json` this turn. `review.findings.items.properties.recommended_route` is `['repair_same_scope','repair_rescope','cannot_deliver','root_cause_diagnosis_needed','none']` — five values, one of which (`none`) is a sentinel rather than a route, so **four real routes**. Its sibling `review.route_condition_id` is `['verdict_accept','executed_and_verified','harness_change_needed','repair_same_scope','repair_rescope','cannot_deliver','root_cause_diagnosis_needed','abandoned','user_review_needed', None]` — nine routes plus null. The disconfirming condition (the enums matching) is not met.

The three the finding names as missing — `harness_change_needed`, `user_review_needed`, `abandoned` — are confirmed absent, and the derivation adds two the finding does not mention: `verdict_accept` and `executed_and_verified` are also absent, which is coherent (a *finding* would not recommend acceptance) and worth stating so the gap is not overcounted. The real deficit is **three** routes a finding cannot recommend, exactly as filed.

Read against F042, confirmed above, the two are the same shortfall from opposite directions: prose offers 6 of 8 emittable routes, this enum offers 4 of the 7 a finding could sensibly recommend.

Disposition: **CONFIRMED**. Files changed: none.

## P3 band, F061-F094

The report's own `## Coverage And Derivation` section at `:1833` discloses that this band was drafted from context rather than from disk, and that seven rows were re-patched against the candidate file afterwards. Every row below therefore re-derives its evidence from the working tree regardless of what the finding asserts, and pointer accuracy is treated as an open question rather than a given.

### F061 [P3] — DUPLICATE of F024, on a different phase

`list(d['reentry_rules'])` → `['executing']`, the same single key derived at F024, and `expected_receiver_phase_after_condition['executed']` → `reviewing`, so the structural claim is true: `reviewing` is a receiver phase with no re-entry rule.

But it is **the same defect as F024, not a second one.** F024's claim is that `reentry_rules` has one key while eight of seventeen conditions land in `blocked`; F061's is that the same one key leaves `reviewing` uncovered. One root cause — `reentry_rules` covers one of the machine's phases — one fix, and the same disconfirming check verbatim.

Disposition: **DUPLICATE**, survivor **F024**. The `reviewing` phase is folded into F024's scope for Phase B: the fix is `reentry_rules` coverage for every non-terminal receiver phase, not a `blocked` key alone. Files changed: none.

### F062 [P3] — CONFIRMED

`git grep -n "close_reason\|--reason" -- skills/beo` → **12 hits**, and `close_reason` appears **zero** times. The `br close --reason` vocabulary derived from the hits is **three distinct spellings for the same act**:
- `--reason done` — `beo-plan/SKILL.md:31`, and `beo_run.py:192` in the script layer.
- `--reason "Completed"` — `lifecycle.md:33`, `:125`, `:128`, and `PLAN.template.md:54`.
- no `--reason` at all — the golden trace's `br close br-101 --json`, which the finding cites and which the grep does not surface because it has no flag to match.

The remaining hits are a different command's flag (`beo_worktree.py cleanup --reason accepted|repair|<route>` at `beo-review/SKILL.md:31-33`, plus the two argparse definitions), which is worth separating: those three values are at least drawn from a route-shaped set, while the `br close` reasons are free prose. No enum, no schema field, and no registry list constrains either.

Pointer note: the finding's `templates/PLAN.template.md:54` is again written without the `beo-reference/` segment (the F040 defect), but the line number and quotation verify exactly at the real path.

Disposition: **CONFIRMED**. Files changed: none.

### F063 [P3] — CONFIRMED on the structural claim; **both counts in the finding are wrong**

The structural claim holds: `caller` appears **7 times** in `pipeline.json` and is never a node in `transitions`, never a key in `expected_receiver_phase_after_condition`, and never defined in any prose file. Two of the seven are the unrelated keys `callers` and `harness_proposal_callers`.

**The counts are not derived.** The headline says "Four non-owner skills return to caller"; the evidence sentence names **five** (`beo-debug`, `beo-learn`, `beo-author`, `beo-reference`, `beo-setup`); the contract-violated line says the destination is "used **12 times** in the routing table". Derived this turn by parsing the three non-delivery sections:
- `support_subroutines`: `beo-debug` has `callers` and `transitions` — **2** `to: caller` edges; `beo-learn` has `entry_conditions`, `authority`, `outcomes` and **no transitions block at all**.
- `maintenance_skills`: `beo-author` has `transitions` — **3** `to: caller` edges (the fourth routes to `user`, per F031); `beo-setup` has `outcomes` only.
- `lookup_skills`: `beo-reference` has `outcomes` only.

So the real figures are **2 skills and 5 edges**, not four or five skills and not twelve edges. Three of the five skills the evidence names have no transitions in the file to route anywhere. This is the fourth count defect found in this report.

Disposition: **CONFIRMED** on the undefined destination, counts corrected to 2 skills / 5 edges. Files changed: none.

### F064 [P3] — CONFIRMED

`degraded-tools.md` read from `:1` through the tool table this turn. The framing is permissive throughout: `:6` "This file guidance focuses on setup checks. Authority invariants are canonical in `references/kernel.md`", then "BEO delivery **can** run when:" and "BEO delivery does **not require**:" — capability statements, not obligations. Every "If missing" cell in the table is an imperative fragment ("Block BEO delivery readiness.", "Use `br ready --json`…", "Skip score events…") with no rule language binding an agent to it, and the file explicitly disclaims authority in favour of a kernel that, per this finding, has no degraded clause among its eleven invariants — verified against the full §2 list read at F034, where none of the eleven concerns tool availability.

Disposition: **CONFIRMED**. Pairs with F053 as filed. Files changed: none.

### F065 [P3] — CONFIRMED, and far more strongly than filed; **the finding's own check is malformed**

The finding's disconfirming check reads `a.get('invalidators')` at the **top level** of `approval-envelope.json`. There is no top-level `invalidators` key — the file's root keys are `['description','validity_model','approval_fields','ticket_projection_fields','included_when_present_ticket_projection_fields','computed_projection_fields','standard_ticket_projection_additions','strict_ticket_projection_additions','strict_evidence_projection_additions','execution_start_definition','contract_hash_policy']` — so the check as written prints `None` and proves nothing. The real path is `validity_model.invalidators`.

Re-derived from the right path, the result is stronger than the finding claims. `invalidators` holds **11** values; `approval.failure_category` holds **15** non-null values; and the set intersection is **empty**. Not "overlapping but non-identical" — **literally zero tokens in common**:
- 11 invalidator-only, including `ticket_file_hash_changed`, `approval_projection_hash_changed`, `repo_head_changed`, `approved_prestate_changed`, and all four strict revocation predicates.
- 15 category-only, including `claim_mismatch` (against the invalidator `claim_invalid`), `issue_closed` and `issue_blocked` (against the single invalidator `issue_closed_or_blocked`), and `strict_reservation_missing` (against `strict_reservation_revoked_or_superseded`, which is a different fact).

So an approval invalidated by any of the eleven named causes has **no** `failure_category` that names that cause; the nearest matches differ in wording, in granularity, or in meaning. F018's proposed fix — a category naming reservation supersession — is confirmed unavailable.

Disposition: **CONFIRMED**, upgraded from "overlapping but non-identical" to "disjoint", check corrected. Files changed: none.

### F066 [P3] — CONFIRMED; two of the finding's three specifics are wrong

All nine `must_not` arrays printed this turn. The drift is real and pervasive. But:

- The finding says "**Six** skills forbid granting approval as `grant_PASS_EXECUTE`". Derived: **seven** — beo-plan, beo-review, beo-debug, beo-learn, beo-author, beo-setup, beo-reference. beo-execute uses `approve`, and **beo-validate has no such atom at all**, correctly, since it is the granter. So the correct statement is 7 of the 8 non-granting owners agree and 1 dissents.
- The finding names the closure family as "`review`/`close`/**`close_beads`**". `git grep -n "close_beads" -- skills/beo` → **exit 1: the token does not exist anywhere in the bundle.** The real closure drift is `close` (seven skills), `close_non_accepted_work` (beo-review) and `close_delivery_issue` (beo-author) — three spellings, none of them `close_beads`.
- The review family drifts too, which the finding does not mention: `review` (six skills), `review_product_ticket` (beo-author), `issue_review_verdicts` (beo-reference), `alter_review_verdict` (beo-learn).

Disposition: **CONFIRMED** on the class, with the count corrected 6 → 7, a non-existent token struck, and a third drifting family added. The F059 link is exact: these are free strings in one of the four files with no `$schema`. Files changed: none.

### F067 [P3] — CONFIRMED, and it is worse than one base

`grep -n "references/\|registry/" skills/beo/README.md` → **8 hits in a 71-line file**, and they use **two different bases**:
- `:12`, `:54`, `:56`, `:57`, `:58`, `:59`, `:60` all write `beo-reference/references/<file>` or `beo-reference/registry/` — resolvable from `skills/beo/`, not from the repository root where a README is read.
- `:71` writes bare `references/command-manifest.md` **twice in one line** — resolvable from neither `skills/beo/` nor the repo root; it is the `beo-reference/`-relative form F033 documents.

So the entry document mixes the two conventions inside itself, and the second appears in the sentence that tells an operator where the helper index lives.

Disposition: **CONFIRMED**, same class as F033 as filed, with the internal inconsistency added. Files changed: none.

### F068 [P3] — CONFIRMED

`git grep -n "beo-verify" -- skills/beo` → **6 hits**. One is the doctrine defect: `safety.md:46`, where the token appears **twice in that single line**, both times in backticks and both times adjacent to the real skill names `beo-validate` and `beo-debug` in identical styling. The finding's "both occurrences" is accurate — they are on one line, not two.

The other five are legitimate and confirm the finding's own "naming drift, not a dead reference" framing: `runtime-event.schema.json:15` and `:157` register `beo-verify` as a **helper actor** id, `beo_audit.py:31` lists it in `HELPER_ACTORS`, and `beo_verify.py:32-33` sets `HELPER_VERSION = "beo-verify/v1"` and `ACTOR = "beo-verify"`. So the hyphenated string is the script's actor identity, and `safety.md:46` uses that identity in a sentence about routing and recovery where every neighbouring token is a skill.

Disposition: **CONFIRMED**. Files changed: none.

### F069 [P3] — CONFIRMED

`git grep -n "logs/" -- skills/beo` → **exactly 1 hit**, `user-handoff.md:44`, `.beads/artifacts/<issue-id>/logs/<file>`. One occurrence in the entire bundle, cards, references, registries, templates, examples and scripts included. No `artifact_write_authorities` entry produces it, `artifact-boundaries.md` does not enumerate it, and the golden trace uses `checks/` throughout.

Disposition: **CONFIRMED** at its filed low-medium — the defect is real and its consequence is genuinely small. Files changed: none.

### F070 [P3] — **NOT CONFIRMED**

The finding claims `beo-reference`'s description "invites treating it as a rule owner". `sed -n '1,8p' beo-reference/SKILL.md` read this turn, and the description says the opposite in its own first two words and three times more after them: "**Read-only lookup** for BEO doctrine, registries, command authority, transitions, schemas, and safety invariants. Use for BEO rule/schema questions, **not delivery execution, approval, or review**. **Never mutates delivery state.** Routes operators to the right helper…". "Doctrine" is the *object* of the lookup, not a claim to own it, and the sentence that follows it excludes three authorities by name.

The nearest thing to the concern is a token the finding does not cite: `:7` reads "**Canonical** lookup router: `references/doctrine-map.md`." That applies "canonical" to the router role rather than to rule ownership, and `doctrine-map.md` is the file it points at — which is the correct owner. It is at most a word choice worth tightening, not a routing hazard.

Disposition: **NOT CONFIRMED**. The premise is not supported by the text at this head. Files changed: none.

### F071 [P3] — CONFIRMED

`sed -n '1,30p' beo-debug/SKILL.md` read whole. The description is scoped verbatim to "BEO **execution or review** blockers", and the `## Input` section restricts invocation to `beo-execute`, `beo-review`, or an operator — **beo-validate is not a permitted caller and validation failure is not a named blocker class**. The `Output` contract returns `recommended_next_route` to a "calling BEO owner" that, by that same Input section, can never be beo-validate.

So `validation_failed -> beo-plan` routes a failure back to the ticket author with no diagnostic owner anywhere in the bundle, and the loop it belongs to is the one F022 confirmed has no counter of any kind — not even the visibility-only one the repair loop has.

Disposition: **CONFIRMED**. Files changed: none.

### F072 [P3] — CONFIRMED as a class; **the finding cites no pointer and names neither collision pair**

The finding asserts "two collision pairs were identified concretely" and then identifies neither, gives no line reference, and quotes no description. That is not a checkable claim as written, so the class was re-derived from the source: all nine `description:` lines read this turn from `sed -n '3p' skills/beo/*/SKILL.md`.

The overlap is real. The clearest pair: **beo-author** — "Maintain BEO control-plane files: skill cards, references, **registries**, templates, scripts, and ADRs" — against **beo-reference** — "Read-only lookup for BEO doctrine, **registries**, command authority, transitions, schemas". One shared trigger noun, two skills, and the authority difference between them is total: one may rewrite the registries, the other may not mutate anything. A second: **beo-debug**'s "Diagnose BEO **execution or review** blockers" shares both delivery-phase nouns with the cards that own those phases.

Counterweight, and it is why this stays P3: seven of the nine descriptions carry an explicit negative clause ("Never approve, review, or close", "No product delivery authority", "Never mutate product files"), so the authority difference *is* stated on the selection surface even where the trigger nouns collide. The exception is F054's gap in the same layer.

Disposition: **CONFIRMED** on the derived pair, with the finding's own evidence recorded as unciteable. Files changed: none.

### F073 [P3] — CONFIRMED, and the gap is wider than filed

`PLAN.template.md` has a `## Risks` section at `:72` with a four-column table (`Risk | Impact | Mitigation | Affects decomposition?`) at `:74-76`.

`grep -n -i "risk" beo-validate/SKILL.md` → **1 hit**, `:22`, the epic/feature plan-validation step. Read whole, it enumerates roughly a dozen criteria — parent bead reference, goals and non-goals, completion criteria, assumptions, brainstorm/options, scope boundaries, verification strategy, proposed atomic beads — and its only "risk" token is **"suggested mode/risk"** for the *child* beads. The parent's Risks table is checked by nothing.

The widening: the template's **own** `## Plan validation summary` at `:162-179` lists eleven things the summary must state, and the Risks table is not among those either. So the section is required by the template, omitted from the template's own self-check, and omitted from the validator's criteria — three chances to consume it, taken zero times.

Disposition: **CONFIRMED**. Files changed: none.

### F074 [P3] — CONFIRMED, with a third site the finding does not name

`grep -n "beo-plan" beo-reference/templates/PLAN.template.md` → **2 hits**, both behavioral rather than document-shape:
- `:99` — "with enough detail that `beo-plan` can copy or lightly normalize it into `br create --description` without reinterpreting the parent plan".
- `:140` — "When creating child Beads, `beo-plan` **should** normalize heading depth for rich markdown rendering in `br --description`/`bv`, not wrap the description in a code fence."

`:140` is the sharper of the two: it is an unqualified behavioral instruction to a skill, using rule language, living in a document template.

The third site, which the finding does not name and which is addressed to a **different** skill: `:180` reads "`beo-validate` **must** validate the actual PLAN content, not trust this summary alone. The summary is planning evidence, not validation authority." That is a validation-authority rule — arguably the sharpest statement of it anywhere — stated in a template rather than in `beo-validate/SKILL.md` or the kernel.

Disposition: **CONFIRMED**, scope widened from one skill to two. Files changed: none.

### F075 [P3] — CONFIRMED at its filed low weight

`grep -n -i "route\|condition" PLAN.template.md` → **2 hits**, both restating registry routing inside a document template: `:154` "Any blocking open decision **routes** `user_review_needed`" and `:178` "user/operator-owned blockers **route** `user_review_needed` instead of `plan_validated`".

Both are consistent with `pipeline.json` at this head, so nothing is contradictory today; the defect is exactly the ownership one filed — a routing rule with a second home that can drift. Read with F074, the same template now carries behavioral instructions for two skills and routing rules for a third owner.

Disposition: **CONFIRMED**. Files changed: none.

### F076 [P3] — CONFIRMED

`grep -n -i "clos" quick-mode-golden-trace.md` → **3 hits**. Two are the `closed_in_br` state field at `:77` (false) and `:179` (true). The third is the defect: `:194`, under the heading "Expected br action", reads "Close only after `verdict_accept` (**helper executes** `br close br-101 --json`)."

The parenthetical is the whole finding and it is accurate as filed: Hard Invariant #9, read in full at F034, is "Only `beo-review` may close accepted work through `br` (strictly via `verdict_accept`)" — beo-review is the actor and `br` is the mechanism. The trace names a helper as the executing party. The sentence's first clause does preserve the gate ("only after `verdict_accept`"), which is why this is P3 and not higher.

Disposition: **CONFIRMED**. Files changed: none.

### F077 [P3] — CONFIRMED, and **the direction is inverted: it is no longer near-disconfirmed**

The scout filed this as almost certainly nothing, pending F086. Deriving F086 first changed the answer.

`ticket.schema.json:52` states the evaluation contract explicitly: "Each verify command is exec'd directly via **execve (shell=False, no shell)**. Pipes, redirects, `&&`, `||`, `;`, and env-var expansion are NOT supported."

The trace's command, at `:37` and again at `:146`, is `grep -i 'receive' README.md` — **single-quoted**, which is a shell quoting construct. Under `shell=False` the quotes are not interpreted by any shell, so whether the command works depends entirely on how the string is split into argv: a shlex-style split strips them and the command works; a naive whitespace split hands `grep` the literal pattern `'receive'`, which would not match. The trace records `exit_code: 0` and `stdout: "Please receive updates."` at `:146-148`, a result reproducible **only** under the quote-stripping splitter.

So the bundle's one worked example models a command shape whose behaviour is not determined by the contract the schema states, and the example's own recorded output silently assumes one of the two possible answers.

Disposition: **CONFIRMED**, upgraded from "near-disconfirmed" to a live inconsistency between the golden trace and `ticket.schema.json:52`. Which splitter is used is `beo_verify.py`/`beo_run.py` business: **BLOCKED, owner S3b**. Files changed: none.

### F078 [P3] — CONFIRMED, and sharper than filed

`doctrine-map.md` read whole, 33 lines. The "Rule ownership" section is the entire precedence statement and it reads: "`references/kernel.md` is the canonical owner of BEO rules and invariants. **Other markdown references in the `references/` directory** are subordinate to `references/kernel.md`."

The scope of that sentence is **markdown references only**. It says nothing about the five `*.schema.json` files or the four plain-data registries — and the registries are the documents this bundle repeatedly declares win for anything a machine checks. So the file that owns precedence declares it for the subordinate half of the corpus and is silent on the half where the conflicts actually occur.

That silence is not hypothetical: F028 is exactly a kernel-versus-`pipeline.json` conflict, and this pass had to adopt a direction for it on evidence because no precedence rule settles it. F019 (`pipeline.json` prose instructing an out-of-enum phase) and F048 (§17 saying the card wins while the subordinate file carries the stricter requirement) are two more.

Disposition: **CONFIRMED**, with the ambiguity located precisely: the subordination clause covers markdown and omits the registries. Files changed: none.

### F079 [P3] — CONFIRMED

`git grep -n "superseded" -- skills/beo`, scripts excluded, → **12 hits**, and the harness-proposal `status` enum at `harness-proposal.schema.json:48` is the **only** appearance of the token in that artifact's world. Every other hit belongs to the **reservation** lifecycle — `reservation-schema.json` `:15`, `:47`, `:57`, `:81`, `:96`, `:105`, `:112`, `:116`, `:126`, plus `safety.md:35` and `approval-envelope.json:31` — where supersession is fully modelled: a `superseded_by` field with pattern `^res-[a-f0-9]{8}$`, required when `status == "superseded"`.

So the bundle knows how to model supersession, does it thoroughly for reservations, and for harness proposals declares the status with no writer, no pointer field, and no card instruction. Same orphan-enum class as F025 as filed; a different artifact and a different enum, so it is not a duplicate of it.

Disposition: **CONFIRMED**. Files changed: none.

### F080 [P3] — CONFIRMED exactly

Derived by set difference this turn: the `condition_id` values appearing in `transitions` are 17 distinct tokens; the union of all nine `route_classes` buckets covers 16 of them. The single uncovered condition is **`executed`**, and the reverse difference is empty — no class member lacks a transition. Exactly the claim, exactly one token, no over- or under-statement.

Disposition: **CONFIRMED**. Files changed: none.

### F081 [P3] — CONFIRMED; **the finding's check names a key that does not exist**

`d.get('forbidden_normal')` → **`None`**. There is no top-level `forbidden_normal` key, so the check as written proves nothing — the second malformed check in this band after F065's.

The real key is `runtime_event_policy.forbidden_normal_event_conditions`, derived whole: `['planned','plan_validated','PASS_EXECUTE','executed','executed_and_verified','verdict_accept']` — **6** conditions, alongside `write_only_for_non_normal_events: true`. `decomposition_recorded` is absent, so the substantive claim survives the malformed check.

Whether the omission is a defect depends on F041's unresolved classification, exactly as the finding says: `decomposition_recorded` is bucketed as a planning *success* (F019's `route_classes.planning`) yet routes to `user` and lands the parent in `blocked` (F041, confirmed). If it is a normal-path condition it belongs on this list; if it is a terminal handoff it does not.

Disposition: **CONFIRMED** at its filed low-medium, key corrected. Resolve with F041 in one edit, as the finding proposes. Files changed: none.

### F082 [P3] — CONFIRMED, and the worse half is one the finding does not name

`git grep -n -i "lane\|tier" -- skills/beo`, scripts excluded, → **28 hits**. Most are the unrelated compound "control-plane", which the case-insensitive pattern catches on "lane"; the real vocabulary sites are these.

**"Lane" for the mode axis:** `context-budget.md` uses it throughout — `:6` "per-lane token budgets", `:8` "## Lane budgets", and the column header "Lane" in six tables at `:10`, `:24`, `:32`, `:40`, `:48`, `:56`, plus `:20`, `:72`, `:81`.

**"Tier" for the same axis:** `kernel.md:38`, "BEO safety ceremony scales with the **risk tier**", introducing exactly `quick`/`standard`/`strict`. One axis, two words, and the canonical file uses the one the budget file does not.

**The half the finding misses, and it is the sharper problem:** "tier" is simultaneously the word for a **different** axis with its own enum — `state.schema.json:66` `trace_tier: minimal|standard|detailed` and `runtime-event.schema.json:118` `tier: minimal|standard|detailed` — and for a third thing entirely at `beo-execute/SKILL.md:37`, "subagent **model tier**". So "tier" is overloaded across three unrelated axes while the mode axis has two names. A grep for either term does not just miss half the doctrine; it returns three concepts.

Disposition: **CONFIRMED**, scope widened. Files changed: none.

### F083 [P3] — CONFIRMED; one detail of the finding corrected

`git grep -n "date-time\|_at\":" -- registry` → **13 hits**, and separately `git grep -n "date-time" -- skills/beo` → **exit 1: the JSON Schema `format: date-time` keyword appears nowhere in the bundle.** The finding's phrasing "one schema constrains format" is therefore wrong in the technical sense — no schema uses `format` at all. The three levels are real, but they are pattern / minLength / untyped:

- **Regex pattern** — `reservation-schema.json:43` `created_at` and `:94`, `:140` `released_at`, all `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$`. Strictest, and it forbids fractional seconds and any non-`Z` offset.
- **`minLength: 1` only** — `runtime-event.schema.json:101` `ran_at`, `:117` `evaluated_at`, `:131` `recorded_at`. Any non-empty string.
- **Bare `["string","null"]`** — `state.schema.json:61` `started_at`, `:62` `completed_at`, `:136` `updated_at`. No constraint whatsoever, on the durable artifact.

The ordering is the point: the loosest typing is on `state.json`, the file every other artifact is reconciled against, and the strictest is on the one whose timestamps the doctrine says never expire (Hard Invariant #8).

Disposition: **CONFIRMED**, "format" corrected to "pattern". Files changed: none.

### F084 [P3] — **NOT CONFIRMED**

The finding says "no file says whether emitting the condition implies writing the phase". A file does. `expected_receiver_phase_after_condition['abandoned']` → **`'abandoned'`**, and that mapping's own note at `pipeline.json:95`, read whole at F019, states its meaning explicitly: "This mapping defines the final phase the receiver transitions to after accepting ownership."

So emitting the condition `abandoned` maps to the phase `abandoned`, stated in the registry that wins for machine-checked contracts. The failure mode the finding predicts — "a bead with condition `abandoned` and phase `blocked`, with no rule saying which reading wins" — is excluded by that entry: `blocked` is the mapped phase for eight *other* conditions (derived at F024) and `abandoned` is not among them.

The residual is that `abandoned` is one of only two conditions whose name is identical to its receiver phase (`abandoned` and, by the same map, none other — `planned`/`planned` and `plan_validated`/`planned` are the near cases from F039), which is a naming observation, not a contract gap.

Disposition: **NOT CONFIRMED**. Files changed: none.

### F085 [P3] — CONFIRMED on the duplication; **the mechanism is stated wrongly, and this corrects F015 in this record**

`git grep -n "safe_path" -- skills/beo`, scripts excluded, plus a parse of every registry file's `$defs` keys, gives the exact shape:

- `state.schema.json` — `$defs: ['safe_path']`, `$ref`'d at `:63`, `:65`, `:90`, `:109`, `:125`.
- `ticket.schema.json` — `$defs: ['safe_path']`, `$ref`'d at `:36`, `:37`, `:40`, `:196`.
- `reservation-schema.json` — **`$defs: []`**. The same traversal-guarded regex is written **inline** on `paths.items` at `:37`, with no `$def` and no name.
- `runtime-event.schema.json` and `harness-proposal.schema.json` — `$defs: []`, and no copy of the pattern at all.

So there are three literal copies of the regex, as the finding says, but only **two** are named `safe_path` `$defs`; the third is an anonymous inline pattern, which is strictly worse for the maintenance risk the finding is about — a fix sweeping on the name `safe_path` finds two of the three sites.

**Correction to this record.** The F015 row above states that "`state.schema.json:8-11`, `ticket.schema.json:9-12` **and `reservation-schema.json:37`** each carry a `safe_path` `$def`". The third is not a `$def`. F015's disposition is unaffected — its subject is `harness-proposal.schema.json`'s missing traversal guard, and the contrast it draws holds with three copies however they are declared — but the wording is corrected here rather than edited above, so the record shows what was derived when.

Disposition: **CONFIRMED**, mechanism corrected 3 `$defs` → 2 `$defs` + 1 inline. Files changed: none.

### F086 [P3] — CONFIRMED, narrowed sharply; **half of it is disconfirmed by the finding's own check**

`git grep -n "verify" -- ticket.schema.json` → **4 hits**, and `:52` answers the finding's headline question directly: "Each verify command is exec'd directly via **execve (shell=False, no shell)**. Pipes, redirects, `&&`, `||`, `;`, and env-var expansion are NOT supported. For multi-step commands, list them as separate items."

That is the shell-versus-argv statement the finding says is "never specified". It is specified, in the schema the finding cites, on the line adjacent to the range it points at. Run as written, the scout's own disconfirming check surfaces it — this row was drafted from context, as the report's Coverage section discloses for this band.

**What survives, and it is a real gap:** the contract says commands are exec'd without a shell and never says **how the string becomes argv**. Whitespace split, shlex, or something else are three different behaviours for the same stored string, and the difference is observable — F077 above is the demonstration, using the bundle's own golden trace, whose single-quoted `grep -i 'receive' README.md` only produces the recorded output under one of them.

Disposition: **CONFIRMED, narrowed** — from "tokenization is never specified" to "the shell contract is specified; the argv-splitting rule is not". The severity should fall in Phase B ranking; the surviving half is the one F077 needs. Files changed: none.

### F087 [P3] — **NOT CONFIRMED**

`sed -n '93,96p' pipeline.json` read this turn. The note's second sentence answers the question the finding says is open, explicitly and in capitals: "**Emitting owners are NOT authorized to write this receiver phase directly**; they must write a transition state (like blocked or planning) or keep executing/planning as authorized by `phase-contracts.json`." Read with the first sentence — "the final phase **the receiver** transitions to after accepting ownership" — the writer is named by elimination and by the subject of the transition: the receiver writes it, the emitter is forbidden to.

The finding's predicted failure mode ("both write it, or neither") is the case the note exists to exclude.

Disposition: **NOT CONFIRMED**. The one genuine defect in this sentence is F019's out-of-enum `planning`, which is confirmed above and filed separately. Files changed: none.

### F088 [P3] — **NOT CONFIRMED**

`git grep -n "forbidden_normal" -- skills/beo` → **2 hits**, and the second is an enforcement mechanism: `beo_state.py:446`, `forbidden_kinds = set(pipeline.get("runtime_event_policy", {}).get("forbidden_normal_event_conditions", []))`. The rule is read out of the registry by the state validator and used.

The finding asserts "nothing validates emissions against it". Something does. The claim is disconfirmed by evidence the finding's own check surfaces — this is the third P3 row whose stated check, run as written, returns the material that contradicts it.

Disposition: **NOT CONFIRMED**. Whether `beo_state.py:446` enforces the rule *correctly* is a different question and belongs to **S3b**, which owns that file; nothing here asserts the enforcement is sound, only that it exists. Files changed: none.

### F089 [P3] — CONFIRMED, but **redirected**: the owner exists and a different skill writes there without authority

`git grep -n "checks/" -- skills/beo`, scripts excluded, → **5 hits**, and they split cleanly:

- **An owner does exist for validation-time evidence.** `beo-validate`'s `artifact_write_authorities` is `['strict_reservation','validation_evidence','br.final_route_comments','br.labels.beo_blocked_user']`, and its card at `:38` binds that grant to the directory: "Optional validation evidence under `.beads/artifacts/<issue-id>/checks/`". So the finding's "no skill's `artifact_write_authorities` names them" is true only of the literal directory string; the authority is there under a different name.
- **The real gap is on the execution side.** `quick-mode-golden-trace.md:151` records `evidence_refs: [".beads/artifacts/br-101/checks/verify.log"]` inside the **execution** delta, and `beo-execute`'s authorities are `['approved_product_files','declared_generated_outputs','harness_proposal']` — **no evidence-write authority of any kind**. The bundle's one worked example therefore has beo-execute writing a file into a directory it is not authorized to write.
- `user-handoff.md:43` lists the path as an allowed evidence ref, and `artifact-boundaries.md` enumerates neither `checks/` nor `logs/`.

Disposition: **CONFIRMED**, redirected from "no owner" to "the owner is beo-validate, and beo-execute writes there in the golden trace with no authority". That restatement makes it a closer sibling of F020 (the trace writing `metadata` no owner is granted) than of F069's genuinely ownerless `logs/`. Files changed: none.

### F090 [P3] — **NOT CONFIRMED**

`grep -n -i "vault\|default" memory.md` → **3 hits in a 58-line file**, and they state both the default and its override:
- `:10-12` — "Default Obsidian learning directory:" followed by `<vault>/beo-learnings/`.
- `:28` — "`beo_memory_write.py` writes to the configured Obsidian `<vault>/beo-learnings/` directory when **`BEO_OBSIDIAN_VAULT`** resolves to a writable vault path; otherwise it falls back to `.beads/learnings/`."

That is a stated default, a named environment variable that overrides it, and a stated fallback when it does not resolve. The finding's "the audit path assumes a vault location the file never names" is not supportable at this head.

Disposition: **NOT CONFIRMED**. F032's separate finding that memory has no growth bound, eviction, or precedence rule is confirmed above and unaffected — memory is under-specified in those three respects, not in this one. Files changed: none.

### F091 [P3] — **NOT CONFIRMED**

`git grep -n -i "precheck" -- skills/beo` → **5 hits**. `phase-contracts.json:43` does allow "`scripts/<descriptor>-precheck.*`, `scripts/verify-<descriptor>.*`" at any extension. `beo-validate/SKILL.md:26` reads: "A `scope.files.allow` entry for a pre-check script (**e.g.** `scripts/<descriptor>-precheck.ts`, `scripts/verify-<descriptor>.ts`, or `scripts/verify-<descriptor>.sql`)."

The card's list is introduced by **"e.g."** — explicitly exemplary, not exhaustive — so it does not narrow the registry and does not read as the whole rule. The finding's stated failure mode ("the agent writing a Python precheck has no way to tell which surface governs") is answered by that abbreviation: the examples are marked as examples.

The residual, recorded and not raised to a finding: the two extensions chosen are `.ts` and `.sql`, which may bias an author toward assuming a TypeScript/SQL repository. That is a wording preference, not a contract conflict.

Disposition: **NOT CONFIRMED**. Files changed: none.

### F092 [P3] — CONFIRMED

`grep -n "skills/beo\|references/\|registry/" AGENTS.template.md` → **5 hits in the managed block**, carrying **two conventions**:
- The arrow-glue symbolic form at `:3`, `:5` and `:9` — `beo-reference -> references/kernel.md`, `beo-reference -> references/lifecycle.md`.
- The repo-root literal form at `:6` — "Load via `skills/beo/<name>/SKILL.md`" — and `:12` — "update `skills/beo/` canonical references instead".

Both are individually defensible; the defect as filed is that they sit in one short block that is copied verbatim into every seeded repository, so a reader gets two path grammars in five lines with nothing declaring either. Unlike F033's cases, neither form here is broken — the arrow is symbolic by construction and the `skills/beo/` paths do resolve from a repository root — which is why this is a consistency finding rather than a dead-link one, and correctly P3.

Disposition: **CONFIRMED**. Files changed: none.

### F093 [P3] — CONFIRMED exactly as filed

`grep -n "beo-reference" beo-plan/SKILL.md beo-validate/SKILL.md` → **17 hits**, and both cited pairs verify to the line:
- `beo-plan/SKILL.md:13` — "`beo-reference -> templates/PLAN.template.md` when writing the parent `PLAN.md`" — against `:21` — "using `beo-reference/templates/PLAN.template.md`". Eight lines apart, one target, two spellings.
- `beo-validate/SKILL.md:17` — "`beo-reference -> templates/PLAN.template.md` when validating epic/feature decomposition readiness" — against `:22` — "validate `.beads/artifacts/<issue-id>/PLAN.md` against `beo-reference/templates/PLAN.template.md`". Five lines apart, same pattern.

The finding's own qualification holds and is worth preserving: both spellings resolve from these cards, so this is internal consistency rather than a broken pointer. Every other `beo-reference` reference in both cards — fifteen of the seventeen — uses the arrow form, which makes the two literal-path lines the outliers and the normalization direction obvious.

Disposition: **CONFIRMED**. Files changed: none.

### F094 [P3] — **NOT CONFIRMED**

`grep -n "^## " skills/beo/*/SKILL.md` run across all nine cards this turn. `beo-execute`'s sections are **`Read` (`:7`), `Do` (`:17`), `Write` (`:41`), `Emit` (`:51`), `Never` (`:62`)** — and that is the exact five-section shape of `beo-plan`, `beo-review`, `beo-validate`, `beo-learn` and `beo-reference`. beo-execute is not the exception; it is one of six identical cards.

The three cards that actually deviate are the ones the finding does not name: `beo-debug` inserts `Input` and `Output` between `Read` and `Do`; `beo-author` adds `Rule ownership` before `Read` and a `C9: stale learning evidence_refs` section before `Never`; `beo-setup` adds `Setup modes`. All three are non-delivery skills, and each addition is plausibly warranted by its role.

Disposition: **NOT CONFIRMED**. The premise is inverted — beo-execute conforms, and card-shape variation lives entirely in the support and maintenance cards. Files changed: none.

---

## Tally

Derived this turn, not carried: `grep '^### F' <this file>` matched by `^### (F\d{3}) \[(P[123])\] — \*{0,2}([A-Z][A-Za-z-]*)`, taking the **first** disposition word so a row that confirms one half and blocks the other counts once, under its headline disposition.

| Disposition | Count |
|---|---|
| CONFIRMED | 86 |
| DUPLICATE | 1 |
| NOT CONFIRMED | 7 |
| **Total rows** | **94** |

94 headings, 94 matched, 0 unmatched, 94 distinct ids. Band split of the same 94: **P1 15, P2 45, P3 34** — identical to the report's own banding.

Set equality against the report and the queue, re-derived with `comm` on sorted id lists at the moment this section was written — not carried from an earlier turn, because a carried number is the failure this record spends six table rows documenting. Ids were extracted with `grep -oE '^#+ F[0-9]{3}'` over the report, `grep -oE '^### F[0-9]{3}'` over this file, and `sed -n '1730,1832p' | grep -oE 'F[0-9]{3}'` over the report's `## Verification Queue` block. Result: report ids **94**, receive ids **94**, queue distinct ids **94**; `report minus receive` empty, `receive minus report` empty, `queue minus report` empty, `report minus queue` empty, `queue minus receive` empty. Every filed finding has exactly one disposition and no disposition was invented.

**The 7 NOT CONFIRMED are all P3** — `F070, F084, F087, F088, F090, F091, F094`. Each was disconfirmed by the thing the finding says is absent being present and quoted in its row: a description line that already excludes the three authorities by name (F070); a mapping key that exists (F084); a note that already forbids the write (F087); an enforcement site at `beo_state.py:446` (F088); a documented default and its named override (F090); an "**e.g.**" that stops the list from narrowing anything (F091); and a Read/Do/Write/Emit/Never block identical to five siblings, so beo-execute is not the deviant (F094).

**The 1 DUPLICATE** is `F061`, whose survivor is **`F024`**. Same root cause — `reentry_rules` carries a single key — and F024's row widens the scope to every non-terminal receiver phase, which is what F061 filed against a different phase.

**Confirmed but narrowed or redirected** (the row confirms less, or something else, than the headline claims): `F001, F040, F044, F086, F089`. Also `F030`, whose structural half stands while its execute-side exploit is disconfirmed, and `F077`, whose direction this pass **inverted**.

**Confirmed halves left BLOCKED on S3b**, because the deciding evidence is in the scripts and this slice may not read them as authority: `F002, F009, F043, F045, F049, F050, F051, F077`. Eight rows, each naming S3b as owner in its own text. None of these is a partial confirmation dressed as a full one: the confirmed half is a doctrine-surface fact derived here, and the blocked half is named as blocked.

## Instrument Log

What the instruments did wrong, on both sides. This section exists because a receive pass that only reports on the findings hides its own error rate.

**A defect in the queue itself, and it is the worst instrument fault in this pass.** Queue item **7**, at `26-09-06-s3a-beo-doctrine-round-1.md:1742`, is the check text for **F007**. It reads `s.get('artifact_write_authorities')` and declares the finding "confirmed if `review` appears on both sides." F007's filed claim is about **`state_write_fields`**, and the finding's own Disconfirming check names that key correctly — so the error is the queue's alone, not the finding's.

Derived this turn: `artifact_write_authorities` for beo-execute is `['approved_product_files', 'declared_generated_outputs', 'harness_proposal']`, while `must_not` is `['approve', 'validate', 'review', 'close', 'mutate_outside_approved_scope']`. `review` appears on **one** side, not both. **Run exactly as the queue writes it, the check disconfirms a P1 that the finding's own check confirms.** That makes it the same fail-open class as F065 and F081 below, and the most costly instance of it, because the proposition at stake is whether the executing phase can write its own verdict. The row above ran the check the *claim* requires and confirmed both halves; the queue's sentence is corrected here rather than in the row, so the row shows what was derived and this section shows what the instrument said.

**Two disconfirming checks in the report are malformed, and both fail open.**

- **F065** — the finding's check reads `a.get('invalidators')` at the top level of the document. That key does not exist there; the real path is `validity_model.invalidators`. Run as written it returns `None`, which reads as "no invalidators", which reads as disconfirmation.
- **F081** — the check reads `d.get('forbidden_normal')`. The real key is `runtime_event_policy.forbidden_normal_event_conditions`. Same failure mode: `None`, read as absence.

Both are the dangerous direction. A malformed *confirming* check produces a claim nobody can reproduce and dies on contact. A malformed *disconfirming* check produces a clean-looking null and retires a live finding. Both findings are CONFIRMED here on re-derived paths, and F065 far more strongly than filed.

**Six count-and-pointer defects in the report, the C16 class.** Every one was found by re-deriving the number rather than by reading the sentence:

| Finding | The report says | Derived this turn |
|---|---|---|
| F019 | "finds it only in that prose note" | A second hit exists, `pipeline.json:68` — a `route_classes` **key**, not an enum member. The structural claim survives; the evidence sentence does not. |
| F023 | "nine incoming edges" | **6** in `transitions`, **7** file-wide. Worse: the six cited line numbers (8, 9, 13, 23, 24, 27) are each exactly **+1** off the real ones (7, 8, 12, 22, 23, 26) — an off-by-one applied uniformly, which is the signature of a count read off a shifted view rather than off the file. |
| F040 | cites `skills/beo/templates/PLAN.template.md:99` | **That path does not exist.** `find skills/beo -name '*.template.md'` returns only `beo-reference/templates/{AGENTS,PLAN}.template.md`. Run as written, the check silently drops a third of its own evidence and still appears to pass. |
| F057 | "five prose sites" | **8.** The finding's own source-pointer line already lists seven, so the headline disagrees with the finding's own body. |
| F063 | headline four skills, evidence five, contract line 12 edges | **2 skills, 5 edges** — beo-debug 2, beo-author 3. beo-learn, beo-setup and beo-reference carry `outcomes` only and no transitions block at all. Three numbers, three different values, none of them derived. |
| F066 | "six skills", and names the token `close_beads` | **7** skills; and `close_beads` **does not exist anywhere in the bundle** — `git grep` exits 1. Two of the finding's three specifics are wrong while its structural claim holds. |

One further evidence defect that is not a count: **F072** cites no pointer at all and names neither member of either collision pair. It is confirmed here as a class, on pairs this pass derived, not on pairs the finding supplied.

**This seat's own errors this pass**, recorded at the same weight:

- I piped `grep -rni climate skills/beo/ | head` and read the pipeline's exit status as grep's. Re-derived without the pipe: exit **1**, zero hits. The conclusion was unchanged; the instrument was not sound.
- My **F015** row asserted that `reservation-schema.json:37` carries a `safe_path` `$def`. It does not — that file's `$defs` is `[]` and the regex is anonymous and inline. Corrected inside the **F085** row rather than by rewriting F015, so the record still shows what was derived when.
- The pointer self-check below caught two bare `README.md:69` citations that resolve against the 61-line **root** `README.md`. The content is at `skills/beo/README.md:69`. Both were corrected to the path `git grep` actually prints, before this section was written.

## Ranked Confirmed Findings

The report's Next Receive Prompt asks the receive pass to rank what it confirmed. Ranking basis, stated so it can be argued with: **Tier 1** is a contradiction that either forbids a correct action outright or permits an incorrect one, where no reading of the doctrine escapes it. **Tier 2** is a contradiction between two authorities that a reader must resolve by guessing, plus every remaining P1. **Tier 3** is everything else confirmed — real, derived, and lower cost to leave standing. Band is an input to the ranking, not the ranking.

**Tier 1 — 8 findings: `F007, F010, F024, F027, F030, F065, F077, F089`**

- **F027** — `phase-contracts.json:90` puts `close_non_accepted_work` in beo-review's `must_not`, and beo-review is the only closure-holder. The single seat authorized to close an epic is affirmatively forbidden from doing so. This is stronger than filed and is the top of the list because no skill can execute the terminal step.
- **F024** — `reentry_rules` carries one key. Every other non-terminal receiver phase has no re-entry rule at all, so a run that leaves one has no documented way back. F061 folds in here.
- **F065** — 11 invalidators against 15 `failure_category` values, and the **set intersection is empty**. Not "overlapping but non-identical" as filed — disjoint. No failure category invalidates anything.
- **F077** — `ticket.schema.json:52` states execve with shell=False, yet the golden trace's single-quoted `grep -i 'receive' README.md` with its recorded `exit_code: 0` and `stdout: "Please receive updates."` is reproducible **only** under a quote-stripping splitter. The trace and the schema describe different executors. Filed as near-disconfirmed; inverted here.
- **F089** — redirected. beo-validate does hold `validation_evidence` and its card binds it to `checks/`. The live defect is `quick-mode-golden-trace.md:151` having **beo-execute** write `checks/verify.log` while beo-execute's authorities are `['approved_product_files','declared_generated_outputs','harness_proposal']`. The canonical trace demonstrates an unauthorized write.
- **F007** — both halves confirmed on `state_write_fields`, despite the queue's own check text pointing at the wrong key.
- **F010** — the README names an output directory that does not exist at the reviewed base, tracked or on disk, and the README and the command manifest disagree on whether the artifact is markdown or json.
- **F030** — the missing else-branch stands on `safety.md:39`; the execute-side exploit the finding attaches to it does not.

**Tier 2 — 31 findings:** `F001, F002, F003, F004, F005, F006, F008, F009, F011, F012, F013, F014, F015, F017, F019, F023, F026, F028, F032, F034, F036, F038, F040, F044, F047, F052, F054, F057, F059, F060, F078`

Two of these carry weight beyond their own row. **F059** earns its P2 from this pass's own results rather than from its filed argument: 23 of the findings confirmed here sit inside the four registry files that have no `$schema`, so the absent schema is the reason a whole class of these defects was never caught mechanically. **F078** explains why the registry conflicts persist at all — doctrine-map's subordination clause covers **markdown references only** and is silent on the registries, which is precisely where F028, F019 and F048 live.

**Tier 3 — 47 findings:** `F016, F018, F020, F021, F022, F025, F029, F031, F033, F035, F037, F039, F041, F042, F043, F045, F046, F048, F049, F050, F051, F053, F055, F056, F058, F062, F063, F064, F066, F067, F068, F069, F071, F072, F073, F074, F075, F076, F079, F080, F081, F082, F083, F085, F086, F092, F093`

8 + 31 + 47 = **86**, which is the confirmed count in the Tally, derived by the same script rather than added by hand.

This ranking is Phase A output. It is not a work order: no fix lands from this pass, and **opening Phase B is the Human's decision**.

## Pointer And Quotation Self-Check

Run against this file at the moment of writing, in the shape S2 used. A regex over backticked `path:line` citations resolved each against the working tree at the reviewed base and required the cited line to exist and be non-blank.

The check covers the **digested prefix** — everything above the final `---` separator, which is the exact range the Record digest at the end of this file is scoped to, so the self-check and the digest describe the same bytes. The range is named by its anchor rather than by a line number, because a line number written inside the range it describes is invalidated by the next edit to that range. It was run twice: once over the 94 rows alone, and again over that whole prefix including these closing sections, because the closing sections add citations of their own and a self-check that does not cover its own text is not a self-check. **The figures below are the second run**, derived after the last correction inside the prefix was written.

- **154** citation instances, **123** distinct.
- **149** resolve to a real, non-blank line at the reviewed base.
- **5** failures, and every one is a **deliberate quotation of a defect this pass reported**, not a defect in this record:
  - **3 ×** `skills/beo/templates/PLAN.template.md:99` — the path the report cites at F040, which does not exist. Cited in the F040 row, in the Instrument Log table, and once more here. The self-check failing on it is the intended result.
  - **2 ×** the bare form `README.md:69` — which resolves against the 61-line **root** `README.md` and so fails. Both occurrences are in the Instrument Log and in this bullet, where the bare form is named *as the error*; the two live citations in the F010 row were corrected to `skills/beo/README.md:69`, the path `git grep` actually prints, before this section was written.

So: **0 unintended pointer failures**, against 5 the record is deliberately quoting. The first run, over the rows alone, was 140 instances / 119 distinct / 139 resolved / 1 failure — the F040 path — and it is what caught the two bare `README.md` citations before they became findings of their own.

The resolver itself was corrected mid-check: an early root list omitted the bare `skills/` prefix and reported `ultra-review/SKILL.md:117` and `ultra-review-receive/SKILL.md:12` as unresolvable. Both exist and both lines were read directly before the failure was dismissed. That is recorded because dismissing a self-check failure without reading the line is how a pointer defect survives a pointer check.

Quotation check: every quoted string in the rows above was pasted from a `sed -n`, `cat`, `git grep` or `git show` result in the same turn as the row was written, never retyped from memory. Where a citation reaches into `AGENTS.md` — out of scope for S3a by the report's own restriction — it was read with `git show 038dc27b:AGENTS.md`, never from the working tree, because the working tree copy is modified and unattributed under G57.

## Custody

Every figure derived this turn, with the command named.

| Fact | Command | Value |
|---|---|---|
| Head under review | `git rev-parse HEAD` | `33eafc5431a265d523241db25b0e455a974f09e3` |
| Stash entries | `git stash list \| wc -l` | `0` |
| Diff inside the reviewed bundle | `git diff -- skills/` | **0 lines** |
| Working tree | `git --no-optional-locks status --porcelain --untracked-files=all` | **12 lines**: ` M AGENTS.md`, ten untracked under `docs/ultrareview/`, `scratchpad/c8-intake.md` |
| Review documents | `ls docs/ultrareview/ \| wc -l` | `10` |
| Branches | `git branch -a` | `main`, `remotes/origin/HEAD`, `remotes/origin/main` — no delivery branch survives |
| Gate ledger | `wc -l` + `shasum -a 256` on `~/.herdr/projects/beo-skills/gates.md` | **150 lines**, `b1845e61df34ed3dad297d50611281f66a1b0fadaf8551c43075986bf647e6e7` |
| Rows claiming no edit | per-row section split on `^### F\d{3} `, checking each row's body | **94 of 94** rows carry `Files changed: none`; **0 missing**. A raw `grep -c` is not used as the measure: it counts the phrase wherever it appears, including the preamble at `:8` and these closing sections, so it drifts upward every time the record discusses the convention. |
| Review base | `git rev-parse --verify 038dc27b^{commit}` | `038dc27b50859cb30542b91683688a1f52ce5d66` — matches INTAKE `## Frozen head` |
| Workspace files edited this pass | `git check-ignore -v` on each | `skills/ultra-review-workspace/campaign-01/INTAKE.md` and the two workspace `HANDOFF.md` files are ignored by `.gitignore:16` (`skills/*-workspace/`). They are edited by this seat and are correctly absent from porcelain, so `git diff -- skills/` at 0 lines is a claim about the **reviewed bundle**, not an accident of what git happens to track. |

The gate digest is **byte-identical** to the digest recorded before this pass began. No ledger row was written and no gate was opened, which is the correct outcome: this pass is verification only, it applies no fix, and **no delivery, merge, push or deploy is authorized by it**.

`git diff -- skills/` at **0 lines** is the mechanical check on the `Files changed: none` claim carried by all 94 rows. Nothing under review was edited. The only files this pass wrote are this record and, earlier in the campaign, the other documents under `docs/ultrareview/`, all of them untracked.

`AGENTS.md` remains ` M` and untouched — not staged, not reverted — pending the Human's attribution of that edit, per G57.

**Open and unchanged: the push is blocked (G97).** `origin/main` is at `038dc27b`; local `main` carries `dcf9f2f5` and `33eafc54`, both independently reviewed and both deployed. Two attempts were refused by this seat's runtime classifier, compound and bare, so the refusal is shape-independent. It is recorded as a **runtime denial, not a Human ruling**, and no further workaround will be attempted; resolution is the Human's.

Next slice: **S3b**, the beo scripts — 26 files, 10062 lines (17 scripts at 5968, 9 test modules at 4094) — against the same review base `038dc27b`, and it inherits the eight BLOCKED halves listed in the Tally.

---

**Record digest.** A whole-file digest cannot be embedded in the file that carries it, so this one is **scoped to the prefix that ends at the `---` above this paragraph**: `head -n 1029 <this file> | shasum -a 256` → `81c05252d30203177e60619ffc4b2b0d3e501f6291c8316125d6a890faa20665`. Lines 1 through 1029 are the 94 dispositioned rows and every closing section through the Custody table, ending at the "Next slice" line. Nothing at or below the separator is inside the digest, so this paragraph can exist without invalidating it. Any later byte change inside the prefix is an edit made after S3a closed, and this is the digest it must be compared against.

Two earlier drafts of this line were wrong and are corrected rather than silently overwritten, because they are the exact fault this record charges the report with at F023 — a number read off a state that no longer exists. The first stated a whole-file digest computed at 1023 lines and then invalidated by the six lines appended after it. The second scoped the digest to 1023 lines but was written after five corrections had already changed bytes inside that prefix, so the stated value no longer reproduced. The prefix now ends above the paragraph that reports it, which is the only arrangement that is stable.

**S3a receive pass closed.** 94 findings dispositioned, 0 fixes applied, 0 gates opened, 0 ledger rows written.
