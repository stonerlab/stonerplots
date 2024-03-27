"""Build the list of stylesheets and add to matplotlib."""
from pathlib import Path
import matplotlib.pyplot as plt
from .context import SavedFigure,InsetPlot

__all__ = ["SavedFigure","InsetPlot"]
__version__ = "1.1.0"

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
