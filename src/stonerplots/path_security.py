# -*- coding: utf-8 -*-
"""Path security validation for detecting high-risk file locations.

This module provides functionality to validate file paths and detect potential
directory traversal attacks that could write to sensitive system directories.

The validation is platform-aware, checking against different sets of sensitive
directories on Windows, MacOS, and Linux/POSIX systems.

This module is designed to be easily replaceable with a more comprehensive
security package in the future.
"""
import os
import sys
from pathlib import Path
from typing import List, Union

# Platform-specific sensitive directory lists
# These directories should not be written to via directory traversal

# Linux and other POSIX systems
POSIX_SENSITIVE_DIRS = [
    "/etc",   # System configuration files
    "/sys",   # Kernel and system information
    "/proc",  # Process and kernel information
    "/boot",  # Boot loader files
    "/dev",   # Device files
]

# MacOS-specific additions (extends POSIX list)
MACOS_SENSITIVE_DIRS = [
    "/etc",
    "/sys",
    "/proc",
    "/dev",
    "/System",            # MacOS system files
    "/Library",           # System-level library (user ~/Library is OK)
    "/private/etc",       # MacOS private system configs
    "/private/var/root",  # Root user private files
]

# Windows-specific sensitive directories
# Note: These are determined at runtime based on environment variables
def _get_windows_sensitive_dirs() -> List[str]:
    """Get Windows sensitive directories based on environment variables.
    
    Returns:
        (List[str]): List of sensitive directory paths with normalized separators.
    """
    windows_dir = os.environ.get("SystemRoot", "C:\\Windows")
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    
    # Normalize to use forward slashes for consistent comparison
    return [
        windows_dir.replace("\\", "/"),
        program_files.replace("\\", "/"),
        program_files_x86.replace("\\", "/"),
    ]


def get_sensitive_directories() -> List[str]:
    """Get the list of sensitive directories for the current platform.
    
    Returns:
        (List[str]): Platform-specific list of sensitive directory paths.
        
    Examples:
        >>> dirs = get_sensitive_directories()
        >>> '/etc' in dirs or 'Windows' in str(dirs)  # Platform dependent
        True
    """
    if sys.platform == "win32":
        return _get_windows_sensitive_dirs()
    elif sys.platform == "darwin":
        return MACOS_SENSITIVE_DIRS
    else:
        return POSIX_SENSITIVE_DIRS


def is_high_risk_path(path: Union[str, Path]) -> bool:
    """Check if a path represents a high-risk location for file writes.
    
    A path is considered high-risk if it contains directory traversal patterns (..)
    and resolves to a sensitive system directory.
    
    Args:
        path (Union[str, Path]): The path to check.
        
    Returns:
        (bool): True if the path is high-risk, False otherwise.
        
    Examples:
        >>> is_high_risk_path("normal/path.txt")
        False
        >>> is_high_risk_path("../safe/path.txt")  # Depends on where it resolves
        False
    """
    path_obj = Path(path)
    
    # Only check paths with directory traversal
    if ".." not in path_obj.parts:
        return False
    
    # Try to resolve the path
    try:
        resolved = path_obj.resolve()
    except (OSError, RuntimeError):
        # If we can't resolve it, consider it high-risk to be safe
        return True
    
    # Get platform-specific sensitive directories
    sensitive_dirs = get_sensitive_directories()
    resolved_str = str(resolved)
    
    # Windows-specific: Check for system drive root
    if sys.platform == "win32":
        resolved_str = resolved_str.replace("\\", "/")
        if resolved.drive and resolved.parent == Path(resolved.drive + "/"):
            return True
    
    # Check if resolved path is in a sensitive directory
    for sensitive_dir in sensitive_dirs:
        if resolved_str.startswith(sensitive_dir + "/") or resolved_str == sensitive_dir:
            return True
    
    return False


def validate_path_security(path: Union[str, Path]) -> None:
    """Validate that a path is not attempting to write to sensitive system directories.
    
    This function checks for directory traversal patterns that could lead to writing
    files in sensitive system directories. It allows legitimate relative and absolute
    paths, but blocks paths that would escape to system directories on any platform.
    
    Platform-specific checks:
    - **POSIX/Linux**: /etc, /sys, /proc, /boot, /dev
    - **MacOS**: Above plus /System, /Library, /private/etc
    - **Windows**: %SystemRoot%, %ProgramFiles%, system drive root
    
    Args:
        path (Union[str, Path]): The path to validate.
        
    Raises:
        ValueError: If the path is high-risk (attempts to write to sensitive directories).
        
    Examples:
        >>> validate_path_security("output/figures/plot.png")  # OK
        >>> validate_path_security("../../../etc/passwd")  # Raises ValueError
        Traceback (most recent call last):
            ...
        ValueError: Invalid path: ../../../etc/passwd (attempted write to sensitive system directory: /etc/passwd)
    """
    path_obj = Path(path)
    
    # Check for directory traversal components
    if ".." not in path_obj.parts:
        return  # No traversal, safe
    
    # Resolve the path to see where it actually points
    try:
        resolved = path_obj.resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {path} (could not resolve path: {e})")
    
    # Check if it's a high-risk location
    if is_high_risk_path(path):
        raise ValueError(
            f"Invalid path: {path} (attempted write to sensitive system directory: {resolved})"
        )
