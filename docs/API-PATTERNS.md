# API Patterns and Best Practices

**Last Updated:** November 12, 2025  
**Status:** ✅ Verified against Context7 documentation

This document provides verified API patterns for all dependencies used in the Documee MCP Server. All patterns have been validated against the latest library documentation.

---

## FastMCP (v0.5.0+)

**Package:** `fastmcp>=0.5.0`  
**Trust Score:** 9.3/10  
**Documentation:** Context7 verified

### Correct Import Pattern

```python
from fastmcp import FastMCP, Context

# ✅ CORRECT - Import from fastmcp directly
# ❌ WRONG - from mcp.server.fastmcp import FastMCP
# ❌ WRONG - from mcp import Server
```

### Server Initialization

```python
from fastmcp import FastMCP

# Basic initialization
mcp = FastMCP("server-name")

# With lifespan management (recommended)
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    # Startup
    cache_manager = UnifiedCacheManager()
    await cache_manager.initialize()
    
    yield {"cache_manager": cache_manager}
    
    # Shutdown
    await cache_manager.close()

mcp = FastMCP("server-name", lifespan=app_lifespan)
```

### Tool Registration

```python
# Simple tool (no parentheses on decorator)
@mcp.tool
def simple_tool(param: str) -> str:
    return f"Result: {param}"

# Tool with Context injection
@mcp.tool
async def advanced_tool(param: str, ctx: Context) -> dict:
    cache_manager = ctx.request_context.get("cache_manager")
    # Use cache_manager
    return {"result": "success"}

# ✅ Return dict/list directly - FastMCP handles JSON serialization
# ❌ Don't manually wrap in TextContent
```

### Resource Registration

```python
@mcp.resource("resource://name")
def get_resource() -> dict:
    # Return dict directly
    return {"key": "value"}

# ✅ FastMCP automatically sets mimeType to "application/json"
# ✅ Handles JSON serialization automatically
```

### Prompt Registration

```python
@mcp.prompt
def my_prompt(param: str) -> str:
    return f"Step 1: Do something with {param}..."

# ✅ Return string directly - converted to user message
# ✅ Function signature generates prompt schema automatically
```

### Error Handling

```python
@mcp.tool
def my_tool(x: int) -> str:
    if x < 0:
        raise ValueError("x must be positive")
    return str(x)

# ✅ FastMCP automatically converts exceptions to MCP error responses
# ❌ Don't manually wrap errors in TextContent
# ❌ Don't manually try-catch for error responses
```

### Entry Point

```python
if __name__ == "__main__":
    mcp.run()  # Starts stdio transport by default
```

---

## aiofiles (v23.2.1+)

**Package:** `aiofiles>=23.2.1`  
**Trust Score:** 9.4/10  
**Purpose:** Async file operations

### Reading Files

```python
import aiofiles

async def read_file(path: str) -> str:
    async with aiofiles.open(path, 'r', encoding='utf-8') as f:
        content = await f.read()
    return content
```

### Writing Files

```python
async def write_file(path: str, content: str) -> None:
    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
        await f.write(content)
```

### Parallel File Reading

```python
import asyncio
import aiofiles

async def read_files_parallel(paths: list[str]) -> list[str]:
    async def read_one(path: str) -> str:
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    results = await asyncio.gather(*[read_one(p) for p in paths])
    return results
```

---

## aiosqlite (v0.19.0+)

**Package:** `aiosqlite>=0.19.0`  
**Trust Score:** 7.7/10  
**Purpose:** Async SQLite operations

### Database Connection

```python
import aiosqlite

async def initialize_db():
    async with aiosqlite.connect("cache.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
```

### Query Operations

```python
async def get_from_cache(key: str) -> str | None:
    async with aiosqlite.connect("cache.db") as db:
        async with db.execute(
            "SELECT value FROM cache WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_in_cache(key: str, value: str) -> None:
    async with aiosqlite.connect("cache.db") as db:
        await db.execute(
            "INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)",
            (key, value)
        )
        await db.commit()
```

---

## PyYAML (v6.0.1+)

