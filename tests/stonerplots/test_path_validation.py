# -*- coding: utf-8 -*-
"""Test file path validation in save_figure.py.

This test module verifies that the file path validation properly prevents
directory traversal attacks while allowing legitimate path usage across
different platforms (Windows, MacOS, Linux).
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest
from matplotlib import pyplot as plt

from stonerplots.context.save_figure import SavedFigure
from stonerplots.path_security import (
    get_sensitive_directories,
    is_high_risk_path,
    validate_path_security,
)


class TestPathSecurityModule:
    """Test the path_security module functions."""

    def test_get_sensitive_directories_returns_list(self):
        """Test that get_sensitive_directories returns a non-empty list."""
        dirs = get_sensitive_directories()
        assert isinstance(dirs, list)
        assert len(dirs) > 0
        assert all(isinstance(d, str) for d in dirs)

    def test_get_sensitive_directories_platform_specific(self):
        """Test that sensitive directories are platform-appropriate."""
        dirs = get_sensitive_directories()
        if sys.platform == "win32":
            # Windows should have Windows-specific paths
            assert any("Windows" in d or "Program" in d for d in dirs), \
                "Windows platform should have Windows or Program Files in sensitive dirs"
        elif sys.platform == "darwin":
            # MacOS should have both /System and /Library
            assert "/System" in dirs, "macOS platform should have /System in sensitive dirs"
            assert "/Library" in dirs, "macOS platform should have /Library in sensitive dirs"
        else:
            # Linux should have /etc
            assert "/etc" in dirs, "Linux platform should have /etc in sensitive dirs"

    def test_is_high_risk_path_safe_paths(self):
        """Test that normal paths are not flagged as high-risk."""
        assert not is_high_risk_path("normal/path.txt")
        assert not is_high_risk_path("relative/safe/path.png")
        assert not is_high_risk_path("/tmp/test.txt")  # nosec

    def test_is_high_risk_path_no_traversal(self):
        """Test that paths without .. are not high-risk."""
        assert not is_high_risk_path("some/long/path/to/file.txt")
        assert not is_high_risk_path("/absolute/path/file.txt")

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX-specific test")
    def test_is_high_risk_path_etc_traversal(self):
        """Test that traversal to /etc is detected as high-risk."""
        # This should be high-risk on POSIX systems
        assert is_high_risk_path("../" * 20 + "etc/passwd")


class TestPathValidation:
    """Test path validation in save_figure.py."""

    def test_validate_path_security_normal_relative(self):
        """Test that normal relative paths pass validation."""
        # Should not raise
        validate_path_security("examples/figures/test.png")
        validate_path_security("test/output.pdf")

    def test_validate_path_security_absolute_safe(self):
        """Test that absolute paths to safe directories pass validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "test.png"
            # Should not raise
            validate_path_security(test_path)
            validate_path_security(str(Path(tmpdir) / "subfolder" / "test.png"))

    def test_validate_path_security_local_relative_with_dotdot(self):
        """Test that local relative paths with .. that stay in safe areas pass validation."""
        # Should not raise - these stay in user space
        validate_path_security("test/../valid.png")
        validate_path_security("../test.png")

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX-specific test")
    def test_validate_path_security_traversal_to_etc(self):
        """Test that directory traversal to /etc is blocked on POSIX systems."""
        # Create a deep path to ensure traversal reaches /etc
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            validate_path_security("../../../../../../../../../etc/passwd")

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX-specific test")
    def test_validate_path_security_traversal_to_sys(self):
        """Test that directory traversal to /sys is blocked on POSIX systems."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            validate_path_security("../../../../../../../../../sys/kernel/config")

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX-specific test")
    def test_validate_path_security_traversal_to_proc(self):
        """Test that directory traversal to /proc is blocked on POSIX systems."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            validate_path_security("../../../../../../../../../proc/sys/kernel/hostname")

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_validate_path_security_traversal_to_windows(self):
        """Test that directory traversal to Windows system directories is blocked."""
        import os
        # Use the actual Windows directory from environment
        windows_dir = os.environ.get("SystemRoot", "C:\\Windows")
        # Try to write to a path inside the Windows directory using .. traversal
        # Path like "C:\Windows\Temp\..\System32\config" should be blocked
        test_path = os.path.join(windows_dir, "Temp", "..", "System32", "test.txt")
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            validate_path_security(test_path)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_validate_path_security_traversal_to_program_files(self):
        """Test that directory traversal to Program Files is blocked on Windows."""
        # Use the actual Program Files directory from environment
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        # Try to write to a path inside Program Files using .. traversal
        # Path like "C:\Program Files\Common Files\..\test.png" should be blocked
        test_path = os.path.join(program_files, "Common Files", "..", "test.png")
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            validate_path_security(test_path)

    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS-specific test")
    def test_validate_path_security_traversal_to_system_macos(self):
        """Test that directory traversal to /System is blocked on MacOS."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            validate_path_security("../../../../../../../../../System/Library/test")

    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS-specific test")
    def test_validate_path_security_traversal_to_library_macos(self):
        """Test that directory traversal to /Library is blocked on MacOS."""
        with pytest.raises(ValueError, match="attempted write to sensitive system directory"):
            validate_path_security("../../../../../../../../../Library/test")


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
                    fig, ax = plt.subplots()
                    ax.plot([1, 2, 3], [4, 5, 6])

                # File should be created in parent directory (tmpdir)
                expected_path = Path(tmpdir) / "test_output.png"
                assert expected_path.exists()
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
