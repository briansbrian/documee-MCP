"""Logging system for MCP Server.

This module provides centralized logging functionality with support for:
- Console and file handlers
- Configurable log levels
- Performance tracking
- God Mode achievement logging
- Structured logging for tool invocations
"""

import logging
import logging.handlers
import sys
from typing import Optional, Dict, Any
from pathlib import Path


class MCPLogger:
    """Centralized logger for MCP Server.
    
    Provides structured logging with console and file handlers,
    performance tracking, and God Mode achievement logging.
    """
    
    _instance: Optional['MCPLogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger (only once)."""
        if not self._initialized:
            self.logger: Optional[logging.Logger] = None
            self.config: Optional[Dict[str, Any]] = None
            MCPLogger._initialized = True
    
    def initialize(
        self,
        log_level: str = "INFO",
        log_file: str = "server.log",
        log_max_size_mb: int = 10,
        log_backup_count: int = 3,
        server_name: str = "codebase-to-course-mcp",
        server_version: str = "1.0.0"
    ):
        """Initialize the logging system.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file
            log_max_size_mb: Maximum log file size in MB before rotation
            log_backup_count: Number of backup log files to keep
            server_name: Name of the server for logging
            server_version: Version of the server for logging
        """
        if self.logger is not None:
            # Already initialized
            return
        
        # Store configuration
        self.config = {
            "log_level": log_level,
            "log_file": log_file,
            "log_max_size_mb": log_max_size_mb,
            "log_backup_count": log_backup_count,
            "server_name": server_name,
            "server_version": server_version
        }
        
        # Create logger
        self.logger = logging.getLogger(server_name)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Add console handler (StreamHandler)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Add file handler (RotatingFileHandler for log rotation)
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler
            max_bytes = log_max_size_mb * 1024 * 1024  # Convert MB to bytes
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=log_backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            # If file handler fails, log to console only
            self.logger.warning(f"Failed to create file handler for {log_file}: {e}")
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        # Log server startup
        self.log_server_startup()
    
    def get_logger(self) -> logging.Logger:
        """Get the logger instance.
        
        Returns:
            Logger instance
            
        Raises:
            RuntimeError: If logger is not initialized
        """
        if self.logger is None:
            raise RuntimeError("Logger not initialized. Call initialize() first.")
        return self.logger
    
    def log_server_startup(self):
        """Log server startup message."""
        if self.logger and self.config:
            self.logger.info(
                f"MCP Server started: {self.config['server_name']} v{self.config['server_version']}"
            )
    
    def log_server_shutdown(self):
        """Log server shutdown message."""
        if self.logger:
            self.logger.info("MCP Server shutting down gracefully")
    
    def log_tool_invocation(self, tool_name: str, arguments: Dict[str, Any]):
        """Log tool invocation.
        
        Args:
            tool_name: Name of the tool being invoked
            arguments: Tool arguments
        """
        if self.logger:
            # Sanitize arguments for logging (remove sensitive data if any)
            safe_args = self._sanitize_arguments(arguments)
            self.logger.info(f"Tool invoked: {tool_name} with arguments: {safe_args}")
    
    def log_tool_completion(self, tool_name: str, duration_ms: float, slow_threshold_ms: int = 1000):
        """Log tool completion with performance tracking.
        
        Args:
            tool_name: Name of the tool that completed
            duration_ms: Execution duration in milliseconds
            slow_threshold_ms: Threshold for slow operation warning
        """
        if self.logger:
            self.logger.info(f"Tool completed: {tool_name} in {duration_ms:.2f}ms")
            
            # Log slow operations
            if duration_ms > slow_threshold_ms:
                self.logger.warning(
                    f"Slow operation detected: {tool_name} took {duration_ms:.2f}ms "
                    f"(threshold: {slow_threshold_ms}ms)"
                )
    
    def log_error(self, message: str, exc_info: bool = True):
        """Log error with full stack trace.
        
        Args:
            message: Error message
            exc_info: Whether to include exception info (default: True)
        """
        if self.logger:
            if exc_info:
                self.logger.exception(message)
            else:
                self.logger.error(message)
    
    def log_cache_stats(self, stats: Dict[str, Any]):
        """Log cache statistics.
        
        Args:
            stats: Cache statistics dictionary with keys:
                - hit_rate: Cache hit rate (0.0-1.0)
                - memory_hits: Number of memory cache hits
                - sqlite_hits: Number of SQLite cache hits
                - redis_hits: Number of Redis cache hits (optional)
                - evictions: Number of cache evictions
                - current_memory_mb: Current memory usage in MB
                - total_requests: Total cache requests
        """
        if self.logger:
            hit_rate = stats.get("hit_rate", 0.0)
            memory_hits = stats.get("memory_hits", 0)
            sqlite_hits = stats.get("sqlite_hits", 0)
            redis_hits = stats.get("redis_hits", 0)
            evictions = stats.get("evictions", 0)
            current_memory_mb = stats.get("current_memory_mb", 0.0)
            total_requests = stats.get("total_requests", 0)
            
            log_msg = (
                f"Cache stats: hit_rate={hit_rate:.2%}, "
                f"memory_hits={memory_hits}, "
                f"sqlite_hits={sqlite_hits}"
            )
            
            if redis_hits > 0:
                log_msg += f", redis_hits={redis_hits}"
            
            log_msg += f", evictions={evictions}"
            
            self.logger.info(log_msg)
            
            # Log God Mode cache performance achievement
            if hit_rate > 0.70 and total_requests > 10:
                self.logger.info(
                    f"God Mode cache performance achieved: hit_rate={hit_rate:.2%} "
                    f"(target: >70%)"
                )
    
    def log_god_mode_performance(
        self,
        operation: str,
        duration_ms: float,
        target_ms: float,
        achieved: bool = None
    ):
        """Log God Mode performance achievements.
        
        Args:
            operation: Name of the operation (e.g., "scan", "detect_frameworks")
            duration_ms: Actual duration in milliseconds
            target_ms: Target duration in milliseconds
            achieved: Whether target was achieved (auto-calculated if None)
        """
        if self.logger:
            if achieved is None:
                achieved = duration_ms <= target_ms
            
            if achieved:
                self.logger.info(
                    f"God Mode performance achieved: {operation} completed in "
                    f"{duration_ms:.2f}ms (target: <{target_ms}ms)"
                )
            else:
                self.logger.warning(
                    f"God Mode performance target missed: {operation} took "
                    f"{duration_ms:.2f}ms (target: <{target_ms}ms)"
                )
    
    def log_debug(self, message: str):
        """Log debug message.
        
        Args:
            message: Debug message
        """
        if self.logger:
            self.logger.debug(message)
    
    def log_info(self, message: str):
        """Log info message.
        
        Args:
            message: Info message
        """
        if self.logger:
            self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message.
        
        Args:
            message: Warning message
        """
        if self.logger:
            self.logger.warning(message)
    
    def _sanitize_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize arguments for logging (remove sensitive data).
        
        Args:
            arguments: Original arguments
            
        Returns:
            Sanitized arguments
        """
        # Create a copy to avoid modifying original
        safe_args = arguments.copy()
        
        # List of sensitive keys to redact
        sensitive_keys = ["password", "token", "secret", "api_key", "auth"]
        
        for key in safe_args:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                safe_args[key] = "***REDACTED***"
        
        return safe_args


# Global logger instance
_logger_instance = MCPLogger()


def initialize_logging(
    log_level: str = "INFO",
    log_file: str = "server.log",
    log_max_size_mb: int = 10,
    log_backup_count: int = 3,
    server_name: str = "codebase-to-course-mcp",
    server_version: str = "1.0.0"
):
    """Initialize the global logging system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        log_max_size_mb: Maximum log file size in MB before rotation
        log_backup_count: Number of backup log files to keep
        server_name: Name of the server for logging
        server_version: Version of the server for logging
    """
    _logger_instance.initialize(
        log_level=log_level,
        log_file=log_file,
        log_max_size_mb=log_max_size_mb,
        log_backup_count=log_backup_count,
        server_name=server_name,
        server_version=server_version
    )


def get_logger() -> MCPLogger:
    """Get the global logger instance.
    
    Returns:
        MCPLogger instance
    """
    return _logger_instance
