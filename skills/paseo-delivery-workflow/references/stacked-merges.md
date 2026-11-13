# Stacked merges

Stacked merges: heads that each stack on the previous one, each with its lanes and a `PASS`
on itself, merge in stack order. A stacked head need not contain the product line's current
head when the product line's current tree equals the tree of an ancestor of the head; its
squash then lands tree-equal to the head, with no product-line merge or lane rerun. When the
forge refuses such a head because its merge base is the pre-squash product line, merge the
product line into the head resolving every conflict to the head's side, prove the new head's
tree equals the tested head (empty diff), and squash pinned to the new head's SHA; no lane
reruns.
