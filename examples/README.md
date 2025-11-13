# Analysis Engine & MCP Server Examples

This directory contains comprehensive examples demonstrating how to use the Analysis Engine and MCP Server.

## Quick Start

All examples can be run directly:

```bash
# Windows
.\venv\Scripts\python.exe examples/analyze_single_file_example.py

# Linux/Mac
python examples/analyze_single_file_example.py
```

## MCP Server Examples

### Basic MCP Client Usage
**File:** `basic_usage.py`

Demonstrates how to use the MCP client to interact with the codebase-to-course-mcp server.

**What you'll learn:**
- Connect to MCP server via stdio
- Call all 3 core discovery tools (scan_codebase, detect_frameworks, discover_features)
- Access MCP resources (codebase://structure, codebase://features)
- Use MCP prompts (analyze_codebase)
- Complete workflow from scan to feature discovery

**Run it:**
```bash
.\venv\Scripts\python.exe examples/basic_usage.py
```

**Expected output:**
```
✓ Connected to MCP server
✓ Available tools: 3
✓ Scan completed in 2500.00ms
  Codebase ID: a1b2c3d4e5f6g7h8
  Total Files: 150
  Primary Language: Python
✓ Detected 3 frameworks
  - FastAPI v0.104.1 (Confidence: 95.00%)
✓ Discovered 12 features
  Categories: routes, api, utils
✓ All tools executed successfully!
```

### Configuration Files

#### Kiro Integration
**File:** `kiro_config.json`

Configuration for integrating the MCP server with Kiro IDE.

**Usage:**
1. Copy to `.kiro/settings/mcp.json` in your workspace
2. Update the `cwd` path to your project directory
3. Restart Kiro or reconnect MCP servers
4. Tools will be available in Kiro's MCP panel

**Features:**
- Auto-approve for all 3 tools (faster workflow)
- Environment variable configuration
- Custom cache and file size limits

#### Claude Desktop Integration
**File:** `claude_config.json`

Configuration for integrating the MCP server with Claude Desktop.

**Usage:**
1. Open Claude Desktop settings
2. Navigate to "Developer" → "Edit Config"
3. Add the server configuration from this file
4. Update the `cwd` path to your project directory
5. Restart Claude Desktop
6. Tools will be available in Claude's tool menu

**Note:** Claude Desktop doesn't support `autoApprove`, so you'll need to approve each tool call.

## Testing Methods

### Method 1: MCP Inspector (Recommended for Development)

The MCP Inspector is the official testing tool from Anthropic.

**Install:**
```bash
npm install -g @modelcontextprotocol/inspector
```

**Run:**
```bash
npx @modelcontextprotocol/inspector python -m src.server
```

**Features:**
- Interactive web UI at http://localhost:5173
- Test all tools with custom parameters
- View tool schemas and descriptions
- Test resources and prompts
- See real-time request/response logs
- Validate JSON schemas

**Example test cases:**
```json
// Test scan_codebase
{
  "path": ".",
  "max_depth": 5,
  "use_cache": true
}

// Test detect_frameworks
{
  "codebase_id": "a1b2c3d4e5f6g7h8",
  "confidence_threshold": 0.7,
  "use_cache": true
}

// Test discover_features
{
  "codebase_id": "a1b2c3d4e5f6g7h8",
  "categories": ["routes", "api"],
  "use_cache": true
}
```

### Method 2: Development Mode (Auto-reload)

Use FastMCP's development mode for rapid iteration.

**Install uv (if not installed):**
```bash
pip install uv
```

**Run:**
```bash
uv run mcp dev src/server.py
```

**Features:**
- Auto-reload on file changes
- Faster development cycle
- Same functionality as production
- Useful for testing changes quickly

### Method 3: Direct Run (Production Mode)

Run the server directly for production testing.

**Run:**
```bash
python -m src.server
```

**Features:**
- Production-ready mode
- Stdio transport (default)
- Used by AI clients (Claude, Kiro)
- No auto-reload

**Test with client:**
```bash
.\venv\Scripts\python.exe examples/basic_usage.py
```

### Method 4: Integration Testing

Test the server with actual AI clients.

**Kiro:**
1. Add config to `.kiro/settings/mcp.json`
2. Restart Kiro
3. Open MCP panel
4. Test tools interactively

**Claude Desktop:**
1. Add config to Claude settings
2. Restart Claude Desktop
3. Start a conversation
4. Ask Claude to use the tools

**Example prompts:**
- "Scan the current codebase and tell me what you find"
- "What frameworks are being used in this project?"
- "Discover all the API endpoints in this codebase"

## Example Tool Calls with Expected Responses

### 1. scan_codebase

**Request:**
```json
{
  "path": ".",
  "max_depth": 10,
  "use_cache": true
}
```

**Response:**
```json
{
  "codebase_id": "a1b2c3d4e5f6g7h8",
  "structure": {
    "total_files": 150,
    "total_directories": 25,
    "total_size_mb": 5.2,
    "languages": {
      "Python": 120,
      "JavaScript": 20,
      "TypeScript": 10
    },
    "file_types": {
      ".py": 120,
      ".js": 15,
      ".ts": 10,
      ".jsx": 5
    }
  },
  "summary": {
    "primary_language": "Python",
    "project_type": "python-application",
    "has_tests": true,
    "size_category": "medium"
  },
  "scan_time_ms": 2500.0,
  "from_cache": false
}
```

### 2. detect_frameworks

**Request:**
```json
{
  "codebase_id": "a1b2c3d4e5f6g7h8",
  "confidence_threshold": 0.7,
  "use_cache": true
}
```

**Response:**
```json
{
  "frameworks": [
    {
      "name": "FastAPI",
      "version": "0.104.1",
      "confidence": 0.95,
      "evidence": ["requirements.txt dependency"]
    },
    {
      "name": "Pytest",
      "version": "7.4.3",
      "confidence": 0.95,
      "evidence": ["requirements.txt dependency"]
    },
    {
      "name": "React",
      "version": "18.2.0",
      "confidence": 0.99,
      "evidence": ["package.json dependency"]
    }
  ],
  "total_detected": 3,
  "confidence_threshold": 0.7,
  "from_cache": false
}
```

### 3. discover_features

**Request:**
```json
{
  "codebase_id": "a1b2c3d4e5f6g7h8",
  "categories": ["all"],
  "use_cache": true
}
```

**Response:**
```json
{
  "features": [
    {
      "id": "f1a2b3c4d5e6f7g8",
      "name": "api",
      "category": "api",
      "path": "/absolute/path/to/src/api",
      "priority": "high"
    },
    {
      "id": "g2h3i4j5k6l7m8n9",
      "name": "components",
      "category": "components",
      "path": "/absolute/path/to/src/components",
      "priority": "medium"
    },
    {
      "id": "h3i4j5k6l7m8n9o0",
      "name": "utils",
      "category": "utils",
      "path": "/absolute/path/to/src/utils",
      "priority": "medium"
    }
  ],
  "total_features": 3,
  "categories": ["api", "components", "utils"],
  "from_cache": false
}
```

### 4. Resource: codebase://structure

**Request:**
```
GET codebase://structure
```

**Response:**
```json
{
  "uri": "codebase://structure",
  "mimeType": "application/json",
  "text": "{\"codebase_id\":\"a1b2c3d4e5f6g7h8\",\"structure\":{...}}"
}
```

### 5. Resource: codebase://features

**Request:**
```
GET codebase://features
```

**Response:**
```json
{
  "uri": "codebase://features",
  "mimeType": "application/json",
  "text": "{\"features\":[...],\"total_features\":3}"
}
```

### 6. Prompt: analyze_codebase

**Request:**
```json
{
  "name": "analyze_codebase",
  "arguments": {
    "codebase_path": "."
  }
}
```

**Response:**
```
Please analyze the codebase at: .

Steps:
1. Call scan_codebase to get structure
2. Call detect_frameworks to identify tech stack
3. Call discover_features to find teachable code
4. Focus on finding code that teaches well
```

## Analysis Engine Examples

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