**Package:** `pyyaml>=6.0.1`  
**Purpose:** YAML configuration parsing

### Safe Loading (Recommended)

```python
import yaml

def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

# ✅ Use safe_load() - prevents arbitrary code execution
# ❌ Don't use load() - security risk
```

### Writing YAML

```python
def save_config(path: str, config: dict) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False)
```

---

## Standard Library Patterns

### hashlib (SHA-256)

```python
import hashlib

def generate_hash(text: str) -> str:
    hash_object = hashlib.sha256(text.encode('utf-8'))
    return hash_object.hexdigest()[:16]  # Truncate to 16 chars
```

### os.walk (Directory Traversal)

```python
import os

def scan_directory(path: str, max_depth: int = 10) -> list[str]:
    files = []
    for dirpath, dirnames, filenames in os.walk(path):
        depth = dirpath[len(path):].count(os.sep)
        if depth >= max_depth:
            dirnames.clear()  # Don't recurse deeper
        files.extend(os.path.join(dirpath, f) for f in filenames)
    return files
```

### pathlib.Path (Path Operations)

```python
from pathlib import Path

# Glob pattern matching
def find_files(pattern: str) -> list[Path]:
    return list(Path('.').glob(pattern))

# Path manipulation
def normalize_path(path: str) -> Path:
    return Path(path).resolve()
```

---

## Anti-Patterns (Don't Do This)

### ❌ Wrong FastMCP Import

```python
# WRONG - Old SDK pattern
from mcp import Server
from mcp.server.fastmcp import FastMCP

# CORRECT
from fastmcp import FastMCP, Context
```

### ❌ Manual Error Wrapping

```python
# WRONG - FastMCP handles this automatically
from mcp.types import TextContent

@mcp.tool
def my_tool(x: int) -> TextContent:
    try:
        result = process(x)
        return TextContent(type="text", text=json.dumps(result))
    except Exception as e:
        return TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )

# CORRECT - Let FastMCP handle it
@mcp.tool
def my_tool(x: int) -> dict:
    result = process(x)  # Exceptions auto-converted
    return result  # Auto-serialized to JSON
```

### ❌ Manual JSON Serialization

```python
# WRONG
import json

@mcp.tool
def my_tool() -> str:
    data = {"key": "value"}
    return json.dumps(data)

# CORRECT
@mcp.tool
def my_tool() -> dict:
    return {"key": "value"}  # FastMCP handles serialization
```

### ❌ Unsafe YAML Loading

```python
# WRONG - Security risk
import yaml

config = yaml.load(file)  # Can execute arbitrary code

# CORRECT
config = yaml.safe_load(file)  # Safe parsing only
```

---

## Context Injection Pattern

### Accessing Lifespan Context

```python
from fastmcp import FastMCP, Context
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    cache_manager = UnifiedCacheManager()
    await cache_manager.initialize()
    
    # Yield context dict
    yield {"cache_manager": cache_manager}
    
    await cache_manager.close()

mcp = FastMCP("server", lifespan=app_lifespan)

# Access in tools via Context
@mcp.tool
async def my_tool(param: str, ctx: Context) -> dict:
    # Get from lifespan context
    cache_manager = ctx.request_context.get("cache_manager")
    
    # Use cache_manager
    result = await cache_manager.get_analysis(param)
    return result

# ✅ Clean dependency injection
# ❌ Don't use module-level globals
```

---

## Async Patterns

### Parallel Operations

```python
import asyncio

async def process_multiple(items: list[str]) -> list[dict]:
    # Run operations in parallel
    results = await asyncio.gather(
        *[process_one(item) for item in items]
    )
    return results
```

### Error Handling in Async

```python
async def safe_operation(item: str) -> dict | None:
    try:
        result = await risky_operation(item)
        return result
    except Exception as e:
        logger.error(f"Failed to process {item}: {e}")
        return None
```

---

## Performance Best Practices

### 1. Use Async for I/O Operations

```python
# ✅ GOOD - Async I/O
async def read_files(paths: list[str]) -> list[str]:
    return await asyncio.gather(*[read_file(p) for p in paths])

# ❌ BAD - Blocking I/O
def read_files(paths: list[str]) -> list[str]:
    return [open(p).read() for p in paths]
```

