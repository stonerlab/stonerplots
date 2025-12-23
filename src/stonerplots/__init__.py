"""Main package file of stonerplots.

Importing :py:module`stonerplots` will make the various context managers available, it will also
modify the lists of matplotlib named colours and update the central matplotlib dictionary of stylesheets.

Attrs:
    default (settings):
        A singleton insance of a simple class that stores default values for the styles, formats and filename.
        These defaults are common for all code that uses stonerplots after it has been first imported.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import _colors_full_map

from .colours import (
    tube_colours,
    tube_colours_10,
    tube_colours_50,
    tube_colours_70,
    tube_colours_90,
)
from .context import DoubleYAxis, InsetPlot, MultiPanel, SavedFigure, StackVertical, CentredAxes
from .counter import counter, roman
from .format import PlotLabeller, TexEngFormatter, TexFormatter
from .util import _default

__all__ = [
    "context",
    "CentredAxes",
    "SavedFigure",
    "InsetPlot",
    "StackVertical",
    "MultiPanel",
    "DoubleYAxis",
    "counter",
    "roman",
    "format",
    "PlotLabeller",
    "TexFormatter",
    "TexEngFormatter",
    "default",
]
__version__ = "1.8.2"

# Default style handling.
default = _default()

# register the included stylesheet in the matplotlib style library
stonerplots_path = Path(__file__).parent
styles_path = stonerplots_path / "styles"

# Reads styles in /styles
stylesheets = plt.style.core.read_style_directory(str(styles_path))
# Reads styles in /styles subfolders
for inode in styles_path.rglob("*"):
    if inode.is_dir():
        new_data_path = styles_path / inode
        new_stylesheets = plt.style.core.read_style_directory(str(new_data_path))
        stylesheets.update(new_stylesheets)

# Update dictionary of styles
plt.style.core.update_nested_dict(plt.style.library, stylesheets)
plt.style.core.available[:] = sorted(plt.style.library.keys())

_colors_full_map.update(tube_colours)
_colors_full_map.update(tube_colours_90)
_colors_full_map.update(tube_colours_70)
_colors_full_map.update(tube_colours_50)
_colors_full_map.update(tube_colours_10)
