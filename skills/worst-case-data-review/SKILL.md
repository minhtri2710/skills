---
name: worst-case-data-review
description: Review an existing screen or component against the data it can actually receive, and report where it fails. Use when the user asks to stress or break a UI with data, or asks how it copes with messy, extreme, empty or missing real-world data, and the review itself is the request. Do not use while building or changing a UI (the data check of a change being built is frontend-design's own), to fix or restyle what the review finds, to explore design variants (throwaway-prototype), or for load and latency (performance-verification).
---

# Worst-Case Data Review

This review's unit is the assumption. Every value a UI renders comes with
assumptions its layout and code make without saying so: how much room the value
takes, that it is there, what it is made of, what band it lies in, how many
there are, which kinds occur together, what shape a picture has. The review
finds the assumptions, builds admissible data that breaks each, looks at the
result, and reports.

Product code is what ships to users. The review changes none; the data sets and
render entries it adds do not ship.

## 1. Map the values

Record every rendered value whose content or quantity is not fixed in the code,
a count and the absence of a value included. For each, record:

- its origin: where it comes from;
- its injection point: where the project injects data for it when the UI is
  rendered outside production (step 2 uses it), or the note that it has none;
- its limit, taken from every layer that accepts or stores the value. Where
  layers disagree, keep each limit, build to the most permissive path by which
  data can arrive, and report the disagreement as a finding. A value no layer
  limits is open. An open value is a finding only where this system accepts and
  stores it; where a caller or an outside service owns it, note it as open and
  no more.

Done when every such value has its origin, its injection point or the note that
it has none, and its limits or the mark open.

## 2. Build the data

For each value, build data that breaks an assumption and is admissible.
Admissible means traceable: to a pattern in what you may read (the project's
sample and seed data, its domain documents, what the user says) or to a limit a
layer states. Read no live records of real users for this. Keep the trace with
the value; step 4 needs it to make the finding reproducible. The classes, by
what is assumed:

- extent: the value takes less room than assumed, or more, or cannot be broken
  across lines at all.
- presence: an optional value is absent; a resource the UI loads does not
  arrive.
- composition, from what the code mishandles to what the layout does:
  characters a renderer would take as instructions; spacing and line breaks
  where one plain line was assumed; single characters built from several code
  points; scripts and reading directions other than the samples'.
- band: a number or a time at or beyond an edge of the band the code handles.
  For a number: both ends, the smallest counts where wording changes, and a
  value that is no number. For a time: the unset value, and times far from now
  in either direction.
- quantity: a collection with nothing, with one item, at the size of a page and
  one beyond, and at its real upper size.
- mixture: what occurs together: every value of an enumerated field at once,
  items with and without their optional values side by side, items that differ
  only in what the UI does not show, the viewer's own entry among the others.
- proportion: a picture or media item that cannot be told from its background
  in a supported theme, or whose shape is far from the one assumed.

Place the hard values so that each is in view at the same time and none hides
another. Collections of different sizes are separate sets. The main set is the
one of ordinary size that carries the hard values. Addresses and links use
names reserved for documentation, so that nothing in a set can be delivered or
fetched.

The data replaces the sample data at the injection point step 1 recorded, and
nowhere else. To render a set you may add what the project's existing render
harness needs, an entry of the kind it already has.

A value with no injection point: invent none and touch no product code. Record
it as blocked, ask the user, naming the ways you see, and go on with the other
values. When the answer is a way that changes product code, that change is the
user's ordinary request, made outside this review; the review then uses the
point it gives. A switch inside the product for flipping between sets is a
product change and is not made under this skill.

Done when each class that applies to a mapped value is in a set with its trace,
or the value is recorded as blocked.

## 3. Look

The base condition is what a viewer with default settings sees where the UI
lives. Render in this order:

1. The sample data at the base, as the reference. A fault it already shows is
   recorded as present without hard data and is not a data finding.
2. Every set at the base.
3. The main set under each variation the product supports, one changed at a
   time from the base, in the order of who sets the condition. The viewer's
   settings first, since they follow the viewer to every screen: language (the
   one with the longest interface text), time zone (one that moves a shown time
   to another day), number format, reading direction, theme, and the largest
   text size the platform's accessibility setting or the product's stated
   target gives. Then the device: input that cannot hover. Then the place: the
   widest and the narrowest width the product supports.

A set whose layout differs from the main set's (the one with nothing in it, as
a rule) takes the place variations too. These are conditions of viewing, set
where the product sets them for a viewer; none is put into the data.

Where the UI cannot be rendered in this session at all, or one variation cannot
be set, say so at once, go on by reading the code against each set, and mark
every finding from that reading inferred.

Done when the reference and each set have their base render, and the main set
has one render per variation that applies. Each variation that does not apply,
and each render not made, is recorded with why.

## 4. Report, then stop

Report in this order: what held, the findings, where the sets are.

- What held: the hard cases the UI passes. They are the set a later fix is run
  against again.
- Findings, most severe first. Severity has two parts, both stated, and the
  first ranks before the second. The effect: the user leaves with the task
  undone or with a false belief, or the user gets through on a screen that
  shows a fault. The exposure: observed, when data of this kind is in something
  you may read (the repository, a development or seed store, a store the user
  asks you to read and names) or the user says it occurs; admitted, when the
  system would accept it and nothing you may read shows it. Read a live store
  to settle exposure only where the user asks and names it.
- Each finding gives, in the order needed to reproduce it: the data set and the
  condition; the value and its trace; what is observed; whether that was seen
  in a render or inferred from the code; where in the code the cause is; and a
  proposed fix. Where the fix depends on a product choice the code cannot
  settle, state the choice and a recommendation in place of a fix.
- Last: where the data sets and render entries are, how each set is rendered
  again, and every value recorded as blocked.

A report with no findings is complete. Fixes are not part of the review. When
the request that started the review already asks for them, make the report
first and let the fixes follow without a second ask, as frontend-design's work
when they meet its trigger and ordinary work otherwise. When it does not, stop
at the report.

Done when steps 1 to 3 ended, each finding has its fields and both severity
parts, the report names what held and where the sets are, and nothing the
review itself did changed product code. A change the user asked for as an
ordinary request, and any change already in the tree before the review began,
are not the review's.

## Borders

- When a UI is being built or changed, its own data check included:
  frontend-design.
- When the question is how a screen looks while its own request is loading, has
  failed or is refused: outside this review, and no skill here reviews it. A
  resource inside a rendered screen that does not arrive is inside (presence).
- When structurally different designs are to be compared: throwaway-prototype.
  A switch between data sets inside the product is a product change and an
  ordinary request.
- When a collection is slow at its real size, once seen:
  performance-verification. This review reports it and measures nothing.
