# -*- coding: utf-8 -*-
"""Context Managers to help with plotting and saving figures."""
from pathlib import Path
import weakref
from collections.abc import Sequence
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, InsetPosition

import stonerplots

__all__ = ["SavedFigure", "InsetPlot", "StackVertical", "MultiPanel"]

_fontargs = ["font", "fontfamily", "fontname", "fontsize", "fontstretch", "fontstyle", "fontvariant", "fontweight"]


def _filter_dict(dic, keys):
    """Return a dictionary derived from dic that only contains the keys in keys."""
    ret = {}
    for key in set(dic.keys()) & set(keys):
        ret[key] = dic[key]
    return ret


def _roman(ix):
    numerals = {
        1000: "M",
        900: "CM",
        500: "D",
        400: "CD",
        100: "C",
        90: "XC",
        50: "L",
        40: "XL",
        10: "X",
        9: "IX",
        5: "V",
        4: "IV",
        1: "I",
    }
    output = ""
    for val, numeral in numerals.items():
        if count := ix // val:
            ix -= count * val
            output += numeral * count
    return output


def _counter(ix, pattern="({alpha})"):
    """Return a representation of an integer according to a pattern.

    Args:
        ux (int):
            The integer to convert to a string.

    Keyword Argyments:
        pattern (str):
            The pattern to be used to format the conversion. Defaykt is '({alpha})'. See Notes for details.

    Returns:
        *(str):
            *ix* converted to a string according to pattern.

        Notes:
            *pattern* is a standard format string with place holders in {}. It is formatted with preset representations
            of the integer *ix*
            - int - ix as an integer
            - alpha - ix as a,b,c...
            - Alpha - ix as A,B,C...
            - roman - ix as i,ii,iii,iv...
            - Roman - ix as I,II,III,IV....
    """
    alpha = chr(ord("a") + int(ix))
    Roman = _roman(int(ix + 1))
    return pattern.format(
        **{"alpha": alpha, "Alpha": alpha.upper(), "roman": Roman.lower(), "Roman": Roman, "int": int(ix)}
    )


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
        include_open (bool):
            If set to True (default is False), then existing figures will be included when saving.

    This wraps the mpl.style.context() context manager and also determines what new figures have been created and
    saves them with a soecified filename.
    """

    def __init__(self, filename=None, style=None, autoclose=False, formats=None, include_open=False):
        """Create the context manager.

        Keyword Arguments:
            filename (str, Path, default=None):
                The filename to use for saving the figure created. If None then the figure's label is used as a
                filename.
            style (str, List[str, False], default is ['stoner']):
                The mnatplotlib syslesheet(s) to use for plotting. If False, then the current styling is unchanged.
            autoclose (bool, default=False):
                Automatically close figures after they are saved. This leaves open figures that were open before we
                started.
            formats (list of str, default ["png"]):
                List of file extensions (and hence formats) to use when saving the file.
            include_open (bool):
                If set to True (default is False), then existing figures will be included when saving.

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
            self.style = ["stoner"]
        else:
            self.style = style
        self.autoclose = autoclose
        self.style_context = None
        if isinstance(formats, str):
            formats = [formats]
        self.formats = ["png"] if formats is None else formats
        self.open_figs = []
        self.include_open = include_open

    def __enter__(self):
        """Record the open figures and start the style context manager.

        Creates a list of weak references to all the open figures. This is then used to detect whether an open figure
        has been created within the context manager or not. We use weak references to allow figures to be closed
        without blocking.
        """
        for num in plt.get_fignums():
            if not self.include_open:
                self.open_figs.append(weakref.ref(plt.figure(num)))
        if self.style:
            self.style_context = mpl.style.context(self.style)
            self.style_context.__enter__()

    def __exit__(self, type, value, traceback):
        """Cleanup context manager and save figures created.

        First call the __exit__ of the style context manager to finish of plotting with the specified stylesheet, then
        cjeck all the open figures and if they were not in our list of figures open before, save them with a filename
        from the keyword parameter to __init__ or the plot label.
        """
        if self.style:
            self.style_context.__exit__(type, value, traceback)
        self.open_figs = [x() for x in self.open_figs if x() is not None]
        processed = -1
        for num in plt.get_fignums():
            if (fig := plt.figure(num)) in self.open_figs:  # old  figure
                continue
            processed += 1
            filename = self.filename if self.filename is not None else Path(fig.get_label())
            for fmt in self.formats:
                new_file = filename.parent / (filename.stem + f".{fmt.lower()}")
                _tmp_file = new_file
                new_file = _counter(processed, str(new_file))
                if new_file == _tmp_file and processed > 0:  # Filename didn't have a counter and we are on file 2
                    parts = new_file.split(".")
                    parts[-2] += f"-{processed}"
                    new_file = ".".join(parts)  # Add -# to the figure()end of the file before the extension.
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
            If 'fraction' then the width and height are a fraction of the parent axes, otherwise the dimensions are
            in inches.
        switch_to_inset (bool):
            If True (default), then within the context mananager, pyplot's current axes are set to the inset and the
            previous axes are restored as the 'current axes' on exit.

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

    def __init__(self, ax=None, loc="upper left", width=0.25, height=0.25, dimension="fraction", switch_to_inset=True):
        """Set the location for the axes."""
        if ax is None:  # Use current axes if not passed explicitly
            ax = plt.gca()
        self.save_ax = plt.gca()
        self.ax = ax
        if not isinstance(loc, int):
            loc = self.locations.get(str(loc).lower().replace("-", " "), 1)
        self.loc = loc
        if dimension == "fraction":
            if isinstance(height, float) and 0.0 < height <= 1.0:
                height = f"{height*100:.0f}%"
            if isinstance(width, float) and 0.0 < width <= 1.0:
                width = f"{width*100:.0f}%"
        self.height = height
        self.width = width
        self.padding = 0.05
        self.switch_to_inset = switch_to_inset

    def __enter__(self):
        """Create the inset axes using the axes_grid toolkit."""
        axins = inset_axes(self.ax, width=self.width, height=self.height, loc=self.loc)
        self.axins = axins
        if self.switch_to_inset:
            plt.sca(self.axins)
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
        if self.switch_to_inset:
            plt.sca(self.save_ax)


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
        label_panels (str or bool):
            Whether to add (a), (b) etc. to the sub-plots. Default of True positions labels in the top right corner of
            the sub-plots. The top sub-plot is the first one. If a string, then use this as a the pattern to determine
            how to format the plot number to a string. The default value of True corresponds to '({alpha})', other
            supported counters are
            - int - simpe numeral
            - alpha / Alpha - lower / uppper case letters
            - roman / Roman - lower / upper case Roman numerals.

        kwargs:
            Other keyword arguments can be used to set the label fonts and are passed into ac.set_title.

    Returns:
        (List[matplotlib.Axes]):
            The context manager bariable is the list of axes created.

    Notes:
        Matplotlib's constrained layout makes it extra hard to get the pots to stack with no space between them as
        labels and figure titles can get in the way and the whole point of constrained layout is to avoid these
        elements colliding. The context manager gets around this by inspecting the y-ticks and y-limits in the
        __exit__  method and adjusting limits as necessary to keep the tick lables from clashing. Within the context
        manager, the current figure will be the one with the stacked axes. The previous active figure is restored on
        exit.
    """

    def __init__(
        self,
        number,
        figure=None,
        joined=True,
        sharex=True,
        sharey=False,
        adjust_figsize=True,
        label_panels=True,
        **kwargs,
    ):
        """Set up for the stack of plots."""
        self.number = number
        self.joined = joined

        self.figure = figure if figure else plt.gcf()
        self._save_fig = plt.gcf()
        if isinstance(self.figure, int) and self.figure in plt.get_fignums:  # If we specified a figure as a number
            self.figure = plt.figure(self.fignum)
        if isinstance(self.figure, str) and self.figure in plt.get_figlabels:  # If we specified a figure as a label
            self.figure = plt.figure(self.fignum)

        plt.figure(self.figure)
        self.gs = None
        self.sharex = sharex
        self.sharey = sharey
        self.adjust_figsize = adjust_figsize if isinstance(adjust_figsize, float) else float(int(adjust_figsize)) * 0.8
        self.label_panels = "({alpha})" if isinstance(label_panels, bool) and label_panels else label_panels
        self.figsize = self.figure.get_figwidth(), self.figure.get_figheight()
        self.kwargs = kwargs

    def __enter__(self):
        """Create the grid of axes."""
        hspace = 0 if self.joined else 0.1
        self.gs = self.figure.add_gridspec(self.number, hspace=hspace)
        self.axes = self.gs.subplots(sharex=self.sharex, sharey=self.sharey)
        if self.adjust_figsize:
            extra_h = self.figsize[1] * self.adjust_figsize * (self.number - 1) + self.figsize[1]
            self.figure.set_figheight(extra_h)
        if self.label_panels:
            fig = self.figure
            for ix, ax in enumerate(self.axes):
                title_pts = ax.title.get_fontsize()
                ax_height = ax.bbox.transformed(fig.transFigure.inverted()).height * fig.get_figheight() * 72
                y = (ax_height - title_pts * 1.25) / ax_height

                ax.set_title(
                    f" {_counter(ix,self.label_panels)}", loc="left", y=y, **_filter_dict(self.kwargs, _fontargs)
                )
        return self.axes

    def __exit__(self, type, value, traceback):
        """Clean up the axes."""
        if self.joined:
            for ax in self.axes:
                ax.label_outer()
            plt.draw()
            fig = self.figure
            for ix, ax in enumerate(self.axes):
                fnt_pts = ax.yaxis.get_ticklabels()[0].get_fontsize()
                ax_height = ax.bbox.transformed(fig.transFigure.inverted()).height * fig.get_figheight() * 72
                ylim = list(ax.get_ylim())
                dy = 0.65 * fnt_pts / ax_height * (ylim[1] - ylim[0])  # How much axes space the labels take up
                yticks = ax.get_yticks()
                if yticks[1] - ylim[0] < dy and ix != len(self.axes) - 1:  # Adjust range of plots excepty bottom one
                    ylim[0] -= dy
                if ylim[1] - yticks[-2] < dy and ix != 0:  # Adjust range of plots except top one.
                    ylim[1] += dy
                ax.set_ylim(ylim)

            self.figure.get_layout_engine().set(h_pad=0.0, hspace=0.0)
        self.figure.canvas.draw()
        plt.figure(self._save_fig)


class MultiPanel(object):

    """A context manager for sorting out multi-panel plots in matplotlib.

    Args:
        panels (tuple[int.int] or int):
            Nunber of sub-plots to produce. If a tuple then it spewcifies rows, columns. If a integer then it
            specifies (1, columns)

    Keyword Args:
        figure (matplotlib.Figure):
            Figure to use to contain the sub-plots in. If None (default) then the current figure is used.
        sharex, sharey (bool):
            Wherther the sub-plots have common x or y axes. Default is neither.
        adjust_figsize (tuple[float,float], float,bool):
            Whether to increase the figure height to accomodate the extra plots. If True, the figure is
            increased by 0.6 of the original height and 1 times the original width  for each additional sub-plot
            row or column after the first. If a float is given, then the additional height ad width factor is the
            adjust_figsize value. If a tuple, them separate expansion factors can be given for each dimenion
            (width, height). The default is True, or 0.8
        label_panels (str or bool):
            Whether to add (a), (b) etc. to the sub-plots. Default of True positions labels in the top right corner of
            the sub-plots. The top sub-plot is the first one. If a string, then use this as a the pattern to determine
            how to format the plot number to a string. The default value of True corresponds to '({alpha})', other
            supported counters are
            - int - simpe numeral
            - alpha / Alpha - lower / uppper case letters
            - roman / Roman - lower / upper case Roman numerals.

        kwargs:
            Other keyword arguments can be used to set the label fonts and are passed into ac.set_title.

    Returns:
        (List[matplotlib.Axes]):
            The context manager bariable is the list of axes created.

    Notes:
        Since double-column figures in journals are more than twice the single figure dimension, it might be useful to
        use the double width figure stylesheet, and then specify an *adjust_figsize* of (0,<something>) to keep the
        full width figure setting and expand the height as required (bearing in mind the double column figures often
        already have more height.)
    """

    def __init__(
        self,
        panels,
        figure=None,
        sharex=False,
        sharey=False,
        adjust_figsize=True,
        label_panels=True,
        **kwargs,
    ):
        """Setup a figure and a gridspec for multi-panel plotting."""
        if isinstance(panels, int):  # Assume 1 x panels
            panels = (1, panels)
        self.panels = panels

        self.figure = figure if figure else plt.gcf()
        self._save_fig = plt.gcf()
        if isinstance(self.figure, int) and self.figure in plt.get_fignums:  # If we specified a figure as a number
            self.figure = plt.figure(self.fignum)
        if isinstance(self.figure, str) and self.figure in plt.get_figlabels:  # If we specified a figure as a label
            self.figure = plt.figure(self.fignum)

        plt.figure(self.figure)
        self.gs = None
        self.sharex = sharex
        self.sharey = sharey
        # Adjust fig size can be a tuple
        if isinstance(adjust_figsize, bool):
            adjust_figsize = (int(adjust_figsize), int(adjust_figsize) * 0.8)
        if isinstance(adjust_figsize, float):
            adjust_figsize = (adjust_figsize, adjust_figsize)
        self.adjust_figsize = adjust_figsize
        self.label_panels = "({alpha})" if isinstance(label_panels, bool) and label_panels else label_panels
        self.figsize = self.figure.get_figwidth(), self.figure.get_figheight()
        self.kwargs = kwargs

    def __enter__(self):
        """Create the grid of axes."""
        self.gs = self.figure.add_gridspec(*self.panels, **self.kwargs)
        self.axes = self.gs.subplots(sharex=self.sharex, sharey=self.sharey)
        if self.adjust_figsize:
            extra_h = self.figsize[1] * self.adjust_figsize[1] * (self.panels[1] - 1) + self.figsize[1]
            self.figure.set_figheight(extra_h)
            extra_w = self.figsize[0] * self.adjust_figsize[0] * (self.panels[0] - 1) + self.figsize[0]
            self.figure.set_figwidth(extra_w)
        if self.label_panels:
            fig = self.figure
            for ix, ax in enumerate(self):
                title_pts = ax.title.get_fontsize()
                ax_height = ax.bbox.transformed(fig.transFigure.inverted()).height * fig.get_figheight() * 72
                y = (ax_height - title_pts * 1.25) / ax_height

                ax.set_title(
                    f" {_counter(ix,self.label_panels)}", loc="left", y=y, **_filter_dict(self.kwargs, _fontargs)
                )
        return self

    def __exit__(self, type, value, traceback):
        """Clean up the axes."""
        self.figure.canvas.draw()
        plt.figure(self._save_fig)

    def __len__(self):
        """Pass through to self.axes."""
        return self.panels[0] * self.panels[1]

    def __contains__(self, value):
        """Pass through to self.axes."""
        return value in self.axes

    def __getitem__(self, index):
        """Pass through to self.axes."""
        return self.axex[index]

    def __iter__(self):
        """Iterate over self.axes."""
        yield from self.axes.ravel()

    def __refersed__(self):
        """Iterate over reversed self.axes."""
        yield from reversed(self.axes.ravel())


if __name__ == "__main__":
    pass
