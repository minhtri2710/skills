---
name: frontend-design
description: Implement a UI change whose rendered hierarchy, interaction flow, responsive behavior, or domain-fit visual design is a material part of acceptance. Do not use for copy-only edits, isolated design-token changes, headless UI logic, or minor component maintenance.
---

# Frontend Design

Build the requested product experience using the repository's design language. This skill owns visual and interaction quality, not product discovery or architecture.

Before editing, identify the audience, primary job, information density, existing
components, and material states. Make routine visual choices locally. Ask only when
different choices would change the product contract.

Where the repository has no design language for the surface, first write a
sentence each on the palette, typography, and arrangement that will make it
recognizably this product's. Then ask whether the same choices would come out for
a different product of the same kind, and revise whatever would before writing
any code.

Prioritize usable structure before decoration:

- expose the primary workflow and action
- preserve semantic controls, keyboard and focus behavior
- handle loading, empty, error, disabled, selected, and recovery states that belong to the flow
- write the interface text this change adds from the result the user gets: label
  a control by the outcome it produces, in the user's own words for the thing
  rather than the system's, repeat the label's verb wherever the flow refers to
  that action again, and give a failure message the fault and the next step
- prevent clipping, overlap, hidden actions, and unintended layout shifts
- assert nothing in the UI that the repository cannot back (figures,
  endorsements, comparisons): leave it out, or name it in the report as
  unverified; shape sample data like the domain's real records
- use domain content and established assets instead of generic card grids, gradients, glass, blobs, oversized marketing headings, cream or off-white backgrounds, italic accent words in headlines, numbered "01/02/03" section labels, monospace labels, or pill-shaped buttons, unless the repository's design language already uses them
- keep motion rare and tied to what the user just did, never ornament across
  sections or cards, and honor the reduced-motion preference

Inspect the rendered result at the representative viewports required by the change
and exercise the primary affected workflow. Render data-driven text and lists with
the longest and shortest values the schema allows, an optional value missing, and
zero, one, and many items. Do not add a separate verification ceremony or
unrelated cleanup. If rendered inspection is unavailable, report that limitation
without claiming visual completion.
