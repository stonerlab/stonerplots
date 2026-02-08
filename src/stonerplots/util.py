# -*- coding: utf-8 -*-
"""Utility functions to support the Context managers.

Based on code used in matplotlib to automatically position a legend.
"""

from collections.abc import Iterable
from copy import copy
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.collections import Collection, PolyCollection
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.text import Text
from matplotlib.transforms import Bbox, IdentityTransform


class _default(object):
    """store default style information."""

    _style: List[str] = ["stoner"]
    _formats: List[str] = ["png"]
    _instance: Optional["_default"] = None

    def __new__(cls) -> "_default":
        """Return the existing class attribute if it is not None."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def style(self) -> List[str]:
        """Return the stylesheets as a list of strings."""
        return copy(self._style)  # return a copy to avoid inadvertently changing the default style.

    @style.setter
    def style(self, value: str | Iterable[str]) -> None:
        """Ensure style is stored as a list of strings."""
        if isinstance(value, str):
            self._style = [x.strip() for x in value.split(",") if x.strip()]
        elif isinstance(value, Iterable):
            self._style = list(value)
        else:
            raise TypeError("Invalid type for default style. Expected str, iterable.")

    @property
    def formats(self) -> List[str]:
        """Return the formats as a list of strings."""
        return copy(self._formats)

    @formats.setter
    def formats(self, value: Union[str, Iterable[str], None]) -> None:
        """Store the default formats."""
        if value is None:
            self._formats = ["png"]
        elif isinstance(value, str):
            self._formats = [x.strip() for x in value.split(",") if x.strip()]
        elif isinstance(value, Iterable):
            self._formats = list(value)
        else:
            raise TypeError("Invalid type for formats. Expected str, iterable, or None.")

    @property
    def filename(self) -> Path:
        """Return filename as a Path object without extension."""
        return self._filename

    @filename.setter
    def filename(self, value: str | Path) -> None:
        """Set filename and extract its extension if valid."""
        if value is not None:
            value = Path(value)
            ext = value.suffix[1:]
            if ext and ext not in self.formats:
                self.formats.append(ext)
            value = value.parent / value.stem
        self._filename = value


class StonerInsetLocator:
    """Wrapper for matplotlib's private _TransformedBoundsLocator.

    We use this to position inset axes. Since it uses a private matplotlib class,
    it's wrapped here so that if matplotlib's internals change, we only have
    one spot to fix.

    Args:
        bounds (List[float]):
            A list of [left, bottom, width, height] in transform coordinates.
        transform (Any):
            The matplotlib transform to apply to the bounds.

    Notes:
        If matplotlib provides a public alternative in the future, we should
        switch to it.

    Examples:
        >>> from matplotlib.transforms import IdentityTransform
        >>> locator = StonerInsetLocator([0.1, 0.1, 0.4, 0.4], IdentityTransform())
    """

    def __init__(self, bounds: List[float], transform: Any) -> None:
        """Initialize with bounds and transform."""
        self._internal = None
        self._init_error: ImportError | None = None
        try:
            # We isolate the private import here to keep the module namespace clean.
            # If matplotlib's internal API changes, this is the only line to fix.
            # pylint: disable=import-outside-toplevel
            from matplotlib.axes._base import _TransformedBoundsLocator  # type: ignore[attr-defined]
        except ImportError as e:
            self._init_error = e
        else:
            self._internal = _TransformedBoundsLocator(bounds, transform)

    def __call__(self, ax: Axes, renderer: Any) -> Any:
        """Execute the internal locator logic."""
        if self._internal is None:
            raise RuntimeError(
                f"stonerplots: Inset positioning failed. Matplotlib's internal API "
                f"is unavailable or has changed: {self._init_error}"
            )
        return self._internal(ax, renderer)

    def __repr__(self) -> str:
        """Return a helpful string representation for debugging."""
        status = "active" if self._internal else "broken"
        return (
            f"<StonerInsetLocator ({status}) wrapping "
            "matplotlib.axes._base._TransformedBoundsLocator>"
        )


def move_inset(parent: Optional[Union[Figure, Axes]], inset_axes: Axes, new_bbox: Bbox) -> None:
    """Relocate an inset_axes to a new location.

    Args:
        parent (Axes, Figure, None):
            The parent class to determine the new bounding box coordinate system.
        inset_axes (Axes):
            The Axes to change the locator for.
        new_bbox (BBox):
            The new position bounding box.

    Notes:
        This creates a new axes locator and assigns it to the axes.

    Examples:
        >>> fig, ax = plt.subplots()
        >>> inset_ax = fig.add_axes([0.1, 0.1, 0.3, 0.3])
        >>> new_bbox = Bbox.from_bounds(0.5, 0.5, 0.3, 0.3)
        >>> move_inset(ax, inset_ax, new_bbox)
    """
    match parent:
        case Figure():
            transform = parent.transFigure
        case Axes():
            transform = parent.transAxes
        case _:
            transform = IdentityTransform()
    locator = StonerInsetLocator([new_bbox.x0, new_bbox.y0, new_bbox.width, new_bbox.height], transform)
    inset_axes.set_axes_locator(locator)  # type: ignore[arg-type]


def _get_inset_axes(ax: Axes) -> List[Axes]:
    """Get a list of axes that overlap the axes given.

    Args:
        ax (Axes): Parent axes.

    Returns:
        list: List of axes that overlap with the given axes and are not the given axes themselves.

    Notes:
        Rather than checking whether we have inset axes, this simply looks for all
        axes in the figure that overlap with the given axes and are not the given axes themselves.
    """
    fig = ax.figure
    container = ax.get_position()
    inset_axes_list = []
    for sub_ax in fig.axes:
        if sub_ax is ax:
            continue
        if container.overlaps(sub_ax.get_position()):
            inset_axes_list.append(sub_ax)
    return inset_axes_list


def _auto_linset_data(
    ax: Axes, axins: Axes, renderer: Any, insets: bool = True
) -> Tuple[List[Bbox], List[Any], List[Tuple[float, float]]]:
    """Return display coordinates for hit testing for "best" positioning.

    Args:
        ax (Axes): Parent axes.
        axins (Axes): Inset axes.
        renderer (Renderer): The figure renderer being used.
        insets (bool): Whether to include inset axes in the calculations. Defaults to True.

    Returns:
        tuple: A tuple containing:
            - bboxes (list): List of bounding boxes of all patches.
            - lines (list): List of `.Path` corresponding to each line.
            - offsets (list): List of (x, y) offsets of all collections.
    """
    bboxes: List[Bbox] = []
    lines: List[Any] = []
    offsets: List[Tuple[float, float]] = []
    inset_axes = _get_inset_axes(ax) if insets else []

    for artist in ax.get_children() + inset_axes:
        _process_artist(artist, renderer, axins, bboxes, lines, offsets)

    return bboxes, lines, offsets


def _handle_line2d(artist: Line2D, lines: List[Any]) -> None:
    """Handle Line2D artist by extracting its transformed path.

    Args:
        artist (Line2D): The Line2D artist to process.
        lines (list): List to append the transformed path to.
    """
    lines.append(artist.get_transform().transform_path(artist.get_path()))


def _handle_rectangle(artist: Rectangle, bboxes: List[Bbox]) -> None:
    """Handle Rectangle artist by extracting its bounding box.

    Args:
        artist (Rectangle): The Rectangle artist to process.
        bboxes (list): List to append the bounding box to.
    """
    bboxes.append(artist.get_bbox().transformed(artist.get_data_transform()))


def _handle_patch(artist: Patch, lines: List[Any]) -> None:
    """Handle Patch artist by extracting its transformed path.

    Args:
        artist (Patch): The Patch artist to process.
        lines (list): List to append the transformed path to.
    """
    lines.append(artist.get_transform().transform_path(artist.get_path()))


def _handle_polycollection(artist: PolyCollection, lines: List[Any]) -> None:
    """Handle PolyCollection artist by extracting all its transformed paths.

    Args:
        artist (PolyCollection): The PolyCollection artist to process.
        lines (list): List to extend with the transformed paths.
    """
    lines.extend(artist.get_transform().transform_path(path) for path in artist.get_paths())


def _handle_collection(artist: Collection, offsets: List[Tuple[float, float]]) -> None:
    """Handle Collection artist by extracting point offsets.

    Args:
        artist (Collection): The Collection artist to process.
        offsets (list): List to extend with transformed offsets.
    """
    _, transOffset, hoffsets, _ = artist._prepare_points()  # type: ignore[attr-defined]
    if hoffsets.size > 0:
        offsets.extend(transOffset.transform(hoffsets))


def _handle_text(artist: Text, renderer: Any, bboxes: List[Bbox]) -> None:
    """Handle Text artist by extracting its window extent.

    Args:
        artist (Text): The Text artist to process.
        renderer (Renderer): The figure renderer being used.
        bboxes (list): List to append the window extent to.
    """
    bboxes.append(artist.get_window_extent(renderer))


def _handle_axes_legend(
    artist: Union[Axes, Legend],
    axins: Axes,
    renderer: Any,
    bboxes: List[Bbox],
    lines: List[Any],
    offsets: List[Tuple[float, float]],
) -> None:
    """Handle Axes or Legend artist by recursively extracting data.

    Args:
        artist (Axes | Legend): The Axes or Legend artist to process.
        axins (Axes): Inset axes to exclude from processing.
        renderer (Renderer): The figure renderer being used.
        bboxes (list): List to extend with bounding boxes.
        lines (list): List to extend with paths.
        offsets (list): List to extend with offsets.
    """
    sub_bboxes, sub_lines, sub_offsets = _auto_linset_data(artist, axins, renderer, insets=False)  # type: ignore[arg-type]
    bboxes.extend(sub_bboxes)
    lines.extend(sub_lines)
    offsets.extend(sub_offsets)


def _process_artist(
    artist: Artist,
    renderer: Any,
    axins: Axes,
    bboxes: List[Bbox],
    lines: List[Any],
    offsets: List[Tuple[float, float]],
) -> None:
    """Process an artist to extract relevant display coordinates.

    Args:
        artist (Artist): The matplotlib artist to process.
        renderer (Renderer): The figure renderer being used.
        axins (Axes): Inset axes to exclude from processing.
        bboxes (list): List to append/extend bounding boxes to.
        lines (list): List to append/extend paths to.
        offsets (list): List to append/extend offsets to.
    """
    match artist:
        case Line2D():
            _handle_line2d(artist, lines)
        case Rectangle():
            _handle_rectangle(artist, bboxes)
        case Patch():
            _handle_patch(artist, lines)
        case PolyCollection():
            _handle_polycollection(artist, lines)
        case Collection():
            _handle_collection(artist, offsets)
        case Text():
            _handle_text(artist, renderer, bboxes)
        case Axes() | Legend() if artist is not axins:
            _handle_axes_legend(artist, axins, renderer, bboxes, lines, offsets)
        case _:
            pass


def calculate_position(inset_bbox: Bbox, parent__bbox: Bbox, loc: int = 1) -> Tuple[float, float]:
    """Calculate the shift in position based on the location of an inset within a parent.

    Args:
        inset_bbox (Bbox): Bounding box of the inset including labels and padding.
        parent_bbox (Bbox): Bounding box of the parent axes.
        loc (int): Location code (1-10 inclusive).

    Returns:
        tuple: The required (dx, dy) shift to align the inset.

    Notes:
        This simply works out which corner of the inset box needs to align to which corner of the parent
        bbox and thus the required dx, dy shift.

    Examples:
        >>> inset_bbox = Bbox.from_bounds(0.1, 0.1, 0.2, 0.2)
        >>> parent_bbox = Bbox.from_bounds(0, 0, 1, 1)
        >>> calculate_position(inset_bbox, parent_bbox, loc=1)
        (0.9, 0.9)
    """
    box_centre = (inset_bbox.x0 + inset_bbox.x1) / 2, (inset_bbox.y0 + inset_bbox.y1) / 2
    parent_centre = (parent__bbox.x0 + parent__bbox.x1) / 2, (parent__bbox.y0 + parent__bbox.y1) / 2
    if loc in [2, 3, 6]:  # Align Left
        dx = parent__bbox.x0 - inset_bbox.x0
    elif loc in [1, 4, 5, 7]:  # align-right
        dx = parent__bbox.x1 - inset_bbox.x1
    else:  # Align centre
        dx = parent_centre[0] - box_centre[0]
    if loc in [1, 2, 9]:
        dy = parent__bbox.y1 - inset_bbox.y1
    elif loc in [3, 4, 8]:
        dy = parent__bbox.y0 - inset_bbox.y0
    else:
        dy = parent_centre[1] - box_centre[1]
    return dx, dy


def new_bbox_for_loc(axins: Axes, ax: Axes, loc: int = 1, padding: Tuple[float, float] = (0.02, 0.02)) -> Bbox:
    """Calculate a new axes bounding box for a given location.

    Args:
        axins (Axes):
            The inset axes to relocate.
        Ax (Axes):
            The parent axes to locate relative to.
        loc (int):
            A location code (1-10) - as per matplotlib legend locations.
        padding (Tuple[float, float]):
            Additional padding (in Axes co-ordinates) to add around the tight bounding box of the inset.

    Returns:
        (Bbox):
            The new bounding box for the axes.
    """
    parent_bbox = ax.get_position()
    inset_bbox_raw = axins.get_tightbbox()
    if inset_bbox_raw is None:
        raise ValueError("Could not get tight bounding box for inset axes")
    inset_bbox = inset_bbox_raw.transformed(ax.figure.transFigure.inverted())

    inset_bbox.update_from_data_xy(  # Adjust the position to allow for the padding
        [
            [inset_bbox.x0 - padding[0], inset_bbox.y0 - padding[1]],
            [inset_bbox.x1 + padding[0], inset_bbox.y1 + padding[1]],
        ]
    )

    dx, dy = calculate_position(inset_bbox, parent_bbox, loc)

    # Get the current inset position and apply our dx,dy shift.
    try:
        inset_location = axins.get_position()
    except AttributeError:
        inset_location = axins.get_window_extent().transformed(ax.transAxes.inverted())
    inset_location.update_from_data_xy(
        [[inset_location.x0 + dx, inset_location.y0 + dy], [inset_location.x1 + dx, inset_location.y1 + dy]]
    )
    return inset_location


def find_best_position(ax: Axes, axins: Axes, renderer: Optional[Any] = None) -> Tuple[int, Bbox]:
    """Calculate a new axes bounding box for a given location.

    Args:
        ax (Axes): The parent axes to locate relative to.
        axins (Axes): The inset axes to relocate.
        renderer (RendererBase): The matplotlib renderer to use for calculating positions.

    Returns:
        Bbox: The new bounding box for the axes.

    Notes:
        This uses a variation on the algorithm used to auto locate matplotlib legends - except it
        takes account of the legend location (!) and any overlapping axes such as other insets. It is
        a rather simple algorithm that just counts the number of collisions with data points, lines, text items
        and the legend and contents of insets. Possibly it should give some weighting to some of these components.

    Examples:
        >>> import matplotlib.pyplot as plt
        >>> fig, ax = plt.subplots()
        >>> axins = fig.add_axes([0.1, 0.1, 0.3, 0.3])
        >>> find_best_position(ax, axins)
        Bbox(...)
    """
    ax.figure.canvas.draw()  # render the figure
    if renderer is None:
        renderer = ax.figure.canvas.get_renderer()  # type: ignore[attr-defined]
    bboxes, lines, offsets = _auto_linset_data(ax, axins, renderer)

    candidates = []
    for idx in range(1, 11):
        insetBox = new_bbox_for_loc(axins, ax, loc=idx).transformed(ax.figure.transFigure)
        # XXX TODO: If markers are present, it would be good to take them
        # into account when checking vertex overlaps in the next line.
        badness = (
            sum(insetBox.count_contains(line.vertices) for line in lines)
            + insetBox.count_contains(offsets)
            + insetBox.count_overlaps(bboxes)
            + sum(line.intersects_bbox(insetBox, filled=False) for line in lines)
        )
        # Include the index to favor lower codes in case of a tie.
        candidates.append((badness, idx, insetBox))
        if badness == 0:
            break

    _, idx, insetBox = min(candidates)

    return idx, insetBox


def copy_properties(obj: Any, properties: dict[str, Any]) -> None:
    """Copy matplotlib properties to an object."""
    for k, v in properties.items():
        if attr := getattr(obj, f"set_{k}", None):
            match v:
                case bool() | int() | float() | str():
                    attr(v)
                case Text():
                    attr(v.get_text(), v.get_fontproperties())
                case _:
                    pass
