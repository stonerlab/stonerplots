# -*- coding: utf-8 -*-
"""InsetPlot context manager."""

from types import TracebackType
from typing import Optional, Type, Union

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from ..util import find_best_position, move_inset, new_bbox_for_loc
from .base import PreserveFigureMixin
from .base import locations as _locations


class InsetPlot(PreserveFigureMixin):
    """A context manager for creating inset plots in matplotlib with minimal effort.

    The `InsetPlot` class simplifies the process of generating inset plots that are properly
    positioned relative to the parent axes. It ensures that the inset labels do not overlap
    with the parent axes and provides flexibility in specifying the dimensions, position, and
    behavior of the inset plot.

    Args:
        ax (matplotlib.Axes, None):
            The parent axes in which to create the inset plot. If `None` (default), the current
            axes from `plt.gca()` are used. This can also be an object that wraps an Axes instance
            and has an `ax` attribute that points to the underlying Axes object (duck typing support
            for axes wrappers).
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

    locations = _locations

    def __init__(
        self,
        ax: Optional[Axes] = None,
        loc: Union[str, int] = "best",
        width: Union[float, str] = 0.33,
        height: Union[float, str] = 0.33,
        dimension: str = "fraction",
        switch_to_inset: bool = True,
        padding: tuple[float, float] = (0.02, 0.02),
    ) -> None:
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

    def __enter__(self) -> Axes:
        """Create the inset axes using the axes_grid toolkit."""
        # Support for axes wrappers: check if _ax is a wrapper with an 'ax' attribute
        if isinstance(ax_attr:=getattr(self._ax, "ax", None), Axes):
            self.ax = ax_attr  # type: ignore[union-attr]
        elif isinstance(self._ax, Axes):
            self.ax = self._ax
        else:
            self.ax = plt.gca()
        if not isinstance(self._loc, int):
            self.loc = self.locations.get(str(self._loc).lower().replace("-", " "), 1)
        else:
            self.loc = self._loc
        axins = inset_axes(self.ax, width=self.width, height=self.height, loc=self.loc if self.loc else 1)
        self.axins = axins
        if self.switch_to_inset:
            plt.sca(self.axins)
        return self.axins

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
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
