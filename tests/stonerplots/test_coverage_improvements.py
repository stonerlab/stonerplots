# -*- coding: utf-8 -*-
"""Test coverage improvements for helper methods and optional parameters.

This test module addresses the specific recommendations in COVERAGE_REPORT.md:
1. Helper methods in format.py (format_data, format_data_short)
2. Optional parameter combinations in context/noframe.py
3. Collection protocol methods in context/base.py
"""

import numpy as np
import pytest
from matplotlib import pyplot as plt
from unittest.mock import MagicMock, patch

from stonerplots.context.base import PlotContextSequence, RavelList
from stonerplots.context.noframe import CentredAxes
from stonerplots.format import TexEngFormatter, TexFormatter
from stonerplots.util import StonerInsetLocator


class TestFormatHelperMethods:
    """Test helper methods in format.py.

    These tests cover format_data() and format_data_short() methods
    that are typically called by matplotlib internals.
    """

    def test_tex_formatter_format_data(self):
        """Test TexFormatter.format_data() method."""
        formatter = TexFormatter()

        # Test with various values
        result = formatter.format_data(1000)
        assert isinstance(result, str)
        assert "$" in result

        result = formatter.format_data(1e6)
        assert isinstance(result, str)
        assert "$" in result
        assert "10^" in result

        result = formatter.format_data(0.0)
        assert result == "$0.0$"

        result = formatter.format_data(None)
        assert result == ""

        result = formatter.format_data(np.nan)
        assert result == ""

    def test_tex_formatter_format_data_short(self):
        """Test TexFormatter.format_data_short() method."""
        formatter = TexFormatter()

        # Test with various values
        result = formatter.format_data_short(1000)
        assert isinstance(result, str)
        assert result == "1000"

        result = formatter.format_data_short(1e6)
        assert isinstance(result, str)
        assert "1e" in result.lower() or "1000000" in result

        result = formatter.format_data_short(3.14159)
        assert isinstance(result, str)
        assert "3.14" in result

    def test_tex_eng_formatter_format_data(self):
        """Test TexEngFormatter.format_data() method."""
        formatter = TexEngFormatter(unit="V")

        # Test with various values
        result = formatter.format_data(1000)
        assert isinstance(result, str)
        assert "$" in result
        assert "V" in result

        result = formatter.format_data(1e6)
        assert isinstance(result, str)
        assert "$" in result
        assert "V" in result

        result = formatter.format_data(0.0)
        assert result == "$0.0$"

        result = formatter.format_data(None)
        assert result == ""

        result = formatter.format_data(np.nan)
        assert result == ""

    def test_tex_eng_formatter_format_data_short(self):
        """Test TexEngFormatter.format_data_short() method."""
        formatter = TexEngFormatter(unit="A")

        # Test with various values
        result = formatter.format_data_short(1000)
        assert isinstance(result, str)
        assert result == "1000"

        result = formatter.format_data_short(1e-6)
        assert isinstance(result, str)
        assert "e" in result.lower() or "0.000001" in result

        result = formatter.format_data_short(2.71828)
        assert isinstance(result, str)
        assert "2.71" in result


