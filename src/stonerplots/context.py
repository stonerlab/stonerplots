# -*- coding: utf-8 -*-
"""Context Managers to help with plotting and saving figures."""
# Standard library imports
import warnings
import weakref
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, List, Union

# Third-party imports
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from .util import find_best_position, move_inset, new_bbox_for_loc, copy_properties

__all__ = ["SavedFigure", "InsetPlot", "StackVertical", "MultiPanel", "counter", "roman"]

# Constants
_fontargs = ["font", "fontfamily", "fontname", "fontsize", "fontstretch", "fontstyle", "fontvariant", "fontweight"]
_gsargs = ["left", "bottom", "right", "top", "width_ratios", "height_ratios", "hspace", "wspace", "h_pad", "w_pad"]

ROMAN_NUMERAL_MAP = {
    1_000_000: "$\\overline{\\mathrm{M}}$",
    900_000: "$\\overline{\\mathrm{CM}}$",
    500_000: "$\\overline{\\mathrm{D}}$",
    400_000: "$\\overline{\\mathrm{CD}}$",
    100_000: "$\\overline{\\mathrm{C}}$",
    90_000: "$\\overline{\\mathrm{XC}}$",
    50_000: "$\\overline{\\mathrm{L}}$",
    40_000: "$\\overline{\\mathrm{XL}}$",
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


class _RavelList(list):
    """A list with additional flattening and fake 2D indexing capabilities.

    This class extends the standard list to provide additional functionalities for
    flattening nested lists and supporting 2D-style indexing.

    Methods:
        flatten(): Flattens a nested list into a single-level list.
        _flatten_recursive(items): Recursively flattens a list.
        __getitem__(index): Supports 2D-style indexing using tuples.
    """

    def flatten(self) -> List[Any]:
        """Flattens a nested list into a single-level list.

        Returns:
            List[Any]: A flattened list.

        Examples:
            >>> lst = _RavelList([[1, 2], [3, 4]])
            >>> lst.flatten()
            [1, 2, 3, 4]
        """
        return self._flatten_recursive(self)

    @staticmethod
    def _flatten_recursive(items: Union[list, Any]) -> List[Any]:
        """Help to recursively flatten a list.

        Args:
            items (Union[list, Any]): The list (or single item) to flatten.

        Returns:
            List[Any]: A flattened list.

        Examples:
            >>> _RavelList._flatten_recursive([[1, 2], [3, [4, 5]]])
            [1, 2, 3, 4, 5]
        """
        return [element for sublist in items for element in (sublist if isinstance(sublist, list) else [sublist])]

    def __getitem__(self, index: Union[int, tuple]) -> Any:
        """2D-style indexing using tuples.

        Args:
            index (Union[int, tuple]): Index or tuple of indices.

        Returns:
            Any: Element at the specified index.

        Examples:
            >>> lst = _RavelList([[1, 2], [3, 4]])
            >>> lst[0, 1]
            2
        """
        if not isinstance(index, tuple):
            return super().__getitem__(index)
        result = self
        for ix in index:
            result = result[ix]
        return result


# Functions
def _filter_keys_in_dict(dic, keys):
    """Filter a dictionary to only include specified keys.

    Args:
        dic (dict): The dictionary to filter.
        keys (iterable): The keys to retain in the dictionary.

    Returns:
        dict: A new dictionary containing only the specified keys.
    """
    return {key: dic[key] for key in keys if key in dic}


def roman(number):
    """Convert a positive integer to Roman numeral representation.

    Args:
        number (int): A positive integer.

    Returns:
        str: The number represented as an upper-case Roman numeral string.

    Raises:
        ValueError: If the input is not a positive integer.
    """
    if not isinstance(number, int) or number <= 0:
        raise ValueError("Only positive integers can be represented as Roman numerals.")

    result = ""
    for value, numeral in ROMAN_NUMERAL_MAP.items():
        count = number // value
        if count:
            result += numeral * count
            number -= count * value
    return result


def counter(value, pattern="({alpha})", **kwargs):
    r"""Format an integer as a string using a pattern and various representations.

    Args:
        value (int): The integer to format.
        pattern (str): A format string with placeholders (default: '({alpha})').
        \*\*kwargs: Additional data to replace placeholders.

    Returns:
        str: The formatted string.
    """
    alpha = chr(ord("a") + value)  # Lowercase alphabet representation
    Roman = roman(value + 1)  # Uppercase Roman numeral
    return pattern.format(alpha=alpha, Alpha=alpha.upper(), roman=Roman.lower(), Roman=Roman, int=value, **kwargs)


class _TrackNewFiguresAndAxes:
    """A simple context manager to handle identifying new figures or axes.

    This context manager tracks figures and axes created within its context, allowing
    for operations on only the new figures and axes.

    Args:
        include_open (bool): If `True`, includes already open figures and axes. Defaults to `False`.

    Attributes:
        _existing_open_figs (list): List of weak references to existing open figures.
        _existing_open_axes (dict): Dictionary of weak references to existing open axes.

    Methods:
        new_figures: Returns an iterator over figures created since the context was entered.
        new_axes: Returns an iterator over axes created since the context was entered.
    """

    def __init__(self, *args, **kwargs):
        """Set storage of figures and axes.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            include_open (bool): If `True`, includes already open figures and axes. Defaults to `False`.
        """
        super().__init__()
        self._existing_open_figs = []
        self._existing_open_axes = {}
        self.include_open = kwargs.pop("include_open", False)

    def __enter__(self):
        """Record any already open figures and axes."""
        for num in plt.get_fignums():
            if not self.include_open:
                self._existing_open_figs.append(weakref.ref(plt.figure(num)))
                self._existing_open_axes[num] = [weakref.ref(ax) for ax in plt.figure(num).axes]

    @property
    def new_figures(self):
        """Return an iterator over figures created since the context manager was entered.

        Yields:
            matplotlib.figure.Figure: New figures created within the context.

        Examples:
            >>> with _TrackNewFiguresAndAxes() as tracker:
            ...     plt.figure()
            ...     # New figure created here
            >>> list(tracker.new_figures)
            [<Figure size ...>]
        """
        for num in plt.get_fignums():
            fig = plt.figure(num)
            if fig in self._existing_open_figs:  # Skip figures opened before context
                continue
            yield fig

    @property
    def new_axes(self):
        """Return an iterator over all new axes created since the context manager was entered.

        Yields:
            matplotlib.axes.Axes: New axes created within the context.

        Examples:
            >>> with _TrackNewFiguresAndAxes() as tracker:
            ...     fig, ax = plt.subplots()
            ...     # New axes created here
            >>> list(tracker.new_axes)
            [<AxesSubplot:...>]
        """
        for num in plt.get_fignums():
            fig = plt.figure(num)
            for ax in fig.axes:
                if ax in self._existing_open_axes:  # Skip figures opened before context
                    continue
                yield ax

    def __exit__(self, exc_type, exc_value, traceback):
        """Clean up the saved figures and axes."""
        self._existing_open_figs = []
        self._existing_open_axes = {}


class _PreserveFigureMixin:
    """Mixin for preserving the current figure and axes."""

    _UNSET = None  # Constant representing the unset state

    def __init__(self):
        """Initialize figure and axes preservation attributes."""
        self._saved_figure = self._UNSET
        self._saved_axes = self._UNSET
        super().__init__()

    def _store_current_figure_and_axes(self):
        """Safely store the current figure and axes without creating new ones.

        Notes:
            - If no figures exist, both figure and axes remain unset.
            - If a figure exists, stores it, and checks whether it has axes.
        """
        self._saved_figure, self._saved_axes = self._UNSET, self._UNSET

        if plt.get_fignums():  # Check if any figures exist
            self._saved_figure = plt.gcf()
            if self._saved_figure.axes:  # Check if the current figure has axes
                self._saved_axes = plt.gca()

    def _restore_current_figure_and_axes(self):
        """Restore the saved figure and axes if previously set.

        Safely reverses the effect of `_store_current_figure_and_axes`.
        """
        if self._saved_axes is not self._UNSET:
            plt.sca(self._saved_axes)  # Restore current axes
        elif self._saved_figure is not self._UNSET:
            plt.figure(self._saved_figure)  # Restore current figure


class _PlotContextSequence(Sequence):
    """A context manager that provides sequence-like access and operations for Matplotlib axes.

    The `_PlotContextSequence` class is designed to handle multiple Matplotlib axes effectively
    and provides utilities for accessing, iterating, and managing axes in a sequence-like
    manner. It ensures that actions like iteration or item access automatically handle the
    current Matplotlib axes state, making it easier to work with complex plots.

    This class integrates with Matplotlib's state machine to ensure that the "current" figure
    and axes are updated automatically when individual axes are accessed or iterated over.

    Attributes:
        axes (list):
            A list containing Matplotlib axes objects for sequential access.
        _save_fig (Optional[matplotlib.figure.Figure]):
            Holds a reference to the current Matplotlib figure, if any, during context-saving operations.
        _save_axes (Optional[matplotlib.axes.Axes]):
            Holds a reference to the current Matplotlib axes, if any, during context-saving operations.

    Notes:
        - The class includes a set of sequence-like operations (`__getitem__`, `__iter__`, etc.)
          that are seamlessly integrated with the current Matplotlib state.
        - The `ravel` operator is used internally to manage and flatten nested axes structures.
        - Accessing an individual axis automatically updates Matplotlib to treat it as the "current" axis.

    Examples:
        Accessing and iterating over axes:

        >>> sequence = _PlotContextSequence()
        >>> for ax in sequence:
        >>>     ax.plot([1, 2, 3], [4, 5, 6])

        Checking if an axis is in the sequence:

        >>> ax in sequence  # Returns True/False

        Retrieving a specific axis and setting it as the current axis:

        >>> specific_ax = sequence[0]
    """

    _NO_FIGURES_MSG = "No current figures exist."

    def __init__(self):
        """Initialize class and ensure private attributes exist."""
        self.axes = _RavelList()
        self._save_fig = None
        self._save_axes = None

    @property
    def raveled_axes(self):
        """Unravel and provide the flattened list of axes."""
        return self.axes.flatten()

    def __len__(self):
        """Return the number of axes."""
        return len(self.raveled_axes)

    def __contains__(self, value):
        """Check if a value is contained within the axes."""
        return value in self.raveled_axes

    def __getitem__(self, index):
        """Get axis item at index and optionally set it as current."""
        ret = self.axes[index]
        self._check_single_axis_selection(ret)
        return ret

    def __iter__(self):
        """Iterate over the axes and set each as current when iterating."""
        for ax in self.raveled_axes:
            plt.sca(ax)
            yield ax

    def __reversed__(self):
        """Iterate in reverse over the axes and set each as current."""
        yield from reversed(self.raveled_axes)

    def _check_single_axis_selection(self, ret):
        """If the result is a single axis, set it as the current axis."""
        if isinstance(ret, mpl.axes.Axes):
            plt.sca(ret)

    def _save_current_fig_and_axes(self):
        """Safely save the current figure and axes without creating new ones."""
        self._save_fig = None
        self._save_axes = None
        if not plt.get_fignums():  # No current figures
            return
        self._save_fig = plt.gcf()
        if self._save_fig.axes:
            self._save_axes = plt.gca()

    def _restore_saved_fig_and_axes(self):
        """Restore the saved figure and axes, if not None."""
        if self._save_axes:
            plt.sca(self._save_axes)
        elif self._save_fig:
            plt.figure(self._save_fig)


class SavedFigure(_TrackNewFiguresAndAxes, _PreserveFigureMixin):
    """A context manager for applying plotting styles and saving matplotlib figures.

    This class simplifies the process of managing figure styling and saving multiple figures
    within a single context. It allows for automatic application of matplotlib stylesheets and
    handles the generation of unique filenames for figures, taking into account user-provided
    templates and output formats. SavedFigure can be reused across multiple `with` blocks,
    and its settings can dynamically be reconfigured by calling the instance with new parameters.

    Args:
        filename (str, Path, None):
            The base filename or target directory for saving figures.
            - If `filename` is a directory, the figure's label is used to generate the filename.
            - If `filename` includes placeholders (e.g., `{label}`, `{number}`), they will be replaced dynamically.
        style (list[str], str, None):
            One or more matplotlib stylesheets to apply. If a single string is provided, it is split by commas
            to form a list of styles. Defaults to ["stoner"].
        autoclose (bool):
            Determines whether figures should be closed automatically after being saved. Default is `False`.
        formats (str, list[str], None):
            The output file formats for saved figures (e.g., "png", "pdf"). Can be a comma-separated string,
            a list of strings, or `None` (default: ["png"]).
        include_open (bool):
            If `True`, any figures opened before entering the context are included for saving. Default is `False`.

    Attributes:
        filename (Path):
            A property representing the base filename or directory for saving figures.
        formats (list[str]):
            A list of file formats to save the figures (e.g., ["png", "pdf"]).
        style (list[str]):
            A list of stylesheets to apply to the figures.
        autoclose (bool):
            Indicates whether figures are closed after being saved.
        include_open (bool):
            Determines whether figures already open before entering the context are saved.

    Notes:
        - `SavedFigure` can identify and save only the new figures created while inside its context, unless
          `include_open` is set to `True`.
        - `filename` and `formats` parameters support dynamic placeholders:
          - `{number}`: Figure number.
          - `{label}`: Figure label.
          - `{alpha}`, `{Alpha}`: Counter in lowercase or uppercase.
          - `{roman}`, `{Roman}`: Roman numeral (lowercase/uppercase).
        - Files are automatically numbered if placeholders are missing and multiple figures are created.

    Examples:
        Saving two figures in the same context:

        >>> cm = SavedFigure(filename="plots/figure_{label}.png", style="default", autoclose=True)
        >>> with cm:
        ...     plt.figure("plot1")
        ...     plt.plot([1, 2, 3], [4, 5, 6])
        ...     plt.show()
        ...     plt.figure("plot2")
        ...     plt.plot([7, 8, 9], [10, 11, 12])
        ...     plt.show()

        After exiting the context, SavedFigure will save:
        - plots/figure_plot1.png
        - plots/figure_plot2.png

        Dynamically updating SavedFigure settings during reuse:

        >>> with cm(formats=["pdf", "png"]):
        ...     plt.figure("plot3")
        ...     plt.plot([3, 4, 5], [9, 8, 7])
        ...     plt.show()

        This saves:
        - plots/figure_plot3.pdf
        - plots/figure_plot3.png
    """

    _keys = ["filename", "style", "autoclose", "formats", "include_open"]

    def __init__(self, filename=None, style=None, autoclose=False, formats=None, include_open=False):
        """Initialize with default settings."""
        # Internal state initialization
        super().__init__(include_open=False)
        self._filename = None
        self._formats = []
        self._style = []

        # Parameter assignment
        self.filename = filename
        self.style = style
        self.autoclose = autoclose
        self.style_context = None
        self.formats = formats

    @property
    def filename(self):
        """Return filename as a Path object without extension.

        Returns:
            Path: The filename or directory path.

        Examples:
            >>> sf = SavedFigure(filename="plot.png")
            >>> sf.filename
            PosixPath('plot')
        """
        return self._filename

    @filename.setter
    def filename(self, value):
        """Set filename and extract its extension if valid.

        Args:
            value (Union[str, Path]): The filename or directory path.

        Examples:
            >>> sf = SavedFigure()
            >>> sf.filename = "plot.png"
            >>> sf.filename
            PosixPath('plot')
        """
        if value is not None:
            value = Path(value)
            ext = value.suffix[1:]
            if ext and ext not in self.formats:
                self.formats.append(ext)
            value = value.parent / value.stem
        self._filename = value

    @property
    def formats(self):
        """Return the output formats as a list of strings.

        Returns:
            list[str]: The list of output formats.

        Examples:
            >>> sf = SavedFigure(formats="png,pdf")
            >>> sf.formats
            ['png', 'pdf']
        """
        return self._formats

    @formats.setter
    def formats(self, value):
        """Ensure formats are stored as a list of strings.

        Args:
            value (Union[str, Iterable[str], None]): The formats to store.

        Raises:
            TypeError: If the value is not str, iterable, or None.

        Examples:
            >>> sf = SavedFigure()
            >>> sf.formats = "png,pdf"
            >>> sf.formats
            ['png', 'pdf']
        """
        if isinstance(value, str):
            self._formats = [x.strip() for x in value.split(",") if x.strip()]
        elif isinstance(value, Iterable):
            self._formats = list(value)
        elif value is None:
            if not self._formats:  # Use default if formats aren't set
                self._formats = ["png"]
        else:
            raise TypeError("Invalid type for formats. Expected str, iterable, or None.")

    @property
    def style(self):
        """Return the stylesheets as a list of strings.

        Returns:
            list[str]: The list of stylesheets.

        Examples:
            >>> sf = SavedFigure(style="default")
            >>> sf.style
            ['default']
        """
        return self._style

    @style.setter
    def style(self, value):
        """Ensure style is stored as a list of strings.

        Args:
            value (Union[str, Iterable[str], None]): The styles to store.

        Raises:
            TypeError: If the value is not str, iterable, or None.

        Examples:
            >>> sf = SavedFigure()
            >>> sf.style = "default,ggplot"
            >>> sf.style
            ['default', 'ggplot']
        """
        if isinstance(value, str):
            self._style = [x.strip() for x in value.split(",") if x.strip()]
        elif isinstance(value, Iterable):
            self._style = list(value)
        elif value is None:
            self._style = ["stoner"]
        else:
            raise TypeError("Invalid type for style. Expected str, iterable, or None.")

    def __call__(self, **kwargs):
        """Update settings dynamically and return self."""
        settings = {key: kwargs[key] for key in self._keys if key in kwargs}
        for key, val in settings.items():
            setattr(self, key, val)
        return self

    def __enter__(self):
        """Record existing open figures and enter style context (if any)."""
        super().__enter__()
        if self.style:
            self.style_context = mpl.style.context(self.style)
            self.style_context.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit style context, save new figures, and optionally close them."""
        if self.style:
            self.style_context.__exit__(exc_type, exc_value, traceback)

        self._existing_open_figs = [ref() for ref in self._existing_open_figs if ref() is not None]
        new_file_counter = 0

        for fig in self.new_figures:

            new_file_counter += 1
            label = fig.get_label()
            filename = self.generate_filename(label, new_file_counter)

            for fmt in self.formats:
                output_file = f"{filename}.{fmt.lower()}"
                fig.savefig(output_file)

            if self.autoclose:
                plt.close(fig)

        # Reset state
        super().__exit__(exc_type, exc_value, traceback)
        self.style_context = None

    def generate_filename(self, label, counter):
        """Help generate filenames based on `filename` and placeholders.

        Supports placeholders like {label}, {number}, and appends
        a counter if multiple new figures are detected.

        Args:
            label (str): The figure label.
            counter (int): The figure counter.

        Returns:
            str: The generated filename.

        Examples:
            >>> sf = SavedFigure(filename="plot_{label}.png")
            >>> sf.generate_filename("test", 1)
            'plot_test.png'
        """
        if self.filename.is_dir():
            filename: Path = self.filename / "{label}"
        else:
            filename: Path = self.filename if self.filename is not None else Path("{label}")

        filename = str(filename).format(label=label, number=counter)
        # Append counter if filename lacks placeholders and multiple files
        if "{label}" not in str(self.filename) and "{number}" not in str(self.filename) and counter > 1:
            parts = filename.rsplit(".", 1)
            filename = f"{parts[0]}-{counter}.{parts[1]}" if len(parts) > 1 else f"{filename}-{counter}"
        return filename


class InsetPlot(_PreserveFigureMixin):
    """A context manager for creating inset plots in matplotlib with minimal effort.

    The `InsetPlot` class simplifies the process of generating inset plots that are properly
    positioned relative to the parent axes. It ensures that the inset labels do not overlap
    with the parent axes and provides flexibility in specifying the dimensions, position, and
    behavior of the inset plot.

    Args:
        ax (matplotlib.Axes, None):
            The parent axes in which to create the inset plot. If `None` (default), the current
            axes from `plt.gca()` are used.
        loc (str, int, None):
            Location of the inset. Accepts location strings compatible with matplotlib legends
            (e.g., "upper left", "center", etc.) or their numeric equivalents. Includes "best" or
            "auto" (or 0) in which case an auto-placement algorithm is used. This is the default.
        width (float):
            The width of the inset. Units depend on the `dimension` argument. Default is `0.33`.
        height (float):
            The height of the inset. Units depend on the `dimension` argument. Default is `0.33`.
        dimension (str):
            Specifies whether `width` and `height` are given as fractions of the parent axes
            ("fraction") or in inches. Default is "fraction".
        switch_to_inset (bool):
            If `True`, the inset axes become the current axes within the context, and the parent
            axes are restored when the context ends. Default is `True`.
        padding (float, float):
            The padding between the inset and the parent axes. Default is `0.02,0.02`.

    Attributes:
        locations (dict):
            A dictionary mapping location strings (e.g., "upper right") to their numeric equivalents.

    Notes:
        - The `dimension` parameter determines whether the `width` and `height` of the inset are
          interpreted as fractions of the parent axes or as absolute values in inches.
        - The context manager ensures that matplotlib's pyplot functions act on the inset axes
          while inside the context, making plotting within the inset more convenient.
        - After exiting the context, the placement of the inset is automatically adjusted to
          prevent overlaps with the parent axes labels.

    Examples:
        Creating an inset plot within a parent plot:

        >>> fig, ax = plt.subplots()
        >>> ax.plot([1, 2, 3], [4, 5, 6])
        >>> with InsetPlot(ax=ax, loc="upper right", width=0.3, height=0.3) as inset_ax:
        ...     inset_ax.plot([1, 2, 3], [6, 5, 4])
        >>> plt.show()

        The inset plot is placed in the upper right corner of the parent plot.

        Using an inset on the current axes:

        >>> plt.plot([1, 2, 3], [4, 5, 6], label="Main Plot")
        >>> with InsetPlot(loc="best", width=0.25, height=0.25) as inset_ax:
        ...     inset_ax.scatter([1, 2, 3], [10, 9, 8], color="red")
        >>> plt.show()
    """

    locations = {
        "auto": 0,
        "best": 0,
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
        loc="best",
        width=0.33,
        height=0.33,
        dimension="fraction",
        switch_to_inset=True,
        padding=(0.02, 0.02),
    ):
        """
        Initialize the `InsetPlot` context manager.

        Parameters are used to configure the parent axes, inset plot dimensions, location, and
        context behavior.
        """
        super().__init__()
        self._ax = ax
        self._loc = loc
        if dimension == "fraction":
            if isinstance(height, float) and 0.0 < height <= 1.0:
                height = f"{height * 100:.0f}%"
            if isinstance(width, float) and 0.0 < width <= 1.0:
                width = f"{width * 100:.0f}%"
        self.height = height
        self.width = width
        self.padding = padding
        self.switch_to_inset = switch_to_inset

    def __enter__(self):
        """Create the inset axes using the axes_grid toolkit."""
        self._store_current_figure_and_axes()  # Note the current figure and axes safely
        if self._ax is None:  # Use current axes if not passed explicitly
            self.ax = plt.gca()
        else:
            self.ax = self.ax
        if not isinstance(self._loc, int):
            self.loc = self.locations.get(str(self._loc).lower().replace("-", " "), 1)
        else:
            self.loc = self._loc
        axins = inset_axes(self.ax, width=self.width, height=self.height, loc=self.loc if self.loc else 1)
        self.axins = axins
        if self.switch_to_inset:
            plt.sca(self.axins)
        return self.axins

    def __exit__(self, exc_type, value, traceback):
        """Reposition the inset as the standard positioning can cause labels to overlap."""
        if self.loc == 0:
            self.loc, _ = find_best_position(self.ax, self.axins)
        inset_location = new_bbox_for_loc(self.axins, self.ax, self.loc, self.padding)
        # We need to give co-ordinates in axes units, not figure units.
        position = inset_location.transformed(self.ax.figure.transFigure).transformed(self.ax.transAxes.inverted())

        # Matplotlib won;t let you move an inset in 3.10, so instead we need to create a new one and copy!
        move_inset(self.ax, self.axins, position)
        self.ax.figure.canvas.draw()

        if self.switch_to_inset:
            self._restore_current_figure_and_axes()


class DoubleYAxis(_PreserveFigureMixin):
    """Context manager to facilitate plotting with dual Y-axes on a Matplotlib figure.

    This class simplifies creating plots with primary and secondary Y-axes, allowing customized
    axes properties, legend merging, and seamless integration with Matplotlib's context management.

    Args:
        ax (matplotlib.axes.Axes | None):
            The primary Matplotlib axis object where the visualization or plot will be created.
            Defaults to `None`, in which case the current active axis will be used.
        legend (bool):
            Whether to display the legend on the plot. Defaults to `True`.
        loc (str | int):
            The location of the legend on the plot. Can be a string (e.g., 'best', 'upper right')
            or an integer corresponding to Matplotlib's legend location codes. Defaults to `'best'`.
        colours (list | tuple | str | None):
            Colours for the primary and secondary Y-axes. Can be specified as:
            - A comma-separated string (e.g., `"red, blue"`).
            - A list or tuple of at least two colours (e.g., `["red", "blue"]`).
            If fewer than two colours are provided, missing values are set to `None`.
            Defaults to `None`.
        switch_to_y2 (bool):
            Whether to activate the secondary Y-axis (`y2`) as the current axis within the context.
            Defaults to `True`.

    Attributes:
        locations (dict):
            A dictionary mapping location strings (e.g., "upper right") to their numeric equivalents.

    Raises:
        ValueError:
            If the provided legend location is a string not recognized by Matplotlib.
        TypeError:
            If the legend location is of an unsupported type or if colours are specified
            in an incorrect format.

    Notes:
        - This class manages the creation of dual Y-axes while adjusting their styles, labels, and legends.
        - Upon exiting the context, any temporary axes changes are reverted to restore the original state.

    Examples:
        Basic usage with default settings:

        >>> fig, ax = plt.subplots()
        >>> ax.plot([0, 1, 2], [10, 20, 30], label="Primary")
        >>> with DoubleYAxis(ax=ax) as ax2:
        >>>     ax2.plot([0, 1, 2], [100, 200, 300], label="Secondary", color="red")
        >>> plt.show()

        Customizing legend location and axis colours:

        >>> fig, ax = plt.subplots()
        >>> ax.plot([0, 1], [0, 1], label="Primary")
        >>> with DoubleYAxis(ax=ax, loc="upper left", colours=["green", "orange"]) as ax2:
        >>>     ax2.plot([0, 1], [10, 20], label="Secondary")
        >>> plt.show()
    """

    locations = InsetPlot().locations

    def __init__(self, ax=None, legend=True, loc="best", colours=None, switch_to_y2=True):
        """Initialize the DoubleYAxis context manager.

        Ensures proper validation and formatting of input parameters.

        Args:
            ax (matplotlib.axes.Axes | None):
                The primary axis object. Defaults to `None`, in which case the current axis
                (`plt.gca()`) is used.
            legend (bool):
                Whether to display the legend on the plot. Defaults to `True`.
            loc (str | int):
                The location of the legend, normalized to lowercase and stripped of extra spaces
                for string values (e.g., 'best', 'upper left'). Defaults to `'best'`.
            colours (list | tuple | str | None):
                Colours for the primary and secondary Y-axes:
                - Strings are split into a list using commas (e.g., `"green, red"`).
                - Lists/tuples with two elements define colours for both axes. Extra colours
                  are truncated, and missing values are set to `None`.
                - If `None`, no specific colours are set. Defaults to `None`.
            switch_to_y2 (bool):
                If `True`, activates the secondary Y-axis as the current axis upon entering
                the context. Defaults to `True`.

        Raises:
            ValueError:
                If the `loc` argument is a string not recognized as a valid legend location.
            TypeError:
                If the `loc` argument is not a string or integer, or if `colours` is not in the
                expected format (list, tuple, or comma-separated string).
        """
        super().__init__()

        self._ax = ax
        self.ax = None

        # Configure legend location
        if isinstance(loc, str):
            loc = loc.lower().replace("-", " ").strip()
            if loc not in self.locations:
                raise ValueError(f"Location '{loc}' not recognised!")
            loc = self.locations[loc]
        if not isinstance(loc, int):
            raise TypeError(f"Legend location must be of type str or int, got {type(loc)}.")
        self.loc = loc
        self.legend = legend

        # Configure axis colours
        if isinstance(colours, str):
            colours = [x.strip() for x in colours.split(",")]
        if isinstance(colours, (list, tuple)):
            if len(colours) < 2:
                colours = [None] * (2 - len(colours)) + list(colours)
            if len(colours) > 2:
                colours = list(colours[:2])
        elif colours is not None:
            raise TypeError(f"Colours must be a list, tuple, or string, not {type(colours)}.")
        self.colours = colours
        self._switch = switch_to_y2

    def __enter__(self):
        """Handle context entry for managing temporary switchable axes in a Matplotlib figure.

        Returns:
            matplotlib.axes._subplots.AxesSubplot:
                The secondary Y-axis created through `twinx()`.
        """
        self._store_current_figure_and_axes()
        self.ax = plt.gca() if self._ax is None else self._ax
        self.ax2 = self.ax.twinx()
        if self._switch:
            plt.sca(self.ax2)  # Set the secondary axis as the current axis
        return self.ax2

    def __exit__(self, exc_type, value, traceback):
        """Handle the exit portion of the context manager.

        Customise axis properties, legends, and restoring the original figure and axes.

        This method ensures dual Y-axes share customizable colour properties and adjusts their
        visibility. Legends from both axes are merged and updated to their defined location.

        Args:
            exc_type (type | None):
                The exception type, if one occurs during the `with` block. Set to `None` if no
                exception occurred.
            value (BaseException | None):
                The exception instance, if one occurs during the `with` block. Set to `None`
                if no exception occurred.
            traceback (types.TracebackType | None):
                The traceback object, if an exception occurs. Set to `None` if no exception occurred.

        Returns:
            bool:
                Returns `False` to propagate exceptions, if any occur, during the `with` block.
        """
        # Configure axis visibility and position
        self.ax2.spines["left"].set_visible(False)
        self.ax2.yaxis.tick_right()
        self.ax.spines["right"].set_visible(False)
        self.ax.yaxis.tick_left()

        # Apply colours to the primary axis
        if self.colours[0] is not None:
            self.ax.tick_params(axis="y", labelcolor=self.colours[0])
            self.ax.yaxis.label.set_color(self.colours[0])
            self.ax.spines["left"].set_color(self.colours[0])
            self.ax.tick_params(axis="y", which="both", colors=self.colours[0])

        # Apply colours to the secondary axis
        if self.colours[1] is not None:
            self.ax2.tick_params(axis="y", labelcolor=self.colours[1])
            self.ax2.yaxis.label.set_color(self.colours[1])
            self.ax2.spines["right"].set_color(self.colours[1])
            self.ax2.tick_params(axis="y", which="both", colors=self.colours[1])

        # Merge legends from primary and secondary axes
        if self.legend:
            if not (lg1 := self.ax.get_legend()):
                lg1 = self.ax.legend()
            if not (lg2 := self.ax2.get_legend()):
                lg2 = self.ax2.legend()
            handles1, labels1 = self.ax.get_legend_handles_labels()
            handles2, labels2 = self.ax2.get_legend_handles_labels()
            prop1 = lg1.properties()
            prop2 = lg2.properties()
            lg1.remove()
            lg2.remove()
            legend = self.ax.legend(handles1 + handles2, labels1 + labels2, loc=self.loc)
            if self.loc == 0:  # Auto-detect the best location if applicable
                self.loc, _ = find_best_position(self.ax, legend)
                legend.remove()
                legend = self.ax.legend(handles1 + handles2, labels1 + labels2, loc=self.loc)
            copy_properties(legend, prop2 | prop1)

        # Restore the original figure and axes
        if self._switch:
            self._restore_current_figure_and_axes()


class MultiPanel(_PlotContextSequence, _PreserveFigureMixin):
    r"""Context manager for creating multi-panel plots in Matplotlib.

    The `MultiPanel` class simplifies the process of creating and managing multi-panel plots. It supports both regular
    and irregular grids of subplots, automatically adjusts figure sizes, supports shared axes options, and can apply
    labeling patterns to subplots.

    Args:
        panels (tuple[int, int], int, or list[int]):
            Specifies the number of subplots to create. Options:

            - `tuple(rows, columns)`: Regular grid with the specified number of rows and columns.
            - `int`: Single row grid with `n` columns.
            - `list[int]`: Irregular grid where each element specifies the number of panels in a row.

    Keyword Args:
        figure (matplotlib.figure.Figure):
            Figure to contain the subplots. Defaults to the current active figure if `None`.
        sharex (bool):
            Enables shared x-axis among subplots. Default is `False`.
        sharey (bool):
            Enables shared y-axis among subplots. Default is `False`.
        adjust_figsize (bool, float, or tuple[float, float]):
            Adjusts figure size to fit the subplots. Options:

            - `True` (default): Automatically adjusts width/height using pre-defined factors for extra rows/columns.
            - `float`: Applies a uniform factor for width and height adjustment.
            - `tuple[float, float]`: Separately adjusts width and height with the provided factors.

        label_panels (str or bool):
            Adds subplot labels (e.g., "(a)", "(b)"). Default of `True` applies the `({alpha})` format. If a string is
            provided, it is used as the format pattern.
        same_aspect (bool):
            Ensures all subplots have the same aspect ratio. Ignored if width or height ratios are specified in
            GridSpec-related configurations. Default is `True`.
        transpose (bool):
            Interprets the grid layout based on transposed rows and columns. For irregular grids, rows are treated as
            columns if `transpose=True`. Default is `False`.

        \*\*kwargs:
            Additional keyword arguments passed down to:

            - :py:meth:`matplitlib.axes.Axes.set_title` for subplot font adjustments.
            - :py:meth:`matplotlib.figure.Figure.add_gridspec` for grid configuration.

    Returns:
        (List[matplotlib.axes.Axes]):
            List of the created Matplotlib Axes.

    Notes:
        - For wide multi-column plots in journal submissions, use double-width figure styles along with
          `adjust_figsize` to maintain figure height while increasing width.
        - The `nplots` parameter is deprecated. Use the `panels` argument instead to specify the number of subplots.

    Examples:
        Create a 2x3 grid with shared x-axis and labeled panels:

        >>> with MultiPanel((2, 3), sharex=True, label_panels=True) as axes:
        ...     for ax in axes:
        ...         ax.plot([1, 2, 3], [4, 5, 6])

        Create an irregular grid with 2 rows (3 panels in the first row, 1 in the second):

        >>> with MultiPanel([3, 1], adjust_figsize=(0.5, 1.0)) as axes:
        ...     axes[0].plot([1, 2, 3], [3, 2, 1])
        ...     axes[1].scatter([1, 2, 3], [4, 5, 6])
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
            warnings.warn(
                "nplots aregument is depricated. Pass the same value directly as the number of panels now.",
                DeprecationWarning,
            )
            self.panels = self.kwargs.pop("nplots")

    def __enter__(self):
        """Create the grid of axes."""
        self._store_current_figure_and_axes()
        self._set_figure()
        self._adjust_figure_size()
        self._create_gridspec()
        self._label_subplots()
        return self

    def __exit__(self, exc_type, value, traceback):
        """Clean up the axes."""
        self.figure.canvas.draw()
        if self.same_aspect:  # Force the aspect ratios to be the same
            asp = np.array([ax.bbox.width / ax.bbox.height for ax in self.axes.flatten()]).min()
            for ax in self.axes.flatten():
                ax.set_box_aspect(1 / asp)

        self._restore_current_figure_and_axes()

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
        gs_kwargs = _filter_keys_in_dict(self.kwargs, _gsargs)
        self.gs = self.figure.add_gridspec(*panels, **gs_kwargs)
        self.axes = _RavelList([])

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

            ax.set_title(
                f" {counter(ix, self.label_panels)}", loc="left", y=y, **_filter_keys_in_dict(self.kwargs, _fontargs)
            )


class StackVertical(MultiPanel):
    r"""A context manager for generating a vertical stack of subplots with shared x-axes.

    This class creates a vertical stack of subplots, optionally removing the vertical space between them
    for a clean and compact layout. Automatically handles adjustments to the figure height, subplot
    alignment, and axes label formatting.

    Args:
        number (int):
            The number of subplots to stack vertically.

    Keyword Args:
        figure (matplotlib.Figure):
            The figure to use for the subplots. Defaults to the current active figure if `None`.
        joined (bool):
            Whether to remove vertical space between subplots for a seamless look. Default is `True`.
        sharex (bool):
            Whether the subplots share the same x-axis. Default is `True`.
        sharey (bool):
            Whether the subplots share the same y-axis. Default is `False`.
        adjust_figsize (bool or float):
            Whether to adjust the figure height to accommodate additional subplots. Options:

            - `True` (default): Increases figure height by `0.6` of the original height for each
               additional subplot beyond the first.
            - `float`: Specifies a custom height adjustment factor for each additional subplot.

        label_panels (str or bool):
            Adds labels (e.g., "(a)", "(b)") to the subplots for clear identification.

            - Default is `True`, which applies the `({alpha})` pattern.
            - A custom string can be provided to format the labels.

        \*\*kwargs:
            Additional arguments:

            - :py:meth:`matplitlib.axes.Axes.set_title` for subplot font adjustments.
            - :py:meth:`matplotlib.figure.Figure.add_gridspec` for grid configuration.

    Returns:
        List[matplotlib.axes.Axes]:
            The list of axes created within the context.

    Notes:
        - Matplotlib's layout engine can make it challenging to remove vertical space between stacked subplots
          due to constraints on label and title positioning. This class manages this for you by adjusting y-limits
          and ensuring tick labels do not overlap.
        - The current figure during the context is the one with the stacked subplots. Upon exiting the context,
          the previous active figure is restored.

    Examples:
        Create a vertical stack of 3 subplots with shared x-axes:

        >>> with StackVertical(3, sharex=True, joined=True) as axes:
        ...     for ax in axes:
        ...         ax.plot([1, 2, 3], [4, 5, 6])
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
        """Initialize the StackVertical class with configuration for stacked subplots."""
        self.number = number
        self.joined = joined
        self._fig_tmp = figure
        self.gs = None
        self.sharex = sharex
        self.sharey = sharey
        self.hspace = 0 if self.joined else kwargs.pop("hspace", 0.1)
        self.adjust_figsize = adjust_figsize if isinstance(adjust_figsize, float) else float(int(adjust_figsize)) * 0.8
        self.label_panels = "({alpha})" if isinstance(label_panels, bool) and label_panels else label_panels
        self.align_labels = kwargs.pop("align__labels", True)
        self.kwargs = kwargs

    def __enter__(self):
        """Set up and create the stacked subplots."""
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

    def __exit__(self, exc_type, value, traceback):
        """Clean up and adjust the subplot layout upon exiting the context."""
        if self.joined:
            for ax in self.axes:
                ax.label_outer()
            plt.draw()
            for ix, ax in enumerate(self.axes):
                self._fix_limits(ix, ax)
            eng = self.figure.get_layout_engine()
            rect = list(eng.get()["rect"])
            h = self.figure.get_figheight()
            boundary = 0.05 / h
            rect[1] = boundary if rect[1] == 0 else rect[1]
            rect[3] = 1 - 2 * boundary if rect[3] == 1 else rect[3]
            self.figure.get_layout_engine().set(h_pad=0.0, hspace=0.0, rect=rect)
        self._align_labels()
        self.figure.canvas.draw()
        self._restore_current_figure_and_axes()

    def _align_labels(self):
        """Align the y-axis labels across all subplots."""
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
        """Adjust the y-axis limits to ensure tick labels are inside the axes frame."""
        fig = self.figure
        fnt_pts = ax.yaxis.get_ticklabels()[0].get_fontsize()
        ax_height = ax.bbox.transformed(fig.transFigure.inverted()).height * fig.get_figheight() * 72
        dy = fnt_pts / ax_height  # Space needed in axes units for labels.
        ylim = list(ax.get_ylim())
        tr = ax.transData + ax.transAxes.inverted()  # Transform data to axes units
        yticks = [tr.transform((0, x))[1] for x in ax.get_yticks()]  # Tick positions in axes units.

        if yticks[1] < dy and ix != len(self.axes) - 1:  # Adjust range for non-bottom plots
            ylim[0] = tr.inverted().transform((0, -dy))[1]
        if yticks[-2] < 1.0 - dy and ix != 0:  # Adjust range for non-top plots
            ylim[1] = tr.inverted().transform((0, 1 + dy))[1]
        ax.set_ylim(ylim)
        self.figure.canvas.draw()


if __name__ == "__main__":
    pass
