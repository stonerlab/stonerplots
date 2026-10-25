# -*- coding: utf-8 -*-
"""Common implementation for double-axis plotting contexts."""

from types import TracebackType
from typing import Literal, Optional, Type, Union

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from ..util import copy_properties, find_best_position
from .base import PreserveFigureMixin
from .base import locations as _locations


class DoubleAxisBase(PreserveFigureMixin):
    """Shared validation, styling, legends and pyplot state for double-axis plots."""

    locations = _locations
    _coordinates: tuple[Literal["x", "y"], ...] = ()

    def __init__(
        self,
        ax: Optional[Axes] = None,
        legend: bool = True,
        loc: Union[str, int] = "best",
        colours: Optional[Union[list, tuple, str]] = None,
        switch_to_secondary: bool = True,
    ) -> None:
        """Validate and store the primary axes, legend, colours and switching options."""
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
        self._switch = switch_to_secondary

    def good_colour(self, axis: int) -> bool:
        """Return True if the normalised colour list defines this axis."""
        axis = int(axis)
        return (
            self.colours is not None
            and -len(self.colours) <= axis < len(self.colours)
            and self.colours[axis] is not None
        )

    def __enter__(self) -> Axes:
        """Handle context entry for managing temporary switchable axes in a Matplotlib figure.

        Returns:
            (matplotlib.axes.Axes):
                The secondary plotting axes created by this context manager.
        """
        self._store_current_figure_and_axes()
        ax_attr = getattr(self._ax, "ax", None)
        if isinstance(ax_attr, Axes):
            self._ax = self._ax.ax  # type: ignore[union-attr]
        self.ax = self._ax if isinstance(self._ax, Axes) else plt.gca()
        self.ax2 = self._create_secondary_axes()
        if self._switch:
            plt.sca(self.ax2)  # Set the secondary axis as the current axis
        else:
            self._restore_current_figure_and_axes()
        return self.ax2

    def _create_secondary_axes(self) -> Axes:
        """Create the secondary axes in a concrete double-axis context."""
        raise NotImplementedError

    def _style_axes(self) -> None:
        """Position and colour each independent coordinate of the two axes."""
        assert self.ax is not None
        assert self.ax2 is not None
        for coordinate in self._coordinates:
            primary_side, secondary_side = ("left", "right") if coordinate == "y" else ("bottom", "top")
            primary_axis = getattr(self.ax, f"{coordinate}axis")
            secondary_axis = getattr(self.ax2, f"{coordinate}axis")
            self.ax2.spines[primary_side].set_visible(False)
            self.ax.spines[secondary_side].set_visible(False)
            secondary_axis.set_ticks_position(secondary_side)
            secondary_axis.set_label_position(secondary_side)
            primary_axis.set_ticks_position(primary_side)
            primary_axis.set_label_position(primary_side)
            for index, (axes, side, axis) in enumerate(
                ((self.ax, primary_side, primary_axis), (self.ax2, secondary_side, secondary_axis))
            ):
                if self.good_colour(index):
                    assert self.colours is not None
                    colour = self.colours[index]
                    axes.tick_params(axis=coordinate, which="both", colors=colour)
                    axis.label.set_color(colour)
                    axes.spines[side].set_color(colour)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Style and merge the axes, restoring pyplot state even if finalisation fails."""
        try:
            self._style_axes()
            if self.legend:
                self._merge_legends()
        finally:
            if self._switch:
                self._restore_current_figure_and_axes()

    def _merge_legends(self) -> None:
        """Combine both axes' legend entries and preserve existing legend styling."""
        assert self.ax is not None
        assert self.ax2 is not None
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
            self.loc, _ = find_best_position(self.ax, legend)  # type: ignore[arg-type]
            legend.remove()
            legend = self.ax.legend(handles1 + handles2, labels1 + labels2, loc=self.loc)
        copy_properties(legend, prop2 | prop1)
