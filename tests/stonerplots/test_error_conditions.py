# -*- coding: utf-8 -*-
"""Test error conditions in stonerplots modules.

This test module verifies that error conditions are properly caught and handled with appropriate
exceptions. It addresses the code coverage gaps identified in COVERAGE_REPORT.md.
"""
from tempfile import NamedTemporaryFile

import pytest
from matplotlib import pyplot as plt

from stonerplots.context.double_y import DoubleYAxis
from stonerplots.context.multiple_plot import MultiPanel
from stonerplots.context.save_figure import SavedFigure, _make_path
from stonerplots.counter import roman
from stonerplots.format import PlotLabeller, TexEngFormatter
from stonerplots.util import _default


class TestCounterErrors:
    """Test error conditions in counter.py."""

    def test_roman_negative_number(self):
        """Test that roman() raises ValueError for negative numbers."""
        with pytest.raises(ValueError, match="Only positive integers can be represented as Roman numerals"):
            roman(-5)

    def test_roman_zero(self):
        """Test that roman() raises ValueError for zero."""
        with pytest.raises(ValueError, match="Only positive integers can be represented as Roman numerals"):
            roman(0)

    def test_roman_non_integer(self):
        """Test that roman() raises ValueError for non-integer inputs."""
        with pytest.raises(ValueError, match="Only positive integers can be represented as Roman numerals"):
            roman(3.14)

    def test_roman_string(self):
        """Test that roman() raises ValueError for string inputs."""
        with pytest.raises(ValueError, match="Only positive integers can be represented as Roman numerals"):
            roman("five")


class TestFormatErrors:
    """Test error conditions in format.py."""

    def test_plot_labeller_invalid_x_type(self):
        """Test that PlotLabeller raises TypeError for invalid x parameter type."""
        with pytest.raises(TypeError, match="x should only contain matplotlib.ticker.Formatter subclasses"):
            PlotLabeller(x="invalid")

    def test_plot_labeller_invalid_y_type(self):
        """Test that PlotLabeller raises TypeError for invalid y parameter type."""
        with pytest.raises(TypeError, match="y should only contain matplotlib.ticker.Formatter subclasses"):
            PlotLabeller(y=123)

    def test_plot_labeller_invalid_z_type(self):
        """Test that PlotLabeller raises TypeError for invalid z parameter type."""
        with pytest.raises(TypeError, match="z should only contain matplotlib.ticker.Formatter subclasses"):
            PlotLabeller(z={"not": "valid"})

    def test_plot_labeller_invalid_list_element(self):
        """Test that PlotLabeller raises TypeError for invalid element in list."""
        with pytest.raises(TypeError, match="x should only contain matplotlib.ticker.Formatter subclasses"):
            PlotLabeller(x=[TexEngFormatter, "invalid"])


class TestUtilErrors:
    """Test error conditions in util.py."""

    def test_default_style_invalid_type(self):
        """Test that _default.style raises TypeError for invalid type."""
        default = _default()
        with pytest.raises(TypeError, match="Invalid type for default style"):
            default.style = 123

    def test_default_style_invalid_float(self):
        """Test that _default.style raises TypeError for float type."""
        default = _default()
        with pytest.raises(TypeError, match="Invalid type for default style"):
            default.style = 3.14

    def test_default_formats_invalid_type(self):
        """Test that _default.formats raises TypeError for invalid type."""
        default = _default()
        with pytest.raises(TypeError, match="Invalid type for formats"):
            default.formats = 456

    def test_default_formats_invalid_float(self):
        """Test that _default.formats raises TypeError for float type."""
        default = _default()
        with pytest.raises(TypeError, match="Invalid type for formats"):
            default.formats = 3.14


