# -*- coding: utf-8 -*-
"""Context Managers to help with plotting and saving figures."""
from pathlib import Path
import weakref
from collections.abc import Sequence, Iterable
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, InsetPosition

import stonerplots

__all__ = ["SavedFigure", "InsetPlot", "StackVertical", "MultiPanel", "counter", "roman"]

_fontargs = ["font", "fontfamily", "fontname", "fontsize", "fontstretch", "fontstyle", "fontvariant", "fontweight"]

_gsargs = ["left", "bottom", "right", "top", "width_ratios", "height_ratios", "hspace", "wspace", "h_pad", "w_pad"]


class _ravel_list(list):
    """A list with a ravel.method."""

    def ravel(self):
        """Implement a sort of ravel for a list."""
        ret = []
        for x in self:
            if isinstance(x, list):
                ret.extend(x)
            else:
                ret.append(x)
        return ret

    def __getitem__(self, index):
        """Fake 2D indexing with a tuple."""
        if not isinstance(index, tuple):
            return super().__getitem__(index)
        r = self
        for ix in index:
            r = r[ix]
        return r


def _filter_dict(dic, keys):
    """Return a dictionary derived from dic that only contains the keys in keys."""
    ret = {}
    for key in set(dic.keys()) & set(keys):
        ret[key] = dic[key]
    return ret


