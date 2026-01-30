# -*- coding: utf-8 -*-
"""Test fixes for issues 17-20 in BUGS.md."""

import numpy as np
import pytest

from stonerplots.format import TexEngFormatter, TexFormatter


class TestIssue17UnsafeDivision:
    """Test that division operations in formatters handle extreme values safely.

    Issue 17: Unsafe Division in format.py
    """

    def test_tex_formatter_extreme_values(self):
        """Test TexFormatter handles extreme values without errors."""
        formatter = TexFormatter()

        # Test very large values
        result = formatter(1e308)
        assert isinstance(result, str)
        assert "$" in result

        # Test very small values
        result = formatter(1e-308)
        assert isinstance(result, str)
        assert "$" in result

        # Test normal values still work
        result = formatter(1000)
        assert isinstance(result, str)
        assert "$" in result

    def test_tex_formatter_zero(self):
        """Test TexFormatter handles zero correctly."""
        formatter = TexFormatter()
        result = formatter(0.0)
        assert result == "$0.0$"

    def test_tex_formatter_none_and_nan(self):
        """Test TexFormatter handles None and NaN correctly."""
        formatter = TexFormatter()

        result = formatter(None)
        assert result == ""

        result = formatter(np.nan)
        assert result == ""

    def test_tex_eng_formatter_extreme_values(self):
        """Test TexEngFormatter handles extreme values without errors."""
        formatter = TexEngFormatter(unit="V")

        # Test very large values
        result = formatter(1e308)
        assert isinstance(result, str)
        assert "$" in result
        assert "V" in result

        # Test very small values
        result = formatter(1e-308)
        assert isinstance(result, str)
        assert "$" in result

        # Test normal values still work
        result = formatter(1000)
        assert isinstance(result, str)
        assert "$" in result
        assert "V" in result

    def test_tex_eng_formatter_zero(self):
        """Test TexEngFormatter handles zero correctly."""
        formatter = TexEngFormatter(unit="A")
        result = formatter(0.0)
        assert result == "$0.0$"

    def test_tex_eng_formatter_none_and_nan(self):
        """Test TexEngFormatter handles None and NaN correctly."""
        formatter = TexEngFormatter(unit="W")

        result = formatter(None)
        assert result == ""

        result = formatter(np.nan)
        assert result == ""

    def test_tex_eng_formatter_prefix_ranges(self):
        """Test TexEngFormatter handles values across different SI prefix ranges."""
        formatter = TexEngFormatter(unit="Hz")

        # Test values that would use different SI prefixes
        test_values = [
            1e-24,  # yocto (y)
            1e-21,  # zepto (z)
            1e-18,  # atto (a)
            1e-15,  # femto (f)
            1e-12,  # pico (p)
            1e-9,  # nano (n)
            1e-6,  # micro (μ)
            1e-3,  # milli (m)
            1,  # base unit
            1e3,  # kilo (k)
            1e6,  # mega (M)
            1e9,  # giga (G)
            1e12,  # tera (T)
            1e15,  # peta (P)
            1e18,  # exa (E)
            1e21,  # zetta (Z)
            1e24,  # yotta (Y)
        ]

        for value in test_values:
            result = formatter(value)
            assert isinstance(result, str)
            assert "$" in result
            assert "Hz" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
