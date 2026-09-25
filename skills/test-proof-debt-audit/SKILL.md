---
name: test-proof-debt-audit
description: Audit one named behavioral claim and the test, validator, benchmark, or gate cited as proof, or audit a named set of existing tests for redundant or low-value tests. Do not use for ordinary implementation, writing new tests, failing tests, weak coverage, or the presence of mocks.
---

# Test Proof Debt Audit

Audit only the claim and proof route, or the test set, named by the user. Do not
turn ordinary implementation, a failing test, weak coverage, or the presence of
mocks into a repository-wide proof audit.

1. Name the claim and production behavior that makes it true.
2. Identify the cited proof.
3. State what the proof actually observes: behavior, machine-readable contract, performance, or proxy text/metadata.
4. Apply deletion sensitivity: would it still pass if the claimed behavior disappeared?
5. Check whether expected values come from independent truth.
6. Choose `keep`, `replace`, `demote`, `closeout-only`, `delete`, or `escalate`.

Treat history-only expected values as proof debt. A current test must not name
or pin a retired width, tag, field, version, byte sequence, or identifier merely
to prove its rejection. Ask whether the test could be derived from the current
contract without repository history. Replace it with current-boundary cases,
demote it to closeout-only evidence, or delete it unless the historical value
is itself a current public machine/security contract.

For a redundancy audit of a named test set, give each contract one primary owner
test at the strongest boundary. Another test of the same contract earns its place
only with a distinct risk the owner cannot reach, such as a transport or lifecycle
failure. Otherwise it is a duplicate: fold it into the owner's table case or shared
fixture, or delete it.

Before choosing `delete`, apply the retention bar. Keep a test that independently
enforces a public API, protocol, config, storage, security, or architecture
contract, observable call ordering, or a regression with a credible failure mode,
even when it resembles the implementation. Static or slow is not a reason to
delete. A retained test that fails on the baseline may be a product bug: reproduce
it and route the owner fix instead of deleting the test.

Record these fields for a delete candidate; if any is missing, choose `keep` or
`escalate`, never `delete`:

- exact test name and location;
- the failure it can actually detect;
- non-test callers of the production or support seam it covers;
- the stronger owner-boundary proof that remains, or why none is needed;
- why the test or seam exists, from history;
- the production or test-support code the deletion unlocks;
- risk and the focused validation command.

Proxy evidence can support lint or closeout but cannot prove runtime behavior. Mocks and replicas prove only their own boundary unless the claim is explicitly about that boundary.

Report location, claimed behavior, actual observation, disconfirming scenario, and
smallest replacement. Weak proof does not authorize an architecture redesign. If
the user requested assessment only, report and stop; modify proof or production code
only when requested.

Read [references/catalog.md](references/catalog.md) only for a broad user-requested audit, a redundancy audit, or when concrete replacement examples are needed.
