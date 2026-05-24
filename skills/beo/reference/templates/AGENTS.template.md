<!-- BEO:MANAGED START -->
BEO always-on rules (kernel is canonical):
1. Work on exactly one verified Beads issue at a time.
2. Load `beo-reference` -> `references/doctrine-map.md` for navigation and `beo-reference` -> `references/kernel.md` when safety invariants matter.
3. Load the active `skills/beo/*/SKILL.md` owner contract before any mutation owned by that skill.
4. Use `br` as transactional lifecycle truth for issue identity, claims, comments, dependencies, sync, and closure.
5. Use `bv` only for read-only graph orientation; it never owns lifecycle state or authorization.
6. Use `beo-reference` -> `references/...`, `registry/...`, `templates/...`, and `scripts/...` for shared doctrine, contracts, templates, and helper entry points.
7. Follow the normal delivery path: `beo-plan` -> `beo-validate` -> `beo-execute` -> `beo-review`.
8. Mutate product files only for a claimed atomic bead with a current `PASS_EXECUTE`, and only inside approved scope or declared generated outputs.
9. Use strict mode for external, stateful, destructive, security-sensitive, or otherwise high-risk work.
10. Treat Human Gates as user-owned; never infer missing authorization.
11. Treat `qmd` recall and Obsidian learning as advisory memory only; they never grant approval, execution permission, verdicts, closure, or Human Gate resolution.
12. Never use broad globs such as `**` or `src/**` without explicit Human Gate authorization.
13. Never close delivery directly or bypass beo-review; only beo-review can route to Beads closure (verdict_accept for normal delivery, or registered abandon/cannot_deliver with user visibility).
<!-- BEO:MANAGED END -->
