# -*- coding: utf-8 -*-
"""Utility functions to support the Context managers.

BAsed on code used in matplotlib to automatically position a legend.
"""
from matplotlib.axes import Axes
from matplotlib.axes._base import _TransformedBoundsLocator
from matplotlib.collections import Collection, PolyCollection
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.text import Text
from matplotlib.transforms import IdentityTransform


def move_inset(parent, inset_axes, new_bbox):
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
    locator = _TransformedBoundsLocator([new_bbox.x0, new_bbox.y0, new_bbox.width, new_bbox.height], transform)
    inset_axes.set_axes_locator(locator)


def _get_inset_axes(ax):
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


def _auto_linset_data(ax, axins, renderer, insets=True):
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
    bboxes, lines, offsets = [], [], []
    inset_axes = _get_inset_axes(ax) if insets else []

    for artist in ax.get_children() + inset_axes:
        _process_artist(artist,renderer, axins, bboxes, lines, offsets)

    return bboxes, lines, offsets


def _process_artist(artist, renderer, axins, bboxes, lines, offsets):
    """Process an artist to extract relevant display coordinates."""
    match artist:
        case Line2D():
            lines.append(artist.get_transform().transform_path(artist.get_path()))
        case Rectangle():
            bboxes.append(artist.get_bbox().transformed(artist.get_data_transform()))
        case Patch():
            lines.append(artist.get_transform().transform_path(artist.get_path()))
        case PolyCollection():
            lines.extend(artist.get_transform().transform_path(path) for path in artist.get_paths())
        case Collection():
            _, transOffset, hoffsets, _ = artist._prepare_points()
            if hoffsets.size>0:
                offsets.extend(transOffset.transform(hoffsets))
        case Text():
            bboxes.append(artist.get_window_extent(renderer))
        case Axes() | Legend() if artist is not axins:
            sub_bboxes, sub_lines, sub_offsets = _auto_linset_data(artist, axins, renderer, insets=False)
            bboxes.extend(sub_bboxes)
            lines.extend(sub_lines)
            offsets.extend(sub_offsets)
        case _:
            pass


def calculate_position(inset_bbox, parent__bbox, loc=1):
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


def new_bbox_for_loc(axins, ax, loc=1, padding=(0.02, 0.02)):
    """Calcualte a new  axesbounding box for a given location.

    Args:
        axins (Axes):
            The inset axes to relocate.
        Ax (Axes):
            The parent axes to locate relative to.
        loc (int):
            A location code (1-10) - as per matplotlib legend locations.
        padding (Tuple[flota, float]):
            Additional padding (in Axes co-ordinates) to add around the tight bounding box of the inset.

    Returns:
        (Bbox):
            The new bounding box for the axes.
    """
    parent_bbox = ax.get_position()
    inset_bbox = axins.get_tightbbox().transformed(ax.figure.transFigure.inverted())

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


def find_best_position(ax, axins, renderer=None):
    """Calculate a new axes bounding box for a given location.

    Args:
        axins (Axes): The inset axes to relocate.
        ax (Axes): The parent axes to locate relative to.
        loc (int): A location code (1-10) - as per matplotlib legend locations.
        padding (Tuple[float, float]):
            Additional padding (in Axes coordinates) to add around the tight
            bounding box of the inset.

    Returns:
        Bbox: The new bounding box for the axes.

    Notes:
        This uses a variation on the algorithm used to auto locate matplolotlib legends - except it
        takes account of the legend location (!) and any overlapping axes such as other insets. It is
        a rather simple algorithm that just counts the number of collisions with data points, lines, text items
        and the legend and contents of insets. Possibly it should give some weighting to some of there components.

    Examples:
        >>> fig, ax = plt.subplots()
        >>> axins = fig.add_axes([0.1, 0.1, 0.3, 0.3])
        >>> new_bbox_for_loc(axins, ax, loc=1)
        Bbox(...)
    """
    ax.figure.canvas.draw()  # render the figure
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

def copy_properties(obj,properties):
    """Copy matplotlib properties to an object."""
    for k,v in properties.items():
        if attr:=getattr(obj,f"set_{k}",None):
            match v:
                case bool()|int()|float()|str():
                    attr(v)
                case Text():
                    attr(v.get_text(),v.get_fontproperties())
                case _:
                    pass


