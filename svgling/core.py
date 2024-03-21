import enum, math, functools
import collections.abc

from xml.etree import ElementTree
import svgwrite


################
# Tree utility functions
#
# For generically handling the various kinds of tree-like things that can be
# passed to this module
################


def treelet_split_nltk(t):
    """Given some tree representation `t`, attempt to split `t` using the
    `nltk.Tree` API.

    Parameters
    ----------
    t
        A tree object to attempt to split. `t` will be handled by this function
        if it implements ``t.label()`` and can be converted to `list`.

    Returns
    -------
    Returns a tuple consisting of a `str` node label, and a (possibly empty)
    list of children; or `None` if `t` does not implement the ``nltk.Tree`` api.
    """
    try:
        return (t.label(), list(t))
    except (AttributeError, TypeError):
        return None


def probtree_split(t):
    """Given some tree representation `t`, attempt to split `t` using the
    `nltk.tree.probabilistic.ProbabilisticTree` API, showing both the label
    and the inside probability of the tree.

    Parameters
    ----------
    t
        A tree object to attempt to split. `t` will be handled by this function
        if it implements both ``t.label()`` and ``t.prob()``  and can be
        converted to `list`.

    Returns
    -------
    Returns a tuple consisting of a `str` node label, and a (possibly empty)
    list of children; or `None` if `t` does not implement the
    `nltk.tree.probabilistic.ProbabilisticTree` api.

    See also
    --------
    `treelet_split_nltk` : split a tree using the base `nltk.Tree` api. Note
    that `ProbabilisticTree` is a subclass of `Tree`, and so the referenced
    function will also work on `ProbabilisticTree` instances, but will not
    show the probability value.
    """

    try:
        return (f"{t.label()} [p={t.prob()}]", list(t))
    except (AttributeError, TypeError):
        return None


def treelet_split_list(t):
    """Given some tree representation `t`, attempt to split `t` by treating
    it as a lisp-style sequence of a node followed by 0 or more child
    subtrees. `t` is length 0, it is treated as an empty leaf node
    returning ``("", ())``. This function does not enforce any type for the
    node value.

    Parameters
    ----------
    t
        A tree object to attempt to split; `t` will be handled by this function
        if it is a sequence that is not a `str`.

    Returns
    -------
    Returns a 2-tuple consisting of a node, and a (possibly empty)
    sequence of children, or `None` if t is either a `str` or a non-sequence.
    """

    if not isinstance(t, collections.abc.Sequence) or isinstance(t, str):
        return None

    if (len(t) == 0):
        # empty leaf node
        return ("", tuple())
    else:
        return (t[0], t[1:])


def tree_split(t, node_fun=lambda x: x):
    """Given some tree representation `t`, attempt to split `t` into a
    a pair consisting of a node and a sequence of child subtrees. A leaf node
    is indicated by an empty sequence in the second slot (so that
    ``len(result[1])`` always gives the number of children.) This function
    handles lisp-style trees, as well as ``nltk.Tree`` objects. It does not
    in and of itself enforce anything about what the nodes are, but `node_fun`
    can do this.

    Parameters
    ----------
    t
        A tree object to attempt to split

    node_fun : Callable
        A function that can handle the conversion from raw nodes into
        representation-specific objects. The default value is the identity
        function. `node_fun` must be able to at least handle `str` arguments.

    Returns
    -------
    tuple
        A 2-tuple consisting of a node, and a (possibly empty) sequence of
        child subtrees.
    """

    # order nltk before general sequence handling: nltk.Tree subclasses `list`
    split = treelet_split_nltk(t)
    if split is not None:
        return (node_fun(split[0]), split[1])
    split = treelet_split_list(t)
    if split is not None:
        return (node_fun(split[0]), split[1])
    # treat `t` as a leaf node:
    return (node_fun(t), ())


def tree_parse(t, node_fun=lambda x: x):
    """Given some tree representation `t`, attempt to fully parse `t` using
    the `tree_split` function and the provided node function into a lisp-style
    tree representation. By default, if a tree is already parsed, this call
    is a noop.

    Parameters
    ----------
    t
        A tree object to attempt to parse

    node_fun : Callable
        A function that can handle the conversion from raw nodes into
        representation-specific objects. The default value is the identity
        function.

    Returns
    -------
    tuple
        a lisp-style tree structure with a node in position 1, followed by
        0 or more subtrees.
    """
    n, children = tree_split(t, node_fun=node_fun)
    return (n,) + tuple(tree_parse(c, node_fun=node_fun) for c in children)


def _tree_cxr(t, i, split=tree_split):
    return split(t)[i]


def tree_car(t, split=tree_split):
    """
    What is the parent of a tree-like object `t`?

    Parameters
    ----------
    t
        A tree object of some kind; this code is flexible and will handle
        a range of possibilities for `t`, including list-like structures, and
        objects that implement the `nltk.Tree` api.

    split : Callable
        A tree split function for handling `t`. The default value is the
        module-level `tree_split` function.

    Returns
    -------
    Any
        A node object of some kind
    """
    return _tree_cxr(t, 0, split=split)


def tree_cdr(t, split=tree_split):
    """
    What are the children of a tree-like object `t`?

    Parameters
    ----------
    t
        A tree object of some kind; this code is flexible and will handle
        a range of possibilities for `t`, including list-like structures, and
        objects that implement the `nltk.Tree` api.

    split : Callable
        A tree split function for handling `t`. The default value is the
        module-level `tree_split` function.

    Returns
    -------
    Sequence
        A (possibly empty) sequence of subtrees in normalized form.
    """
    return _tree_cxr(t, 1, split=split)


def is_leaf(t, split=tree_split):
    """
    Is tree-like object `t` a leaf node?

    Parameters
    ----------
    t
        A tree object of some kind; this code is flexible and will handle
        a range of possibilities for `t`, including list-like structures, and
        objects that implement the `nltk.Tree` api.

    split : Callable
        A tree split function for handling `t`. The default value is the
        module-level `tree_split` function.

    Returns
    -------
    bool
        True iff `t` has 0 daughter nodes
    """
    return len(tree_cdr(t, split=split)) == 0


def tree_depth(t, split=tree_split):
    """
    What is the maximum (deepest) depth of tree-like object `t`?

    Parameters
    ----------
    t
        A tree object of some kind; this code is flexible and will handle
        a range of possibilities for `t`, including list-like structures, and
        objects that implement the `nltk.Tree` api.

    split : Callable
        A tree split function for handling `t`. The default value is the
        module-level `tree_split` function.

    Returns
    -------
    int
        a non-negative depth value
    """
    subdepth = 0
    for subtree in tree_cdr(t, split=split):
        subdepth = max(subdepth, tree_depth(subtree, split=split))
    return subdepth + 1


def leaf_iter(t, split=tree_split):
    """
    What is the maximum (deepest) depth of tree-like object `t`?

    Parameters
    ----------
    t
        A tree object of some kind; this code is flexible and will handle
        a range of possibilities for `t`, including list-like structures, and
        objects that implement the `nltk.Tree` api.

    split : Callable
        A tree split function for handling `t`. The default value is the
        module-level `tree_split` function.

    Yields
    ------
    Any
        Leaf nodes in `t`
    """

    parent, children = split(t)
    if len(children) == 0:
        yield parent
    for c in children:
        yield from leaf_iter(c, split=split)


