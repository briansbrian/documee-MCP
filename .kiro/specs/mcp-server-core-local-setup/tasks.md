# Implementation Tasks

## Task Breakdown

### Phase 1: Project Setup and Environment

- [x] 1. Create Project Structure and Environment









  - Create directory structure: `src/`, `src/tools/`, `src/cache/`, `src/models/`, `src/utils/`, `src/config/`, `tests/`, `cache_db/`, `examples/`
  - Create `__init__.py` files in all Python packages
  - Create `.gitignore` for Python project (include venv/, cache_db/, *.pyc, __pycache__/, *.log)
  - Create `requirements.txt` with all dependencies (fastmcp>=0.5.0, aiofiles>=23.2.1, aiosqlite>=0.19.0, pyyaml>=6.0.1, python-dotenv>=1.0.0, pytest>=7.4.3, pytest-asyncio>=0.21.1, pytest-cov>=4.1.0)
  - Note: Use 'fastmcp' package, not 'mcp' - FastMCP is the framework, MCP is the protocol
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 2. Create Configuration Management System










  - Create `config.yaml` with default settings for server, cache, analysis, security, performance, and logging
  - Implement `src/config/settings.py` with Settings class that loads config.yaml
  - Implement environment variable overrides (CACHE_MAX_SIZE_MB, REDIS_URL, MAX_FILE_SIZE_MB)
  - Add validation for configuration values (positive numbers, valid paths)
  - Provide default values: max_memory_mb=500, sqlite_path="cache_db/cache.db", redis_url=None, max_file_size_mb=10, max_depth=10, log_level="INFO"
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

---

### Phase 2: Core Infrastructure

- [x] 3. Implement Data Models and Schemas





  - Create `src/models/schemas.py` with dataclasses
  - Define `ScanResult` dataclass with codebase_id, structure, summary, scan_time_ms, from_cache fields
  - Define `Framework` dataclass with name, version, confidence, evidence fields
  - Define `FrameworkDetectionResult` dataclass with frameworks, total_detected, confidence_threshold, from_cache fields
  - Define `Feature` dataclass with id, name, category, path, priority fields
  - Define `FeatureDiscoveryResult` dataclass with features, total_features, categories, from_cache fields
  - Ensure all dataclasses can serialize to/from JSON
  always use .\venv\Scripts\python.exe
  - _Requirements: Design Section - Data Models_

- [x] 4. Implement Utility Functions





  - Create `src/utils/path_utils.py` with path sanitization function that removes ".." and "~" characters
  - Create `src/utils/file_utils.py` with file size calculation and file operations
  - Implement `generate_codebase_id()` function using SHA-256 hash of absolute path, truncated to 16 characters
  - Implement `generate_feature_id()` function using SHA-256 hash of directory path, truncated to 16 characters
  - Add Windows-specific path handling (support both backslashes and forward slashes)
    always use .\venv\Scripts\python.exe
  - _Requirements: 1.4, 3.3, 5.5, 8.4_

- [x] 5. Implement UnifiedCacheManager with 3-Tier Architecture













  - Create `src/cache/unified_cache.py` with UnifiedCacheManager class
  - Implement memory cache (Tier 1) with LRU eviction and max_memory_bytes limit
  - Implement SQLite cache (Tier 2) with tables: file_cache, analysis_cache, session_state
  - Implement optional Redis cache (Tier 3) support
  - Implement `async def initialize()` method to create database tables and connections
  - Implement `async def close()` method to properly close all connections
  - Support async context manager protocol (`__aenter__`, `__aexit__`)
  - Implement `get_analysis(key)` that checks Memory → SQLite → Redis with cache promotion
  - Implement `set_analysis(key, data, ttl)` that stores in all three tiers
  - Implement `get_session(codebase_id)` and `set_session(codebase_id, state)` for session state management
  - Implement `get_resource(key)` and `set_resource(key, data)` for MCP resources
  - Implement `get_stats()` returning hit_rate, memory_hits, sqlite_hits, redis_hits, evictions, current_memory_mb, etc.
  - Track statistics: memory_hits, memory_misses, sqlite_hits, sqlite_misses, redis_hits, redis_misses, evictions, total_requests
    always use .\venv\Scripts\python.exe
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12, 6.13, 6.14_

---

### Phase 3: Tool Implementation

