"""Behavioural checks for dataset discovery, grouping and vertical offsets."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from stonerplots import OffsetPlots


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


@pytest.mark.parametrize("logarithmic", [False, True])
def test_paired_lines_and_scatter(logarithmic):
    x, y = np.arange(3), np.array([1.0, 2.0, 3.0])
    with OffsetPlots(offset=4, factor=3):
        _, ax = plt.subplots()
        if logarithmic:
            ax.set_yscale("log")
        # Pairing must also work when the two types are plotted in batches.
        lines = [ax.plot(x, y)[0] for _ in range(3)]
        points = [ax.scatter(x, y) for _ in range(3)]
    for index, (line, scatter) in enumerate(zip(lines, points)):
        expected = y * 3**index if logarithmic else y + 4 * index
        np.testing.assert_allclose(line.get_ydata(), expected)
        np.testing.assert_allclose(scatter.get_offsets()[:, 1], expected)
        np.testing.assert_allclose(scatter.get_offsets()[:, 0], x)
    np.testing.assert_array_equal(y, [1, 2, 3])
    assert ax.get_ylim()[1] > expected.max()


@pytest.mark.parametrize("pair", [False, "auto"])
def test_unpaired_creation_order(pair):
    with OffsetPlots(offset=2, pair=pair):
        _, ax = plt.subplots()
        first = ax.scatter([0, 1], [1, 2])
        second = ax.plot([0, 1], [1, 2])[0]
        third = ax.plot([0, 1], [1, 2])[0]
    np.testing.assert_allclose(first.get_offsets()[:, 1], [1, 2])
    np.testing.assert_allclose(second.get_ydata(), [3, 4])
    np.testing.assert_allclose(third.get_ydata(), [5, 6])


def test_pair_false_separates_equal_counts():
    with OffsetPlots(pair=False, offset=-2):
        _, ax = plt.subplots()
        ax.plot([1, 2])
        scatter = ax.scatter([0, 1], [1, 2])
    np.testing.assert_allclose(scatter.get_offsets()[:, 1], [-1, 0])


@pytest.mark.parametrize("include_open", [False, True])
def test_existing_axes_and_restore(include_open):
    fig, old = plt.subplots()
    old.plot([1, 2])
    second = old.plot([1, 2])[0]
    with OffsetPlots(include_open=include_open, offset=5):
        new = fig.add_subplot(212)
        new.plot([1, 2])
        new_second = new.plot([1, 2])[0]
    np.testing.assert_allclose(second.get_ydata(), [6, 7] if include_open else [1, 2])
    np.testing.assert_allclose(new_second.get_ydata(), [6, 7])
    assert plt.gca() is old


def test_each_axes_independent_and_context_reusable():
    context = OffsetPlots(offset=3)
    for _ in range(2):
        with context:
            _, axes = plt.subplots(1, 2)
            for ax in axes:
                ax.scatter([0, 1], [1, 2])
                ax.scatter([0, 1], [1, 2])
        for ax in axes:
            np.testing.assert_allclose(ax.collections[1].get_offsets()[:, 1], [4, 5])
            assert ax.get_ylim()[1] > 5


@pytest.mark.parametrize("fmt", ["o-", "none"])
@pytest.mark.parametrize("logarithmic", [False, True])
def test_complete_errorbars(fmt, logarithmic):
    y = np.array([2.0, 3.0])
    with OffsetPlots(offset=5, factor=4):
        _, ax = plt.subplots()
        if logarithmic:
            ax.set_yscale("log")
        first = ax.errorbar([1, 2], y, yerr=[[0.2, 0.3], [0.4, 0.5]], xerr=0.1, fmt=fmt, capsize=4)
        second = ax.errorbar([1, 2], y, yerr=[[0.2, 0.3], [0.4, 0.5]], xerr=0.1, fmt=fmt, capsize=4)

    def expected(values):
        return values * 4 if logarithmic else values + 5

    if fmt != "none":
        np.testing.assert_allclose(second.lines[0].get_ydata(), expected(y))
    for original, shifted in zip(first.lines[1], second.lines[1]):
        np.testing.assert_allclose(shifted.get_ydata(), expected(np.array(original.get_ydata(), dtype=float)))
        np.testing.assert_allclose(shifted.get_xdata(orig=False), original.get_xdata(orig=False))
    for original, shifted in zip(first.lines[2], second.lines[2]):
        before, after = np.array(original.get_segments()), np.array(shifted.get_segments())
        np.testing.assert_allclose(after[:, :, 1], expected(before[:, :, 1]))
        np.testing.assert_allclose(after[:, :, 0], before[:, :, 0])
    assert ax.get_ylim()[1] > expected(np.array(3.5))
    np.testing.assert_array_equal(y, [2, 3])


def test_errorbars_pair_with_scatter_without_counting_caps():
    with OffsetPlots(offset=5, pair=True):
        _, ax = plt.subplots()
        for _ in range(2):
            error = ax.errorbar([0, 1], [1, 2], yerr=0.2, capsize=3)
            points = ax.scatter([0, 1], [1, 2])
    np.testing.assert_allclose(error.lines[0].get_ydata(), [6, 7])
    np.testing.assert_allclose(points.get_offsets()[:, 1], [6, 7])


@pytest.mark.parametrize("option", ["lines", "scatter", "errorbars"])
def test_artist_selection(option):
    with OffsetPlots(offset=5, pair=False, **{option: False}):
        _, ax = plt.subplots()
        line = ax.plot([1, 2])[0]
        points = ax.scatter([0, 1], [1, 2])
        error = ax.errorbar([0, 1], [1, 2], yerr=0.2, capsize=3)
    if option == "lines":
        np.testing.assert_allclose(line.get_ydata(), [1, 2])
        np.testing.assert_allclose(error.lines[0].get_ydata(orig=False), [1, 2])
    elif option == "scatter":
        np.testing.assert_allclose(points.get_offsets()[:, 1], [1, 2])
        np.testing.assert_allclose(error.lines[0].get_ydata(), [6, 7])
    else:
        np.testing.assert_allclose(error.lines[0].get_ydata(orig=False), [1, 2])
        np.testing.assert_allclose(points.get_offsets()[:, 1], [6, 7])


def test_reference_artists_masks_and_explicit_limits():
    with OffsetPlots(offset=5):
        _, ax = plt.subplots()
        reference = ax.axhline(3)
        fill = ax.fill_between([0, 1], [0, 0], [2, 2])
        ax.plot([1, 2, 3])
        line = ax.plot(np.ma.array([1, 2, 3], mask=[False, True, False]))[0]
        ax.set_ylim(-1, 20)
        ax.set_xlim(-2, 5)
    np.testing.assert_allclose(reference.get_ydata(), [3, 3])
    np.testing.assert_allclose(line.get_ydata().compressed(), [6, 8])
    assert ax.get_ylim() == (-1, 20)
    assert ax.get_xlim() == (-2, 5)
    assert fill in ax.collections


def test_exception_skips_offsets_and_restores_state():
    _, original = plt.subplots()
    context = OffsetPlots()
    with pytest.raises(RuntimeError, match="plot failed"):
        with context:
            _, ax = plt.subplots()
            ax.plot([1, 2])
            line = ax.plot([1, 2])[0]
            raise RuntimeError("plot failed")
    np.testing.assert_allclose(line.get_ydata(), [1, 2])
    assert plt.gca() is original
    assert not context._existing_open_axes


def test_strict_pairing_validates_before_any_offsets():
    _, original = plt.subplots()
    with pytest.raises(ValueError, match="equal nonzero"):
        with OffsetPlots(pair=True):
            _, axes = plt.subplots(1, 2)
            for _ in range(2):
                line = axes[0].plot([1, 2])[0]
                axes[0].scatter([0, 1], [1, 2])
            axes[1].plot([1, 2])
    np.testing.assert_allclose(line.get_ydata(), [1, 2])
    assert plt.gca() is original


def test_empty_single_and_unsupported_axes():
    with OffsetPlots():
        _, ax = plt.subplots()
        empty = ax.plot([], [])[0]
        line = ax.plot([1, 2])[0]
        polar = plt.figure().add_subplot(projection="polar")
        polar.plot([1, 2])
        ignored = polar.plot([1, 2])[0]
    np.testing.assert_allclose(line.get_ydata(), [1, 2])
    np.testing.assert_allclose(ignored.get_ydata(), [1, 2])
    assert len(empty.get_ydata()) == 0
    plt.close("all")
    with OffsetPlots():
        pass
    assert not plt.get_fignums()


@pytest.mark.parametrize(
    "kwargs",
    [{"offset": np.nan}, {"offset": np.inf}, {"factor": 0}, {"factor": -1}, {"factor": np.inf}, {"pair": "yes"}],
)
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        OffsetPlots(**kwargs)
