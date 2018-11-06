# svgling: syntax trees in python + svg

The `svgling` package is a pure python package for doing single-pass rendering
of linguistics-style constituent trees into SVG. It is primarily intended for
integrating with Jupyter notebooks, but could be used to generate SVG diagrams
for all sorts of other purposes.

It accepts two main tree formats: lisp-style trees made from lists of lists (or
tuples of tuples), with node labels as strings, or trees from the `nltk`
package, i.e. objects instantiating the `nltk.Tree` API.

**Dependencies**: svgwrite, python 3

The basic interface is pretty simple: pass a tree object to `svgling.draw_tree`.

    svgling.draw_tree(("S", ("NP", ("D", "the"), ("N", "rhinocerous")), ("VP", ("V", "saw"), ("NP", ("D", "the"), ("N", "elephant"))))

This produces an SVG image like the following:

![example sentence](./demotree.svg)

For more examples and documentation, see [Overview.ipynb](./Overview.ipynb).

There are many things that it might be nice to add to this package; if you find
it useful, have any requests, or find any bugs, please let me know. There's a
small roadmap at the end of the above .ipynb.
