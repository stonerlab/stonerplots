# -*- coding: utf-8 -*-
"""Test file path validation in save_figure.py.

This test module verifies that SavedFigure correctly integrates with the bad_path
package to prevent directory traversal attacks while allowing legitimate path usage
across different platforms (Windows, MacOS, Linux).
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest
from matplotlib import pyplot as plt

from stonerplots.context.save_figure import SavedFigure


class TestSavedFigureWithValidation:
    """Test SavedFigure with path validation integrated."""

    def setup_method(self):
        """Close all figures before each test."""
        plt.close('all')

    def teardown_method(self):
        """Close all figures after each test."""
        plt.close('all')

    def test_saved_figure_with_safe_path(self):
        """Test that SavedFigure works with safe paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output.png"

            with SavedFigure(filename=str(output_path), style="default", autoclose=True):
                _, ax = plt.subplots()
                ax.plot([1, 2, 3], [4, 5, 6])

            # File should be created
            assert output_path.exists()

    def test_saved_figure_with_template_and_safe_label(self):
        """Test that SavedFigure works with template substitution and safe labels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "figure_{label}.png"

            with SavedFigure(filename=str(template_path), style="default", autoclose=True):
                fig = plt.figure("test_label")
                ax = fig.add_subplot(111)
                ax.plot([1, 2, 3], [4, 5, 6])

            # File should be created with label substituted
            expected_path = Path(tmpdir) / "figure_test_label.png"
            assert expected_path.exists()

    def test_saved_figure_blocks_malicious_label(self):
        """Test that SavedFigure blocks malicious labels in template substitution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "figure_{label}.png"

            # Use a platform-appropriate malicious label that tries to escape to system directories
            if sys.platform == "win32":
                malicious_label = "../" * 20 + "Windows/System32/config"
            elif sys.platform == "darwin":
                malicious_label = "../" * 20 + "System/Library/test"
            else:
                malicious_label = "../" * 20 + "etc/passwd"

            with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
                with SavedFigure(filename=str(template_path), style="default", autoclose=True):
                    fig = plt.figure(malicious_label)
                    ax = fig.add_subplot(111)
                    ax.plot([1, 2, 3], [4, 5, 6])

    def test_saved_figure_allows_parent_directory_in_safe_area(self):
        """Test that SavedFigure allows using parent directory if it's in a safe area."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a subdirectory and try to save to parent (tmpdir)
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir(parents=True, exist_ok=True)

            # Change to subdir to test relative parent path
            original_cwd = os.getcwd()
            try:
                os.chdir(subdir)
                output_path = "../test_output.png"

                with SavedFigure(filename=output_path, style="default", autoclose=True):
                    _, ax = plt.subplots()
                    ax.plot([1, 2, 3], [4, 5, 6])

                # File should be created in parent directory (tmpdir)
                expected_path = Path(tmpdir) / "test_output.png"
                assert expected_path.exists()
            finally:
                os.chdir(original_cwd)

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX-specific test")
    def test_saved_figure_blocks_dangerous_path_etc(self):
        """Test that SavedFigure blocks direct dangerous paths to /etc on POSIX systems."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            with SavedFigure(filename="../" * 20 + "etc/test_output.png", autoclose=True):
                _, ax = plt.subplots()
                ax.plot([1, 2, 3], [4, 5, 6])

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX-specific test")
    def test_saved_figure_blocks_dangerous_path_sys(self):
        """Test that SavedFigure blocks direct dangerous paths to /sys on POSIX systems."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            with SavedFigure(filename="../" * 20 + "sys/test.png", autoclose=True):
                _, ax = plt.subplots()
                ax.plot([1, 2, 3], [4, 5, 6])

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_saved_figure_blocks_dangerous_path_windows(self):
        """Test that SavedFigure blocks direct dangerous paths to Windows system directories."""
        windows_dir = os.environ.get("SystemRoot", "C:\\Windows")
        test_path = os.path.join(windows_dir, "System32", "test.png")
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            with SavedFigure(filename=test_path, autoclose=True):
                _, ax = plt.subplots()
                ax.plot([1, 2, 3], [4, 5, 6])

    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS-specific test")
    def test_saved_figure_blocks_dangerous_path_macos(self):
        """Test that SavedFigure blocks direct dangerous paths to /System on MacOS."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            with SavedFigure(filename="../" * 20 + "System/test.png", autoclose=True):
                _, ax = plt.subplots()
                ax.plot([1, 2, 3], [4, 5, 6])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
