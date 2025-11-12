"""
Main Analysis Engine orchestrator.

This module coordinates all analysis components and provides the main API
for analyzing files and codebases.
"""

import hashlib
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from .config import AnalysisConfig
from .ast_parser import ASTParserManager
from .symbol_extractor import SymbolExtractor
from .pattern_detector import PatternDetector, ReactPatternDetector, APIPatternDetector, DatabasePatternDetector, AuthPatternDetector
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
        
        # Initialize all analysis components
        self.parser = ASTParserManager(config)
        self.symbol_extractor = SymbolExtractor()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.doc_coverage_analyzer = DocumentationCoverageAnalyzer()
        
        # Initialize pattern detector with default detectors
        self.pattern_detector = PatternDetector()
        self.pattern_detector.register_detector(ReactPatternDetector())
        self.pattern_detector.register_detector(APIPatternDetector())
        self.pattern_detector.register_detector(DatabasePatternDetector())
        self.pattern_detector.register_detector(AuthPatternDetector())
        
        self.dependency_analyzer = DependencyAnalyzer()
        self.teaching_value_scorer = TeachingValueScorer(config)
        self.persistence = PersistenceManager(config.persistence_path)
        self.linter = LinterIntegration(config)
        self.notebook_analyzer = NotebookAnalyzer()
        
        logger.info("Analysis Engine initialized with all components")
    
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
                # Convert dict back to FileAnalysis
                return FileAnalysis.from_dict(cached_dict)
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {e}")
        
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
        
        # Calculate file hash for incremental analysis
        file_hash = self._calculate_file_hash(file_path)
        
        # Check cache if not forcing re-analysis
        if not force and file_hash:
            cached = await self._get_cached_analysis(file_path, file_hash)
            if cached:
                cached.cache_hit = True
                return cached
        
        logger.info(f"Analyzing file: {file_path}")
        
        # Handle Jupyter notebooks
        is_notebook = file_path.endswith('.ipynb')
        if is_notebook:
            try:
                notebook_code = self.notebook_analyzer.extract_code(file_path)
                source_code = notebook_code.full_code.encode('utf-8')
                logger.debug(f"Extracted {notebook_code.total_cells} cells from notebook")
            except Exception as e:
                logger.error(f"Failed to extract notebook code: {e}")
                # Return error analysis
                return self._create_error_analysis(
                    file_path, 
                    "python",
                    f"Failed to extract notebook code: {e}",
                    start_time
                )
        else:
            try:
                with open(file_path, 'rb') as f:
                    source_code = f.read()
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                return self._create_error_analysis(
                    file_path,
                    "unknown",
                    f"Failed to read file: {e}",
                    start_time
                )
        
        # Parse file
        try:
            parse_result = self.parser.parse_file(file_path)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return self._create_error_analysis(
                file_path,
                "unknown",
                f"Parse error: {e}",
                start_time
            )
        
        # Extract symbols
        try:
            symbol_info_extractor = self.symbol_extractor.extract_symbols(parse_result)
        except Exception as e:
            logger.error(f"Failed to extract symbols from {file_path}: {e}")
            return self._create_error_analysis(
                file_path,
                parse_result.language,
                f"Symbol extraction error: {e}",
                start_time
            )
        
        # Detect patterns
        try:
            file_content = source_code.decode('utf-8', errors='ignore')
            patterns = self.pattern_detector.detect_patterns_in_file(
                symbol_info_extractor,
                file_content,
                file_path
            )
        except Exception as e:
            logger.warning(f"Pattern detection failed for {file_path}: {e}")
            patterns = []
        
        # Calculate complexity metrics
        try:
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
        except Exception as e:
            logger.warning(f"Complexity analysis failed for {file_path}: {e}")
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
            doc_coverage = self.doc_coverage_analyzer.calculate_coverage(
                symbol_info_extractor,
                file_content,
                parse_result.language
            )
        except Exception as e:
            logger.warning(f"Documentation coverage analysis failed for {file_path}: {e}")
            from .documentation_coverage import DocumentationCoverage
            doc_coverage = DocumentationCoverage()
        
        # Score teaching value
        try:
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
        except Exception as e:
            logger.warning(f"Teaching value scoring failed for {file_path}: {e}")
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
            linter_issues = await self.linter.run_linters(
                file_path,
                parse_result.language
            )
        except Exception as e:
            logger.warning(f"Linter execution failed for {file_path}: {e}")
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
        
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"Analysis complete for {file_path} in {elapsed_ms:.0f}ms")
        
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
        logger.info(f"Starting codebase analysis: {codebase_id} (incremental={incremental})")
        
        # Get scan results
        scan_result = await self.cache.get_analysis(f"scan:{codebase_id}")
        if not scan_result:
            raise ValueError(
                f"Codebase not scanned. Call scan_codebase first for codebase_id: {codebase_id}"
            )
        
        # Load previous analysis for incremental mode
        previous_analysis = None
        previous_hashes = {}
        if incremental and self.config.enable_incremental:
            previous_analysis = self.persistence.load_analysis(codebase_id)
            previous_hashes = self.persistence.get_file_hashes(codebase_id)
            if previous_analysis:
                logger.info(f"Loaded previous analysis with {len(previous_analysis.file_analyses)} files")
        
        # Determine which files to analyze
        files_to_analyze = []
        current_hashes = {}
        
        # Get file list from scan result
        file_list = []
        if hasattr(scan_result, 'files'):
            # If scan_result has files attribute (list of FileInfo objects)
            file_list = [f.path if hasattr(f, 'path') else str(f) for f in scan_result.files]
        elif isinstance(scan_result, dict) and 'files' in scan_result:
            # If scan_result is a dict
            file_list = scan_result['files']
        else:
            logger.error(f"Invalid scan result format for {codebase_id}")
            raise ValueError("Invalid scan result format")
        
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
        
        # Reuse previous analyses for unchanged files
        if previous_analysis and incremental and self.config.enable_incremental:
            for file_path, analysis in previous_analysis.file_analyses.items():
                if file_path not in files_to_analyze and file_path in current_hashes:
                    # File unchanged, reuse previous analysis
                    file_analyses[file_path] = analysis
                    logger.debug(f"Reusing previous analysis for {file_path}")
        
        # Analyze new/changed files in parallel
        if files_to_analyze:
            logger.info(f"Analyzing {len(files_to_analyze)} files in parallel...")
            
            # Create analysis tasks
            tasks = [self.analyze_file(fp) for fp in files_to_analyze]
            
            # Run in parallel with asyncio.gather
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for file_path, result in zip(files_to_analyze, results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to analyze {file_path}: {result}")
                    # Create error analysis
                    file_analyses[file_path] = self._create_error_analysis(
                        file_path,
                        "unknown",
                        str(result),
                        start_time
                    )
                else:
                    file_analyses[file_path] = result
        
        logger.info(f"File analysis complete: {len(file_analyses)} files analyzed")
        
        # Build dependency graph
        try:
            logger.info("Building dependency graph...")
            dependency_graph = self.dependency_analyzer.analyze_dependencies(
                codebase_id,
                file_analyses
            )
        except Exception as e:
            logger.error(f"Failed to build dependency graph: {e}")
            # Create empty dependency graph
            from .dependency_analyzer import DependencyGraph
            dependency_graph = DependencyGraph()
        
        # Detect global patterns
        try:
            logger.info("Detecting global patterns...")
            global_patterns = self.pattern_detector.detect_global_patterns(file_analyses)
        except Exception as e:
            logger.error(f"Failed to detect global patterns: {e}")
            global_patterns = []
        
        # Rank files by teaching value
        try:
            top_teaching_files = sorted(
                [(fp, fa.teaching_value.total_score) for fp, fa in file_analyses.items()],
                key=lambda x: x[1],
                reverse=True
            )[:20]  # Top 20 files
        except Exception as e:
            logger.error(f"Failed to rank teaching files: {e}")
            top_teaching_files = []
        
        # Calculate codebase metrics
        try:
            metrics = self._calculate_codebase_metrics(file_analyses, start_time)
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
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
            logger.info("Persisting analysis to disk...")
            self.persistence.save_analysis(codebase_id, analysis)
            self.persistence.save_file_hashes(codebase_id, current_hashes)
        except Exception as e:
            logger.error(f"Failed to persist analysis: {e}")
        
        # Cache in memory
        try:
            await self.cache.set_analysis(
                f"codebase:{codebase_id}",
                analysis.to_dict(),
                ttl=self.config.cache_ttl_seconds
            )
        except Exception as e:
            logger.error(f"Failed to cache analysis: {e}")
        
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
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
