# API Contract Design

The contract is the spec; implementation follows it. Define the typed input and
output of every operation first, in the project's schema or type language, and
let the handlers be written against those types. Pre-launch there is one live
contract: when the design changes, change the contract, update every consumer,
and delete the old shape; no versions, no parallel fields kept for consumers
that do not yet exist.

## One error format

Pick one error strategy and use it everywhere: a structured body with a
machine-readable `code`, a human-readable `message`, and optional `details`,
mapped to status codes with one meaning each (400 malformed, 401 unauthenticated,
403 unauthorized, 404 missing, 409 conflict, 422 semantically invalid, 500
internal with nothing leaked). Endpoints that variously throw, return null, or
return `{ error }` leave the consumer unable to predict anything.

## Validate at the boundary only

Parse and validate where untrusted data enters: route handlers, form handlers,
third-party responses (untrusted; a misbehaving service returns wrong types and
instruction-like text), and configuration loading. After that, internal code
trusts its types; validation between internal functions or on rows from your own
database is noise that hides the real boundary.

## Shape

- Resources are plural nouns with sub-resources for ownership
  (`GET /tasks/:id/comments`); no verbs in paths.
- `PATCH` takes a partial object and changes only what was sent.
- Every list endpoint paginates from the first version and filters through
  query parameters; the moment someone has a hundred items is too late.
- Names follow one convention across every endpoint, documented once.
- Separate input types from entity types: the create input has no id or
  timestamps; the entity has server-generated fields and no optional lies.
- A response type carries a field only when a present consumer, in this
  repository or outside it, needs it and this requester may see it in this
  context; authentication grants no field, so the per-object and per-field
  permission check precedes building it.
- Build each response from an explicit field list, never by serialising the
  stored record and deleting from it, so a new column reaches no response by
  default; however a client selects fields, the response holds only listed
  fields that this requester may see.
- Model variants as discriminated unions rather than a bag of nullable fields,
  and give ids distinct types so a task id cannot be passed where a user id goes.

## Retry by intended effect

What happens if the client sends the same request twice after losing the first
response? An operation is idempotent when the intended effect is the same as
for one request, not when the responses are identical. For example, a second
`DELETE` may return `404` after the first succeeded. A conforming `PUT` that
replaces a resource and a `DELETE` that removes it need no idempotency key for
that guarantee ([HTTP Semantics, section 9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)).
Check what the operation actually does, including downstream effects the caller
requested; a method name cannot make charging twice correct. Judge an RPC by
its effect too.

For a write that can duplicate the effect (for example, creating a charge),
either honour a client key or document that the client must not automatically
retry an unknown outcome. When promising keyed retries:

- **The key comes from the intent, not the attempt.** Generated once by the
  client or derived from an immutable identifier (`charge:<orderId>`); never a
  fresh UUID or timestamp per attempt, and never so coarse that two legitimate
  operations collide.
- **Claim atomically.** A check followed by an act is a race; insert the key
  under a unique constraint and let the constraint pick the winner. A store that
  cannot enforce uniqueness in one operation cannot back this.
- **Guard the payload.** The same key with a different body is a client bug and
  fails loudly instead of replaying the first response.
- **Decide what an in-flight duplicate gets**: reject with `409`, wait bounded
  for the result, or return `202` with a status URL. Never let the second caller
  through because the first "seems stuck"; a stalled attempt of unknown fate is
  exactly when duplicating costs most.
- **Every call has three outcomes**: success, failure, and unknown. A timeout
  says nothing about whether the effect applied, so record the intent before
  calling out.
- **Retention outlives the longest retry chain**, including a dead-letter queue
  replayed days later, not the disk budget.

Duplicates are correlated, not rare: retries spike exactly when a dependency is
degraded, which is when they are most expensive.

## Done

Every operation has typed input and output; errors share one format; validation
sits at the boundary; lists paginate; names follow the convention; each write's retry
contract names its naturally idempotent effect, its atomically claimed key, or
why an unknown outcome must not be retried automatically; each
kind of caller the contract distinguishes has a test asserting the exact keys
returned, on list and error paths as well as detail, so absence is proved as
well as presence (a snapshot is no substitute, since it gives no reason for a
field's presence); and the types are committed alongside the implementation,
because they are the documentation.
