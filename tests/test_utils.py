"""
Unit tests for utility functions.

Tests path sanitization, codebase ID generation, and feature ID generation.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path

from src.utils.path_utils import (
    sanitize_path,
    normalize_path,
    is_valid_path,
    get_absolute_path
)
from src.utils.file_utils import (
    calculate_file_size,
    calculate_directory_size,
    bytes_to_mb,
    generate_codebase_id,
    generate_feature_id,
    is_file_too_large,
    get_file_extension,
    is_text_file
)


# Path Utils Tests

def test_sanitize_path_valid():
    """Test sanitizing a valid path."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        result = sanitize_path(tmpdir)
        assert os.path.isabs(result)
        assert os.path.exists(result)


def test_sanitize_path_directory_traversal():
    """Test that directory traversal attempts are blocked."""
    with pytest.raises(ValueError, match="Directory traversal detected"):
        sanitize_path("../../../etc/passwd")
    
    with pytest.raises(ValueError, match="Directory traversal detected"):
        sanitize_path("./src/../../etc/passwd")


def test_sanitize_path_tilde_expansion():
    """Test that tilde expansion is blocked."""
    with pytest.raises(ValueError, match="Tilde expansion not allowed"):
        sanitize_path("~/documents")


def test_sanitize_path_empty():
    """Test that empty path raises error."""
    with pytest.raises(ValueError, match="Path cannot be empty"):
        sanitize_path("")


def test_sanitize_path_absolute():
    """Test that absolute paths are allowed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        abs_path = os.path.abspath(tmpdir)
        result = sanitize_path(abs_path)
        assert result == abs_path


def test_normalize_path():
    """Test path normalization."""
    # Test forward slashes
    result = normalize_path("src/utils/file.py")
    assert os.sep in result
    
    # Test backslashes
    result = normalize_path("src\\utils\\file.py")
    assert os.sep in result
    
    # Test mixed
    result = normalize_path("src/utils\\file.py")
    assert os.sep in result


def test_is_valid_path():
    """Test path validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Valid path
        assert is_valid_path(tmpdir) is True
        
        # Invalid path
        assert is_valid_path("/nonexistent/path/12345") is False


def test_get_absolute_path():
    """Test getting absolute path."""
    tmpdir = tempfile.mkdtemp()
    
    try:
        # Relative path
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = get_absolute_path(".")
            assert os.path.isabs(result)
        finally:
            os.chdir(original_dir)
        
        # Absolute path
        abs_path = os.path.abspath(tmpdir)
        result = get_absolute_path(abs_path)
        assert result == abs_path
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# File Utils Tests

def test_calculate_file_size():
    """Test file size calculation."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Hello, World!")
        temp_path = f.name
    
    try:
        size = calculate_file_size(temp_path)
        assert size > 0
        assert isinstance(size, int)
    finally:
        os.unlink(temp_path)


def test_calculate_file_size_nonexistent():
    """Test file size calculation for nonexistent file."""
    with pytest.raises(FileNotFoundError):
        calculate_file_size("/nonexistent/file.txt")


def test_calculate_directory_size():
    """Test directory size calculation."""
    tmpdir = tempfile.mkdtemp()
    
    try:
        # Create some files
        Path(os.path.join(tmpdir, "file1.txt")).write_text("Hello")
        Path(os.path.join(tmpdir, "file2.txt")).write_text("World")
        
        size = calculate_directory_size(tmpdir)
        assert size > 0
        assert isinstance(size, int)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_calculate_directory_size_not_directory():
    """Test directory size calculation for non-directory."""
    with tempfile.NamedTemporaryFile() as f:
        with pytest.raises(NotADirectoryError):
            calculate_directory_size(f.name)


def test_bytes_to_mb():
    """Test bytes to megabytes conversion."""
    # 1 MB
    assert bytes_to_mb(1024 * 1024) == 1.0
    
    # 2.5 MB
    assert bytes_to_mb(2.5 * 1024 * 1024) == 2.5
    
    # 0 bytes
    assert bytes_to_mb(0) == 0.0
    
    # Small value (1024 bytes = 0.001 MB rounded to 2 decimals = 0.0)
    result = bytes_to_mb(1024)
    assert result == 0.0  # Rounded to 2 decimal places
    
    # Larger small value
    result = bytes_to_mb(100 * 1024)  # 100 KB
    assert 0 < result < 1


def test_generate_codebase_id():
    """Test codebase ID generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate ID
        codebase_id = generate_codebase_id(tmpdir)
        
        # Verify format
        assert isinstance(codebase_id, str)
        assert len(codebase_id) == 16
        assert codebase_id.isalnum()
        
        # Same path should generate same ID
        codebase_id2 = generate_codebase_id(tmpdir)
        assert codebase_id == codebase_id2


