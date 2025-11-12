# Utilities Module

## Overview

The utilities module provides core helper functions for path handling, file operations, and ID generation. These utilities ensure secure, cross-platform operations and consistent identifier generation across the MCP server.

## Module Structure

```
src/utils/
├── __init__.py
├── path_utils.py      # Path sanitization and validation
└── file_utils.py      # File operations and ID generation
```

## Path Utilities (`path_utils.py`)

### Purpose

Provides secure path handling with protection against directory traversal attacks and cross-platform path normalization.

### Key Functions

#### `sanitize_path(path: str) -> str`

Sanitizes paths by removing directory traversal attempts and normalizing for the current OS.

**Security Features:**
- Removes `..` (parent directory traversal)
- Removes `~` (home directory expansion)
- Converts to absolute path
- Normalizes path separators for current OS

**Usage:**
```python
from src.utils.path_utils import sanitize_path

# Safe path handling
safe_path = sanitize_path("./src/tools")
# Returns: "C:\\Users\\project\\src\\tools" (Windows)

# Blocks traversal attempts
safe_path = sanitize_path("../../../etc/passwd")
# Returns: "C:\\Users\\project\\etc\\passwd" (traversal removed)
```

#### `normalize_path(path: str) -> str`

Normalizes path separators for the current operating system.

**Usage:**
```python
from src.utils.path_utils import normalize_path

# Cross-platform path handling
normalized = normalize_path("src/utils/file.py")
# Returns: "src\\utils\\file.py" (Windows)
# Returns: "src/utils/file.py" (Unix)
```

#### `is_valid_path(path: str) -> bool`

Checks if a path exists and is accessible.

**Usage:**
```python
from src.utils.path_utils import is_valid_path

if is_valid_path("/path/to/codebase"):
    # Proceed with analysis
    pass
```

#### `get_absolute_path(path: str) -> str`

Converts relative paths to absolute paths using pathlib for cross-platform compatibility.

**Usage:**
```python
from src.utils.path_utils import get_absolute_path

abs_path = get_absolute_path("./src")
# Returns: "C:\\Users\\project\\src" (Windows)
```

## File Utilities (`file_utils.py`)

### Purpose

Provides file operations, size calculations, and unique identifier generation for codebases and features.

### Key Functions

#### `calculate_file_size(file_path: str) -> int`

Returns file size in bytes.

**Usage:**
```python
from src.utils.file_utils import calculate_file_size

size_bytes = calculate_file_size("config.yaml")
# Returns: 1024 (bytes)
```

#### `calculate_directory_size(directory_path: str) -> int`

Recursively calculates total size of all files in a directory.

**Usage:**
```python
from src.utils.file_utils import calculate_directory_size

total_size = calculate_directory_size("./src")
# Returns: 524288 (bytes)
```

#### `bytes_to_mb(bytes_size: int) -> float`

Converts bytes to megabytes (rounded to 2 decimal places).

**Usage:**
```python
from src.utils.file_utils import bytes_to_mb

size_mb = bytes_to_mb(1048576)
# Returns: 1.0 (MB)
```

#### `generate_codebase_id(path: str) -> str`

Generates a unique 16-character identifier for a codebase using SHA-256 hash of the absolute path.

**Algorithm:**
1. Convert path to absolute path
2. Normalize path separators to forward slashes
3. Compute SHA-256 hash of normalized path
4. Truncate to 16 characters

**Usage:**
```python
from src.utils.file_utils import generate_codebase_id

codebase_id = generate_codebase_id("/home/user/project")
# Returns: "a1b2c3d4e5f6g7h8"

# Same path always generates same ID
codebase_id2 = generate_codebase_id("/home/user/project")
# Returns: "a1b2c3d4e5f6g7h8" (identical)
```

**Cross-Platform Consistency:**
- Windows: `C:\Users\project` → normalized to `C:/Users/project`
- Unix: `/home/user/project` → already normalized
- Ensures same codebase gets same ID regardless of OS

#### `generate_feature_id(directory_path: str) -> str`

Generates a unique 16-character identifier for a feature directory using SHA-256 hash.

**Usage:**
```python
from src.utils.file_utils import generate_feature_id

feature_id = generate_feature_id("/home/user/project/src/routes")
# Returns: "f1e2d3c4b5a69788"
```

#### `is_file_too_large(file_path: str, max_size_mb: int = 10) -> bool`

Checks if a file exceeds the maximum allowed size (default: 10MB).

**Usage:**
```python
from src.utils.file_utils import is_file_too_large

if not is_file_too_large("large_file.json"):
    # Process file
    pass
```

#### `get_file_extension(file_path: str) -> str`

Returns the lowercase file extension including the dot.

**Usage:**
```python
from src.utils.file_utils import get_file_extension

ext = get_file_extension("script.py")
# Returns: ".py"
```

