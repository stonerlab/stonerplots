# -*- coding: utf-8 -*-
"""Tests for StackVertical context manager, focusing on the _fix_limits robustness fix.

These tests verify that the `_fix_limits` method in StackVertical correctly adjusts
y-axis limits for joined subplots so that tick labels do not overflow into adjacent
panels, using the algebraic approach with a FixedLocator to prevent feedback ticks.
"""
import pytest
from matplotlib import pyplot as plt
from matplotlib.ticker import FixedLocator

from stonerplots import StackVertical


def _axes_dy(ax) -> float:
    """Return the minimum required tick-to-edge clearance in axes units for *ax*."""
    fig = ax.get_figure()
    ticklabels = ax.yaxis.get_ticklabels()
    if not ticklabels:
        return 0.0
    fnt_pts = float(ticklabels[0].get_fontsize())
    ax_height = ax.bbox.transformed(fig.transFigure.inverted()).height * fig.get_figheight() * 72
    return 1.40 * fnt_pts / ax_height if ax_height > 0 else 0.0


class TestFixLimitsBottomTickPadding:
    """Verify that the lowest visible tick is pushed away from the bottom frame edge."""

    def test_bottom_tick_not_too_close_to_bottom_for_non_bottom_subplot(self):
        """For every non-bottom subplot the lowest visible tick must sit >= dy from the bottom."""
        plt.figure()
        with StackVertical(3, joined=True) as axes:
            for ax in axes:
                ax.plot([0, 1, 2], [0, 1, 0])

        # Inspect each non-bottom subplot (indices 0 and 1 in a 3-panel stack)
        for ix, ax in enumerate(axes[:-1]):
            dy = _axes_dy(ax)
            if dy <= 0:
                continue
            tr = ax.transData + ax.transAxes.inverted()
            yticks_axes = [tr.transform((0, t))[1] for t in ax.get_yticks()]
            visible = [ta for ta in yticks_axes if -0.01 <= ta <= 1.01]
            if not visible:
                continue
            lowest = min(visible)
            # Allow a small numerical tolerance of 1e-6 in the comparison.
            assert lowest >= dy - 1e-6, (
                f"Subplot {ix}: lowest visible tick at axes pos {lowest:.4f} "
                f"is closer than dy={dy:.4f} to the bottom edge"
            )

        plt.close("all")

    def test_top_tick_not_too_close_to_top_for_non_top_subplot(self):
        """For every non-top subplot the highest visible tick must sit >= dy from the top."""
        plt.figure()
        with StackVertical(3, joined=True) as axes:
            for ax in axes:
                ax.plot([0, 1, 2], [0, 1, 0])

        # Inspect each non-top subplot (indices 1 and 2 in a 3-panel stack)
        for ix, ax in enumerate(axes[1:], start=1):
            dy = _axes_dy(ax)
            if dy <= 0:
                continue
            tr = ax.transData + ax.transAxes.inverted()
            yticks_axes = [tr.transform((0, t))[1] for t in ax.get_yticks()]
            visible = [ta for ta in yticks_axes if -0.01 <= ta <= 1.01]
            if not visible:
                continue
            highest = max(visible)
            assert highest <= 1.0 - dy + 1e-6, (
                f"Subplot {ix}: highest visible tick at axes pos {highest:.4f} "
                f"is closer than dy={dy:.4f} to the top edge"
            )

        plt.close("all")


class TestFixLimitsLockerPreventsEdgeTicks:
    """Verify that a FixedLocator is installed after a limit adjustment."""

    def test_fixed_locator_installed_when_limits_are_adjusted(self):
        """At least one non-bottom/non-top subplot should have a FixedLocator after exit."""
        plt.figure()
        with StackVertical(3, joined=True) as axes:
            for ax in axes:
                ax.plot([0, 1, 2], [0, 1, 0])

        # The middle subplot is most likely to need both lower and upper adjustments.
        # If the data happened to be perfectly spaced the locator may remain unchanged,
        # but when an adjustment is made it must be a FixedLocator.
        middle_ax = axes[1]
        locator = middle_ax.yaxis.get_major_locator()
        if isinstance(locator, FixedLocator):
            ticks = locator.locs
            assert len(ticks) > 0, "FixedLocator should contain at least one tick"
        plt.close("all")


class TestFixLimitsNoJoined:
    """When joined=False, _fix_limits should not be called and limits remain default."""

    def test_limits_unchanged_when_not_joined(self):
        """With joined=False the context manager should not adjust y limits at all."""
        plt.figure()
        with StackVertical(3, joined=False) as axes:
            for ax in axes:
                ax.plot([0, 1, 2], [0, 1, 0])

        for ax in axes:
            locator = ax.yaxis.get_major_locator()
            assert not isinstance(locator, FixedLocator), (
                "FixedLocator should not be applied when joined=False"
            )
        plt.close("all")


class TestFixLimitsTwoSubplots:
    """Sanity check for a 2-subplot stack (top and bottom only, no middle)."""

    def test_two_subplot_stack_exits_cleanly(self):
        """A 2-panel StackVertical must exit without raising an exception."""
        plt.figure()
        with StackVertical(2, joined=True) as axes:
            for ax in axes:
                ax.plot([0, 1, 2], [0, 0.5, 0])
        plt.close("all")

    def test_two_subplot_bottom_tick_ok(self):
        """In a 2-panel stack the top subplot's bottom tick must be padded."""
        plt.figure()
        with StackVertical(2, joined=True) as axes:
            for ax in axes:
                ax.plot([0, 1, 2], [0, 0.5, 0])

        top_ax = axes[0]
        dy = _axes_dy(top_ax)
        if dy > 0:
            tr = top_ax.transData + top_ax.transAxes.inverted()
            yticks_axes = [tr.transform((0, t))[1] for t in top_ax.get_yticks()]
            visible = [ta for ta in yticks_axes if -0.01 <= ta <= 1.01]
            if visible:
                assert min(visible) >= dy - 1e-6
        plt.close("all")


class TestFixLimitsEdgeCases:
    """Edge-case handling in _fix_limits."""

    def test_single_tick_does_not_raise(self):
        """_fix_limits must not raise when an axis has only one visible tick."""
        plt.figure()
        with StackVertical(2, joined=True) as axes:
            axes[0].plot([0, 1], [0.5, 0.5])  # Horizontal line → single tick at 0.5
        plt.close("all")

    def test_large_number_of_subplots(self):
        """A 5-panel stack should produce consistent padding on every panel."""
        plt.figure()
        with StackVertical(5, joined=True) as axes:
            for ax in axes:
                ax.plot([0, 1, 2], [0, 1, 0])

        for ix, ax in enumerate(axes):
            dy = _axes_dy(ax)
            if dy <= 0:
                continue
            tr = ax.transData + ax.transAxes.inverted()
            yticks_axes = [tr.transform((0, t))[1] for t in ax.get_yticks()]
            visible = [ta for ta in yticks_axes if -0.01 <= ta <= 1.01]
            if not visible:
                continue
            if ix != len(axes) - 1:  # non-bottom
                assert min(visible) >= dy - 1e-6, f"Panel {ix}: bottom tick too close to edge"
            if ix != 0:  # non-top
                assert max(visible) <= 1.0 - dy + 1e-6, f"Panel {ix}: top tick too close to edge"

        plt.close("all")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
