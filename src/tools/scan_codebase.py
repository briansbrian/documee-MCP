"""
Codebase Scanner Tool for MCP Server.

This module implements the scan_codebase tool that traverses a directory tree,
analyzes file types and languages, and generates a comprehensive structure summary.
Achieves God Mode performance through intelligent caching (2-3s first run, <0.1s cached).
"""

import logging
import os
import time
from typing import Dict, Any, Optional

from src.cache.unified_cache import UnifiedCacheManager
from src.utils.file_utils import (
    generate_codebase_id,
    calculate_file_size,
    bytes_to_mb,
    get_file_extension,
    is_file_too_large
)
from src.utils.path_utils import sanitize_path, is_valid_path


logger = logging.getLogger(__name__)


# Language detection by file extension
LANGUAGE_EXTENSIONS = {
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".py": "Python",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C++",
}


# Directories to skip during scanning
IGNORE_PATTERNS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    "__pycache__",
    "venv",
    "env",
    ".venv",
    "target",
    "out",
    "coverage",
    ".pytest_cache",
}


async def scan_codebase(
    path: str,
    max_depth: int = 10,
    use_cache: bool = True,
    cache_manager: Optional[UnifiedCacheManager] = None,
    max_file_size_mb: int = 10
) -> Dict[str, Any]:
    """
    Scan a codebase directory and analyze its structure, languages, and characteristics.
    
    This function traverses the directory tree up to max_depth, counts files by language,
    detects project type, and generates a unique codebase ID. Results are cached for
    1 hour to achieve God Mode performance (<0.1s on subsequent calls).
    
    Args:
        path: Directory path to scan
        max_depth: Maximum directory depth to traverse (default: 10)
        use_cache: Whether to use cached results if available (default: True)
        cache_manager: UnifiedCacheManager instance for caching
        max_file_size_mb: Maximum file size in MB to process (default: 10)
        
    Returns:
        Dictionary containing:
            - codebase_id: Unique 16-character identifier
            - structure: {total_files, total_directories, total_size_mb, languages, file_types}
            - summary: {primary_language, project_type, has_tests, size_category}
            - scan_time_ms: Execution time in milliseconds
            - from_cache: Whether result was from cache
            
    Raises:
        ValueError: If path is invalid or contains directory traversal attempts
        PermissionError: If access to path is denied
        
    Examples:
        >>> result = await scan_codebase("/path/to/project")
        >>> print(result["codebase_id"])
        "a1b2c3d4e5f6g7h8"
        >>> print(result["summary"]["primary_language"])
        "TypeScript"
    """
    start_time = time.time()
    
    # Validate and sanitize path
    try:
        sanitized_path = sanitize_path(path)
    except ValueError as e:
        logger.error(f"Invalid path: {path} - {e}")
        raise ValueError(f"Invalid path: {path}") from e
    
    # Check if path exists
    if not is_valid_path(sanitized_path):
        logger.error(f"Path does not exist: {sanitized_path}")
        raise ValueError(f"Path does not exist: {path}")
    
    # Check if path is a directory
    if not os.path.isdir(sanitized_path):
        logger.error(f"Path is not a directory: {sanitized_path}")
        raise ValueError(f"Path is not a directory: {path}")
    
    # Generate unique codebase ID
    codebase_id = generate_codebase_id(sanitized_path)
    logger.info(f"Scanning codebase: {sanitized_path} (ID: {codebase_id})")
    
    # Check cache if enabled
    if use_cache and cache_manager:
        cached_result = await cache_manager.get_analysis(f"scan:{codebase_id}")
        if cached_result:
            cache_time_ms = (time.time() - start_time) * 1000
            logger.info(f"Cache hit for codebase {codebase_id} ({cache_time_ms:.2f}ms)")
            cached_result["from_cache"] = True
            # Ensure resource is available even from cache
            await cache_manager.set_resource("structure", cached_result)
            return cached_result
    
    # Perform the scan
    try:
        structure = _scan_directory(sanitized_path, max_depth, max_file_size_mb)
        summary = _generate_summary(structure)
        
        scan_time_ms = (time.time() - start_time) * 1000
        
        result = {
            "codebase_id": codebase_id,
            "path": sanitized_path,  # Store path for later use
            "structure": structure,
            "summary": summary,
            "scan_time_ms": scan_time_ms,
            "from_cache": False
        }
        
        logger.info(
            f"Scan complete: {structure['total_files']} files, "
            f"{structure['total_directories']} dirs, "
            f"{structure['total_size_mb']:.2f}MB in {scan_time_ms:.2f}ms"
        )
        
        # Cache the result
        if cache_manager:
            await cache_manager.set_analysis(f"scan:{codebase_id}", result, ttl=3600)
            await cache_manager.set_resource("structure", result)
            await cache_manager.set_session(
                codebase_id,
                {"phase": "scanned", "timestamp": time.time()}
            )
            logger.debug(f"Cached scan result for {codebase_id}")
        
        # Log God Mode performance achievement
        if scan_time_ms < 3000:
            logger.info(
                f"God Mode performance achieved: scan completed in {scan_time_ms:.2f}ms "
                f"(target: <3000ms)"
            )
        elif scan_time_ms > 1000:
            logger.warning(
                f"Slow operation detected: scan_codebase took {scan_time_ms:.2f}ms"
            )
        
        return result
        
    except PermissionError as e:
        logger.error(f"Permission denied: {sanitized_path}")
        raise PermissionError(f"Permission denied: {path}") from e
    except Exception as e:
        logger.error(f"Error scanning codebase: {e}", exc_info=True)
        raise


