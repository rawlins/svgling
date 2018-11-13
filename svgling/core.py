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

class NodePos(object):
    def __init__(self, svg, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.inner_width = width
        self.height = height
        self.inner_height = height
        self.svg = svg

    @classmethod
    def from_label(cls, label, options):
        y = 1
        svg_parent = svgwrite.container.SVG(x=0, y=0, width="100%")
        if len(label) == 0:
            return NodePos(svg_parent, 50, 0, 0, 0)
        for line in label.split("\n"):
            svg_parent.add(svgwrite.text.Text(line, insert=("50%", em(y)),
                                                    text_anchor="middle"))
            y += 1
        width = max([options.label_width(line) for line in label.split("\n")])
        return NodePos(svg_parent, 50, 0, width, y-1)

class TreeLayout(object):
    def __init__(self, t, options=None):
        if options is None:
            options = TreeOptions()
        self.level_heights = dict()
        self.level_ys = dict({0: 0})
        self.depth = 0
        self.options = options
        self._do_layout(t)

    def _do_layout(self, t):
        self.level_heights = dict()
        self.level_ys = dict({0: 0})
        self.depth =  tree_depth(t) - 1
        for i in range(self.depth + 1):
            self.level_heights[i] = 0
        parsed = self._build_initial_layout(t)
        if len(parsed) > 0:
            self.max_width = parsed[0].width
        else:
            self.max_width = 0
        self._normalize_widths(parsed)
        self._normalize_y(parsed)
        self._adjust_leaf_nodes(parsed)
        self.layout = parsed
        self.raw_tree = t

    def _build_initial_layout(self, t, level=0):
        # initialize raw widths and node heights, both in em at this point.
        # also initialize level_heights for all levels.
        parent, children = tree_split(t)
        node = NodePos.from_label(parent, self.options)

        # if leaf nodes align, all leaf nodes contribute to height for the
        # deepest level, not their actual depth
        if len(children) == 0 and self.options.leaf_nodes_align:
            level = self.depth
        self.level_heights[level] = max(self.level_heights[level], node.height)
        result_children = [self._build_initial_layout(c, level+1)
                                                            for c in children]
        node.width = max(node.width, sum([c[0].width for c in result_children]))
        return [node] + result_children

    def _subtree_proportions(self, l):
        if len(l) == 0:
            return list()
        if (self.options.horiz_spacing == HorizOptions.EVEN):
            return [100.0 / len(l)] * len(l)
        else: # TEXT or NODES
            widths = list()
            sum = 0
            for t in l:
                if self.options.horiz_spacing == HorizOptions.TEXT:
                    widths.append(t[0].width) # precalculated
                else: # NODES
                    widths.append(leaf_nodecount(t[0], self.options))
                sum += widths[-1]

            # normalize to percentages
            for i in range(len(widths)):
                widths[i] = widths[i] * 100.0 / sum
            return widths

    def _normalize_widths(self, t):
        # normalize widths to percentages.
        parent, children = t[0], t[1:]
        for c in children:
            self._normalize_widths(c)
        widths = self._subtree_proportions(children)
        for i in range(len(children)):
            children[i][0].width = widths[i]

    def _normalize_y(self, t, level=0):
        # calculate y distances for each level. This is done on a second pass
        # because it needs level_heights to be initialized.
        parent, children = t[0], t[1:]
        y_distance = (parent.height + 
                      self.options.distance_to_daughter +
                        (self.level_heights[level] - parent.height) / 2)
        if len(children) > 0 and (level + 1) not in self.level_ys:
            self.level_ys[level + 1] = self.options.distance_to_daughter + self.level_heights[level]
        for c in children:
            c[0].y = (y_distance +
                (self.level_heights[level + 1] - c[0].height) / 2)
            self._normalize_y(c, level + 1)

    def _adjust_leaf_nodes(self, t, level=0):
        # if leaf nodes align, move leaves down to match the lowest one. Done on
        # a third pass so that non-leaf ys are all established.
        if not self.options.leaf_nodes_align:
            return
        parent, children = t[0], t[1:]
        if len(children) == 0 and level > 0:
            parent.y = (parent.y
                - (self.level_heights[level] - parent.height) / 2
                + sum([self.level_ys[y] for y in range(level + 1, self.depth+1)])
                + (self.level_heights[self.depth] - parent.height) / 2)
        for c in children:
            self._adjust_leaf_nodes(c, level + 1)

    def _svg_add_subtree(self, svg_parent, t):
        parent, children = t[0], t[1:]
        if parent.height > 0:
            line_start = parent.height + 0.2
        else:
            line_start = 0
        x_pos = 0
        svg_parent.add(parent.svg)
        for c in children:
            child = svgwrite.container.SVG(x=perc(x_pos),
                                           y=em(c[0].y),
                                           width=perc(c[0].width))
            if self.options.debug:
                child.add(svgwrite.shapes.Rect(insert=("0%","0%"),
                                               size=("100%", "100%"),
                                               fill="none", stroke="red"))
            svg_parent.add(child)

            svg_parent.add(svgwrite.shapes.Line(start=("50%", em(line_start)),
                                                end=(perc(x_pos + c[0].width / 2),
                                                     em(c[0].y)),
                                                stroke="black"))
            self._svg_add_subtree(child, c)
            x_pos += c[0].width

    def height(self):
        return (sum([self.level_ys[l] for l in range(self.depth + 1)]) +
                self.level_heights[self.depth] +
                1)

    def _svg_build_tree(self, name="tree"):
        width = self.max_width
        height = self.height()
        tree = svgwrite.Drawing(name, (em(width), em(height)),
            style=self.options.global_font_style)
        if self.options.debug:
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
        self._svg_add_subtree(tree, self.layout)
        return tree

    def _repr_svg_(self):
        return self._svg_build_tree().tostring()

class TreeOptions(object):
    def __init__(self, horiz_spacing=HorizOptions.TEXT,
                       leaf_padding=2,
                       distance_to_daughter=2,
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

    def tree_height(self, t):
        """Calculate tree height, in ems. Takes into account multi-line leaf
        nodes."""
        # TODO: generalize to multi-line nodes of all kinds.
        parent, children = tree_split(t)
        if len(children) == 0:
            return len(parent.split("\n"))
        subheight = 0
        for subtree in children:
            subheight = max(subheight, self.tree_height(subtree))
        return subheight + self.distance_to_daughter + 1


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
        return max([options.label_width(line) for line in parent.split("\n")])
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

def svg_add_label(svg_parent, label, options):
    y = 1
    for line in label.split("\n"):
        svg_parent.add(svgwrite.text.Text(line, insert=("50%", em(y)),
                                                text_anchor="middle"))
        y += 1

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
    if options is None:
        options = TreeOptions()
    if options.max_depth == 0:
        options.max_depth = tree_depth(t)
    parent, children = tree_split(t)
    parent = str(parent)
    if len(children) > 0:
        parent = " ".join(parent.split("\n")) # hack to allow for multi-line
                                              # leaf nodes. Multi-line nodes in
                                              # general require more work, so
                                              # avoid rendering them for now.
    if len(parent) > 0:
        line_start = "1.2em"
        svg_add_label(svg_parent, parent, options)
    else:
        line_start = "0em"
    if len(children) > 0:
        x_pos = 0
        x_widths = subtree_proportions(children, options=options)
        for i in range(len(children)):
            if is_leaf(children[i]) and options.leaf_nodes_align:
                # Find a position for the daughter svg that lines up with the
                # deepest leaf nodes, relative to the current depth.
                daughter_height = ((options.max_depth - cur_depth - 1) *
                                        (options.distance_to_daughter + 1))
            else:
                daughter_height = options.distance_to_daughter + 1
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
    height = options.tree_height(t) + 1 # 1 extra em for descenders
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

def draw_tree_old(*t, options=None, **opts):
    """Return an svg tree object wrapped in an IPython SVG object, for display
    in a Jupyter notebook."""
    from IPython.core.display import SVG
    if options is None:
        options = TreeOptions(**opts)
    if len(t) == 1:
        t = t[0]
    tree = svg_build_tree(t, options=options)

    return SVG(tree.tostring())


def draw_tree(*t, options=None, **opts):
    """Return an svg tree object wrapped in an IPython SVG object, for display
    in a Jupyter notebook."""
    from IPython.core.display import SVG
    if options is None:
        options = TreeOptions(**opts)
    if len(t) == 1:
        t = t[0]
    return TreeLayout(t, options=options)

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

