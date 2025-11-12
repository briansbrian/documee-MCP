# Implementation Checklist

**Last Updated:** November 12, 2025  
**Purpose:** Step-by-step checklist for implementing the MCP server

---

## Pre-Implementation Checklist

### ⚠️ Before Writing Any Server Code

- [ ] Read [API-VERIFICATION-SUMMARY.md](API-VERIFICATION-SUMMARY.md)
- [ ] Read [IMPLEMENTATION-READINESS.md](IMPLEMENTATION-READINESS.md)
- [ ] Read [API-PATTERNS.md](API-PATTERNS.md) completely
- [ ] Understand the 5 critical issues in specification documents
- [ ] Memorize correct FastMCP import: `from fastmcp import FastMCP, Context`
- [ ] Understand Context injection pattern
- [ ] Understand automatic error handling (no manual wrapping)
- [ ] Review [ULTIMATE-MCP-SERVER.md](ULTIMATE-MCP-SERVER.md) for architecture

### ✅ Verify Foundation

- [x] Python 3.12 installed
- [x] Virtual environment created
- [x] Dependencies installed from requirements.txt
- [x] Project structure created
- [x] Configuration management implemented (Task 2)
- [x] Data models defined (Task 3)
- [x] Utilities implemented (Task 4)

---

## Phase 2: Core Infrastructure

### Task 5: UnifiedCacheManager

- [ ] Create `src/cache/unified_cache.py`
- [ ] Implement `UnifiedCacheManager` class
- [ ] Add memory cache (Tier 1) with LRU eviction
  - [ ] `_memory_cache` dictionary
  - [ ] `_cache_order` for LRU tracking
  - [ ] `max_memory_bytes` limit
  - [ ] `current_memory_size` tracking
- [ ] Add SQLite cache (Tier 2)
  - [ ] Create database connection
  - [ ] Create tables: `file_cache`, `analysis_cache`, `session_state`
  - [ ] Implement async queries with aiosqlite
- [ ] Add optional Redis cache (Tier 3)
  - [ ] Check if redis_url provided
  - [ ] Create Redis connection if available
- [ ] Implement `async def initialize()`
  - [ ] Create database tables
  - [ ] Initialize connections
- [ ] Implement `async def close()`
  - [ ] Close database connections
  - [ ] Close Redis connection if exists
- [ ] Implement async context manager (`__aenter__`, `__aexit__`)
- [ ] Implement `get_analysis(key)` with cache promotion
  - [ ] Check memory cache first
  - [ ] Check SQLite cache second
  - [ ] Check Redis cache third
  - [ ] Promote to higher tiers on hit
- [ ] Implement `set_analysis(key, data, ttl)`
  - [ ] Store in all three tiers
  - [ ] Handle TTL expiration
- [ ] Implement `get_session(codebase_id)` and `set_session(codebase_id, state)`
- [ ] Implement `get_resource(key)` and `set_resource(key, data)`
- [ ] Implement `get_stats()` returning hit rates and metrics
- [ ] Track statistics: hits, misses, evictions per tier
- [ ] Write unit tests in `tests/test_cache.py`
- [ ] Test LRU eviction
- [ ] Test cache promotion
- [ ] Test statistics tracking

---

## Phase 3: Tool Implementation

### Task 6: Codebase Scanner

- [ ] Create `src/tools/scan_codebase.py`
- [ ] Implement `scan_codebase(path, max_depth, use_cache, ctx)` function
- [ ] Implement directory traversal with `os.walk()`
- [ ] Implement max_depth limiting
- [ ] Implement language detection by extension
- [ ] Skip directories in IGNORE_PATTERNS
- [ ] Generate codebase_id using SHA-256 hash
- [ ] Calculate total_files, total_directories, total_size_mb
- [ ] Build languages dictionary (count by language)
- [ ] Build file_types dictionary (count by extension)
- [ ] Determine primary_language (most common)
- [ ] Determine project_type (web-application/python-application/Unknown)
- [ ] Check has_tests (look for test directories)
- [ ] Determine size_category (small/medium/large)
- [ ] Measure scan_time_ms
- [ ] Check cache if use_cache=True
- [ ] Store result in cache with key "scan:{codebase_id}"
- [ ] Store result as resource "structure"
- [ ] Create session state with phase="scanned"
- [ ] Handle errors: invalid path, permission denied, file too large
- [ ] Write unit tests in `tests/test_scan_codebase.py`
- [ ] Test with sample codebase
- [ ] Verify performance: <3s for 1000 files
- [ ] Verify caching: <0.1s on second run

