import svgwrite
import svgling.core
from svgling.core import em, perc, px

################
# More general SVG utility classes for drawing complex figures
#
# These are a bit brittle, but work well for svgling trees whose style doesn't
# change significantly.
################

# some hacky code for inheriting embedded styles. We need to do this in various
# cases because `em`s are interpreted relative to a style, and so widths are
# also therefore relative to the style of the embedded svg. This all could use
# a better solution, but I'm not currently sure what it is.
def safe_get_style(s):
    try:
        style = s["style"]
    except:
        style = ""
    return style

def inherit_style(parent, child):
    style = safe_get_style(child)
    if len(style) > 0:
        parent["style"] = style

# essentially a duck type check, does the object support get_svg? If so, we
# are already working with an svgling object. If not, try to convert it to one
# using `draw_tree`. This is maybe a bit too broad, but it is really aiming
# to handle nltk.tree.Tree objects.
def get_svgable(e):
    if hasattr(e, "get_svg") and callable(e.get_svg):
        # we also assume height and width, but don't bother with an explicit
        # check for now...
        return e
    else:
        try:
            return svgling.core.draw_tree(e)
        except: # TypeError?
            raise TypeError("Failed to convert object to renderable: '%s'" % repr(e))

class SideBySide(object):
    def __init__(self, *args, padding=16):
        self.elements = [get_svgable(a) for a in args]
        self.svg_contents = [e.get_svg() for e in self.elements]
        self.widths = [e.width() for e in self.elements]
        self.padding = padding

    def width(self):
        return (sum(self.widths)
                + self.padding * (len(self.elements) + 1))

    def height(self):
        return max([e.height() for e in self.elements])

    def get_svg(self, name="figure", debug=False):
        # TODO: is there any problem embedding `Drawing`s within `Drawing`s?
        container = svgwrite.Drawing(name, (px(self.width()), px(self.height())))
        container.viewbox(minx=0, miny=0, width=self.width(), height=self.height())
        container.fit()
        x_pos = self.padding
        for i in range(len(self.elements)):
            width = self.widths[i]
            box = svgwrite.container.SVG(x=x_pos,
                                         y=0,
                                         width=width,
                                         height=self.elements[i].height())
            box.add(self.svg_contents[i])
            if debug:
                box.add(svgwrite.shapes.Rect(insert=("0%","0%"),
                                                 size=("100%", "100%"),
                                                 fill="none", stroke="red"))
            container.add(box)
            x_pos += width + self.padding
        return container

    def _repr_svg_(self):
        return self.get_svg().tostring()

class RowByRow(object):
    def __init__(self, *args, padding=16, gridify=True):
        self.elements = [get_svgable(a) for a in args]
        self.padding = padding
        if gridify:
            self._gridify()
        self.svg_contents = [e.get_svg() for e in self.elements]

    def height(self):
        return (sum([e.height() for e in self.elements])
                + self.padding * (len(self.elements) + 1))

    def _gridify(self):
        max_widths = list()
        max_padding = 0
        for e in self.elements:
            if isinstance(e, SideBySide):
                max_padding = max(max_padding, e.padding)
                for j in range(len(e.elements)):
                    if j >= len(max_widths):
                        max_widths.extend([0])
                    max_widths[j] = max(max_widths[j], e.elements[j].width())
            else:
                if len(max_widths) == 0:
                    max_widths.extend([0])
                max_widths[0] = max(max_widths[0], e.width())
        for e in self.elements:
            if isinstance(e, SideBySide):
                e.padding = max_padding
                for j in range(len(e.elements)):
                    e.widths[j] = max_widths[j]

    def width(self):
        return max([e.width() for e in self.elements])

    def get_svg(self, name="figure"):
        # TODO: is there any problem embedding `Drawing`s within `Drawing`s?
        container = svgwrite.Drawing(name,
                                     (px(self.width()), px(self.height())))
        container.viewbox(minx=0, miny=0, width=self.width(), height=self.height())
        container.fit()
        y_pos = self.padding
        for i in range(len(self.elements)):
            height = self.elements[i].height()
            box = svgwrite.container.SVG(x=0, y=y_pos,
                                         height=height,
                                         width=self.elements[i].width())
            box.add(self.svg_contents[i])
            inherit_style(box, self.svg_contents[i])
            container.add(box)
            y_pos += height + self.padding
        return container

    def _repr_svg_(self):
        return self.get_svg().tostring()

class Caption(object):
    font_style = "font-family: times, serif; font-weight:normal; font-style: italic;"
    def __init__(self, fig, caption, font_size=13):
        self.fig = get_svgable(fig)
        self.caption = caption
        self.font_size = font_size

    def height(self):
        return self.fig.height() + 2.5 * self.font_size

    def width(self):
        return max(self.fig.width(), self.caption_width())

    def caption_width(self):
        return self.font_size * len(self.caption) / 2.0

    def style_str(self):
        # TODO: generalize caption style
        return self.font_style + " font-size: " + px(self.font_size) + ";"

    def get_svg(self, name="figure", debug=False):
        width = self.width()
        height = self.height()
        fig_width = self.fig.width()
        caption_width = self.caption_width()
        container = svgwrite.Drawing(name, (px(width), px(height)))
        container.viewbox(minx=0, miny=0, width=width, height=height)
        container.fit()
        y_pos = self.fig.height() + 0.5 * self.font_size
        caption_svg = svgwrite.text.Text(self.caption,
                                         insert=("50%", "1em"),
                                         text_anchor="middle",
                                         style = self.style_str())
        # this next is to keep any font style from impacting the interpretation
        # of ems in positioning the box.
        caption_box = svgwrite.container.SVG(x=0, y=y_pos, width="100%", height="100%")
        if debug:
            caption_box.add(svgwrite.shapes.Rect(insert=("0%","0%"),
                                                 size=("100%", "100%"),
                                                 fill="none", stroke="red"))
        caption_box.add(caption_svg)
        if (fig_width > caption_width):
            fig_x = 0
        else:
            fig_x = (caption_width - fig_width) / 2.0
        box = svgwrite.container.SVG(x=fig_x, y=0,
                                     width=fig_width,
                                     height=self.fig.height())
        fig_svg = self.fig.get_svg()
        box.add(fig_svg)
        container.add(box)
        container.add(caption_box)
        return container

    def _repr_svg_(self):
        return self.get_svg().tostring()

