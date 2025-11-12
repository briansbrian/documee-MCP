# Design Document

## Overview

This design document outlines the architecture and implementation approach for the MCP Server Core with local development setup. The system achieves "God Mode" performance through intelligent caching, parallel processing, and evidence-based validation.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AI Client                             │
│                  (Claude, GPT, Kiro)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ JSON-RPC 2.0 over stdio
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Core                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Tools      │  │  Resources   │  │   Prompts    │      │
│  │  (3 tools)   │  │ (2 resources)│  │  (1 prompt)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              UnifiedCacheManager (3-Tier)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Memory (LRU) │→ │    SQLite    │→ │Redis (opt.)  │      │
│  │   <0.001s    │  │    <0.1s     │  │   <0.2s      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    File System                               │
│         (Codebase, package.json, requirements.txt)           │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
src/
├── server.py                    # MCP Server entry point
├── tools/
│   ├── __init__.py
│   ├── scan_codebase.py        # Codebase scanning tool
│   ├── detect_frameworks.py    # Framework detection tool
│   └── discover_features.py    # Feature discovery tool
├── cache/
│   ├── __init__.py
│   └── unified_cache.py        # 3-tier cache manager
├── models/
│   ├── __init__.py
│   └── schemas.py              # Data models and schemas
├── utils/
│   ├── __init__.py
│   ├── file_utils.py           # File operations
│   └── path_utils.py           # Path sanitization
└── config/
    ├── __init__.py
    └── settings.py             # Configuration management
```

## Component Design

### 1. MCP Server Core (server.py)

**Responsibilities:**
- Initialize FastMCP server with stdio transport
- Register tools, resources, and prompts via decorators
- Handle JSON-RPC 2.0 communication automatically
- Manage UnifiedCacheManager lifecycle via lifespan
- Provide error handling and logging

**Key Implementation:**
```python
from fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

@dataclass
class AppContext:
    """Application context shared across all tools."""
    cache_manager: UnifiedCacheManager
    config: Settings

# Module-level variable to store app context
app_context: AppContext = None

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage server startup and shutdown lifecycle."""
    global app_context
    
    # Startup: initialize resources
    config = Settings()
    cache_manager = UnifiedCacheManager(
        max_memory_mb=config.cache_max_memory_mb,
        sqlite_path=config.sqlite_path,
        redis_url=config.redis_url
    )
    await cache_manager.initialize()
    
    app_context = AppContext(cache_manager=cache_manager, config=config)
    
    try:
        yield app_context
    finally:
        # Shutdown: cleanup resources
        await cache_manager.close()
        app_context = None

# Create FastMCP server with lifespan management
mcp = FastMCP("codebase-to-course-mcp", lifespan=app_lifespan)

# Tool registration using decorators (no parentheses)
@mcp.tool
async def scan_codebase(
    path: str,
    max_depth: int = 10,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """Scan codebase structure, languages, and frameworks."""
    # Access app context from module-level variable
    cache_manager = app_context.cache_manager
    # Implementation
    return result  # FastMCP handles serialization

@mcp.resource("codebase://structure")
async def get_structure(ctx: Context = None) -> dict:
    """Get cached codebase structure."""
    # Access app context from module-level variable
    cache_manager = app_context.cache_manager
    structure = await cache_manager.get_resource("structure")
    return structure  # FastMCP handles JSON serialization

@mcp.prompt
async def analyze_codebase(codebase_path: str) -> str:
    """Generate a codebase analysis prompt."""
    return f"""Please analyze the codebase at: {codebase_path}

