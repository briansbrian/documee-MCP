# Logging System Documentation

## Overview

The MCP Server includes a comprehensive logging system that provides:
- Console and file output with log rotation
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Performance tracking and God Mode achievement logging
- Structured logging for tool invocations
- Cache statistics logging
- Error logging with full stack traces

## Architecture

The logging system is implemented in `src/utils/logger.py` and consists of:

1. **MCPLogger**: Singleton class that manages the logging infrastructure
2. **initialize_logging()**: Function to initialize the global logger
3. **get_logger()**: Function to retrieve the logger instance

## Configuration

Logging is configured through `config.yaml`:

```yaml
logging:
  level: INFO                # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: server.log          # Log file path
  max_size_mb: 10           # Maximum log file size before rotation
  backup_count: 3           # Number of backup log files to keep
```

### Log Levels

- **DEBUG**: Detailed information for debugging (cache hits/misses, file operations, parameter values)
- **INFO**: General informational messages (tool invocations, completions, server lifecycle)
- **WARNING**: Warning messages (slow operations, approaching limits)
- **ERROR**: Error messages with stack traces
- **CRITICAL**: Critical errors that may cause system failure

## Usage

### Initialization

```python
from src.config.settings import Settings
from src.utils.logger import initialize_logging, get_logger

# Load configuration
config = Settings()

# Initialize logging
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
```

### Server Lifecycle Logging

```python
# Server startup (automatically logged during initialization)
# Output: "MCP Server started: codebase-to-course-mcp v1.0.0"

# Server shutdown
logger.log_server_shutdown()
# Output: "MCP Server shutting down gracefully"
```

### Tool Invocation Logging

```python
# Log tool invocation
logger.log_tool_invocation("scan_codebase", {
    "path": "/project/path",
    "max_depth": 10,
    "use_cache": True
})
# Output: "Tool invoked: scan_codebase with arguments: {'path': '/project/path', 'max_depth': 10, 'use_cache': True}"

# Log tool completion
logger.log_tool_completion("scan_codebase", 2500.0, slow_threshold_ms=1000)
# Output: "Tool completed: scan_codebase in 2500.00ms"
# Output: "Slow operation detected: scan_codebase took 2500.00ms (threshold: 1000ms)"
```

### Cache Statistics Logging

```python
cache_stats = {
    "hit_rate": 0.75,
    "memory_hits": 100,
    "sqlite_hits": 50,
    "redis_hits": 10,
    "evictions": 5,
    "current_memory_mb": 250.5,
    "total_requests": 200
}
logger.log_cache_stats(cache_stats)
# Output: "Cache stats: hit_rate=75.00%, memory_hits=100, sqlite_hits=50, redis_hits=10, evictions=5"
# Output: "God Mode cache performance achieved: hit_rate=75.00% (target: >70%)"
```

### God Mode Performance Logging

```python
# Log performance achievement
logger.log_god_mode_performance("scan", 2500.0, 3000.0)
# Output: "God Mode performance achieved: scan completed in 2500.00ms (target: <3000.0ms)"

# Log performance target missed
logger.log_god_mode_performance("scan", 3500.0, 3000.0)
# Output: "God Mode performance target missed: scan took 3500.00ms (target: <3000.0ms)"
```

### Error Logging

```python
try:
    # Some operation that may fail
    result = risky_operation()
except Exception:
    logger.log_error("Operation failed")
    # Logs error with full stack trace
```

### General Logging

```python
# Debug messages (only logged when log_level=DEBUG)
logger.log_debug("Cache hit for key: scan:abc123")

# Info messages
logger.log_info("Processing completed successfully")

# Warning messages
logger.log_warning("Cache approaching memory limit")
```

## Log Format

All log entries follow this format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Example:
```
2025-11-12 04:48:02,050 - codebase-to-course-mcp - INFO - MCP Server started: codebase-to-course-mcp v1.0.0
```

## Log Rotation

The logging system uses `RotatingFileHandler` to automatically rotate log files:
- When the log file reaches `max_size_mb`, it's rotated
- Up to `backup_count` backup files are kept
- Backup files are named: `server.log.1`, `server.log.2`, etc.

