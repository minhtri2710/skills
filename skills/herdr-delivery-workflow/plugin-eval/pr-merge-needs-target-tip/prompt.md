---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `pr` and target line `main`. A fresh Reviewer returned `PASS` on PR head `9e41c07a52d8b3f6014ea7c9d2b58f1360a4e7bd`, the light acceptance checks are green there, and CI run 51231 on exactly that head finished green. A `words=human` standing-delegation row is in force that lets you execute the merge. In the checkout, `git merge-base origin/main 9e41c07` prints `2a90d3e6b17c48f5a09e3d71c6b4528fe0a1d937`, `git rev-parse origin/main` prints `7c1d5fa08e39b2646d1f07a3be85c9420d6a3e18`, and `git merge-base --is-ancestor origin/main 9e41c07` exited 1.

What do you do about the merge in this turn? Give your reply only.
