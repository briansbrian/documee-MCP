"""Example of using the logging system with configuration.

This example demonstrates how to initialize and use the logging system
with settings from config.yaml.
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.config.settings import Settings
from src.utils.logger import initialize_logging, get_logger


def main():
    """Main function demonstrating logging usage."""
    # Load configuration
    config = Settings()
    
    # Initialize logging with settings from config
    initialize_logging(
        log_level=config.log_level,
        log_file=config.log_file,
        log_max_size_mb=config.log_max_size_mb,
        log_backup_count=config.log_backup_count,
        server_name=config.server_name,
        server_version=config.server_version
    )
    
    # Get logger instance
    logger = get_logger()
    
    # Example: Log tool invocation
    logger.log_tool_invocation("scan_codebase", {
        "path": "/example/project",
        "max_depth": 10,
        "use_cache": True
    })
    
    # Example: Log tool completion
    logger.log_tool_completion("scan_codebase", 2500.0, config.slow_operation_threshold_ms)
    
    # Example: Log cache statistics
    cache_stats = {
        "hit_rate": 0.85,
        "memory_hits": 150,
        "sqlite_hits": 30,
        "evictions": 2,
        "current_memory_mb": 200.0,
        "total_requests": 200
    }
    logger.log_cache_stats(cache_stats)
    
    # Example: Log God Mode performance
    logger.log_god_mode_performance("scan", 2500.0, 3000.0)
    
    # Example: Log info message
    logger.log_info("Processing completed successfully")
    
    # Example: Log warning
    logger.log_warning("Cache approaching memory limit")
    
    # Example: Log error with exception
    try:
        # Simulate an error
        raise ValueError("Example error")
    except Exception:
        logger.log_error("Failed to process request")
    
    # Log server shutdown
    logger.log_server_shutdown()
    
    print(f"\nLogging example completed. Check {config.log_file} for output.")


if __name__ == "__main__":
    main()
