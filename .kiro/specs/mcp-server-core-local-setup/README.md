# MCP Server Core - Local Setup Specification

## Overview

This specification defines the implementation of a Model Context Protocol (MCP) server that achieves "God Mode" performance for codebase analysis. The system delivers 20x faster analysis (2-3 seconds vs 30-100 seconds), 99% accuracy, and 0% hallucination rate through intelligent caching, parallel processing, and evidence-based validation.

## Specification Documents

### 1. [Requirements](./requirements.md)
Comprehensive requirements document with 15 detailed requirements covering:
- Local development environment setup
- MCP server core implementation
- 3 discovery tools (scan, detect, discover)
- 3-tier caching system (Memory → SQLite → Redis)
- Error handling and security
- Configuration management
- Logging and diagnostics
- Performance benchmarking

### 2. [Design](./design.md)
Detailed design document including:
- High-level architecture diagrams
- Component architecture and responsibilities
- Data models and schemas
- Performance optimization strategies
- Security considerations
- Error handling strategy
- Testing strategy

### 3. [Tasks](./tasks.md)
Implementation task breakdown with:
- 18 tasks organized into 6 phases
- Estimated time: 18.5 hours total
- Priority levels (High/Medium/Low)
- Dependencies and critical path
- Acceptance criteria for each task

## Key Features

### Tools (3)
1. **scan_codebase** - Scan directory structure, languages, and file types
2. **detect_frameworks** - Identify frameworks with confidence scores
3. **discover_features** - Find routes, components, API endpoints, utilities, hooks

### Resources (2)
1. **codebase://structure** - Cached codebase structure data
2. **codebase://features** - Cached discovered features data

### Prompts (1)
1. **analyze_codebase** - Step-by-step analysis workflow template

## Performance Targets (God Mode)

| Metric | Target | Baseline | Improvement |
|--------|--------|----------|-------------|
| Initial Scan (1000 files) | <3 seconds | 30-100 seconds | 20x faster |
| Cached Scan | <0.1 seconds | 45 seconds | 450x faster |
| Complete Workflow | <15 seconds | 100+ seconds | 7x faster |
| Framework Detection Accuracy | 99% | 70-80% | 25% improvement |
| Cache Hit Rate | >70% | 0% | N/A |
| Hallucination Rate | 0% | 10-20% | 100% reduction |

## Technology Stack

### Core Dependencies
- **Python 3.11+** - Runtime environment
- **mcp>=1.0.0** - Model Context Protocol SDK (includes FastMCP)
- **aiofiles>=23.2.1** - Async file I/O
- **aiosqlite>=0.19.0** - Async SQLite operations
- **pyyaml>=6.0.1** - Configuration management

### Development Dependencies
- **pytest>=7.4.3** - Testing framework
- **pytest-asyncio>=0.21.1** - Async test support
- **pytest-cov>=4.1.0** - Code coverage

### Optional Dependencies
- **redis>=5.0.0** - Distributed caching (Tier 3)

### Key Features of FastMCP
- ✅ Decorator-based tool/resource/prompt registration
- ✅ Automatic JSON Schema generation from type hints
- ✅ Built-in input validation
- ✅ Automatic error handling
- ✅ Structured content support (no JSON string serialization)
- ✅ Lifespan management for resource initialization/cleanup
- ✅ Development mode with auto-reload (`uv run mcp dev`)

## Project Structure

```
.
├── src/
│   ├── server.py                 # MCP server entry point
│   ├── tools/
│   │   ├── scan_codebase.py     # Codebase scanning tool
│   │   ├── detect_frameworks.py # Framework detection tool
│   │   └── discover_features.py # Feature discovery tool
│   ├── cache/
│   │   └── unified_cache.py     # 3-tier cache manager
│   ├── models/
│   │   └── schemas.py           # Data models
│   ├── utils/
│   │   ├── file_utils.py        # File operations
│   │   └── path_utils.py        # Path sanitization
│   └── config/
│       └── settings.py          # Configuration management
├── tests/
│   ├── test_cache.py
│   ├── test_scan_codebase.py
│   ├── test_detect_frameworks.py
│   └── test_discover_features.py
├── cache_db/
│   └── cache.db                 # SQLite cache database
├── examples/
│   ├── basic_usage.py
│   └── kiro_config.json
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Server
```bash
# Development mode with auto-reload (recommended)
uv run mcp dev src/server.py

