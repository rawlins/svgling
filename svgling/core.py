import svgwrite
import enum

################
# Tree utility functions
################

def treelet_split_str(t):
    # treat strings as leaf nodes.
    if isinstance(t, str):
        return (t, tuple())
    else:
        return None

def treelet_split_nltk(t):
    # nltk.Tree API: the parent is in label(). The children are elements of the
    # object itself, which inherits from list.
    try:
        h = t.label()
        return (h, list(t))
    except:
        return None

def treelet_split_list(t):
    # treat a list as a lisp-like tree structure, i.e. each subtree is a list
    # of the parent followed by any children.
    # A 0-length list is treated as an empty leaf node.
    try:
        if (len(t) == 0):
            return ("", tuple())
        else:
            return (t[0], t[1:])
    except:
        return None

def treelet_split_fallback(t):
    # fallback to str(). TODO: enhance, or remove?
    return (str(t), tuple())

def tree_split(t):
    """Splits `t` into a parent and an iterable of children, possibly empty."""
    split = treelet_split_str(t)
    if split is not None:
        return split
    split = treelet_split_nltk(t)
    if split is not None:
        return split
    split = treelet_split_list(t)
    if split is not None:
        return split
    return treelet_split_fallback(t)   

def tree_cxr(t, i):
    return tree_split(t)[i]

def tree_car(t):
    """What is the parent of a tree-like object `t`?
    Try to adapt to various possibilities, including nltk.Tree."""
    return tree_cxr(t, 0)

def tree_cdr(t):
    """What are the children of a tree-like object `t`?
    Try to adapt to various possibilities, including nltk.Tree."""
    return tree_cxr(t, 1)

################
# Tree size estimation and options
################

# either EVEN or NODES usually looks best with abstract trees; TEXT usually
# looks the best for trees with real node labels, and so it is the default.
class HorizOptions(enum.Enum):
    TEXT = 0
    EVEN = 1
    NODES = 2

def em(n):
    return "%gem" % n

def perc(n):
    return "%g%%" % n

class TreeOptions(object):
    def __init__(self, horiz_spacing=HorizOptions.TEXT,
                       leaf_padding=2,
                       distance_to_daughter=3,
                       debug=False,
                       leaf_nodes_align=False,
                       global_font_style="font-family: times, serif; font-weight:normal; font-style: normal;",
                       average_glyph_width=2.0):
        self.horiz_spacing = horiz_spacing
        self.leaf_padding = leaf_padding
        self.distance_to_daughter = distance_to_daughter
        self.debug = debug
        self.leaf_nodes_align = leaf_nodes_align
        self.global_font_style = global_font_style
        # 2.0 default value is a heuristic -- roughly, 2 chars per em
        self.average_glyph_width = average_glyph_width 

        # not technically an option, but convenient to store here for now...
        self.max_depth = 0


    def label_width(self, label):
        return (len(str(label)) + self.leaf_padding) / self.average_glyph_width

def is_leaf(t):
    return len(tree_cdr(t)) == 0

def tree_depth(t):
    """What is the max depth of t?"""
    # n.b. car is always length 1 the way trees are currently parsed
    subdepth = 0
    for subtree in tree_cdr(t):
        subdepth = max(subdepth, tree_depth(subtree))
    return subdepth + 1

def subtree_textwidth(t, options=None):
    """How many ems wide are all the leafs? Will add padding."""
    if options is None:
        options=TreeOptions()
    parent, children = tree_split(t)
    if len(children) == 0:
        return options.label_width(parent)
    subwidth = 0
    for subtree in children:
        subwidth += subtree_textwidth(subtree, options)
    # don't make the width either smaller than the label, or smaller than 1em
    return max(subwidth, options.label_width(parent), 1)

def leaf_nodecount(t, options=None):
    """How many nodes wide are all the leafs? Will add padding."""
    if options is None:
        options=TreeOptions()
    parent, children = tree_split(t)
    if len(children) == 0:
        return 1 + options.leaf_padding
    subwidth = 0
    for subtree in children:
        subwidth += leaf_nodecount(subtree, options)
    return subwidth

def subtree_proportions(l, options):
    if (options.horiz_spacing == HorizOptions.EVEN):
        return [100.0 / len(l)] * len(l)
    else: # TEXT or NODES
        widths = list()
        sum = 0
        for t in l:
            if options.horiz_spacing == HorizOptions.TEXT:
                widths.append(subtree_textwidth(t, options))
            else: # NODES
                widths.append(leaf_nodecount(t, options))
            sum += widths[-1]

        # normalize to percentages
        for i in range(len(widths)):
            widths[i] = widths[i] * 100.0 / sum
        return widths

