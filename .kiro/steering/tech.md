# Technology Stack

## Core Framework

**FastMCP 0.5.0+** - Simplified MCP server implementation
- Decorator-based tool registration (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`)
- Automatic JSON Schema generation from type hints
- Lifespan management for startup/shutdown
- JSON-RPC 2.0 over stdio transport

## Language & Runtime

**Python 3.12+** (required)
- Modern type hints and dataclasses
- Async/await for concurrent operations
- Pattern matching and structural pattern matching

## Key Dependencies

**Analysis**
- `tree-sitter==0.21.3` - Multi-language AST parsing
- `tree-sitter-languages==1.10.2` - Language grammar support
- `nbformat>=5.9.0` - Jupyter notebook support

**Async I/O**
- `aiofiles>=23.2.1` - Async file operations
- `aiosqlite>=0.19.0` - Async SQLite database

**Configuration & Templates**
- `pyyaml>=6.0.1` - YAML config parsing
- `python-dotenv>=1.0.0` - Environment variables
- `jinja2>=3.1.2` - Template engine for course generation

**Testing**
- `pytest>=7.4.3` - Test framework
- `pytest-asyncio>=0.21.1` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting

## Architecture

**3-Tier Caching**
1. Memory (LRU) - <0.001s, 500MB default
2. SQLite - <0.1s, persistent storage at `cache_db/cache.db`
3. Redis (optional) - <0.2s, distributed caching

**Module Structure**
- `src/server.py` - FastMCP server entry point with tool definitions
- `src/tools/` - MCP tool implementations (scan, detect, discover)
- `src/analysis/` - Analysis engine (AST, symbols, patterns, dependencies)
- `src/course/` - Course generation (structure, content, exercises, exporters)
- `src/cache/` - Unified cache manager
- `src/models/` - Dataclass models for all data structures
- `src/config/` - Configuration management
- `src/utils/` - Utility functions (file ops, path sanitization)

## Common Commands

**Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Testing**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_cache.py -v

# Quick integration test
python test_mcp_local.py
```

**Development**
```bash
# Interactive testing with MCP Inspector
npx @modelcontextprotocol/inspector python -m src.server

# Check for issues
pytest tests/ -v

# View logs
tail -f server.log
```

**Important Notes**
- Never run `python -m src.server` directly - it waits for JSON-RPC messages
- Use MCP Inspector or integration tests for manual testing
- Server is started automatically by MCP clients (Kiro, Claude Desktop)
- Configuration in `config.yaml` or environment variables
- Cache database at `cache_db/cache.db` (can be deleted to clear cache)

## Build System

No build step required - pure Python runtime. Virtual environment isolation recommended for dependency management.
