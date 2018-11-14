import svgwrite
import svgling.core
from svgling.core import em, perc

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

class SideBySide(object):
    def __init__(self, *args, padding=1):
        self.elements = args
        self.svg_contents = [e.get_svg() for e in self.elements]
        self.padding = padding

    def width(self):
        return (sum([e.width() for e in self.elements])
                + self.padding * (len(self.elements) - 1))

    def height(self):
        return max([e.height() for e in self.elements])

    def get_svg(self, name="figure", debug=False):
        # TODO: is there any problem embedding `Drawing`s within `Drawing`s?
        container = svgwrite.Drawing(name, (em(self.width()), em(self.height())))
        # the somewhat elaborate recursion here is to try to handle the case
        # where the font style changes the meaning of an `em` between
        # subfigures. TODO: I still haven't figured out how to calculate the
        # width reliably when this happens.
        # TODO: this also leads to unexpected inheritence if font styles are
        # only partially specified.
        last_box = container
        inherit_style(container, self.svg_contents[0])
        last_width = 0
        for i in range(len(self.elements)):
            outer_box = svgwrite.container.SVG(x=em(last_width), y=0, width="100%")
            box = svgwrite.container.SVG(x=0, y=0)
            outer_box.add(box)
            box.add(self.svg_contents[i])
            if debug:
                box.add(svgwrite.shapes.Rect(insert=("0%","0%"),
                                                 size=("100%", "100%"),
                                                 fill="none", stroke="red"))
            inherit_style(box, self.svg_contents[i])
            inherit_style(last_box, outer_box)
            last_box.add(outer_box)
            last_box = box
            last_width = self.elements[i].width()
        return container

    def _repr_svg_(self):
        return self.get_svg().tostring()

class RowByRow(object):
    def __init__(self, *args, padding=1):
        self.elements = args
        self.svg_contents = [e.get_svg() for e in self.elements]
        self.padding = padding

    def height(self):
        return (sum([e.height() for e in self.elements])
                + self.padding * (len(self.elements) - 1))

    def width(self):
        return max([e.width() for e in self.elements])

    def get_svg(self, name="figure"):
        # TODO: is there any problem embedding `Drawing`s within `Drawing`s?
        # TODO: update with recursive code as in SideBySide
        container = svgwrite.Drawing(name,
                                     (em(self.width()), em(self.height())))
        y_pos = 0
        for i in range(len(self.elements)):
            height = self.elements[i].height()
            box = svgwrite.container.SVG(x=0, y=em(y_pos), height=em(height))
            box.add(self.svg_contents[i])
            inherit_style(box, self.svg_contents[i])
            container.add(box)
            y_pos += height + self.padding
        return container

    def _repr_svg_(self):
        return self.get_svg().tostring()

class Caption(object):
    font_style = "font-family: times, serif; font-weight:normal; font-style: italic; font-size: 10pt;"
    def __init__(self, fig, caption):
        self.fig = fig
        self.caption = caption

    def height(self):
        return self.fig.height() + 2.0

    def width(self):
        return max(self.fig.width(), self.caption_width())

    def caption_width(self):
        return len(self.caption) / 2.0

    def get_svg(self, name="figure", debug=False):
        width = self.width()
        fig_width = self.fig.width()
        caption_width = self.caption_width()
        container = svgwrite.Drawing(name,
                                     (em(width), em(self.height())))
        y_pos = self.fig.height()
        caption_svg = svgwrite.text.Text(self.caption,
                                         insert=("50%", "1em"),
                                         text_anchor="middle",
                                         style = self.font_style)
        # this next is to keep any font style from impacting the interpretation
        # of ems in positioning the box.
        caption_box = svgwrite.container.SVG(x=0, y=em(y_pos))
        if debug:
            caption_box.add(svgwrite.shapes.Rect(insert=("0%","0%"),
                                                 size=("100%", "100%"),
                                                 fill="none", stroke="red"))
        caption_box.add(caption_svg)
        # TODO: this is a bit broken if font style in the fig changes...
        if (fig_width > caption_width):
            fig_x = 0
        else:
            fig_x = (caption_width - fig_width) / 2.0
        box = svgwrite.container.SVG(x=em(fig_x), y=0, width=em(fig_width))
        fig_svg = self.fig.get_svg()
        box.add(fig_svg)
        inherit_style(box, fig_svg)
        container.add(box)
        inherit_style(container, box)
        container.add(caption_box)
        return container

    def _repr_svg_(self):
        return self.get_svg().tostring()

