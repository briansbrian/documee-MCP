# Requirements Document

## Introduction

This specification defines the requirements for building the core MCP (Model Context Protocol) server with local development setup for the Documee project. The MCP Server will achieve "God Mode" performance - transforming AI assistants from "pretty good" to "absolutely unstoppable" at codebase analysis. The system must deliver 20x faster analysis (2-3 seconds vs 30-100 seconds), 99% accuracy, and 0% hallucination rate through intelligent caching, parallel processing, and evidence-based validation.

This initial implementation (Spec 1) focuses on establishing the foundation: local environment, core MCP server, 3 essential discovery tools, and the 3-tier caching system that enables God Mode performance.

## Glossary

- **MCP Server**: A server implementing the Model Context Protocol that exposes tools, resources, and prompts to AI clients via JSON-RPC 2.0 over stdio transport
- **AI Client**: An AI assistant (like Claude, GPT, or Kiro) that connects to the MCP Server
- **Tool**: A callable function exposed by the MCP Server that performs a specific operation (e.g., scan_codebase, detect_frameworks)
- **Resource**: A URI-addressable data source that provides structured information (e.g., codebase://structure)
- **Prompt**: A template that guides AI clients through common workflows (e.g., analyze_codebase)
- **Codebase**: A software project directory containing source code files
- **Codebase ID**: A unique SHA-256 hash identifier generated for each analyzed codebase
- **Discovery Tool**: A tool that scans and identifies characteristics of a codebase (scan_codebase, discover_features, detect_frameworks)
- **MCP Inspector**: A testing tool provided by Anthropic for validating MCP server implementations
- **Session State**: Per-codebase data maintained during analysis operations, stored in memory and SQLite
- **Cache Key**: A SHA-256 hash identifier used to store and retrieve cached analysis results
- **3-Tier Cache**: A caching system with Memory (LRU), SQLite (persistent), and Redis (optional distributed) layers
- **God Mode**: Performance target of 20x faster analysis with 99% accuracy and 0% hallucination rate
- **Parallel File Reader**: A tool that reads multiple files simultaneously using asyncio, achieving 10x speedup
- **Framework Confidence Score**: A 0.0-1.0 score indicating detection certainty, with 0.99 for package.json dependencies
- **Teaching Value Score**: A 0-14 scale score assessing code's suitability for teaching purposes
- **Evidence-Based Validation**: Anti-hallucination technique requiring all claims to be backed by actual code evidence

## Requirements

### Requirement 1: Local Development Environment Setup

**User Story:** As a developer, I want to set up a local Python development environment with all required dependencies, so that I can develop and test the MCP server on my Windows machine before deploying to Azure.

#### Acceptance Criteria

1. WHEN the developer installs Python 3.12, THE Development_Environment SHALL verify the Python version is 3.12 or above
2. WHEN the developer creates a virtual environment using python -m venv venv, THE Development_Environment SHALL create an isolated Python 3.12 virtual environment in the venv directory
3. WHEN the developer installs required dependencies from requirements.txt, THE Development_Environment SHALL install mcp>=1.0.0, aiofiles>=23.2.1, tree-sitter>=0.20.4, aiosqlite>=0.19.0, pyyaml>=6.0.1, python-dotenv>=1.0.0, pytest>=7.4.3, and pytest-asyncio>=0.21.1 without errors
4. WHERE the developer uses Windows, THE Development_Environment SHALL support Windows-specific path handling with backslashes and forward slashes
5. WHEN the developer activates the virtual environment, THE Development_Environment SHALL make all installed packages available for import in Python scripts
6. WHEN the developer runs python --version, THE Development_Environment SHALL display Python 3.12.0 or higher
7. WHEN the developer creates the project structure, THE Development_Environment SHALL create directories src/, src/tools/, src/cache/, src/analyzers/, src/generators/, src/validators/, src/models/, src/utils/, tests/, cache_db/, and examples/

---

### Requirement 2: MCP Server Core Implementation

**User Story:** As a developer, I want to implement the core MCP server structure using the official Anthropic MCP SDK, so that it can register and expose 3 discovery tools, 2 resources, and 1 prompt to AI clients via JSON-RPC 2.0 over stdio transport.

#### Acceptance Criteria

1. WHEN the MCP server starts using python -m src.server, THE MCP_Server SHALL initialize using the mcp.Server class with name "codebase-to-course-mcp"
2. WHEN an AI client connects, THE MCP_Server SHALL establish a JSON-RPC 2.0 communication channel over stdio transport using mcp.server.stdio.stdio_server
3. WHEN an AI client requests available tools using list_tools, THE MCP_Server SHALL return 3 tool definitions: scan_codebase, discover_features, and detect_frameworks with complete JSON Schema input schemas
4. WHEN an AI client requests available resources using list_resources, THE MCP_Server SHALL return 2 resource definitions: codebase://structure and codebase://features with mimeType application/json
5. WHEN an AI client requests available prompts using list_prompts, THE MCP_Server SHALL return 1 prompt definition: analyze_codebase with required argument codebase_path
6. WHEN an AI client calls a tool, THE MCP_Server SHALL validate the input parameters against the tool's JSON Schema and return a validation error if parameters are invalid
7. WHEN a tool execution completes successfully, THE MCP_Server SHALL return the result wrapped in a TextContent object with type "text" and JSON-formatted text
8. IF a tool execution fails with an exception, THEN THE MCP_Server SHALL return a TextContent object containing a JSON error with fields: error, tool, arguments, and type
9. WHEN the server receives a shutdown signal, THE MCP_Server SHALL gracefully close the stdio streams and clean up the UnifiedCacheManager resources
10. WHEN the server initializes, THE MCP_Server SHALL create a UnifiedCacheManager instance with max_memory_mb=500, sqlite_path="cache_db/cache.db", and redis_url=None

---

### Requirement 3: Codebase Scanning Tool (God Mode Performance)

**User Story:** As an AI assistant, I want to scan a codebase's structure in 2-3 seconds (vs 30-100 seconds without MCP), so that I can understand its organization, file types, languages, and size before deeper analysis, achieving 20x performance improvement.

#### Acceptance Criteria

1. WHEN the scan_codebase tool receives a valid directory path, THE Codebase_Scanner SHALL traverse the directory tree up to max_depth (default 10) using os.walk
2. WHEN scanning a directory, THE Codebase_Scanner SHALL count files by programming language using extension mapping: .js/.jsx=JavaScript, .ts/.tsx=TypeScript, .py=Python, .java=Java, .go=Go, .rs=Rust, .rb=Ruby, .php=PHP, .cs=C#, .cpp/.c=C++
3. WHEN scanning completes, THE Codebase_Scanner SHALL generate a unique codebase_id using SHA-256 hash of the absolute path, truncated to 16 characters
4. WHEN scanning completes, THE Codebase_Scanner SHALL return structure containing total_files, total_directories, total_size_mb, languages dictionary, and file_types dictionary
5. WHEN scanning completes, THE Codebase_Scanner SHALL return summary containing primary_language (most common), project_type (web-application, python-application, or Unknown), has_tests boolean, and size_category (small <100 files, medium <1000 files, large >=1000 files)
6. WHEN scanning completes, THE Codebase_Scanner SHALL return scan_time_ms showing actual execution time in milliseconds
7. WHEN the scan_codebase tool receives an invalid path, THE Codebase_Scanner SHALL return an error with message "Path does not exist: {path}"
8. WHEN scanning a directory, THE Codebase_Scanner SHALL skip directories matching IGNORE_PATTERNS: node_modules, .git, dist, build, .next, __pycache__, venv, env, .venv, target, out, coverage, .pytest_cache
9. WHEN use_cache is true and a cached result exists, THE Codebase_Scanner SHALL return the cached result with from_cache=true in under 0.1 seconds
10. WHEN scanning completes, THE Codebase_Scanner SHALL cache the result in UnifiedCacheManager with key "scan:{codebase_id}" and ttl=3600 seconds
11. WHEN scanning completes, THE Codebase_Scanner SHALL store the result as a resource with key "structure" in cache_manager.set_resource
12. WHEN scanning completes, THE Codebase_Scanner SHALL create session state with phase="scanned" and timestamp using cache_manager.set_session
13. WHEN scanning a codebase with 1000 files, THE Codebase_Scanner SHALL complete in under 3 seconds on first run
14. WHEN scanning a previously scanned codebase with cache enabled, THE Codebase_Scanner SHALL return results in under 0.1 seconds

---

### Requirement 4: Framework Detection Tool (99% Accuracy)

**User Story:** As an AI assistant, I want to detect frameworks and libraries used in a codebase with 99% accuracy and confidence scores, so that I can understand the technology stack and provide relevant analysis with evidence-based validation.

#### Acceptance Criteria

1. WHEN the detect_frameworks tool receives a codebase_id, THE Framework_Detector SHALL retrieve the scan result from cache using key "scan:{codebase_id}"
2. IF the scan result does not exist, THEN THE Framework_Detector SHALL raise ValueError with message "Codebase not scanned. Call scan_codebase first."
3. WHEN analyzing JavaScript/TypeScript projects, THE Framework_Detector SHALL read package.json from codebase path and parse dependencies and devDependencies
4. WHEN a framework is found in package.json dependencies, THE Framework_Detector SHALL assign confidence score 0.99 with evidence "package.json dependency"
5. WHEN analyzing JavaScript projects, THE Framework_Detector SHALL detect React (if "react" in deps), Next.js (if "next" in deps), Express (if "express" in deps), Vue (if "vue" in deps), Angular (if "@angular/core" in deps), and NestJS (if "@nestjs/core" in deps)
6. WHEN analyzing Python projects, THE Framework_Detector SHALL read requirements.txt from codebase path and detect Django (if "django" in requirements), Flask (if "flask" in requirements), FastAPI (if "fastapi" in requirements), and Pytest (if "pytest" in requirements) with confidence 0.95
7. WHEN a framework is detected, THE Framework_Detector SHALL include name, version (from dependency file or "detected"), confidence (0.0-1.0), and evidence array
8. WHEN multiple frameworks are detected, THE Framework_Detector SHALL return them sorted by confidence score in descending order
9. WHEN the detect_frameworks tool receives confidence_threshold parameter (default 0.7), THE Framework_Detector SHALL filter results to only include frameworks with confidence >= threshold
10. WHEN no frameworks are detected, THE Framework_Detector SHALL return empty frameworks array with total_detected=0
11. WHEN detection completes, THE Framework_Detector SHALL cache the result with key "frameworks:{codebase_id}" and ttl=3600 seconds
12. WHEN use_cache is true and a cached result exists, THE Framework_Detector SHALL return the cached result with from_cache=true in under 0.1 seconds
13. WHEN analyzing a React + Next.js project, THE Framework_Detector SHALL detect both frameworks with confidence 0.99 and include version numbers from package.json
14. WHEN detection completes in under 3 seconds on first run, THE Framework_Detector SHALL meet the God Mode performance target

---

### Requirement 5: Feature Discovery Tool (5 Second Performance)

**User Story:** As an AI assistant, I want to discover features in a codebase such as routes, components, API endpoints, utilities, and hooks in under 5 seconds, so that I can identify teachable code examples with priorities and categories.

#### Acceptance Criteria

1. WHEN the discover_features tool receives a codebase_id, THE Feature_Discoverer SHALL retrieve the scan result from cache using key "scan:{codebase_id}"
2. IF the scan result does not exist, THEN THE Feature_Discoverer SHALL raise ValueError with message "Codebase not scanned. Call scan_codebase first."
3. WHEN the discover_features tool receives categories parameter (default ["all"]), THE Feature_Discoverer SHALL filter discovery to specified categories: routes, components, api, utils, hooks, or all
4. WHEN analyzing a codebase, THE Feature_Discoverer SHALL search for directory patterns: routes/ or pages/ or app/ for routes category, components/ or widgets/ for components category, api/ or endpoints/ or controllers/ for api category, utils/ or helpers/ or lib/ for utils category, hooks/ or composables/ for hooks category
5. WHEN a feature directory is found, THE Feature_Discoverer SHALL generate a unique feature_id using SHA-256 hash of the directory path, truncated to 16 characters
6. WHEN a feature is discovered, THE Feature_Discoverer SHALL create a feature object with id, name (directory name without trailing slash), category, path (absolute directory path), and priority (high for routes/api, medium for others)
7. WHEN multiple features are discovered, THE Feature_Discoverer SHALL return them in the features array
8. WHEN discovery completes, THE Feature_Discoverer SHALL return total_features count and categories list (unique categories found)
9. WHEN discovery completes, THE Feature_Discoverer SHALL cache the result with key "features:{codebase_id}" and ttl=3600 seconds
10. WHEN use_cache is true and a cached result exists, THE Feature_Discoverer SHALL return the cached result with from_cache=true in under 0.1 seconds
11. WHEN discovery completes, THE Feature_Discoverer SHALL store the result as a resource with key "features" using cache_manager.set_resource
12. WHEN analyzing a React application with routes/, components/, and hooks/ directories, THE Feature_Discoverer SHALL discover all three features with appropriate categories and priorities
13. WHEN discovery completes in under 5 seconds on first run, THE Feature_Discoverer SHALL meet the God Mode performance target
14. WHEN categories parameter is ["routes", "api"], THE Feature_Discoverer SHALL only return features in those categories, skipping components, utils, and hooks

---

### Requirement 6: 3-Tier Cache System (God Mode Performance Enabler)

**User Story:** As a developer, I want a 3-tier caching system with Memory (LRU), SQLite (persistent), and Redis (optional) that achieves 450x speedup on cached operations (0.1s vs 45s), so that subsequent tool calls can access previously computed data without re-scanning.

#### Acceptance Criteria

1. WHEN the UnifiedCacheManager initializes, THE Cache_Manager SHALL create an in-memory LRU cache with max_memory_bytes calculated from max_memory_mb parameter (default 500MB)
2. WHEN the UnifiedCacheManager initializes, THE Cache_Manager SHALL create SQLite database at sqlite_path with tables: file_cache (path, content, hash, language, size, cached_at), analysis_cache (key, data, cached_at, ttl), and session_state (codebase_id, state, updated_at)
3. WHEN a tool calls cache_manager.get_analysis(key), THE Cache_Manager SHALL first check memory cache (Tier 1), then SQLite cache (Tier 2), then Redis cache (Tier 3) if available
4. WHEN a cache hit occurs in memory, THE Cache_Manager SHALL increment stats["memory_hits"] and return the result in under 0.001 seconds
5. WHEN a cache miss occurs in memory but hit in SQLite, THE Cache_Manager SHALL increment stats["sqlite_hits"], promote the entry to memory cache, and return the result in under 0.1 seconds
6. WHEN a cache miss occurs in both memory and SQLite but hit in Redis, THE Cache_Manager SHALL increment stats["redis_hits"], promote the entry to memory and SQLite, and return the result
7. WHEN a tool calls cache_manager.set_analysis(key, data, ttl), THE Cache_Manager SHALL store the data in all three cache tiers (memory, SQLite, and Redis if available)
8. WHEN memory cache exceeds max_memory_bytes, THE Cache_Manager SHALL evict the least recently used (LRU) entry, decrement current_memory_size, and increment stats["evictions"]
9. WHEN a tool calls cache_manager.get_session(codebase_id), THE Cache_Manager SHALL first check session_state dictionary in memory, then query SQLite session_state table
10. WHEN a tool calls cache_manager.set_session(codebase_id, state), THE Cache_Manager SHALL store the state in memory session_state dictionary and persist to SQLite session_state table
11. WHEN a tool calls cache_manager.get_stats(), THE Cache_Manager SHALL return hit_rate (total_hits / total_requests), memory_hits, memory_misses, sqlite_hits, sqlite_misses, redis_hits, redis_misses, evictions, total_requests, current_memory_mb, max_memory_mb, file_cache_entries, analysis_cache_entries, and active_sessions
12. WHEN cache hit rate exceeds 70% after initial scan, THE Cache_Manager SHALL meet the God Mode performance target
13. WHEN a cached operation completes in under 0.1 seconds (vs 45 seconds uncached), THE Cache_Manager SHALL achieve 450x speedup
14. WHEN the server restarts, THE Cache_Manager SHALL load persistent data from SQLite, maintaining cache across restarts

---

### Requirement 7: Local Testing with MCP Inspector

**User Story:** As a developer, I want to test the MCP server using the MCP Inspector tool from Anthropic, so that I can verify all 3 tools, 2 resources, and 1 prompt work correctly before integration with AI clients like Claude or Kiro.

#### Acceptance Criteria

1. WHEN the developer runs npx @modelcontextprotocol/inspector python -m src.server, THE MCP_Server SHALL start and connect to the inspector via stdio transport
2. WHEN the MCP Inspector connects, THE MCP_Server SHALL respond to the initialize request with server capabilities including tools, resources, and prompts
3. WHEN the developer clicks "List Tools" in the inspector, THE MCP_Inspector SHALL display 3 tools: scan_codebase (Scan codebase structure, languages, and frameworks), discover_features (Find all features with priorities), and detect_frameworks (Identify frameworks with confidence scores)
4. WHEN the developer clicks "List Resources" in the inspector, THE MCP_Inspector SHALL display 2 resources: codebase://structure (Codebase Structure) and codebase://features (Discovered Features)
5. WHEN the developer clicks "List Prompts" in the inspector, THE MCP_Inspector SHALL display 1 prompt: analyze_codebase (Template for initial codebase analysis)
6. WHEN the developer invokes scan_codebase with path parameter through the inspector, THE MCP_Server SHALL execute the tool and return JSON result with codebase_id, structure, summary, and scan_time_ms
7. WHEN the developer invokes detect_frameworks with codebase_id parameter, THE MCP_Server SHALL execute the tool and return JSON result with frameworks array, total_detected, and confidence_threshold
8. WHEN the developer invokes discover_features with codebase_id parameter, THE MCP_Server SHALL execute the tool and return JSON result with features array, total_features, and categories
9. WHEN the developer provides invalid parameters (e.g., missing required path), THE MCP_Inspector SHALL display the validation error from the server with clear error message
10. WHEN the developer views tool results, THE MCP_Inspector SHALL format the JSON response in a readable manner with syntax highlighting
11. WHEN the developer reads resource codebase://structure, THE MCP_Inspector SHALL display the cached structure data in JSON format
12. WHEN the developer gets prompt analyze_codebase with codebase_path argument, THE MCP_Inspector SHALL display the step-by-step analysis template

---

### Requirement 8: Error Handling and Security Validation

**User Story:** As a developer, I want comprehensive error handling, input validation, and security checks, so that the server provides clear error messages, fails gracefully, and prevents malicious path traversal or file access attacks.

#### Acceptance Criteria

1. WHEN a tool receives invalid input parameters that don't match the JSON Schema, THE MCP_Server SHALL return a TextContent error with fields: error (validation message), tool (tool name), arguments (provided args), and type ("ValidationError")
2. WHEN a file operation fails due to OSError or PermissionError, THE MCP_Server SHALL catch the exception and return an error with message "Permission denied: {path}"
3. WHEN a tool execution encounters an unexpected exception, THE MCP_Server SHALL catch the exception, log the error with stack trace, and return a TextContent error with error message, tool name, arguments, and exception type
4. WHEN a path parameter contains directory traversal attempts (../ or ~), THE MCP_Server SHALL sanitize the path by removing ".." and "~" characters before processing
5. WHEN a file size exceeds MAX_FILE_SIZE (10MB), THE MCP_Server SHALL skip the file during scanning and log a warning "File too large, skipping: {path}"
6. WHEN scanning encounters a file with insufficient permissions, THE MCP_Server SHALL skip the file and continue scanning other files without failing the entire operation
7. WHEN a tool receives a codebase_id that doesn't exist in cache, THE MCP_Server SHALL return an error with message "Codebase not scanned. Call scan_codebase first."
8. WHEN a tool receives a path that doesn't exist, THE MCP_Server SHALL return an error with message "Path does not exist: {path}"
9. WHEN the server encounters a JSON parsing error in package.json or requirements.txt, THE MCP_Server SHALL catch the exception and continue without failing the entire framework detection
10. WHEN a tool execution completes with an error, THE MCP_Server SHALL return the error wrapped in a TextContent object with type="text" and JSON-formatted error details

---

### Requirement 9: Configuration Management

**User Story:** As a developer, I want to configure server settings through config.yaml and environment variables, so that I can adjust cache size, security settings, and performance parameters without modifying code.

#### Acceptance Criteria

1. WHEN the server starts, THE Configuration_Manager SHALL load settings from config.yaml file in the project root if present
2. WHEN config.yaml exists, THE Configuration_Manager SHALL parse YAML and load settings for server (name, version, transport), cache (memory.max_size_mb, sqlite.enabled, sqlite.path, redis.enabled, redis.url), analysis (max_file_size_mb, max_files_per_scan, max_parallel_reads, scan_timeout_seconds), security (allowed_paths, max_depth, blocked_patterns), performance (enable_profiling, log_slow_operations, slow_operation_threshold_ms), and logging (level, file, max_size_mb, backup_count)
3. WHEN environment variables are defined, THE Configuration_Manager SHALL override config.yaml settings: CACHE_MAX_SIZE_MB overrides cache.memory.max_size_mb, REDIS_URL overrides cache.redis.url, MAX_FILE_SIZE_MB overrides analysis.max_file_size_mb
4. WHERE a setting has a default value, THE Configuration_Manager SHALL use the default if no override is provided: max_memory_mb=500, sqlite_path="cache_db/cache.db", redis_url=None, max_file_size_mb=10, max_depth=10, log_level="INFO"
5. WHEN the server starts, THE Configuration_Manager SHALL expose configuration values to UnifiedCacheManager (max_memory_mb, sqlite_path, redis_url) and tool modules (max_file_size_mb, max_depth, ignore_patterns)
6. WHEN config.yaml is missing, THE Configuration_Manager SHALL use all default values and log a warning "config.yaml not found, using defaults"
7. WHEN an invalid configuration value is provided (e.g., negative max_size_mb), THE Configuration_Manager SHALL raise ValueError with message "Invalid configuration: {setting} must be positive"

---

### Requirement 10: Logging and Performance Diagnostics

**User Story:** As a developer, I want the server to log operations, errors, and performance metrics, so that I can troubleshoot issues, monitor God Mode performance targets, and verify 20x speedup is achieved.

#### Acceptance Criteria

1. WHEN the server starts, THE Logging_System SHALL initialize using Python's logging module with level from config (default "INFO"), format "%(asctime)s - %(name)s - %(levelname)s - %(message)s", and handlers for both console (StreamHandler) and file (FileHandler to server.log)
2. WHEN a tool is invoked, THE Logging_System SHALL log at INFO level: "Tool invoked: {tool_name} with arguments: {arguments}"
3. WHEN a tool completes successfully, THE Logging_System SHALL log at INFO level: "Tool completed: {tool_name} in {duration_ms}ms"
4. WHEN a tool execution time exceeds slow_operation_threshold_ms (default 1000ms), THE Logging_System SHALL log at WARNING level: "Slow operation detected: {tool_name} took {duration_ms}ms"
5. WHEN an error occurs, THE Logging_System SHALL log at ERROR level with the error message and full stack trace using logging.exception()
6. WHEN the log level is set to DEBUG, THE Logging_System SHALL log detailed information including: cache hits/misses, file read operations, parameter values, and intermediate results
7. WHEN the log level is set to INFO, THE Logging_System SHALL log only high-level operations: tool invocations, completions, errors, and slow operations
8. WHEN cache statistics are requested, THE Logging_System SHALL log at INFO level: "Cache stats: hit_rate={hit_rate:.2%}, memory_hits={memory_hits}, sqlite_hits={sqlite_hits}, evictions={evictions}"
9. WHEN the server starts, THE Logging_System SHALL log at INFO level: "MCP Server started: codebase-to-course-mcp v1.0.0"
10. WHEN the server shuts down, THE Logging_System SHALL log at INFO level: "MCP Server shutting down gracefully"
11. WHEN a scan completes in under 3 seconds, THE Logging_System SHALL log at INFO level: "God Mode performance achieved: scan completed in {duration_ms}ms (target: <3000ms)"
12. WHEN cache hit rate exceeds 70%, THE Logging_System SHALL log at INFO level: "God Mode cache performance achieved: hit_rate={hit_rate:.2%} (target: >70%)"

---

### Requirement 11: Parallel File Operations (10x Performance Boost)

**User Story:** As an AI assistant, I want to read multiple files in parallel using asyncio and aiofiles, so that I can achieve 10x speedup compared to sequential file reading (1 second vs 10 seconds for 10 files).

#### Acceptance Criteria

1. WHEN the read_files_parallel tool receives a patterns array, THE Parallel_File_Reader SHALL expand glob patterns using pathlib.Path.glob() to generate a list of file paths
2. WHEN file paths are generated, THE Parallel_File_Reader SHALL limit the total number of files to max_files parameter (default 100)
3. WHEN reading files, THE Parallel_File_Reader SHALL use asyncio.gather() to read all files concurrently using aiofiles.open()
4. WHEN reading a file, THE Parallel_File_Reader SHALL skip files larger than max_size_per_file parameter (default 1024KB = 1MB)
5. WHEN reading a file, THE Parallel_File_Reader SHALL detect language based on file extension using the same mapping as scan_codebase
6. WHEN reading a file, THE Parallel_File_Reader SHALL generate a SHA-256 hash of the content for cache validation
7. WHEN reading completes, THE Parallel_File_Reader SHALL return an array of FileContent objects with fields: path, content, size (bytes), lines (count), language, and hash
8. WHEN use_cache is true and a file exists in cache with matching hash, THE Parallel_File_Reader SHALL return cached content without reading from disk
9. WHEN reading completes, THE Parallel_File_Reader SHALL cache all file contents using cache_manager.set_file() with ttl=3600 seconds
10. WHEN reading 10 files in parallel, THE Parallel_File_Reader SHALL complete in under 1 second (vs 10 seconds sequential)
11. WHEN a file read fails due to permissions or encoding errors, THE Parallel_File_Reader SHALL skip the file and include an error entry in the results with error message
12. WHEN patterns include glob patterns like "src/**/*.tsx", THE Parallel_File_Reader SHALL recursively match all TypeScript React files in the src directory tree

---

### Requirement 12: Progressive Discovery Pattern (Context Management)

**User Story:** As an AI assistant, I want to use progressive discovery with minimal cache structure, so that I can analyze large codebases without exceeding context limits by analyzing features incrementally and caching results.

#### Acceptance Criteria

1. WHEN scan_codebase completes, THE Session_Manager SHALL create a discovery_cache object with fields: timestamp, project_path, structure (total_files, main_directories, likely_framework, entry_points_to_check), progress (phase, files_read, features_discovered), and next_steps array
2. WHEN discover_features completes, THE Session_Manager SHALL update the discovery_cache with features array containing objects with fields: name, category, files, priority (high/medium/low), and status (not_analyzed/analyzed)
3. WHEN analyzing a feature, THE Session_Manager SHALL track which files have been read to avoid re-reading the same files
4. WHEN session state is stored, THE Session_Manager SHALL include metadata: project_name, analyzed_at timestamp, total_files, files_analyzed, and progress percentage
5. WHEN session state is stored, THE Session_Manager SHALL include next_actions array with recommended next steps for the AI assistant
6. WHEN a tool retrieves session state, THE Session_Manager SHALL return the minimal cache structure (under 5KB) to avoid consuming excessive context
7. WHEN features are prioritized, THE Session_Manager SHALL assign priority based on: entry points (high), core features (high), well-tested code (high), utilities (medium), helpers (low), edge cases (low)
8. WHEN the AI assistant completes analyzing a feature, THE Session_Manager SHALL mark the feature status as "analyzed" and increment files_analyzed counter
9. WHEN the AI assistant requests next actions, THE Session_Manager SHALL return the highest priority unanalyzed feature from the discovery_cache
10. WHEN session state exceeds 1 hour of inactivity, THE Session_Manager SHALL mark the session as stale but retain the cache for future use

---

### Requirement 13: MCP Resources Implementation

**User Story:** As an AI assistant, I want to access cached analysis results through MCP resources using URI patterns, so that I can retrieve codebase structure and feature data instantly without re-running tools.

#### Acceptance Criteria

1. WHEN an AI client requests resource codebase://structure, THE MCP_Server SHALL return the cached scan result from cache_manager.get_resource("structure") in JSON format
2. WHEN an AI client requests resource codebase://features, THE MCP_Server SHALL return the cached features list from cache_manager.get_resource("features") in JSON format
3. WHEN the resource does not exist in cache, THE MCP_Server SHALL return an error with message "Resource not available. Run scan_codebase first."
4. WHEN a resource is accessed, THE MCP_Server SHALL return the data with mimeType "application/json"
5. WHEN scan_codebase completes, THE MCP_Server SHALL automatically store the result as resource "structure" using cache_manager.set_resource()
6. WHEN discover_features completes, THE MCP_Server SHALL automatically store the result as resource "features" using cache_manager.set_resource()
7. WHEN a resource is accessed, THE MCP_Server SHALL log at DEBUG level: "Resource accessed: {uri}"
8. WHEN resources are listed, THE MCP_Server SHALL return 2 resource definitions with uri, name, description, and mimeType fields

---

### Requirement 14: MCP Prompts Implementation

**User Story:** As an AI assistant, I want to use prompt templates that guide me through common workflows, so that I follow best practices for codebase analysis and progressive discovery.

#### Acceptance Criteria

1. WHEN an AI client requests prompt analyze_codebase with argument codebase_path, THE MCP_Server SHALL return a template string with steps: "1. Call scan_codebase to get structure, 2. Call detect_frameworks to identify tech stack, 3. Call discover_features to find teachable code, 4. Focus on finding code that teaches well"
2. WHEN the prompt template is returned, THE MCP_Server SHALL include the codebase_path argument value in the template text
3. WHEN prompts are listed, THE MCP_Server SHALL return 1 prompt definition with name "analyze_codebase", description "Template for initial codebase analysis", and arguments array with codebase_path (required=true)
4. WHEN a prompt is requested, THE MCP_Server SHALL log at DEBUG level: "Prompt requested: {prompt_name} with arguments: {arguments}"
5. WHEN the analyze_codebase prompt is used, THE MCP_Server SHALL guide the AI through the progressive discovery workflow: initial scan → framework detection → feature discovery → prioritization

---

### Requirement 15: Performance Benchmarking and Validation

**User Story:** As a developer, I want to validate that the MCP server achieves God Mode performance targets, so that I can verify 20x speedup, 99% accuracy, and 70%+ cache hit rate are met.

#### Acceptance Criteria

1. WHEN scan_codebase analyzes a codebase with 1000 files, THE MCP_Server SHALL complete in under 3000ms on first run
2. WHEN scan_codebase analyzes a previously scanned codebase with cache enabled, THE MCP_Server SHALL complete in under 100ms
3. WHEN detect_frameworks analyzes a JavaScript project with package.json, THE MCP_Server SHALL achieve 99% confidence score for frameworks listed in dependencies
4. WHEN the cache hit rate is calculated after 10 tool calls, THE Cache_Manager SHALL achieve at least 70% hit rate
5. WHEN read_files_parallel reads 10 files, THE Parallel_File_Reader SHALL complete at least 6x faster than sequential reading (target: 10x)
6. WHEN a complete analysis workflow is executed (scan → detect → discover), THE MCP_Server SHALL complete in under 15 seconds total (vs 100+ seconds without MCP)
7. WHEN performance metrics are logged, THE Logging_System SHALL include actual vs target times for comparison
8. WHEN a performance target is not met, THE Logging_System SHALL log at WARNING level: "Performance target missed: {operation} took {actual_ms}ms (target: {target_ms}ms)"
9. WHEN the server runs performance benchmarks, THE MCP_Server SHALL track and report: scan_time_ms, cache_hit_rate, parallel_speedup_factor, and total_workflow_time_ms
10. WHEN accuracy is measured for framework detection, THE MCP_Server SHALL achieve at least 95% accuracy on a test set of 20 diverse codebases