#### `is_text_file(file_path: str) -> bool`

Checks if a file is likely a text file based on its extension.

**Supported Extensions:**
- Programming: `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.java`, `.go`, `.rs`, `.rb`, `.php`, `.cs`, `.cpp`, `.c`, `.h`, `.hpp`
- Config: `.json`, `.yaml`, `.yml`, `.xml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.env`
- Documentation: `.txt`, `.md`
- Web: `.html`, `.css`, `.scss`, `.sass`, `.less`
- Scripts: `.sql`, `.sh`, `.bash`

**Usage:**
```python
from src.utils.file_utils import is_text_file

if is_text_file("script.py"):
    # Read and analyze file
    pass
```

## Design Principles

### Security

1. **Path Sanitization**: All paths are sanitized to prevent directory traversal attacks
2. **Error Handling**: Functions gracefully handle permission errors and missing files
3. **Validation**: Input validation prevents malicious or malformed paths

### Cross-Platform Compatibility

1. **Path Normalization**: Handles both Windows backslashes and Unix forward slashes
2. **Absolute Paths**: Uses absolute paths for consistent hashing
3. **OS-Agnostic**: Works on Windows, macOS, and Linux

### Performance

1. **Efficient Hashing**: SHA-256 provides fast, collision-resistant hashing
2. **Minimal I/O**: File operations are optimized to minimize disk access
3. **Caching-Friendly**: Consistent IDs enable effective caching

### Consistency

1. **Deterministic IDs**: Same path always generates same ID
2. **Normalized Hashing**: Path normalization ensures cross-platform consistency
3. **Truncated Hashes**: 16-character IDs balance uniqueness with readability

## Integration with MCP Server

### Codebase Scanner (Task 6)

Uses utilities for:
- Path sanitization before scanning
- Directory size calculation
- Codebase ID generation
- File extension detection

### Framework Detector (Task 7)

Uses utilities for:
- Path validation for package.json and requirements.txt
- File size checks before parsing

### Feature Discoverer (Task 8)

Uses utilities for:
- Feature ID generation for discovered directories
- Path normalization for feature paths

### Cache Manager (Task 5)

Uses utilities for:
- Codebase ID as cache keys
- Feature ID for feature-specific caching

## Error Handling

All utility functions include comprehensive error handling:

```python
# Path sanitization
try:
    safe_path = sanitize_path(user_input)
except ValueError as e:
    # Handle invalid path
    print(f"Invalid path: {e}")

# File operations
try:
    size = calculate_file_size(file_path)
except FileNotFoundError:
    # Handle missing file
    pass
except OSError as e:
    # Handle permission or I/O errors
    pass
```

## Testing Considerations

### Unit Tests (Task 14)

Test coverage should include:

1. **Path Sanitization**
   - Valid paths
   - Traversal attempts (`../`, `~`)
   - Empty paths
   - Invalid characters

2. **File Operations**
   - Existing files
   - Missing files
   - Permission errors
   - Large files (>10MB)

3. **ID Generation**
   - Consistency (same path → same ID)
   - Cross-platform (Windows vs Unix paths)
   - Uniqueness (different paths → different IDs)

4. **Cross-Platform**
   - Windows paths with backslashes
   - Unix paths with forward slashes
   - Mixed separators

## Performance Characteristics

| Function | Time Complexity | Notes |
|----------|----------------|-------|
| `sanitize_path()` | O(n) | n = path length |
| `normalize_path()` | O(n) | n = path length |
| `calculate_file_size()` | O(1) | Single system call |
| `calculate_directory_size()` | O(n) | n = number of files |
| `generate_codebase_id()` | O(n) | n = path length, SHA-256 hashing |
| `generate_feature_id()` | O(n) | n = path length, SHA-256 hashing |
| `is_file_too_large()` | O(1) | Single system call |
| `get_file_extension()` | O(1) | String operation |
| `is_text_file()` | O(1) | Set lookup |

## Requirements Coverage

This module satisfies the following requirements:

- **Requirement 1.4**: Windows-specific path handling with backslashes and forward slashes
- **Requirement 3.3**: Generate unique codebase_id using SHA-256 hash (16 chars)
- **Requirement 5.5**: Generate unique feature_id using SHA-256 hash (16 chars)
- **Requirement 8.4**: Path sanitization removes ".." and "~" characters
- **Requirement 8.5**: Skip files exceeding MAX_FILE_SIZE (10MB)

## Next Steps

The utilities module is now complete and ready for use by:

1. **Task 5**: UnifiedCacheManager (uses codebase_id for cache keys)
2. **Task 6**: Codebase Scanner (uses path sanitization and ID generation)
3. **Task 7**: Framework Detector (uses path validation)
4. **Task 8**: Feature Discoverer (uses feature_id generation)

---

**Status**: ✅ Complete (Task 4)  
**Last Updated**: November 12, 2025
