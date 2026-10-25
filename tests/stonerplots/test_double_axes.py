"""Shared contracts for independent top and right plotting axes."""

from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_rgba

from stonerplots import DoubleXAxis, DoubleXYAxis, DoubleYAxis

VARIANTS = [
    (DoubleYAxis, "switch_to_y2", ("y",)),
    (DoubleXAxis, "switch_to_x2", ("x",)),
    (DoubleXYAxis, "switch_to_xy2", ("x", "y")),
]


@pytest.fixture(autouse=True)
def close_figures():
    """Release figures created by each test."""
    yield
    plt.close("all")


@pytest.mark.parametrize("manager_class, switch_name, coordinates", VARIANTS)
def test_coordinates_and_style(manager_class, switch_name, coordinates):
    """Only the intended coordinates are independent, coloured and moved."""
    fig, parent = plt.subplots()
    parent.plot([0, 1], [0, 1], label="Primary")
    parent.set(xlabel="Bottom", ylabel="Left")
    with manager_class(ax=parent, colours=("red", "blue"), loc="upper left") as secondary:
        assert plt.gca() is secondary
        secondary.plot([10, 20], [100, 200], label="Secondary")
        secondary.set(xlabel="Top", ylabel="Right")
    assert plt.gca() is parent
    assert len(fig.axes) == 2
    for coordinate, sides in (("x", ("bottom", "top")), ("y", ("left", "right"))):
        shared = getattr(parent, f"get_shared_{coordinate}_axes")().joined(parent, secondary)
        assert shared == (coordinate not in coordinates)
        if coordinate not in coordinates:
            continue
        primary_side, secondary_side = sides
        for axes, side, hidden, colour in (
            (parent, primary_side, secondary_side, "red"),
            (secondary, secondary_side, primary_side, "blue"),
        ):
            axis = getattr(axes, f"{coordinate}axis")
            assert axis.get_ticks_position() == side
            assert axis.get_label_position() == side
            assert not axes.spines[hidden].get_visible()
            assert axes.spines[side].get_edgecolor() == to_rgba(colour)
            assert axis.label.get_color() == colour
            assert all(tick.label1.get_color() == colour for tick in axis.get_major_ticks())
        getattr(parent, f"set_{coordinate}lim")(-5, 5)
        getattr(secondary, f"set_{coordinate}lim")(10, 30)
        assert getattr(parent, f"get_{coordinate}lim")() == (-5, 5)
    assert [text.get_text() for text in parent.get_legend().get_texts()] == ["Primary", "Secondary"]
    assert secondary.get_legend() is None
    fig.canvas.draw()


@pytest.mark.parametrize("manager_class, switch_name, coordinates", VARIANTS)
@pytest.mark.parametrize("switch", [True, False])
@pytest.mark.parametrize("other_figure", [True, False])
def test_current_axes_and_body_exception(manager_class, switch_name, coordinates, switch, other_figure):
    """Explicit and wrapped parent axes preserve the caller's pyplot state."""
    fig, parent = plt.subplots()
    previous_fig, previous = plt.subplots() if other_figure else (fig, parent)
    manager = manager_class(ax=SimpleNamespace(ax=parent), legend=False, **{switch_name: switch})
    with pytest.raises(RuntimeError, match="body failed"):
        with manager as secondary:
            assert plt.gca() is (secondary if switch else previous)
            raise RuntimeError("body failed")
    assert plt.gcf() is previous_fig
    assert plt.gca() is previous
    assert manager.ax2 is secondary
    assert secondary in fig.axes


