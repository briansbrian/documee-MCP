"""Path utility functions for secure path handling and validation."""

import os
from pathlib import Path


def sanitize_path(path: str) -> str:
    """
    Sanitize a path by blocking directory traversal attempts and normalizing it.
    
    This function detects ".." in relative paths to prevent directory traversal attacks,
    converts the path to an absolute path, and validates it exists.
    
    Args:
        path: The path string to sanitize
        
    Returns:
        Sanitized absolute path string
        
    Raises:
        ValueError: If the path contains directory traversal attempts or is invalid
        
    Examples:
        >>> sanitize_path("./src")
        "C:\\Users\\project\\src"  # On Windows
        
        >>> sanitize_path("../../../etc/passwd")
        ValueError: Directory traversal detected in path
        
        >>> sanitize_path("C:\\Users\\project")
        "C:\\Users\\project"  # Absolute paths are allowed
    """
    if not path:
        raise ValueError("Path cannot be empty")
    
    # Check for directory traversal attempts in relative paths
    # Only block ".." if it's in a relative path (not an absolute path)
    if not os.path.isabs(path):
        if ".." in path:
            raise ValueError(f"Directory traversal detected in path: {path}")
    
    # Block tilde expansion for security
    if "~" in path:
        raise ValueError(f"Tilde expansion not allowed in path: {path}")
    
    # Handle both Windows backslashes and forward slashes
    # Normalize path separators for current OS
    path = path.replace("\\", os.sep).replace("/", os.sep)
    
    # Convert to absolute path
    try:
        abs_path = os.path.abspath(path)
    except Exception as e:
        raise ValueError(f"Invalid path: {path}") from e
    
    return abs_path


def normalize_path(path: str) -> str:
    """
    Normalize a path to use the current OS path separator.
    
    Converts both forward slashes and backslashes to the appropriate
    separator for the current operating system.
    
    Args:
        path: The path string to normalize
        
    Returns:
        Normalized path string with OS-appropriate separators
        
    Examples:
        >>> normalize_path("src/utils/file.py")
        "src\\utils\\file.py"  # On Windows
    """
    # Replace both types of separators with OS-specific separator
    normalized = path.replace("\\", os.sep).replace("/", os.sep)
    return normalized


def is_valid_path(path: str) -> bool:
    """
    Check if a path exists and is accessible.
    
    Args:
        path: The path to validate
        
    Returns:
        True if the path exists and is accessible, False otherwise
    """
    try:
        return os.path.exists(path)
    except (OSError, ValueError):
        return False


def get_absolute_path(path: str) -> str:
    """
    Get the absolute path for a given path, handling Windows-specific cases.
    
    Args:
        path: The path to convert to absolute
        
    Returns:
        Absolute path string
        
    Raises:
        ValueError: If the path cannot be converted to absolute
    """
    try:
        # Use pathlib for cross-platform compatibility
        abs_path = Path(path).resolve()
        return str(abs_path)
    except Exception as e:
        raise ValueError(f"Cannot resolve absolute path for: {path}") from e
