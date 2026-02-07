# -*- coding: utf-8 -*-
"""Context managers for preparing multiple subplot figures."""
import warnings
from types import TracebackType
from typing import Any, Optional, Type, Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..counter import counter
from .base import PlotContextSequence, PreserveFigureMixin, RavelList

_gsargs = ["left", "bottom", "right", "top", "width_ratios", "height_ratios", "hspace", "wspace", "h_pad", "w_pad"]
_fontargs = ["font", "fontfamily", "fontname", "fontsize", "fontstretch", "fontstyle", "fontvariant", "fontweight"]


def _filter_keys_in_dict(dic: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """Filter a dictionary to only include specified keys.

    Args:
        dic (dict): The dictionary to filter.
        keys (iterable): The keys to retain in the dictionary.

    Returns:
        (dict): A new dictionary containing only the specified keys.
    """
    return {key: dic[key] for key in keys if key in dic}


class MultiPanel(PlotContextSequence, PreserveFigureMixin):
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
        panels: Union[tuple[int, int], int, list[int]],
        figure: Optional[Union[Figure, int, str]] = None,
        sharex: bool = False,
        sharey: bool = False,
        adjust_figsize: Union[bool, float, tuple[float, float]] = True,
        label_panels: Union[str, bool] = True,
        same_aspect: bool = True,
        transpose: bool = False,
        **kwargs: Any,
    ) -> None:
        """Configure figure and a gridspec for multi-panel plotting."""
        super().__init__()
        if isinstance(panels, int):  # Assume 1 x panels
            panels = (1, panels)
        self.panels = panels
        self._fig_arg = figure
        self.figure: Figure  # Will be set in __enter__
        self.gs: Any = None  # GridSpec type
        self.sharex = sharex
        self.sharey = sharey
        self._adjust_figsize_arg = adjust_figsize
        self.transpose = transpose
        # Adjust fig size can be a tuple
        self.label_panels = "({alpha})" if isinstance(label_panels, bool) and label_panels else label_panels
        self.kwargs = kwargs
        self.same_aspect = "height_ratios" not in kwargs and "width_ratios" not in kwargs and same_aspect
        if "nplots" in self.kwargs:
            warnings.warn(
                "nplots argument is deprecated. Pass the same value directly as the number of panels now. This p[arameter will be removed in version 2.0",
                DeprecationWarning,
            )
            self.panels = self.kwargs.pop("nplots")

    def __enter__(self) -> "MultiPanel":
        """Create the grid of axes."""
        self._store_current_figure_and_axes()
        self._set_figure()
        self._adjust_figure_size()
        self._create_gridspec()
        self._label_subplots()
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        """Clean up the axes."""
        self.figure.canvas.draw()
        if self.same_aspect:  # Force the aspect ratios to be the same
            asp = np.array([ax.bbox.width / ax.bbox.height for ax in self.axes.flatten()]).min()
            for ax in self.axes.flatten():
                ax.set_box_aspect(1 / asp)

        self._restore_current_figure_and_axes()

    def _set_figure(self) -> None:
        """Set the figure based on the provided figure argument or the current figure."""
        fig_or_other: Union[Figure, int, str] = self._fig_arg or plt.gcf()
        match fig_or_other:
            case int() | str():
                self.figure = plt.figure(fig_or_other)
            case _ if isinstance(getattr(fig_or_other, "figure", None), Figure):
                self.figure = fig_or_other.figure  # type: ignore[union-attr]
            case _ if hasattr(fig_or_other, "number"):
                self.figure = plt.figure(fig_or_other.number)  # type: ignore[union-attr]
            case Figure():
                self.figure = fig_or_other
            case _:
                raise TypeError("Unable to interpret {fig_or_other} as a figure.")

    def _adjust_figure_size(self) -> None:
        """Adjust the figure size if necessary."""
        adjust_figsize = self._adjust_figsize_arg
        if isinstance(adjust_figsize, bool):
            adjust_figsize = (int(adjust_figsize), int(adjust_figsize) * 0.8)
        elif isinstance(adjust_figsize, float):
            adjust_figsize = (adjust_figsize, adjust_figsize)
        self.adjust_figsize = adjust_figsize
        self.figsize = self.figure.get_figwidth(), self.figure.get_figheight()

    def _create_gridspec(self) -> None:
        """Create the gridspec for the subplots."""
        match self.panels:
            case int():
                self._create_subplots((1, self.panels) if not self.transpose else (self.panels, 1))
            case list():
                panel_count = int(np.prod(np.unique(self.panels)))
                self._create_subplots(
                    (
                        (len(self.panels), panel_count)
                        if not self.transpose
                        else (panel_count, len(self.panels))
                    ),
                    self.panels,
                )
            case tuple():
                self._create_subplots(self.panels)
            case _:
                raise TypeError(f"Unable to interpret the number of panels to create: {self.panels}")
        if self.adjust_figsize:
            self._do_figure_adjustment()

    def _label_subplots(self) -> None:
        """Label the subplots if necessary."""
        if self.label_panels:
            self._label_figure()

    def _create_subplots(self, panels: tuple[int, int], nplots: Optional[list[int]] = None) -> None:
        """Create the subplots for the given panels."""
        gs_kwargs = _filter_keys_in_dict(self.kwargs, _gsargs)
        self.gs = self.figure.add_gridspec(*panels, **gs_kwargs)
        self.axes = RavelList([])

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

    def _calculate_extent(self, panels: tuple[int, int], nplots: list[int], r: int, c: int) -> int:
        """Calculate the extent of the subplot."""
        if self.transpose:
            return panels[0] // nplots[c]
        return panels[1] // nplots[r]

    def _mark_used(self, used: np.ndarray, r: int, c: int, extent: int) -> None:  # type: ignore[type-arg]
        """Mark the used subplots in the grid."""
        if self.transpose:
            used[r: r + extent, c] = True
        else:
            used[r, c: c + extent] = True

    def _create_subplot(self, r: int, c: int, extent: int) -> Axes:
        """Create a subplot for the given row, column, and extent."""
        if self.transpose:
            return self.figure.add_subplot(self.gs[r: r + extent, c])
        return self.figure.add_subplot(self.gs[r, c: c + extent])

    def _do_figure_adjustment(self) -> None:
        """Adjust the figure size based on the adjust_figsize setting."""
        extra_width = self._calculate_dimension(self.figsize[0], self.adjust_figsize[0], self.panels[1])
        extra_height = self._calculate_dimension(self.figsize[1], self.adjust_figsize[1], self.panels[0])
        self.figure.set_figwidth(extra_width)
        self.figure.set_figheight(extra_height)

    def _calculate_dimension(self, base_size: float, factor: float, panels_count: int) -> float:
        """Calculate the extra dimension (width or height) based on the factor and panels count."""
        if factor < 0:
            return base_size * (1 + factor)
        return base_size * factor * (panels_count - 1) + base_size

    def _label_figure(self) -> None:
        """Do the subplot figure labelling."""
        fig = self.figure
        label_pattern = self.label_panels if isinstance(self.label_panels, str) else "({alpha})"
        for ix, ax in enumerate(self):
            title_pts = ax.title.get_fontsize()
            ax_height = ax.bbox.transformed(fig.transFigure.inverted()).height * fig.get_figheight() * 72
            y = (ax_height - title_pts * 1.5) / ax_height

            ax.set_title(
                f" {counter(ix, label_pattern)}", loc="left", y=y, **_filter_keys_in_dict(self.kwargs, _fontargs)
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
        number: int,
        figure: Optional[Union[Figure, int, str]] = None,
        joined: bool = True,
        sharex: bool = True,
        sharey: bool = False,
        adjust_figsize: Union[bool, float] = True,
        label_panels: Union[str, bool] = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the StackVertical class with configuration for stacked subplots."""
        self.number = number
        self.joined = joined
        self._fig_tmp = figure
        self.gs = None
        self.sharex = sharex
        self.sharey = sharey
        self.hspace = 0 if self.joined else kwargs.pop("hspace", 0.1)
        # Calculate adjust_figsize value to pass to parent class
        adjust_figsize_val: Union[bool, float, tuple[float, float]] = (
            adjust_figsize if isinstance(adjust_figsize, float) else float(int(adjust_figsize)) * 0.8
        )
        self.adjust_figsize_input = adjust_figsize_val
        self.label_panels = "({alpha})" if isinstance(label_panels, bool) and label_panels else label_panels
        self.align_labels = kwargs.pop("align__labels", True)
        self.kwargs = kwargs

    def __enter__(self) -> "StackVertical":
        """Set up and create the stacked subplots."""
        panels = (self.number, 1)
        super().__init__(
            panels,
            figure=self._fig_tmp,
            sharex=self.sharex,
            sharey=self.sharey,
            adjust_figsize=self.adjust_figsize_input,
            label_panels=self.label_panels,
            same_aspect=False,
            **self.kwargs,
        )
        super().__enter__()
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> None:
        """Clean up and adjust the subplot layout upon exiting the context."""
        if self.joined:
            for ax in self.axes:
                ax.label_outer()
            plt.draw()
            for ix, ax in enumerate(self.axes):
                self._fix_limits(ix, ax)
            eng = self.figure.get_layout_engine()
            if eng is not None:
                rect = list(eng.get()["rect"])  # type: ignore[call-arg]
                h = self.figure.get_figheight()
                boundary = 0.05 / h
                rect[1] = boundary if rect[1] == 0 else rect[1]
                rect[3] = 1 - 2 * boundary if rect[3] == 1 else rect[3]
                # Parameters are accepted by ConstrainedLayoutEngine but not in base LayoutEngine signature.
                eng.set(h_pad=0.0, hspace=0.0, rect=rect)  # type: ignore[call-arg]
        self._align_labels()
        self.figure.canvas.draw()
        self._restore_current_figure_and_axes()

    def _align_labels(self) -> None:
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

    def _fix_limits(self, ix: int, ax: Axes) -> None:
        """Adjust the y-axis limits to ensure tick labels are inside the axes frame."""
        fig = self.figure
        ticklabels = ax.yaxis.get_ticklabels()
        if not ticklabels:
            return  # No tick labels to adjust for
        fnt_pts_val = ticklabels[0].get_fontsize()
        fnt_pts = float(fnt_pts_val) if isinstance(fnt_pts_val, (int, float, str)) else 10.0
        ax_height = ax.bbox.transformed(fig.transFigure.inverted()).height * fig.get_figheight() * 72
        dy = 1.33 * fnt_pts / ax_height  # Space needed in axes units for labels 4/3 font size.
        ylim = list(ax.get_ylim())
        tr = ax.transData + ax.transAxes.inverted()  # Transform data to axes units
        yticks = [tr.transform((0, x))[1] for x in ax.get_yticks()]  # Tick positions in axes units.

        if len(yticks) > 1 and yticks[1] < dy and ix != len(self.axes) - 1:  # Adjust range for non-bottom plots
            ylim[0] = tr.inverted().transform((0, -dy))[1]
        if len(yticks) > 2 and yticks[-2] < 1.0 - dy and ix != 0:  # Adjust range for non-top plots
            ylim[1] = tr.inverted().transform((0, 1 + dy))[1]
        ax.set_ylim(ylim[0], ylim[1])
        self.figure.canvas.draw()