Steps:
1. Call scan_codebase to get structure
2. Call detect_frameworks to identify tech stack
3. Call discover_features to find teachable code
4. Focus on finding code that teaches well"""

if __name__ == "__main__":
    # Run with stdio transport (default)
    mcp.run()
```

**Server Capabilities:**
FastMCP automatically declares capabilities based on registered components:
```python
{
    "capabilities": {
        "tools": {
            "listChanged": True  # Supports tool list change notifications
        },
        "resources": {
            "subscribe": False,  # Not supporting subscriptions in v1
            "listChanged": True  # Supports resource list change notifications
        },
        "prompts": {
            "listChanged": True  # Supports prompt list change notifications
        }
    }
}
```

### 2. UnifiedCacheManager (cache/unified_cache.py)

**Responsibilities:**
- Manage 3-tier cache (Memory → SQLite → Redis)
- Implement LRU eviction for memory tier
- Provide cache promotion between tiers
- Track cache statistics and hit rates
- Manage session state
- Support async context manager protocol

**Key Classes:**
```python
class UnifiedCacheManager:
    def __init__(self, max_memory_mb: int, sqlite_path: str, redis_url: str = None):
        self.memory_cache = {}  # LRU dict
        self.current_memory_size = 0
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.sqlite_conn = None  # aiosqlite connection
        self.redis_client = None  # Optional redis client
        self.stats = {...}
        self._initialized = False
    
    async def initialize(self):
        """Initialize cache connections and create tables."""
        if self._initialized:
            return
        
        # Initialize SQLite
        self.sqlite_conn = await aiosqlite.connect(self.sqlite_path)
        await self._create_tables()
        
        # Initialize Redis if URL provided
        if self.redis_url:
            self.redis_client = await aioredis.from_url(self.redis_url)
        
        self._initialized = True
    
    async def close(self):
        """Close all cache connections."""
        if self.sqlite_conn:
            await self.sqlite_conn.close()
        if self.redis_client:
            await self.redis_client.close()
        self._initialized = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def get_analysis(self, key: str) -> Optional[dict]:
        # Check memory → SQLite → Redis
        
    async def set_analysis(self, key: str, data: dict, ttl: int):
        # Store in all tiers
        
    async def get_session(self, codebase_id: str) -> Optional[dict]:
        # Retrieve session state
        
    async def set_session(self, codebase_id: str, state: dict):
        # Store session state
        
    async def get_stats(self) -> dict:
        # Return cache statistics
```

**Cache Key Strategy:**
- Scan results: `scan:{codebase_id}`
- Framework detection: `frameworks:{codebase_id}`
- Feature discovery: `features:{codebase_id}`
- File content: `file:{file_hash}`

**SQLite Schema:**
```sql
CREATE TABLE file_cache (
    path TEXT PRIMARY KEY,
    content TEXT,
    hash TEXT,
    language TEXT,
    size INTEGER,
    cached_at TIMESTAMP
);

CREATE TABLE analysis_cache (
    key TEXT PRIMARY KEY,
    data TEXT,  -- JSON
    cached_at TIMESTAMP,
    ttl INTEGER
);

CREATE TABLE session_state (
    codebase_id TEXT PRIMARY KEY,
    state TEXT,  -- JSON
    updated_at TIMESTAMP
);
```

### 3. Codebase Scanner (tools/scan_codebase.py)

**Responsibilities:**
- Traverse directory tree with max_depth limit
- Count files by language and type
- Calculate total size and file counts
- Generate unique codebase_id
- Skip ignored directories (node_modules, .git, etc.)
- Cache results for 1 hour

**Tool Registration (in server.py):**
```python
@mcp.tool
async def scan_codebase(
    path: str,
    max_depth: int = 10,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Scan codebase structure, languages, and frameworks.
    
    Args:
        path: Directory path to scan
        max_depth: Maximum directory depth (default: 10)
        use_cache: Use cached results if available (default: True)
    
    Returns:
        Dictionary with codebase_id, structure, summary, scan_time_ms, from_cache
    """
    # Access app context from module-level variable
    cache_manager = app_context.cache_manager
    
    # Generate codebase_id from path
    codebase_id = generate_codebase_id(path)
    
    # Check cache
    if use_cache:
        cached = await cache_manager.get_analysis(f"scan:{codebase_id}")
        if cached:
            return {**cached, "from_cache": True}
    
    # Perform scan
    start_time = time.time()
    structure = await _scan_directory(path, max_depth)
    scan_time_ms = (time.time() - start_time) * 1000
    
    # Generate summary
    summary = _generate_summary(structure)
    
    result = {
        "codebase_id": codebase_id,
        "structure": structure,
        "summary": summary,
        "scan_time_ms": scan_time_ms,
        "from_cache": False
    }
    
    # Cache result
    await cache_manager.set_analysis(f"scan:{codebase_id}", result, ttl=3600)
    await cache_manager.set_resource("structure", result)
    await cache_manager.set_session(codebase_id, {"phase": "scanned", "timestamp": time.time()})
    
    return result  # FastMCP handles serialization automatically
