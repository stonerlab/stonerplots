# -*- coding: utf-8 -*-
"""Base class for context managers."""
from copy import copy
import weakref
from collections.abc import Sequence
from typing import Any, List, Union, Optional, Type
from types import TracebackType

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

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
        ix = 0
        items = copy(items)
        while True:
            if ix >= len(items):
                break
            if isinstance(items[ix], list):
                items = items[:ix]+copy(items[ix])+items[ix+1:]
            ix += 1
        return items

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

    def __init__(self) -> None:
        """Initialize figure and axes preservation attributes."""
        self._saved_figure = self._UNSET
        self._saved_axes = self._UNSET
        super().__init__()

    def _store_current_figure_and_axes(self) -> None:
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

    def _restore_current_figure_and_axes(self) -> None:
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

    def __init__(self) -> None:
        """Initialize class and ensure private attributes exist."""
        self.axes = RavelList()
        self._save_fig = None
        self._save_axes = None

    @property
    def raveled_axes(self) -> List[Axes]:
        """Unravel and provide the flattened list of axes."""
        return self.axes.flatten()

    def __len__(self) -> int:
        """Return the number of axes."""
        return len(self.raveled_axes)

    def __contains__(self, value) -> bool:
        """Check if a value is contained within the axes."""
        return value in self.raveled_axes

    def __getitem__(self, index) -> Axes:
        """Get axis item at index and optionally set it as current."""
        ret = self.axes[index]
        self._check_single_axis_selection(ret)
        return ret

    def __iter__(self) -> Axes:
        """Iterate over the axes and set each as current when iterating."""
        for ax in self.raveled_axes:
            plt.sca(ax)
            yield ax

    def __reversed__(self) -> List[Axes]:
        """Iterate in reverse over the axes and set each as current."""
        yield from reversed(self.raveled_axes)

    def _check_single_axis_selection(self, ret) -> None:
        """If the result is a single axis, set it as the current axis."""
        if isinstance(ret, mpl.axes.Axes):
            plt.sca(ret)

    def _save_current_fig_and_axes(self) -> None:
        """Safely save the current figure and axes without creating new ones."""
        self._save_fig = None
        self._save_axes = None
        if not plt.get_fignums():  # No current figures
            return
        self._save_fig = plt.gcf()
        if self._save_fig.axes:
            self._save_axes = plt.gca()

    def _restore_saved_fig_and_axes(self) -> None:
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

    def __init__(self, *args, **kwargs) -> None:
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

    def __enter__(self) -> None:
        """Record any already open figures and axes."""
        for num in plt.get_fignums():
            if not self.include_open:
                self._existing_open_figs.append(weakref.ref(plt.figure(num)))
                self._existing_open_axes[num] = [weakref.ref(ax) for ax in plt.figure(num).axes]

    @property
    def new_figures(self) -> Figure:
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
        # Dereference weakrefs to get actual figure objects for comparison
        # Handle both cases: list of weakrefs or list of already-dereferenced figures
        existing_figs = []
        for item in self._existing_open_figs:
            if isinstance(item, weakref.ref):
                # Item is a weakref, dereference it
                fig = item()
                if fig is not None:
                    existing_figs.append(fig)
            else:
                # Item is already a dereferenced figure
                existing_figs.append(item)

        for num in plt.get_fignums():
            fig = plt.figure(num)
            if fig in existing_figs:  # Skip figures opened before context
                continue
            yield fig

    @property
    def new_axes(self) -> Axes:
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
        # Dereference all weakrefs from all figures to get actual axes objects for comparison
        # Handle both cases: weakrefs or already-dereferenced axes objects
        existing_axes = []
        for _, axes_refs in self._existing_open_axes.items():
            for item in axes_refs:
                if isinstance(item, weakref.ref):
                    # Item is a weakref, dereference it
                    ax = item()
                    if ax is not None:
                        existing_axes.append(ax)
                else:
                    # Item is already a dereferenced axes
                    existing_axes.append(item)

        for num in plt.get_fignums():
            fig = plt.figure(num)
            for ax in fig.axes:
                if ax in existing_axes:  # Skip axes opened before context
                    continue
                yield ax

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Clean up the saved figures and axes."""
        self._existing_open_figs = []
        self._existing_open_axes = {}
