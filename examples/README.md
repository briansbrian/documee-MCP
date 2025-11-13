# Analysis Engine Examples

This directory contains comprehensive examples demonstrating how to use the Analysis Engine.

## Quick Start

All examples can be run directly:

```bash
# Windows
.\venv\Scripts\python.exe examples/analyze_single_file_example.py

# Linux/Mac
python examples/analyze_single_file_example.py
```

## Available Examples

### 1. Analyze Single File
**File:** `analyze_single_file_example.py`

Demonstrates how to analyze a single code file.

**What you'll learn:**
- Initialize the Analysis Engine
- Analyze a Python file
- Access symbol information (functions, classes)
- View detected patterns
- Check teaching value scores
- Understand complexity metrics
- Force re-analysis (bypass cache)
- Analyze different file types (JavaScript, TypeScript)

**Run it:**
```bash
.\venv\Scripts\python.exe examples/analyze_single_file_example.py
```

---

### 2. Analyze Entire Codebase
**File:** `analyze_codebase_example.py`

Demonstrates how to analyze an entire codebase with parallel processing.

**What you'll learn:**
- Scan a codebase first
- Perform full codebase analysis
- Use incremental analysis for speed
- View top teaching files
- Explore global patterns
- Analyze dependency graphs
- Detect circular dependencies
- View external dependencies
- Explore specific file details

**Run it:**
```bash
.\venv\Scripts\python.exe examples/analyze_codebase_example.py
```

---

### 3. Incremental Analysis
**File:** `incremental_analysis_example.py`

Demonstrates how incremental analysis dramatically speeds up repeated analysis.

**What you'll learn:**
- How file hashing works
- Initial full analysis
- Re-analysis without changes (450x faster!)
- Re-analysis with one file modified
- Re-analysis with new files added
- Performance comparisons
- Cache hit rates

**Run it:**
```bash
.\venv\Scripts\python.exe examples/incremental_analysis_example.py
```

**Expected output:**
```
Initial full analysis: 2.5s
No changes (cached): 0.005s (500x faster)
One file modified: 0.3s (8x faster)
One file added: 0.4s (6x faster)
```

---

### 4. Custom Pattern Detector
**File:** `custom_pattern_detector_example.py`

Demonstrates how to create and register custom pattern detectors.

**What you'll learn:**
- Extend BasePatternDetector
- Implement custom detection logic
- Assign confidence scores
- Provide evidence for detections
- Register custom detectors
- Integrate with the engine

**Example detectors:**
- ErrorHandlingPatternDetector (try-except, custom exceptions, logging)
- PerformancePatternDetector (caching, async/await, lazy loading)

**Run it:**
```bash
.\venv\Scripts\python.exe examples/custom_pattern_detector_example.py
```

---

### 5. MCP Tools Usage
**File:** `mcp_tools_usage_example.py`

Demonstrates how AI assistants interact with the Analysis Engine through MCP tools.

**What you'll learn:**
- How MCP tools work
- analyze_file tool
- score_teaching_value tool
- detect_patterns tool
- analyze_dependencies tool
- Typical AI workflow
- Integration with Claude Desktop

**Run it:**
```bash
.\venv\Scripts\python.exe examples/mcp_tools_usage_example.py
```

---

## Existing Examples

The following examples were created during development and are also available:

### AST Parser
- `ast_parser_example.py` - Basic AST parsing
- `test_symbol_extraction.py` - Symbol extraction testing
- `test_js_extraction.py` - JavaScript symbol extraction
- `test_multi_lang.py` - Multi-language support
- `test_all_languages.py` - All language testing

### Analysis Components
- `complexity_analyzer_example.py` - Complexity analysis
- `dependency_analyzer_example.py` - Dependency analysis
- `documentation_coverage_example.py` - Documentation coverage
- `pattern_detector_example.py` - Pattern detection
- `linter_integration_example.py` - Linter integration

### Other Tools
- `course_generator_example.py` - Course generation
- `metadata_generator_example.py` - Metadata generation
- `mkdocs_export_example.py` - MkDocs export
- `logging_example.py` - Logging configuration

---

## Example Workflow

Here's a typical workflow using the examples:

### 1. Start with Single File Analysis
```bash
.\venv\Scripts\python.exe examples/analyze_single_file_example.py
```
Learn the basics of file analysis.

### 2. Scale to Codebase Analysis
```bash
.\venv\Scripts\python.exe examples/analyze_codebase_example.py
```
Understand how to analyze entire projects.

### 3. Optimize with Incremental Analysis
```bash
.\venv\Scripts\python.exe examples/incremental_analysis_example.py
```
See the performance benefits of incremental updates.

### 4. Extend with Custom Patterns
```bash
.\venv\Scripts\python.exe examples/custom_pattern_detector_example.py
```
Learn how to add your own pattern detectors.

### 5. Integrate with MCP
```bash
.\venv\Scripts\python.exe examples/mcp_tools_usage_example.py
```
Understand how AI assistants use the engine.

---

## Common Patterns

### Initialize the Engine

```python
from src.analysis import AnalysisEngine, AnalysisConfig
from src.cache import CacheManager

config = AnalysisConfig()
cache = CacheManager()
engine = AnalysisEngine(cache, config)
```

### Analyze a File

```python
result = await engine.analyze_file("path/to/file.py")

print(f"Functions: {len(result.symbol_info.functions)}")
print(f"Teaching value: {result.teaching_value.total_score:.2f}")
print(f"Patterns: {[p.pattern_type for p in result.patterns]}")
```

### Analyze a Codebase

```python
from src.tools.scan_codebase import scan_codebase

# Scan first
scan_result = await scan_codebase("/path/to/code")
cache.set(f"scan:{scan_result.codebase_id}", scan_result)

# Then analyze
analysis = await engine.analyze_codebase(
    scan_result.codebase_id,
    incremental=True
)

print(f"Files: {analysis.metrics.total_files}")
print(f"Top file: {analysis.top_teaching_files[0]}")
```

### Custom Pattern Detector

```python
from src.analysis.pattern_detector import BasePatternDetector, DetectedPattern

class MyDetector(BasePatternDetector):
    def detect(self, symbol_info, file_content, file_path):
        patterns = []
        # Your logic here
        return patterns

# Register
engine.pattern_detector.register_detector(MyDetector())
```

---

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the project root:

```bash
# Wrong (from examples directory)
cd examples
python analyze_single_file_example.py  # ❌ Import error

# Correct (from project root)
python examples/analyze_single_file_example.py  # ✅ Works
```

### Virtual Environment

Always use the virtual environment:

```bash
# Windows
.\venv\Scripts\python.exe examples/example.py

# Linux/Mac
./venv/bin/python examples/example.py
```

### Missing Dependencies

If you get module not found errors:

```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Next Steps

After exploring the examples:

1. **Read the documentation:**
   - [Configuration Guide](../docs/ANALYSIS_ENGINE_CONFIGURATION.md)
   - [API Documentation](../docs/ANALYSIS_ENGINE_API.md)
   - [Design Document](../.kiro/specs/analysis-engine/design.md)

2. **Try on your own code:**
   ```python
   result = await engine.analyze_file("your_file.py")
   ```

3. **Create custom detectors:**
   - Extend BasePatternDetector
   - Implement your detection logic
   - Register with the engine

4. **Integrate with MCP:**
   - Configure MCP server
   - Test with MCP Inspector
   - Use with Claude Desktop

---

## Contributing

Found a bug or have an idea for a new example? Contributions welcome!

---

**Last Updated:** November 13, 2025