### Task 7: Framework Detector

- [ ] Create `src/tools/detect_frameworks.py`
- [ ] Implement `detect_frameworks(codebase_id, confidence_threshold, use_cache, ctx)` function
- [ ] Retrieve scan result from cache
- [ ] Raise ValueError if scan result doesn't exist
- [ ] For JavaScript/TypeScript: read package.json
- [ ] Parse dependencies and devDependencies
- [ ] Detect React, Next.js, Express, Vue, Angular, NestJS
- [ ] Assign confidence 0.99 for package.json dependencies
- [ ] For Python: read requirements.txt
- [ ] Detect Django, Flask, FastAPI, Pytest
- [ ] Assign confidence 0.95 for requirements.txt
- [ ] Create Framework objects with name, version, confidence, evidence
- [ ] Sort frameworks by confidence descending
- [ ] Filter by confidence_threshold
- [ ] Check cache if use_cache=True
- [ ] Store result in cache with key "frameworks:{codebase_id}"
- [ ] Handle JSON parsing errors gracefully
- [ ] Write unit tests in `tests/test_detect_frameworks.py`
- [ ] Test with React project
- [ ] Test with Python project
- [ ] Verify 99% confidence for package.json deps

### Task 8: Feature Discoverer

- [ ] Create `src/tools/discover_features.py`
- [ ] Implement `discover_features(codebase_id, categories, use_cache, ctx)` function
- [ ] Retrieve scan result from cache
- [ ] Raise ValueError if scan result doesn't exist
- [ ] Accept categories parameter (default ["all"])
- [ ] Search for directory patterns:
  - [ ] routes/pages/app for routes
  - [ ] components/widgets for components
  - [ ] api/endpoints/controllers for api
  - [ ] utils/helpers/lib for utils
  - [ ] hooks/composables for hooks
- [ ] Generate feature_id using SHA-256 hash
- [ ] Create Feature objects with id, name, category, path, priority
- [ ] Assign priority: high for routes/api, medium for others
- [ ] Filter by categories if not ["all"]
- [ ] Check cache if use_cache=True
- [ ] Store result in cache with key "features:{codebase_id}"
- [ ] Store result as resource "features"
- [ ] Write unit tests in `tests/test_discover_features.py`
- [ ] Test with React app (routes, components, hooks)
- [ ] Verify performance: <5s on first run

---

## Phase 4: MCP Server Implementation

### Task 9: Logging System

- [ ] Configure Python logging in `src/server.py`
- [ ] Set level from config (default "INFO")
- [ ] Set format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
- [ ] Add console handler (StreamHandler)
- [ ] Add file handler (FileHandler to server.log)
- [ ] Log tool invocations at INFO
- [ ] Log tool completions at INFO with duration
- [ ] Log slow operations at WARNING (>1000ms)
- [ ] Log errors at ERROR with stack trace
- [ ] Log cache statistics at INFO
- [ ] Log server startup at INFO
- [ ] Log server shutdown at INFO
- [ ] Support DEBUG level for detailed logging

### Task 10: MCP Server Core

- [ ] Create `src/server.py`
- [ ] Import FastMCP and Context: `from fastmcp import FastMCP, Context`
- [ ] Define AppContext dataclass with cache_manager and config
- [ ] Implement `app_lifespan` async context manager
  - [ ] Startup: load Settings
  - [ ] Startup: create UnifiedCacheManager
  - [ ] Startup: call `await cache_manager.initialize()`
  - [ ] Yield context dict with cache_manager
  - [ ] Shutdown: call `await cache_manager.close()`
- [ ] Initialize FastMCP: `mcp = FastMCP("codebase-to-course-mcp", lifespan=app_lifespan)`
- [ ] Register scan_codebase tool
  - [ ] Use `@mcp.tool` decorator (no parentheses)
  - [ ] Parameters: path (str), max_depth (int, default 10), use_cache (bool, default True), ctx (Context)
  - [ ] Call implementation from `src/tools/scan_codebase.py`
  - [ ] Return dict directly (FastMCP handles JSON)