@pytest.mark.parametrize("manager_class, switch_name, coordinates", VARIANTS)
def test_legend_disabled_and_context_reuse(manager_class, switch_name, coordinates):
    """Disabling merging preserves legends and a manager can be reused."""
    manager = manager_class(legend=False)
    for _ in range(2):
        fig, parent = plt.subplots()
        parent.plot([0, 1], [0, 1], label="Primary")
        primary_legend = parent.legend()
        with manager as secondary:
            secondary.plot([0, 1], [1, 0], label="Secondary")
            secondary_legend = secondary.legend()
        assert parent.get_legend() is primary_legend
        assert secondary.get_legend() is secondary_legend
        assert manager.ax is parent
        assert len(fig.axes) == 2


@pytest.mark.parametrize("manager_class", [DoubleXAxis, DoubleXYAxis])
def test_validation_and_best_legend(manager_class):
    """New variants inherit input validation and automatic legend placement."""
    with pytest.raises(ValueError, match="not recognised"):
        manager_class(loc="invalid")
    with pytest.raises(TypeError, match="location"):
        manager_class(loc=[])
    with pytest.raises(TypeError, match="Colours"):
        manager_class(colours=123)
    _, parent = plt.subplots()
    parent.plot([0, 1], [0, 1], label="Primary")
    with manager_class() as secondary:
        secondary.plot([10, 20], [1, 0], label="Secondary")
    assert len(parent.get_legend().get_texts()) == 2


@pytest.mark.parametrize("layout", [None, "tight", "constrained", "manual"])
def test_double_xy_alignment(layout):
    """The two independent scales remain overlaid through layout and resizing."""
    fig = plt.figure(layout=layout if layout != "manual" else None)
    parent = fig.add_axes([0.2, 0.2, 0.6, 0.6]) if layout == "manual" else fig.add_subplot()
    with DoubleXYAxis(ax=parent, legend=False) as secondary:
        parent.plot([0, 1], [0, 1])
        secondary.plot([10, 20], [100, 200])
        parent.set(xlabel="Primary x", ylabel="Primary y")
        secondary.set(xlabel="Secondary x", ylabel="Secondary y")
    fig.canvas.draw()
    np.testing.assert_allclose(parent.get_position().bounds, secondary.get_position().bounds)
    fig.set_size_inches(8, 6)
    if layout in (None, "manual"):
        parent.set_position([0.15, 0.15, 0.65, 0.65])
    fig.canvas.draw()
    np.testing.assert_allclose(parent.get_position().bounds, secondary.get_position().bounds)


@pytest.mark.parametrize("manager_class, switch_name, coordinates", VARIANTS)
def test_nested_contexts(manager_class, switch_name, coordinates):
    """Nested contexts restore the outer secondary axes and then the original."""
    _, parent = plt.subplots()
    with manager_class(legend=False) as outer:
        with manager_class(legend=False) as inner:
            assert plt.gca() is inner
        assert plt.gca() is outer
    assert plt.gca() is parent


@pytest.mark.parametrize("manager_class, switch_name, coordinates", VARIANTS)
def test_exit_error_restores_axes(manager_class, switch_name, coordinates, monkeypatch):
    """Legend finalisation errors propagate after restoring the previous axes."""
    _, parent = plt.subplots()
    manager = manager_class()

    def fail():
        raise RuntimeError("legend failed")

    monkeypatch.setattr(manager, "_merge_legends", fail)
    with pytest.raises(RuntimeError, match="legend failed"):
        with manager:
            pass
    assert plt.gca() is parent


def test_double_xy_independent_scales_and_tickers():
    """Changing either overlay scale or ticker cannot change the primary axes."""
    from matplotlib.ticker import MultipleLocator

    _, parent = plt.subplots()
    with DoubleXYAxis(legend=False) as secondary:
        secondary.set(xscale="log", yscale="log")
    assert parent.get_xscale() == "linear"
    assert parent.get_yscale() == "linear"
    for coordinate in ("x", "y"):
        original = getattr(parent, f"{coordinate}axis").get_major_locator()
        getattr(secondary, f"{coordinate}axis").set_major_locator(MultipleLocator(2))
        assert getattr(parent, f"{coordinate}axis").get_major_locator() is original
