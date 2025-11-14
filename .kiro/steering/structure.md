# Project Structure

## Root Directory

```
documee-mcp/
├── src/                    # Source code
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Usage examples and configs
├── cache_db/               # SQLite cache storage
├── output/                 # Generated course exports
├── config.yaml             # Server configuration
├── requirements.txt        # Python dependencies
└── README.md              # Main documentation
```

## Source Code (`src/`)

**Server Entry Point**
- `server.py` - FastMCP server with all MCP tool definitions (11 tools, 2 resources, 1 prompt)

**Tools** (`src/tools/`)
- `scan_codebase.py` - Directory structure analysis
- `detect_frameworks.py` - Framework/library detection from package.json/requirements.txt
- `discover_features.py` - Feature discovery (routes, components, APIs, utils, hooks)

**Analysis Engine** (`src/analysis/`)
- `engine.py` - Main orchestrator coordinating all analysis components
- `config.py` - Analysis configuration settings
- `ast_parser.py` - Multi-language AST parsing with tree-sitter
- `symbol_extractor.py` - Extract functions, classes, imports, exports
- `pattern_detector.py` - Base pattern detection + React/API/Database/Auth detectors
- `language_pattern_detector.py` - Python and JavaScript specific patterns
- `universal_language_detectors.py` - Java, Go, Rust, C++, C#, Ruby, PHP patterns
- `dependency_analyzer.py` - Build dependency graphs, detect circular deps
- `teaching_value_scorer.py` - Score files for educational value (0.0-1.0)
- `complexity_analyzer.py` - Cyclomatic complexity and nesting depth
- `documentation_coverage.py` - Calculate documentation percentage
- `linter_integration.py` - Pylint/ESLint integration (optional)
- `notebook_analyzer.py` - Jupyter notebook support
- `persistence.py` - Save/load analysis results

**Course Generation** (`src/course/`)
- `config.py` - Course generation configuration (audience, focus, duration)
- `structure_generator.py` - Generate course outline with modules and lessons
- `content_generator.py` - Generate lesson content from file analysis
- `exercise_generator.py` - Create exercises with starter code, solutions, hints
- `exporters/` - Export to different formats (MkDocs, Next.js, JSON, Markdown, PDF)

**Caching** (`src/cache/`)
- `unified_cache.py` - 3-tier cache manager (Memory LRU, SQLite, Redis)

**Data Models** (`src/models/`)
- `schemas.py` or `analysis_models.py` - Dataclasses for all structured data
  - FileAnalysis, CodebaseAnalysis, SymbolInfo, DetectedPattern
  - ComplexityMetrics, TeachingValueScore, DependencyGraph
  - CourseOutline, Module, Lesson, Exercise

**Configuration** (`src/config/`)
- `settings.py` - Load config.yaml and environment variables

**Utilities** (`src/utils/`)
- `file_utils.py` - Async file operations
- `path_utils.py` - Path sanitization and validation

## Tests (`tests/`)

**Unit Tests**
- `test_cache.py` - Cache manager tests
- `test_scan_codebase.py` - Scanner tests
- `test_detect_frameworks.py` - Framework detection
- `test_discover_features.py` - Feature discovery
- `test_symbol_extractor.py` - Symbol extraction
- `test_pattern_detector.py` - Pattern detection
- `test_complexity_analyzer.py` - Complexity metrics
- `test_teaching_value_scorer.py` - Teaching value scoring

**Integration Tests**
- `test_analysis_engine_integration.py` - Full analysis workflow
- `test_mcp_tools_integration.py` - MCP tool integration
- `test_mcp_local.py` - Quick integration test script

**Performance Tests**
- `test_performance_validation.py` - Validate God Mode performance targets
- `test_cache_optimization.py` - Cache hit rate validation

## Documentation (`docs/`)

**Getting Started**
- `START_HERE.md` - Quick start guide (choose your path)
- `README.md` - Documentation index
- `LOCAL_TEST_GUIDE.md` - Testing instructions

**Status & Planning**
- `PROJECT_STATUS_AND_ROADMAP.md` - Current status and future plans
- `COURSE_GENERATOR_SPEC_COMPLETE.md` - Course generation specification

**Technical Docs**
- `ULTIMATE-MCP-SERVER.md` - Complete implementation guide
- `API_VERIFICATION_REPORT.md` - API verification results
- `UTILITIES.md` - Utility functions documentation

## Examples (`examples/`)

- `kiro_config.json` - Kiro IDE integration config
- `claude_config.json` - Claude Desktop integration config
- `basic_usage.py` - Basic MCP client example
- `*_example.py` - Various usage examples for different features

## Configuration Files

**Server Configuration** (`config.yaml`)
- Server settings (name, version, transport)
- Cache settings (memory, SQLite, Redis)
- Analysis settings (file size limits, parallel reads, timeouts)
- Security settings (allowed paths, blocked patterns)
- Performance settings (profiling, slow operation logging)
- Logging settings (level, file, rotation)

**MCP Integration**
- `.kiro/settings/mcp.json` - Kiro workspace config
- `~/.kiro/settings/mcp.json` - Kiro user-level config
- Claude Desktop config varies by OS

## Key Conventions

**Async/Await**
- All I/O operations are async (file reads, cache operations, analysis)
- Use `await` for all async functions
- FastMCP handles async tool execution automatically

**Dataclasses**
- All data structures use Python dataclasses with type hints
- Include `to_dict()` and `from_dict()` methods for JSON serialization
- Use Optional[] for nullable fields

**Error Handling**
- Raise ValueError for invalid input parameters
- Raise RuntimeError for server/initialization errors
- Log errors with context before raising
- Return error information in analysis results (don't fail silently)

**Caching Strategy**
- Check cache before expensive operations
- Use `use_cache` parameter to allow cache bypass
- Cache keys: `codebase:{id}`, `file:{hash}`, `analysis:{id}`
- TTL: 1 hour default, configurable

**Logging**
- Use module-level logger: `logger = logging.getLogger(__name__)`
- Log tool invocations with parameters
- Log completion with duration
- Log slow operations (>1000ms default threshold)
- Log cache hits/misses at DEBUG level

**Testing**
- Use pytest with async support
- Mock file system operations where appropriate
- Test both cached and non-cached paths
- Validate performance targets in benchmarks
