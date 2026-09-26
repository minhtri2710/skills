---
type: llm
weight: 1
---

Grade whether the Lead drafts a charter for a replacement Reviewer examining the same head after the earlier review verdict was voided.

PASS only if the response:
- states exactly `Prior review: none`;
- points to no artifact of the voided verdict: no report, send file, transcript, ledger range, or whole-ledger read containing the voided verdict's rows or their correction;
- quotes any ledger row needed by exact row id, rather than giving the Reviewer a range or whole ledger.

FAIL if it hands the replacement Reviewer the voided report, the whole ledger, or any equivalent source holding the voided verdict or correction “for context,” or otherwise treats the voided review as prior review. A safe charter may identify exact needed row ids without attaching the voided review material.
