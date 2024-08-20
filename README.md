# `svgling`: Linguistic tree diagrams in python + svg

**Author**: Kyle Rawlins, [kgr@jhu.edu](kgr@jhu.edu)

**Website and documentation**: [https://rawlins.github.io/svgling/](https://rawlins.github.io/svgling/)

**Dependencies**: [`svgwrite`](https://pypi.org/project/svgwrite/), python 3, (optional) [cairosvg](https://cairosvg.org/)

**Repository**: [https://github.com/rawlins/svgling/](https://github.com/rawlins/svgling/)

**Installation**: `pip install svgling` for the current release version, install from the repository for the current unreleased version. (E.g., `pip install git+https://github.com/rawlins/svgling`)

**License**: MIT License

## Overview

The `svgling` package is a pure python package for doing single-pass rendering
of tree diagrams as used in Linguistics and NLP, in the [SVG (Scalable Vector
Graphics)](https://www.w3.org/Graphics/SVG/) format. It is primarily intended
for integrating with Jupyter notebooks, but can also be used to generate SVG
diagrams for all sorts of other purposes. It involves no javascript and so
will work in Jupyter without any plugins.

The basic interface is pretty simple: pass a tree-describing object to
`svgling.draw_tree` (e.g. a tuple consisting of a label and a sequence of
daughter nodes, which may themselves be trees).

    import svgling
    svgling.draw_tree(("S", ("NP", ("D", "the"), ("N", "elephant")), ("VP", ("V", "saw"), ("NP", ("D", "the"), ("N", "rhinoceros")))))

In Jupyter, this code produces an SVG image like the following:

![example sentence](https://raw.githubusercontent.com/rawlins/svgling/master/demotree.svg?sanitize=true)

The tree drawing code accepts two main tree formats: lisp-style trees made from
lists of lists (or tuples of tuples), with node labels as strings, or trees from
the [`nltk`](https://www.nltk.org/) package, i.e. objects instantiating the
[`nltk.tree.Tree`](https://www.nltk.org/_modules/nltk/tree.html) API. The
following nltk code run in Jupyter, as long as `svgling` has been installed,
produces an identical tree diagram to the above example:

    nltk.Tree.fromstring("(S (NP (D the) (N elephant)) (VP (V saw) (NP (D the) (N rhinoceros))))")

On current versions of `nltk`, the support goes both ways: the default (and
only) tree renderer in Jupyter is `svgling`. If the package is installed, nltk
`Tree`s will automatically render using svgling trees. For more control, you can
also provide a tree directly to the `svgling.draw_tree` function, which allows
you to use options:

    x = nltk.Tree.fromstring("(S (NP (D the) (N elephant)) (VP (V saw) (NP (D the) (N rhinoceros))))")
    svgling.draw_tree(x, leaf_nodes_align=True)

Beyond basic tree-drawing, the package supports a number of flourishes like
movement arrows. For documentation and examples, see the project website:

* [Overview of the package](https://rawlins.github.io/svgling/)
* [`svgling` diagram gallery](https://rawlins.github.io/svgling/gallery.html)
* [Full manual for `svgling`](https://rawlins.github.io/svgling/manual.html)

These three pages are directly rendered from notebooks in the [docs/]
(https://github.com/rawlins/svgling/tree/master/docs) directory that you can
also download and execute in Jupyter Lab (or another frontend, modulo some
compatibility notes).

## Core design principles and goals

1. Be well suited for *programmatic* generation of tree diagrams (not just
hand-customized diagrams).
2. Be equally suited for theoretical linguistics and computational
linguistics/NLP, at least for cases where the latter is targeting constituent
trees. (This package is not aimed at dependency trees/graphs.)
3. Do as much as possible with pure python (as opposed to python+javascript, or
python+tk, or python+dot, or...).

## Strengths and limitations

The `svgling` package does its rendering in one pass -- it takes a tree
structure as input, produces an svg output, and that's it. Because of this,
it is extremely simple to use in Jupyter, and no messing with plugins or
Jupyter settings should be necessary. Because it is SVG-based, scaling and
embedding in any web context should work smoothly. It also has minimal
dependencies, just one package
([`svgwrite`](https://github.com/mozman/svgwrite)) that provides an abstraction
layer over the process of generating valid SVG text.

Single-pass rendering also places limitations on what can be done. One of the
challenges is that it mostly uses absolute position, and the exact position
and width of text elements can't be determined without actually rendering to
some device and seeing what happens. In addition, the exact details of
rendering are in various ways at the mercy of the rendering device. This all
means that `svgling` uses a bunch of tricks to estimate node size and width,
and won't always be perfect on all devices. This situation also places some
hard limitations on how far `svgling` can be extended without adding
javascript or other multi-pass rendering techniques. For example, I would
eventually like to allow mathjax in nodes, but at the moment this does not
seem possible in pure SVG without javascript on the client side. The package
does provide support for hybrid HTML/SVG tree diagrams that allows MathJax in
nodes, but this rendering mode comes with certain limitations.

There are many things that it might be nice to add to this package; if you find
`svgling` useful, have any requests, or find any bugs, please let me know.

## Compatibility

The SVG files produced by `svgling` should be compatible with all major browsers
(Chrome, Firefox, Safari, Edge) on both desktop and mobile; if you find a
compatibility issue with some browser, please [report it as a
bug](https://github.com/rawlins/svgling/issues). It also supports all major
interactive editing packages that I am aware of.

There are various ways to convert the generated SVG files to other formats,
including raster ones, but the recommended/supported way to do this
programmatically is via the [`cairosvg`](https://cairosvg.org/) package.
`svgling.utils` provides some convenience functions for conversion to
PNG/PDF/PS using cairosvg. See the "Compatibility and Conversion" section of
the svgling manual for more details. Note that `cairosvg` is an optional
dependency of `svgling`, so won't necessarily be installed by default.
