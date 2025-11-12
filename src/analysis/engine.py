"""
Main Analysis Engine orchestrator.

This module coordinates all analysis components and provides the main API
for analyzing files and codebases.
"""

import hashlib
import logging
import asyncio
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from .config import AnalysisConfig
from .ast_parser import ASTParserManager
from .symbol_extractor import SymbolExtractor
from .pattern_detector import PatternDetector, ReactPatternDetector, APIPatternDetector, DatabasePatternDetector, AuthPatternDetector
from .language_pattern_detector import PythonPatternDetector, JavaScriptPatternDetector
from .universal_language_detectors import (
    JavaPatternDetector, GoPatternDetector, RustPatternDetector,
    CppPatternDetector, CSharpPatternDetector, RubyPatternDetector, PHPPatternDetector
)
from .dependency_analyzer import DependencyAnalyzer
from .teaching_value_scorer import TeachingValueScorer
from .complexity_analyzer import ComplexityAnalyzer
from .documentation_coverage import DocumentationCoverageAnalyzer
from .persistence import PersistenceManager
from .linter_integration import LinterIntegration
from .notebook_analyzer import NotebookAnalyzer
from src.models.analysis_models import (
    FileAnalysis, CodebaseAnalysis, CodebaseMetrics,
    ComplexityMetrics as ComplexityMetricsModel,
    SymbolInfo as SymbolInfoModel,
    FunctionInfo as FunctionInfoModel,
    ClassInfo as ClassInfoModel,
    ImportInfo as ImportInfoModel
)

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """
    Main analysis engine orchestrator with incremental analysis support.
    
    Coordinates AST parsing, symbol extraction, pattern detection,
    dependency analysis, and teaching value scoring.
    """
    
    def __init__(self, cache_manager, config: AnalysisConfig):
        """
        Initialize the Analysis Engine.
        
        Args:
            cache_manager: Cache manager instance for caching results
            config: Analysis configuration
        """
        self.cache = cache_manager
        self.config = config
        
        # Performance metrics tracking
        self.metrics = {
            'total_files_analyzed': 0,
            'total_cache_hits': 0,
            'total_cache_misses': 0,
            'total_analysis_time_ms': 0.0,
            'slow_operations': [],  # List of (file_path, duration_ms)
            'errors': [],  # List of (file_path, error_message)
            'file_analysis_times': []  # List of (file_path, duration_ms)
        }
        
        # Initialize all analysis components
        logger.info("Initializing Analysis Engine components...")
        
        try:
            self.parser = ASTParserManager(config)
            logger.debug("AST Parser Manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AST Parser Manager: {e}", exc_info=True)
            raise
        
        try:
            self.symbol_extractor = SymbolExtractor()
            logger.debug("Symbol Extractor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Symbol Extractor: {e}", exc_info=True)
            raise
        
        try:
            self.complexity_analyzer = ComplexityAnalyzer()
            logger.debug("Complexity Analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Complexity Analyzer: {e}", exc_info=True)
            raise
        
        try:
            self.doc_coverage_analyzer = DocumentationCoverageAnalyzer()
            logger.debug("Documentation Coverage Analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Documentation Coverage Analyzer: {e}", exc_info=True)
            raise
        
        # Initialize pattern detector with default detectors
        try:
            self.pattern_detector = PatternDetector()
            # Framework-specific detectors
            self.pattern_detector.register_detector(ReactPatternDetector())
            self.pattern_detector.register_detector(APIPatternDetector())
            self.pattern_detector.register_detector(DatabasePatternDetector())
            self.pattern_detector.register_detector(AuthPatternDetector())
            # Language-specific detectors (Universal God Mode)
            self.pattern_detector.register_detector(PythonPatternDetector())
            self.pattern_detector.register_detector(JavaScriptPatternDetector())
            self.pattern_detector.register_detector(JavaPatternDetector())
            self.pattern_detector.register_detector(GoPatternDetector())
            self.pattern_detector.register_detector(RustPatternDetector())
            self.pattern_detector.register_detector(CppPatternDetector())
            self.pattern_detector.register_detector(CSharpPatternDetector())
            self.pattern_detector.register_detector(RubyPatternDetector())
            self.pattern_detector.register_detector(PHPPatternDetector())
            logger.debug("Pattern Detector initialized with 13 detectors (4 framework + 9 language) - Universal God Mode")
        except Exception as e:
            logger.error(f"Failed to initialize Pattern Detector: {e}", exc_info=True)
            raise
        
        try:
            self.dependency_analyzer = DependencyAnalyzer()
            logger.debug("Dependency Analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Dependency Analyzer: {e}", exc_info=True)
            raise
        
        try:
            self.teaching_value_scorer = TeachingValueScorer(config)
            logger.debug("Teaching Value Scorer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Teaching Value Scorer: {e}", exc_info=True)
            raise
        
        try:
            self.persistence = PersistenceManager(config.persistence_path)
            logger.debug(f"Persistence Manager initialized (path: {config.persistence_path})")
        except Exception as e:
            logger.error(f"Failed to initialize Persistence Manager: {e}", exc_info=True)
            raise
        
        try:
            self.linter = LinterIntegration(config)
            logger.debug(f"Linter Integration initialized (enabled: {config.enable_linters})")
        except Exception as e:
            logger.error(f"Failed to initialize Linter Integration: {e}", exc_info=True)
            raise
        
        try:
            self.notebook_analyzer = NotebookAnalyzer()
            logger.debug("Notebook Analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Notebook Analyzer: {e}", exc_info=True)
            raise
        
        logger.info("Analysis Engine initialized successfully with all components")
    
    def _convert_symbol_info(self, symbol_info) -> SymbolInfoModel:
        """
        Convert symbol_extractor.SymbolInfo to models.SymbolInfo.
        
        Args:
            symbol_info: SymbolInfo from symbol_extractor
        
        Returns:
            SymbolInfo model instance
        """
        # Convert functions
        functions = [
            FunctionInfoModel(
                name=f.name,
                parameters=f.parameters,
                return_type=f.return_type,
                docstring=f.docstring,
                start_line=f.start_line,
                end_line=f.end_line,
                complexity=f.complexity,
                is_async=f.is_async,
                decorators=f.decorators
            )
            for f in symbol_info.functions
        ]
        
        # Convert classes
        classes = [
            ClassInfoModel(
                name=c.name,
                methods=[
                    FunctionInfoModel(
                        name=m.name,
                        parameters=m.parameters,
                        return_type=m.return_type,
                        docstring=m.docstring,
                        start_line=m.start_line,
                        end_line=m.end_line,
                        complexity=m.complexity,
                        is_async=m.is_async,
                        decorators=m.decorators
                    )
                    for m in c.methods
                ],
                base_classes=c.base_classes,
                docstring=c.docstring,
                start_line=c.start_line,
                end_line=c.end_line,
                decorators=c.decorators
            )
            for c in symbol_info.classes
        ]
        
        # Convert imports
        imports = [
            ImportInfoModel(
                module=i.module,
                imported_symbols=i.imported_symbols,
                is_relative=i.is_relative,
                import_type=i.import_type,
                line_number=i.line_number
            )
            for i in symbol_info.imports
        ]
        
        return SymbolInfoModel(
            functions=functions,
            classes=classes,
            imports=imports,
            exports=symbol_info.exports
        )
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of file content.
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA-256 hash as hex string
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _is_analyzable(self, file_path: str) -> bool:
        """
        Check if file can be analyzed.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if file extension is supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.ipynb']
    
    async def _get_cached_analysis(self, file_path: str, file_hash: str) -> Optional[FileAnalysis]:
        """
        Retrieve cached analysis if available and hash matches.
        
        Args:
            file_path: Path to file
            file_hash: Current file hash
        
        Returns:
            FileAnalysis if cached, None otherwise
        """
        cache_key = f"file:{file_hash}"
        try:
            cached_dict = await self.cache.get_analysis(cache_key)
            
            if cached_dict:
                logger.debug(f"Cache hit for {file_path} (hash: {file_hash[:8]}...)")
                self.metrics['total_cache_hits'] += 1
                # Convert dict back to FileAnalysis
                return FileAnalysis.from_dict(cached_dict)
            else:
                logger.debug(f"Cache miss for {file_path} (hash: {file_hash[:8]}...)")
                self.metrics['total_cache_misses'] += 1
        except Exception as e:
            logger.warning(f"Error retrieving from cache for {file_path}: {e}")
            self.metrics['total_cache_misses'] += 1
        
        return None
    
    async def _cache_analysis(self, file_path: str, file_hash: str, analysis: FileAnalysis):
        """
        Cache analysis results with file hash as key.
        
        Args:
            file_path: Path to file
            file_hash: File hash
            analysis: Analysis result to cache
        """
        cache_key = f"file:{file_hash}"
        try:
            # Convert FileAnalysis to dict for caching
            analysis_dict = analysis.to_dict()
            await self.cache.set_analysis(cache_key, analysis_dict, ttl=self.config.cache_ttl_seconds)
            logger.debug(f"Cached analysis for {file_path} (hash: {file_hash[:8]}...)")
        except Exception as e:
            logger.warning(f"Error caching analysis: {e}")
    
    async def analyze_file(self, file_path: str, force: bool = False) -> FileAnalysis:
        """
        Analyze single file with caching and incremental support.
        
        Args:
            file_path: Path to file to analyze
            force: If True, bypass cache and re-analyze
        
        Returns:
            FileAnalysis with all extracted information
        
        Example:
            >>> engine = AnalysisEngine(cache, config)
            >>> analysis = await engine.analyze_file("src/main.py")
            >>> print(f"Teaching value: {analysis.teaching_value.total_score}")
        """
        start_time = datetime.now()
        logger.info(f"Starting analysis for file: {file_path}")
        
        # Calculate file hash for incremental analysis
        file_hash = self._calculate_file_hash(file_path)
        if not file_hash:
            logger.error(f"Failed to calculate file hash for {file_path}")
        
        # Check cache if not forcing re-analysis
        if not force and file_hash:
            cached = await self._get_cached_analysis(file_path, file_hash)
            if cached:
                cached.cache_hit = True
                elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
                logger.info(f"Analysis complete for {file_path} (cached) in {elapsed_ms:.0f}ms")
                return cached
        
        logger.debug(f"Performing full analysis for {file_path} (force={force})")
        
        # Handle Jupyter notebooks
        is_notebook = file_path.endswith('.ipynb')
        if is_notebook:
            logger.debug(f"Detected Jupyter notebook: {file_path}")
            try:
                notebook_code = self.notebook_analyzer.extract_code(file_path)
                source_code = notebook_code.full_code.encode('utf-8')
                logger.debug(f"Extracted {notebook_code.total_cells} cells from notebook {file_path}")
            except Exception as e:
                error_msg = f"Failed to extract notebook code: {e}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                self.metrics['errors'].append((file_path, error_msg))
                # Return error analysis
                return self._create_error_analysis(
                    file_path, 
                    "python",
                    error_msg,
                    start_time
                )
        else:
            try:
                with open(file_path, 'rb') as f:
                    source_code = f.read()
                logger.debug(f"Read {len(source_code)} bytes from {file_path}")
            except Exception as e:
                error_msg = f"Failed to read file: {e}"
                logger.error(f"{error_msg} - {file_path}\n{traceback.format_exc()}")
                self.metrics['errors'].append((file_path, error_msg))
                return self._create_error_analysis(
                    file_path,
                    "unknown",
                    error_msg,
                    start_time
                )
        
        # Parse file
        try:
            logger.debug(f"Parsing file: {file_path}")
            parse_result = self.parser.parse_file(file_path)
            logger.debug(f"Parse complete for {file_path} (language: {parse_result.language}, has_errors: {parse_result.has_errors})")
            
            if parse_result.has_errors:
                logger.warning(f"Parse errors detected in {file_path}: {len(parse_result.error_nodes)} error nodes")
        except Exception as e:
            error_msg = f"Parse error: {e}"
            logger.error(f"Failed to parse {file_path}: {e}\n{traceback.format_exc()}")
            self.metrics['errors'].append((file_path, error_msg))
            return self._create_error_analysis(
                file_path,
                "unknown",
                error_msg,
                start_time
            )
        
        # Extract symbols
        try:
            logger.debug(f"Extracting symbols from {file_path}")
            symbol_info_extractor = self.symbol_extractor.extract_symbols(parse_result)
            logger.debug(
                f"Symbol extraction complete for {file_path}: "
                f"{len(symbol_info_extractor.functions)} functions, "
                f"{len(symbol_info_extractor.classes)} classes, "
                f"{len(symbol_info_extractor.imports)} imports"
            )
        except Exception as e:
            error_msg = f"Symbol extraction error: {e}"
            logger.error(f"Failed to extract symbols from {file_path}: {e}\n{traceback.format_exc()}")
            self.metrics['errors'].append((file_path, error_msg))
            return self._create_error_analysis(
                file_path,
                parse_result.language,
                error_msg,
                start_time
            )
        
        # Detect patterns
        try:
            logger.debug(f"Detecting patterns in {file_path}")
            file_content = source_code.decode('utf-8', errors='ignore')
            patterns = self.pattern_detector.detect_patterns_in_file(
                symbol_info_extractor,
                file_content,
                file_path
            )
            logger.debug(f"Pattern detection complete for {file_path}: {len(patterns)} patterns detected")
        except Exception as e:
            logger.warning(f"Pattern detection failed for {file_path}: {e}\n{traceback.format_exc()}")
            patterns = []
        
        # Calculate complexity metrics
        try:
            logger.debug(f"Calculating complexity metrics for {file_path}")
            complexity_metrics = self.complexity_analyzer.analyze_file(symbol_info_extractor)
            
            # Convert to model format
            complexity_metrics_model = ComplexityMetricsModel(
                avg_complexity=complexity_metrics.avg_complexity,
                max_complexity=complexity_metrics.max_complexity,
                min_complexity=complexity_metrics.min_complexity,
                high_complexity_functions=[
                    func.name for func in symbol_info_extractor.functions 
                    if func.complexity > 10
                ] + [
                    f"{cls.name}.{method.name}" 
                    for cls in symbol_info_extractor.classes 
                    for method in cls.methods 
                    if method.complexity > 10
                ],
                trivial_functions=[
                    func.name for func in symbol_info_extractor.functions 
                    if func.complexity < 2
                ] + [
                    f"{cls.name}.{method.name}" 
                    for cls in symbol_info_extractor.classes 
                    for method in cls.methods 
                    if method.complexity < 2
                ],
                avg_nesting_depth=complexity_metrics.avg_nesting_depth
            )
            logger.debug(
                f"Complexity analysis complete for {file_path}: "
                f"avg={complexity_metrics.avg_complexity:.1f}, "
                f"max={complexity_metrics.max_complexity}, "
                f"high_complexity_count={len(complexity_metrics_model.high_complexity_functions)}"
            )
        except Exception as e:
            logger.warning(f"Complexity analysis failed for {file_path}: {e}\n{traceback.format_exc()}")
            complexity_metrics_model = ComplexityMetricsModel(
                avg_complexity=0.0,
                max_complexity=0,
                min_complexity=0,
                high_complexity_functions=[],
                trivial_functions=[],
                avg_nesting_depth=0.0
            )
        
        # Calculate documentation coverage
        try:
            logger.debug(f"Calculating documentation coverage for {file_path}")
            doc_coverage = self.doc_coverage_analyzer.calculate_coverage(
                symbol_info_extractor,
                file_content,
                parse_result.language
            )
            logger.debug(f"Documentation coverage for {file_path}: {doc_coverage.total_score:.2%}")
        except Exception as e:
            logger.warning(f"Documentation coverage analysis failed for {file_path}: {e}\n{traceback.format_exc()}")
            from .documentation_coverage import DocumentationCoverage
            doc_coverage = DocumentationCoverage()
        
        # Score teaching value
        try:
            logger.debug(f"Scoring teaching value for {file_path}")
            teaching_value_result = self.teaching_value_scorer.score_file(
                symbol_info_extractor,
                patterns,
                complexity_metrics,
                doc_coverage
            )
            # Convert to model format
            from src.models.analysis_models import TeachingValueScore as TeachingValueScoreModel
            teaching_value = TeachingValueScoreModel(
                total_score=teaching_value_result.total_score,
                documentation_score=teaching_value_result.documentation_score,
                complexity_score=teaching_value_result.complexity_score,
                pattern_score=teaching_value_result.pattern_score,
                structure_score=teaching_value_result.structure_score,
                explanation=teaching_value_result.explanation,
                factors=teaching_value_result.factors
            )
            logger.debug(f"Teaching value score for {file_path}: {teaching_value.total_score:.2f}")
        except Exception as e:
            logger.warning(f"Teaching value scoring failed for {file_path}: {e}\n{traceback.format_exc()}")
            from src.models.analysis_models import TeachingValueScore as TeachingValueScoreModel
            teaching_value = TeachingValueScoreModel(
                total_score=0.0,
                documentation_score=0.0,
                complexity_score=0.0,
                pattern_score=0.0,
                structure_score=0.0,
                explanation="Scoring failed",
                factors={}
            )
        
        # Run linters asynchronously (non-blocking)
        try:
            logger.debug(f"Running linters for {file_path}")
            linter_issues = await self.linter.run_linters(
                file_path,
                parse_result.language
            )
            if linter_issues:
                logger.debug(f"Linter found {len(linter_issues)} issues in {file_path}")
        except Exception as e:
            logger.warning(f"Linter execution failed for {file_path}: {e}\n{traceback.format_exc()}")
            linter_issues = []
        
        # Convert symbol_info to model version for storage
        symbol_info_model = self._convert_symbol_info(symbol_info_extractor)
        
        # Create analysis result
        analysis = FileAnalysis(
            file_path=file_path,
            language=parse_result.language,
            symbol_info=symbol_info_model,
            patterns=patterns,
            teaching_value=teaching_value,
            complexity_metrics=complexity_metrics_model,
            documentation_coverage=doc_coverage.total_score,
            linter_issues=linter_issues,
            has_errors=parse_result.has_errors,
            errors=[str(node) for node in parse_result.error_nodes] if parse_result.has_errors else [],
            analyzed_at=datetime.now().isoformat(),
            cache_hit=False,
            is_notebook=is_notebook
        )
        
        # Cache results
        if file_hash:
            await self._cache_analysis(file_path, file_hash, analysis)
        
        # Track performance metrics
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.metrics['total_files_analyzed'] += 1
        self.metrics['total_analysis_time_ms'] += elapsed_ms
        self.metrics['file_analysis_times'].append((file_path, elapsed_ms))
        
        # Log slow operations (>1000ms)
        if elapsed_ms > 1000:
            logger.warning(
                f"Slow operation detected: Analysis of {file_path} took {elapsed_ms:.0f}ms "
                f"(threshold: 1000ms)"
            )
            self.metrics['slow_operations'].append((file_path, elapsed_ms))
        
        logger.info(
            f"Analysis complete for {file_path} in {elapsed_ms:.0f}ms "
            f"(teaching_value: {analysis.teaching_value.total_score:.2f}, "
            f"functions: {len(analysis.symbol_info.functions)}, "
            f"classes: {len(analysis.symbol_info.classes)})"
        )
        
        return analysis
    
    def _create_error_analysis(
        self,
        file_path: str,
        language: str,
        error_message: str,
        start_time: datetime
    ) -> FileAnalysis:
        """
        Create an error analysis result when analysis fails.
        
        Args:
            file_path: Path to file
            language: Programming language
            error_message: Error message
            start_time: Analysis start time
        
        Returns:
            FileAnalysis with error flag set
        """
        from src.models.analysis_models import TeachingValueScore
        
        return FileAnalysis(
            file_path=file_path,
            language=language,
            symbol_info=SymbolInfoModel(
                functions=[],
                classes=[],
                imports=[],
                exports=[]
            ),
            patterns=[],
            teaching_value=TeachingValueScore(
                total_score=0.0,
                documentation_score=0.0,
                complexity_score=0.0,
                pattern_score=0.0,
                structure_score=0.0,
                explanation="Analysis failed",
                factors={}
            ),
            complexity_metrics=ComplexityMetricsModel(
                avg_complexity=0.0,
                max_complexity=0,
                min_complexity=0,
                high_complexity_functions=[],
                trivial_functions=[],
                avg_nesting_depth=0.0
            ),
            documentation_coverage=0.0,
            linter_issues=[],
            has_errors=True,
            errors=[error_message],
            analyzed_at=datetime.now().isoformat(),
            cache_hit=False,
            is_notebook=False
        )
    
    async def analyze_codebase(
        self,
        codebase_id: str,
        incremental: bool = True
    ) -> CodebaseAnalysis:
        """
        Analyze entire codebase with parallel processing and incremental support.
        
        Args:
            codebase_id: ID of codebase to analyze
            incremental: If True, only analyze changed files
        
        Returns:
            CodebaseAnalysis with all files analyzed
        
        Example:
            >>> engine = AnalysisEngine(cache, config)
            >>> analysis = await engine.analyze_codebase("my_project", incremental=True)
            >>> print(f"Analyzed {analysis.metrics.total_files} files")
        """
        start_time = datetime.now()
        logger.info(
            f"Starting codebase analysis: {codebase_id} "
            f"(incremental={incremental}, enable_incremental={self.config.enable_incremental})"
        )
        
        # Get scan results
        try:
            scan_result = await self.cache.get_analysis(f"scan:{codebase_id}")
            if not scan_result:
                error_msg = f"Codebase not scanned. Call scan_codebase first for codebase_id: {codebase_id}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            logger.debug(f"Retrieved scan results for {codebase_id}")
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Failed to retrieve scan results for {codebase_id}: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise ValueError(error_msg)
        
        # Load previous analysis for incremental mode
        previous_analysis = None
        previous_hashes = {}
        if incremental and self.config.enable_incremental:
            try:
                logger.debug(f"Loading previous analysis for {codebase_id}")
                previous_analysis = self.persistence.load_analysis(codebase_id)
                previous_hashes = self.persistence.get_file_hashes(codebase_id)
                if previous_analysis:
                    logger.info(
                        f"Loaded previous analysis for {codebase_id}: "
                        f"{len(previous_analysis.file_analyses)} files, "
                        f"{len(previous_hashes)} hashes"
                    )
                else:
                    logger.info(f"No previous analysis found for {codebase_id}, performing full analysis")
            except Exception as e:
                logger.warning(f"Failed to load previous analysis for {codebase_id}: {e}")
                previous_analysis = None
                previous_hashes = {}
        
        # Determine which files to analyze
        files_to_analyze = []
        current_hashes = {}
        
        # Get file list from scan result
        # scan_result contains 'path' which is the root directory
        # We need to walk the directory to get all analyzable files
        file_list = []
        
        if isinstance(scan_result, dict) and 'path' in scan_result:
            root_path = scan_result['path']
            logger.debug(f"Scanning directory for files: {root_path}")
            
            # Walk the directory to find all analyzable files
            import os
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Filter out ignored directories
                dirnames[:] = [d for d in dirnames if d not in [
                    'node_modules', '.git', '__pycache__', 'venv', '.venv',
                    'dist', 'build', '.next', '.cache'
                ]]
                
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if self._is_analyzable(file_path):
                        file_list.append(file_path)
            
            logger.info(f"Found {len(file_list)} analyzable files")
        else:
            logger.error(f"Invalid scan result format for {codebase_id}: missing 'path' key")
            raise ValueError("Invalid scan result format: missing 'path' key")
        
        for file_path in file_list:
            if not self._is_analyzable(file_path):
                continue
            
            file_hash = self._calculate_file_hash(file_path)
            if not file_hash:
                logger.warning(f"Could not calculate hash for {file_path}, skipping")
                continue
            
            current_hashes[file_path] = file_hash
            
            # In incremental mode, skip unchanged files
            if incremental and self.config.enable_incremental and file_path in previous_hashes:
                if previous_hashes[file_path] == file_hash:
                    logger.debug(f"Skipping unchanged file: {file_path}")
                    continue
                else:
                    logger.debug(f"File changed: {file_path}")
            
            files_to_analyze.append(file_path)
        
        logger.info(
            f"Analyzing {len(files_to_analyze)} files "
            f"(total: {len(current_hashes)}, incremental: {incremental})"
        )
        
        # Initialize file analyses dict
        file_analyses = {}
        reused_count = 0
        
        # Reuse previous analyses for unchanged files
        if previous_analysis and incremental and self.config.enable_incremental:
            for file_path, analysis in previous_analysis.file_analyses.items():
                if file_path not in files_to_analyze and file_path in current_hashes:
                    # File unchanged, reuse previous analysis
                    file_analyses[file_path] = analysis
                    reused_count += 1
                    logger.debug(f"Reusing previous analysis for {file_path}")
            
            if reused_count > 0:
                logger.info(f"Reusing {reused_count} unchanged file analyses from previous run")
        
        # Analyze new/changed files in parallel
        if files_to_analyze:
            logger.info(
                f"Analyzing {len(files_to_analyze)} files in parallel "
                f"(max_workers: {self.config.max_parallel_files})..."
            )
            
            # Create analysis tasks
            tasks = [self.analyze_file(fp) for fp in files_to_analyze]
            
            # Run in parallel with asyncio.gather
            parallel_start = datetime.now()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            parallel_elapsed_ms = (datetime.now() - parallel_start).total_seconds() * 1000
            
            # Process results
            success_count = 0
            error_count = 0
            for file_path, result in zip(files_to_analyze, results):
                if isinstance(result, Exception):
                    error_count += 1
                    error_msg = str(result)
                    logger.error(f"Failed to analyze {file_path}: {error_msg}\n{traceback.format_exc()}")
                    self.metrics['errors'].append((file_path, error_msg))
                    # Create error analysis
                    file_analyses[file_path] = self._create_error_analysis(
                        file_path,
                        "unknown",
                        error_msg,
                        start_time
                    )
                else:
                    success_count += 1
                    file_analyses[file_path] = result
            
            logger.info(
                f"Parallel file analysis complete: {success_count} succeeded, {error_count} failed "
                f"in {parallel_elapsed_ms:.0f}ms "
                f"(avg: {parallel_elapsed_ms / len(files_to_analyze):.0f}ms per file)"
            )
        
        logger.info(f"Total file analyses: {len(file_analyses)} files")
        
        # Build dependency graph
        try:
            logger.info("Building dependency graph...")
            dep_start = datetime.now()
            dependency_graph = self.dependency_analyzer.analyze_dependencies(
                codebase_id,
                file_analyses
            )
            dep_elapsed_ms = (datetime.now() - dep_start).total_seconds() * 1000
            logger.info(
                f"Dependency graph built in {dep_elapsed_ms:.0f}ms: "
                f"{len(dependency_graph.nodes)} nodes, "
                f"{len(dependency_graph.edges)} edges, "
                f"{len(dependency_graph.circular_dependencies)} circular dependencies"
            )
        except Exception as e:
            logger.error(f"Failed to build dependency graph: {e}\n{traceback.format_exc()}")
            # Create empty dependency graph
            from .dependency_analyzer import DependencyGraph
            dependency_graph = DependencyGraph()
        
        # Detect global patterns
        try:
            logger.info("Detecting global patterns...")
            pattern_start = datetime.now()
            global_patterns = self.pattern_detector.detect_global_patterns(file_analyses)
            pattern_elapsed_ms = (datetime.now() - pattern_start).total_seconds() * 1000
            logger.info(f"Global pattern detection complete in {pattern_elapsed_ms:.0f}ms: {len(global_patterns)} patterns")
        except Exception as e:
            logger.error(f"Failed to detect global patterns: {e}\n{traceback.format_exc()}")
            global_patterns = []
        
        # Rank files by teaching value
        try:
            logger.debug("Ranking files by teaching value...")
            top_teaching_files = sorted(
                [(fp, fa.teaching_value.total_score) for fp, fa in file_analyses.items()],
                key=lambda x: x[1],
                reverse=True
            )[:20]  # Top 20 files
            if top_teaching_files:
                logger.info(
                    f"Top teaching file: {top_teaching_files[0][0]} "
                    f"(score: {top_teaching_files[0][1]:.2f})"
                )
        except Exception as e:
            logger.error(f"Failed to rank teaching files: {e}\n{traceback.format_exc()}")
            top_teaching_files = []
        
        # Calculate codebase metrics
        try:
            logger.debug("Calculating codebase metrics...")
            metrics = self._calculate_codebase_metrics(file_analyses, start_time)
            logger.info(
                f"Codebase metrics: {metrics.total_files} files, "
                f"{metrics.total_functions} functions, "
                f"{metrics.total_classes} classes, "
                f"avg_complexity={metrics.avg_complexity:.1f}, "
                f"avg_doc_coverage={metrics.avg_documentation_coverage:.2%}, "
                f"cache_hit_rate={metrics.cache_hit_rate:.2%}"
            )
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}\n{traceback.format_exc()}")
            metrics = CodebaseMetrics(
                total_files=len(file_analyses),
                total_functions=0,
                total_classes=0,
                avg_complexity=0.0,
                avg_documentation_coverage=0.0,
                total_patterns_detected=0,
                analysis_time_ms=0.0,
                cache_hit_rate=0.0
            )
        
        # Create codebase analysis
        analysis = CodebaseAnalysis(
            codebase_id=codebase_id,
            file_analyses=file_analyses,
            dependency_graph=dependency_graph,
            global_patterns=global_patterns,
            top_teaching_files=top_teaching_files,
            metrics=metrics,
            analyzed_at=datetime.now().isoformat()
        )
        
        # Persist to disk
        try:
            logger.info(f"Persisting analysis to disk: {self.config.persistence_path}/{codebase_id}")
            persist_start = datetime.now()
            self.persistence.save_analysis(codebase_id, analysis)
            self.persistence.save_file_hashes(codebase_id, current_hashes)
            persist_elapsed_ms = (datetime.now() - persist_start).total_seconds() * 1000
            logger.info(f"Analysis persisted to disk in {persist_elapsed_ms:.0f}ms")
        except Exception as e:
            logger.error(f"Failed to persist analysis: {e}\n{traceback.format_exc()}")
        
        # Cache in memory
        try:
            logger.debug("Caching analysis in memory...")
            await self.cache.set_analysis(
                f"codebase:{codebase_id}",
                analysis.to_dict(),
                ttl=self.config.cache_ttl_seconds
            )
            logger.debug(f"Analysis cached with TTL={self.config.cache_ttl_seconds}s")
        except Exception as e:
            logger.error(f"Failed to cache analysis: {e}\n{traceback.format_exc()}")
        
        # Calculate and log final metrics
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log batch analysis summary
        logger.info("=" * 80)
        logger.info(f"BATCH ANALYSIS SUMMARY - {codebase_id}")
        logger.info("=" * 80)
        logger.info(f"Total files analyzed: {metrics.total_files}")
        logger.info(f"Total functions: {metrics.total_functions}")
        logger.info(f"Total classes: {metrics.total_classes}")
        logger.info(f"Total patterns detected: {metrics.total_patterns_detected}")
        logger.info(f"Average complexity: {metrics.avg_complexity:.2f}")
        logger.info(f"Average documentation coverage: {metrics.avg_documentation_coverage:.2%}")
        logger.info(f"Cache hit rate: {metrics.cache_hit_rate:.2%}")
        logger.info(f"Total analysis time: {elapsed_ms:.0f}ms ({elapsed_ms/1000:.1f}s)")
        logger.info(f"Average time per file: {metrics.analysis_time_ms / metrics.total_files:.0f}ms")
        
        # Log cache statistics
        total_cache_requests = self.metrics['total_cache_hits'] + self.metrics['total_cache_misses']
        if total_cache_requests > 0:
            cache_hit_rate = self.metrics['total_cache_hits'] / total_cache_requests
            logger.info(f"Cache hits: {self.metrics['total_cache_hits']}")
            logger.info(f"Cache misses: {self.metrics['total_cache_misses']}")
            logger.info(f"Session cache hit rate: {cache_hit_rate:.2%}")
        
        # Log slow operations
        if self.metrics['slow_operations']:
            logger.warning(f"Slow operations detected: {len(self.metrics['slow_operations'])}")
            for file_path, duration_ms in self.metrics['slow_operations'][:5]:  # Top 5 slowest
                logger.warning(f"  - {file_path}: {duration_ms:.0f}ms")
        
        # Log errors
        if self.metrics['errors']:
            logger.error(f"Errors encountered: {len(self.metrics['errors'])}")
            for file_path, error_msg in self.metrics['errors'][:5]:  # First 5 errors
                logger.error(f"  - {file_path}: {error_msg}")
        
        logger.info("=" * 80)
        
        logger.info(
            f"Codebase analysis complete for {codebase_id}: "
            f"{metrics.total_files} files, "
            f"{metrics.total_functions} functions, "
            f"{metrics.total_classes} classes "
            f"in {elapsed_ms:.0f}ms"
        )
        
        return analysis
    
    def _calculate_codebase_metrics(
        self,
        file_analyses: Dict[str, FileAnalysis],
        start_time: datetime
    ) -> CodebaseMetrics:
        """
        Calculate aggregate metrics for the codebase.
        
        Args:
            file_analyses: Dictionary of file analyses
            start_time: Analysis start time
        
        Returns:
            CodebaseMetrics with aggregate statistics
        """
        total_files = len(file_analyses)
        total_functions = 0
        total_classes = 0
        complexities = []
        doc_coverages = []
        total_patterns = 0
        cache_hits = 0
        
        for analysis in file_analyses.values():
            # Count functions and classes
            total_functions += len(analysis.symbol_info.functions)
            total_classes += len(analysis.symbol_info.classes)
            
            # Collect complexity scores
            if analysis.complexity_metrics.avg_complexity > 0:
                complexities.append(analysis.complexity_metrics.avg_complexity)
            
            # Collect documentation coverage
            doc_coverages.append(analysis.documentation_coverage)
            
            # Count patterns
            total_patterns += len(analysis.patterns)
            
            # Count cache hits
            if analysis.cache_hit:
                cache_hits += 1
        
        # Calculate averages
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0.0
        avg_doc_coverage = sum(doc_coverages) / len(doc_coverages) if doc_coverages else 0.0
        cache_hit_rate = cache_hits / total_files if total_files > 0 else 0.0
        
        # Calculate analysis time
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return CodebaseMetrics(
            total_files=total_files,
            total_functions=total_functions,
            total_classes=total_classes,
            avg_complexity=round(avg_complexity, 2),
            avg_documentation_coverage=round(avg_doc_coverage, 3),
            total_patterns_detected=total_patterns,
            analysis_time_ms=round(elapsed_ms, 2),
            cache_hit_rate=round(cache_hit_rate, 3)
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics for the analysis engine.
        
        Returns:
            Dictionary containing performance metrics:
                - total_files_analyzed: Total number of files analyzed
                - total_cache_hits: Number of cache hits
                - total_cache_misses: Number of cache misses
                - cache_hit_rate: Cache hit rate (0.0-1.0)
                - total_analysis_time_ms: Total time spent analyzing
                - avg_time_per_file_ms: Average time per file
                - slow_operations_count: Number of slow operations (>1000ms)
                - errors_count: Number of errors encountered
                - file_analysis_times: List of (file_path, duration_ms) tuples
        """
        total_requests = self.metrics['total_cache_hits'] + self.metrics['total_cache_misses']
        cache_hit_rate = (
            self.metrics['total_cache_hits'] / total_requests 
            if total_requests > 0 else 0.0
        )
        
        avg_time_per_file = (
            self.metrics['total_analysis_time_ms'] / self.metrics['total_files_analyzed']
            if self.metrics['total_files_analyzed'] > 0 else 0.0
        )
        
        return {
            'total_files_analyzed': self.metrics['total_files_analyzed'],
            'total_cache_hits': self.metrics['total_cache_hits'],
            'total_cache_misses': self.metrics['total_cache_misses'],
            'cache_hit_rate': round(cache_hit_rate, 3),
            'total_analysis_time_ms': round(self.metrics['total_analysis_time_ms'], 2),
            'avg_time_per_file_ms': round(avg_time_per_file, 2),
            'slow_operations_count': len(self.metrics['slow_operations']),
            'errors_count': len(self.metrics['errors']),
            'file_analysis_times': self.metrics['file_analysis_times']
        }
    
    def reset_performance_metrics(self):
        """Reset performance metrics to initial state."""
        logger.info("Resetting performance metrics")
        self.metrics = {
            'total_files_analyzed': 0,
            'total_cache_hits': 0,
            'total_cache_misses': 0,
            'total_analysis_time_ms': 0.0,
            'slow_operations': [],
            'errors': [],
            'file_analysis_times': []
        }
    
    def log_performance_summary(self):
        """Log a summary of performance metrics."""
        metrics = self.get_performance_metrics()
        
        logger.info("=" * 80)
        logger.info("PERFORMANCE METRICS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total files analyzed: {metrics['total_files_analyzed']}")
        logger.info(f"Total analysis time: {metrics['total_analysis_time_ms']:.0f}ms")
        logger.info(f"Average time per file: {metrics['avg_time_per_file_ms']:.0f}ms")
        logger.info(f"Cache hits: {metrics['total_cache_hits']}")
        logger.info(f"Cache misses: {metrics['total_cache_misses']}")
        logger.info(f"Cache hit rate: {metrics['cache_hit_rate']:.2%}")
        logger.info(f"Slow operations (>1000ms): {metrics['slow_operations_count']}")
        logger.info(f"Errors encountered: {metrics['errors_count']}")
        logger.info("=" * 80)