- [x] 6. Implement Codebase Scanner Tool





  - Create `src/tools/scan_codebase.py` with scan implementation
  - Implement directory traversal using `os.walk()` with max_depth limit (default 10)
  - Implement language detection by extension: .js/.jsx=JavaScript, .ts/.tsx=TypeScript, .py=Python, .java=Java, .go=Go, .rs=Rust, .rb=Ruby, .php=PHP, .cs=C#, .cpp/.c=C++
  - Skip directories matching IGNORE_PATTERNS: node_modules, .git, dist, build, .next, __pycache__, venv, env, .venv, target, out, coverage, .pytest_cache
  - Generate unique codebase_id using SHA-256 hash of absolute path (16 chars)
  - Return structure with total_files, total_directories, total_size_mb, languages dict, file_types dict
  - Return summary with primary_language, project_type (web-application/python-application/Unknown), has_tests, size_category (small/medium/large)
  - Return scan_time_ms showing actual execution time
  - Implement caching with key "scan:{codebase_id}" and ttl=3600 seconds
  - Store result as resource "structure" using cache_manager.set_resource()
  - Create session state with phase="scanned" and timestamp
  - Handle errors: invalid path, permission denied, file too large (>10MB)
    always use .\venv\Scripts\python.exe
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14_

- [x] 7. Implement Framework Detection Tool





  - Create `src/tools/detect_frameworks.py` with detection logic
  - Retrieve scan result from cache using key "scan:{codebase_id}"
  - Raise ValueError if scan result doesn't exist: "Codebase not scanned. Call scan_codebase first."
  - For JavaScript/TypeScript: read package.json, parse dependencies and devDependencies
  - Detect JS frameworks: React, Next.js, Express, Vue, Angular (@angular/core), NestJS (@nestjs/core)
  - Assign confidence 0.99 for package.json dependencies with evidence "package.json dependency"
  - For Python: read requirements.txt and detect Django, Flask, FastAPI, Pytest
  - Assign confidence 0.95 for requirements.txt dependencies
  - Include name, version (from file or "detected"), confidence (0.0-1.0), evidence array for each framework
  - Sort frameworks by confidence score descending
  - Filter by confidence_threshold parameter (default 0.7)
  - Return empty array if no frameworks detected
  - Cache result with key "frameworks:{codebase_id}" and ttl=3600 seconds
  - Handle JSON parsing errors gracefully without failing entire detection

  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14_

- [x] 8. Implement Feature Discovery Tool





  - Create `src/tools/discover_features.py` with discovery logic
  - Retrieve scan result from cache using key "scan:{codebase_id}"
  - Raise ValueError if scan result doesn't exist: "Codebase not scanned. Call scan_codebase first."
  - Accept categories parameter (default ["all"]): routes, components, api, utils, hooks, or all
  - Search for directory patterns: routes/pages/app (routes), components/widgets (components), api/endpoints/controllers (api), utils/helpers/lib (utils), hooks/composables (hooks)
  - Generate unique feature_id using SHA-256 hash of directory path (16 chars)
  - Create feature objects with id, name (directory name), category, path (absolute), priority (high for routes/api, medium for others)
  - Return features array, total_features count, categories list (unique categories found)
  - Filter features by categories parameter if not ["all"]
  - Cache result with key "features:{codebase_id}" and ttl=3600 seconds
  - Store result as resource "features" using cache_manager.set_resource()
    always use .\venv\Scripts\python.exe
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12, 5.13, 5.14_

---

### Phase 4: MCP Server Implementation

- [x] 9. Implement Logging System





  - Initialize Python logging module with level from config (default "INFO")
  - Set format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  - Add console handler (StreamHandler) and file handler (FileHandler to server.log)
  - Log tool invocations at INFO: "Tool invoked: {tool_name} with arguments: {arguments}"
  - Log tool completions at INFO: "Tool completed: {tool_name} in {duration_ms}ms"
  - Log slow operations at WARNING if duration > slow_operation_threshold_ms (default 1000ms)
  - Log errors at ERROR level with full stack trace using logging.exception()
  - Log cache statistics at INFO: "Cache stats: hit_rate={hit_rate:.2%}, memory_hits={memory_hits}, sqlite_hits={sqlite_hits}, evictions={evictions}"
  - Log server startup at INFO: "MCP Server started: codebase-to-course-mcp v1.0.0"
  - Log server shutdown at INFO: "MCP Server shutting down gracefully"
  - Log God Mode performance achievements when targets are met
  - Support DEBUG level for detailed logging (cache hits/misses, file operations, parameter values)
   always use .\venv\Scripts\python.exe

  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11, 10.12_