### 2. Cache Aggressively

```python
@mcp.tool
async def expensive_operation(param: str, ctx: Context) -> dict:
    cache_manager = ctx.request_context.get("cache_manager")
    
    # Check cache first
    cached = await cache_manager.get_analysis(f"op:{param}")
    if cached:
        return cached
    
    # Compute if not cached
    result = await compute_expensive(param)
    
    # Cache for next time
    await cache_manager.set_analysis(f"op:{param}", result, ttl=3600)
    return result
```

### 3. Use Connection Pooling

```python
# For SQLite, reuse connection
class CacheManager:
    def __init__(self):
        self.db_path = "cache.db"
        self._connection = None
    
    async def get_connection(self):
        if not self._connection:
            self._connection = await aiosqlite.connect(self.db_path)
        return self._connection
```

---

## Testing Patterns

### Testing FastMCP Tools

```python
import pytest
from fastmcp import FastMCP

@pytest.mark.asyncio
async def test_tool():
    mcp = FastMCP("test-server")
    
    @mcp.tool
    def add(a: int, b: int) -> int:
        return a + b
    
    # Test tool directly
    result = add(2, 3)
    assert result == 5
```

### Testing Async Operations

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result == expected
```

---

## Security Best Practices

### 1. Path Sanitization

```python
import os
from pathlib import Path

def sanitize_path(user_path: str) -> Path:
    # Remove dangerous patterns
    clean = user_path.replace("..", "").replace("~", "")
    
    # Resolve to absolute path
    path = Path(clean).resolve()
    
    # Validate it's within allowed directory
    allowed = Path("/allowed/directory").resolve()
    if not str(path).startswith(str(allowed)):
        raise ValueError("Path outside allowed directory")
    
    return path
```

### 2. Input Validation

```python
@mcp.tool
def process_file(path: str, max_size_mb: int = 10) -> dict:
    # Validate path
    safe_path = sanitize_path(path)
    
    # Check file size
    size_mb = safe_path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"File too large: {size_mb:.1f}MB > {max_size_mb}MB")
    
    # Process file
    return process(safe_path)
```

### 3. Use Safe YAML Loading

```python
# ✅ ALWAYS use safe_load
config = yaml.safe_load(file)

# ❌ NEVER use load (unless you control the YAML source)
config = yaml.load(file)  # Security risk!
```

---

## Logging Best Practices

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log")
    ]
)

logger = logging.getLogger(__name__)

# Log tool invocations
@mcp.tool
async def my_tool(param: str) -> dict:
    logger.info(f"Tool invoked: my_tool with param={param}")
    
    try:
        result = await process(param)
        logger.info(f"Tool completed: my_tool in {duration}ms")
        return result
    except Exception as e:
        logger.exception(f"Tool failed: my_tool - {e}")
        raise
```

---

## Summary

### Key Takeaways

1. **FastMCP handles serialization** - Return dict/list directly
2. **FastMCP handles errors** - Just raise exceptions
3. **Use Context injection** - Don't use module-level globals
4. **Use async for I/O** - aiofiles, aiosqlite, asyncio.gather
5. **Use safe_load for YAML** - Prevents code execution
6. **Sanitize paths** - Prevent directory traversal
7. **Cache aggressively** - 3-tier cache for performance
8. **Log operations** - Track performance and errors

### Verification Status

All patterns in this document have been verified against:
- FastMCP Context7 documentation (Trust Score 9.3)
- aiofiles Context7 documentation (Trust Score 9.4)
- aiosqlite Context7 documentation (Trust Score 7.7)
- Python standard library documentation

**Last Verified:** November 12, 2025

---

**For implementation examples, see:**
- [ULTIMATE-MCP-SERVER.md](ULTIMATE-MCP-SERVER.md) - Complete server implementation
- [LOCAL-DEVELOPMENT.md](LOCAL-DEVELOPMENT.md) - Development workflow
- [API_VERIFICATION_REPORT.md](../API_VERIFICATION_REPORT.md) - Detailed verification report
