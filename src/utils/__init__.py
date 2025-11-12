"""Utility functions for path handling, file operations, ID generation, and logging."""

from .path_utils import (
    sanitize_path,
    normalize_path,
    is_valid_path,
    get_absolute_path,
)

from .file_utils import (
    calculate_file_size,
    calculate_directory_size,
    bytes_to_mb,
    generate_codebase_id,
    generate_feature_id,
    is_file_too_large,
    get_file_extension,
    is_text_file,
)

from .logger import (
    MCPLogger,
    initialize_logging,
    get_logger,
)

__all__ = [
    # Path utilities
    "sanitize_path",
    "normalize_path",
    "is_valid_path",
    "get_absolute_path",
    # File utilities
    "calculate_file_size",
    "calculate_directory_size",
    "bytes_to_mb",
    "generate_codebase_id",
    "generate_feature_id",
    "is_file_too_large",
    "get_file_extension",
    "is_text_file",
    # Logging utilities
    "MCPLogger",
    "initialize_logging",
    "get_logger",
]
