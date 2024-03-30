# -*- coding: utf-8 -*-
"""Context Managers to help with plotting and saving figures."""
from pathlib import Path
import weakref
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, InsetPosition

import stonerplots

__all__ = ["SavedFigure", "InsetPlot", "StackVertical"]


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
            filename = Path(filename)
            ext = filename.suffix
            if formats is None and len(ext) > 1:  # Use filename extension as format ifd not set
                formats = [ext[1:]]
            # Store filename with extension stripped
            filename = filename.parent / filename.stem
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
                    new_file = filename.parent / (filename.stem + f".{fmt.lower()}")
                    new_file = str(new_file).format(fighum=num, ix=processed, fmt=fmt)
                    fig.savefig(new_file)
                if self.autoclose:
                    plt.close(num)


class InsetPlot(object):
    """A context manager to help make inset plopts a bit less painful.

    Keyword Arguments:
        ax (matplotlib.Axes):
            The axes in which to create the inset. If not set (default is None), then use the current axes.
        loc (str,int):
            Location string - same meanings as legend locators except there isn't an "auto" value 0.
        width, height (float):
            Dimension of the width and height of the inset. The units are in inches unless *dimension* is "fraction" -
            which is the default.
        dimension (str, default 'fraction'):
            IF 'fraction' then the width and height are a fraction of the parent axes, otherwise the dimensions are
            in inches.

    The InsetPlot conext manager will adjust the placement of the inset as it exists to ensure the inset axes labels
    don't collide with the parent axes.
    """

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
        dx0 = (inset_axes_bbox.x0 - inset_bbox.x0) / parent_bbox.width  # X axes label space
        dy0 = inset_axes_bbox.y0 - inset_bbox.y0 / parent_bbox.height  # yaxis labels space
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


class StackVertical(object):

    """A context manager that will generate a stack of subplots with common x axes.

    Args:
        number (int):
            Nunber of sub-plots to stack vertically.

    Keyword Args:
        figure (matplotlib.Figure):
            Figure to use to contain the sub-plots in. If None (default) then the current figure is used.
        joined (bool):
            Whether to remove the vertical space between the sub-plots or not. Default is True.
        sharex, sharey (bool):
            Wherther the sub-plots have common x or y axes. Default is shared x and separate y.
        adjust_figsize (float,bool):
            Whether to increase the figure height to accomodate the extra plots. If True, the figure is
            increased by 0.6 of the original height for each additional sub-plot after the first. If a float
            is given, then the additional height factor is the adjust_figsize value. The default is True, or 0.6
        label_panels (book):
            Whether to add (a), (b) etc. to the sub-plots. Default of True positions labels in the top right corner of
            the sub-plots. The top sub-plot is the first one.

    Returns:
        (List[matplotlib.Axes]):
            The context manager bariable is the list of axes created.

    Notes:
        Matplotlib's constrained layout makes it extra hard to get the pots to stack with no space between them as
        labels and figure titles can get in the way and the whole point of constrained layout is to avoid these
        elements colliding. The context manager gets around this by inspecting the y-ticks and y-limits in the
        __exit__  method and adjusting limits as necessary to keep the tick lables from clashing.
    """

    def __init__(
        self, number, figure=None, joined=True, sharex=True, sharey=False, adjust_figsize=True, label_panels=True
    ):
        """Set up for the stack of plots."""
        self.number = number
        self.joined = joined
        self.figure = figure if figure else plt.gcf()
        self.gs = None
        self.sharex = sharex
        self.sharey = sharey
        self.adjust_figsize = adjust_figsize if isinstance(adjust_figsize, float) else float(int(adjust_figsize)) * 0.6
        self.label_panels = label_panels
        self.figsize = self.figure.get_figwidth(), self.figure.get_figheight()

    def __enter__(self):
        """Create the grid of axes."""
        hspace = 0 if self.joined else 0.1
        self.gs = self.figure.add_gridspec(self.number, hspace=hspace)
        self.axes = self.gs.subplots(sharex=self.sharex, sharey=self.sharey)
        if self.adjust_figsize:
            extra_h = self.figsize[1] * self.adjust_figsize * (self.number - 1) + self.figsize[0]
            self.figure.set_figheight(extra_h)
        if self.label_panels:
            for ix, ax in enumerate(self.axes):
                ax.set_title(f" ({chr(ix+ord('a'))})", loc="left", y=0.85)
        return self.axes

    def __exit__(self, type, value, traceback):
        """Clean up the axes."""
        if self.joined:
            for ax in self.axes:
                ax.label_outer()
            plt.draw()
            for ix, ax in enumerate(self.axes):
                ylim = list(ax.get_ylim())
                yticks = ax.get_yticks()
                dy = (yticks[1] - yticks[0]) / 4
                if ylim[0] - yticks[0] < dy and ix != len(self.axes) - 1:  # Adjust range of plots excepty bottom one
                    ylim[0] = yticks[0] - dy
                if yticks[-1] - ylim[1] < dy and ix != 0:  # Adjust range of plots except top one.
                    ylim[1] = yticks[-1] + dy
                ax.set_ylim(ylim)

            self.figure.get_layout_engine().set(h_pad=0.0, hspace=0.0)
        # breakpoint()
        self.figure.canvas.draw()
        pass


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
