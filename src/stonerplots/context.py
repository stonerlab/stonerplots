# -*- coding: utf-8 -*-
"""Context Managers to help with plotting and saving figures."""
from pathlib import Path
import weakref
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, InsetPosition


import stonerplots

__all__ = ["SavedFigure", "InsetPlot"]


class SavedFigure(object):
    """Context manager that applies a style and saves figures.

    Keyword Arguments:
        filename (str, Path, default=None):
            The filename to use for saving the figure created. If None then the figure's label is used as a
            filename.
        style (str, List[str], default is ['science','nature','vibrant']):
            The mnatplotlib syslesheet(s) to use for plotting.
        autoclose (bool, default=False):
            Automatically close figures after they are saved. This leaves open figures that were open before we
            started,
        formats (list of str, default ["png"]):
            List of file extensions (and hence formats) to use when saving the file.

    This wraps the mpl.style.context() context manager and also determines what new figures have been created and
    saves them with a soecified filename.
    """

    def __init__(self, filename=None, style=None, autoclose=False, formats=None):
        """Create the context manager.

        Keyword Arguments:
            filename (str, Path, default=None):
                The filename to use for saving the figure created. If None then the figure's label is used as a
                filename.
            style (str, List[str], default is ['stoner','aps','aps1.5']):
                The mnatplotlib syslesheet(s) to use for plotting.
            autoclose (bool, default=False):
                Automatically close figures after they are saved. This leaves open figures that were open before we
                started.
            formats (list of str, default ["png"]):
                List of file extensions (and hence formats) to use when saving the file.

        """
        if filename is not None:
            filename=Path(filename)
            ext=filename.suffix
            if formats is None and len(ext)>1: # Use filename extension as format ifd not set
                formats=[ext[1:]]
            # Store filename with extension stripped
            filename=filename.parent/filename.stem           
        self.filename = filename
        
        if style is None:
            self.style = ["stoner", "aps", "aps1.5"]
        else:
            self.style = style
        self.autoclose = autoclose
        self.style_context = None
        self.formats = ["png"] if formats is None else formats
        self.open_figs = []

    def __enter__(self):
        """Record the open figures and start the style context manager.

        Creates a list of weak references to all the open figures. This is then used to detect whether an open figure
        has been created within the context manager or not. We use weak references to allow figures to be closed
        without blocking.
        """
        for num in plt.get_fignums():
            self.open_figs.append(weakref.ref(plt.figure(num)))
        self.style_context = mpl.style.context(self.style)
        self.style_context.__enter__()

    def __exit__(self, type, value, traceback):
        """Cleanup context manager and save figures created.

        First call the __exit__ of the style context manager to finish of plotting with the specified stylesheet, then
        cjeck all the open figures and if they were not in our list of figures open before, save them with a filename
        from the keyword parameter to __init__ or the plot label.
        """
        self.style_context.__exit__(type, value, traceback)
        self.open_figs = [x() for x in self.open_figs if x() is not None]
        processed = -1
        for num in plt.get_fignums():
            if (fig := plt.figure(num)) not in self.open_figs:  # new figure
                processed += 1
                filename = self.filename if self.filename is not None else Path(fig.get_label())
                for fmt in self.formats:
                    new_file=filename.parent/(filename.stem+f".{fmt.lower()}")
                    new_file = str(new_file).format(fighum=num, ix=processed, fmt=fmt)
                    fig.savefig(new_file)
                if self.autoclose:
                    plt.close(num)


class InsetPlot(object):
    """A context manager to help make inset plopts a bit less painful."""

    locations = {
        "upper right": 1,
        "upper left": 2,
        "lower left": 3,
        "lower right": 4,
        "right": 5,
        "center left": 6,
        "center right": 7,
        "lower center": 8,
        "upper center": 9,
        "center": 10,
    }

    def __init__(self, ax=None, loc="upper left", width=0.25, height=0.25, dimension="fraction"):
        """Set the location for the axes."""
        if ax is None:  # Use current axes if not passed explicitly
            ax = plt.gca()
        self.ax = ax
        if not isinstance(loc, int):
            loc = self.locations.get(loc.lower(), 1)
        self.loc = loc
        if dimension == "fraction":
            if isinstance(height, float) and 0.0 < height <= 1.0:
                height = f"{height*100:.0f}%"
            if isinstance(width, float) and 0.0 < width <= 1.0:
                width = f"{width*100:.0f}%"
        self.height = height
        self.width = width
        self.padding = 0.05

    def __enter__(self):
        """Create the inset axes using the axes_grid toolkit."""
        axins = inset_axes(self.ax, width=self.width, height=self.height, loc=self.loc)
        self.axins = axins
        return self.axins

    def __exit__(self, type, value, traceback):
        """Reposition the inset as the standard positioning can cause labels to overlap."""

        parent_bbox = self.ax.get_position()
        inset_bbox = self.axins.get_tightbbox().transformed(self.ax.figure.transFigure.inverted())
        inset_axes_bbox = self.axins.get_position()
        dx0 = (inset_axes_bbox.x0 - inset_bbox.x0) / parent_bbox.width # X axes label space
        dy0 = inset_axes_bbox.y0 - inset_bbox.y0 / parent_bbox.height # yaxis labels space
        rw = inset_bbox.width / parent_bbox.width
        rh = inset_bbox.height / parent_bbox.height

        if self.loc == 1:  # Upper right
            x0 = 1 - rw - self.padding
            y0 = 1 - rh - self.padding
        elif self.loc == 2:  # Upper left
            x0 = dx0 + self.padding
            y0 = 1 - rh - self.padding
        elif self.loc == 3:  # Lower left
            x0 = dx0 + self.padding
            y0 = dy0 + self.padding
        elif self.loc == 4:  # lower right
            x0 = 1 - rw - self.padding
            y0 = dy0 + self.padding
        elif self.loc in [5, 7]:  # right
            x0 = 1 - rw - self.padding
            y0 = (1 - rh) / 2
        elif self.loca == 6:  # centre left
            x0 = dx0 + self.padding
            y0 = (1 - rh) / 2
        elif self.loc == 8:  # lower center
            x0 = (1 - rw) / 2
            y0 = dy0 + self.padding
        elif self.loc == 9:  # upper center
            x0 = dx0 + self.padding
            y0 = 1 - rh - self.padding
        elif self.loc == 10:  # center
            x0 = (1 - rw) / 2
            y0 = (1 - rh) / 2
        newpos = InsetPosition(self.ax, [x0, y0, rw, rh])
        self.axins.set_axes_locator(newpos)
        self.ax.figure.canvas.draw()


if __name__ == "__main__":
    with SavedFigure("test-{ix}.pdf", autoclose=True):
        plt.figure()
        x = np.linspace(0, 6, 200)
        y = np.sinc(x) ** 2
        plt.plot(x, y, "+")
        plt.xlabel("Test")
        plt.figure()
        plt.plot(x, y**2, "+")
        plt.yscale("log")
        plt.ylim(1e-9, 1)
        plt.xlabel("Test")
