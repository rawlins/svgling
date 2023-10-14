# Changelog for `svgling`

## [0.4.0] - Node styling and compatibility - 2023-09-25

As of 0.3.1, `svgling` is the default tree-drawing package for `nltk` Trees
in Jupyter; this update provides better compatibility for that. It also
improves some styling options, and direct support for format conversion.

New features:

- Limited per-node styling in trees: supports changing font style, size, and
  color/fill
- convenience wrappers to make conversion to PNG/PDF via the `cairosvg`
  package easier (`cairosvg` is now an optional package dependency)
- Support `nltk.Tree` objects directly in `svgling.figure` classes

Fixes, improvements, changes:

- Simplify import code for nltk, remove monkeypatching
- The option `global_font_style` is renamed to just `font_style`
- Refactor `TreeOptions` to make it easier to pass around options bundles
- Default change: `relative_units=False`. This provides better compatibility
  with inkscape, among other things. This option is now deprecated.
- Documentation improvements

## [0.3.1] - Inkscape compatibility - 2021-10-11

New feature:

- Compatibility mode aimed at Inkscape: allow using `px` instead of relative
  `em` units. This allows current versions of Inkscape to load the output
  SVGs. This mode is not on by default.

Fixes, improvements, changes:

- Update documentation to reflect some issues in MathJax math mode delimeter
  choice for hybrid mode.

## [0.3.0] - Hybrid HTML/SVG tree drawing - 2018-12-10

New features:

- Basic support for drawing trees using a mix of HTML/CSS (for positioning) and
  SVG (for line drawing). This is much more limited than the core drawing
  algorithms, but allows for arbitrary node labels + MathJax.

Fixes, improvements, changes:

- Improve documentation

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

## [0.1.3] - Bugfix release - 2018-11-8

- Fix for non-leaf nodes that are larger than the leaf nodes they dominate.
- More flexible arguments to `draw_tree` (will accept the top node + children
  via variable arguments, rather than a list/tuple as the first argument.)
- Documentation improvements.

## [0.1.2] - First real release - 2018-11-7

- Support for basic tree drawing with lists and `nltk.tree.Tree` objects.
