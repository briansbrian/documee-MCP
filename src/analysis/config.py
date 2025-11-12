"""
Configuration for Analysis Engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AnalysisConfig:
    """Configuration for the Analysis Engine."""
    
    # File size limits
    max_file_size_mb: int = 10
    
    # Language support
    supported_languages: List[str] = field(default_factory=lambda: [
        'python',
        'javascript',
        'typescript',
        'java',
        'go',
        'rust',
        'cpp',
        'c_sharp',
        'ruby',
        'php'
    ])
    
    # Complexity thresholds
    max_complexity_threshold: int = 10
    min_complexity_threshold: int = 2
    
    # Documentation coverage
    min_documentation_coverage: float = 0.5
    
    # Teaching value weights
    teaching_value_weights: Dict[str, float] = field(default_factory=lambda: {
        'documentation': 0.3,
        'complexity': 0.25,
        'pattern': 0.25,
        'structure': 0.2
    })
    
    # Performance settings
    max_parallel_files: int = 10
    parse_timeout_seconds: int = 5
    
    # Linter integration
    enable_linters: bool = False
    
    # Cache settings
    cache_ttl_seconds: int = 3600
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'AnalysisConfig':
        """Create AnalysisConfig from dictionary."""
        analysis_config = config_dict.get('analysis', {})
        
        return cls(
            max_file_size_mb=analysis_config.get('max_file_size_mb', 10),
            supported_languages=analysis_config.get('supported_languages', cls.__dataclass_fields__['supported_languages'].default_factory()),
            max_complexity_threshold=analysis_config.get('max_complexity_threshold', 10),
            min_complexity_threshold=analysis_config.get('min_complexity_threshold', 2),
            min_documentation_coverage=analysis_config.get('min_documentation_coverage', 0.5),
            teaching_value_weights=analysis_config.get('teaching_value_weights', cls.__dataclass_fields__['teaching_value_weights'].default_factory()),
            max_parallel_files=analysis_config.get('max_parallel_files', 10),
            parse_timeout_seconds=analysis_config.get('parse_timeout_seconds', 5),
            enable_linters=analysis_config.get('enable_linters', False),
            cache_ttl_seconds=analysis_config.get('cache_ttl_seconds', 3600)
        )
