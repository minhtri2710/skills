# Destructive Scope Guard

A credential that opens a tenancy does not say the tenancy is the one meant, and
a removal at a provider cannot be taken back.

- The **tenancy** is the smallest scope whose identifier the removal commands
  take and the provider's identity answer returns. That property decides,
  whatever the provider or the user calls the scope; a scope that holds several
  such units is not one.
- A **resource** is a thing the provider lists with an identifier and
  permissions of its own. Emptying a resource of all it holds is an act on that
  resource and is in scope; removing a selection of what it holds is not.
- The **inventory** is the read-only record, taken in this session, of what the
  request reaches.

## Four facts before the first removal

Record the intended tenancy, the identity established by the provider, the
inventory, and the consent. Only the advance inventory has an exception (Who
decides). A removal is made only inside what the consent covers.

1. **The tenancy.** Record the identifier the provider itself uses for it, given
   or confirmed by the user. When the user names it another way (an alias, a
   display name), find the identifier, have the user confirm the name means it,
   and record both. Several tenancies give several identifiers; a scope above
   tenancies is resolved with the user into tenancy identifiers. When the user
   gave no name, ask; showing what the credential opens is a means to ask.
   Held when the identifier and the user's words are written down.
2. **The identity.** Evidence from the provider that the credential the removals
   will use acts in that tenancy: a read through that same credential path whose
   answer contains the tenancy's identifier. Record the answer, the principal it
   names, and the credential's source. An answer without the identifier is not
   this fact. A different credential coming into force voids it until it is
   established again. From fact 1 on, every command takes the tenancy (and the
   location, where the provider has locations) from fact 1's record, as an
   argument.
3. **The inventory.** Its reach follows the request: for named targets, those
   targets with what they own and what uses them; for a whole tenancy or a class
   of resources, the tenancy. It leaves the tenancy's state and permissions as
   they were and reads no secret value; a secret appears by name. Coverage is
   part of the record: every location and every kind of resource the reach
   includes is marked read or unread, and one never tried is unread exactly as
   one that was refused. Mark three things on what it lists: what resources in
   other tenancies use; what a deployment tool or another party owns, with the
   owner named; what would make a removal fail or keep a copy after it. What is
   unread is no listed thing: it stays coverage, goes to the report, and nothing
   in it is removed. Held when whoever gives the consent has the inventory.
4. **The consent.** Present the proposed action, verified tenancy identifier and
   targets (items or a bounded class), with the inventory or the limits of the
   explicit inventory exception below. Proceed only when the approver explicitly
   confirms that proposal. A request to investigate or clean up is not that
   confirmation. With several tenancies, each has its identifier and approved
   set. A whole tenancy's contents can be a class. A resource with any of the
   three marks above needs consent naming it; an unread target is not covered.
   Removing the tenancy itself, closing its billing, or turning off a whole
   service needs consent naming that act and identifier. One confirmation may
   cover both the contents and such an act if it names both. Record its words.

## Who decides

Consent answers *may we remove these targets?* The provider's identity response
answers *where will this credential act?* Require both for the same tenancy.
If either is missing, stale or mismatched, stop before removal and name the
missing proof. An instruction to proceed cannot establish identity; access to
a resource cannot establish consent.

Only the approver can explicitly waive the advance inventory. Record their
words, the verified tenancy and approved set, and what was not inspected. Read
each candidate in that tenancy immediately before removal to establish that it
matches the consent; do not remove an unread or uncertain target. If the read
reveals outside ownership or use, deployment-tool ownership, or protection,
tell the approver and obtain consent naming that resource before removing it.
The closing inventory still covers the full approved scope.

Under a workflow that gates any act this skill covers (a removal, an act under
an outside account, the reads of facts 2 and 3 where it gates those), that gate
stands and its approver is the one who consents. This skill adds no gate to a
read and lifts none. There the inventory goes to the approver through the
workflow's channel, and the consent is the request together with its answer.

## Removal

- Read the target just beforehand: it must be what the consent was given on, the
  same resource, owner and protection, and still matching the attribute the
  consent chose it by. A target that fails is left and reported. Other change
  (size, activity) does not count.
- What would bring removed resources back goes first; what you need in order to
  finish goes last. Take the closing inventory before your own access is
  removed, and report what that last removal leaves as unverified.
- Act only in the tenancies the consent names. A link that leads out of them, in
  either direction, is reported and not acted on.
- Remove a resource a deployment tool owns through that tool; what the tool
  would remove with it belongs in the inventory and the consent. Where you
  cannot drive the owner, say so and say what direct removal risks (the owner
  may bring the resources back, or lose track of them); direct removal then
  needs a consent that names it.
- With an advance inventory, leave and report any target it did not list. Without
  one, the immediate read must establish that the target belongs to the approved set.

## End

Take the inventory again over the same reach and build the report from it:

- what is gone;
- what is still there, each with why: not consented, failed its check, refused,
  failed, or still in progress;
- what is unread or unverified;
- what only a person can do, handed over as steps (human-step-wizard).

Done when the record contains the tenancy, matching provider identity, named
consent, and the inventory or its explicit exception; every removal passed its
check within that consent; and the closing inventory names what remains unread.

## Borders

- A path on the local filesystem that a delete, move or overwrite would hit:
  destructive-path-guard.
- A remainder only a person can remove: human-step-wizard.
