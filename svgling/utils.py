
# conversion functions. Just a light wrapper on cairosvg for objects that
# implement `_repr_svg_()`. See cairosvg documentation for possible named args.

def try_import_cairosvg():
    try:
        import cairosvg
        return cairosvg
    except ImportError:
        print("Error: for svgling conversion functions to work, install the `cairosvg` package.")
        raise

# TODO: cairosvg seems to be expecting utf-8 encoded byte sequence by the docs,
# but passing a string seems to work fine. Does it ever break?
def svg2png(tree, **args):
    cairosvg = try_import_cairosvg()
    return cairosvg.svg2png(tree._repr_svg_(), **args)

def svg2pdf(tree, **args):
    cairosvg = try_import_cairosvg()
    return cairosvg.svg2pdf(tree._repr_svg_(), **args)

def svg2ps(tree, **args):
    cairosvg = try_import_cairosvg()
    return cairosvg.svg2ps(tree._repr_svg_(), **args)
