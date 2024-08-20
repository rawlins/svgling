__all__ = ['core', 'figure', 'semantics', 'html', 'utils', '__main__']

__version_info__ = (0, 5, 0)
__release__ = True
__version__ = ".".join(str(i) for i in __version_info__)
if not __release__:
    __version__ = __version__ + "-a1"

import svgling.core

draw_tree = svgling.core.draw_tree
tree2svg = svgling.core.tree2svg

disable_nltk_png = svgling.core.disable_nltk_png