```

**Note:** FastMCP automatically handles:
- JSON Schema generation from type hints
- Input validation
- Error handling and conversion to proper error responses
- Structured content serialization

**Language Detection:**
```python
LANGUAGE_EXTENSIONS = {
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".py": "Python",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C++",
}
```

**Ignore Patterns:**
```python
IGNORE_PATTERNS = {
    "node_modules", ".git", "dist", "build", ".next",
    "__pycache__", "venv", "env", ".venv", "target",
    "out", "coverage", ".pytest_cache"
}
```

### 4. Framework Detector (tools/detect_frameworks.py)

**Responsibilities:**
- Read package.json for JavaScript/TypeScript projects
- Read requirements.txt for Python projects
- Assign confidence scores (0.99 for package.json, 0.95 for requirements.txt)
- Provide evidence for each detection
- Filter by confidence threshold
- Cache results for 1 hour

**Tool Registration (in server.py):**
```python
@mcp.tool
async def detect_frameworks(
    codebase_id: str,
    confidence_threshold: float = 0.7,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Detect frameworks and libraries with confidence scores.
    
    Args:
        codebase_id: Unique identifier from scan_codebase
        confidence_threshold: Minimum confidence score (0.0-1.0, default: 0.7)
        use_cache: Use cached results if available (default: True)
    
    Returns:
        Dictionary with frameworks array, total_detected, confidence_threshold, from_cache
    """
    # Access app context from module-level variable
    cache_manager = app_context.cache_manager
    
    # Check cache
    if use_cache:
        cached = await cache_manager.get_analysis(f"frameworks:{codebase_id}")
        if cached:
            return {**cached, "from_cache": True}
    
    # Get scan result
    scan_result = await cache_manager.get_analysis(f"scan:{codebase_id}")
    if not scan_result:
        raise ValueError("Codebase not scanned. Call scan_codebase first.")
    
    # Detect frameworks
    frameworks = []
    
    # JavaScript/TypeScript detection
    if "JavaScript" in scan_result["structure"]["languages"] or "TypeScript" in scan_result["structure"]["languages"]:
        js_frameworks = await _detect_js_frameworks(scan_result["path"])
        frameworks.extend(js_frameworks)
    
    # Python detection
    if "Python" in scan_result["structure"]["languages"]:
        py_frameworks = await _detect_python_frameworks(scan_result["path"])
        frameworks.extend(py_frameworks)
    
    # Filter by confidence
    frameworks = [f for f in frameworks if f["confidence"] >= confidence_threshold]
    
    # Sort by confidence
    frameworks.sort(key=lambda x: x["confidence"], reverse=True)
    
    result = {
        "frameworks": frameworks,
        "total_detected": len(frameworks),
        "confidence_threshold": confidence_threshold,
        "from_cache": False
    }
    
    # Cache result
    await cache_manager.set_analysis(f"frameworks:{codebase_id}", result, ttl=3600)
    
    return result  # FastMCP handles serialization automatically
```

**Framework Detection Logic:**
```python
JS_FRAMEWORKS = {
    "react": {"name": "React", "confidence": 0.99},
    "next": {"name": "Next.js", "confidence": 0.99},
    "express": {"name": "Express", "confidence": 0.99},
    "vue": {"name": "Vue", "confidence": 0.99},
    "@angular/core": {"name": "Angular", "confidence": 0.99},
    "@nestjs/core": {"name": "NestJS", "confidence": 0.99},
}

PYTHON_FRAMEWORKS = {
    "django": {"name": "Django", "confidence": 0.95},
    "flask": {"name": "Flask", "confidence": 0.95},
    "fastapi": {"name": "FastAPI", "confidence": 0.95},
    "pytest": {"name": "Pytest", "confidence": 0.95},
}
```

### 5. Feature Discoverer (tools/discover_features.py)

**Responsibilities:**
- Search for feature directories (routes, components, api, utils, hooks)
- Generate unique feature IDs
- Assign priorities (high for routes/api, medium for others)
- Filter by categories
- Cache results for 1 hour

**Tool Registration (in server.py):**
```python
@mcp.tool
async def discover_features(
    codebase_id: str,
    categories: list[str] = None,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Discover features like routes, components, API endpoints, utilities, and hooks.
    
    Args:
        codebase_id: Unique identifier from scan_codebase
        categories: List of categories to discover (default: ["all"])
        use_cache: Use cached results if available (default: True)
    
    Returns:
        Dictionary with features array, total_features, categories, from_cache
    """
    if categories is None:
        categories = ["all"]
    
    # Access app context from module-level variable
    cache_manager = app_context.cache_manager
    
    # Check cache
    if use_cache:
        cached = await cache_manager.get_analysis(f"features:{codebase_id}")
        if cached:
            filtered = _filter_by_categories(cached["features"], categories)
            return {**cached, "features": filtered, "from_cache": True}
    
    # Get scan result
    scan_result = await cache_manager.get_analysis(f"scan:{codebase_id}")
    if not scan_result:
        raise ValueError("Codebase not scanned. Call scan_codebase first.")
    
    # Discover features
    features = []
    codebase_path = scan_result["path"]
    
    # Search for feature directories
    for category, patterns in FEATURE_PATTERNS.items():
        if categories != ["all"] and category not in categories:
            continue
            
        for pattern in patterns:
            matches = await _find_directories(codebase_path, pattern)
            for match in matches:
                feature = {
                    "id": generate_feature_id(match),
                    "name": os.path.basename(match),
                    "category": category,
                    "path": match,
                    "priority": "high" if category in ["routes", "api"] else "medium"
                }
                features.append(feature)
    
    result = {
        "features": features,
        "total_features": len(features),
        "categories": list(set(f["category"] for f in features)),
        "from_cache": False
    }
    
    # Cache result
    await cache_manager.set_analysis(f"features:{codebase_id}", result, ttl=3600)
    await cache_manager.set_resource("features", result)
    
    return result  # FastMCP handles serialization automatically
```

**Feature Patterns:**
```python
FEATURE_PATTERNS = {
    "routes": ["routes/", "pages/", "app/"],
    "components": ["components/", "widgets/"],
    "api": ["api/", "endpoints/", "controllers/"],
    "utils": ["utils/", "helpers/", "lib/"],
    "hooks": ["hooks/", "composables/"]
}
```

### 6. Configuration Management (config/settings.py)

**Responsibilities:**
- Load settings from config.yaml
- Override with environment variables
- Provide default values
- Validate configuration
- Expose settings to components

**Key Classes:**
```python
class Settings:
    def __init__(self):
        self.config = self._load_config()
        self._apply_env_overrides()
        self._validate()
    
    def _load_config(self) -> dict:
        # Load from config.yaml or use defaults
        
    def _apply_env_overrides(self):
        # Override with environment variables
        
    def _validate(self):
        # Validate configuration values
        
    @property
    def cache_max_memory_mb(self) -> int:
        return self.config.get("cache", {}).get("memory", {}).get("max_size_mb", 500)
```

**Default Configuration:**
```yaml
server:
  name: codebase-to-course-mcp
  version: 1.0.0
  transport: stdio

cache:
  memory:
    max_size_mb: 500
  sqlite:
    enabled: true
    path: cache_db/cache.db
  redis:
    enabled: false
    url: null

analysis:
  max_file_size_mb: 10
  max_files_per_scan: 10000
  max_parallel_reads: 10
  scan_timeout_seconds: 30

security:
  allowed_paths: []
  max_depth: 10
  blocked_patterns: ["node_modules", ".git"]

performance:
  enable_profiling: false
  log_slow_operations: true
  slow_operation_threshold_ms: 1000

logging:
  level: INFO
  file: server.log
  max_size_mb: 10
  backup_count: 3
```

## Data Models

### Scan Result
```python
@dataclass
class ScanResult:
    codebase_id: str
    structure: dict  # {total_files, total_directories, total_size_mb, languages, file_types}
    summary: dict    # {primary_language, project_type, has_tests, size_category}
    scan_time_ms: float
    from_cache: bool
```

### Framework Detection Result
```python
@dataclass
class Framework:
    name: str
    version: str
    confidence: float
    evidence: List[str]

@dataclass
class FrameworkDetectionResult:
    frameworks: List[Framework]
    total_detected: int
    confidence_threshold: float
    from_cache: bool
```

### Feature Discovery Result
```python
@dataclass
class Feature:
    id: str
    name: str
    category: str
    path: str
    priority: str

@dataclass
class FeatureDiscoveryResult:
    features: List[Feature]
    total_features: int
    categories: List[str]
    from_cache: bool
```

## Performance Optimization Strategies

### 1. Caching Strategy
- **Memory Tier**: LRU cache with 500MB limit, <0.001s access
- **SQLite Tier**: Persistent cache, <0.1s access
- **Redis Tier**: Optional distributed cache, <0.2s access
- **Cache Promotion**: Move frequently accessed data to faster tiers
- **TTL**: 1 hour for analysis results, 24 hours for file content

### 2. Parallel Processing
- Use `asyncio.gather()` for concurrent file reads
- Limit concurrent operations to avoid resource exhaustion
- Use `aiofiles` for non-blocking file I/O

### 3. Progressive Discovery
- Scan structure first (lightweight)
- Detect frameworks second (medium weight)
- Discover features third (medium weight)
- Read files last (heavyweight, on-demand)

### 4. Smart Filtering
- Skip ignored directories early in traversal
- Filter by file size before reading
- Use glob patterns for efficient file matching

## Security Considerations

### 1. Path Sanitization
```python
def sanitize_path(path: str) -> str:
    # Remove directory traversal attempts
    path = path.replace("..", "").replace("~", "")
    # Convert to absolute path
    path = os.path.abspath(path)
    # Validate against allowed paths
    if not _is_allowed_path(path):
        raise ValueError(f"Access denied: {path}")
    return path
```

### 2. File Size Limits
- Max file size: 10MB (configurable)
- Max files per scan: 10,000 (configurable)
- Timeout: 30 seconds per operation

### 3. Input Validation
- Validate all tool parameters against JSON Schema
- Sanitize user-provided paths
- Limit recursion depth to prevent stack overflow

## Error Handling Strategy

### 1. Tool-Level Errors
```python
try:
    result = await execute_tool(name, arguments)
    return TextContent(type="text", text=json.dumps(result))
except ValueError as e:
    return TextContent(type="text", text=json.dumps({
        "error": str(e),
        "tool": name,
        "arguments": arguments,
        "type": "ValidationError"
    }))
except Exception as e:
    logger.exception(f"Tool execution failed: {name}")
    return TextContent(type="text", text=json.dumps({
        "error": str(e),
        "tool": name,
        "arguments": arguments,
        "type": type(e).__name__
    }))
```

### 2. Graceful Degradation
- Skip unreadable files instead of failing entire scan
- Continue framework detection even if package.json is malformed
- Return partial results when possible

### 3. Logging
- Log all errors with full stack traces
- Log slow operations for performance monitoring
- Log cache statistics for optimization

## Testing Strategy

### 1. Unit Tests
- Test each tool independently
- Test cache manager with mock data
- Test path sanitization and validation
- Test error handling paths

### 2. Integration Tests
- Test complete workflows (scan → detect → discover)
- Test cache promotion between tiers
- Test MCP protocol communication
- Test lifespan management (startup/shutdown)

### 3. Performance Tests
- Benchmark scan_codebase on 1000-file codebase (<3s target)
- Benchmark cache hit performance (<0.1s target)
- Benchmark parallel file reading (10x speedup target)

### 4. MCP Inspector Testing
- Validate all tools are registered correctly
- Test tool invocation with valid/invalid parameters
- Test resource access
- Test prompt templates

**Testing Commands:**
```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python -m src.server

# Development mode with auto-reload
uv run mcp dev src/server.py
```

## Deployment Considerations

### Local Development
- Use Python 3.12 virtual environment (venv)
- Install dependencies from requirements.txt
- Run server with `python -m src.server` or `uv run mcp dev src/server.py`
- Test with MCP Inspector: `npx @modelcontextprotocol/inspector python -m src.server`

**Development Workflow:**
```bash
# Setup with Python 3.12
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Development with auto-reload
uv run mcp dev src/server.py

# Testing
pytest tests/

# Production run
python -m src.server
```

### Future Azure Deployment (Out of Scope for Spec 1)
- Package as Docker container
- Deploy to Azure Container Instances
- Use Azure Redis Cache for distributed caching
- Configure Azure Application Insights for monitoring

## Success Metrics

### Performance Targets
- Scan 1000 files in <3 seconds (first run)
- Cached scan in <0.1 seconds
- Complete workflow in <15 seconds
- Cache hit rate >70% after initial scan
- Parallel file reading 10x faster than sequential

### Accuracy Targets
- Framework detection: 99% confidence for package.json dependencies
- Framework detection: 95% confidence for requirements.txt dependencies
- Zero hallucinations (all claims backed by evidence)

### Reliability Targets
- Graceful error handling for all failure modes
- No crashes on malformed input files
- Successful recovery from cache corruption
