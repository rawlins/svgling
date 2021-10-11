__all__ = ['core', 'figure', 'semantics', 'html', '__main__']

__version_info__ = (0, 3, 1)
__release__ = True
__version__ = ".".join(str(i) for i in __version_info__)

import svgling.core

draw_tree = svgling.core.draw_tree

def disable_nltk_png():
    """
    while SVG will take priority, Jupyter will still typically call the png
    renderer, which can have annoying consequences, because of its dependency on
    tk. On OS X, this leads to a blank, windowless app in the dock as long as
    the kernel is running. On a headless setup, it leads to errors. This
    convenience function completely disables the png-drawing code in nltk. If it
    fails (either because nltk isn't installed, or the relevant function has
    already been deleted) it will fail silently.
    """
    # TODO: do this by default?
    # TODO: should we save this function somehow?
    try:
        import nltk
        del nltk.tree.Tree._repr_png_
    except:
        pass
