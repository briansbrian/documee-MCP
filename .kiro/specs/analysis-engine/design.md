# Design Document - Analysis Engine

## Overview

The Analysis Engine is the intelligence layer of the Documee MCP Server that transforms basic codebase scanning into deep, meaningful analysis. It uses Abstract Syntax Tree (AST) parsing via tree-sitter to understand code structure, detects patterns, analyzes dependencies, and scores files by teaching value. This design builds on the existing scan_codebase functionality and integrates with the caching layer.

### Key Design Goals

1. **Multi-language support**: Python, JavaScript, and TypeScript via tree-sitter
2. **Performance**: Fast analysis with aggressive caching and parallel processing
3. **Accuracy**: Reliable extraction of functions, classes, and patterns
4. **Extensibility**: Easy to add new languages and pattern detectors
5. **Integration**: Seamless integration with existing MCP tools and cache

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP Tools Layer                       │
│  (analyze_file, detect_patterns, analyze_dependencies, etc) │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Analysis Engine Core                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ AST Parser   │  │   Pattern    │  │  Dependency  │     │
│  │   Manager    │  │   Detector   │  │   Analyzer   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Symbol     │  │  Teaching    │  │  Complexity  │     │
│  │  Extractor   │  │Value Scorer  │  │   Analyzer   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    Support Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Cache     │  │    Config    │  │   Logging    │     │
│  │   Manager    │  │   Manager    │  │   System     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User Request → MCP Tool → Analysis Engine Core → AST Parser
                                ↓
                          Symbol Extractor
                                ↓
                          Pattern Detector
                                ↓
                         Dependency Analyzer
                                ↓
                        Teaching Value Scorer
                                ↓
                          Cache Results → Return to User
```

## Components and Interfaces

### 1. AST Parser Manager

**Purpose**: Manages tree-sitter parsers for multiple languages and provides unified parsing interface.

**Location**: `src/analysis/ast_parser.py`

**Key Classes**:

```python
from tree_sitter import Language, Parser
from tree_sitter_languages import get_language, get_parser

class ASTParserManager:
    """Manages tree-sitter parsers for multiple languages.
    
    Uses tree-sitter-languages for pre-built binaries (no compilation needed).
    Verified against Context7 documentation (Trust Score: 9.7).
    """
    
    def __init__(self, config: AnalysisConfig):
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        self.config = config
        self._initialize_parsers()
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a file and return AST with metadata.
        
        Example:
            result = parser_manager.parse_file("src/main.py")
            print(result.root_node.type)  # "module"
        """
        language = self._detect_language(file_path)
        parser = self.get_parser(language)
        
        with open(file_path, 'rb') as f:
            source_code = f.read()
        
        start_time = time.time()
        tree = parser.parse(source_code)
        parse_time_ms = (time.time() - start_time) * 1000
        
        return ParseResult(
            file_path=file_path,
            language=language,
            tree=tree,
            root_node=tree.root_node,
            has_errors=tree.root_node.has_error,
            error_nodes=self._find_error_nodes(tree.root_node),
            parse_time_ms=parse_time_ms
        )
    
    def get_parser(self, language: str) -> Parser:
        """Get or create parser for language using tree-sitter-languages."""
        if language not in self.parsers:
            # Use pre-built parser from tree-sitter-languages
            self.parsers[language] = get_parser(language)
            self.languages[language] = get_language(language)
        return self.parsers[language]
    
    def _initialize_parsers(self):
        """Pre-load parsers for configured languages."""
        for lang in self.config.supported_languages:
            self.get_parser(lang)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension."""
        ext = Path(file_path).suffix.lower()
        mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.ipynb': 'python'  # Jupyter notebooks
        }
        return mapping.get(ext, 'unknown')
    
    def _find_error_nodes(self, node) -> List:
        """Recursively find all error nodes in tree."""
        errors = []
        if node.type == 'ERROR' or node.is_missing:
            errors.append(node)
        for child in node.children:
            errors.extend(self._find_error_nodes(child))
        return errors

@dataclass
class ParseResult:
    """Result of parsing a file."""
    file_path: str
    language: str
    tree: Any  # tree-sitter Tree object
    root_node: Any  # tree-sitter Node object
    has_errors: bool
    error_nodes: List[Any]
    parse_time_ms: float
```

**Dependencies**:
- `tree-sitter>=0.23.0` - Core parsing library
- `tree-sitter-languages>=1.10.2` - Pre-built language binaries
- Config manager for language settings

**API Pattern** (verified with Context7):
```python
# Correct pattern from tree-sitter-languages
from tree_sitter_languages import get_language, get_parser

language = get_language('python')
parser = get_parser('python')
tree = parser.parse(source_code.encode())
root_node = tree.root_node
```

### 2. Symbol Extractor

**Purpose**: Extracts functions, classes, and other symbols from AST.

**Location**: `src/analysis/symbol_extractor.py`

**Key Classes**:

```python
class SymbolExtractor:
    """Extracts functions and classes from AST."""
    
    def extract_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """Extract all symbols from parsed file."""
        pass
    
    def _extract_python_symbols(self, node: Node) -> SymbolInfo:
        """Extract symbols from Python AST."""
        pass
    
    def _extract_javascript_symbols(self, node: Node) -> SymbolInfo:
        """Extract symbols from JavaScript/TypeScript AST."""
        pass