################
# SVG generation
################

def svg_add_subtree(svg_parent, t, options=None, cur_depth=0):
    # This uses two tricks to simulate the ways in which relative positioning
    # in raw SVG is hard:
    # 1. For x, it uses percentage-based positioning relative to nested `svg`
    #    elements. Every subtree has its own `<svg />` container, and the
    #    parent node is at `(50%, 1em)` relative to that container.
    # 2. It does all y positioning in `em`s. This is because it is
    #    impossible to accurately get text sizes ahead of time (without somehow
    #    doing or simulating rendering) when generating SVG. So since `em`s
    #    ought to be relative to text size, only use that.
    #
    # These tricks place some noticeable limitations on how much further the
    # pure python + svg part of this can be taken, for example, what to do with
    # more complex node contents, what to do if you want to draw movement
    # arrows, etc. But this so far has worked surprisingly well.
    if (options is None):
        options = TreeOptions()
    if (options.max_depth == 0):
        options.max_depth = tree_depth(t)
    parent, children = tree_split(t)
    parent = str(parent)
    if len(parent) > 0:
        line_start = "1.2em"
        svg_parent.add(svgwrite.text.Text(parent, insert=("50%", em(1)),
                                              text_anchor="middle"))
    else:
        line_start = "0em"
    if (len(children) > 0):
        x_pos = 0
        x_widths = subtree_proportions(children, options=options)
        for i in range(len(children)):
            if is_leaf(children[i]) and options.leaf_nodes_align:
                # Find a position for the daughter svg that lines up with the
                # deepest leaf nodes, relative to the current depth.
                daughter_height = ((options.max_depth - cur_depth - 1) *
                                        options.distance_to_daughter)
            else:
                daughter_height = options.distance_to_daughter
            child = svgwrite.container.SVG(x=perc(x_pos),
                                           y=em(daughter_height),
                                           width=perc(x_widths[i]))
            if options.debug:
                child.add(svgwrite.shapes.Rect(insert=("0%","0%"),
                                               size=("100%", "100%"),
                                               fill="none", stroke="red"))
            svg_parent.add(child)

            svg_parent.add(svgwrite.shapes.Line(start=("50%", line_start),
                                                end=(perc(x_pos + x_widths[i] / 2),
                                                     em(daughter_height)),
                                                stroke="black"))
            svg_add_subtree(child, children[i], options=options,
                                                cur_depth=cur_depth + 1)
            x_pos += x_widths[i]

def svg_build_tree(t, name="tree", options=None):
    """Build an `svgwrite.Drawing` objets based on a tree-structured object
    `t`. Will handle various structures for `t`, including nltk.Tree and
    lisp-style lists of lists/strings."""

    # estimate canvas size based on depth + leaf widths. This probably isn't
    # very accurate in some limiting cases...but to do any better would need
    # either some way of simulating text rendering (inkscape?) or javascript
    # code that adjusts the tree spacing dynamically after the initial
    # rendering. Here we try to do as good as possible with pure python => SVG.

    if options is None:
        options = TreeOptions()
    options.max_depth = tree_depth(t)
    height = ((options.max_depth - 1) *
              options.distance_to_daughter + 2) # 1 extra em for descenders
    width = subtree_textwidth(t, options)
    tree = svgwrite.Drawing(name, (em(width), em(height)),
        style=options.global_font_style)
    if (options.debug):
        tree.add(tree.rect(insert=(0,0), size=("100%", "100%"),
            fill="none", stroke="lightgray"))
        for i in range(1, int(width)):
            tree.add(tree.line(start=(em(i), 0),
                               end=(em(i), "100%"),
                               stroke="lightgray"))
        for i in range(1, int(height)):
            tree.add(tree.line(start=(0, em(i)),
                               end=("100%", em(i)),
                               stroke="lightgray"))
    svg_add_subtree(tree, t, options=options)
    return tree

def draw_tree(*t, options=None):
    """Return an svg tree object wrapped in an IPython SVG object, for display
    in a Jupyter notebook."""
    from IPython.core.display import SVG
    if options is None:
        options = TreeOptions(debug=False)
    if len(t) == 1:
        t = t[0]
    tree = svg_build_tree(t, options=options)

    return SVG(tree.tostring())

nltk_tree_options = TreeOptions()

def monkeypatch_nltk():
    import nltk
    global nltk_tree_options
    nltk.Tree._repr_svg_ = lambda self: svg_build_tree(self, options=nltk_tree_options).tostring()

def module_setup():
    try:
        monkeypatch_nltk()
    except:
        pass

module_setup()

