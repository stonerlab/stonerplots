# -*- coding: utf-8 -*-
"""Context Manager for Double Y axis plots."""

from types import TracebackType
from typing import Optional, Type, Union

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from ..util import copy_properties, find_best_position
from .base import PreserveFigureMixin
from .base import locations as _locations


class DoubleYAxis(PreserveFigureMixin):
    """Context manager to facilitate plotting with dual Y-axes on a Matplotlib figure.

    This class simplifies creating plots with primary and secondary Y-axes, allowing customised
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

    locations = _locations

    def __init__(
        self,
        ax: Optional[Axes] = None,
        legend: bool = True,
        loc: Union[str, int] = "best",
        colours: Optional[Union[list, tuple, str]] = None,
        switch_to_y2: bool = True,
    ) -> None:
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
        self.ax: Optional[Axes] = None
        self.ax2: Optional[Axes] = None

        # Configure legend location
        match loc:
            case str():
                loc = loc.lower().replace("-", " ").strip()
                if loc not in self.locations:
                    raise ValueError(f"Location '{loc}' not recognised!")
                loc = self.locations[loc]
            case int():
                pass
            case _:
                raise TypeError(f"Legend location must be of type str or int, got {type(loc)}.")
        self.loc = loc
        self.legend = legend

        # Configure axis colours
        colours_list: Optional[list] = None
        if isinstance(colours, str):
            colours_list = [x.strip() for x in colours.split(",")]
        elif isinstance(colours, (list, tuple)):
            if len(colours) < 2:
                colours_list = [None] * (2 - len(colours)) + list(colours)
            elif len(colours) > 2:
                colours_list = list(colours[:2])
            else:
                colours_list = list(colours)
        elif colours is not None:
            raise TypeError(f"Colours must be a list, tuple, or string, not {type(colours)}.")
        self.colours = colours_list
        self._switch = switch_to_y2

    def good_colour(self, axis: int) -> bool:
        """Return True if we have a colours defined for this axis."""
        axis = int(axis)
        if self.colours is None:
            return False
        match self.colours:
            case list() if -len(self.colours) < axis < len(self.colours):
                return self.colours[axis] is not None
            case str() if -len(self.colours) < axis < len(self.colours):
                return True
            case _:
                return False

    def __enter__(self) -> Axes:
        """Handle context entry for managing temporary switchable axes in a Matplotlib figure.

        Returns:
            (matplotlib.axes._subplots.AxesSubplot):
                The secondary Y-axis created through `twinx()`.
        """
        self._store_current_figure_and_axes()
        ax_attr = getattr(self._ax, "ax", None)
        if isinstance(ax_attr, Axes):
            self._ax = self._ax.ax  # type: ignore[union-attr]
        self.ax = self._ax if isinstance(self._ax, Axes) else plt.gca()
        self.ax2 = self.ax.twinx()
        if self._switch:
            plt.sca(self.ax2)  # Set the secondary axis as the current axis
        return self.ax2

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        """Handle the exit portion of the context manager.

        Customise axis properties, legends, and restoring the original figure and axes.

        This method ensures dual Y-axes share customisable colour properties and adjusts their
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
        assert self.ax is not None
        assert self.ax2 is not None
        assert self.colours is not None
        
        self.ax2.spines["left"].set_visible(False)
        self.ax2.yaxis.tick_right()
        self.ax.spines["right"].set_visible(False)
        self.ax.yaxis.tick_left()

        # Apply colours to the primary axis
        if self.good_colour(0):
            self.ax.tick_params(axis="y", labelcolor=self.colours[0])
            self.ax.yaxis.label.set_color(self.colours[0])
            self.ax.spines["left"].set_color(self.colours[0])
            self.ax.tick_params(axis="y", which="both", colors=self.colours[0])

        # Apply colours to the secondary axis
        if self.good_colour(1):
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