def test_generate_codebase_id_consistency():
    """Test that codebase ID is consistent across different path formats."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Get absolute path
        abs_path = os.path.abspath(tmpdir)
        
        # Generate IDs with different path formats
        id1 = generate_codebase_id(tmpdir)
        id2 = generate_codebase_id(abs_path)
        
        # Should be the same
        assert id1 == id2


def test_generate_feature_id():
    """Test feature ID generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        feature_dir = os.path.join(tmpdir, "routes")
        os.makedirs(feature_dir)
        
        # Generate ID
        feature_id = generate_feature_id(feature_dir)
        
        # Verify format
        assert isinstance(feature_id, str)
        assert len(feature_id) == 16
        assert feature_id.isalnum()
        
        # Same path should generate same ID
        feature_id2 = generate_feature_id(feature_dir)
        assert feature_id == feature_id2


def test_generate_feature_id_different_paths():
    """Test that different paths generate different IDs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir1 = os.path.join(tmpdir, "routes")
        dir2 = os.path.join(tmpdir, "components")
        os.makedirs(dir1)
        os.makedirs(dir2)
        
        id1 = generate_feature_id(dir1)
        id2 = generate_feature_id(dir2)
        
        # Should be different
        assert id1 != id2


def test_is_file_too_large():
    """Test file size checking."""
    # Create a small file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Small file")
        temp_path = f.name
    
    try:
        # Should not be too large with default 10MB limit
        assert is_file_too_large(temp_path, max_size_mb=10) is False
        
        # Get actual file size to test properly
        file_size_bytes = calculate_file_size(temp_path)
        file_size_mb = bytes_to_mb(file_size_bytes)
        
        # Should be too large with limit smaller than file size
        assert is_file_too_large(temp_path, max_size_mb=file_size_mb - 0.01) is True
    finally:
        os.unlink(temp_path)


def test_is_file_too_large_nonexistent():
    """Test file size checking for nonexistent file."""
    # Should return True (consider it too large to skip it)
    assert is_file_too_large("/nonexistent/file.txt") is True


def test_get_file_extension():
    """Test file extension extraction."""
    assert get_file_extension("file.py") == ".py"
    assert get_file_extension("file.js") == ".js"
    assert get_file_extension("file.test.ts") == ".ts"
    assert get_file_extension("README.md") == ".md"
    assert get_file_extension("Makefile") == ""
    assert get_file_extension("/path/to/file.txt") == ".txt"


def test_get_file_extension_case_insensitive():
    """Test that file extension is lowercase."""
    assert get_file_extension("FILE.PY") == ".py"
    assert get_file_extension("File.Js") == ".js"


def test_is_text_file():
    """Test text file detection."""
    # Text files
    assert is_text_file("file.py") is True
    assert is_text_file("file.js") is True
    assert is_text_file("file.txt") is True
    assert is_text_file("README.md") is True
    assert is_text_file("config.json") is True
    assert is_text_file("style.css") is True
    
    # Non-text files
    assert is_text_file("image.png") is False
    assert is_text_file("video.mp4") is False
    assert is_text_file("archive.zip") is False
    assert is_text_file("binary.exe") is False


def test_is_text_file_case_insensitive():
    """Test that text file detection is case insensitive."""
    assert is_text_file("FILE.PY") is True
    assert is_text_file("File.Js") is True
    assert is_text_file("IMAGE.PNG") is False


def test_path_sanitization_windows_paths():
    """Test path sanitization with Windows-style paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Windows-style path with backslashes
        windows_path = tmpdir.replace("/", "\\")
        result = sanitize_path(windows_path)
        assert os.path.isabs(result)


def test_codebase_id_cross_platform():
    """Test that codebase ID generation works across platforms."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test with both forward and backslashes
        path_forward = tmpdir.replace("\\", "/")
        path_backward = tmpdir.replace("/", "\\")
        
        id1 = generate_codebase_id(path_forward)
        id2 = generate_codebase_id(path_backward)
        
        # Should generate same ID regardless of separator
        assert id1 == id2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
