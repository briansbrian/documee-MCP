# Analysis Engine Configuration Guide

This document provides comprehensive documentation for all configuration options available in the Analysis Engine.

## Table of Contents

- [Configuration File](#configuration-file)
- [Analysis Settings](#analysis-settings)
- [Supported Languages](#supported-languages)
- [Teaching Value Weights](#teaching-value-weights)
- [Performance Settings](#performance-settings)
- [Incremental Analysis](#incremental-analysis)
- [Linter Integration](#linter-integration)
- [Pattern Detector Plugins](#pattern-detector-plugins)
- [Jupyter Notebook Support](#jupyter-notebook-support)
- [Environment Variables](#environment-variables)
- [Examples](#examples)

---

## Configuration File

The Analysis Engine uses `config.yaml` for configuration. The file is located in the project root directory.

### Default Location

```
project-root/
├── config.yaml          # Main configuration file
├── src/
└── ...
```

### Loading Configuration

```python
from src.config import load_config

config = load_config()
analysis_config = config.analysis
```

---

## Analysis Settings

### Core Settings

```yaml
analysis:
  # Maximum file size to analyze (in MB)
  max_file_size_mb: 10
  
  # Maximum number of files to scan in one operation
  max_files_per_scan: 10000
  
  # Maximum parallel file reads
  max_parallel_reads: 10
  
  # Timeout for scan operations (in seconds)
  scan_timeout_seconds: 30
```

#### Options Explained

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_file_size_mb` | int | 10 | Files larger than this are skipped to prevent memory issues |
| `max_files_per_scan` | int | 10000 | Maximum files to process in a single scan operation |
| `max_parallel_reads` | int | 10 | Number of files to read concurrently |
| `scan_timeout_seconds` | int | 30 | Maximum time allowed for scan operations |

### Complexity Thresholds

```yaml
analysis:
  # Maximum acceptable cyclomatic complexity
  max_complexity_threshold: 10
  
  # Minimum complexity (below this is "trivial")
  min_complexity_threshold: 2
```

#### Complexity Scoring

- **Trivial** (< 2): Very simple code, may not be interesting for teaching
- **Ideal** (2-10): Good balance of simplicity and real-world complexity
- **High** (> 10): Complex code that may be overwhelming for learners

### Documentation Coverage

```yaml
analysis:
  # Minimum acceptable documentation coverage (0.0-1.0)
  min_documentation_coverage: 0.5
```

- **0.0**: No documentation required
- **0.5**: At least 50% of functions should have docstrings
- **1.0**: All functions must be documented

---

## Supported Languages

The Analysis Engine supports 50+ languages through tree-sitter-languages. Configure which languages to analyze:

```yaml
analysis:
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
```

### Available Languages

#### Tier 1: Fully Supported (Complete AST parsing + Symbol extraction)

- **Python** (.py, .pyw)
- **JavaScript** (.js, .jsx, .mjs)
- **TypeScript** (.ts, .tsx)
- **Java** (.java)
- **Go** (.go)
- **Rust** (.rs)
- **C++** (.cpp, .cc, .cxx, .hpp, .h)
- **C#** (.cs)
- **Ruby** (.rb)
- **PHP** (.php)

#### Tier 2: Parsing Supported (AST parsing only)

- Scala, Kotlin, Swift, Dart
- Elixir, Haskell, Clojure
- Bash, PowerShell
- HTML, CSS, JSON, YAML, TOML
- SQL, GraphQL
- And 30+ more...

### Language Detection

File extensions are automatically mapped to languages:

```python
# Automatic detection
.py   → python
.js   → javascript
.ts   → typescript
.java → java
.go   → go
.rs   → rust
.cpp  → cpp
.cs   → c_sharp
.rb   → ruby
.php  → php
```

### Adding New Languages

To add support for a new language:

1. Add to `supported_languages` in config.yaml
2. Ensure tree-sitter-languages supports it
3. Optionally add symbol extraction patterns

```yaml
analysis:
  supported_languages:
    - python
    - javascript
    - your_new_language  # Add here
```

---

## Teaching Value Weights

Configure how teaching value is calculated:

```yaml
analysis:
  teaching_value_weights:
    documentation: 0.3    # 30% weight
    complexity: 0.25      # 25% weight
    pattern: 0.25         # 25% weight
    structure: 0.2        # 20% weight
```

### Weight Factors

#### Documentation (default: 0.3)

- Measures docstring/comment coverage
- Higher weight prioritizes well-documented code
- Range: 0.0 (no docs) to 1.0 (fully documented)

#### Complexity (default: 0.25)

- Measures cyclomatic complexity
- Prefers moderate complexity (not too simple, not too complex)
- Sweet spot: 3-7 complexity
- Range: 0.0 (trivial or overwhelming) to 1.0 (ideal complexity)

#### Pattern (default: 0.25)

- Measures usage of common patterns
- Higher score for files with recognized patterns
- Examples: React hooks, API routes, ORM models
- Range: 0.0 (no patterns) to 1.0 (many patterns)

#### Structure (default: 0.2)

- Measures code organization and clarity
- Considers: consistent naming, separation of concerns, file size
- Range: 0.0 (poor structure) to 1.0 (excellent structure)

### Customizing Weights

**For documentation-focused courses:**
```yaml
teaching_value_weights:
  documentation: 0.5    # Prioritize well-documented code
  complexity: 0.2
  pattern: 0.2
  structure: 0.1
```

**For pattern-focused courses:**
```yaml
teaching_value_weights:
  documentation: 0.2
  complexity: 0.2
  pattern: 0.4          # Prioritize pattern usage
  structure: 0.2
```

**For beginner-friendly courses:**
```yaml
teaching_value_weights:
  documentation: 0.3
  complexity: 0.4       # Prioritize simple code
  pattern: 0.1
  structure: 0.2
```

---

## Performance Settings

### Parallel Processing

```yaml
analysis:
  # Number of files to analyze concurrently
  max_parallel_files: 10
  
  # Timeout for parsing a single file (in seconds)
  parse_timeout_seconds: 5
```

#### Tuning for Performance

**For fast machines (8+ cores):**
```yaml
max_parallel_files: 20
```

**For slower machines (2-4 cores):**
```yaml
max_parallel_files: 5
```

**For very large files:**
```yaml
parse_timeout_seconds: 10
```

### Caching

```yaml
analysis:
  # Cache TTL in seconds (1 hour = 3600)
  cache_ttl_seconds: 3600
```

#### Cache Behavior

- **Memory Cache**: Instant access, limited by `max_size_mb`
- **SQLite Cache**: Persistent across restarts
- **Redis Cache**: Optional distributed cache

**Adjust TTL based on usage:**
- Development: 300 (5 minutes) - frequent changes
- Production: 7200 (2 hours) - stable code
- CI/CD: 0 (disabled) - always fresh analysis

---

## Incremental Analysis

Incremental analysis only re-analyzes changed files, dramatically improving performance.

```yaml
analysis:
  # Enable incremental analysis
  enable_incremental: true
  
  # Directory for storing analysis results
  persistence_path: ".documee/analysis"
```

### How It Works

1. **First Run**: Analyzes all files, stores hashes
2. **Subsequent Runs**: Compares file hashes
3. **Changed Files**: Re-analyzes only modified files
4. **Unchanged Files**: Uses cached results

### Performance Impact

| Scenario | Without Incremental | With Incremental | Speedup |
|----------|---------------------|------------------|---------|
| No changes | 45s | 0.1s | 450x |
| 1 file changed | 45s | 2s | 22x |
| 10% changed | 45s | 8s | 5.6x |

### Storage Location

Analysis results are stored in:
```
.documee/analysis/
├── {codebase_id}/
│   ├── analysis.json          # Main analysis results
│   ├── file_hashes.json       # File hash tracking
│   └── file_*.json            # Individual file analyses
```

### Disabling Incremental Analysis

```yaml
analysis:
  enable_incremental: false
```

Use when:
- Testing analysis changes
- Debugging issues
- First-time setup

---

## Linter Integration

Integrate external linters (pylint, eslint) for additional code quality insights.

```yaml
analysis:
  # Enable linter integration
  enable_linters: true
  
  # Linter configuration per language
  linters:
    python: pylint
    javascript: eslint
    typescript: eslint
```

### Supported Linters

#### Python: pylint

```bash
# Install
pip install pylint

# Configure (optional)
# Create .pylintrc in project root
```

#### JavaScript/TypeScript: eslint

```bash
# Install
npm install -g eslint

# Configure (optional)
# Create .eslintrc.json in project root
```

### Linter Behavior

- **Non-blocking**: Linter failures don't stop analysis
- **Async**: Runs in parallel with other analysis
- **Optional**: Can be disabled without affecting core analysis

### Disabling Linters

```yaml
analysis:
  enable_linters: false
```

Use when:
- Linters not installed
- Performance is critical
- Linter output not needed

### Linter Output

Linter issues are included in analysis results:

```python
file_analysis.linter_issues = [
    LinterIssue(
        tool='pylint',
        severity='warning',
        message='Line too long (85/80)',
        line=42,
        column=80,
        rule='C0301'
    )
]
```

---

## Pattern Detector Plugins

The Analysis Engine uses a plugin architecture for pattern detection. Configure which detectors to use:

```yaml
analysis:
  pattern_detectors:
    - ReactPatternDetector
    - APIPatternDetector
    - DatabasePatternDetector
    - AuthPatternDetector
    - PythonPatternDetector
    - JavaScriptPatternDetector
    # Add custom detectors here
```

### Built-in Detectors

#### Framework Detectors

1. **ReactPatternDetector**
   - Detects: Functional components, hooks, JSX
   - Languages: JavaScript, TypeScript
   - Confidence: 0.8-0.99

2. **APIPatternDetector**
   - Detects: Express routes, FastAPI endpoints, Next.js API routes
   - Languages: JavaScript, TypeScript, Python
   - Confidence: 0.85-0.95

3. **DatabasePatternDetector**
   - Detects: ORM models, query builders, migrations
   - Languages: Python, JavaScript, TypeScript
   - Confidence: 0.8-0.95

4. **AuthPatternDetector**
   - Detects: JWT, OAuth, session-based auth
   - Languages: All
   - Confidence: 0.75-0.9

#### Language-Specific Detectors

5. **PythonPatternDetector**
   - Detects: Decorators, context managers, generators, comprehensions
   - Language: Python
   - Confidence: 0.85-0.95

6. **JavaScriptPatternDetector**
   - Detects: Promises, async/await, arrow functions, destructuring
   - Languages: JavaScript, TypeScript
   - Confidence: 0.8-0.95

7. **JavaPatternDetector**
   - Detects: Annotations, streams, generics
   - Language: Java
   - Confidence: 0.8-0.9

8. **GoPatternDetector**
   - Detects: Goroutines, channels, defer
   - Language: Go
   - Confidence: 0.85-0.95

9. **RustPatternDetector**
   - Detects: Lifetimes, traits, macros
   - Language: Rust
   - Confidence: 0.8-0.9

### Creating Custom Detectors

See [examples/custom_pattern_detector_example.py](../examples/custom_pattern_detector_example.py) for a complete guide.

**Basic structure:**

```python
from src.analysis.pattern_detector import BasePatternDetector, DetectedPattern

class MyCustomDetector(BasePatternDetector):
    def detect(self, symbol_info, file_content, file_path):
        patterns = []
        
        # Your detection logic here
        if self._detect_my_pattern(file_content):
            patterns.append(DetectedPattern(
                pattern_type="my_custom_pattern",
                file_path=file_path,
                confidence=0.9,
                evidence=["Found pattern X", "Found pattern Y"],
                line_numbers=[10, 20],
                metadata={"key": "value"}
            ))
        
        return patterns
```

**Register in config:**

```yaml
analysis:
  pattern_detectors:
    - ReactPatternDetector
    - MyCustomDetector  # Your custom detector
```

---

## Jupyter Notebook Support

Analyze Jupyter notebooks (.ipynb files) by extracting code cells.

```yaml
analysis:
  # Enable notebook analysis
  analyze_notebooks: true
```

### How It Works

1. **Parse .ipynb**: Read notebook as JSON
2. **Extract Code Cells**: Get only code cells (skip markdown)
3. **Concatenate**: Combine cells into single code string
4. **Analyze**: Run normal analysis on combined code
5. **Map Results**: Track which cell each result came from

### Notebook-Specific Features

- **Cell Boundaries**: Track line numbers per cell
- **Execution Count**: Include cell execution order
- **Cell Metadata**: Preserve cell-level metadata

### Example

```python
# Notebook with 3 code cells
Cell 1: import pandas as pd
Cell 2: df = pd.read_csv('data.csv')
Cell 3: df.head()

# Analysis treats as single file:
import pandas as pd
df = pd.read_csv('data.csv')
df.head()

# Results include cell mapping:
function_at_line_2 → Cell 2
```

### Disabling Notebook Support

```yaml
analysis:
  analyze_notebooks: false
```

---

## Environment Variables

Override configuration with environment variables:

```bash
# Analysis settings
export DOCUMEE_MAX_FILE_SIZE_MB=20
export DOCUMEE_MAX_PARALLEL_FILES=20
export DOCUMEE_CACHE_TTL_SECONDS=7200

# Linter settings
export DOCUMEE_ENABLE_LINTERS=false

# Incremental analysis
export DOCUMEE_ENABLE_INCREMENTAL=true
export DOCUMEE_PERSISTENCE_PATH="/custom/path"
```

### Priority Order

1. Environment variables (highest priority)
2. config.yaml
3. Default values (lowest priority)

---

## Examples

### Example 1: Development Configuration

Fast iteration, frequent changes:

```yaml
analysis:
  max_file_size_mb: 5
  max_parallel_files: 10
  cache_ttl_seconds: 300        # 5 minutes
  enable_incremental: true
  enable_linters: false          # Skip for speed
  
  supported_languages:
    - python
    - javascript
    - typescript
  
  teaching_value_weights:
    documentation: 0.3
    complexity: 0.3
    pattern: 0.2
    structure: 0.2
```

### Example 2: Production Configuration

Stable code, comprehensive analysis:

```yaml
analysis:
  max_file_size_mb: 10
  max_parallel_files: 20
  cache_ttl_seconds: 7200       # 2 hours
  enable_incremental: true
  enable_linters: true           # Full quality checks
  
  supported_languages:
    - python
    - javascript
    - typescript
    - java
    - go
    - rust
  
  teaching_value_weights:
    documentation: 0.35
    complexity: 0.25
    pattern: 0.25
    structure: 0.15
  
  pattern_detectors:
    - ReactPatternDetector
    - APIPatternDetector
    - DatabasePatternDetector
    - AuthPatternDetector
    - PythonPatternDetector
    - JavaScriptPatternDetector
```

### Example 3: Educational Focus

Prioritize teaching value:

```yaml
analysis:
  max_complexity_threshold: 7    # Lower threshold
  min_documentation_coverage: 0.7 # Higher requirement
  
  teaching_value_weights:
    documentation: 0.4            # Prioritize docs
    complexity: 0.3               # Prefer simpler code
    pattern: 0.2
    structure: 0.1
  
  enable_linters: true
  analyze_notebooks: true         # Include notebooks
```

### Example 4: Performance-Optimized

Maximum speed:

```yaml
analysis:
  max_parallel_files: 30          # High parallelism
  cache_ttl_seconds: 14400        # 4 hours
  enable_incremental: true
  enable_linters: false           # Skip linters
  
  supported_languages:
    - python                      # Only essential languages
    - javascript
  
  pattern_detectors:
    - ReactPatternDetector        # Only essential detectors
    - APIPatternDetector
```

---

## Troubleshooting

### Issue: Analysis is slow

**Solutions:**
1. Increase `max_parallel_files`
2. Enable `enable_incremental`
3. Disable `enable_linters`
4. Reduce `supported_languages` to only needed ones

### Issue: Out of memory

**Solutions:**
1. Decrease `max_file_size_mb`
2. Decrease `max_parallel_files`
3. Increase `cache_ttl_seconds` to reduce re-analysis

### Issue: Patterns not detected

**Solutions:**
1. Check `pattern_detectors` includes needed detectors
2. Verify file language is in `supported_languages`
3. Check pattern confidence thresholds

### Issue: Linter errors

**Solutions:**
1. Verify linters are installed (`pylint`, `eslint`)
2. Set `enable_linters: false` to disable
3. Check linter configuration files (.pylintrc, .eslintrc.json)

---

## See Also

- [Analysis Engine Design](../.kiro/specs/analysis-engine/design.md)
- [Usage Examples](../examples/)
- [API Documentation](ANALYSIS_ENGINE_API.md)
- [Performance Guide](PERFORMANCE-TESTING-GUIDE.md)

---

**Last Updated:** November 13, 2025
