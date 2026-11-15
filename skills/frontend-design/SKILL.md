---
name: frontend-design
description: Implement a UI change whose rendered hierarchy, interaction flow, responsive behavior, or domain-fit visual design is a material part of acceptance. Do not use for copy-only edits, isolated design-token changes, headless UI logic, or minor component maintenance.
---

# Frontend Design

Build the requested product experience using the repository's design language. This skill owns visual and interaction quality, not product discovery or architecture.

Before editing, identify the audience, primary job, information density, existing
components, and material states. Make routine visual choices locally. Ask only when
different choices would change the product contract.

Where the repository has no design language for the surface, the failure to avoid
is a look that would suit any product. Before any code, state in a sentence each
what the arrangement, the type, and the color do for this product, and revise
every choice that would serve a different product of the same kind equally well.

Prioritize usable structure before decoration:

- expose the primary workflow and action
- preserve semantic controls, keyboard and focus behavior
- handle loading, empty, error, disabled, selected, and recovery states that belong to the flow
- write the interface text this change adds from the result the user gets: label
  a control by the outcome it produces, in the words the product's users already
  have for the thing, repeat the label's verb wherever the flow refers to that
  action again, and give a failure message the fault and the next step
- prevent clipping, overlap, hidden actions, and unintended layout shifts
- shape sample data like the domain's real records, and show no figure,
  endorsement, or comparison the repository cannot back: omit it and list the
  omission in the report
- use domain content and established assets instead of generic card grids, gradients, glass, blobs, oversized marketing headings, cream or off-white backgrounds, italic accent words in headlines, numbered "01/02/03" section labels, monospace labels, or pill-shaped buttons, unless the repository's design language already uses them
- keep motion to what the repository's design language already animates; where it
  has none, animate only in response to what the user just did, and honor the
  reduced-motion preference either way

Inspect the rendered result at the representative viewports required by the change
and exercise the primary affected workflow. Render the data-driven text and
lists the change touches with the longest and shortest values the schema allows,
an optional value missing, and zero, one, and many items. Do not add a separate
verification ceremony or unrelated cleanup. If rendered inspection is
unavailable, report that limitation without claiming visual completion.
