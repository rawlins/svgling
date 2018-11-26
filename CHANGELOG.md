# Changelog for `svgling`

## [0.1.2] - First real release - 2018-11-7

- Support for basic tree drawing with lists and `nltk.tree.Tree` objects.

## [0.1.3] - Bugfix release - 2018-11-8

- Fix for non-leaf nodes that are larger than the leaf nodes they dominate.
- More flexible arguments to `draw_tree` (will accept the top node + children
  via variable arguments, rather than a list/tuple as the first argument.)
- Documentation improvements.

## [0.2.0] - Core features complete - 2018-11-26

New features:
- Support for multi-line nodes.
- Edge styles, muti-segment descents for level skipping.
- Wrote a manual.
- Tree annotations: movement arrows, constituent highlighting / underlining.
- Complex figures: grids of trees, captioning.

Fixes, improvements, changes:
- Massively improve responsivity of svgling diagrams.
- TreeLayout objects manage font size directly.
- `distance_to_daughter` is now a distance between levels, i.e. excluding node
  height.
