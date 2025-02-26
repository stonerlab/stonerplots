# -*- coding: utf-8 -*-
"""Base class for context managers."""
import weakref
from collections.abc import Sequence
from typing import Any, List, Union

import matplotlib as mpl
import matplotlib.pyplot as plt

__all__ = ["RavelList", "PreserveFigureMixin", "PlotContextSequence", "TrackNewFiguresAndAxes"]


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

class RavelList(list):
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


class PreserveFigureMixin:
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


class PlotContextSequence(Sequence):
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
        self.axes = RavelList()
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


class TrackNewFiguresAndAxes:
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
