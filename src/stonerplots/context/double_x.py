"""Context managers for top x axes and independent top/right axes."""

from typing import Optional, Union

from matplotlib.axes import Axes

from .double_base import DoubleAxisBase


class _ParentAxesLocator:
    """Keep an overlay aligned while exposing its subplot to layout engines."""

    def __init__(self, parent: Axes) -> None:
        self.parent = parent

    def __call__(self, axes, renderer):
        """Return the primary axes' current plotting rectangle."""
        return self.parent.get_position()

    def get_subplotspec(self):
        """Expose the primary subplot specification to tight layout."""
        return self.parent.get_subplotspec()


class DoubleXAxis(DoubleAxisBase):
    """Add a top x-axis sharing the primary y-axis.

    :param ax: Primary axes, or the current axes if None.
    :param legend: Merge legends onto the primary axes on exit. Defaults to True.
    :param loc: Merged legend location. Defaults to "best".
    :param colours: Bottom and top axis colours, using the same parsing rules as
        DoubleYAxis. Accepts a list, tuple, comma-separated string or None.
    :param switch_to_x2: Make the returned secondary axes current within the
        context and restore the previous axes on exit. Defaults to True.

    The returned Axes supports plotting against an independent top x scale.
    Legend handling and colour validation share a common base with DoubleYAxis.
    """

    _coordinates = ("x",)

    def __init__(
        self,
        ax: Optional[Axes] = None,
        legend: bool = True,
        loc: Union[str, int] = "best",
        colours: Optional[Union[list, tuple, str]] = None,
        switch_to_x2: bool = True,
    ) -> None:
        """Configure the primary axes, legend, colours and current-axes switch."""
        super().__init__(ax, legend, loc, colours, switch_to_x2)

    def _create_secondary_axes(self) -> Axes:
        """Create the overlaid axes, sharing the primary y coordinate."""
        assert self.ax is not None
        return self.ax.twiny()


class DoubleXYAxis(DoubleAxisBase):
    """Add independent top x and right y axes for a second dataset.

    :param ax: Primary axes, or the current axes if None.
    :param legend: Merge legends onto the primary axes on exit. Defaults to True.
    :param loc: Merged legend location. Defaults to "best".
    :param colours: Primary (bottom/left) and secondary (top/right) colours, using
        the same parsing rules as DoubleYAxis. Accepts a list, tuple,
        comma-separated string or None.
    :param switch_to_xy2: Make the returned secondary axes current within the
        context and restore the previous axes on exit. Defaults to True.

    The context returns one Axes with both coordinates independent of the
    primary axes. It remains aligned with the primary plot during layout and
    resizing. Legend handling and colour validation share a common base with DoubleYAxis.
    """

    _coordinates = ("x", "y")

    def __init__(
        self,
        ax: Optional[Axes] = None,
        legend: bool = True,
        loc: Union[str, int] = "best",
        colours: Optional[Union[list, tuple, str]] = None,
        switch_to_xy2: bool = True,
    ) -> None:
        """Configure the primary axes, legend, colours and current-axes switch."""
        super().__init__(ax, legend, loc, colours, switch_to_xy2)

    def _create_secondary_axes(self) -> Axes:
        """Overlay an unshared axes, retaining the primary subplot layout."""
        assert self.ax is not None
        parent = self.ax
        figure = parent.figure
        spec = parent.get_subplotspec()
        if spec is not None:
            secondary = figure.add_subplot(spec)
        else:
            secondary = figure.add_axes(parent.get_position().bounds)
        secondary.set_axes_locator(_ParentAxesLocator(parent))
        secondary.set_zorder(parent.get_zorder())
        secondary.patch.set_visible(False)
        secondary.xaxis.tick_top()
        secondary.xaxis.set_label_position("top")
        secondary.yaxis.tick_right()
        secondary.yaxis.set_label_position("right")
        return secondary
