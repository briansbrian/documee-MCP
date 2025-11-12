# Analysis Engine

The Analysis Engine is the intelligence layer of the Documee MCP Server that provides deep code analysis capabilities.

## Overview

This module transforms basic codebase scanning into meaningful analysis through:
- **AST Parsing**: Parse code files into Abstract Syntax Trees for 10+ languages
- **Symbol Extraction**: Extract functions, classes, and other code symbols
- **Pattern Detection**: Identify common coding patterns and architectural decisions
- **Dependency Analysis**: Map relationships between files and packages
- **Teaching Value Scoring**: Score files by their educational value

## Directory Structure

```
src/analysis/
├── __init__.py           # Module exports
├── config.py             # Configuration management
├── engine.py             # Main orchestrator
├── ast_parser.py         # AST Parser Manager (NEW)
├── verify_setup.py       # Setup verification script
└── README.md            # This file
```

## Setup Status

✓ **Task 1 Complete**: Project structure and dependencies set up
✓ **Task 2 Complete**: AST Parser Manager implemented

### Completed:
- Created `src/analysis/` directory structure
- Installed tree-sitter (v0.21.3) and tree-sitter-languages (v1.10.2)
- Installed nbformat (v5.9.0) for Jupyter notebook support
- Created `AnalysisConfig` class with configuration management
- Created `AnalysisEngine` stub class
- Updated `config.yaml` with analysis engine settings
- Updated `requirements.txt` with all dependencies
- **NEW**: Implemented `ASTParserManager` class with multi-language support
- **NEW**: Implemented `ParseResult` dataclass for parse results
- **NEW**: Added support for 10+ languages (Python, JS, TS, Java, Go, Rust, C++, C#, Ruby, PHP)
- **NEW**: Added error node detection and parse timing metrics
- **NEW**: Created example script demonstrating AST parser usage

### Configuration

The analysis engine is configured via `config.yaml`:

```yaml
analysis:
  # Language support
  supported_languages:
    - python
    - javascript
    - typescript
    - java
    - go
    - rust
    - cpp
    - c_sharp
    - ruby
    - php
  
  # Complexity thresholds
  max_complexity_threshold: 10
  min_complexity_threshold: 2
  
  # Documentation coverage
  min_documentation_coverage: 0.5
  
  # Teaching value weights
  teaching_value_weights:
    documentation: 0.3
    complexity: 0.25
    pattern: 0.25
    structure: 0.2
  
  # Performance settings
  max_parallel_files: 10
  parse_timeout_seconds: 5
  enable_linters: false
  cache_ttl_seconds: 3600
```

## Verification

Run the verification script to ensure everything is set up correctly:

```powershell
.\venv\Scripts\python.exe -m src.analysis.verify_setup
```

Expected output:
```
============================================================
Analysis Engine Setup Verification
============================================================

1. Verifying tree-sitter installation...
✓ tree-sitter installed correctly

2. Verifying nbformat installation...
✓ nbformat installed correctly

3. Verifying AnalysisConfig...
✓ AnalysisConfig loaded correctly

4. Verifying AnalysisEngine...
✓ AnalysisEngine loaded correctly

============================================================
✓ All verification checks passed!
============================================================
```

## Next Steps

The following components will be implemented in subsequent tasks:

1. ✓ ~~**AST Parser Manager** (Task 2) - Parse files using tree-sitter~~
2. **Symbol Extractor** (Task 3) - Extract functions and classes
3. **Complexity Analyzer** (Task 4) - Calculate code complexity
4. **Documentation Coverage Analyzer** (Task 5) - Measure documentation
5. **Pattern Detector** (Task 6) - Detect coding patterns
6. **Dependency Analyzer** (Task 7) - Analyze dependencies
7. **Teaching Value Scorer** (Task 8) - Score educational value
8. **Persistence Manager** (Task 9) - Save/load analysis results
9. **Linter Integration** (Task 10) - Integrate pylint/eslint
10. **Jupyter Notebook Support** (Task 11) - Analyze notebooks
11. **Analysis Engine Core** (Task 12) - Complete implementation
12. **MCP Tool Integration** (Task 13) - Expose via MCP tools

## Dependencies

- **tree-sitter** (0.21.3): Fast, incremental parsing library
- **tree-sitter-languages** (1.10.2): Pre-built language grammars for 50+ languages
- **nbformat** (5.9.0+): Jupyter notebook format support

## Usage

### Using the AST Parser Manager

```python
from src.analysis import ASTParserManager, AnalysisConfig

# Initialize the parser
config = AnalysisConfig()
parser = ASTParserManager(config)

# Parse a file
result = parser.parse_file("path/to/file.py")

# Access parse results
print(f"Language: {result.language}")
print(f"Root node: {result.root_node.type}")
print(f"Has errors: {result.has_errors}")
print(f"Parse time: {result.parse_time_ms}ms")

# Check if file is supported
if parser.is_supported_file("example.py"):
    result = parser.parse_file("example.py")

# Get supported languages
languages = parser.get_supported_languages()
print(f"Supported: {', '.join(languages)}")
```

### Using the Analysis Engine (Full Pipeline)

```python
from src.analysis import AnalysisEngine, AnalysisConfig
from src.cache import CacheManager

# Load configuration
config = AnalysisConfig.from_dict(config_dict)

# Initialize engine
cache_manager = CacheManager(config)
engine = AnalysisEngine(cache_manager, config)

# Analyze a file (to be implemented in later tasks)
# result = await engine.analyze_file("path/to/file.py")

# Analyze a codebase (to be implemented in later tasks)
# result = await engine.analyze_codebase("codebase_id")
```

### Example

See `examples/ast_parser_example.py` for a complete working example.

## Notes

- The engine uses tree-sitter for fast, incremental parsing
- All parsers are pre-built (no compilation needed)
- Configuration is loaded from `config.yaml`
- Results are cached for performance
- Supports incremental analysis (only analyze changed files)
