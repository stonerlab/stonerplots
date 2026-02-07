# -*- coding: utf-8 -*-
"""Test file path validation in save_figure.py.

This test module verifies that the file path validation properly prevents
directory traversal attacks while allowing legitimate path usage.
"""
import os
import tempfile
from pathlib import Path

import pytest
from matplotlib import pyplot as plt

from stonerplots.context.save_figure import SavedFigure, _validate_path


class TestPathValidation:
    """Test path validation in save_figure.py."""

    def test_validate_path_normal_relative(self):
        """Test that normal relative paths pass validation."""
        # Should not raise
        _validate_path("examples/figures/test.png")
        _validate_path("test/output.pdf")

    def test_validate_path_absolute_safe(self):
        """Test that absolute paths to safe directories pass validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "test.png"
            # Should not raise
            _validate_path(test_path)
            _validate_path("/tmp/test.png")

    def test_validate_path_local_relative_with_dotdot(self):
        """Test that local relative paths with .. that stay in safe areas pass validation."""
        # Should not raise - these stay in user space
        _validate_path("test/../valid.png")
        _validate_path("../test.png")

    def test_validate_path_traversal_to_etc(self):
        """Test that directory traversal to /etc is blocked."""
        # Create a deep path to ensure traversal reaches /etc
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            _validate_path("../../../../../../../../../etc/passwd")

    def test_validate_path_traversal_to_sys(self):
        """Test that directory traversal to /sys is blocked."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            _validate_path("../../../../../../../../../sys/kernel/config")

    def test_validate_path_traversal_to_proc(self):
        """Test that directory traversal to /proc is blocked."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            _validate_path("../../../../../../../../../proc/sys/kernel/hostname")

    def test_validate_path_traversal_to_boot(self):
        """Test that directory traversal to /boot is blocked."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            _validate_path("../../../../../../../../../boot/grub/grub.cfg")

    def test_validate_path_traversal_to_dev(self):
        """Test that directory traversal to /dev is blocked."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            _validate_path("../../../../../../../../../dev/null")


class TestSavedFigureWithValidation:
    """Test SavedFigure with path validation integrated."""

    def test_saved_figure_with_safe_path(self):
        """Test that SavedFigure works with safe paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output.png"
            
            with SavedFigure(filename=str(output_path), style="default", autoclose=True):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3], [4, 5, 6])
                plt.show()
            
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
                plt.show()
            
            # File should be created with label substituted
            expected_path = Path(tmpdir) / "figure_test_label.png"
            assert expected_path.exists()

    def test_saved_figure_blocks_malicious_label(self):
        """Test that SavedFigure blocks malicious labels in template substitution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "figure_{label}.png"
            
            # Use a malicious label that tries to escape to /etc
            malicious_label = "../" * 20 + "etc/passwd"
            
            with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
                with SavedFigure(filename=str(template_path), style="default", autoclose=True):
                    fig = plt.figure(malicious_label)
                    ax = fig.add_subplot(111)
                    ax.plot([1, 2, 3], [4, 5, 6])
                    plt.show()

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
                    fig, ax = plt.subplots()
                    ax.plot([1, 2, 3], [4, 5, 6])
                    plt.show()
                
                # File should be created in parent directory (tmpdir)
                expected_path = Path(tmpdir) / "test_output.png"
                assert expected_path.exists()
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
