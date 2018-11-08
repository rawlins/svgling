# Changelog for `svgling`

## [0.1.2] - First real release - 2018-11-7

- Support for basic tree drawing with lists and `nltk.tree.Tree` objects.

## [0.1.3] Bugfix release - 2018-11-8

- Fix for non-leaf nodes that are larger than the leaf nodes they dominate.
- More flexible arguments to `draw_tree` (will accept the top node + children
  via variable arguments, rather than a list/tuple as the first argument.)
- Documentation improvements.
