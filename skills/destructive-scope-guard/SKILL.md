---
name: destructive-scope-guard
description: Resources held by a provider (in a cloud account or project, a subscription, a tenant of a hosted service) are removed only inside a proven scope and a named consent. Use when the agent itself is about to delete, empty, tear down, reset or clean up such resources. Do not use for a local path (destructive-path-guard), for reading or investigating with nothing removed, for creating or changing resources that stay, for removing selected data inside a resource that stays (some rows, some objects), or for writing or reviewing code that will remove resources when it runs later.
---

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

A removal in a tenancy rests on four facts, each on record with its evidence
before the first removal. A removal is made only inside what the fourth covers.

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
4. **The consent.** An answer, given with the inventory in hand, that names the
   tenancy's identifier and the set to remove, as items or as a class the
   inventory can be checked against; with several tenancies, each has its
   identifier and its set. An earlier instruction counts for what the inventory,
   taken afterwards, shows it to name, and the identifier is in it or it is not
   this fact. The whole of a tenancy is one such class, checked the same way.
   Whatever the class, a listed thing with one of the three marks is covered
   only when the consent names it; no consent covers what is unread. An act on
   the tenancy itself (removing it, closing what bills for it, turning off a
   whole service in it) is covered only when the consent names the act and the
   identifier; consent to the contents does not imply it, and one instruction
   naming both needs no second message. Held when the consent's words are on
   record beside its inventory.

## Who decides

Judge a consent by what it names, never by its form of words. When the user
tells you to go on without one of the facts, say which fact is missing and what
you then cannot vouch for; the user's instruction decides, and the fact goes on
record as waived, with the user's words.

Whoever gives the consent (the user, or under a workflow its approver) gives a
waiver, and that person's words take the waived fact's place wherever this
skill refers to the fact or to what it holds. With the consent or the inventory
waived, the consent is what those words name, as targets or as a class, in the
tenancy of fact 1; the reads the removal needs find a class's members. With
that tenancy waived, it is the one those words name. With no inventory there is
nothing earlier to compare a target with, so you act on the read just before the
removal; the closing inventory is still taken, over what the words reach. A
waiver does not lift acting on what you see: when that read shows the target
owned by a deployment tool or another party, protected, or used from another
tenancy, tell that person before removing it; the answer is the consent for it.
That read is a read of the target, not an inventory.

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
- A resource the inventory did not hold is not in the consent: report it and
  leave it.

## End

Take the inventory again over the same reach and build the report from it:

- what is gone;
- what is still there, each with why: not consented, failed its check, refused,
  failed, or still in progress;
- what is unread or unverified;
- what only a person can do, handed over as steps (human-step-wizard).

Done when the four facts are on record, each with its evidence or as waived in
the user's words with what you could not vouch for; every removal was inside the
consent and passed its check; the closing inventory is in the report with the
unread parts named.

## Borders

- A path on the local filesystem that a delete, move or overwrite would hit:
  destructive-path-guard.
- A remainder only a person can remove: human-step-wizard.
