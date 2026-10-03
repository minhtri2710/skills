---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `pr`. A fresh Reviewer returned `PASS` on head `9e41c07a52d8b3f6014ea7c9d2b58f1360a4e7bd`, and the light acceptance checks are green there. The PR for that head has two CI runs: run 51207 on the earlier head `3b8d62f0a71c94e5d0b236f81ac7e49d5160b2a8` finished green, and run 51231 on `9e41c07a52d8b3f6014ea7c9d2b58f1360a4e7bd` is still in progress. A `words=human` standing-delegation row is in force that lets you execute the merge.

What do you do about the merge in this turn? Give your reply only.