def common_parent(path1, path2):
    """
    Find the longest common tree path between the two arguments, i.e. the
    path to the deepest shared parent.

    Parameters
    ----------
    path1 : Sequence[int]
        A tree path

    path2 : Sequence[int]
        A tree path

    Returns
    -------
    Sequence[int]
        The longest common shared path for `path1` and `path2`
    """

    for i in range(min(len(path1), len(path2))):
        if path1[i] != path2[i]:
            return tuple(path1[0:i])
    if len(path1) < len(path2):
        return path1
    else:
        return path2


################
# Tree layout options
################

def cssfont(family, weight="normal", style="normal"):
    """A function that produces CSS font strings given some templatic info.
    Note that for svgling purposes, the size is not included here -- it is
    handled separately.

    Parameters
    ----------
    family: str
        a font family to choose, e.g. ``times``, ``Arial, Helvetica, sans-serif``, etc.

    weight: str
        The font's weight. E.g. ``normal``, ``bold``. Default: ``normal``.

    style: str
        The font style. E.g. ``normal``, ``italic``, ``oblique``. Default: ``normal``.
    """
    return f"font-family: {family}; font-weight: {weight}; font-style: {style};"

SERIF = cssfont("times, serif")
# n.b. Lucida Console is more like 1.5 average glyph width
MONO = cssfont('"Lucida Console", Monaco, monospace')
SANS = cssfont("Arial, Helvetica, sans-serif")

# either EVEN or NODES usually looks best with abstract trees; TEXT usually
# looks the best for trees with real node labels, and so it is the default.
class HorizSpacing(enum.Enum):
    """Settings for horizontal spacing in trees.

    `TEXT`:  Space daughter nodes proportional to label width (default)
    `EVEN`:  Space daughter nodes evenly
    `NODES`: Space daughter nodes based on number of leaf nodes
    """
    TEXT = 0
    EVEN = 1
    NODES = 2

    # generate valid python repr (as long as enum class is imported)
    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'

HorizOptions = HorizSpacing # backwards compatibility

class VertAlign(enum.Enum):
    """
    Settings for vertical node alignment. Nodes are aligned to a level.

    `TOP`:    align nodes at the top of the level's height
    `CENTER`: align nodes to the center of the level's height (default)
    `BOTTOM`: align nodes with the bottom of the level's height
    `FULL`:   all nodes take up full level height, with text aligned to the top
    """
    TOP = 0
    CENTER = 1
    BOTTOM = 2
    FULL = 3

    # generate valid python repr (as long as enum class is imported)
    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'

def px(n):
    """Given a numeric value, return a string with ``px`` units."""
    return f"{n:g}px"

def em(n, options=None):
    """Given a numeric size in ``em`` units, produce an appropriate css string
    in the context. If `options` is provided, this will typically convert to
    ``px`` based on the current font size. (Generally, it is more reliable
    for compatibility to convert to ``px`` this way rather than relying on the
    svg renderer.)

    Parameters
    ----------
    n : Number
        a size value interpreted in ``em``s (i.e. 1.0 is the baseline to
        baseline height of the current font)

    options : TreeOptions
        a tree options context, providing the current font size for unit
        conversion

    Returns
    -------
    str
        A CSS size string in either ``em`` or ``px`` units.
    """
    if options is None or options.relative_units:
        return f"{n:g}em"
    else:
        # convert into px using the font size specified in options. Per the
        # css spec, 1em is Xpx where X is the current font size.
        return px(options.em_to_px(n))

def perc(n):
    """Given a number `n`, convert to a css percentage string."""
    return f"{n:g}%"

crisp_perpendiculars = True

# the set of options available, and their default values
_opt_defaults = dict(
    horiz_spacing=HorizSpacing.TEXT,
    vert_align=VertAlign.CENTER,
    leaf_padding=2,
    distance_to_daughter=2,
    debug=False,
    leaf_edges=True,
    leaf_nodes_align=False,
    font_style=SERIF,
    # 2.0 default value is a heuristic -- roughly, 2 chars per em
    average_glyph_width=2.0,
    descend_direct=True,
    relative_units=False,
    font_size = 16,
    text_color = "",
    text_stroke = "",
    tree_split = None)