- [x] 10. Implement MCP Server Core with FastMCP






  - Create `src/server.py` as main entry point
  - Import FastMCP and Context from fastmcp (not mcp.server.fastmcp)
  - Define AppContext dataclass with cache_manager and config fields
  - Implement app_lifespan async context manager for cache lifecycle management
  - In lifespan startup: load Settings, create UnifiedCacheManager, call await cache_manager.initialize()
  - In lifespan shutdown: call await cache_manager.close()
  - Initialize FastMCP server: `mcp = FastMCP("codebase-to-course-mcp", lifespan=app_lifespan)`
  - Register scan_codebase tool using @mcp.tool decorator (no parentheses) with parameters: path (str), max_depth (int, default 10), use_cache (bool, default True), ctx (Context)
  - Register detect_frameworks tool using @mcp.tool decorator with parameters: codebase_id (str), confidence_threshold (float, default 0.7), use_cache (bool, default True), ctx (Context)
  - Register discover_features tool using @mcp.tool decorator with parameters: codebase_id (str), categories (list[str], default None), use_cache (bool, default True), ctx (Context)
  - Access lifespan context in tools: Store app_ctx in a module-level variable or use ctx to access server state
  - Each tool should call corresponding implementation from tools/ modules
  - Each tool should return dict directly (FastMCP handles serialization automatically)
  - Let FastMCP handle error conversion automatically - no manual try-catch needed for error responses
  - Add `if __name__ == "__main__": mcp.run()` entry point for stdio transport (default)
   always use .\venv\Scripts\python.exe

  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10_

- [x] 11. Implement MCP Resources





  - Add @mcp.resource("codebase://structure") decorator in src/server.py
  - Implement get_structure function that retrieves cached structure from cache_manager.get_resource("structure")
  - Raise ValueError with message "Resource not available. Run scan_codebase first." if not found
  - Return dict or str directly (FastMCP handles JSON serialization automatically)
  - Add @mcp.resource("codebase://features") decorator in src/server.py
  - Implement get_features function that retrieves cached features from cache_manager.get_resource("features")
  - Raise ValueError with message "Resource not available. Run discover_features first." if not found
  - Return dict or str directly (FastMCP handles JSON serialization automatically)
  - FastMCP automatically sets mimeType to "application/json" for dict returns
   always use .\venv\Scripts\python.exe

  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

- [x] 12. Implement MCP Prompts





  - Add @mcp.prompt decorator (no parentheses) in src/server.py
  - Implement analyze_codebase function with parameter: codebase_path (str)
  - Return template string with 4-step workflow: 1) scan_codebase, 2) detect_frameworks, 3) discover_features, 4) focus on teachable code
  - Include codebase_path in template text using f-string interpolation
  - Template should guide AI through progressive discovery workflow
  - FastMCP auto-generates prompt schema from function signature and type hints
    always use .\venv\Scripts\python.exe
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

---

### Phase 5: Testing and Validation

