import svgwrite
import svgling.core
import svgling.figure
from svgling.core import px

def svg_double_bracket(svg_parent, x, y, width, height):
    x2 = x + width
    y2 = y + height
    x_double = x + width / 2.0
    opts = {"stroke_width": 1, "stroke": "black", "fill": "none"}
    if svgling.core.crisp_perpendiculars:
        opts["shape_rendering"] = "crispEdges"
    svg_parent.add(svgwrite.shapes.Polyline([(x2,y), (x,y), (x,y2), (x2,y2)],
        **opts))
    svg_parent.add(svgwrite.shapes.Line(start=(x_double,y), end=(x_double,y2),
        **opts))

class DoubleBrackets(object):
    def __init__(self, content, padding=0, bracket_width=6):
        self.padding = padding
        self.content = svgling.figure.get_svgable(content)
        self.bracket_width = bracket_width

    def width(self):
        return self.content.width() + (self.bracket_width + self.padding + 1) * 2

    def height(self):
        return self.content.height() + 4

    def get_svg(self, name="figure"):
        height = self.height()
        width = self.width()
        fig_height = self.content.height()
        container = svgwrite.Drawing(name,
                                     (px(width), px(height)))
        container.viewbox(minx=0, miny=0, width=width, height=height)
        container.fit()
        fig_box = svgwrite.container.SVG(x=(self.bracket_width + self.padding + 1),
                                         y=2,
                                         width=self.content.width(),
                                         height=self.content.height())
        fig_box.add(self.content.get_svg())
        container.add(fig_box)
        svg_double_bracket(container, 1, 1, self.bracket_width, height-2)
        svg_double_bracket(container, width-1, 1, -self.bracket_width, height-2)
        return container

    def _repr_svg_(self):
        return self.get_svg().tostring()