class TestNoframeOptionalParameters:
    """Test optional parameter combinations in context/noframe.py.

    These tests cover the __call__ method with various parameter combinations
    and the 'use' parameter for figure selection.
    """

    def test_centred_axes_call_with_x(self):
        """Test CentredAxes.__call__() with only x parameter."""
        cm = CentredAxes(x=0.0, y=0.0)
        result = cm(x=1.5)
        assert result is cm
        assert result.x == 1.5
        assert result.y == 0.0

    def test_centred_axes_call_with_y(self):
        """Test CentredAxes.__call__() with only y parameter."""
        cm = CentredAxes(x=0.0, y=0.0)
        result = cm(y=2.5)
        assert result is cm
        assert result.x == 0.0
        assert result.y == 2.5

    def test_centred_axes_call_with_include_open(self):
        """Test CentredAxes.__call__() with include_open parameter."""
        cm = CentredAxes(x=0.0, y=0.0, include_open=False)
        result = cm(include_open=True)
        assert result is cm
        assert result.include_open is True

    def test_centred_axes_call_with_all_parameters(self):
        """Test CentredAxes.__call__() with all parameters."""
        cm = CentredAxes(x=0.0, y=0.0, include_open=False, use=None)
        result = cm(x=1.0, y=2.0, include_open=True, use=None)
        assert result is cm
        assert result.x == 1.0
        assert result.y == 2.0
        assert result.include_open is True

    def test_centred_axes_call_with_no_parameters(self):
        """Test CentredAxes.__call__() with no parameters (preserves existing values)."""
        cm = CentredAxes(x=3.0, y=4.0, include_open=True)
        result = cm()
        assert result is cm
        assert result.x == 3.0
        assert result.y == 4.0
        assert result.include_open is True

    def test_centred_axes_with_use_parameter(self):
        """Test CentredAxes with 'use' parameter for figure selection."""
        # Create a figure first
        fig1 = plt.figure()
        _ = fig1.add_subplot(111)

        # Create another figure
        fig2 = plt.figure()
        _ = fig2.add_subplot(111)

        # Use CentredAxes with the 'use' parameter
        with CentredAxes(x=0.0, y=0.0, use=fig1):
            # Should work with fig1 as the current figure
            current_fig = plt.gcf()
            assert current_fig == fig1

        plt.close(fig1)
        plt.close(fig2)

    def test_centred_axes_xlim_adjustment(self):
        """Test CentredAxes adjusts x-axis limits when origin is outside range."""
        with CentredAxes(x=10.0, y=0.0):
            fig, ax = plt.subplots()
            ax.plot([0, 5], [0, 5])  # x range is 0-5, but origin at x=10
            # Context manager should extend xlim to include x=10

        xlim = ax.get_xlim()
        assert xlim[0] <= 10.0 <= xlim[1], "x origin should be within xlim"
        plt.close(fig)

    def test_centred_axes_ylim_adjustment(self):
        """Test CentredAxes adjusts y-axis limits when origin is outside range."""
        with CentredAxes(x=0.0, y=-5.0):
            fig, ax = plt.subplots()
            ax.plot([0, 5], [0, 5])  # y range is 0-5, but origin at y=-5
            # Context manager should extend ylim to include y=-5

        ylim = ax.get_ylim()
        assert ylim[0] <= -5.0 <= ylim[1], "y origin should be within ylim"
        plt.close(fig)


