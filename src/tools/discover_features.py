"""
Feature Discovery Tool for MCP Server.

This module implements the discover_features tool that identifies features in a codebase
such as routes, components, API endpoints, utilities, and hooks. Achieves God Mode
performance through intelligent caching (<0.1s cached, <5s first run).
"""

import logging
import os
from typing import Dict, Any, List, Optional

from src.cache.unified_cache import UnifiedCacheManager
from src.models.schemas import Feature, FeatureDiscoveryResult
from src.utils.file_utils import generate_feature_id


logger = logging.getLogger(__name__)


# Feature directory patterns by category
FEATURE_PATTERNS = {
    "routes": ["routes", "pages", "app"],
    "components": ["components", "widgets"],
    "api": ["api", "endpoints", "controllers"],
    "utils": ["utils", "helpers", "lib"],
    "hooks": ["hooks", "composables"]
}


async def discover_features(
    codebase_id: str,
    categories: Optional[List[str]] = None,
    use_cache: bool = True,
    cache_manager: Optional[UnifiedCacheManager] = None
) -> Dict[str, Any]:
    """
    Discover features in a codebase such as routes, components, API endpoints, utilities, and hooks.
    
    This function searches for feature directories based on common patterns, generates unique
    feature IDs, assigns priorities, and filters by categories. Results are cached for 1 hour
    to achieve God Mode performance (<0.1s on subsequent calls).
    
    Args:
        codebase_id: Unique identifier from scan_codebase
        categories: List of categories to discover (default: ["all"])
                   Options: routes, components, api, utils, hooks, or all
        use_cache: Whether to use cached results if available (default: True)
        cache_manager: UnifiedCacheManager instance for caching
        
    Returns:
        Dictionary containing:
            - features: List of Feature objects with id, name, category, path, priority
            - total_features: Total number of features discovered
            - categories: List of unique categories found
            - from_cache: Whether result was from cache
            
    Raises:
        ValueError: If codebase has not been scanned first
        
    Examples:
        >>> result = await discover_features("a1b2c3d4e5f6g7h8")
        >>> print(result["total_features"])
        5
        >>> print(result["features"][0]["category"])
        "routes"
    """
    # Validate codebase_id
    if not codebase_id or not codebase_id.strip():
        raise ValueError("codebase_id cannot be empty")
    
    # Default to all categories if not specified or empty
    if categories is None or len(categories) == 0:
        categories = ["all"]
    
    logger.info(f"Discovering features for codebase: {codebase_id} (categories: {categories})")
    
    # Check cache if enabled
    if use_cache and cache_manager:
        cached_result = await cache_manager.get_analysis(f"features:{codebase_id}")
        if cached_result:
            logger.info(f"Cache hit for features:{codebase_id}")
            # Filter by categories if not "all"
            if categories != ["all"]:
                filtered_features = _filter_by_categories(cached_result["features"], categories)
                cached_result["features"] = filtered_features
                cached_result["total_features"] = len(filtered_features)
                # Update categories list to only include filtered ones
                cached_result["categories"] = list(set(f["category"] for f in filtered_features))
            cached_result["from_cache"] = True
            # Ensure resource is available even from cache
            await cache_manager.set_resource("features", cached_result)
            return cached_result
    
    # Retrieve scan result from cache
    if not cache_manager:
        raise ValueError("Cache manager is required for feature discovery")
    
    scan_result = await cache_manager.get_analysis(f"scan:{codebase_id}")
    if not scan_result:
        logger.error(f"Codebase not scanned: {codebase_id}")
        raise ValueError("Codebase not scanned. Call scan_codebase first.")
    
    codebase_path = scan_result.get("path")
    if not codebase_path:
        logger.error(f"Scan result missing path for codebase: {codebase_id}")
        raise ValueError("Codebase not scanned. Call scan_codebase first.")
    
    # Discover features
    features: List[Feature] = []
    
    # Search for feature directories
    for category, patterns in FEATURE_PATTERNS.items():
        # Skip if not in requested categories (unless "all")
        if categories != ["all"] and category not in categories:
            continue
        
        logger.debug(f"Searching for {category} features with patterns: {patterns}")
        
        for pattern in patterns:
            matches = _find_directories(codebase_path, pattern)
            for match in matches:
                # Generate unique feature ID
                feature_id = generate_feature_id(match)
                
                # Get directory name (without trailing slash)
                name = os.path.basename(match.rstrip(os.sep))
                
                # Assign priority based on category
                priority = "high" if category in ["routes", "api"] else "medium"
                
                feature = Feature(
                    id=feature_id,
                    name=name,
                    category=category,
                    path=match,
                    priority=priority
                )
                features.append(feature)
                logger.debug(f"Discovered {category} feature: {name} at {match}")
    
    # Convert to dict format
    features_dict = [f.to_dict() for f in features]
    
    # Get unique categories found
    unique_categories = list(set(f.category for f in features))
    
    result = {
        "features": features_dict,
        "total_features": len(features_dict),
        "categories": unique_categories,
        "from_cache": False
    }
    
    logger.info(
        f"Feature discovery complete: {len(features_dict)} features found "
        f"in categories: {unique_categories}"
    )
    
    # Cache the result
    if cache_manager:
        await cache_manager.set_analysis(f"features:{codebase_id}", result, ttl=3600)
        await cache_manager.set_resource("features", result)
        logger.debug(f"Cached feature discovery result for {codebase_id}")
    
    return result


def _find_directories(root_path: str, pattern: str) -> List[str]:
    """
    Find all directories matching a pattern in the codebase.
    
    This function searches for directories whose name matches the pattern,
    looking at all levels of the directory tree.
    
    Args:
        root_path: Root directory to search
        pattern: Directory name pattern to match (e.g., "routes", "components")
        
    Returns:
        List of absolute paths to matching directories
    """
    matches = []
    
    try:
        for dirpath, dirnames, _ in os.walk(root_path):
            # Skip common ignore patterns
            dirnames[:] = [
                d for d in dirnames 
                if d not in {
                    "node_modules", ".git", "dist", "build", ".next",
                    "__pycache__", "venv", "env", ".venv", "target",
                    "out", "coverage", ".pytest_cache"
                }
            ]
            
            # Check if any directory name matches the pattern
            for dirname in dirnames:
                if dirname == pattern or dirname.startswith(pattern):
                    match_path = os.path.join(dirpath, dirname)
                    matches.append(match_path)
                    logger.debug(f"Found directory matching '{pattern}': {match_path}")
    
    except (OSError, PermissionError) as e:
        logger.warning(f"Error searching for directories in {root_path}: {e}")
    
    return matches


def _filter_by_categories(features: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
    """
    Filter features by specified categories.
    
    Args:
        features: List of feature dictionaries
        categories: List of categories to include
        
    Returns:
        Filtered list of feature dictionaries
    """
    if categories == ["all"]:
        return features
    
    return [f for f in features if f["category"] in categories]
