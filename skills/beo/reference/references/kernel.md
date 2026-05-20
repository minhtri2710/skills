# BEO in one page

Use one Beads issue at a time.

## Normal path

Plan → Validate → Execute → Review

## Quick path

Use for tiny repo-only low-risk work.

1. Show and claim the issue.
2. Write minimal ticket.
3. Validate grants PASS_EXECUTE.
4. Execute edits only approved files.
5. Review verdict.
6. Close only after accept.

## Standard path

Same as quick, but declare generated outputs, risk, and rollback.

## Strict path

Same path, but requires human authorization, strict artifacts, and side-effect contract.

## Never

- execute without PASS_EXECUTE
- mutate outside scope.files.allow or generated outputs
- let debug/recall/memory approve or route delivery
- close outside beo-review
- use broad globs without authorization
- treat advisory drift as approval invalidation