@dataclass
class FunctionInfo:
    name: str
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    start_line: int
    end_line: int
    complexity: int
    is_async: bool
    decorators: List[str]

@dataclass
class ClassInfo:
    name: str
    methods: List[FunctionInfo]
    base_classes: List[str]
    docstring: Optional[str]
    start_line: int
    end_line: int
    decorators: List[str]

@dataclass
class SymbolInfo:
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[ImportInfo]
    exports: List[str]  # For JS/TS
```

**Algorithm**:
1. Traverse AST using depth-first search
2. Identify function/class definition nodes by type
3. Extract metadata from child nodes (parameters, docstrings, etc.)
4. Calculate complexity during traversal
5. Return structured symbol information

### 3. Pattern Detector

**Purpose**: Identifies common coding patterns and architectural decisions.

**Location**: `src/analysis/pattern_detector.py`

**Key Classes**:

```python
class PatternDetector:
    """Detects coding patterns in codebase."""
    
    def __init__(self):
        self.detectors: List[BasePatternDetector] = [
            ReactPatternDetector(),
            APIPatternDetector(),
            DatabasePatternDetector(),
            AuthPatternDetector(),
        ]
    
    def detect_patterns(self, codebase_id: str) -> List[DetectedPattern]:
        """Detect all patterns in codebase."""
        pass

class BasePatternDetector(ABC):
    """Base class for pattern detectors."""
    
    @abstractmethod
    def detect(self, symbol_info: SymbolInfo, file_content: str) -> List[DetectedPattern]:
        pass

@dataclass
class DetectedPattern:
    pattern_type: str  # "react_component", "api_route", etc.
    file_path: str
    confidence: float  # 0.0-1.0
    evidence: List[str]  # What triggered detection
    line_numbers: List[int]
    metadata: Dict[str, Any]  # Pattern-specific data

class ReactPatternDetector(BasePatternDetector):
    """Detects React patterns."""
    
    def detect(self, symbol_info: SymbolInfo, file_content: str) -> List[DetectedPattern]:
        # Look for:
        # - Function components (returns JSX)
        # - Hook usage (useState, useEffect, etc.)
        # - Props destructuring
        pass
```

**Pattern Detection Rules**:

- **React Component**: Function returns JSX, uses hooks, has props parameter
- **API Route**: Express/FastAPI route decorators, HTTP method handlers
- **Database Pattern**: ORM imports, model definitions, query methods
- **Auth Pattern**: JWT/OAuth imports, authentication middleware, token handling

### 4. Dependency Analyzer

**Purpose**: Analyzes import relationships and builds dependency graph.

**Location**: `src/analysis/dependency_analyzer.py`

**Key Classes**:

```python
class DependencyAnalyzer:
    """Analyzes dependencies between files."""
    
    def analyze_dependencies(self, codebase_id: str) -> DependencyGraph:
        """Build dependency graph for codebase."""
        pass
    
    def _extract_imports(self, symbol_info: SymbolInfo) -> List[ImportInfo]:
        """Extract import statements."""
        pass
    
    def _resolve_import_paths(self, import_info: ImportInfo, file_path: str) -> str:
        """Resolve relative imports to absolute paths."""
        pass
    
    def _detect_circular_dependencies(self, graph: DependencyGraph) -> List[CircularDependency]:
        """Detect circular dependencies using DFS."""
        pass

@dataclass
class ImportInfo:
    module: str
    imported_symbols: List[str]
    is_relative: bool
    import_type: str  # "import", "from_import", "require", "es6_import"
    line_number: int

@dataclass
class DependencyGraph:
    nodes: Dict[str, FileNode]  # file_path -> FileNode
    edges: List[DependencyEdge]
    circular_dependencies: List[CircularDependency]
    external_dependencies: Dict[str, int]  # package -> usage_count

@dataclass
class FileNode:
    file_path: str
    imports: List[str]  # Files this file imports
    imported_by: List[str]  # Files that import this file
    external_imports: List[str]  # External packages

@dataclass
class DependencyEdge:
    from_file: str
    to_file: str
    import_count: int  # Number of imports between files
```

**Algorithm**:
1. Extract all imports from each file
2. Resolve relative imports to absolute paths
3. Build directed graph (file A imports file B = edge A→B)
4. Detect cycles using DFS with visited/recursion stack
5. Categorize dependencies as internal vs external

### 5. Teaching Value Scorer

**Purpose**: Scores files by educational value based on multiple factors.

**Location**: `src/analysis/teaching_value_scorer.py`

**Key Classes**:

```python
class TeachingValueScorer:
    """Scores files by teaching value."""
    
    def __init__(self, config: AnalysisConfig):
        self.weights = config.teaching_value_weights
    
    def score_file(self, file_analysis: FileAnalysis) -> TeachingValueScore:
        """Calculate teaching value score for file."""
        pass
    
    def _score_documentation(self, symbol_info: SymbolInfo) -> float:
        """Score based on documentation coverage."""
        pass
    
    def _score_complexity(self, symbol_info: SymbolInfo) -> float:
        """Score based on code complexity (prefer moderate)."""
        pass
    
    def _score_patterns(self, patterns: List[DetectedPattern]) -> float:
        """Score based on pattern usage."""
        pass
    
    def _score_structure(self, symbol_info: SymbolInfo) -> float:
        """Score based on code structure clarity."""
        pass

