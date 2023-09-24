__all__ = ['core', 'figure', 'semantics', 'html', 'utils', '__main__']

__version_info__ = (0, 4, 0)
__release__ = True
__version__ = ".".join(str(i) for i in __version_info__)

import svgling.core

draw_tree = svgling.core.draw_tree

disable_nltk_png = svgling.core.disable_nltk_png
