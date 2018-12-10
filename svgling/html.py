import copy
from xml.etree import ElementTree
Element = ElementTree.Element
SubElement = ElementTree.SubElement

import svgwrite

import svgling.core
from svgling.core import TreeOptions, px

def html_split_fallback(t):
    return (to_html(t), tuple())

# override core version because we want to handle Elements specially, at least
# in principle. TODO: core just doesn't handle them at all.
def tree_split(t):
    if isinstance(t, ElementTree.Element):
        return (t, tuple())
    else:
        return svgling.core.tree_split(t, fallback=html_split_fallback)

def element_with_text(name, text="", **kwargs):
    e = Element(name, **kwargs)
    e.text = text
    return e

def subelement_with_text(parent, name, text="", **kwargs):
    e = Element(name, **kwargs)
    e.text = text
    parent.append(e)
    return e

def style_append(element, style):
    e_style = element.get("style", "").strip()
    if len(e_style) > 0 and e_style[-1] != ";":
        e_style = e_style + ";"
    element.set("style", e_style + style)

# this is based in a similar function in the lambda notebook display code, but
# the spacing here is customized for the needs of tree nodes.
def html_text_wrap(t, debug=False):
    """The idea is that this is a safe wrapper for putting a string into an
    html output somewhere. It's a bit convoluted, because of attempting to
    work around various things that produce bad line breaking in mathjax
    rendering."""
    if debug:
        border = "border: 1px solid #848482;"
    else:
        border = ""
    e = Element("div",
        style="display:inline-block;padding-left:0.75em;padding-right:0.75em;text-align:center;"
        # CommonHTML needs something like the following, but since it's buggy
        # on some browsers, and CommonHTML is not enabled on inter
        # + "width: -webkit-min-content;width: -moz-min-content;width: min-content;" # ugh
        + border)
    subelement_with_text(e, "span", text=t, style="text-align:center;")
    return e

def multiline_text(*lines, debug=False):
    if debug:
        border = "border: 1px solid #848482;"
    else:
        border = ""
    e = Element("div",
        style="display:grid;grid-template-columns:auto;")
    for l in lines:
        line_div = SubElement(e, "div",
            style="padding-left:0.75em;padding-right:0.75em;text-align:center;")
        subelement_with_text(line_div, "span", text=l)
    return e

# more code based on lambda notebook versions (next three functions).
def to_html(x, debug=False):
    if isinstance(x, str):
        return html_text_wrap(x, debug=debug)
    elif isinstance(x, Element):
        return x
    try:
        return ElementTree.fromstring(x._repr_html_())
    except:
        try:
            return html_text_wrap(x._repr_latex_())
        except:
            return html_text_wrap(repr(x))

def element_with_text(name, text="", **kwargs):
    e = Element(name, **kwargs)
    e.text = text
    return e

def subelement_with_text(parent, name, text="", **kwargs):
    e = Element(name, **kwargs)
    e.text = text
    parent.append(e)
    return e

def line_svg_raw(x_pos, x_pos2):
    """Produce an svg that consists of a single vertical(/diagonal) line, with
    x positions anchored to corners or centered. This is designed to be
    arbitrarily scaled.
    `x_pos`: the top x position
    `x_pos2`: the bottom x position
    For both of these arguments:
        `-1` gives the left edge
        `0` gives the center
        `1` gives the right edge.
    so, for example, -1,1 would give you a diagonal line angled to the right.
    """

    # this is not done with svgwrite because it doesn't allow applying both
    # style, and vector-effect at the same time.
    # display is set to block, because otherwise it will allow a bunch of extra
    # space below the svg, apparently because it is treating the svg bottom as
    # a baseline?
    svg = Element("svg", baseProfile="tiny", height="0", width="0",
        preserveAspectRatio="none", version="1.2", viewBox="0,0,100,100",
        xmlns="http://www.w3.org/2000/svg",
        style="height:100%;width:100%;display:block;")
    svg.set("xmlns:ev", "http://www.w3.org/2001/xml-events")
    svg.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    SubElement(svg, "defs")
    if x_pos < 0:
        start_x = 0
    elif x_pos > 0:
        start_x = 100
    else:
        start_x = 50
    if x_pos2 < 0:
        end_x = 0
    elif x_pos2 > 0:
        end_x = 100
    else:
        end_x = 50

    # back off from the top/bottom edges so that line ends are more likely to
    # be visible after stretching
    line = SubElement(svg, "line", stroke="black",
        x1=str(start_x), x2=str(end_x), y1="2", y2="98")
    line.set("stroke_width", "1px")
    line.set("vector-effect", "non-scaling-stroke")
    return svg

