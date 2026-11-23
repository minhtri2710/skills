# Spec Conformance Review

Code review answers "is this good code?". This review answers "is this what was
asked for?". The two are separate axes: a diff can be clean and miss half its
requirements, or deliver everything through a tangle. Findings from the two axes
are never merged or reranked against each other, because a single ranked list
hides whichever axis lost.

## 1. Pin the range and the spec

Use the spec, issue, or plan the user names. If none is named, follow references
in the branch or commit messages, then look in the project's planning directory.
Ask if the spec is missing or ambiguous; if there is none, report "no spec
available" rather than inferring requirements from the code.

Pin the comparison the user asked for; a commit range does not include local edits:

- Branch or PR: verify the base and head refs. `git diff <base>...<head>` compares
  the head with the merge base; `git log --oneline <base>..<head>` lists the commits.
- Working tree: `git diff HEAD --` shows net tracked changes, staged and unstaged.
  If the review also includes branch commits against a named base, use
  `git diff --merge-base <base> --` instead. `git ls-files --others --exclude-standard`
  lists untracked files; inspect those in scope as additions without staging them.

If the selected scope contains no changes, say so and stop.

## 2. Read the spec first, then the diff

List every requirement the spec states, including the explicit exclusions and
the acceptance criteria. Only then read the diff, requirement by requirement.

## 3. Report in three sections, quoting the spec

- **Missing or partial**: a requirement with no implementation, or one that
  covers part of the stated behavior. Quote the spec line; name where the diff
  stops short.
- **Not asked for**: quote the exclusion or scope limit that the change crosses
  and name the extra behavior. If the spec is silent, ask rather than calling it
  a violation.
- **Implemented but looks wrong**: a requirement that has code against it where
  the code's behavior differs from the spec's words (an off-by-one boundary,
  a different default, a case the spec names that the branch never takes).

Each finding carries the quoted spec text and the file and hunk it concerns.

## 4. Close

End with one line: findings per section and the worst single gap. When a
code-quality review ran alongside, present its report under its own heading, and
give no combined verdict; the user weighs the axes.
