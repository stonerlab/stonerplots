"""Main package file of stonerplots.

Importing :py:mod:`stonerplots` will make the various context managers available, it will also
modify the lists of matplotlib named colours and update the central matplotlib dictionary of stylesheets.

Attributes:
    default (settings):
        A singleton instance of a simple class that stores default values for the styles, formats and filename.
        These defaults are common for all code that uses stonerplots after it has been first imported.
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import get_named_colors_mapping

from .colours import tube_colours, tube_colours_10, tube_colours_50, tube_colours_70, tube_colours_90
from .context import CentredAxes, DoubleYAxis, InsetPlot, MultiPanel, SavedFigure, StackVertical
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
__version__ = "1.9.5"

# Default style handling.
default = _default()

# register the included stylesheet in the matplotlib style library
stonerplots_path = Path(__file__).parent
styles_path = stonerplots_path / "styles"

# Load the bundled styles through Matplotlib's public configuration API.  Older
# versions used helpers from matplotlib.style.core, but those private helpers
# were removed in Matplotlib 3.11.
stylesheets = {
    style_file.stem: mpl.rc_params_from_file(style_file, use_default_template=False)
    for style_file in styles_path.rglob("*.mplstyle")
}
plt.style.library.update(stylesheets)
plt.style.available[:] = sorted(plt.style.library.keys())

get_named_colors_mapping().update(tube_colours)
get_named_colors_mapping().update(tube_colours_90)
get_named_colors_mapping().update(tube_colours_70)
get_named_colors_mapping().update(tube_colours_50)
get_named_colors_mapping().update(tube_colours_10)