class TreeOptions(collections.abc.MutableMapping):
    """
    An options container class for tree rendering. This class is a flexible
    mapping class that accepts allowed options as named parameters to the
    constructor, as attributes, or via a standard dict interface. All valid
    options have a value on a `TreeOptions` object.

    Allowed options:

        ``horiz_spacing``:  a `HorizSpacing` value indicating horizontal tree spacing.
                            default: `HorizSpacing.TEXT`
        ``vert_align``:     a `VertAlign` value indicating vertical node alignment.
                            default: `VertAlign.CENTER`
        ``leaf_padding``:   a value indicating how much total extra padding in the x dimension
                            to add around leaf nodes; this is interpreted as a glyph count,
                            so is relative to ``average_glyph_width``. default: 2
        ``distance_to_daughter``: a value in ``em``s indicating the spacing between
                                  levels in the tree. default: 2
        ``debug``:          if set to ``True``, renders a grid and node outlines. default: False
        ``leaf_edges``:     Whether the terminal edge line sections will be drawn to leaf nodes.
        ``leaf_nodes_align``: if set to true, all leaf nodes will align at the lowest level
                              of the tree. Otherwise, leaf nodes are just the normal distance
                              from their parent node. default: False
        ``font_style``:     a (size-less) CSS font string. It is recommended to construct these
                            using `cssfont`. Default: `SERIF`
        ``average_glyph_width``: because `svgling` doesn't (and essentially can't) know font
                                 glyph info in the general case, it needs to heuristically
                                 guess this for horizontal spacing purposes. This option is
                                 a tweakable parameter in the unit of characters per ``em``,
                                 that you can change if you use a wider or narrower font. It
                                 is calibrated to look reasonable by default with standard
                                 serif and sans serif options. Default: 2.0.
        ``descend_direct``: For multi-level descents (if ``leaf_nodes_align`` is set to
                            True), should the edge from parent to daughter descend directly
                            or render a segmented line that is diagonal only at the current
                            level? default: True
        ``relative_units``: Whether the renderer will produce relative units (``em``s) or
                            absolute units (``px``s) based on the current font size.
                            Absolute units are better for compatibility, and this option
                            is essentially a legacy option. Default: False
        ``font_size``:      a CSS font size value, that will determine how many ``px`` are
                            in ``1em``. Setting font size in any other way will most likely
                            break svgling rendering. Default: 16.
        ``text_color``:     A CSS color to use as the text color. Default: '' (inherit)
        ``text_stroke``:    A CSS stroke value to use as the text stroke. Default: '' (inherit)
        ``tree_split``:     A custom tree split function to use for parsing tree objects.
                            see the manual for more details. Default: None
        """

    def __init__(self, global_font_style=None, **opts):
        global _opt_defaults
        mismatch = [k for k in opts if k not in _opt_defaults]
        if len(mismatch) == 1:
            raise TypeError(f"Unknown tree option '{mismatch[0]}'")
        elif len(mismatch):
            raise TypeError(f"Unknown tree options: {', '.join(mismatch)}")

        self.explicit = set(opts.keys())

        fullopts = _opt_defaults.copy() # default values
        fullopts.update(opts) # values from kwargs to constructor
        for k in fullopts:
            setattr(self, k, fullopts[k])

        # deprecated name, but still allow setting in constructor. See the
        # managed setter below. Simply overrides `font_style`.
        if global_font_style:
            self.global_font_style = global_font_style

    def __getitem__(self, k):
        global _opt_defaults
        if k not in _opt_defaults:
            raise KeyError(k)
        return getattr(self, k)

    def __setitem__(self, k, val):
        global _opt_defaults
        if k not in _opt_defaults:
            raise KeyError(k)
        self.explicit.add(k)
        setattr(self, k, val)

    def __delitem__(self, k):
        """Clear an option setting from this options object. Unlike a standard
        ``dict`` object, this does not remove `k` from keys, but rather resets
        ``self[k]`` to the default value."""
        global _opt_defaults
        self[k] = _opt_defaults[k]
        if k in self.explicit:
            self.explicit.remove(k)

    def __len__(self):
        global _opt_defaults
        return len(_opt_defaults)

    def __iter__(self):
        global _opt_defaults
        return iter(_opt_defaults)

    def __repr__(self):
        return repr(dict(self))

    def __str__(self):
        return str(dict(self))

    def update_explicit(self, other):
        """Update this options object with only the values explicitly set in
        `TreeOptions` object `other`.

        Parameters
        ----------
        other : TreeOptions
            An options object to update from
        """
        for k in other.explicit:
            self[k] = other[k]

    def _repr_pretty_(self, p, cycle):
        return p.pretty(dict(self))

    def copy(self):
        """Return a copy of this TreeOptions object"""
        new = TreeOptions()
        new.update_explicit(self)
        return new


    def style_str(self, size_only=False, scale=None):
        """Given some options, produce a complete CSS style string, including
        the font size value.

        Parameters
        ----------
        size_only : bool
            if set to True, produce only the size string. (If
            ``self.font_style`` is None, that will also cause this behavior.)

        scale : Union[int, None]
            if set, multiply font size by some scale value. The result will
            produce only integer font sizes.

        """
        fs = self.font_size
        if scale:
            fs = int(fs * scale)
        size = f"font-size: {px(fs)}"
        # empty or None font_style is effectively inherit. This is risky on
        # global values...
        if size_only or not self.font_style:
            return size
        # XX: nothing checks syntax here so it's easy for the user to make
        # mistakes if they don't use the factory functions...
        return f"{self.font_style} {size}"

    def label_width(self, label):
        """Get a label width in ``em``s given leaf padding, and the average
        glyph width heuristic in the current context."""
        return (len(str(label)) + self.leaf_padding) / self.average_glyph_width

    def _base_tree_split(self, t):
        # use module-level function
        return tree_split(t, node_fun=NodePos.from_label)

    def split(self, t):
        """
        Given some tree representation `t`, produce a canonicalized form with
        the nodes handled, etc. This will take into account a custom
        ``tree_split`` function set as an option on this object.

        Parameters
        ----------
        t
            A tree representation to parse.

        Returns
        -------
        Sequence
            A sequence in canonicalized tree form

        See also
        --------
        tree_split : the module-level function that does most of the work.
        """
        if self.tree_split:
            # try custom tree_split option
            r = self.tree_split(t)
            if r is not None:
                node, children = r
                # now, we use the base split function to canonicalize the
                # return value of `tree_split`, including applying the
                # appropriate node construction in case the custom tree_split
                # has returned a `str` label
                return self._base_tree_split((node,) + tuple(children))
        return self._base_tree_split(t)

    def tree_height(self, t):
        """Calculate tree height, in ems. Takes into account multi-line leaf
        nodes."""
        # TODO: generalize to multi-line nodes of all kinds.
        # XX or remove -- this code is not currently used
        parent, children = self.tree_split(t)
        if len(children) == 0:
            return len(parent.split("\n"))
        subheight = 0
        for subtree in children:
            subheight = max(subheight, self.tree_height(subtree))
        return subheight + self.distance_to_daughter + 1

    def em_to_px(self, n):
        """Convert an ``em`` value into (absolute) ``px``, given the current
        font size."""
        return n * self.font_size

    # backwards compatibility:
    @property
    def global_font_style(self):
        return self.font_style

    @global_font_style.setter
    def global_font_style(self, val):
        self.font_style = val

def leaf_nodecount(t, options=None):
    """How many nodes wide are all the leafs? Will add padding."""
    if options is None:
        options=TreeOptions()
    parent, children = options.split(t)
    if len(children) == 0:
        return 1 + options.leaf_padding
    subwidth = 0
    for subtree in children:
        subwidth += leaf_nodecount(subtree, options)
    return subwidth

################
# Tree layout and SVG generation
################


# this is implemented as a class, not just a function, in order to
# allow for explicit typing
class DeferredNodePos(object):
    """Wrapper class that will finalize a node builder with an options object
    supplied from a specific tree context."""
    def __init__(self, f, text="", options=None):
        self.text = text
        if not callable(f):
            raise ValueError("DeferredNodePos needs a callable!")
        self.f = f
        self.outer_opts = options

    def __call__(self, options=None):
        if self.outer_opts is not None:
            # any explicitly set options at the outer layer will be used at
            # the inner layer. However, explicit options provided from the
            # tree context on finalizing will still be used if not overridden.
            # if the same option is set differently in both, the outer version
            # will win (with no errors)
            if options is None:
                # make a copy to prevent side effects in case this object is
                # reused
                options = self.outer_opts.copy()
            else:
                # modify a copy only to prevent side-effects
                options = options.copy()
                options.update_explicit(self.outer_opts)
        return self.f(options=options)

    def __repr__(self):
        if self.text:
            return f"DeferredNodePos({repr(self.text)})"
        else:
            # kind of hacky, but instantiate this node and get the resulting
            # text
            return f"DeferredNodePos({self().text})"

    def _repr_svg_(self):
        # debugging shortcut
        return self()._repr_svg_()

def node_builder(fun):
    """Decorator for functions that build NodePos objects, so that filling in
    options can be deferred until the tree is constructed."""
    def wrapped(*args, **kwargs):
        return DeferredNodePos(functools.partial(fun, *args, **kwargs), options=kwargs.get('options', None))
    return wrapped

