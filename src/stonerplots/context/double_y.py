"""Context manager for a separate right y-axis."""

from typing import Optional, Union

from matplotlib.axes import Axes

from .double_base import DoubleAxisBase


class DoubleYAxis(DoubleAxisBase):
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

    _coordinates = ("y",)

    def __init__(
        self,
        ax: Optional[Axes] = None,
        legend: bool = True,
        loc: Union[str, int] = "best",
        colours: Optional[Union[list, tuple, str]] = None,
        switch_to_y2: bool = True,
    ) -> None:
        """Configure the primary axes, legend, colours and current-axes switch."""
        super().__init__(ax, legend, loc, colours, switch_to_y2)

    def _create_secondary_axes(self) -> Axes:
        """Create the overlaid axes, sharing the primary x coordinate."""
        assert self.ax is not None
        return self.ax.twinx()
