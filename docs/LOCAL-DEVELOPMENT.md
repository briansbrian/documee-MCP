# Local Development Guide

## Overview

This guide covers setting up the MCP server for local development on Windows. The server implements the Model Context Protocol (MCP) to provide AI assistants with powerful codebase analysis capabilities.

## Prerequisites

- **Python 3.12** (required) - Specific version needed for async features and type hints
- **pip** - Python package manager
- **Node.js** (optional) - For MCP Inspector testing
- **Windows** - This guide is Windows-specific

## Quick Setup

See [SETUP.md](../SETUP.md) for detailed installation instructions.

```bash
# 1. Create virtual environment with Python 3.12
py -3.12 -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
python -m src.server
```

## Project Structure

```
Documee_mcp/
├── src/
│   ├── server.py              # MCP server entry point
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── cache/
│   │   └── unified_cache.py   # 3-tier caching system
│   ├── tools/
│   │   ├── scan_codebase.py   # Codebase scanner
│   │   ├── detect_frameworks.py  # Framework detector
│   │   └── discover_features.py  # Feature discoverer
│   ├── models/
│   │   └── schemas.py         # Data models
│   └── utils/
│       ├── path_utils.py      # Path sanitization
│       └── file_utils.py      # File operations
├── tests/                     # Unit tests
├── cache_db/                  # SQLite cache storage
├── config.yaml                # Server configuration
└── requirements.txt           # Python dependencies
```

## Configuration

### config.yaml

The server uses `config.yaml` for configuration:

```yaml
server:
  name: "codebase-to-course-mcp"
  version: "1.0.0"
  transport: "stdio"

cache:
  memory:
    max_size_mb: 500
  sqlite:
    enabled: true
    path: "cache_db/cache.db"
  redis:
    enabled: false
    url: null

analysis:
  max_file_size_mb: 10
  max_files_per_scan: 10000
  max_depth: 10

security:
  allowed_paths: []
  blocked_patterns:
    - "node_modules"
    - ".git"
    - "__pycache__"
    - "venv"

logging:
  level: "INFO"
  file: "server.log"
```

### Environment Variables

Override config.yaml settings:

```bash
# Windows CMD
set CACHE_MAX_SIZE_MB=1000
set MAX_FILE_SIZE_MB=20
set REDIS_URL=redis://localhost:6379

# Windows PowerShell
$env:CACHE_MAX_SIZE_MB="1000"
$env:MAX_FILE_SIZE_MB="20"
$env:REDIS_URL="redis://localhost:6379"
```

## Development Workflow

### 1. Make Changes

Edit files in `src/` directory:
- `src/tools/` - Tool implementations
- `src/cache/` - Caching logic
- `src/config/` - Configuration
- `src/models/` - Data structures

### 2. Test Locally

```bash
# Run with MCP Inspector
npx @modelcontextprotocol/inspector python -m src.server

# Or run directly
python -m src.server
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_cache.py
```

### 4. Check Diagnostics

Use Kiro's getDiagnostics or run:

```bash
# Type checking
mypy src/

# Linting
pylint src/
```

## Testing with MCP Inspector

The MCP Inspector is the official tool for testing MCP servers:

```bash
# Install (one-time)
npm install -g @modelcontextprotocol/inspector

# Run inspector
npx @modelcontextprotocol/inspector python -m src.server
```

### Inspector Features

1. **List Tools** - View all 3 discovery tools
2. **List Resources** - View codebase://structure and codebase://features
3. **List Prompts** - View analyze_codebase prompt
4. **Invoke Tools** - Test tool execution with parameters
5. **Read Resources** - Access cached data
6. **Get Prompts** - View prompt templates

### Example Tool Invocations

```json
// scan_codebase
{
  "path": "C:\\Users\\YourName\\project",
  "max_depth": 10,
  "use_cache": true
}

// detect_frameworks
{
  "codebase_id": "abc123def456",
  "confidence_threshold": 0.7,
  "use_cache": true
}

// discover_features
{
  "codebase_id": "abc123def456",
  "categories": ["routes", "api"],
  "use_cache": true
}
```

## Performance Targets

The server aims for "God Mode" performance:

| Metric | Target | Actual |
|--------|--------|--------|
| First scan (1000 files) | <3s | TBD |
| Cached scan | <0.1s | TBD |
| Framework detection | <3s | TBD |
| Feature discovery | <5s | TBD |
| Cache hit rate | >70% | TBD |
| Framework accuracy | 99% | TBD |

## Debugging

### Enable Debug Logging

```yaml
# config.yaml
logging:
  level: "DEBUG"
```

Or via environment:

```bash
set LOG_LEVEL=DEBUG
python -m src.server
```

### Common Issues

**Import errors:**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Cache errors:**
```bash
# Clear cache database
del cache_db\cache.db

# Restart server
python -m src.server
```

**Path issues:**
```python
# Use absolute paths in tool calls
"path": "C:\\Users\\YourName\\project"

# Or use forward slashes
"path": "C:/Users/YourName/project"
```

## Integration with AI Clients

### Kiro

Add to `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "documee": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "C:/path/to/Documee_mcp",
      "disabled": false,
      "autoApprove": ["scan_codebase", "detect_frameworks", "discover_features"]
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "documee": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "C:/path/to/Documee_mcp"
    }
  }
}
```

## Next Steps

1. **Complete Task 1** - Project structure is done
2. **Task 2** - Implement configuration management
3. **Task 3** - Create data models
4. **Task 4** - Implement utilities
5. **Task 5** - Build 3-tier cache system
6. **Tasks 6-8** - Implement the 3 discovery tools
7. **Tasks 9-12** - Build MCP server with FastMCP
8. **Task 13** - Test with MCP Inspector

See [tasks.md](../.kiro/specs/mcp-server-core-local-setup/tasks.md) for detailed implementation tasks.

## Resources

- [SETUP.md](../SETUP.md) - Installation guide
- [ULTIMATE-MCP-SERVER.md](ULTIMATE-MCP-SERVER.md) - Complete implementation
- [GOD-MODE-TOOLKIT.md](GOD-MODE-TOOLKIT.md) - Vision and capabilities
- [MCP Protocol Docs](https://modelcontextprotocol.io) - Official MCP documentation
- [FastMCP Docs](https://github.com/jlowin/fastmcp) - FastMCP framework

---

**Last Updated:** November 12, 2025