@node_builder
def multiline_node(text, line_margin=0.0, options=None):
    # XX may be a nicer interface to also allow kw opts here
    if options is None:
        options = TreeOptions()

    # some explicit handling for this case is helpful, because otherwise
    # errors in this function on user mistakes are fairly cryptic.
    if not isinstance(text, str):
        raise TypeError(
            f"`multiline_text_to_node` needs a string, got {text.__class__}: `{repr(text)}`")
    svg_parent = svgwrite.container.SVG(x=0, y=0, width="100%")

    height = 0.0
    if len(text):
        lines = text.split("\n")
        for line in lines:
            height += 1.0 + line_margin # pre-increment to use as a y position
            svg_parent.add(svgwrite.text.Text(line, insert=("50%", em(height, options)),
                                                    text_anchor="middle",
                                                    fill=options.text_color,
                                                    stroke=options.text_stroke))
        width = max([options.label_width(line) for line in lines])
    else:
        # slightly different behavior on a completely empty label: use height
        # and width 0, and an empty parent (not a parent with an empty Text).
        width=options.label_width("")

    return NodePos(svg_parent, x=50, y=0, width=width, height=height,
        options=options, text=text)


# default node builder
node = multiline_node


@node_builder
def subscript_node(text, sub, scale=0.75, options=None):
    if options is None:
        options = TreeOptions()

    # try to make this robust to mistakes
    if not scale:
        scale = 1.0
    # values outside this range will render poorly, so just limit it
    scale = max(min(2.0, scale), 0.1)

    svg_parent = svgwrite.container.SVG(x=0, y=0, width="100%")
    text_parent = svgwrite.text.Text("", insert=("50%", em(1, options)),
                                                    text_anchor="middle",
                                                    fill=options.text_color,
                                                    stroke=options.text_stroke)
    span1 = svgwrite.text.TSpan(text)

    span2 = svgwrite.text.TSpan(sub, dy=[em(NodePos.descender_margin, options)],
                                style=options.style_str(size_only=True, scale=scale))
    text_width = options.label_width(text)
    width = text_width + options.label_width(sub) * scale
    # height: simply use 1em. The node margin already factors in enought space
    # for a descender, and may be further adjusted below.
    height = 1.0
    text_parent.add(span1)
    text_parent.add(span2)
    svg_parent.add(text_parent)
    n = NodePos(svg_parent, x=50, y=0, width=width, height=height, options=options, text=f"{text}_{{{sub}}}")
    # using a constant node height here doesn't look good for many cases: we
    # want to adjust depending on how the subscript is positioned in the x
    # dimension, which will tweak where the edge starts from. The basic issue
    # is that enough height to allow for a subscript + descender looks bad
    # if the subscript is not anywhere near the edge.
    #
    # So, if the midpoint of the node would fall in the subscript, add a bit of
    # extra y height to the margin to compensate, on top of the default margin.
    # Using the margin (instead of height) keeps nodes aligned.
    #
    # Both 0.2 and 0.05 here are fairly heuristic. In general, 0.2 puts a
    # subscript descender *just* above the lower edge of the node
    if width / 2 > text_width - 0.05:
        n.descender_margin += 0.2
    return n


class NodePos(object):
    # in ems. (XX not ideal to hardcode)
    descender_margin = 0.25 # Tree-internal margin for descenders
    annotation_margin = 0.25 # margin at the lower edge -- used for tree annotation positioning
    def __init__(self, svg, x=0, y=0, width=0, height=0, options=None, depth=0, text=None):
        self.x = x
        self.y = y
        self.set_dimensions(width=width, height=height)
        self.depth = depth
        self.svg = svg
        if text is None:
            text = svg
        self.text = text
        if options is None:
            options = TreeOptions()
        else:
            options = options.copy()
        self.options = options
        self.clear_edge_styles()

    def set_dimensions(self, width=None, height=None):
        if width is not None:
            self.orig_width = max(width, 1) # avoid divide by 0 errors
        if height is not None:
            self.orig_height = height
        self.reset_calcs()

    def reset_calcs(self):
        self.width = self.orig_width
        self.inner_width = self.width
        self.height = self.orig_height
        self.inner_height = self.height
        # depth?

    def set_edge_style(self, daughter, style):
        self.edge_styles[daughter] = style

    def get_edge_style(self, daughter):
        return self.edge_styles.get(daughter, None)

    def has_edge_style(self, daughter):
        return daughter in self.edge_styles

    def clear_edge_styles(self):
        self.edge_styles = dict() # no info about surrounding tree structure...

    def margin(self, full=False):
        r = 0.0
        if self.height > 0:
            r += self.descender_margin
        if full:
            r += self.annotation_margin
        return r

    def em_height(self, margin=False, full=False):
        r = self.height
        if margin:
            r += self.margin(full=full)
        return r

    def get_svg(self, options=None):
        # TODO: generalize this / make it less hacky
        # the options arg is because we need to set this relative to the
        # containing tree's global font size...
        if options is None:
            options = self.options
        self.svg["y"] = em(self.y, options)
        return self.svg

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"NodePos({repr(self.text)})"

    def _repr_svg_(self):
        # this is basically a mock svg frame for debugging; it is simplified
        # from svg_build_tree + _svg_add_subtree. Some code dup.
        width = self.options.em_to_px(self.width)
        height = self.options.em_to_px(self.em_height(margin=True, full=True))
        tree = svgwrite.Drawing(self.text,
            (px(width), px(height)),
            style=self.options.style_str())
        tree.viewbox(minx=0, miny=0, width=width, height=height)
        tree.fit()
        tree.add(self.get_svg())
        return tree.tostring()


    @classmethod
    def in_context(cls, n, depth, options):
        """
        Given a node object of some kind, finalize it in its tree context with
        the provided `depth` and `options`.

        Parameters
        ----------
        n : Union[NodePos, DeferredNodePos, str]
            A node representation. If this is a `DeferredNodePos`, it is
            finalized to a `NodePos` with the provided options. If it is a
            `NodePos`, its derived sizing is reset, but otherwise it is left
            unchanged. If `n` is `str` (intended for debugging purposes), it
            is parsed using the module default node builder and finalized.

        depth : int
            The tree depth at which this node appears

        options : TreeOptions
            The options from the tree context.

        Returns
        -------
        NodePos
            A finalized `NodePos` object that is ready for rendering.
        """
        if isinstance(n, NodePos):
            # this is allowed, but non-ideal -- prefer using DeferredNodePos
            # so that options work correctly.
            result = n
            result.reset_calcs()
        elif isinstance(n, DeferredNodePos):
            # finalize the label with the current options argument
            result = n(options=options)
        else:
            # intended for debugging only
            # otherwise, call the default node builder with the current
            # options argument
            result = node(n)(options=options)

        result.depth = depth
        return result


    @classmethod
    def from_label(cls, label):
        """Given an arbitrary label, produce an SVG container object for
        that label.

        Parameters
        ----------
        label
            an element representing the node label. If this is an instance of
            `NodePos` or `DeferredNodePos` this is returned unchanged;
            otherwise it is passed to the default node builder as a string. The
            default node builder is `multiline_node`, which parses strings with
            newlines into centered rows of text in SVG format.

        Returns
        -------
        Union[NodePos, DeferredNodePos]
            A container object for a rendered SVG node. This is normally a
            `DeferredNodePos`.
        """
        if isinstance(label, ElementTree.Element):
            # explicit error message in case someone tries to mix svgling.core
            # with svgling.html
            raise ValueError(
                "`svgling.core` does not support ElementTree objects.")

        if isinstance(label, NodePos) or isinstance(label, DeferredNodePos):
            # already handled
            return label
        elif isinstance(label, collections.abc.Sequence):
            # this (by default) will error for all non-str Sequences
            return node(label)
        else:
            return node(str(label))