@dataclass
class TeachingValueScore:
    total_score: float  # 0.0-1.0
    documentation_score: float
    complexity_score: float
    pattern_score: float
    structure_score: float
    explanation: str  # Human-readable explanation
    factors: Dict[str, float]  # Detailed breakdown
```

**Scoring Algorithm**:

```
total_score = (
    documentation_weight * documentation_score +
    complexity_weight * complexity_score +
    pattern_weight * pattern_score +
    structure_weight * structure_score
)

documentation_score = (functions_with_docs / total_functions)

complexity_score = {
    1.0 if 3 <= avg_complexity <= 7  # Sweet spot
    0.7 if 2 <= avg_complexity < 3 or 7 < avg_complexity <= 10
    0.3 if avg_complexity > 10 or avg_complexity < 2
}

pattern_score = (detected_patterns_count * 0.2) capped at 1.0

structure_score = {
    1.0 if clear_separation_of_concerns and consistent_naming
    0.5 if moderate_structure
    0.2 if poor_structure
}
```

### 6. Complexity Analyzer

**Purpose**: Calculates cyclomatic complexity and other metrics.

**Location**: `src/analysis/complexity_analyzer.py`

**Key Classes**:

```python
class ComplexityAnalyzer:
    """Analyzes code complexity metrics."""
    
    def calculate_complexity(self, node: Node, language: str) -> int:
        """Calculate cyclomatic complexity for function."""
        pass
    
    def calculate_nesting_depth(self, node: Node) -> int:
        """Calculate maximum nesting depth."""
        pass
    
    def _count_decision_points(self, node: Node) -> int:
        """Count if, for, while, case, and, or statements."""
        pass
