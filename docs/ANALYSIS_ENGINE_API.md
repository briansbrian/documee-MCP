# Analysis Engine API Documentation

Complete API reference for the Analysis Engine, including all public classes, methods, data models, error handling, and performance characteristics.

## Table of Contents

- [Core Classes](#core-classes)
- [Data Models](#data-models)
- [Public Methods](#public-methods)
- [Error Handling](#error-handling)
- [Performance Characteristics](#performance-characteristics)
- [Usage Examples](#usage-examples)

---

## Core Classes

### AnalysisEngine

Main orchestrator for code analysis operations.

```python
from src.analysis import AnalysisEngine, AnalysisConfig
from src.cache import CacheManager

class AnalysisEngine:
    """
    Main analysis engine that orchestrates all analysis components.
    
    Provides:
    - Single file analysis
    - Codebase-wide analysis
    - Incremental analysis (only changed files)
    - Parallel processing
    - Caching and persistence
    """
    
    def __init__(self, cache_manager: CacheManager, config: AnalysisConfig):
        """
        Initialize the analysis engine.
        
        Args:
            cache_manager: Cache manager for storing results
            config: Analysis configuration
        """
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `cache` | CacheManager | Cache manager instance |
| `config` | AnalysisConfig | Configuration settings |
| `parser` | ASTParserManager | AST parser for multiple languages |
| `symbol_extractor` | SymbolExtractor | Extracts functions and classes |
| `pattern_detector` | PatternDetector | Detects coding patterns |
| `dependency_analyzer` | DependencyAnalyzer | Analyzes dependencies |
| `teaching_value_scorer` | TeachingValueScorer | Scores teaching value |
| `complexity_analyzer` | ComplexityAnalyzer | Calculates complexity metrics |
| `persistence` | PersistenceManager | Manages disk storage |
| `linter` | LinterIntegration | Integrates external linters |
| `notebook_analyzer` | NotebookAnalyzer | Analyzes Jupyter notebooks |

---

### ASTParserManager

Manages tree-sitter parsers for multiple languages.

```python
from src.analysis import ASTParserManager, AnalysisConfig

class ASTParserManager:
    """
    Manages AST parsers for 50+ programming languages.
    
    Uses tree-sitter-languages for pre-built parser binaries.
    No compilation required!
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize parser manager.
        
        Args:
            config: Analysis configuration with supported languages
        """
```

**Methods:**

- `parse_file(file_path: str) -> ParseResult`
- `get_parser(language: str) -> Parser`
- `is_supported_file(file_path: str) -> bool`
- `get_supported_languages() -> List[str]`

---

### SymbolExtractor

Extracts functions, classes, and other symbols from AST.

```python
from src.analysis import SymbolExtractor

class SymbolExtractor:
    """
    Extracts symbols (functions, classes, imports) from parsed AST.
    
    Supports:
    - Python: functions, classes, decorators, docstrings
    - JavaScript/TypeScript: functions, classes, JSDoc
    - Java, Go, Rust, C++, C#, Ruby, PHP
    """
    
    def extract_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """
        Extract all symbols from parsed file.
        
        Args:
            parse_result: Result from ASTParserManager.parse_file()
            
        Returns:
            SymbolInfo with functions, classes, and imports
        """
```

---

### PatternDetector

Detects coding patterns and architectural decisions.

```python
from src.analysis import PatternDetector

class PatternDetector:
    """
    Orchestrates multiple pattern detectors.
    
    Built-in detectors:
    - ReactPatternDetector
    - APIPatternDetector
    - DatabasePatternDetector
    - AuthPatternDetector
    - PythonPatternDetector
    - JavaScriptPatternDetector
    - And 7 more language-specific detectors
    """
    
    def __init__(self):
        """Initialize with default detectors."""
    
    def register_detector(self, detector: BasePatternDetector):
        """
        Register a custom pattern detector.
        
        Args:
            detector: Custom detector extending BasePatternDetector
        """
    
    def detect_patterns_in_file(
        self,
        symbol_info: SymbolInfo,
        file_content: str,
        file_path: str
    ) -> List[DetectedPattern]:
        """
        Detect all patterns in a file.
        
        Args:
            symbol_info: Extracted symbols
            file_content: Raw file content
            file_path: Path to file
            
        Returns:
            List of detected patterns with confidence scores
        """
```

---

### TeachingValueScorer

Scores code files by educational value.

```python
from src.analysis import TeachingValueScorer, AnalysisConfig

class TeachingValueScorer:
    """
    Scores code files by teaching value (0.0-1.0).
    
    Factors:
    - Documentation coverage (35%)
    - Code complexity (25%)
    - Pattern usage (25%)
    - Code structure (15%)
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize scorer with configuration.
        
        Args:
            config: Configuration with teaching value weights
        """
    
    def score_file(
        self,
        symbol_info: SymbolInfo,
        patterns: List[DetectedPattern],
        complexity_metrics: ComplexityMetrics,
        doc_coverage: float
    ) -> TeachingValueScore:
        """
        Calculate teaching value score for a file.
        
        Args:
            symbol_info: Extracted symbols
            patterns: Detected patterns
            complexity_metrics: Complexity analysis
            doc_coverage: Documentation coverage (0.0-1.0)
            
        Returns:
            TeachingValueScore with breakdown and explanation
        """
```

---

## Data Models

### ParseResult

Result of parsing a file.

```python
@dataclass
class ParseResult:
    """Result of parsing a file with tree-sitter."""
    
    file_path: str              # Path to parsed file
    language: str               # Detected language
    tree: Any                   # tree-sitter Tree object
    root_node: Any              # tree-sitter Node object
    has_errors: bool            # True if syntax errors found
    error_nodes: List[Any]      # List of error nodes
    parse_time_ms: float        # Time taken to parse (ms)
```

---

### SymbolInfo

Extracted symbols from a file.

```python
@dataclass
class SymbolInfo:
    """Symbols extracted from a file."""
    
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)  # For JS/TS
```

---

### FunctionInfo

Information about a function.

```python
@dataclass
class FunctionInfo:
    """Information about a function."""
    
    name: str                           # Function name
    parameters: List[str]               # Parameter names
    return_type: Optional[str] = None   # Return type (if available)
    docstring: Optional[str] = None     # Docstring/JSDoc
    start_line: int = 0                 # Starting line number
    end_line: int = 0                   # Ending line number
    complexity: int = 1                 # Cyclomatic complexity
    is_async: bool = False              # True if async function
    decorators: List[str] = field(default_factory=list)  # Decorators
```

---

### ClassInfo

Information about a class.

```python
@dataclass
class ClassInfo:
    """Information about a class."""
    
    name: str                           # Class name
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None     # Class docstring
    start_line: int = 0                 # Starting line number
    end_line: int = 0                   # Ending line number
    decorators: List[str] = field(default_factory=list)
```

---

### DetectedPattern

A detected coding pattern.

```python
@dataclass
class DetectedPattern:
    """A detected coding pattern."""
    
    pattern_type: str           # e.g., "react_component", "api_route"
    file_path: str              # File where pattern was found
    confidence: float           # Confidence score (0.0-1.0)
    evidence: List[str]         # Evidence for detection
    line_numbers: List[int]     # Relevant line numbers
    metadata: Dict[str, Any]    # Additional pattern-specific data
```

---

### TeachingValueScore

Teaching value score with breakdown.

```python
@dataclass
class TeachingValueScore:
    """Teaching value score for a file."""
    
    total_score: float              # Overall score (0.0-1.0)
    documentation_score: float      # Documentation factor
    complexity_score: float         # Complexity factor
    pattern_score: float            # Pattern usage factor
    structure_score: float          # Code structure factor
    explanation: str                # Human-readable explanation
    factors: Dict[str, float]       # Detailed breakdown
```

---

### FileAnalysis

Complete analysis of a single file.

```python
@dataclass
class FileAnalysis:
    """Complete analysis of a single file."""
    
    file_path: str                          # Path to file
    language: str                           # Programming language
    symbol_info: SymbolInfo                 # Extracted symbols
    patterns: List[DetectedPattern]         # Detected patterns
    teaching_value: TeachingValueScore      # Teaching value score
    complexity_metrics: ComplexityMetrics   # Complexity analysis
    documentation_coverage: float           # Doc coverage (0.0-1.0)
    linter_issues: List[LinterIssue]        # Linter findings
    has_errors: bool                        # True if parse errors
    errors: List[str]                       # Error messages
    analyzed_at: datetime                   # Analysis timestamp
    cache_hit: bool                         # True if from cache
    is_notebook: bool = False               # True if Jupyter notebook
```

---

### CodebaseAnalysis

Complete analysis of an entire codebase.

```python
@dataclass
class CodebaseAnalysis:
    """Complete analysis of a codebase."""
    
    codebase_id: str                            # Unique codebase ID
    file_analyses: Dict[str, FileAnalysis]      # Per-file analyses
    dependency_graph: DependencyGraph           # Dependency relationships
    global_patterns: List[DetectedPattern]      # All detected patterns
    top_teaching_files: List[Tuple[str, float]] # Top files by teaching value
    metrics: CodebaseMetrics                    # Aggregate metrics
    analyzed_at: datetime                       # Analysis timestamp
```

---

### ComplexityMetrics

Complexity metrics for code.

```python
@dataclass
class ComplexityMetrics:
    """Complexity metrics for a file or codebase."""
    
    avg_complexity: float           # Average cyclomatic complexity
    max_complexity: int             # Maximum complexity found
    min_complexity: int             # Minimum complexity found
    high_complexity_count: int      # Functions with complexity > 10
    trivial_count: int              # Functions with complexity < 2
    total_functions: int            # Total functions analyzed
```

---

### DependencyGraph

Dependency graph for a codebase.

```python
@dataclass
class DependencyGraph:
    """Dependency graph showing file relationships."""
    
    nodes: Dict[str, FileNode]                  # file_path -> FileNode
    edges: List[DependencyEdge]                 # Dependencies
    circular_dependencies: List[CircularDependency]
    external_dependencies: Dict[str, int]       # package -> count
```

---

## Public Methods

### AnalysisEngine.analyze_file()

Analyze a single file.

```python
async def analyze_file(
    self,
    file_path: str,
    force: bool = False
) -> FileAnalysis:
    """
    Analyze a single code file.
    
    Args:
        file_path: Path to file to analyze
        force: If True, bypass cache and re-analyze
        
    Returns:
        FileAnalysis with complete analysis results
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is too large or unsupported
        
    Performance:
        - First run: 100-500ms for typical file
        - Cached: <10ms
        - Large files (>1000 lines): 500-1000ms
        
    Example:
        >>> engine = AnalysisEngine(cache_manager, config)
        >>> result = await engine.analyze_file("src/main.py")
        >>> print(f"Teaching value: {result.teaching_value.total_score}")
    """
```

**Cache Behavior:**
- Uses file hash as cache key
- Automatically invalidates on file change
- TTL: 1 hour (configurable)

**Error Handling:**
- Syntax errors: Returns partial analysis with `has_errors=True`
- File access errors: Raises FileNotFoundError
- Unsupported files: Raises ValueError

---

### AnalysisEngine.analyze_codebase()

Analyze an entire codebase.

```python
async def analyze_codebase(
    self,
    codebase_id: str,
    incremental: bool = True
) -> CodebaseAnalysis:
    """
    Analyze an entire codebase with parallel processing.
    
    Args:
        codebase_id: ID from scan_codebase
        incremental: If True, only analyze changed files
        
    Returns:
        CodebaseAnalysis with all files analyzed
        
    Raises:
        ValueError: If codebase not scanned first
        
    Performance:
        - First run (100 files): 20-30s
        - Incremental (no changes): 0.1-1s
        - Incremental (10% changed): 3-5s
        
    Example:
        >>> # First, scan the codebase
        >>> scan_result = await scan_codebase("/path/to/code")
        >>> cache.set(f"scan:{scan_result.codebase_id}", scan_result)
        >>> 
        >>> # Then analyze
        >>> analysis = await engine.analyze_codebase(
        ...     scan_result.codebase_id,
        ...     incremental=True
        ... )
        >>> print(f"Analyzed {analysis.metrics.total_files} files")
    """
```

**Incremental Analysis:**
- Tracks file hashes
- Only re-analyzes changed files
- Reuses cached results for unchanged files
- Provides 10-450x speedup

**Parallel Processing:**
- Processes 10 files concurrently (configurable)
- Uses asyncio.gather for parallelism
- Handles errors gracefully (continues on failure)

---

### ASTParserManager.parse_file()

Parse a file into an AST.

```python
def parse_file(self, file_path: str) -> ParseResult:
    """
    Parse a file using tree-sitter.
    
    Args:
        file_path: Path to file to parse
        
    Returns:
        ParseResult with AST and metadata
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file too large or unsupported
        
    Performance:
        - Small files (<100 lines): 10-50ms
        - Medium files (100-1000 lines): 50-200ms
        - Large files (>1000 lines): 200-500ms
        
    Example:
        >>> parser = ASTParserManager(config)
        >>> result = parser.parse_file("src/main.py")
        >>> print(f"Language: {result.language}")
        >>> print(f"Has errors: {result.has_errors}")
    """
```

**Supported Languages:**
- Python, JavaScript, TypeScript, Java, Go, Rust
- C++, C#, Ruby, PHP
- And 40+ more via tree-sitter-languages

---

### PatternDetector.detect_patterns_in_file()

Detect patterns in a file.

```python
def detect_patterns_in_file(
    self,
    symbol_info: SymbolInfo,
    file_content: str,
    file_path: str
) -> List[DetectedPattern]:
    """
    Detect all patterns in a file using registered detectors.
    
    Args:
        symbol_info: Extracted symbols from file
        file_content: Raw file content
        file_path: Path to file
        
    Returns:
        List of detected patterns with confidence scores
        
    Performance:
        - Typical file: 10-50ms
        - Complex file: 50-100ms
        
    Example:
        >>> detector = PatternDetector()
        >>> patterns = detector.detect_patterns_in_file(
        ...     symbol_info, file_content, "src/App.jsx"
        ... )
        >>> for pattern in patterns:
        ...     print(f"{pattern.pattern_type}: {pattern.confidence}")
    """
```

**Pattern Types:**
- Framework: react_component, api_route, database_model
- Language: python_decorator, javascript_promise, java_annotation
- Architecture: auth_jwt, caching, async_await

---

## Error Handling

### Error Categories

#### 1. Parse Errors

**Cause:** Syntax errors in source code

**Behavior:**
- Returns partial AST with error nodes
- Sets `has_errors=True`
- Includes error messages in `errors` list
- Analysis continues with available information

**Example:**
```python
result = await engine.analyze_file("broken.py")
if result.has_errors:
    print(f"Parse errors: {result.errors}")
    # Still has partial analysis:
    print(f"Functions found: {len(result.symbol_info.functions)}")
```

#### 2. File Access Errors

**Cause:** File not found, permission denied

**Behavior:**
- Raises `FileNotFoundError` or `PermissionError`
- No partial results
- Logged at ERROR level

**Example:**
```python
try:
    result = await engine.analyze_file("missing.py")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

#### 3. Unsupported File Errors

**Cause:** File extension not recognized

**Behavior:**
- Raises `ValueError`
- Logged at WARNING level
- File skipped in codebase analysis

**Example:**
```python
try:
    result = await engine.analyze_file("data.txt")
except ValueError as e:
    print(f"Unsupported file: {e}")
```

#### 4. Cache Errors

**Cause:** Redis connection issues, SQLite errors

**Behavior:**
- Logged at WARNING level
- Falls back to no cache
- Analysis continues normally
- Performance degraded but no data loss

#### 5. Linter Errors

**Cause:** Linter not installed, linter crashes

**Behavior:**
- Logged at WARNING level
- Returns empty linter_issues list
- Analysis continues normally
- Non-blocking

---

### Error Response Format

All errors include:

```python
@dataclass
class AnalysisError:
    """Error that occurred during analysis."""
    
    error_type: str         # "parse_error", "file_access_error", etc.
    file_path: str          # File where error occurred
    message: str            # Error message
    stack_trace: Optional[str]  # Full stack trace
    timestamp: datetime     # When error occurred
```

---

## Performance Characteristics

### Single File Analysis

| File Size | First Run | Cached | Speedup |
|-----------|-----------|--------|---------|
| <100 lines | 50-100ms | <5ms | 20x |
| 100-500 lines | 100-300ms | <10ms | 30x |
| 500-1000 lines | 300-500ms | <10ms | 50x |
| >1000 lines | 500-1000ms | <10ms | 100x |

### Codebase Analysis

| Files | First Run | Incremental (0% changed) | Incremental (10% changed) |
|-------|-----------|-------------------------|---------------------------|
| 10 | 2-3s | 0.1s | 0.5s |
| 50 | 8-12s | 0.2s | 2s |
| 100 | 20-30s | 0.5s | 5s |
| 500 | 90-120s | 2s | 20s |
| 1000 | 180-240s | 5s | 40s |

### Memory Usage

| Operation | Memory |
|-----------|--------|
| Single file | 10-50 MB |
| 100 files | 100-200 MB |
| 1000 files | 500-800 MB |
| Cache (memory) | Up to 500 MB (configurable) |

### Parallelism

- **Default:** 10 concurrent files
- **Configurable:** 1-50 concurrent files
- **Optimal:** 2x CPU cores

---

## Usage Examples

### Example 1: Basic File Analysis

```python
from src.analysis import AnalysisEngine, AnalysisConfig
from src.cache import CacheManager

# Initialize
config = AnalysisConfig()
cache = CacheManager()
engine = AnalysisEngine(cache, config)

# Analyze a file
result = await engine.analyze_file("src/main.py")

# Access results
print(f"Functions: {len(result.symbol_info.functions)}")
print(f"Teaching value: {result.teaching_value.total_score:.2f}")
print(f"Patterns: {[p.pattern_type for p in result.patterns]}")
```

### Example 2: Codebase Analysis with Incremental Updates

```python
from src.tools.scan_codebase import scan_codebase

# First run: full analysis
scan_result = await scan_codebase("/path/to/code")
cache.set(f"scan:{scan_result.codebase_id}", scan_result)

analysis = await engine.analyze_codebase(
    scan_result.codebase_id,
    incremental=False  # Full analysis
)
print(f"First run: {analysis.metrics.analysis_time_ms / 1000:.2f}s")

# Second run: incremental (much faster)
analysis = await engine.analyze_codebase(
    scan_result.codebase_id,
    incremental=True  # Only changed files
)
print(f"Incremental: {analysis.metrics.analysis_time_ms / 1000:.2f}s")
```

### Example 3: Custom Pattern Detection

```python
from src.analysis.pattern_detector import BasePatternDetector, DetectedPattern

class MyPatternDetector(BasePatternDetector):
    def detect(self, symbol_info, file_content, file_path):
        patterns = []
        # Your detection logic
        return patterns

# Register custom detector
engine.pattern_detector.register_detector(MyPatternDetector())

# Use as normal
result = await engine.analyze_file("src/custom.py")
```

### Example 4: Error Handling

```python
try:
    result = await engine.analyze_file("src/broken.py")
    
    if result.has_errors:
        print("Parse errors found:")
        for error in result.errors:
            print(f"  - {error}")
    
    # Still use partial results
    print(f"Functions found: {len(result.symbol_info.functions)}")
    
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Unsupported file: {e}")
```

---

## See Also

- [Configuration Guide](ANALYSIS_ENGINE_CONFIGURATION.md)
- [Usage Examples](../examples/)
- [Design Document](../.kiro/specs/analysis-engine/design.md)
- [Requirements](../.kiro/specs/analysis-engine/requirements.md)

---

**Last Updated:** November 13, 2025