class EdgeStyle(object):
    def __init__(self, path=None, stroke="black", stroke_width=None):
        if path:
            path = tuple(path)
        self.path = path
        self.stroke = stroke
        self.stroke_width = stroke_width

    def __hash__(self):
        if (self.path is not None):
            return hash(self.path)
        else:
            return object.hash(self)

    def svg_opts(self):
        opts = dict({"stroke": self.stroke})
        if self.stroke_width:
            opts["stroke_width"] = self.stroke_width
        return opts

    def draw(self, svg_parent, tree_layout, parent, child):
        line_start = parent.y + parent.em_height(True)
        box_y = tree_layout.y_distance(parent.depth, child.depth)
        y_target = em(box_y + child.y, tree_layout.options)
        x_target = perc(child.x + child.width / 2)
        svg_parent.add(svgwrite.shapes.Line(
                            start=("50%", em(line_start, tree_layout.options)),
                            end=(x_target, y_target),
                            **self.svg_opts()))

class EmptyEdge(EdgeStyle):
    # set this for blanket changes. `leaf_edges=False` assumes this default
    # is 0.0. Set to `None` for the equiv of auto_distance=True.
    default_distance = 0.0

    def __init__(self, distance=None, auto_distance=False):
        if auto_distance:
            # awkward interface, but this option tells the renderer to use
            # the regular level distance
            distance = None
        elif distance is None:
            distance = self.default_distance
        self.distance = distance

    def draw(self, svg_parent, tree_layout, parent, child):
        pass

class IndirectDescent(EdgeStyle):
    def draw(self, svg_parent, tree_layout, parent, child):
        from svgwrite.shapes import Line
        if child.depth > parent.depth + 1:
            line_start = parent.y + parent.em_height(True)
            box_y = tree_layout.y_distance(parent.depth, child.depth)
            y_target = em(box_y + child.y, tree_layout.options)
            x_target = perc(child.x + child.width / 2)
            # we are skipping level(s). Find the y position that an empty
            # node on the next level would have.
            intermediate_y = em(tree_layout.label_y_dodge(level=parent.depth+1,
                                                          height=0)[0]
                        + tree_layout.y_distance(parent.depth, parent.depth+1),
                        tree_layout.options)
            # TODO: do as Path?
            svg_parent.add(Line(start=("50%", em(line_start, tree_layout.options)),
                                end=(x_target, intermediate_y),
                                **self.svg_opts()))
            svg_parent.add(Line(start=(x_target, intermediate_y),
                                end=(x_target, y_target),
                                **self.svg_opts()))
        else:
            EdgeStyle.draw(self, svg_parent, tree_layout, parent, child)

class TriangleEdge(EdgeStyle):
    def draw(self, svg_parent, tree_layout, parent, child):
        line_start = parent.y + parent.em_height(True)
        box_y = tree_layout.y_distance(parent.depth, child.depth)
        y_target = em(box_y + child.y, tree_layout.options)

        # difference from the midpoint. 0.8 is a heuristic to account for leaf
        # padding. Under normal font conditions, doesn't start to look off until
        # ~60 character widths.
        width_dodge = 0.8 * child.inner_width / 2.0
        x_target_l = perc(child.x + child.width / 2 - width_dodge)
        x_target_r = perc(child.x + child.width / 2 + width_dodge)
        svg_parent.add(svgwrite.shapes.Line(start=("50%", em(line_start, tree_layout.options)),
                                            end=(x_target_l, y_target),
                                            **self.svg_opts()))
        svg_parent.add(svgwrite.shapes.Line(start=("50%", em(line_start, tree_layout.options)),
                                            end=(x_target_r, y_target),
                                            **self.svg_opts()))
        svg_parent.add(svgwrite.shapes.Line(start=(x_target_l, y_target),
                                            end=(x_target_r, y_target),
                                            **self.svg_opts()))