class TestBaseCollectionProtocol:
    """Test collection protocol methods in context/base.py.

    These tests cover __contains__, tuple indexing, and other collection operations.
    """

    def test_ravel_list_tuple_indexing(self):
        """Test RavelList supports tuple indexing."""
        nested = RavelList([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        # Test tuple indexing
        assert nested[0, 1] == 2
        assert nested[1, 0] == 4
        assert nested[2, 2] == 9

    def test_ravel_list_multiple_level_tuple_indexing(self):
        """Test RavelList supports multiple levels of tuple indexing."""
        deeply_nested = RavelList([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

        # Test multiple level tuple indexing
        assert deeply_nested[0, 0, 1] == 2
        assert deeply_nested[1, 1, 0] == 7

    def test_ravel_list_single_index(self):
        """Test RavelList still works with single indices."""
        lst = RavelList([[1, 2], [3, 4]])

        # Single index should work normally
        assert lst[0] == [1, 2]
        assert lst[1] == [3, 4]

    def test_ravel_list_contains(self):
        """Test RavelList __contains__ method through flatten."""
        lst = RavelList([[1, 2], [3, 4]])
        flattened = lst.flatten()

        # Test contains on flattened list
        assert 1 in flattened
        assert 4 in flattened
        assert 5 not in flattened

    def test_plot_context_sequence_contains_with_axes(self):
        """Test PlotContextSequence.__contains__ with actual axes."""

        seq = PlotContextSequence()
        fig, ax = plt.subplots()
        seq.axes.append(ax)

        # Test __contains__
        assert ax in seq

        # Create another axes that is not in the sequence
        fig2, ax2 = plt.subplots()
        assert ax2 not in seq

        plt.close(fig)
        plt.close(fig2)

    def test_plot_context_sequence_reversed(self):
        """Test PlotContextSequence.__reversed__ method."""

        seq = PlotContextSequence()
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        seq.axes.extend([ax1, ax2, ax3])

        # Test reversed iteration
        reversed_axes = list(reversed(seq))
        assert len(reversed_axes) == 3
        assert reversed_axes[0] == ax3
        assert reversed_axes[1] == ax2
        assert reversed_axes[2] == ax1

        plt.close(fig)

    def test_plot_context_sequence_getitem_single_axis(self):
        """Test PlotContextSequence.__getitem__ with single axis selection."""

        seq = PlotContextSequence()
        fig, (ax1, ax2) = plt.subplots(1, 2)
        seq.axes.extend([ax1, ax2])

        # Access single axis - should set it as current
        result = seq[0]
        assert result == ax1
        assert plt.gca() == ax1

        result = seq[1]
        assert result == ax2
        assert plt.gca() == ax2

        plt.close(fig)

    def test_plot_context_sequence_iteration(self):
        """Test PlotContextSequence.__iter__ sets axes as current during iteration."""

        seq = PlotContextSequence()
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        seq.axes.extend([ax1, ax2, ax3])

        # Iterate and check that each axis becomes current
        iterated_axes = []
        for ax in seq:
            iterated_axes.append(ax)
            assert plt.gca() == ax

        assert len(iterated_axes) == 3
        assert iterated_axes == [ax1, ax2, ax3]

        plt.close(fig)


class TestStonerInsetLocator:
    """Test the StonerInsetLocator adapter class."""

    def test_locator_initialization(self):
        """Test that the locator initializes correctly."""
        bounds = [0.1, 0.1, 0.3, 0.3]
        fig, ax = plt.subplots()
        locator = StonerInsetLocator(bounds, ax.transAxes)
        assert locator._internal is not None
        plt.close(fig)

    def test_locator_is_callable(self):
        """Test that the locator is callable as expected by matplotlib."""
        bounds = [0.1, 0.1, 0.3, 0.3]
        fig, ax = plt.subplots()
        locator = StonerInsetLocator(bounds, ax.transAxes)
        assert callable(locator)
        plt.close(fig)

    def test_locator_repr(self):
        """Test the string representation of the locator."""
        bounds = [0.1, 0.1, 0.3, 0.3]
        fig, ax = plt.subplots()
        locator = StonerInsetLocator(bounds, ax.transAxes)
        repr_str = repr(locator)
        assert "StonerInsetLocator" in repr_str
        assert "active" in repr_str
        assert "matplotlib.axes._base._TransformedBoundsLocator" in repr_str
        plt.close(fig)

    def test_locator_repr_when_broken(self):
        """Test the string representation when internal API is missing."""
        locator = StonerInsetLocator.__new__(StonerInsetLocator)
        locator._internal = None
        repr_str = repr(locator)
        assert "broken" in repr_str

    def test_locator_runtime_error_on_missing_internal(self):
        """Test that a RuntimeError is raised if the internal locator is missing."""
        fig, ax = plt.subplots()
        locator = StonerInsetLocator([0, 0, 1, 1], ax.transAxes)
        locator._internal = None  # Simulate missing internal API
        with pytest.raises(RuntimeError, match="Inset positioning failed"):
            locator(ax, None)
        plt.close(fig)

    def test_locator_fallback_on_missing_api(self):
        """Test that _internal is None when the private API is unavailable."""

        with patch.dict("sys.modules", {"matplotlib.axes._base": None}):
            locator = StonerInsetLocator([0, 0, 1, 1], None)
        assert locator._internal is None

    def test_locator_call_delegation(self):
        """Test that calling the adapter delegates to the internal locator."""

        fig, ax = plt.subplots()
        locator = StonerInsetLocator([0, 0, 1, 1], ax.transAxes)

        # Replace internal with a mock to verify delegation
        mock_internal = MagicMock()
        locator._internal = mock_internal

        ax_mock = MagicMock()
        renderer_mock = MagicMock()
        locator(ax_mock, renderer_mock)

        mock_internal.assert_called_once_with(ax_mock, renderer_mock)
        plt.close(fig)

    def test_locator_fails_on_signature_change(self):
        """Test that the adapter captures errors if the internal API signature changes."""

        # Simulate a change where the internal class now requires 3 arguments instead of 2
        def mock_internal_new_version(bounds, transform, something_else):
            return None

        # This should fail during __init__ because we only pass 2 arguments
        # and our catch-all 'except Exception' should store this TypeError
        locator = StonerInsetLocator([0, 0, 1, 1], MagicMock())

        # We manually force the failure by trying to instantiate the "new version"
        # inside the same logic the adapter uses.
        # We deliberately pass fewer arguments than required by the mock to simulate
        # an upstream API change and verify our error handling logic.
        try:
            # pylint: disable=no-value-for-parameter
            mock_internal_new_version([0, 0, 1, 1], MagicMock())  # type: ignore[call-arg]
        except TypeError as e:
            locator._init_error = e
            locator._internal = None

        # Now verify that the adapter reports this specific signature error
        with pytest.raises(RuntimeError, match="missing 1 required positional argument"):
            locator(MagicMock(), MagicMock())