# there's no need to constantly rerun this, so precalculate all combos:
# TODO this is just a quick memoization hack, could be a lot more elegant
# however, it's not clear that this is really even necessary.
line_svg_memoized = {x1: {x2: line_svg_raw(x1,x2) for x2 in [-1,0,1]}
                         for x1 in [-1,0,1]}
def line_svg(x1, x2):
    global line_svg_memoized
    try:
        return line_svg_memoized[x1][x2]
    except:
        return line_svg_raw(x1,x2)


class DivTreeLayout(object):
    def __init__(self, t, options=None):
        if options is None:
            options = TreeOptions()
        self.options = options
        self.tree = t

    def render(self, t=None, parent_dir=None):
        initial = (t is None)
        if initial:
            t = self.tree
        parent, children = tree_split(t)
        if len(children) == 0:
            child_layouts = []
        elif len(children) == 1:
            child_layouts = [self.render(children[0], 0)]
        elif len(children) == 2:
            child_layouts = [self.render(children[0], 1),
                             self.render(children[1], -1)]
        else:
            raise NotImplementedError(
                "Trees with >2 daughters are not supported by "
                "html.DivTreeLayout")
        result = self.node_layout(parent, *child_layouts, parent_dir=parent_dir)
        if initial:
            result.set("style",
                       result.get("style", "") + self.options.style_str())
        return result

    def _repr_html_(self):
        return ElementTree.tostring(self.render(), encoding="unicode",
                                                   method="xml")

    def node_layout_unary_grid(self, label, daughter, parent_dir=None):
        if self.options.debug:
            border = "border: 1px solid #848482;"
        else:
            border = "border:none;"
        line_height = px(self.options.em_to_px(
                                            self.options.distance_to_daughter))
        e = Element("div", align="center",
            style=("display:inline-grid;grid-template-columns: 1fr;align-items:start;"
                  + border))
        label_cell = SubElement(e, "div",
            style="grid-column-1;grid-row:1;", align="center")
        label_cell.append(to_html(label, debug=self.options.debug))
        line_cell = SubElement(e, "div", align="center",
            style="grid-column-1;grid-row:2;border:0;height:%s;" % line_height)
        line_cell.append(line_svg(0, 0))
        d_cell = SubElement(e, "div", style="grid-column-1;grid-row:3;")
        d_cell.append(daughter)
        return e

    def node_layout_binary_even(self, label, d1, d2, parent_dir=None):
        if self.options.debug:
            border = "border: 1px solid #848482;"
        else:
            border = "border:none;"
        line_height = px(self.options.em_to_px(self.options.distance_to_daughter))
        e = Element("div",
            style="display:inline-grid;grid-template-columns: repeat(2, 1fr);align-items:start;"
            + border, align="center")
        label_cell = SubElement(e, "div",
            style="grid-column:1/3;grid-row:1;grid-gap:0px",
                                                  align="center")
        label_cell.append(to_html(label, debug=self.options.debug))

        line_cell = SubElement(e, "div", align="center",
            style="grid-column:1;grid-row:2;height:%s;" % line_height)
        line_cell.append(line_svg(1, 0))
        line2_cell = SubElement(e, "div", align="center",
            style="grid-column:2;grid-row:2;height:%s;" % line_height)
        line2_cell.append(line_svg(-1, 0))

        d_cell = SubElement(e, "div",
            style="grid-column:1;grid-row:3;")
        d_cell.append(d1)
        d2_cell = SubElement(e, "div",
            style="grid-column:2;grid-row:3;")
        d2_cell.append(d2)
        return e

    def node_layout_binary_text(self, label, d1, d2, parent_dir=None):
        if self.options.debug:
            border = "border: 1px solid #848482;"
        else:
            border = "border:none;"
        line_height = px(self.options.em_to_px(
                                            self.options.distance_to_daughter))
        e = Element("div",
            style="display:inline-grid;grid-template-columns: repeat(2, auto);align-items:start;"
            + border)
        row = 1
        if parent_dir is not None:
            if parent_dir < 0:
                line = line_svg(-1, 1)
                line_col = "grid-column:1;"
            elif parent_dir > 0:
                line = line_svg(1, -1)
                line_col = "grid-column:2;"
            else:
                line = line_svg(0, 0)
                line_col = "grid-column:1/3;"
            line_div = SubElement(e, "div",
                style=line_col + "grid-row:1;height:%s;" % line_height)
            line_div.append(line)
            row += 1
        # TODO: this is a shameful stack of hacks to get non-leaf nodes for
        # binary branches to position right. First, put the displayed label in
        # a floated cell positioned along the middle grid line in a 0-width
        # grid cell, and transformed to be centered. Second, show the same
        # content in a 0-height hidden div that is centered across the whole
        # grid, in order to get the label to contribute to grid width. Neither
        # of these tricks by themself does the whole thing: the floated div
        # alone can lead to non-leaf nodes overlapping, and the centered div
        # (if it were visible) wouldn't position short labels correctly. A
        # previous version used just the transform trick on a 1-grid cell, but
        # this led to bad spacing when the label is too long.
        label_cell = SubElement(e, "div",
            style="grid-row:%d;grid-column:1;justify-self:right;width:0;" % row)
        label_subdiv = to_html(label, debug=self.options.debug)
        label_dup = copy.deepcopy(label_subdiv)
        style_append(label_subdiv,
            "float:right;transform:translate(50%);white-space:nowrap;")
        label_cell.append(label_subdiv)
        spacer_cell = SubElement(e, "div",
            style="grid-row:%d;grid-column:1/3;justify-self:center;height:0;overflow:hidden;padding-right:1em;padding-left:1em;" % row)
        spacer_cell.append(label_dup)
        row += 1
        d1_cell = SubElement(e, "div",
            style="grid-column:1;grid-row:%d;justify-self:right;" % row)
        d1_cell.append(d1)
        d2_cell = SubElement(e, "div", style="grid-column:2;grid-row:%d;" % row)
        d2_cell.append(d2)
        return e

    def node_layout_unary_text(self, label, *daughters, parent_dir=None):
        if self.options.debug:
            border = "border: 1px solid #848482;"
        else:
            border = "border:none;"
        line_height = px(self.options.em_to_px(
                                            self.options.distance_to_daughter))
        e = Element("div",
            style=("display:inline-grid;grid-template-columns: 1fr;align-items:start;"
                  + border))
        row = 1
        if parent_dir is not None:
            if parent_dir < 0:
                svg = line_svg(-1,0)
            elif parent_dir > 0:
                svg = line_svg(1,0)
            else:
                svg = line_svg(0,0)
            line_cell = SubElement(e, "div",
                style="grid-column:1;grid-row:1;height:%s;" % line_height,
                align="center")
            line_cell.append(svg)
            row += 1

        label_cell = SubElement(e, "div",
            style="grid-column:1;grid-row:%d;justify-self:center;" % row)
        row += 1
        label_cell.append(to_html(label, debug=self.options.debug))
        if len(daughters):
            d_cell = SubElement(e, "div",
                style="grid-column:1;grid-row:%d;justify-self:center;" % row)
            d_cell.append(daughters[0])
        return e

    def leaf_node_layout(self, label, parent_dir=None):
        return to_html(label, debug=self.options.debug)

    def node_layout(self, label, *daughters, parent_dir=None):
        # TODO: idea for arbitrary arity for even. Use the fr values to
        # construct a single svg that stretches across all grid columns?
        def err(o):
            return lambda *x, **y: element_with_text("span",
                style="color:red;",
                text="Unsupported %s for svgling.core.DivTreeLayout" % o)
        layout_map = {
            svgling.core.HorizSpacing.EVEN : [self.leaf_node_layout,
                                              self.node_layout_unary_grid,
                                              self.node_layout_binary_even],
            svgling.core.HorizSpacing.TEXT : [self.node_layout_unary_text,
                                              self.node_layout_unary_text,
                                              self.node_layout_binary_text],
            svgling.core.HorizSpacing.NODES: [err("option NODES")] * 3
        }
        layout_fns = layout_map[self.options.horiz_spacing]
        if len(daughters) > len(layout_fns) - 1:
            err("arity " + str(len(daughters)))
        return layout_fns[len(daughters)](label, *daughters,
                                                        parent_dir=parent_dir)

    def node_layout_table(self, label, *daughters):
        if len(daughters) == 0:
            return to_html(label, debug=self.options.debug)
        if self.options.debug:
            border = "border: 1px solid #848482;"
        else:
            border = ""
        line_height = px(self.options.em_to_px(
                                            self.options.distance_to_daughter))
        e = Element("div", style="display:table;" + border, align="center")
    
        if len(daughters) == 1:
            label_row = SubElement(e, "div", style="display:table-row;")
            label_cell = SubElement(label_row, "div",
                style="display:table-cell;",
                align="center")
            label_cell.append(to_html(label, debug=self.options.debug))
            line_row = SubElement(e, "div", style="display:table-row;")
            line_cell = SubElement(line_row, "div", align="center",
                style="display:table-cell;height:%s;" % line_height)
            line_cell.append(line_svg(0, 0))
            d_row = SubElement(e, "div", style="display:table-row;")
            d_cell = SubElement(d_row, "div", style="display:table-cell;")
            d_cell.append(daughters[0])
        elif len(daughters) == 2:
            label_row = SubElement(e, "div", style="display:table-row;")
            label_cell = SubElement(label_row, "div",
                style="display:table-cell;transform:translate(50%);",
                align="center")
            label_cell.append(to_html(label, debug=self.options.debug))
            extra_cell = SubElement(label_row, "div",
                style="display:table-cell;")
            SubElement(extra_cell, "span") # why is this necessary??
            line_row = SubElement(e, "div",
                style="display:table-row;width:100%;")
            line_cell = SubElement(line_row, "div", align="center",
                style="display:table-cell;height:%s;" % line_height)
            line_cell.append(line_svg(-1, 0))
            line2_cell = SubElement(line_row, "div", align="center",
                style="display:table-cell;height:%s;" % line_height)
            line2_cell.append(line_svg(1, 0))
            d_row = SubElement(e, "div", style="display:table-row;width:100%;")
            d_cell = SubElement(d_row, "div", style="display:table-cell;")
            d_cell.append(daughters[0])
            d2_cell = SubElement(d_row, "div", style="display:table-cell;")
            d2_cell.append(daughters[1])
        else:
            raise NotImplementedError(
                "Trees with >2 daughters are not supported by "
                "html.DivTreeLayout")
        return e
    
def draw_tree(*t, options=None, **opts):
    """Return an object that implements SVG tree rendering, for display
    in a Jupyter notebook."""
    if options is None:
        options = TreeOptions(**opts)
    if len(t) == 1:
        t = t[0]
    return DivTreeLayout(t, options=options)