- [ ] Register detect_frameworks tool
  - [ ] Use `@mcp.tool` decorator
  - [ ] Parameters: codebase_id (str), confidence_threshold (float, default 0.7), use_cache (bool, default True), ctx (Context)
  - [ ] Call implementation from `src/tools/detect_frameworks.py`
  - [ ] Return dict directly
- [ ] Register discover_features tool
  - [ ] Use `@mcp.tool` decorator
  - [ ] Parameters: codebase_id (str), categories (list[str], default None), use_cache (bool, default True), ctx (Context)
  - [ ] Call implementation from `src/tools/discover_features.py`
  - [ ] Return dict directly
- [ ] Add entry point: `if __name__ == "__main__": mcp.run()`
- [ ] Test server starts without errors
- [ ] Verify stdio transport works

### Task 11: MCP Resources

- [ ] Add `@mcp.resource("codebase://structure")` decorator
- [ ] Implement `get_structure()` function
  - [ ] Retrieve from cache_manager.get_resource("structure")
  - [ ] Raise ValueError if not found
  - [ ] Return dict directly
- [ ] Add `@mcp.resource("codebase://features")` decorator
- [ ] Implement `get_features()` function
  - [ ] Retrieve from cache_manager.get_resource("features")
  - [ ] Raise ValueError if not found
  - [ ] Return dict directly
- [ ] Test resources accessible

### Task 12: MCP Prompts

- [ ] Add `@mcp.prompt` decorator (no parentheses)
- [ ] Implement `analyze_codebase(codebase_path: str)` function
- [ ] Return template string with 4-step workflow
  - [ ] Step 1: Call scan_codebase
  - [ ] Step 2: Call detect_frameworks
  - [ ] Step 3: Call discover_features
  - [ ] Step 4: Focus on teachable code
- [ ] Include codebase_path in template using f-string
- [ ] Test prompt returns correct template

---

## Phase 5: Testing and Validation

### Task 13: MCP Inspector Testing

- [ ] Install MCP Inspector: `npm install -g @modelcontextprotocol/inspector`
- [ ] Start server with inspector: `npx @modelcontextprotocol/inspector python -m src.server`
- [ ] Verify server connects
- [ ] Test List Tools
  - [ ] Verify 3 tools displayed
  - [ ] Check tool names: scan_codebase, detect_frameworks, discover_features
  - [ ] Check tool descriptions
- [ ] Test List Resources
  - [ ] Verify 2 resources displayed
  - [ ] Check URIs: codebase://structure, codebase://features
- [ ] Test List Prompts
  - [ ] Verify 1 prompt displayed
  - [ ] Check name: analyze_codebase
- [ ] Test scan_codebase tool
  - [ ] Call with valid path: `{"path": ".", "max_depth": 5}`
  - [ ] Verify JSON result returned
  - [ ] Check codebase_id, structure, summary fields
  - [ ] Verify scan_time_ms < 3000
- [ ] Test scan_codebase with invalid path
  - [ ] Call with path: `"../../../etc/passwd"`
  - [ ] Verify error returned
- [ ] Test detect_frameworks tool
  - [ ] Call with valid codebase_id
  - [ ] Verify frameworks array returned
  - [ ] Check confidence scores
- [ ] Test detect_frameworks with invalid codebase_id
  - [ ] Verify error: "Codebase not scanned. Call scan_codebase first."
- [ ] Test discover_features tool
  - [ ] Call with valid codebase_id
  - [ ] Verify features array returned
  - [ ] Check categories
- [ ] Test discover_features with categories filter
  - [ ] Call with `{"codebase_id": "<id>", "categories": ["routes", "api"]}`
  - [ ] Verify only routes and api features returned
- [ ] Test reading resource codebase://structure
  - [ ] Verify JSON data returned after scan
- [ ] Test reading resource codebase://features
  - [ ] Verify JSON data returned after discover
- [ ] Test getting prompt analyze_codebase
  - [ ] Provide codebase_path argument
  - [ ] Verify template returned with interpolated path
- [ ] Test error handling
  - [ ] Verify clear error messages for invalid inputs
  - [ ] Verify FastMCP parameter validation works

