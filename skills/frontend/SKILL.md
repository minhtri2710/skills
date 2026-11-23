---
name: frontend
description: "Build, change, or polish a user interface, or stress an existing one. Use when a UI change's rendered hierarchy, layout, interaction flow, responsive behavior, or visual design is part of acceptance; or when the user asks to stress or break an existing screen with data, or how it copes with messy, extreme, empty, or missing real-world data. Do not use for copy-only edits, design tokens, headless UI logic, comparing design variants, or load and latency."
---

# Frontend

Two branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `frontend-design` | Implement a UI change whose rendered hierarchy, interaction flow, responsive behavior, or domain-fit visual design is a material part of acceptance. Do not use for copy-only edits, isolated design-token changes, headless UI logic, or minor component maintenance. | `references/frontend-design.md` |
| `worst-case-data-review` | Review an existing screen or component against the data it can actually receive, and report where it fails. Use when the user asks to stress or break a UI with data, or asks how it copes with messy, extreme, empty or missing real-world data, and the review itself is the request. Do not use while building or changing a UI (the data check of a change being built is frontend-design's own), to fix or restyle what the review finds, to explore design variants (throwaway-prototype in the `design` skill), or for load and latency (performance-verification in the `diagnosis` skill). | `references/worst-case-data-review.md` |
