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

from stonerplots.context.base import RavelList
from stonerplots.context.noframe import CentredAxes
from stonerplots.format import TexEngFormatter, TexFormatter


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
        ax1 = fig1.add_subplot(111)
        
        # Create another figure
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(111)
        
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
        from stonerplots.context.base import PlotContextSequence
        
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
        from stonerplots.context.base import PlotContextSequence
        
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
        from stonerplots.context.base import PlotContextSequence
        
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
        from stonerplots.context.base import PlotContextSequence
        
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