---

## Phase 6: Performance Validation

### Performance Benchmarks

- [ ] Create test codebase with 1000 files
- [ ] Benchmark scan_codebase first run
  - [ ] Verify completes in <3000ms
  - [ ] Log actual time
- [ ] Benchmark scan_codebase cached run
  - [ ] Verify completes in <100ms
  - [ ] Log actual time
- [ ] Benchmark detect_frameworks
  - [ ] Verify completes in <3000ms on first run
- [ ] Benchmark discover_features
  - [ ] Verify completes in <5000ms on first run
- [ ] Benchmark complete workflow (scan → detect → discover)
  - [ ] Verify completes in <15000ms total
- [ ] Measure cache hit rate after 10 tool calls
  - [ ] Verify >70% hit rate
- [ ] Verify framework detection accuracy
  - [ ] Test with 5 different projects
  - [ ] Verify 99% confidence for package.json deps
- [ ] Log performance metrics
  - [ ] scan_time_ms
  - [ ] cache_hit_rate
  - [ ] total_workflow_time_ms
- [ ] Log warnings when targets not met

---

## Phase 7: Documentation Updates

### Update Documentation

- [ ] Update README.md with actual usage examples
- [ ] Update SETUP.md with any new setup steps
- [ ] Update LOCAL-DEVELOPMENT.md with testing results
- [ ] Update PROJECT-STATUS.md with completion status
- [ ] Create examples in `examples/` directory
  - [ ] Basic usage example
  - [ ] Kiro integration config
  - [ ] Claude Desktop config
- [ ] Document any issues encountered
- [ ] Document performance results
- [ ] Update IMPLEMENTATION-PLAN.md with actual timeline

---

## Final Checklist

### Before Marking Complete

- [ ] All 13 core tasks completed
- [ ] All tools work in MCP Inspector
- [ ] All resources accessible
- [ ] Prompt returns correct template
- [ ] Error handling works correctly
- [ ] Performance targets met
- [ ] Unit tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed for security issues
- [ ] No hardcoded credentials or sensitive data
- [ ] Logging configured correctly
- [ ] Cache working across all three tiers

### Integration Testing

- [ ] Test with Kiro
  - [ ] Create `.kiro/settings/mcp.json`
  - [ ] Start server
  - [ ] Verify tools accessible from Kiro
- [ ] Test with Claude Desktop (optional)
  - [ ] Create `claude_desktop_config.json`
  - [ ] Start server
  - [ ] Verify tools accessible from Claude

---

## Success Criteria

### Functional Requirements

- ✅ Server starts without errors
- ✅ All 3 tools work correctly
- ✅ All 2 resources accessible
- ✅ Prompt returns correct template
- ✅ Error handling works
- ✅ Caching works across restarts

### Performance Requirements

- ✅ Scan completes in <3s (1000 files)
- ✅ Cached scan in <0.1s
- ✅ Framework detection in <3s
- ✅ Feature discovery in <5s
- ✅ Complete workflow in <15s
- ✅ Cache hit rate >70%
- ✅ Framework accuracy 99%

### Quality Requirements

- ✅ No security vulnerabilities
- ✅ Path sanitization working
- ✅ Error messages clear
- ✅ Logging comprehensive
- ✅ Code documented
- ✅ Tests passing

---

## Notes

### Common Issues

1. **Import errors**: Make sure to use `from fastmcp import FastMCP, Context`
2. **Cache not working**: Verify `await cache_manager.initialize()` is called
3. **Slow performance**: Check if caching is enabled
4. **Resources not found**: Verify tools store results as resources
5. **Context not accessible**: Use `ctx: Context` parameter in tools

### Tips

- Use `logger.debug()` for detailed debugging
- Test each tool individually before integration
- Use MCP Inspector for quick testing
- Check cache statistics regularly
- Monitor performance metrics

---

**Last Updated:** November 12, 2025

**For Questions:**
- Review [API-PATTERNS.md](API-PATTERNS.md) for correct patterns
- Check [IMPLEMENTATION-READINESS.md](IMPLEMENTATION-READINESS.md) for status
- See [API_VERIFICATION_REPORT.md](../API_VERIFICATION_REPORT.md) for issues