def _scan_directory(
    root_path: str,
    max_depth: int,
    max_file_size_mb: int
) -> Dict[str, Any]:
    """
    Recursively scan a directory and collect statistics.
    
    Args:
        root_path: Root directory to scan
        max_depth: Maximum depth to traverse
        max_file_size_mb: Maximum file size in MB to process
        
    Returns:
        Dictionary with total_files, total_directories, total_size_mb, languages, file_types
    """
    total_files = 0
    total_directories = 0
    total_size_bytes = 0
    languages: Dict[str, int] = {}
    file_types: Dict[str, int] = {}
    
    # Calculate the depth of the root path for relative depth calculation
    root_depth = root_path.rstrip(os.sep).count(os.sep)
    
    try:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Calculate current depth relative to root
            current_depth = dirpath.count(os.sep) - root_depth
            
            # Check depth limit
            if current_depth >= max_depth:
                # Clear dirnames to prevent further traversal
                dirnames.clear()
                continue
            
            # Filter out ignored directories
            dirnames[:] = [d for d in dirnames if d not in IGNORE_PATTERNS]
            
            # Count this directory
            if dirpath != root_path:
                total_directories += 1
            
            # Process files in this directory
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                
                try:
                    # Check file size
                    if is_file_too_large(file_path, max_file_size_mb):
                        logger.warning(f"File too large, skipping: {file_path}")
                        continue
                    
                    # Get file size
                    try:
                        file_size = calculate_file_size(file_path)
                        total_size_bytes += file_size
                    except (OSError, FileNotFoundError) as e:
                        logger.debug(f"Cannot access file size: {file_path} - {e}")
                        continue
                    
                    # Count file
                    total_files += 1
                    
                    # Detect language by extension
                    ext = get_file_extension(filename)
                    if ext in LANGUAGE_EXTENSIONS:
                        language = LANGUAGE_EXTENSIONS[ext]
                        languages[language] = languages.get(language, 0) + 1
                    
                    # Count file types
                    if ext:
                        file_types[ext] = file_types.get(ext, 0) + 1
                    else:
                        file_types["no_extension"] = file_types.get("no_extension", 0) + 1
                        
                except (OSError, PermissionError) as e:
                    logger.debug(f"Cannot access file: {file_path} - {e}")
                    continue
                    
    except (OSError, PermissionError) as e:
        logger.warning(f"Error walking directory {root_path}: {e}")
    
    total_size_mb = bytes_to_mb(total_size_bytes)
    
    return {
        "total_files": total_files,
        "total_directories": total_directories,
        "total_size_mb": total_size_mb,
        "languages": languages,
        "file_types": file_types
    }


def _generate_summary(structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a high-level summary from the structure data.
    
    Args:
        structure: Structure dictionary from _scan_directory
        
    Returns:
        Dictionary with primary_language, project_type, has_tests, size_category
    """
    languages = structure["languages"]
    file_types = structure["file_types"]
    total_files = structure["total_files"]
    
    # Determine primary language (most common)
    primary_language = "Unknown"
    if languages:
        primary_language = max(languages.items(), key=lambda x: x[1])[0]
    
    # Determine project type
    project_type = "Unknown"
    if "JavaScript" in languages or "TypeScript" in languages:
        # Check for web framework indicators
        if ".jsx" in file_types or ".tsx" in file_types:
            project_type = "web-application"
        else:
            project_type = "javascript-application"
    elif "Python" in languages:
        project_type = "python-application"
    elif "Java" in languages:
        project_type = "java-application"
    elif "Go" in languages:
        project_type = "go-application"
    elif "Rust" in languages:
        project_type = "rust-application"
    
    # Check for tests
    has_tests = any(
        ext in file_types 
        for ext in [".test.js", ".test.ts", ".spec.js", ".spec.ts"]
    ) or "test" in str(file_types).lower()
    
    # Determine size category
    if total_files < 100:
        size_category = "small"
    elif total_files < 1000:
        size_category = "medium"
    else:
        size_category = "large"
    
    return {
        "primary_language": primary_language,
        "project_type": project_type,
        "has_tests": has_tests,
        "size_category": size_category
    }
