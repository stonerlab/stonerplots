"""Offset related datasets vertically after plotting has finished."""

from typing import Literal, Union

import numpy as np
from matplotlib.collections import LineCollection, PathCollection
from matplotlib.container import ErrorbarContainer
from matplotlib.lines import Line2D

from .base import PreserveFigureMixin, TrackNewFiguresAndAxes

__all__ = ["OffsetPlots"]


class OffsetPlots(TrackNewFiguresAndAxes, PreserveFigureMixin):
    """Separate datasets on each new axes by a constant y offset or factor.

    Inspection and adjustment happen on successful exit. The first dataset is
    unchanged; dataset ``i`` receives ``i * offset`` on linear axes or is
    multiplied by ``factor ** i`` on logarithmic axes. Each axes starts at zero.

    :param float offset: Additive step in y data units on linear axes. Default 1.
    :param float factor: Positive multiplicative step on log axes. Default 10.
        Values below 1 stack downwards; negative offsets do likewise.
    :param pair: By default (``"auto"``), equal nonzero numbers of lines and
        scatter collections are paired by their order within each type.
        False offsets every dataset separately in overall creation order.
        True requires equal numbers of both types, raising ValueError
        otherwise (except on empty axes).
    :type pair: bool or str
    :param bool lines: Include data-coordinate Line2D artists. Default True.
    :param bool scatter: Include data-coordinate scatter collections. Default True.
    :param bool errorbars: Include complete errorbar plots as line datasets,
        including plots with ``fmt="none"``. Default True. Requires lines=True.
    :param bool include_open: Also process existing axes and their existing artists.
        Default False, processing only axes created within the context.

    Only ordinary 2D Cartesian axes with linear or log y scales are handled.
    Reference lines using axes coordinates, filled regions,
    images and other artist types are not shifted. Pairing is positional,
    not inferred from labels or colours. Empty ordinary lines and scatter
    collections are ignored.

    Artist y data are changed, without changing caller-owned arrays. Limits
    are recalculated, respecting disabled autoscaling and explicit limits.
    Reusing the manager applies another offset to the selected datasets.

    Example::

        >>> with OffsetPlots(offset=2):
        ...     fig, ax = plt.subplots()
        ...     for y in datasets:
        ...         ax.plot(x, y)
        ...         ax.scatter(x, y)
    """

    def __init__(
        self,
        offset: float = 1.0,
        *,
        factor: float = 10.0,
        pair: Union[bool, Literal["auto"]] = "auto",
        lines: bool = True,
        scatter: bool = True,
        errorbars: bool = True,
        include_open: bool = False,
    ) -> None:
        super().__init__(include_open=include_open)
        self.offset = float(offset)
        self.factor = float(factor)
        if not np.isfinite(self.offset):
            raise ValueError("offset must be finite")
        if not np.isfinite(self.factor) or self.factor <= 0:
            raise ValueError("factor must be finite and positive")
        if pair != "auto" and not isinstance(pair, bool):
            raise ValueError('pair must be True, False or "auto"')
        self.pair = pair
        self.lines = lines
        self.scatter = scatter
        self.errorbars = errorbars

    def __enter__(self):
        """Save the active axes and start tracking newly created axes."""
        self._store_current_figure_and_axes()
        super().__enter__()
        return self

    def _groups(self, ax):
        """Discover eligible artists and group lines with scatter if requested."""
        groups = []
        error_artists = {}
        for container in ax.containers:
            if isinstance(container, ErrorbarContainer):
                children = tuple(container.get_children())
                for child in children:
                    error_artists[child] = children
        seen = set()
        for artist in ax.get_children():
            if artist in error_artists:
                children = error_artists[artist]
                if (
                    self.lines
                    and self.errorbars
                    and children not in seen
                    and all(child.get_transform() == ax.transData for child in children)
                ):
                    groups.append(children)
                    seen.add(children)
                continue
            if (
                self.lines
                and isinstance(artist, Line2D)
                and artist.get_transform() == ax.transData
                and len(artist.get_ydata())
            ):
                groups.append((artist,))
            elif (
                self.scatter
                and isinstance(artist, PathCollection)
                and artist.get_offset_transform() == ax.transData
                and len(artist.get_offsets())
            ):
                groups.append((artist,))
        lines = [group for group in groups if not isinstance(group[0], PathCollection)]
        scatter = [group for group in groups if isinstance(group[0], PathCollection)]
        if self.pair is True and groups and (not lines or len(lines) != len(scatter)):
            raise ValueError("pair=True requires equal nonzero numbers of lines and scatter collections")
        if self.pair is not False and lines and len(lines) == len(scatter):
            return [line + points for line, points in zip(lines, scatter)]
        return groups

    def _shift_artist(self, artist, index, logarithmic):
        """Move data, scatter offsets or error-bar segments as appropriate."""

        def shift(y):
            return y * self.factor**index if logarithmic else y + index * self.offset

        if isinstance(artist, Line2D):
            y = np.ma.array(artist.get_ydata(orig=False), mask=np.ma.getmaskarray(artist.get_ydata()), copy=True)
            artist.set_ydata(shift(y))
        elif isinstance(artist, LineCollection):
            segments = []
            for segment in artist.get_segments():
                xy = np.ma.array(segment, copy=True)
                if xy.size:
                    xy[:, 1] = shift(xy[:, 1])
                segments.append(xy)
            artist.set_segments(segments)
        else:
            xy = np.ma.array(artist.get_offsets(), copy=True)
            xy[:, 1] = shift(xy[:, 1])
            artist.set_offsets(xy)

    def _offset_axes(self, ax, groups):
        """Shift each group and refresh data and view limits, including collections."""
        if len(groups) < 2:
            return
        logarithmic = ax.get_yscale() == "log"
        for index, group in enumerate(groups[1:], start=1):
            for artist in group:
                self._shift_artist(artist, index, logarithmic)
        ax.relim()
        # Matplotlib < 3.11 does not include collections in relim(). Include
        # every collection, including unshifted ones, and positive log minima.
        for collection in ax.collections:
            bounds = collection.get_datalim(ax.transData)
            points = bounds.get_points()
            if np.isfinite(bounds.minpos).any():
                points = np.vstack([points, bounds.minpos])
            ax.update_datalim(points)
        ax.autoscale_view()

    def __exit__(self, exc_type, exc_value, traceback):
        """Inspect and offset new axes, then restore state even on failure."""
        try:
            if exc_type is None:
                # Validate grouping everywhere before modifying any artist.
                plans = [
                    (ax, self._groups(ax))
                    for ax in self.new_axes
                    if ax.name == "rectilinear" and ax.get_yscale() in ("linear", "log")
                ]
                for ax, groups in plans:
                    self._offset_axes(ax, groups)
        finally:
            super().__exit__(exc_type, exc_value, traceback)
            self._restore_current_figure_and_axes()