# Production mode
python -m src.server
```

### 3. Test with MCP Inspector
```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Run with inspector
npx @modelcontextprotocol/inspector python -m src.server
```

### 4. Integrate with Kiro
Add to `.kiro/settings/mcp.json`:
```json
{
  "mcpServers": {
    "codebase-analyzer": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-server",
      "disabled": false
    }
  }
}
```

## Implementation Phases

### Phase 1: Project Setup (40 minutes)
- Create project structure
- Setup virtual environment
- Install dependencies
- Create configuration

### Phase 2: Core Infrastructure (3.5 hours)
- Implement UnifiedCacheManager with lifecycle methods
- Implement utility functions
- Define data models

### Phase 3: Tool Implementation (5 hours)
- Implement codebase scanner
- Implement framework detector
- Implement feature discoverer

### Phase 4: MCP Server (3 hours) ⚡ **Simplified with FastMCP**
- Implement FastMCP server with lifespan management
- Register tools, resources, and prompts via decorators
- Automatic error handling and validation

### Phase 5: Testing (5 hours)
- Write unit tests
- Test with MCP Inspector
- Performance benchmarking

### Phase 6: Documentation (1 hour)
- Create examples
- Write README

**Total Time: 18 hours** (reduced from 18.5 hours thanks to FastMCP simplifications)

## Success Criteria

### Functional Requirements
- ✅ All 3 tools work correctly
- ✅ All 2 resources accessible
- ✅ 1 prompt template available
- ✅ MCP Inspector tests pass
- ✅ Error handling works gracefully

### Performance Requirements
- ✅ Scan 1000 files in <3 seconds (first run)
- ✅ Cached scan in <0.1 seconds
- ✅ Complete workflow in <15 seconds
- ✅ Cache hit rate >70%
- ✅ Framework detection 99% confidence

### Quality Requirements
- ✅ Unit test coverage >80%
- ✅ All tests pass
- ✅ No crashes on invalid input
- ✅ Comprehensive error messages
- ✅ Security validation (path sanitization)

## Key Implementation Details

### FastMCP Server Pattern
```python
from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    # Startup: initialize cache
    cache_manager = UnifiedCacheManager(...)
    await cache_manager.initialize()
    try:
        yield {"cache_manager": cache_manager}
    finally:
        # Shutdown: cleanup
        await cache_manager.close()

mcp = FastMCP("codebase-to-course-mcp", lifespan=app_lifespan)

@mcp.tool()
async def scan_codebase(path: str, ctx: Context = None) -> dict:
    cache_manager = ctx.request_context.lifespan_context.cache_manager
    # Implementation
    return result

if __name__ == "__main__":
    mcp.run()  # Defaults to stdio transport
```

### Benefits Over Low-Level Server
- **Less Code:** ~40% reduction in boilerplate
- **Type Safety:** Automatic schema generation from type hints
- **Error Handling:** Exceptions automatically converted to proper error responses
- **Validation:** Input validation handled automatically
- **Lifecycle:** Built-in resource management with lifespan

## Future Enhancements (Out of Scope)

The following features will be implemented in subsequent specs:

### Spec 2: Advanced Analysis Tools
- Parallel file reader (10x speedup)
- Code analyzer with AST parsing
- Teaching value scorer
- Evidence-based validation

### Spec 3: Course Generation
- Course outline generator
- Lesson planner
- Content generator
- Export to multiple formats

### Spec 4: Azure Deployment
- Docker containerization
- Azure Container Instances deployment
- Azure Redis Cache integration
- Azure Application Insights monitoring

## References

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Anthropic MCP SDK](https://github.com/anthropics/anthropic-sdk-python)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [God Mode Toolkit](../../docs/GOD-MODE-TOOLKIT.md)
- [Ultimate MCP Server](../../docs/ULTIMATE-MCP-SERVER.md)

## Support

For questions or issues:
1. Check the [Requirements](./requirements.md) for detailed specifications
2. Review the [Design](./design.md) for architecture details
3. Follow the [Tasks](./tasks.md) for implementation guidance
4. Refer to project documentation in `/docs`

## License

[Your License Here]

## Version

**Spec Version:** 1.0.0  
**Last Updated:** November 12, 2025  
**Status:** Ready for Implementation