class TreeLayout(object):
    """Container class for storing a tree layout state."""
    def __init__(self, t, options=None):
        if options is None:
            self.options = TreeOptions()
        else:
            self.options = options.copy()
        self.level_heights = dict()
        self.level_ys = dict({0: 0})
        self.max_width = 1
        self.extra_y = 0.5
        self.depth = 0
        # behavior of t is a tree: copy the structure and nothing else.
        # (Maybe more sensible to copy or merge options too?)
        if isinstance(t, TreeLayout):
            self.tree = t.tree
        else:
            self.tree = t
        self.annotations = list() # list of svgwrite objects
        self.layout = None
        self._do_layout(self.tree) # initializes self.layout

    def __str__(self):
        return str(self.tree)

    def __repr__(self):
        # TODO: options repr? Not really very important? This function is mostly
        # here so that raw object ids don't contribute to .ipynb diffs.
        return "TreeLayout(%s)" % repr(self.tree)

    def reset(self, options=None, **args):
        if options is None:
            options = TreeOptions(**args)
        return TreeLayout(self.tree, options=options)

    def relayout(self):
        self._do_layout(self.tree)
        # annotations were already drawn in svg relative to the old layout, so
        # they would need a complete redo
        self.annotations = []

    ######## Annotations

    def box_constituent(self, path, stroke="none", rounding=8,
                        stroke_width=1, fill="gray", fill_opacity=0.15):
        (x, y, width, height) = self.subtree_bounds(path)
        rect = svgwrite.shapes.Rect(insert=(perc(x), em(y, self.options)),
                                    size=(perc(width), em(height, self.options)),
                                    stroke=stroke,
                                    fill=fill,
                                    fill_opacity=fill_opacity,
                                    rx=rounding,
                                    ry=rounding,
                                    stroke_width=stroke_width)
        self.annotations.append(rect)
        return self

    def underline_constituent(self, path, stroke="black", stroke_width=1,
                              stroke_opacity=1.0):
        (x, y, width, height) = self.subtree_bounds(path)
        opts = {"stroke": stroke, "stroke_width": stroke_width,
                "stroke_opacity": stroke_opacity}
        global crisp_perpendiculars
        if crisp_perpendiculars:
            opts["shape_rendering"] = "crispEdges"
        underline = svgwrite.shapes.Line(
                            start=(perc(x), em(y + height, self.options)),
                            end=(perc(x + width), em(y + height, self.options)),
                            **opts)

        self.extra_y = max(self.extra_y, (y + height) + 0.5 - (self.em_height() - self.extra_y))
        self.annotations.append(underline)
        return self

    def _movement_find_y(self, x1, x2, y):
        # try to keep movement arrows from obscuring each other; a bit hacky
        try:
            self._movement_arrows
        except:
            self._movement_arrows = list()
        for existing_x1, existing_x2, existing_y in self._movement_arrows:
            if math.isclose(y, existing_y) and (x1 < existing_x2 or x2 > existing_x1):
                return self._movement_find_y(x1, x2, y + 0.5)
        self._movement_arrows.append((x1, x2, y))
        return y

    def deepest_intervening_leaf(self, path1, path2):
        """Find the deepest leaf node between nodes characterized by two paths.
        """
        return max([n.depth for n in self.leaf_span_iter(path1, path2)])

    def movement_arrow(self, path1, path2, stroke="black", stroke_width=1):
        width = self.width()
        n1_pos = self.subtree_bounds_user(path1)
        n2_pos = self.subtree_bounds_user(path2)
        n1_y = n1_pos[1] + n1_pos[3]
        n1_x = n1_pos[0] + n1_pos[2] / 2
        n2_y = n2_pos[1] + n2_pos[3]
        n2_x = n2_pos[0] + n2_pos[2] / 2

        y_depth = self.deepest_intervening_leaf(path1, path2) # ems
        # first calculate the baseline of the deepest intervening leaf (which
        # could be n1, n2, or some other node). Then find a position that is at
        # least 1.5em below that baseline that will (uniquely) hold the
        # horizontal part of the movement line. Then ensure that the canvas
        # will have at least space for that line + 0.5em.
        y_target_base = (self.y_distance(0, y_depth)
                         + self.level_heights[y_depth])
        y_target = self._movement_find_y(min(n1_x, n2_x),
                        max(n1_x, n2_x), y_target_base + 1.5)
        self.extra_y = max(self.extra_y, y_target - y_target_base + 0.5)

        # convert out of ems now
        y_target = self.options.em_to_px(y_target)

        opts = {"stroke": stroke, "fill": "none"}
        if stroke_width is not None:
            opts["stroke_width"] = stroke_width
        global crisp_perpendiculars
        if crisp_perpendiculars:
            opts["shape_rendering"] = "crispEdges"
        arrow_y_delta = self.options.em_to_px(0.45)

        self.annotations.append(svgwrite.shapes.Polyline(
            [(n1_x, n1_y), (n1_x, y_target), (n2_x, y_target),
            (n2_x, n2_y+arrow_y_delta)],
            **opts))

        #TODO markers for arrowheads? these arrowheads are a bit dumb
        opts = {"fill": stroke, "stroke": "none"}
        # if crisp_perpendiculars:
        #     opts["shape_rendering"] = "crispEdges"
        self.annotations.append(svgwrite.shapes.Polyline(
            [(n2_x+3, n2_y+arrow_y_delta),
             (n2_x, n2_y),
             (n2_x-3, n2_y+arrow_y_delta)],
            **opts))
        return self

    ######## Layout information

    def em_height(self):
        return (sum([self.level_ys[l] for l in range(self.depth + 1)]) +
                self.level_heights[self.depth] +
                self.extra_y)

    def em_width(self):
        return self.max_width

    def height(self):
        return self.options.em_to_px(self.em_height())

    def width(self):
        return self.options.em_to_px(self.em_width())

    def label_y_dodge(self, node=None, level=None, height=None):
        """Calculate the y positions of a label, relative to other labels in the
        same row. Returns a tuple of the top dodge, and the bottom dodge, as
        positive numbers."""
        if node is None:
            # dummy node to get default values...caller should supply either
            # node or level, otherwise we'll get the calculation wrong
            node = NodePos(None, options=self.options)
        if level is None:
            level = node.depth
        if height is None:
            # height = node.height * node.options.font_size / self.options.font_size
            height = node.height
        if self.options.vert_align == VertAlign.TOP:
            return (0, self.level_heights[level] - height)
        elif self.options.vert_align == VertAlign.BOTTOM:
            return (self.level_heights[level] - height, 0)
        elif self.options.vert_align == VertAlign.CENTER:
            dodge = (self.level_heights[level] - height) / 2.0
            return (dodge, dodge)
        else:
            return (0,0)

    def y_distance(self, level_a, level_b):
        """What is the total y distance between levels a and b, starting from
        the containing svg for level_a?"""
        # level_ys is a dict, so can't use slicing
        level_b = min(self.depth, level_b)
        return sum([self.level_ys[l] for l in range(level_a + 1, level_b + 1)])

    def layout_iter(self, path):
        """An iterator over every position in a path, where the head is
        at the root node, and any children follow. Will throw AttributeError on an
        invalid path at the point in iteration where the path is invalid. (If
        you want to validate a path, you can do this by converting to a list.)
        """
        node = self.layout
        yield node
        i = 0
        for c in path:
            parent, children = node[0], node[1:]
            try:
                node = children[c]
            except IndexError:
                raise AttributeError(
                    "Invalid tree path at index %d (daughter %d)" % (i, c))
            yield node
            i += 1

    def node_iter(self, path):
        """An iterator over every node in a path. Will throw AttributeError
        on an invalid path at the point in iteration where the path is invalid.
        """
        for n in self.layout_iter(path):
            yield n[0]

    def subtree_iter(self, path):
        """Iterate over every layout position starting at the indicated path.
        Goes depth-first, left-right."""
        root = self.sublayout(path)
        def df(pos):
            yield pos
            for c in pos[1:]:
                yield from df(c)
        return df(root)

    def leaf_iter(self, t):
        return leaf_iter(t, split=self.options.split)

    def leaf_span_iter(self, path1, path2):
        """Iterate over a potentially non-constituent sequences of leaves
        delimited by path1 and path2. Includes any leaves under the paths, and
        so therefore will be non-empty (if the tree is non-empty). The paths
        may be in either order, but the iteration will always be left-to-right.
        """
        branch = common_parent(path1, path2)
        # the complication comes in here because the path bounds might not
        # specify a constituent (in fact they typically won't unless they are
        # equal).
        constituent_leaves = list(self.leaf_iter(self.sublayout(branch)))
        path1_leaves = list(self.leaf_iter(self.sublayout(path1)))
        path2_leaves = list(self.leaf_iter(self.sublayout(path2)))
        for i in range(len(constituent_leaves)):
            if constituent_leaves[i] == path1_leaves[0]:
                path1_i = i
            if constituent_leaves[i] == path2_leaves[0]:
                path2_i = i
        if path1_i < path2_i:
            left = path1_i
            right = path2_i + len(path2_leaves)
        else:
            left = path2_i
            right = path1_i + len(path1_leaves)
        return iter(constituent_leaves[left:right])

    def sublayout(self, path):
        """Find the position in the layout given by a tree path, i.e. a sequence
        of daughter indices (indexed from 0). Will throw AttributeError on an
        invalid path."""
        return list(self.layout_iter(path))[-1]

    def nmost_path(self, path, n):
        """Find the deepest path from starting position `path` that can be
        reached via daughter index n repeatedly."""
        path = list(path)
        t = self.sublayout(path)
        parent, children = t[0], t[1:]
        i = len(path)
        while i < self.depth + 1:
            try:
                parent, children = children[n][0], children[n][1:]
                path = path + [n]
            except IndexError:
                break
        return path

    def leftmost_path(self, path=()):
        """Find the deepest path starting position `path` that can be
        found by going left repeatedly."""
        return self.nmost_path(path, 0)

    def rightmost_path(self, path=()):
        """Find the deepest path starting position `path` that can be
        found by going right repeatedly."""
        return self.nmost_path(path, -1)

    def node_x_vals(self, path):
        """Find, relative to the outer svg, the x position and width for node
        at position `path`. Both values are in percentages."""
        left = 0.0
        width = 100.0
        i = 0
        for node in self.node_iter(path):
            left += node.x * width / 100.0
            width = width * node.width / 100.0
        return left, width

    def subtree_bounds(self, path):
        """Find the bounding box for a subtree whose parent is at position
        `path`, in the format of a tuple (x, y, width, height). X values are
        in percentages, and Y values are in ems. The values are relative to the
        outermost svg."""
        parent = self.sublayout(path)
        deepest = max([l.depth for l in self.leaf_iter(parent)])
        left_path = self.leftmost_path(path)
        right_path = self.rightmost_path(path)
        x = self.node_x_vals(left_path)[0]
        width = sum(self.node_x_vals(right_path)) - x
        y = self.y_distance(0, parent[0].depth)
        height = (self.y_distance(parent[0].depth, deepest)
                  + self.level_heights[deepest]
                  # XX this should check all leaf nodes, rather than using
                  # the static values...
                  + NodePos.descender_margin + NodePos.annotation_margin)
        return (x, y, width, height)

    def subtree_bounds_user(self, path):
        """Find the bounding box for a subtree whose parent is at position
        `path`, in the format of a tuple (x, y, width, height). All values
        are in user units relative to the outermost svg."""
        (x, y, width, height) = self.subtree_bounds(path)
        tree_width = self.width()
        x = x * tree_width / 100.0
        width = width * tree_width / 100.0
        y = self.options.em_to_px(y)
        height = self.options.em_to_px(height)
        return (x, y, width, height)


    ########### Layout stuff, mostly internal

    def set_edge_style(self, path, style):
        if len(path) == 0: # there are no edges to the top node
            return
        path_to_parent = path[:-1]
        # we use tree_split to traverse an already constructed tree; at this
        # point, all nodes and leafs are regularized NodePos objects so there's
        # no need to use options.split. The point of this is just to extract
        # the parent node for the relevant path.
        parent, children = tree_split(self.sublayout(path_to_parent))
        daughter = path[-1]
        if daughter >= len(children):
            raise AttributeError("Invalid daughter index %d" % daughter)
        daughter = daughter % len(children) # handle negative indices
        parent.set_edge_style(daughter, style)
        return self

    def set_subtree_style(self, path, **opts):
        allowed = ["debug", "font_style", "font_size", "text_color", "text_stroke"]
        # Maybe: disallow font_size if relative_units = True?
        if any(k not in allowed for k in opts.keys()):
            raise TypeError(f"Allowed subtree option keys: {', '.join(allowed)}")
        for pos in self.subtree_iter(path):
            pos[0].options.update(**opts)
        self.relayout()
        return self

    def set_leaf_style(self, **opts):
        allowed = ["debug", "font_style", "font_size", "text_color", "text_stroke"]
        # Maybe: disallow font_size if relative_units = True?
        if any(k not in allowed for k in opts.keys()):
            raise TypeError(f"Allowed subtree option keys: {', '.join(allowed)}")
        for l in self.leaf_iter(self.layout):
            l.options.update(**opts)
        self.relayout()
        return self

    def set_node_style(self, path, **opts):
        allowed = ["debug", "font_style", "font_size", "text_color", "text_stroke"]
        # Maybe: disallow font_size if relative_units = True?
        if any(k not in allowed for k in opts.keys()):
            raise TypeError(f"Allowed node option keys: {', '.join(allowed)}")
        self.sublayout(path)[0].options.update(**opts)
        self.relayout()
        return self

    def clear_edge_styles(self):
        for n in self.node_iter():
            n.clear_edge_styles()
        return self

    def _do_layout(self, t):
        self.level_heights = dict()
        self.level_ys = dict({0: 0})
        self.depth =  tree_depth(t, split=self.options.split) - 1
        for i in range(self.depth + 1):
            self.level_heights[i] = 0
        parsed = self._build_initial_layout(t, self.layout)
        self._calc_level_ys()
        if len(parsed) > 0:
            self.max_width = parsed[0].width
        else:
            self.max_width = 0
        if len(parsed) > 0: # normalize_widths doesn't affect parents
            parsed[0].width = 100.0
            parsed[0].x = 0
        self._normalize_widths(parsed)
        self._normalize_y(parsed)
        self.layout = parsed

    def _build_initial_layout(self, t, old_layout=None, level=0):
        # initialize raw widths and node heights, both in em at this point.
        # also initialize level_heights for all levels, and depth values for
        # nodes.
        parent, children = self.options.split(t)
        if old_layout:
            node_options = old_layout[0].options
            old_child_layout = old_layout[1:]
        else:
            node_options = self.options
            # dummy values
            old_child_layout = [None] * len(children)

        # if leaf nodes align, all leaf nodes contribute to height for the
        # deepest level, not their actual depth
        if len(children) == 0 and self.options.leaf_nodes_align:
            level = self.depth
        node = NodePos.in_context(parent, depth=level, options=node_options)
        # n.b. this doesn't fully make sense if a custom node overrides the
        # font size...
        node.height = node.height * node.options.font_size / self.options.font_size

        real_node_height = node.height
        # real_node_height = real_node_height * node_options.font_size / self.options.font_size

        self.level_heights[level] = max(self.level_heights[level], real_node_height)
        result_children = [self._build_initial_layout(
                                    children[i], old_child_layout[i], level+1)
                            for i in range(len(children))]

        # take into account any font size tweaks on a particular node label
        node.width = max(
            node.width * node.options.font_size / self.options.font_size,
            sum([c[0].width for c in result_children]))
        return [node] + result_children

    def _sublayout_width(self, t):
        if t[0].options.horiz_spacing == HorizOptions.TEXT:
            return t[0].width # precalculated
        elif t[0].options.horiz_spacing == HorizOptions.NODES:
            return leaf_nodecount(t, t[0].options)
        else: # EVEN
            return 1

    def _normalize_widths(self, t):
        # normalize tree widths to percentages in the appropriate way.
        parent, children = t[0], t[1:]
        if len(children) == 0:
            return
        # recurse first, so that parent widths are still in ems
        for c in children:
            self._normalize_widths(c)

        widths = list()
        sub_sum = 0
        em_sum = 0
        # calculate widths according to scheme determined by options. This
        # may or may not be in real units.
        for c in children:
            widths.append(self._sublayout_width(c))
            sub_sum += widths[-1]
            em_sum += c[0].width

        # if the parent node is wider than all the children, the parent box is
        # what will determine the overall box size. The limiting case of this
        # is when each is one node.
        if em_sum < parent.inner_width:
            em_sum = parent.inner_width
        # normalize to percentages
        x_pos = 0
        for i in range(len(widths)):
            # TODO: inner width is not very accurate for non-TEXT width schemes.
            # Could calculate it relative to the entire canvas? Could I just
            # switch to viewbox-determined units rather than percentages?
            children[i][0].inner_width = children[i][0].inner_width * 100.0 / em_sum
            children[i][0].width = widths[i] * 100.0 / sub_sum
            children[i][0].x = x_pos
            x_pos += children[i][0].width

    def _calc_level_ys(self):
        # Calculate the y position of each row, relative to containing svg
        self.level_ys[0] = 0
        for i in range(1, self.depth + 1):
            self.level_ys[i] = (self.options.distance_to_daughter
                                + self.level_heights[i - 1])

    def _normalize_y(self, t):
        # calculate y distances for each level. This is done on a second pass
        # because it needs level_heights to be initialized.
        parent, children = t[0], t[1:]
        if (self.options.vert_align == VertAlign.FULL):
            parent.height = self.level_heights[parent.depth]
        parent.y = self.label_y_dodge(node=parent)[0]
        for c in children:
            self._normalize_y(c)

    ######### SVG building

    def _svg_add_subtree(self, svg_parent, t):
        # This uses several tricks to simulate the ways in which relative
        # positioning in raw SVG is hard:
        # 1. For x, use percentage-based positioning relative to nested `svg`
        #    elements. Every subtree has its own `<svg />` container, and the
        #    parent node is at `(50%, 1em)` relative to that container. There
        #.   are also some (simple) heuristics for estimating text width.
        # 2. Do all y positioning in `em`s. This is because it is impossible 
        #    to accurately get text sizes ahead of time (without somehow
        #    doing or simulating rendering) when generating SVG. So since `em`s
        #    ought to be relative to text size, only use that.
        from svgwrite.shapes import Line
        parent, children = t[0], t[1:]
        svg_parent.add(parent.get_svg(self.options))
        i = 0
        for c in children:
            if not self.options.leaf_edges and is_leaf(c):
                edge = EmptyEdge()
                if edge.distance is not None and c[0].depth - parent.depth > 0:
                    # multi-level descent; we probably have `leaf_nodes_align`
                    # set. One option might be to error, but this implements
                    # a behavior where the leaf row is aligned immediately
                    # below the prior level.
                    edge.distance += self.y_distance(parent.depth, c[0].depth - 1)
            elif parent.has_edge_style(i):
                edge = parent.get_edge_style(i)
            elif parent.options.descend_direct:
                edge = EdgeStyle()
            else:
                edge = IndirectDescent()

            if isinstance(edge, EmptyEdge) and edge.distance is not None:
                # XX near code dup width edge rendering code
                box_y = edge.distance + parent.y + parent.em_height(margin=False)
            else:
                box_y = self.y_distance(parent.depth, c[0].depth)

            child = svgwrite.container.SVG(x=perc(c[0].x),
                                           y=em(box_y, self.options),
                                           width=perc(c[0].width))
            style = c[0].options.style_str()
            if style != parent.options.style_str():
                child['style'] = style

            if parent.options.debug or c[0].options.debug:
                # XX: for very unclear reasons, the lower edge of these rects
                # are drawn out of frame. 100% in the y dimension must not
                # mean what I think, but why?
                child.add(svgwrite.shapes.Rect(insert=("0%","0%"),
                                               size=("100%", "100%"),
                                               fill="none", stroke="red"))

            svg_parent.add(child)

            edge.draw(svg_parent, self, parent, c[0])

            self._svg_add_subtree(child, c)
            i += 1

    def svg_build_tree(self, name="tree"):
        """Build an `svgwrite.Drawing` object based on the layout calculated
        when initializing the object."""

        # estimate canvas size based on depth + leaf widths. This probably isn't
        # very accurate in some limiting cases...but to do any better would need
        # either some way of simulating text rendering (inkscape?) or javascript
        # code that adjusts the tree spacing dynamically after the initial
        # rendering. Here we try to do as well as possible with pure python =>
        # SVG.
        width = self.width()
        height = self.height()

        if self.layout:
            style = self.layout[0].options.style_str()
        else:
            style = self.options.style_str() # fallback, shouldn't matter much

        tree = svgwrite.Drawing(name, (px(width), px(height)), style=style)
        tree.viewbox(minx=0, miny=0, width=width, height=height)
        tree.fit()

        if self.options.debug:
            tree.add(tree.rect(insert=(0,0), size=("100%", "100%"),
                fill="none", stroke="lightgray"))
            for i in range(1, int(self.em_width())):
                tree.add(tree.line(start=(em(i, self.options), 0),
                                   end=(em(i, self.options), "100%"),
                                   stroke="lightgray"))
            for i in range(1, int(self.em_height())):
                tree.add(tree.line(start=(0, em(i, self.options)),
                                   end=("100%", em(i, self.options)),
                                   stroke="lightgray"))

        self._svg_add_subtree(tree, self.layout)

        for a in self.annotations:
            tree.add(a)
        return tree

    def saveas(self, filename, pretty=False, indent=2):
        return self.get_svg().saveas(filename, pretty=pretty, indent=indent)

    def get_svg(self):
        tree = self.svg_build_tree()
        for a in self.annotations:
            tree.add(a)
        return tree

    def _repr_svg_(self):
        return self.get_svg().tostring()

