# svgling: syntax trees in python + svg

The `svgling` package is a pure python package for doing single-pass rendering
of linguistics-style constituent trees into SVG. It is primarily intended for
integrating with Jupyter notebooks, but could be used to generate SVG diagrams
for all sorts of other purposes. It involves no javascript and so will work
in Jupyter without any plugins.

It accepts two main tree formats: lisp-style trees made from lists of lists (or
tuples of tuples), with node labels as strings, or trees from the
[`nltk`](https://www.nltk.org/) package, i.e. objects instantiating the
[`nltk.tree.Tree`](https://www.nltk.org/_modules/nltk/tree.html) API.

**Dependencies**: [`svgwrite`](https://pypi.org/project/svgwrite/), python 3

The basic interface is pretty simple: pass a tree object to `svgling.draw_tree`.

    svgling.draw_tree(("S", ("NP", ("D", "the"), ("N", "rhinoceros")), ("VP", ("V", "saw"), ("NP", ("D", "the"), ("N", "elephant"))))


This produces an SVG image like the following:

![example sentence](./demotree.svg)

The package also by default tries by default to monkeypatch `nltk.tree.Tree` so
that a Jupyter notebook will use svg-based rendering, instead of the built-in
.png rendering. For more examples and documentation, see
[Overview.ipynb](./Overview.ipynb); a rendered preview version can be seen
[here](https://nbviewer.jupyter.org/github/rawlins/svgling/blob/master/Overview.ipynb).

There are many things that it might be nice to add to this package; if you find
`svgling` useful, have any requests, or find any bugs, please let me know.
There's a small roadmap and discussion of possible features at the end of
`Overview.ipynb`.
