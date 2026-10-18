"""Regression tests for independent tickers and inset context state (issues #79 and #80)."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.ticker import AutoMinorLocator, MultipleLocator, NullFormatter, NullLocator, ScalarFormatter

from stonerplots import DoubleYAxis, InsetPlot, PlotLabeller, StackVertical


@pytest.fixture(autouse=True)
def close_figures():
    """Release figures owned by these tests."""
    yield
    plt.close("all")


@pytest.mark.parametrize("configured", [False, True])
@pytest.mark.parametrize("coordinate", ["x", "y", "z"])
def test_independent_tickers(configured, coordinate):
    """Each axis and ticker slot owns its state, including configured, bound inputs."""
    source = plt.figure().add_subplot(projection="3d")
    source_axis = getattr(source, f"{coordinate}axis")
    locator = MultipleLocator(0.5)
    formatter = ScalarFormatter(useOffset=False)
    formatter.set_powerlimits([-2, 2])
    source_axis.set_major_locator(locator)
    source_axis.set_major_formatter(formatter)
    templates = [locator, formatter] if configured else [MultipleLocator, ScalarFormatter]

    with PlotLabeller(**{coordinate: templates}):
        fig = plt.figure()
        axes = [fig.add_subplot(1, 2, i, projection="3d") for i in (1, 2)]
        for ax, lower in zip(axes, (0, 10)):
            getattr(ax, f"set_{coordinate}lim")(lower, lower + 2)
            axis = getattr(ax, f"{coordinate}axis")
            axis.set_minor_locator(AutoMinorLocator())
            axis.set_minor_formatter(ScalarFormatter())

    tickers = []
    for ax, lower in zip(axes, (0, 10)):
        axis = getattr(ax, f"{coordinate}axis")
        for which in ("major", "minor"):
            loc = getattr(axis, f"get_{which}_locator")()
            fmt = getattr(axis, f"get_{which}_formatter")()
            assert loc.axis is axis
            assert fmt.axis is axis
            tickers.extend((loc, fmt))
            expected = MultipleLocator(0.5 if configured else 1).tick_values(lower, lower + 2)
            np.testing.assert_allclose(loc(), expected)
            if configured:
                assert not fmt.get_useOffset()
    assert len({id(ticker) for ticker in tickers}) == len(tickers)
    assert locator.axis is source_axis
    assert formatter.axis is source_axis
    if configured:
        # Mutating one copy's configuration must not affect another copy or the template.
        left = getattr(axes[0], f"{coordinate}axis").get_major_formatter()
        right = getattr(axes[1], f"{coordinate}axis").get_major_formatter()
        left._powerlimits[0] = -9
        assert right._powerlimits == [-2, 2]
        assert formatter._powerlimits == [-2, 2]
    fig.canvas.draw()


def test_null_minor_tickers_remain_disabled():
    """Supplying a major locator must not enable previously disabled minor ticks."""
    with PlotLabeller(y=[MultipleLocator, ScalarFormatter]):
        _, ax = plt.subplots()
    assert isinstance(ax.yaxis.get_minor_locator(), NullLocator)
    assert isinstance(ax.yaxis.get_minor_formatter(), NullFormatter)


def test_labeller_reuse_creates_new_tickers():
    """A reused labeller cannot bind an earlier plot's ticker to a later plot."""
    labeller = PlotLabeller(y=MultipleLocator(0.5))
    with labeller:
        _, first = plt.subplots()
    with labeller:
        _, second = plt.subplots()
    assert first.yaxis.get_major_locator() is not second.yaxis.get_major_locator()
    assert first.yaxis.get_major_locator().axis is first.yaxis


@pytest.mark.parametrize("switch", [False, True])
@pytest.mark.parametrize("other_figure", [False, True])
@pytest.mark.parametrize("loc", ["upper right", "best"])
def test_inset_restores_previous_axes_and_preserves_handle(switch, other_figure, loc):
    """Inset entry and exit preserve pyplot state and keep the returned axes usable."""
    fig, parent = plt.subplots()
    if other_figure:
        previous_fig, previous = plt.subplots()
    else:
        previous_fig, previous = fig, parent
    manager = InsetPlot(ax=parent, loc=loc, switch_to_inset=switch)
    with manager as inset:
        assert plt.gca() is (inset if switch else previous)
        (line,) = inset.plot([0, 1], [0, 1])
    assert plt.gcf() is previous_fig
    assert plt.gca() is previous
    assert manager.axins is inset
    assert inset in fig.axes
    assert line.axes is inset
    inset.set_title("Still usable")
    fig.canvas.draw()


def test_nested_and_sequential_insets_restore_each_target():
    """Nested contexts return to the outer inset, then to the original axes."""
    _, parent = plt.subplots()
    with InsetPlot(loc="upper right") as outer:
        with InsetPlot(loc="lower left") as inner:
            assert plt.gca() is inner
        assert plt.gca() is outer
    assert plt.gca() is parent
    with InsetPlot(loc="lower right"):
        pass
    assert plt.gca() is parent


@pytest.mark.parametrize("switch", [False, True])
def test_inset_restores_on_body_exception(switch):
    """Exceptions propagate after restoring the axes saved on entry."""
    _, parent = plt.subplots()
    with pytest.raises(ValueError, match="body failed"):
        with InsetPlot(switch_to_inset=switch):
            raise ValueError("body failed")
    assert plt.gca() is parent


def test_inset_restores_on_layout_exception(monkeypatch):
    """A failure during exit must still restore pyplot state."""
    _, parent = plt.subplots()

    def fail(*args, **kwargs):
        """Simulate an inset placement failure."""
        raise RuntimeError("layout failed")

    monkeypatch.setattr("stonerplots.context.inset_plot.new_bbox_for_loc", fail)
    with pytest.raises(RuntimeError, match="layout failed"):
        with InsetPlot(loc="upper right"):
            pass
    assert plt.gca() is parent


@pytest.mark.parametrize("panels", [2, 6])
def test_stacked_layout_batches_canvas_draws(monkeypatch, panels):
    """Stack layout draws a fixed number of times regardless of the panel count (#56)."""
    fig = plt.figure()
    draws = []
    original_draw = fig.canvas.draw

    def draw(*args, **kwargs):
        """Count full renders while retaining real layout calculations."""
        draws.append(None)
        return original_draw(*args, **kwargs)

    with StackVertical(panels, figure=fig) as axes:
        for ax in axes:
            ax.plot([0, 1, 2], [0, 1, 0])
        monkeypatch.setattr(fig.canvas, "draw", draw)
    assert len(draws) == 2


@pytest.mark.parametrize(
    "colours, expected",
    [(None, []), ("red", [0, -1]), ("red, blue", [0, 1, -1, -2]), ([None, "blue"], [1, -1])],
)
def test_double_y_colour_indices(colours, expected):
    """Colour checks use parsed entries and support all valid negative indices (#50)."""
    manager = DoubleYAxis(colours=colours)
    for index in range(-3, 4):
        assert manager.good_colour(index) == (index in expected)