class TestSaveFigureErrors:
    """Test error conditions in save_figure.py."""

    def test_make_path_invalid_type(self):
        """Test that _make_path raises TypeError for invalid type."""
        with pytest.raises(TypeError, match="output filename should be a string or pathlib.Path"):
            _make_path(123)

    def test_make_path_invalid_list(self):
        """Test that _make_path raises TypeError for list type."""
        with pytest.raises(TypeError, match="output filename should be a string or pathlib.Path"):
            _make_path(["not", "valid"])

    def test_saved_figure_invalid_filename_in_call(self):
        """Test that SavedFigure raises ValueError for invalid filename in __call__."""
        with NamedTemporaryFile(suffix=".png") as tmp:
            cm = SavedFigure(filename=tmp.name)
            with pytest.raises(ValueError, match="Only a single positional argument"):
                cm(123)

    def test_saved_figure_invalid_formats_type(self):
        """Test that SavedFigure.formats setter raises TypeError for invalid type."""
        with NamedTemporaryFile(suffix=".png") as tmp:
            cm = SavedFigure(filename=tmp.name)
            with pytest.raises(TypeError, match="Invalid formats specified"):
                cm.formats = 789

    def test_saved_figure_invalid_style_type(self):
        """Test that SavedFigure.style setter raises TypeError for invalid type."""
        with NamedTemporaryFile(suffix=".png") as tmp:
            cm = SavedFigure(filename=tmp.name)
            with pytest.raises(TypeError, match="Invalid style"):
                cm.style = 456

    def test_saved_figure_invalid_extra_type(self):
        """Test that SavedFigure.extra setter raises KeyError for invalid rcParams."""
        with NamedTemporaryFile(suffix=".png") as tmp:
            cm = SavedFigure(filename=tmp.name)
            with pytest.raises(KeyError, match="are not valid Matplotlib rcParameters"):
                cm.extra = {"invalid_param_name": "value"}

    def test_saved_figure_multiple_positional_args(self):
        """Test that SavedFigure raises ValueError for multiple positional arguments."""
        with NamedTemporaryFile(suffix=".png") as tmp:
            cm = SavedFigure(filename=tmp.name)
            with pytest.raises(ValueError, match="Only a single positional argument"):
                cm("file1", "file2")


class TestDoubleYAxisErrors:
    """Test error conditions in double_y.py."""

    def test_double_y_invalid_location_string(self):
        """Test that DoubleYAxis raises ValueError for invalid location string."""
        with pytest.raises(ValueError, match="Location .* not recognised"):
            DoubleYAxis(loc="invalid_location")

    def test_double_y_invalid_location_type(self):
        """Test that DoubleYAxis raises TypeError for invalid location type."""
        with pytest.raises(TypeError, match="Legend location must be of type str or int"):
            DoubleYAxis(loc=[1, 2])

    def test_double_y_invalid_colours_type(self):
        """Test that DoubleYAxis raises TypeError for invalid colours type."""
        with pytest.raises(TypeError, match="Colours must be a list, tuple, or string"):
            DoubleYAxis(colours=123)

    def test_double_y_invalid_colours_dict(self):
        """Test that DoubleYAxis raises TypeError for dict colours."""
        with pytest.raises(TypeError, match="Colours must be a list, tuple, or string"):
            DoubleYAxis(colours={"red": "#FF0000"})


class TestMultiPanelErrors:
    """Test error conditions in multiple_plot.py."""

    def test_multipanel_invalid_figure_type(self):
        """Test that MultiPanel raises TypeError for invalid figure type in context."""
        with pytest.raises(TypeError, match="Unable to interpret .* as a figure"):
            with MultiPanel(2, figure=[1, 2, 3]):
                pass

    def test_multipanel_invalid_panels_type(self):
        """Test that MultiPanel raises TypeError for invalid panels type in context."""
        with pytest.raises(TypeError, match="Unable to interpret the number of panels to create"):
            with MultiPanel({"not": "valid"}):
                pass


class TestErrorConditionIntegration:
    """Integration tests to ensure error handling doesn't break normal functionality."""

    def test_plot_labeller_valid_usage_after_error(self):
        """Test that PlotLabeller still works correctly after an error."""
        # First trigger an error
        with pytest.raises(TypeError):
            PlotLabeller(x="invalid")

        # Then verify normal usage still works
        with PlotLabeller(x=TexEngFormatter):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            plt.close(fig)

    def test_double_y_valid_usage_after_error(self):
        """Test that DoubleYAxis still works correctly after an error."""
        # First trigger an error
        with pytest.raises(ValueError):
            DoubleYAxis(loc="nowhere")

        # Then verify normal usage still works
        fig, ax = plt.subplots()
        with DoubleYAxis(ax=ax, loc="upper right"):
            pass
        plt.close(fig)

    def test_saved_figure_valid_usage_after_error(self):
        """Test that SavedFigure still works correctly after an error."""
        # First trigger an error in __call__
        with NamedTemporaryFile(suffix=".png") as tmp:
            cm = SavedFigure(filename=tmp.name)
            with pytest.raises(ValueError):
                cm(123)

        # Then verify normal usage still works (without actually saving)
        with NamedTemporaryFile(suffix=".png") as tmp:
            cm2 = SavedFigure(filename=tmp.name, style="default", autoclose=True)
            with cm2:
                fig = plt.figure()
                plt.plot([1, 2], [3, 4])
                plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "--pdb"])
