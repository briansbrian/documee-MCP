"""Configuration management for MCP Server.

This module provides the Settings class that loads configuration from config.yaml,
applies environment variable overrides, and validates configuration values.
"""

import os
import logging
from pathlib import Path
from typing import Any, Optional
import yaml


logger = logging.getLogger(__name__)


class Settings:
    """Configuration settings manager.
    
    Loads settings from config.yaml and applies environment variable overrides.
    Provides validated access to all configuration values.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize settings.
        
        Args:
            config_path: Path to config.yaml file (default: "config.yaml")
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._apply_env_overrides()
        self._validate()
    
    def _load_config(self) -> dict:
        """Load configuration from config.yaml or use defaults.
        
        Returns:
            Configuration dictionary
        """
        # Default configuration
        default_config = {
            "server": {
                "name": "codebase-to-course-mcp",
                "version": "1.0.0",
                "transport": "stdio"
            },
            "cache": {
                "memory": {
                    "max_size_mb": 500
                },
                "sqlite": {
                    "enabled": True,
                    "path": "cache_db/cache.db"
                },
                "redis": {
                    "enabled": False,
                    "url": None
                }
            },
            "analysis": {
                "max_file_size_mb": 10,
                "max_files_per_scan": 10000,
                "max_parallel_reads": 10,
                "scan_timeout_seconds": 30
            },
            "security": {
                "allowed_paths": [],
                "max_depth": 10,
                "blocked_patterns": [
                    "node_modules", ".git", "dist", "build", ".next",
                    "__pycache__", "venv", "env", ".venv", "target",
                    "out", "coverage", ".pytest_cache"
                ]
            },
            "performance": {
                "enable_profiling": False,
                "log_slow_operations": True,
                "slow_operation_threshold_ms": 1000
            },
            "logging": {
                "level": "INFO",
                "file": "server.log",
                "max_size_mb": 10,
                "backup_count": 3
            },
            "ai_enrichment": {
                "skill_level": "beginner",
                "tone": "casual",
                "depth": "detailed",
                "content_options": {
                    "include_analogies": True,
                    "include_diagrams": True,
                    "include_examples": True,
                    "include_exercises": True,
                    "include_best_practices": True,
                    "include_anti_patterns": True,
                    "include_real_world_context": True,
                    "progressive_hints": True
                },
                "evidence_requirements": {
                    "always_cite_sources": True,
                    "validate_against_tests": True,
                    "cross_reference_files": True,
                    "include_git_context": True
                },
                "teaching_value": {
                    "min_score_to_teach": 7,
                    "prioritize_fundamentals": True,
                    "focus_on_reusability": True
                }
            }
        }
        
        # Try to load from config.yaml
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        # Merge loaded config with defaults (loaded config takes precedence)
                        config = self._deep_merge(default_config, loaded_config)
                        logger.info(f"Configuration loaded from {self.config_path}")
                        return config
            except Exception as e:
                logger.warning(f"Failed to load {self.config_path}: {e}. Using defaults.")
        else:
            logger.warning(f"{self.config_path} not found, using defaults")
        
        return default_config
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        # Cache overrides
        if "CACHE_MAX_SIZE_MB" in os.environ:
            try:
                self.config["cache"]["memory"]["max_size_mb"] = int(os.environ["CACHE_MAX_SIZE_MB"])
                logger.info(f"Override: cache.memory.max_size_mb = {os.environ['CACHE_MAX_SIZE_MB']}")
            except ValueError:
                logger.warning(f"Invalid CACHE_MAX_SIZE_MB value: {os.environ['CACHE_MAX_SIZE_MB']}")
        
        if "REDIS_URL" in os.environ:
            redis_url = os.environ["REDIS_URL"]
            self.config["cache"]["redis"]["url"] = redis_url if redis_url else None
            self.config["cache"]["redis"]["enabled"] = bool(redis_url)
            logger.info(f"Override: cache.redis.url = {redis_url}")
        
        # Analysis overrides
        if "MAX_FILE_SIZE_MB" in os.environ:
            try:
                self.config["analysis"]["max_file_size_mb"] = int(os.environ["MAX_FILE_SIZE_MB"])
                logger.info(f"Override: analysis.max_file_size_mb = {os.environ['MAX_FILE_SIZE_MB']}")
            except ValueError:
                logger.warning(f"Invalid MAX_FILE_SIZE_MB value: {os.environ['MAX_FILE_SIZE_MB']}")
        
        # Enrichment overrides
        if "ENRICHMENT_SKILL_LEVEL" in os.environ:
            skill_level = os.environ["ENRICHMENT_SKILL_LEVEL"]
            if skill_level in ["beginner", "intermediate", "advanced"]:
                self.config["ai_enrichment"]["skill_level"] = skill_level
                logger.info(f"Override: ai_enrichment.skill_level = {skill_level}")
            else:
                logger.warning(f"Invalid ENRICHMENT_SKILL_LEVEL value: {skill_level}")
        
        if "ENRICHMENT_TONE" in os.environ:
            tone = os.environ["ENRICHMENT_TONE"]
            if tone in ["casual", "formal", "technical"]:
                self.config["ai_enrichment"]["tone"] = tone
                logger.info(f"Override: ai_enrichment.tone = {tone}")
            else:
                logger.warning(f"Invalid ENRICHMENT_TONE value: {tone}")
        
        if "ENRICHMENT_DEPTH" in os.environ:
            depth = os.environ["ENRICHMENT_DEPTH"]
            if depth in ["brief", "moderate", "detailed", "comprehensive"]:
                self.config["ai_enrichment"]["depth"] = depth
                logger.info(f"Override: ai_enrichment.depth = {depth}")
            else:
                logger.warning(f"Invalid ENRICHMENT_DEPTH value: {depth}")
    
    def _validate(self):
        """Validate configuration values.
        
        Raises:
            ValueError: If configuration values are invalid
        """
        # Validate cache settings
        max_memory_mb = self.config["cache"]["memory"]["max_size_mb"]
        if max_memory_mb <= 0:
            raise ValueError(f"Invalid configuration: cache.memory.max_size_mb must be positive, got {max_memory_mb}")
        
        # Validate analysis settings
        max_file_size_mb = self.config["analysis"]["max_file_size_mb"]
        if max_file_size_mb <= 0:
            raise ValueError(f"Invalid configuration: analysis.max_file_size_mb must be positive, got {max_file_size_mb}")
        
        max_files_per_scan = self.config["analysis"]["max_files_per_scan"]
        if max_files_per_scan <= 0:
            raise ValueError(f"Invalid configuration: analysis.max_files_per_scan must be positive, got {max_files_per_scan}")
        
        max_parallel_reads = self.config["analysis"]["max_parallel_reads"]
        if max_parallel_reads <= 0:
            raise ValueError(f"Invalid configuration: analysis.max_parallel_reads must be positive, got {max_parallel_reads}")
        
        scan_timeout_seconds = self.config["analysis"]["scan_timeout_seconds"]
        if scan_timeout_seconds <= 0:
            raise ValueError(f"Invalid configuration: analysis.scan_timeout_seconds must be positive, got {scan_timeout_seconds}")
        
        # Validate security settings
        max_depth = self.config["security"]["max_depth"]
        if max_depth <= 0:
            raise ValueError(f"Invalid configuration: security.max_depth must be positive, got {max_depth}")
        
        # Validate SQLite path
        sqlite_path = self.config["cache"]["sqlite"]["path"]
        sqlite_dir = os.path.dirname(sqlite_path)
        if sqlite_dir and not os.path.exists(sqlite_dir):
            try:
                os.makedirs(sqlite_dir, exist_ok=True)
                logger.info(f"Created directory for SQLite database: {sqlite_dir}")
            except Exception as e:
                raise ValueError(f"Invalid configuration: cannot create directory for sqlite path {sqlite_path}: {e}")
        
        # Validate performance settings
        threshold_ms = self.config["performance"]["slow_operation_threshold_ms"]
        if threshold_ms <= 0:
            raise ValueError(f"Invalid configuration: performance.slow_operation_threshold_ms must be positive, got {threshold_ms}")
        
        # Validate logging settings
        log_max_size_mb = self.config["logging"]["max_size_mb"]
        if log_max_size_mb <= 0:
            raise ValueError(f"Invalid configuration: logging.max_size_mb must be positive, got {log_max_size_mb}")
        
        backup_count = self.config["logging"]["backup_count"]
        if backup_count < 0:
            raise ValueError(f"Invalid configuration: logging.backup_count must be non-negative, got {backup_count}")
        
        # Validate enrichment settings
        valid_skill_levels = ["beginner", "intermediate", "advanced"]
        skill_level = self.config["ai_enrichment"]["skill_level"]
        if skill_level not in valid_skill_levels:
            raise ValueError(f"Invalid configuration: ai_enrichment.skill_level must be one of {valid_skill_levels}, got {skill_level}")
        
        valid_tones = ["casual", "formal", "technical"]
        tone = self.config["ai_enrichment"]["tone"]
        if tone not in valid_tones:
            raise ValueError(f"Invalid configuration: ai_enrichment.tone must be one of {valid_tones}, got {tone}")
        
        valid_depths = ["brief", "moderate", "detailed", "comprehensive"]
        depth = self.config["ai_enrichment"]["depth"]
        if depth not in valid_depths:
            raise ValueError(f"Invalid configuration: ai_enrichment.depth must be one of {valid_depths}, got {depth}")
        
        min_score = self.config["ai_enrichment"]["teaching_value"]["min_score_to_teach"]
        if not (0 <= min_score <= 14):
            raise ValueError(f"Invalid configuration: ai_enrichment.teaching_value.min_score_to_teach must be between 0 and 14, got {min_score}")
    
    # Property accessors for easy access to configuration values
    
    @property
    def server_name(self) -> str:
        """Get server name."""
        return self.config["server"]["name"]
    
    @property
    def server_version(self) -> str:
        """Get server version."""
        return self.config["server"]["version"]
    
    @property
    def server_transport(self) -> str:
        """Get server transport."""
        return self.config["server"]["transport"]
    
    @property
    def cache_max_memory_mb(self) -> int:
        """Get maximum memory cache size in MB."""
        return self.config["cache"]["memory"]["max_size_mb"]
    
    @property
    def sqlite_enabled(self) -> bool:
        """Check if SQLite cache is enabled."""
        return self.config["cache"]["sqlite"]["enabled"]
    
    @property
    def sqlite_path(self) -> str:
        """Get SQLite database path."""
        return self.config["cache"]["sqlite"]["path"]
    
    @property
    def redis_enabled(self) -> bool:
        """Check if Redis cache is enabled."""
        return self.config["cache"]["redis"]["enabled"]
    
    @property
    def redis_url(self) -> Optional[str]:
        """Get Redis URL."""
        return self.config["cache"]["redis"]["url"]
    
    @property
    def max_file_size_mb(self) -> int:
        """Get maximum file size in MB."""
        return self.config["analysis"]["max_file_size_mb"]
    
    @property
    def max_files_per_scan(self) -> int:
        """Get maximum files per scan."""
        return self.config["analysis"]["max_files_per_scan"]
    
    @property
    def max_parallel_reads(self) -> int:
        """Get maximum parallel reads."""
        return self.config["analysis"]["max_parallel_reads"]
    
    @property
    def scan_timeout_seconds(self) -> int:
        """Get scan timeout in seconds."""
        return self.config["analysis"]["scan_timeout_seconds"]
    
    @property
    def allowed_paths(self) -> list:
        """Get allowed paths."""
        return self.config["security"]["allowed_paths"]
    
    @property
    def max_depth(self) -> int:
        """Get maximum directory depth."""
        return self.config["security"]["max_depth"]
    
    @property
    def blocked_patterns(self) -> list:
        """Get blocked directory patterns."""
        return self.config["security"]["blocked_patterns"]
    
    @property
    def enable_profiling(self) -> bool:
        """Check if profiling is enabled."""
        return self.config["performance"]["enable_profiling"]
    
    @property
    def log_slow_operations(self) -> bool:
        """Check if slow operations logging is enabled."""
        return self.config["performance"]["log_slow_operations"]
    
    @property
    def slow_operation_threshold_ms(self) -> int:
        """Get slow operation threshold in milliseconds."""
        return self.config["performance"]["slow_operation_threshold_ms"]
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.config["logging"]["level"]
    
    @property
    def log_file(self) -> str:
        """Get log file path."""
        return self.config["logging"]["file"]
    
    @property
    def log_max_size_mb(self) -> int:
        """Get log file maximum size in MB."""
        return self.config["logging"]["max_size_mb"]
    
    @property
    def log_backup_count(self) -> int:
        """Get log file backup count."""
        return self.config["logging"]["backup_count"]
    
    # AI Enrichment Configuration
    
    @property
    def enrichment_skill_level(self) -> str:
        """Get enrichment skill level (beginner, intermediate, advanced)."""
        return self.config["ai_enrichment"]["skill_level"]
    
    @property
    def enrichment_tone(self) -> str:
        """Get enrichment tone (casual, formal, technical)."""
        return self.config["ai_enrichment"]["tone"]
    
    @property
    def enrichment_depth(self) -> str:
        """Get enrichment depth (brief, moderate, detailed, comprehensive)."""
        return self.config["ai_enrichment"]["depth"]
    
    @property
    def enrichment_content_options(self) -> dict:
        """Get enrichment content options."""
        return self.config["ai_enrichment"]["content_options"]
    
    @property
    def enrichment_evidence_requirements(self) -> dict:
        """Get enrichment evidence requirements."""
        return self.config["ai_enrichment"]["evidence_requirements"]
    
    @property
    def enrichment_teaching_value(self) -> dict:
        """Get enrichment teaching value settings."""
        return self.config["ai_enrichment"]["teaching_value"]
    
    @property
    def enrichment_min_score_to_teach(self) -> int:
        """Get minimum teaching value score to include content."""
        return self.config["ai_enrichment"]["teaching_value"]["min_score_to_teach"]
    
    @property
    def enrichment_include_analogies(self) -> bool:
        """Check if analogies should be included."""
        return self.config["ai_enrichment"]["content_options"]["include_analogies"]
    
    @property
    def enrichment_include_diagrams(self) -> bool:
        """Check if diagrams should be included."""
        return self.config["ai_enrichment"]["content_options"]["include_diagrams"]
    
    @property
    def enrichment_always_cite_sources(self) -> bool:
        """Check if sources must always be cited."""
        return self.config["ai_enrichment"]["evidence_requirements"]["always_cite_sources"]
    
    @property
    def enrichment_validate_against_tests(self) -> bool:
        """Check if validation against tests is required."""
        return self.config["ai_enrichment"]["evidence_requirements"]["validate_against_tests"]