################
# Module-level api
################

default_options = TreeOptions()
nltk_tree_options = default_options # backwards compatibility
def reset_defaults(options=None, **opts):
    if options is None:
        options = TreeOptions(**opts)
    global default_options, nltk_tree_options
    default_options = options
    nltk_tree_options = default_options


def draw_tree(*t, options=None, **opts):
    """Return an object that implements SVG tree rendering. These objects
    auto-display in a Jupyter notebook via `_repr_svg_()`. For non-IPython
    use, see `tree2svg`."""
    if options is None:
        if opts:
            options = TreeOptions(**opts)
        else:
            global default_options
            options = default_options
    if len(t) == 1:
        t = t[0]
    # If `t` is already a tree, this is equivalent to calling `reset` on that
    # tree with the provided options
    return TreeLayout(t, options=options)

def tree2svg(*t, options=None, **opts):
    """Convert a tree `t` into SVG output. If `t` is an already rendered tree,
    and no options are provided, get that tree's SVG."""

    # special case: if *just* a TreeLayout is provided, give that layout's SVG
    # back. If any options are provided, this will rerender.
    if len(t) == 1 and isinstance(t[0], TreeLayout) and options is None and len(opts) == 0:
        return t[0]._repr_svg_()
    return draw_tree(*t, options=options, **opts)._repr_svg_()

# no longer needed for current nltk, but here for backwards compatibility
def monkeypatch_nltk():
    """
    On older versions of nltk, this lets you add an svg-based renderer to
    Tree objects.

    This is not needed on current versions of nltk, which automatically load
    svgling if it's available.
    """
    import nltk
    global default_options
    nltk.Tree._repr_svg_ = lambda self: TreeLayout(self, options=default_options)._repr_svg_()

def disable_nltk_png():
    """
    When nltk's PNG renderer still existed, SVG would take priority, but Jupyter
    would typically call both renderers. This could have annoying consequences
    because of the dependency on tk, for example in headless setups. This
    backwards-compatibility convenience function completely disables the
    png-drawing code in nltk. If it fails (either because nltk isn't installed,
    or the relevant function has already been deleted) it will fail silently.

    This is not needed on current versions of nltk.
    """
    try:
        import nltk
        del nltk.tree.Tree._repr_png_
    except:
        pass