```

**Complexity Calculation**:
- Start with complexity = 1
- +1 for each: if, elif, for, while, case, and, or, except
- Nesting depth = maximum indentation level
- Flag as "high complexity" if > 10
- Flag as "trivial" if < 2

### 7. Persistence Manager

**Purpose**: Manages long-term storage of analysis results to disk.

**Location**: `src/analysis/persistence.py`

**Key Classes**:

```python
class PersistenceManager:
    """Manages disk persistence of analysis results."""
    
    def __init__(self, base_path: str = ".documee/analysis"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_analysis(self, codebase_id: str, analysis: CodebaseAnalysis):
        """Save analysis to disk as JSON."""
        analysis_dir = self.base_path / codebase_id
        analysis_dir.mkdir(exist_ok=True)
        
        # Save main analysis
        with open(analysis_dir / "analysis.json", 'w') as f:
            json.dump(analysis.to_dict(), f, indent=2)
        
        # Save individual file analyses
        for file_path, file_analysis in analysis.file_analyses.items():
            safe_name = hashlib.sha256(file_path.encode()).hexdigest()[:16]
            with open(analysis_dir / f"file_{safe_name}.json", 'w') as f:
                json.dump(file_analysis.to_dict(), f, indent=2)
    
    def load_analysis(self, codebase_id: str) -> Optional[CodebaseAnalysis]:
        """Load analysis from disk."""
        analysis_file = self.base_path / codebase_id / "analysis.json"
        if not analysis_file.exists():
            return None
        
        with open(analysis_file, 'r') as f:
            data = json.load(f)
        
        return CodebaseAnalysis.from_dict(data)
    
    def get_file_hashes(self, codebase_id: str) -> Dict[str, str]:
        """Get stored file hashes for incremental analysis."""
        hash_file = self.base_path / codebase_id / "file_hashes.json"
        if not hash_file.exists():
            return {}
        
        with open(hash_file, 'r') as f:
            return json.load(f)
    
    def save_file_hashes(self, codebase_id: str, hashes: Dict[str, str]):
        """Save file hashes for incremental analysis."""
        analysis_dir = self.base_path / codebase_id
        analysis_dir.mkdir(exist_ok=True)
        
        with open(analysis_dir / "file_hashes.json", 'w') as f:
            json.dump(hashes, f, indent=2)
```

### 8. Linter Integration

**Purpose**: Integrates external linters (pylint, eslint) without blocking analysis.

**Location**: `src/analysis/linter_integration.py`

**Key Classes**:

```python
class LinterIntegration:
    """Integrates external linters asynchronously."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.enabled = config.enable_linters
    
    async def run_linters(self, file_path: str, language: str) -> List[LinterIssue]:
        """Run appropriate linters for file."""
        if not self.enabled:
            return []
        
        linters = {
            'python': self._run_pylint,
            'javascript': self._run_eslint,
            'typescript': self._run_eslint
        }
        
        linter_func = linters.get(language)
        if not linter_func:
            return []
        
        try:
            return await linter_func(file_path)
        except Exception as e:
            logger.warning(f"Linter failed for {file_path}: {e}")
            return []
    
    async def _run_pylint(self, file_path: str) -> List[LinterIssue]:
        """Run pylint and parse output."""
        proc = await asyncio.create_subprocess_exec(
            'pylint', file_path, '--output-format=json',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        
        if proc.returncode in [0, 4, 8, 16]:  # Pylint exit codes
            issues = json.loads(stdout.decode())
            return [
                LinterIssue(
                    tool='pylint',
                    severity=issue['type'],
                    message=issue['message'],
                    line=issue['line'],
                    column=issue['column'],
                    rule=issue['message-id']
                )
                for issue in issues
            ]
        return []
    
    async def _run_eslint(self, file_path: str) -> List[LinterIssue]:
        """Run eslint and parse output."""
        proc = await asyncio.create_subprocess_exec(
            'eslint', file_path, '--format=json',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        
        if proc.returncode in [0, 1]:  # ESLint exit codes
            results = json.loads(stdout.decode())
            issues = []
            for result in results:
                for message in result.get('messages', []):
                    issues.append(LinterIssue(
                        tool='eslint',
                        severity=message['severity'],
                        message=message['message'],
                        line=message['line'],
                        column=message['column'],
                        rule=message.get('ruleId', 'unknown')
                    ))
            return issues
        return []

@dataclass
class LinterIssue:
    tool: str  # 'pylint', 'eslint'
    severity: str  # 'error', 'warning', 'info'
    message: str
    line: int
    column: int
    rule: str
```

### 9. Jupyter Notebook Support

**Purpose**: Analyzes Jupyter notebooks by extracting code cells.

**Location**: `src/analysis/notebook_support.py`

**Key Classes**:

```python
import nbformat

class NotebookAnalyzer:
    """Analyzes Jupyter notebooks."""
    
    def extract_code(self, notebook_path: str) -> NotebookCode:
        """Extract code cells from notebook."""
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        code_cells = []
        line_offset = 0
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                source = cell.source
                lines = source.split('\n')
                
                code_cells.append(CodeCell(
                    content=source,
                    start_line=line_offset,
                    end_line=line_offset + len(lines),
                    execution_count=cell.execution_count
                ))
                
                line_offset += len(lines) + 1  # +1 for cell boundary
        
        # Concatenate all code cells
        full_code = '\n'.join(cell.content for cell in code_cells)
        
        return NotebookCode(
            notebook_path=notebook_path,
            cells=code_cells,
            full_code=full_code,
            total_cells=len(code_cells)
        )
    
    def map_line_to_cell(self, line_number: int, notebook_code: NotebookCode) -> Optional[int]:
        """Map line number in concatenated code to cell index."""
        for i, cell in enumerate(notebook_code.cells):
            if cell.start_line <= line_number <= cell.end_line:
                return i
        return None

@dataclass
class CodeCell:
    content: str
    start_line: int
    end_line: int
    execution_count: Optional[int]

@dataclass
class NotebookCode:
    notebook_path: str
    cells: List[CodeCell]
    full_code: str
    total_cells: int
```

### 10. Analysis Engine Core

**Purpose**: Orchestrates all analysis components and provides main API.

**Location**: `src/analysis/engine.py`

**Key Classes**:

```python
class AnalysisEngine:
    """Main analysis engine orchestrator with incremental analysis support."""
    
    def __init__(self, cache_manager: CacheManager, config: AnalysisConfig):
        self.cache = cache_manager
        self.config = config
        self.parser = ASTParserManager(config)
        self.symbol_extractor = SymbolExtractor()
        self.pattern_detector = PatternDetector()
        self.dependency_analyzer = DependencyAnalyzer()
        self.teaching_value_scorer = TeachingValueScorer(config)
        self.complexity_analyzer = ComplexityAnalyzer()
        self.persistence = PersistenceManager()
        self.linter = LinterIntegration(config)
        self.notebook_analyzer = NotebookAnalyzer()
    
    async def analyze_file(self, file_path: str, force: bool = False) -> FileAnalysis:
        """Analyze single file with caching and incremental support.
        
        Args:
            file_path: Path to file to analyze
            force: If True, bypass cache and re-analyze
        
        Returns:
            FileAnalysis with all extracted information
        """
        # Calculate file hash for incremental analysis
        file_hash = self._calculate_file_hash(file_path)
        
        # Check cache if not forcing re-analysis
        if not force:
            cached = self._get_cached_analysis(file_path, file_hash)
            if cached:
                logger.info(f"Cache hit for {file_path}")
                cached.cache_hit = True
                return cached
        
        logger.info(f"Analyzing {file_path}")
        
        # Handle Jupyter notebooks
        if file_path.endswith('.ipynb'):
            notebook_code = self.notebook_analyzer.extract_code(file_path)
            source_code = notebook_code.full_code.encode()
            is_notebook = True
        else:
            with open(file_path, 'rb') as f:
                source_code = f.read()
            is_notebook = False
        
        # Parse file
        parse_result = self.parser.parse_file(file_path)
        
        # Extract symbols
        symbol_info = self.symbol_extractor.extract_symbols(parse_result)
        
        # Detect patterns
        patterns = self.pattern_detector.detect_patterns_in_file(symbol_info, source_code)
        
        # Calculate complexity
        complexity_metrics = self.complexity_analyzer.analyze_file(symbol_info)
        
        # Calculate documentation coverage
        doc_coverage = self._calculate_doc_coverage(symbol_info)
        
        # Score teaching value
        teaching_value = self.teaching_value_scorer.score_file(
            symbol_info, patterns, complexity_metrics, doc_coverage
        )
        
        # Run linters asynchronously (non-blocking)
        linter_issues = await self.linter.run_linters(
            file_path, 
            parse_result.language
        )
        
        # Create analysis result
        analysis = FileAnalysis(
            file_path=file_path,
            language=parse_result.language,
            symbol_info=symbol_info,
            patterns=patterns,
            teaching_value=teaching_value,
            complexity_metrics=complexity_metrics,
            documentation_coverage=doc_coverage,
            linter_issues=linter_issues,
            has_errors=parse_result.has_errors,
            errors=[str(node) for node in parse_result.error_nodes],
            analyzed_at=datetime.now(),
            cache_hit=False,
            is_notebook=is_notebook
        )
        
        # Cache results
        self._cache_analysis(file_path, file_hash, analysis)
        
        return analysis
    
    async def analyze_codebase(self, codebase_id: str, incremental: bool = True) -> CodebaseAnalysis:
        """Analyze entire codebase with parallel processing and incremental support.
        
        Args:
            codebase_id: ID of codebase to analyze
            incremental: If True, only analyze changed files
        
        Returns:
            CodebaseAnalysis with all files analyzed
        """
        # Get scan results
        scan_result = self.cache.get(f"scan:{codebase_id}")
        if not scan_result:
            raise ValueError("Codebase not scanned. Call scan_codebase first.")
        
        # Load previous analysis for incremental mode
        previous_analysis = None
        previous_hashes = {}
        if incremental:
            previous_analysis = self.persistence.load_analysis(codebase_id)
            previous_hashes = self.persistence.get_file_hashes(codebase_id)
        
        # Determine which files to analyze
        files_to_analyze = []
        current_hashes = {}
        
        for file_path in scan_result.files:
            if not self._is_analyzable(file_path):
                continue
            
            file_hash = self._calculate_file_hash(file_path)
            current_hashes[file_path] = file_hash
            
            # In incremental mode, skip unchanged files
            if incremental and file_path in previous_hashes:
                if previous_hashes[file_path] == file_hash:
                    logger.debug(f"Skipping unchanged file: {file_path}")
                    continue
            
            files_to_analyze.append(file_path)
        
        logger.info(f"Analyzing {len(files_to_analyze)} files (incremental: {incremental})")
        
        # Analyze files in parallel
        file_analyses = {}
        
        # Reuse previous analyses for unchanged files
        if previous_analysis and incremental:
            for file_path, analysis in previous_analysis.file_analyses.items():
                if file_path not in files_to_analyze:
                    file_analyses[file_path] = analysis
        
        # Analyze new/changed files
        tasks = [self.analyze_file(fp) for fp in files_to_analyze]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for file_path, result in zip(files_to_analyze, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to analyze {file_path}: {result}")
            else:
                file_analyses[file_path] = result
        
        # Build dependency graph
        dependency_graph = self.dependency_analyzer.analyze_dependencies(
            codebase_id, file_analyses
        )
        
        # Detect global patterns
        global_patterns = self.pattern_detector.detect_global_patterns(file_analyses)
        
        # Rank files by teaching value
        top_teaching_files = sorted(
            [(fp, fa.teaching_value.total_score) for fp, fa in file_analyses.items()],
            key=lambda x: x[1],
            reverse=True
        )[:20]  # Top 20 files
        
        # Calculate metrics
        metrics = self._calculate_codebase_metrics(file_analyses)
        
        # Create codebase analysis
        analysis = CodebaseAnalysis(
            codebase_id=codebase_id,
            file_analyses=file_analyses,
            dependency_graph=dependency_graph,
            global_patterns=global_patterns,
            top_teaching_files=top_teaching_files,
            metrics=metrics,
            analyzed_at=datetime.now()
        )
        
        # Persist to disk
        self.persistence.save_analysis(codebase_id, analysis)
        self.persistence.save_file_hashes(codebase_id, current_hashes)
        
        # Cache in memory/Redis
        self.cache.set(f"analysis:{codebase_id}", analysis, ttl=3600)
        
        return analysis
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content."""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _is_analyzable(self, file_path: str) -> bool:
        """Check if file can be analyzed."""
        ext = Path(file_path).suffix.lower()
        return ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.ipynb']
    
    def _get_cached_analysis(self, file_path: str, file_hash: str) -> Optional[FileAnalysis]:
        """Retrieve cached analysis if available and hash matches."""
        cache_key = f"analysis:{file_hash}"
        return self.cache.get(cache_key)
    
    def _cache_analysis(self, file_path: str, file_hash: str, analysis: FileAnalysis):
        """Cache analysis results with file hash as key."""
        cache_key = f"analysis:{file_hash}"
        self.cache.set(cache_key, analysis, ttl=3600)

@dataclass
class FileAnalysis:
    file_path: str
    language: str
    symbol_info: SymbolInfo
    patterns: List[DetectedPattern]
    teaching_value: TeachingValueScore
    complexity_metrics: ComplexityMetrics
    documentation_coverage: float
    linter_issues: List[LinterIssue]  # NEW: Linter integration
    has_errors: bool
    errors: List[str]
    analyzed_at: datetime
    cache_hit: bool
    is_notebook: bool = False  # NEW: Jupyter notebook flag

@dataclass
class CodebaseAnalysis:
    codebase_id: str
    file_analyses: Dict[str, FileAnalysis]
    dependency_graph: DependencyGraph
    global_patterns: List[DetectedPattern]
    top_teaching_files: List[Tuple[str, float]]  # Sorted by teaching value
    metrics: CodebaseMetrics
    analyzed_at: datetime

@dataclass
class CodebaseMetrics:
    total_files: int
    total_functions: int
    total_classes: int
    avg_complexity: float
    avg_documentation_coverage: float
    total_patterns_detected: int
    analysis_time_ms: float
    cache_hit_rate: float
```

## Data Models

### Configuration Model

```python
@dataclass
class AnalysisConfig:
    """Configuration for analysis engine."""
    max_complexity_threshold: int = 10
    min_documentation_coverage: float = 0.5
    max_file_size_mb: int = 5
    
    # Multi-language support (50+ languages via tree-sitter-languages)
    supported_languages: List[str] = field(default_factory=lambda: [
        "python", "javascript", "typescript",
        "java", "go", "rust", "cpp", "c", "csharp",
        "ruby", "php", "scala", "kotlin", "swift"
    ])
    
    teaching_value_weights: TeachingValueWeights = field(default_factory=TeachingValueWeights)
    parallel_workers: int = 10
    cache_ttl_seconds: int = 3600
    enable_linters: bool = True  # Enable/disable linter integration
    enable_incremental: bool = True  # Enable incremental analysis
    persistence_path: str = ".documee/analysis"  # Disk persistence location
    
    # Plugin architecture for custom pattern detectors
    pattern_detectors: List[str] = field(default_factory=lambda: [
        "ReactPatternDetector",
        "APIPatternDetector", 
        "DatabasePatternDetector",
        "AuthPatternDetector"
    ])

@dataclass
class TeachingValueWeights:
    documentation: float = 0.35
    complexity: float = 0.25
    patterns: float = 0.25
    structure: float = 0.15
```

### Cache Keys

```
ast:{file_hash} → ParseResult
symbols:{file_hash} → SymbolInfo
teaching_value:{file_hash} → TeachingValueScore
patterns:{codebase_id} → List[DetectedPattern]
dependencies:{codebase_id} → DependencyGraph
analysis:{codebase_id} → CodebaseAnalysis
```

## Error Handling

### Error Categories

1. **Parse Errors**: Syntax errors in source files
   - Action: Log error, return partial AST with error flag
   - User impact: Analysis continues with degraded results

2. **File Access Errors**: Permission denied, file not found
   - Action: Log error, skip file, continue with others
   - User impact: File excluded from analysis

3. **Unsupported Language**: File extension not recognized
   - Action: Log warning, skip file
   - User impact: File excluded from analysis

4. **Cache Errors**: Redis connection issues
   - Action: Log error, proceed without cache
   - User impact: Slower performance, no data loss

5. **Configuration Errors**: Invalid config values
   - Action: Use default values, log warning
   - User impact: Analysis uses defaults

### Error Response Format

```python
@dataclass
class AnalysisError:
    error_type: str  # "parse_error", "file_access_error", etc.
    file_path: str
    message: str
    stack_trace: Optional[str]
    timestamp: datetime
```

## Testing Strategy

### Unit Tests

**Location**: `tests/analysis/`

1. **test_ast_parser.py**
   - Test parsing valid Python/JS/TS files
   - Test handling syntax errors
   - Test file size limits
   - Test language detection

2. **test_symbol_extractor.py**
   - Test function extraction (all parameter types)
   - Test class extraction (inheritance, decorators)
   - Test docstring extraction
   - Test edge cases (nested functions, lambdas)

3. **test_pattern_detector.py**
   - Test React pattern detection
   - Test API pattern detection
   - Test confidence scoring
   - Test false positive rate

4. **test_dependency_analyzer.py**
   - Test import extraction
   - Test circular dependency detection
   - Test import path resolution
   - Test external vs internal categorization

5. **test_teaching_value_scorer.py**
   - Test scoring algorithm
   - Test weight configuration
   - Test score consistency
   - Test edge cases (empty files, generated code)

6. **test_complexity_analyzer.py**
   - Test cyclomatic complexity calculation
   - Test nesting depth calculation
   - Test decision point counting

### Integration Tests

**Location**: `tests/integration/`

1. **test_analysis_engine.py**
   - Test full file analysis pipeline
   - Test codebase analysis with real projects
   - Test caching behavior
   - Test parallel processing
   - Test error recovery

2. **test_mcp_tools.py**
   - Test MCP tool registration
   - Test tool input validation
   - Test tool response format
   - Test error handling in tools

### Test Data

**Location**: `tests/fixtures/`

- Sample Python files (simple, complex, with errors)
- Sample JavaScript/TypeScript files
- Sample React components
- Sample API routes
- Known pattern examples

### Performance Tests

1. **Single file analysis**: < 500ms for 1000-line file
2. **Codebase analysis**: < 30s for 100 files (first run)
3. **Cached analysis**: < 3s for 100 files
4. **Memory usage**: < 500MB for 1000-file codebase

## Performance Optimizations

### 1. Aggressive Caching

- Cache AST, symbols, and scores separately
- Use file hash as cache key (invalidates on change)
- TTL of 1 hour (configurable)
- Cache hit rate target: > 80% for repeated analysis

### 2. Parallel Processing

- Process files in parallel using asyncio
- Worker pool of 10 concurrent tasks (configurable)
- Batch processing for large codebases
- Progress reporting for long-running analysis

### 3. Lazy Loading

- Only parse files when needed
- Only extract symbols if not cached
- Only detect patterns if requested
- Only build dependency graph if requested

### 4. Incremental Analysis

- Track file changes via hash
- Only re-analyze changed files
- Reuse cached results for unchanged files
- Update dependency graph incrementally

### 5. Memory Management

- Stream large files instead of loading entirely
- Release AST after symbol extraction
- Limit concurrent file processing
- Clear caches periodically

## Integration Points

### 1. Integration with scan_codebase

```python
# Analysis engine uses scan results
scan_result = cache.get(f"scan:{codebase_id}")
if not scan_result:
    raise ValueError("Codebase not scanned. Call scan_codebase first.")

# Use file list from scan
for file_info in scan_result.files:
    if file_info.extension in supported_extensions:
        await analyze_file(file_info.path)
```

### 2. Integration with Cache Manager

```python
# Reuse existing cache manager
from src.cache.manager import CacheManager

cache = CacheManager(config)
engine = AnalysisEngine(cache, analysis_config)
```

### 3. Integration with MCP Tools

```python
# Register analysis tools
@server.call_tool()
async def analyze_file(file_path: str) -> FileAnalysis:
    return await engine.analyze_file(file_path)

@server.call_tool()
async def detect_patterns(codebase_id: str) -> List[DetectedPattern]:
    analysis = await engine.analyze_codebase(codebase_id)
    return analysis.global_patterns

@server.call_tool()
async def analyze_dependencies(codebase_id: str) -> DependencyGraph:
    analysis = await engine.analyze_codebase(codebase_id)
    return analysis.dependency_graph

@server.call_tool()
async def score_teaching_value(file_path: str) -> TeachingValueScore:
    analysis = await engine.analyze_file(file_path)
    return analysis.teaching_value
```

### 4. Integration with Logging

```python
# Use existing logging system
from src.utils.logging import get_logger

logger = get_logger(__name__)
logger.info(f"Starting analysis for {file_path}")
logger.error(f"Parse error in {file_path}: {error}")
```

## Deployment Considerations

### Local Development Environment

**IMPORTANT for Windows**: Always use the virtual environment Python executable:

```powershell
# Correct way to run Python commands
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m src.server
.\venv\Scripts\python.exe -m pytest

# NOT: python (uses system Python)
# NOT: python.exe (uses system Python)
```

### Dependencies

Based on Context7 verification and latest API patterns:

```
# Core parsing (verified with Context7)
tree-sitter>=0.23.0
tree-sitter-languages>=1.10.2  # Pre-built binaries for ALL languages

# Async operations (from API-PATTERNS.md)
aiofiles>=23.2.1
aiosqlite>=0.19.0

# Optional linter integration
pylint>=3.0.0  # Optional
eslint  # Via subprocess, not Python package

# Jupyter notebook support
nbformat>=5.9.0  # For .ipynb parsing
```

**Note**: Using `tree-sitter-languages` package provides pre-built binaries for **50+ languages** including Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, Ruby, PHP, and more. No compilation required! This is the recommended approach per Context7 documentation (Trust Score: 9.7).

**Supported Languages** (via tree-sitter-languages):
- Python, JavaScript, TypeScript, JSX, TSX
- Java, Go, Rust, C, C++, C#
- Ruby, PHP, Scala, Kotlin, Swift
- HTML, CSS, JSON, YAML, Markdown
- Bash, SQL, and 30+ more

See full list: https://github.com/grantjenks/py-tree-sitter-languages

### Configuration

Add to `config.yaml`:

```yaml
analysis:
  # Core settings
  max_complexity_threshold: 10
  min_documentation_coverage: 0.5
  max_file_size_mb: 5
  
  # Multi-language support (50+ languages available via tree-sitter-languages)
  # Start with these, add more as needed
  supported_languages:
    - python
    - javascript
    - typescript
    - java
    - go
    - rust
    - cpp
    - c
    - csharp
    - ruby
    - php
    # Add more: scala, kotlin, swift, bash, sql, html, css, json, yaml, etc.
  
  # Teaching value weights
  teaching_value_weights:
    documentation: 0.35
    complexity: 0.25
    patterns: 0.25
    structure: 0.15
  
  # Performance settings
  parallel_workers: 10
  cache_ttl_seconds: 3600
  
  # NEW: Incremental analysis
  enable_incremental: true
  persistence_path: ".documee/analysis"
  
  # NEW: Linter integration
  enable_linters: true
  linters:
    python: pylint
    javascript: eslint
    typescript: eslint
  
  # NEW: Pattern detector plugins
  pattern_detectors:
    - ReactPatternDetector
    - APIPatternDetector
    - DatabasePatternDetector
    - AuthPatternDetector
    # Add custom detectors here:
    # - CustomPatternDetector
  
  # NEW: Jupyter notebook support
  analyze_notebooks: true
```

### Logging

- Log all analysis operations at INFO level
- Log errors at ERROR level with stack traces
- Log performance metrics after each analysis
- Log cache hit/miss rates

## Implemented Enhancements

Based on user requirements, the following enhancements are included in this spec:

1. ✅ **Multi-Language Support**: 50+ languages via tree-sitter-languages (Python, JS, TS, Java, Go, Rust, C++, C#, Ruby, PHP, etc.)
2. ✅ **Incremental Analysis**: Only analyze changed files based on hash comparison
3. ✅ **Disk Persistence**: Save analysis results to disk for long-term storage
4. ✅ **Linter Integration**: Integrate pylint/eslint output (non-blocking)
5. ✅ **Plugin Architecture**: Support custom pattern detectors via BasePatternDetector
6. ✅ **Jupyter Notebook Support**: Analyze .ipynb files by extracting code cells
7. ✅ **Advanced Patterns**: Design patterns, anti-patterns via plugin system
8. ✅ **Code Quality Metrics**: Complexity, documentation coverage, teaching value scoring
9. ✅ **Dependency Analysis**: Import graphs, circular dependency detection
10. ✅ **Performance Optimization**: Parallel processing, 3-tier caching, incremental updates

## Future Enhancements (Phase 2)

Additional features for future specs:

1. **AI-Powered Analysis**: Use LLM to explain code purpose and generate documentation
2. **Interactive Visualization**: Web-based dependency graphs, complexity heatmaps, architecture diagrams
3. **Git Integration**: Analyze changes between commits, track code evolution over time
4. **Security Analysis**: Detect security vulnerabilities, unsafe patterns, OWASP top 10
5. **Performance Profiling**: Identify performance bottlenecks, suggest optimizations
6. **Multi-Repository Analysis**: Analyze dependencies across multiple repositories
7. **Real-time Analysis**: Watch mode for continuous analysis during development
8. **Code Generation**: Auto-generate documentation, tests, type hints
9. **Refactoring Suggestions**: Identify code smells, suggest improvements
10. **Team Analytics**: Track code quality trends, developer contributions, technical debt

## Resolved Design Decisions

Based on research and user requirements:

1. **Incremental Analysis**: YES - Track file changes via hash, only re-analyze changed files
2. **Persistence**: BOTH - Cache in Redis/SQLite AND persist to disk for long-term storage
3. **Custom Pattern Detectors**: YES - Plugin architecture using BasePatternDetector abstract class
4. **Linter Integration**: YES - Integrate pylint/eslint output without blocking performance
5. **Jupyter Notebooks**: YES - Support .ipynb files by extracting code cells

### Implementation Notes

**Incremental Analysis**:
- Store file hashes in cache
- Compare hash on each analysis request
- Only re-parse if hash changed
- Update dependency graph incrementally

**Persistence Strategy**:
- Hot cache: Redis (Tier 3) - 1 hour TTL
- Warm cache: SQLite (Tier 2) - 24 hour TTL  
- Cold storage: Disk JSON files - Permanent
- Location: `.documee/analysis/{codebase_id}/`

**Plugin Architecture**:
```python
# Users can add custom detectors
class CustomPatternDetector(BasePatternDetector):
    def detect(self, symbol_info, file_content):
        # Custom logic
        return patterns

# Register in config.yaml
pattern_detectors:
  - ReactPatternDetector
  - APIPatternDetector
  - CustomPatternDetector  # User-defined
```

**Linter Integration**:
- Run linters asynchronously (non-blocking)
- Parse linter output (JSON format)
- Include in analysis results as `linter_issues`
- Don't fail analysis if linter fails
- Configurable: `enable_linters: true/false`

**Jupyter Notebook Support**:
- Parse .ipynb as JSON
- Extract code cells only
- Concatenate cells for analysis
- Track cell boundaries in line numbers
- Flag as `notebook: true` in analysis