## Security Features

### Sensitive Data Redaction

The logging system automatically redacts sensitive information from tool arguments:
- Passwords
- Tokens
- Secrets
- API keys
- Authentication credentials

Example:
```python
logger.log_tool_invocation("authenticate", {
    "username": "user@example.com",
    "password": "secret123",
    "api_key": "abc123xyz"
})
# Output: "Tool invoked: authenticate with arguments: {'username': 'user@example.com', 'password': '***REDACTED***', 'api_key': '***REDACTED***'}"
```

## Performance Tracking

The logging system tracks and reports on God Mode performance targets:

### Scan Performance
- **Target**: <3000ms for first scan
- **Target**: <100ms for cached scan
- Automatically logged when targets are met or missed

### Cache Performance
- **Target**: >70% hit rate after initial scan
- Automatically logged when target is achieved

### Slow Operations
- **Threshold**: 1000ms (configurable via `slow_operation_threshold_ms`)
- Operations exceeding threshold are logged as warnings

## Best Practices

1. **Initialize Early**: Initialize logging at server startup before any operations
2. **Use Appropriate Levels**: 
   - DEBUG for detailed diagnostics
   - INFO for normal operations
   - WARNING for potential issues
   - ERROR for failures
3. **Log Tool Boundaries**: Always log tool invocations and completions
4. **Track Performance**: Use `log_tool_completion()` to track execution times
5. **Log Cache Stats**: Periodically log cache statistics to monitor performance
6. **Handle Errors Gracefully**: Always use `log_error()` with exception info

## Troubleshooting

### Log File Not Created

If the log file is not created:
1. Check that the directory exists (created automatically if possible)
2. Verify write permissions
3. Check for disk space
4. Review console output for warnings

### Missing Log Entries

If log entries are missing:
1. Check the log level configuration
2. Verify logger is initialized before use
3. Ensure proper exception handling

### Log File Too Large

If log files grow too large:
1. Reduce `max_size_mb` in configuration
2. Reduce `backup_count` to keep fewer backups
3. Consider increasing log level to reduce verbosity

## Example Integration

See `examples/logging_example.py` for a complete example of integrating the logging system with the MCP server configuration.

## API Reference

### MCPLogger Class

#### Methods

- `initialize(log_level, log_file, log_max_size_mb, log_backup_count, server_name, server_version)`: Initialize the logger
- `get_logger()`: Get the underlying Python logger instance
- `log_server_startup()`: Log server startup message
- `log_server_shutdown()`: Log server shutdown message
- `log_tool_invocation(tool_name, arguments)`: Log tool invocation
- `log_tool_completion(tool_name, duration_ms, slow_threshold_ms)`: Log tool completion
- `log_error(message, exc_info)`: Log error with optional stack trace
- `log_cache_stats(stats)`: Log cache statistics
- `log_god_mode_performance(operation, duration_ms, target_ms, achieved)`: Log God Mode performance
- `log_debug(message)`: Log debug message
- `log_info(message)`: Log info message
- `log_warning(message)`: Log warning message

### Module Functions

- `initialize_logging(...)`: Initialize the global logging system
- `get_logger()`: Get the global logger instance

## Requirements Coverage

This logging system satisfies all requirements from Requirement 10:

✅ 10.1: Initialize Python logging module with level from config (default "INFO")  
✅ 10.2: Set format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  
✅ 10.3: Add console handler (StreamHandler) and file handler (FileHandler to server.log)  
✅ 10.4: Log tool invocations at INFO  
✅ 10.5: Log tool completions at INFO  
✅ 10.6: Log slow operations at WARNING if duration > slow_operation_threshold_ms  
✅ 10.7: Log errors at ERROR level with full stack trace using logging.exception()  
✅ 10.8: Log cache statistics at INFO  
✅ 10.9: Log server startup at INFO  
✅ 10.10: Log server shutdown at INFO  
✅ 10.11: Log God Mode performance achievements when targets are met  
✅ 10.12: Support DEBUG level for detailed logging  
