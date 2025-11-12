"""
Data models and schemas for MCP Server.

This module defines dataclasses for all tool responses and internal data structures.
All dataclasses support JSON serialization via the to_dict() method.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class ScanResult:
    """Result from scanning a codebase structure.
    
    Attributes:
        codebase_id: Unique SHA-256 hash identifier for the codebase
        structure: Dictionary containing total_files, total_directories, total_size_mb, 
                   languages dict, and file_types dict
        summary: Dictionary containing primary_language, project_type, has_tests, 
                 and size_category
        scan_time_ms: Actual execution time in milliseconds
        from_cache: Whether the result was retrieved from cache
    """
    codebase_id: str
    structure: Dict[str, Any]
    summary: Dict[str, Any]
    scan_time_ms: float
    from_cache: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class Framework:
    """Detected framework or library.
    
    Attributes:
        name: Framework name (e.g., "React", "Django")
        version: Version string from dependency file or "detected"
        confidence: Confidence score from 0.0 to 1.0
        evidence: List of evidence strings (e.g., "package.json dependency")
    """
    name: str
    version: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class FrameworkDetectionResult:
    """Result from detecting frameworks in a codebase.
    
    Attributes:
        frameworks: List of detected Framework objects
        total_detected: Total number of frameworks detected
        confidence_threshold: Minimum confidence score used for filtering
        from_cache: Whether the result was retrieved from cache
    """
    frameworks: List[Framework]
    total_detected: int
    confidence_threshold: float
    from_cache: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Ensure frameworks are properly serialized
        result['frameworks'] = [f.to_dict() if hasattr(f, 'to_dict') else f 
                                for f in self.frameworks]
        return result


@dataclass
class Feature:
    """Discovered feature in a codebase.
    
    Attributes:
        id: Unique SHA-256 hash identifier for the feature
        name: Feature name (directory name)
        category: Feature category (routes, components, api, utils, hooks)
        path: Absolute path to the feature directory
        priority: Priority level (high for routes/api, medium for others)
    """
    id: str
    name: str
    category: str
    path: str
    priority: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class FeatureDiscoveryResult:
    """Result from discovering features in a codebase.
    
    Attributes:
        features: List of discovered Feature objects
        total_features: Total number of features discovered
        categories: List of unique categories found
        from_cache: Whether the result was retrieved from cache
    """
    features: List[Feature]
    total_features: int
    categories: List[str]
    from_cache: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Ensure features are properly serialized
        result['features'] = [f.to_dict() if hasattr(f, 'to_dict') else f 
                              for f in self.features]
        return result
