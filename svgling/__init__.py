__all__ = ['core']

__version_info__ = (0, 1, 3)
__release__ = False
__version__ = ".".join(str(i) for i in __version_info__)

import svgling.core

draw_tree = svgling.core.draw_tree