- [x] 13. Test with MCP Inspector






  - Install MCP Inspector: `npm install -g @modelcontextprotocol/inspector`
  - Start server with inspector: `npx @modelcontextprotocol/inspector python -m src.server`
  - Verify server connects and responds to initialize request
  - Test List Tools: verify 3 tools displayed (scan_codebase, detect_frameworks, discover_features)
  - Test List Resources: verify 2 resources displayed (codebase://structure, codebase://features)
  - Test List Prompts: verify 1 prompt displayed (analyze_codebase)
  - Test scan_codebase with valid path: `{"path": ".", "max_depth": 5}`
  - Test scan_codebase with invalid path: verify error handling for "../../../etc/passwd"
  - Test detect_frameworks with valid codebase_id: verify frameworks returned
  - Test detect_frameworks with nonexistent codebase_id: verify error "Codebase not scanned. Call scan_codebase first."
  - Test discover_features with valid codebase_id and categories: `{"codebase_id": "<id>", "categories": ["routes", "api"]}`
  - Test discover_features with empty codebase_id: verify validation error
  - Test reading resource codebase://structure after scan: verify JSON data returned
  - Test reading resource codebase://features after discover: verify JSON data returned
  - Test getting prompt analyze_codebase with codebase_path: verify template returned with interpolated path
  - Verify FastMCP parameter validation returns clear error messages for invalid inputs
    always use .\venv\Scripts\python.exe
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12_

- [ ]* 14. Write Unit Tests
  - Create `tests/test_cache.py` for UnifiedCacheManager (test memory cache, SQLite cache, LRU eviction, cache promotion, statistics)
  - Create `tests/test_scan_codebase.py` for scanner (test directory traversal, language detection, ignore patterns, caching)
  - Create `tests/test_detect_frameworks.py` for detector (test package.json parsing, requirements.txt parsing, confidence scoring)
  - Create `tests/test_discover_features.py` for discoverer (test directory pattern matching, feature ID generation, priority assignment)
  - Create `tests/test_utils.py` for utilities (test path sanitization, codebase ID generation, feature ID generation)
  - Run tests with `pytest` and verify all pass
  - Run tests with coverage: `pytest --cov=src tests/`
  - Verify code coverage >80%
  - Verify tests run in <10 seconds
  - _Requirements: Testing Strategy_
   always use .\venv\Scripts\python.exe

- [ ]* 15. Performance Benchmarking and Validation
  - Create test codebase with 1000 files for benchmarking
  - Benchmark scan_codebase first run: verify completes in <3000ms
  - Benchmark scan_codebase cached run: verify completes in <100ms
  - Benchmark detect_frameworks: verify completes in <3000ms on first run
  - Benchmark discover_features: verify completes in <5000ms on first run
  - Benchmark complete workflow (scan → detect → discover): verify completes in <15000ms total
  - Measure cache hit rate after 10 tool calls: verify >70%
  - Log performance metrics: scan_time_ms, cache_hit_rate, total_workflow_time_ms
  - Log warnings when performance targets are not met
  - Verify framework detection achieves 99% confidence for package.json dependencies

  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8, 15.9, 15.10_

---

### Phase 6: Documentation and Examples

- [ ]* 16. Create Example Usage and Configuration Files
  - Create `examples/basic_usage.py` with MCP client example demonstrating all 3 tools
  - Create `examples/kiro_config.json` for Kiro integration with command, args, cwd, disabled fields
  - Create `examples/claude_config.json` for Claude Desktop integration
  - Document testing methods: MCP Inspector, development mode (`uv run mcp dev`), direct run
  - Include example tool calls with expected responses
   always use .\venv\Scripts\python.exe
  - _Requirements: Documentation_

- [ ]* 17. Write Project README
  - Create comprehensive `README.md` in project root
  - Document installation steps: Python 3.12, virtual environment, requirements.txt
  - Document project structure and architecture overview
  - Document usage examples for all 3 tools
  - Document configuration options (config.yaml and environment variables)
  - Document God Mode performance targets: 20x speedup, 99% accuracy, 70%+ cache hit rate
  - Document testing instructions: MCP Inspector, unit tests, performance benchmarks
  - Document integration with Kiro and Claude Desktop
  - Include troubleshooting section
  - _Requirements: Documentation_

---

## Implementation Summary

### Total Tasks: 17 tasks
- **Core Implementation Tasks:** 13 tasks (Tasks 1-13)
- **Optional Testing/Documentation Tasks:** 4 tasks (Tasks 14-17, marked with *)

### Estimated Time: ~15 hours for core implementation
- Phase 1: Project Setup (1 hour)
- Phase 2: Core Infrastructure (4 hours)
- Phase 3: Tool Implementation (5 hours)
- Phase 4: MCP Server Implementation (3 hours)
- Phase 5: Testing and Validation (2 hours for MCP Inspector testing)
- Phase 6: Documentation (optional, ~1 hour)

### Critical Path:
1. Tasks 1-2: Project setup and configuration
2. Tasks 3-5: Core infrastructure (data models, utilities, cache manager)
3. Tasks 6-8: Tool implementation (scanner, detector, discoverer)
4. Tasks 9-12: MCP server with FastMCP (logging, server core, resources, prompts)
5. Task 13: MCP Inspector testing (validation)

### Key Implementation Notes:
- Using FastMCP for simplified server implementation with decorator-based registration
- Lifespan management ensures proper cache initialization and cleanup
- 3-tier cache (Memory → SQLite → Redis) enables God Mode performance
- All tools follow consistent pattern: check cache → execute → cache result → return
- Error handling is automatic via FastMCP exception conversion
- Path sanitization prevents security vulnerabilities
- Performance logging tracks God Mode targets

### Requirements Coverage:
- **Requirement 1:** Tasks 1, 2 (Local Development Environment)
- **Requirement 2:** Tasks 10, 11, 12 (MCP Server Core)
- **Requirement 3:** Task 6 (Codebase Scanner)
- **Requirement 4:** Task 7 (Framework Detector)
- **Requirement 5:** Task 8 (Feature Discoverer)
- **Requirement 6:** Task 5 (3-Tier Cache System)
- **Requirement 7:** Task 13 (MCP Inspector Testing)
- **Requirement 8:** Tasks 4, 6, 7, 8, 10 (Error Handling & Security)
- **Requirement 9:** Task 2 (Configuration Management)
- **Requirement 10:** Task 9 (Logging & Performance Diagnostics)
- **Requirement 11:** Not in Spec 1 (Parallel File Reader - future spec)
- **Requirement 12:** Task 5 (Progressive Discovery via Session State)
- **Requirement 13:** Task 11 (MCP Resources)
- **Requirement 14:** Task 12 (MCP Prompts)
- **Requirement 15:** Task 15 (Performance Benchmarking - optional)

### Next Steps After Completion:
- **Spec 2:** Advanced Analysis Tools (parallel file reader, code analyzer, teaching value scorer)
- **Spec 3:** Course Generation (outline generator, lesson planner, content generator)
- **Spec 4:** Azure Deployment (containerization, Azure services integration)