def roman(ix):
    """Return a roman numeral representation of a positive integer.

    Args:
        ix (int):
            A positive integer to be represetned as roman numerals.

    Returns:
        (str):
            *ix* in an upper case Roman numeral representation.

    Raises:
        - ValueError if *ix* is not a positive integer.

    Notes:
        The conversion routine uses the Vinculum notation (overlines) for numerals from 4000 up to a million. This
        is implemented as LaTeX codes (since the routine assumes mathtext of similar rendering is available.

        The Vinculum standard multiplies digits by 1000 above M, by adding an overline over the digit. There doesn't
        seem to be a standard way to deal with numbers bigger than 1 000 000 - presumeably Romans didn't need to do
        this very often!"""
    numerals = {
        1_000_000: "$\\overline{\\mathrm{M}}$",
        900_000: "$\\overline{\\mathrm{CM}}$",
        500_000: "$\\overline{\\mathrm{D}}$",
        400_000: "$\\pverline{\\mathrm{CD}}$",
        100_000: "$\\overline{\\mathrm{C}}$",
        90_000: "$\\overline{\\mathrm{XC}}$",
        50_000: "$\\overline{\\mathrm{L}}$",
        40_000: "$\\overbar{\\mathrm{XL}}$",
        10_000: "$\\overline{\\mathrm{X}}$",
        9_000: "$\\overline{\\mathrm{IX}}$",
        5_000: "$\\overline{\\mathrm{V}}$",
        4_000: "$\\overline{\\mathrm{IV}}$",
        1_000: "M",
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
    if not isinstance(ix, int) or ix <= 0:
        raise ValueError("Only positive integers can be represented as Roman numerals.")
    output = []
    for val, numeral in numerals.items():
        count, ix = divmod(ix, val)
        output.append(numeral * count)
    return "".join(output)


def counter(ix, pattern="({alpha})", **kargs):
    """Return a representation of an integer according to a pattern.

    Args:
        ix (int): The integer to convert to a string.

    Keyword Arguments:
        pattern (str): The pattern to be used to format the conversion. Default is '({alpha})'.
        **kargs: Other data to replace pattern with.

    Returns:
        str: ix converted to a string according to pattern.

    Notes:
        *pattern* is a standard format string with place holders in {}. It is formatted with preset representations
        of the integer *ix*
        - int - ix as an integer
        - alpha - ix as a,b,c...
        - Alpha - ix as A,B,C...
        - roman - ix as i,ii,iii,iv...
        - Roman - ix as I,II,III,IV....

    """
    if not isinstance(ix, int) or ix < 0:
        raise ValueError("ix must be a non-negative integer.")

    alpha = chr(ord("a") + ix)
    Roman = roman(ix + 1)
    replacements = {"alpha": alpha, "Alpha": alpha.upper(), "roman": Roman.lower(), "Roman": Roman, "int": ix}
    replacements.update(kargs)

    return pattern.format(**replacements)


class _Preserve_Fig(object):
    """Mixin for preserving figure and current axes."""

    def __init__(self):
        """Set instance variables."""
        self._save_fig = None
        self._save_axes = None
        super().__init__()

    def _get_gcfa(self):
        """Safely get the currenbt figure and axes without creating new ones.

        Notes:
            Checks if plt.get_fignums() is empty and if so, leaves the figure and axes unset
            Otherwise, getsa the current figure and then checks whether that has axes or not
            and if so, stores the current axes.

            The problem with naively calling plt.gcf() and plt.gca() is that they will create
            new figures and axes if they don't exist.
        """
        self._save_fig = None
        self._save_axes = None
        if not plt.get_fignums():  # No current figures
            return
        self._save_fig = plt.gcf()
        if self._save_fig.axes:
            self._save_axes = plt.gca()

    def _set_gcfa(self):
        """Set the current figure and axes from state if not None.

        This safely revets the effect of the _get_gcfa() method.
        """
        if self._save_axes:
            plt.sca(self._save_axes)
        elif self._save_fig:
            plt.figure(self._save_fig)


class SavedFigure(object):
    """Context manager that applies a style and saves figures.

    Keyword Arguments:
        filename (str, Path, default=None):
            The filename to use for saving the figure created. If None then the figure's label is used as a
            filename.
        style (str, List[str], default is `stoner`):
            The mnatplotlib syslesheet(s) to use for plotting. Multiple stylesheets can be specified either as a list
            of strings, or as a comman separated values string.
        autoclose (bool, default=False):
            Automatically close figures after they are saved. This leaves open figures that were open before we
            started,
        formats (str, list of str, default "png"):
            String or list of strings for file extensions (and hence formats) to use when saving the file. As with
            style, a comma separated values string or  a list of strings can be used to specify multiple formats.
        include_open (bool):
            If set to True (default is False), then existing figures will be included when saving.

    Notes:
        This wraps the mpl.style.context() context manager and also determines what new figures have been created and
        saves them with a soecified filename.

        *Filename* can be a directory - in which case the fiogure label will be used as the final part of the filename.
        *Filename* can also include placeholders:
            - number - the figure plot number
            - label - the fogire label
            - alpha/Alpha/roman/Roman/int - a counter that increases for each saved file in the current with:... block.

        SavedFigure supports reuse - so can do somethingf like.::

            cm = SavedFigure(filename="figures/fig_{label}.png",
                             style="stoiner,thesis", autoclose=True)
            with cm:
                plt.figure("one")
                ....

            with cm:
                plt.figure("two")

        and get `figures/fig_one.png` and `figures/fig_two.png` with a consistent styling.

        SavedFigure objects can be called with the same parameters as the consuctor to upadte their settings.::

            cm = SavedFigure(filename="figures/fig_{label}.png",
                             style="stoiner,thesis", autoclose=True)
            with cm:
                plt.figure("one")
                ....

            with cm(fprmats=["pdf","png"!]):
                plt.figure("two")

        Would do the same as above, but also creater `figures/fig_two.pdf`.
    """

    _keys = ["filename", "style", "autoclose", "formats", "include_open"]

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
        # Set internal state
        self._filename = None
        self._formats = []
        self._style = []
        self._open_figs = []
        # Copy constrictor parameters
        self.filename = filename
        self.style = style
        self.autoclose = autoclose
        self.style_context = None
        self.formats = formats
        self.include_open = include_open

    @property
    def filename(self):
        """Store the filename as a Path object without an extension."""
        return self._filename

    @filename.setter
    def filename(self, value):
        if value is not None:
            value = Path(value)
            ext = value.suffix[1:]
            if ext not in self.formats:
                self.formats.append(ext)
            value = value.parent / value.stem
        self._filename = value

    @property
    def formats(self):
        """Store the output formats as a list of strings"""
        return self._formats

    @formats.setter
    def formats(self, value):
        """Ensure formats is a list of strings."""
        if isinstance(value, str):
            self._formatrs = [x.strip() for x in value.split(",") if x.strip() != ""]
        elif isinstance(value, Iterable):
            self._formats = list(value)
        elif value is None:
            if len(self._formats) == 0:
                self._formats = ["png"]
        else:
            raise TypeError("Cannot workout format type")

    @property
    def style(self):
        """Store the stylesheets as a list of strings."""
        return self._style

    @style.setter
    def style(self, value):
        """Ensure style is a list of strings."""
        if isinstance(value, str):
            self._style = [x.strip() for x in value.split(",") if x.strip() != ""]
        elif isinstance(value, Iterable):
            self._style = list(value)
        elif value is None:
            self._style = ["stoner"]
        else:
            raise TypeError("Cannot workout style type")

    def __cal__(self, **kwargs):
        """Update the settings and return ourself."""
        settings = _filter_dict(kwargs, self.keys)
        for key, val in settings.items():
            setattr(self, key, val)
        return self

    def __enter__(self):
        """Record the open figures and start the style context manager.

        Creates a list of weak references to all the open figures. This is then used to detect whether an open figure
        has been created within the context manager or not. We use weak references to allow figures to be closed
        without blocking.
        """
        for num in plt.get_fignums():
            if not self.include_open:
                self._open_figs.append(weakref.ref(plt.figure(num)))
        if self.style:
            self.style_context = mpl.style.context(self.style)
            self.style_context.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        """Cleanup context manager and save figures created.

        First call the __exit__ of the style context manager to finish plotting with the specified stylesheet, then
        check all the open figures and if they were not in our list of figures open before, save them with a filename
        from the keyword parameter to __init__ or the plot label.
        """
        if self.style:
            self.style_context.__exit__(exc_type, exc_value, traceback)

        self._open_figs = [fig() for fig in self._open_figs if fig() is not None]
        processed = -1

        for num in plt.get_fignums():
            fig = plt.figure(num)
            if fig in self._open_figs:
                continue

            processed += 1
            label = fig.get_label()
            filename = self._generate_filename(label, processed)
            self._save_figure(fig, filename, processed)
            if self.autoclose:
                plt.close(num)

        self._reset_state()

    def _generate_filename(self, label, processed):
        """Generate the filename for the figure."""
        if self.filename.is_dir():
            filename = self.filename / "{label}"
        else:
            filename = self.filename or Path("{label}")

        return filename

    def _save_figure(self, fig, filename, processed):
        """Save the figure in the specified formats."""
        for fmt in self.formats:
            new_file = filename.parent / f"{filename.stem}.{fmt.lower()}"
            new_file = counter(processed, str(new_file), number=fig.number, label=fig.get_label())

            if new_file == filename and processed > 0:
                parts = new_file.split(".")
                parts[-2] += f"-{processed}"
                new_file = ".".join(parts)

            fig.savefig(new_file)

    def _reset_state(self):
        """Reset the internal state of the context manager."""
        self._open_figs = []
        self.style_context = None


class InsetPlot(_Preserve_Fig):
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

    def __init__(
        self,
        ax=None,
        loc="upper left",
        width=0.25,
        height=0.25,
        dimension="fraction",
        switch_to_inset=True,
        padding=0.05,
    ):
        """Set the location for the axes."""
        super().__init__()
        self._ax = ax
        self._loc = loc
        if dimension == "fraction":
            if isinstance(height, float) and 0.0 < height <= 1.0:
                height = f"{height*100:.0f}%"
            if isinstance(width, float) and 0.0 < width <= 1.0:
                width = f"{width*100:.0f}%"
        self.height = height
        self.width = width
        self.padding = padding
        self.switch_to_inset = switch_to_inset

    def __enter__(self):
        """Create the inset axes using the axes_grid toolkit."""
        self._get_gcfa()  # Note the current figure and axes safely
        if self._ax is None:  # Use current axes if not passed explicitly
            self.ax = plt.gca()
        else:
            self.ax = self.ax
        if not isinstance(self._loc, int):
            self.loc = self.locations.get(str(self._loc).lower().replace("-", " "), 1)
        else:
            self.loc = self._loc
        axins = inset_axes(self.ax, width=self.width, height=self.height, loc=self.loc)
        self.axins = axins
        if self.switch_to_inset:
            plt.sca(axins)
        return self.axins

    def __exit__(self, type, value, traceback):
        """Reposition the inset as the standard positioning can cause labels to overlap."""
        parent_bbox = self.ax.get_position()
        inset_bbox = self.axins.get_tightbbox().transformed(self.ax.figure.transFigure.inverted())
        inset_axes_bbox = self.axins.get_position()

        dx0, dy0, rw, rh = self._calculate_dimensions(parent_bbox, inset_bbox, inset_axes_bbox)
        x0, y0 = self._calculate_position(dx0, dy0, rw, rh)

        newpos = InsetPosition(self.ax, [x0, y0, rw, rh])
        self.axins.set_axes_locator(newpos)
        self.ax.figure.canvas.draw()

        if self.switch_to_inset:
            self._set_gcfa()

    def _calculate_dimensions(self, parent_bbox, inset_bbox, inset_axes_bbox):
        """Calculate the dimensions for inset positioning."""
        dx0 = (inset_axes_bbox.x0 - inset_bbox.x0) / parent_bbox.width  # X axes label space
        dy0 = inset_axes_bbox.y0 - inset_bbox.y0 / parent_bbox.height  # Y axes label space
        rw = inset_bbox.width / parent_bbox.width
        rh = inset_bbox.height / parent_bbox.height
        return dx0, dy0, rw, rh

    def _calculate_position(self, dx0, dy0, rw, rh):
        """Calculate the position based on the location."""
        if self.loc == 1:  # Upper right
            return 1 - rw - self.padding, 1 - rh - self.padding
        elif self.loc == 2:  # Upper left
            return dx0 + self.padding, 1 - rh - self.padding
        elif self.loc == 3:  # Lower left
            return dx0 + self.padding, dy0 + self.padding
        elif self.loc == 4:  # Lower right
            return 1 - rw - self.padding, dy0 + self.padding
        elif self.loc in [5, 7]:  # Right
            return 1 - rw - self.padding, (1 - rh) / 2
        elif self.loc == 6:  # Center left
            return dx0 + self.padding, (1 - rh) / 2
        elif self.loc == 8:  # Lower center
            return (1 - rw) / 2, dy0 + self.padding
        elif self.loc == 9:  # Upper center
            return dx0 + self.padding, 1 - rh - self.padding
        elif self.loc == 10:  # Center
            return (1 - rw) / 2, (1 - rh) / 2
        return 0, 0  # Default case if location is not matched


class _PlotContextSequence(Sequence):
    """Base class for Plot Context Managers that deals with Sequence Like Behaviour."""

    def __init__(self):
        """Ensure private  attributes exist."""
        self.axes = _ravel_list()
        self._save_fig = None
        self._save_axes = None

    def __len__(self):
        """Pass through to self.axes.

        Note:
            self.axes may be a _ravel_list - so unravel the list first.
        """
        return len(self.axes.ravel())

    def __contains__(self, value):
        """Pass through to self.axes.

        Note:
            self.axes may be a _ravel_list - so unravel the list first.
        """
        return value in self.axes.ravel()

    def __getitem__(self, index):
        """Pass through to self.axes.

        Notes:
            If the result is a single axes instance, then call :py:func:`matplotlib.pyplot.sca`
            with it.
        """
        ret = self.axes[index]
        if isinstance(ret, mpl.axes.Axes):
            plt.sca(ret)
        return ret

    def __iter__(self):
        """Iterate over self.axes.

        Note:
            self.axes may be a _ravel_list - so unravel the list first.
        """
        for ax in self.axes.ravel():
            plt.sca(ax)
            yield ax

    def __reversed__(self):
        """Iterate over reversed self.axes.

        Note:
            self.axes may be a _ravel_list - so unravel the list first.
        """
        yield from reversed(self.axes.ravel())

    def _get_gcfa(self):
        """Safely get the currenbt figure and axes without creating new ones.

        Notes:
            Checks if plt.get_fignums() is empty and if so, leaves the figure and axes unset
            Otherwise, getsa the current figure and then checks whether that has axes or not
            and if so, stores the current axes.

            The problem with naively calling plt.gcf() and plt.gca() is that they will create
            new figures and axes if they don't exist.
        """
        self._save_fig = None
        self._save_axes = None
        if not plt.get_fignums():  # No current figures
            return
        self._save_fig = plt.gcf()
        if self._save_fig.axes:
            self._save_axes = plt.gca()

    def _set_gcfa(self):
        """Set the current figure and axes from state if not None.

        This safely revets the effect of the _get_gcfa() method.
        """
        if self._save_axes:
            plt.sca(self._save_axes)
        elif self._save_fig:
            plt.figure(self._save_fig)


class MultiPanel(_PlotContextSequence, _Preserve_Fig):
    """A context manager for sorting out multi-panel plots in matplotlib.

    Args:
        panels (tuple[int.int],int, List[int]):
            Nunber of sub-plots to produce.
            - tuple(rows, columns) - regular grid of rows and coluimns
            - int - Make a grid of 1 row and n columns
            - list(columns per row) - make an irregular grid of different numbers of plots on each row.

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
        same_aspect (bool):
            If *nnplots* is in use then the aspect ratio of each plot will be adjusted to be the same unless you
            set this to be False, or unless you pass *width_ratios* or *height_ratios* to control the aspect ratios.
        transpose (bool):
            If True, then transpose the rows and columns if panels is a tuple. If panels is a list, then assume that
            the list specifies the number of rows in each column rather than the default of assuming if is the number
            of columns in each row.

        kwargs:
            Other keyword arguments can be used to set the label fonts and are passed into ax.set_title, arguments
            for GridSpec are passed to fig.add_gridspec.

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
        same_aspect=True,
        transpose=False,
        **kwargs,
    ):
        """Configure figure and a gridspec for multi-panel plotting."""
        super().__init__()
        if isinstance(panels, int):  # Assume 1 x panels
            panels = (1, panels)
        self.panels = panels
        self._fig_arg = figure
        self.gs = None
        self.sharex = sharex
        self.sharey = sharey
        self._adjust_figsize_arg = adjust_figsize
        self.transpose = transpose
        # Adjust fig size can be a tuple
        self.label_panels = "({alpha})" if isinstance(label_panels, bool) and label_panels else label_panels
        self.kwargs = kwargs
        self.same_aspect = "height_ratios" not in kwargs and "wdith_ratios" not in kwargs and same_aspect
        if "nplots" in self.kwargs:
            raise DeprecationWarning(
                "nplots aregument is depricated. Pass the same value directly as the number of panels now."
            )
            self.panels = self.kwargs.pop("nplots")

    def __enter__(self):
        """Create the grid of axes."""
        self._get_gcfa()
        self._set_figure()
        self._adjust_figure_size()
        self._create_gridspec()
        self._label_subplots()
        return self

    def __exit__(self, type, value, traceback):
        """Clean up the axes."""
        self.figure.canvas.draw()
        if self.same_aspect:  # Force the aspect ratios to be the same
            asp = np.array([ax.bbox.width / ax.bbox.height for ax in self.axes.ravel()]).min()
            for ax in self.axes.ravel():
                ax.set_box_aspect(1 / asp)

        self._set_gcfa()

    def _set_figure(self):
        """Set the figure based on the provided figure argument or the current figure."""
        self.figure = self._fig_arg or plt.gcf()
        if isinstance(self.figure, int):
            self.figure = plt.figure(self.figure)
        elif isinstance(self.figure, str):
            self.figure = plt.figure(self.figure)
        plt.figure(self.figure)

    def _adjust_figure_size(self):
        """Adjust the figure size if necessary."""
        adjust_figsize = self._adjust_figsize_arg
        if isinstance(adjust_figsize, bool):
            adjust_figsize = (int(adjust_figsize), int(adjust_figsize) * 0.8)
        elif isinstance(adjust_figsize, float):
            adjust_figsize = (adjust_figsize, adjust_figsize)
        self.adjust_figsize = adjust_figsize
        self.figsize = self.figure.get_figwidth(), self.figure.get_figheight()

    def _create_gridspec(self):
        """Create the gridspec for the subplots."""
        if isinstance(self.panels, int):
            self._create_subplots((1, self.panels) if not self.transpose else (self.panels, 1))
        elif isinstance(self.panels, list):
            self._create_subplots(
                (
                    (len(self.panels), np.prod(np.unique(self.panels)))
                    if not self.transpose
                    else (np.prod(np.unique(self.panels)), len(self.panels))
                ),
                self.panels,
            )
        elif isinstance(self.panels, tuple):
            self._create_subplots(self.panels)
        else:
            raise TypeError(f"Unable to interpret the number of panels to create: {self.panels}")
        if self.adjust_figsize:
            self._do_figure_adjustment()

    def _label_subplots(self):
        """Label the subplots if necessary."""
        if self.label_panels:
            self._label_figure()

    def _create_subplots(self, panels, nplots=None):
        """Create the subplots for the given panels."""
        gs_kwargs = _filter_dict(self.kwargs, _gsargs)
        self.gs = self.figure.add_gridspec(*panels, **gs_kwargs)
        self.axes = _ravel_list([])

        if nplots is not None:
            used = np.zeros(panels, dtype=bool)
            for r in range(panels[0]):
                row_axes = []
                for c in range(panels[1]):
                    if used[r, c]:
                        continue  # already taken this subplot
                    extent = self._calculate_extent(panels, nplots, r, c)
                    self._mark_used(used, r, c, extent)
                    subplot = self._create_subplot(r, c, extent)
                    row_axes.append(subplot)
                self.axes.append(row_axes)
        else:
            self.axes = self.gs.subplots(sharex=self.sharex, sharey=self.sharey)

    def _calculate_extent(self, panels, nplots, r, c):
        """Calculate the extent of the subplot."""
        if self.transpose:
            return panels[0] // nplots[c]
        return panels[1] // nplots[r]

    def _mark_used(self, used, r, c, extent):
        """Mark the used subplots in the grid."""
        if self.transpose:
            used[r : r + extent, c] = True
        else:
            used[r, c : c + extent] = True

    def _create_subplot(self, r, c, extent):
        """Create a subplot for the given row, column, and extent."""
        if self.transpose:
            return self.figure.add_subplot(self.gs[r : r + extent, c])
        return self.figure.add_subplot(self.gs[r, c : c + extent])

    def _do_figure_adjustment(self):
        """Adjust the figure size based on the adjust_figsize setting."""
        extra_width = self._calculate_dimension(self.figsize[0], self.adjust_figsize[0], self.panels[1])
        extra_height = self._calculate_dimension(self.figsize[1], self.adjust_figsize[1], self.panels[0])
        self.figure.set_figwidth(extra_width)
        self.figure.set_figheight(extra_height)

    def _calculate_dimension(self, base_size, factor, panels_count):
        """Calculate the extra dimension (width or height) based on the factor and panels count."""
        if factor < 0:
            return base_size * (1 + factor)
        return base_size * factor * (panels_count - 1) + base_size

    def _label_figure(self):
        """Do the subplot figure labelling."""
        fig = self.figure
        for ix, ax in enumerate(self):
            title_pts = ax.title.get_fontsize()
            ax_height = ax.bbox.transformed(fig.transFigure.inverted()).height * fig.get_figheight() * 72
            y = (ax_height - title_pts * 1.5) / ax_height

            ax.set_title(f" {counter(ix,self.label_panels)}", loc="left", y=y, **_filter_dict(self.kwargs, _fontargs))


class StackVertical(MultiPanel):
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
            Other keyword arguments can be used to set the label fonts and are passed into ac.set_title and gridspec
            arguments are passed to fig.add_gridspec.

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
        self._fig_tmp = figure
        self.gs = None
        self.sharex = sharex
        self.sharey = sharey
        self.hspace = 0 if self.joined else self.kwargs.pop("hspace", 0.1)
        self.adjust_figsize = adjust_figsize if isinstance(adjust_figsize, float) else float(int(adjust_figsize)) * 0.8
        self.label_panels = "({alpha})" if isinstance(label_panels, bool) and label_panels else label_panels
        self.align_labels = kwargs.pop("align__labels", True)
        self.kwargs = kwargs

    def __enter__(self):
        """Create the grid of axes."""

        panels = (self.number, 1)
        super().__init__(
            panels,
            figure=self._fig_tmp,
            sharex=self.sharex,
            sharey=self.sharey,
            adjust_figsize=self.adjust_figsize,
            label_panels=self.label_panels,
            same_aspect=False,
            **self.kwargs,
        )

        return super().__enter__()

    def __exit__(self, type, value, traceback):
        """Clean up the axes."""
        if self.joined:
            self._label_outer_axes()
            plt.draw()
            self._adjust_limits_for_axes()
            self._adjust_layout_engine()

        self._align_labels()
        self.figure.canvas.draw()
        self._set_gcfa()

    def _label_outer_axes(self):
        """Label outer axes."""
        for ax in self.axes:
            ax.label_outer()

    def _adjust_limits_for_axes(self):
        """Adjust y-limits for all axes."""
        for ix, ax in enumerate(self.axes):
            self._fix_limits(ix, ax)

    def _adjust_layout_engine(self):
        """Adjust the layout engine settings."""
        eng = self.figure.get_layout_engine()
        rect = list(eng.get()["rect"])
        h = self.figure.get_figheight()
        boundary = 0.05 / h
        rect[1] = boundary if rect[1] == 0 else rect[1]
        rect[3] = 1 - 2 * boundary if rect[3] == 1 else rect[3]
        self.figure.get_layout_engine().set(h_pad=0.0, hspace=0.0, rect=rect)

    def _align_labels(self):
        """Align y-axist labels."""
        if not self.align_labels:
            return
        label_pos = []
        for ax in self.axes:
            tr = ax.transAxes.inverted() + ax.yaxis.label.get_transform()
            label_pos.append(tr.transform(ax.yaxis.label.get_position())[0])
        label_pos = min(label_pos)
        for ax in self.axes:
            ax.yaxis.set_label_coords(label_pos, 0.5)

    def _fix_limits(self, ix, ax):
        """Adjust y-limits so labels are inside the axes frame."""
        dy = self._calculate_dy(ax)
        ylim = list(ax.get_ylim())
        tr = ax.transData + ax.transAxes.inverted()  # Transform Data to Axes
        yticks = self._get_yticks_in_axes_units(ax, tr)

        if yticks[1] < dy and ix != len(self.axes) - 1:  # Adjust range of plots except bottom one
            ylim[0] = self._adjust_ylim_lower(tr, -dy)
        if yticks[-2] < 1.0 - dy and ix != 0:  # Adjust range of plots except top one.
            ylim[1] = self._adjust_ylim_upper(tr, 1 + dy)
        ax.set_ylim(ylim)
        self.figure.canvas.draw()

    def _calculate_dy(self, ax):
        """Calculate the space needed in axes units for the label."""
        fnt_pts = ax.yaxis.get_ticklabels()[0].get_fontsize()
        ax_height = ax.bbox.transformed(self.figure.transFigure.inverted()).height * self.figure.get_figheight() * 72
        return fnt_pts / ax_height

    def _get_yticks_in_axes_units(self, ax, tr):
        """Get y-tick locations in axes units."""
        return [tr.transform((0, x))[1] for x in ax.get_yticks()]

    def _adjust_ylim_lower(self, tr, dy):
        """Adjust the lower y-limit."""
        return tr.inverted().transform((0, dy))[1]

    def _adjust_ylim_upper(self, tr, dy):
        """Adjust the upper y-limit."""
        return tr.inverted().transform((0, dy))[1]


if __name__ == "__main__":
    pass
