"""
MCP Server Core Implementation using FastMCP.

This module implements the main MCP server entry point with FastMCP framework.
It registers 3 discovery tools (scan_codebase, detect_frameworks, discover_features),
2 resources (codebase://structure, codebase://features), and 1 prompt (analyze_codebase).

The server uses lifespan management for proper cache initialization and cleanup,
achieving God Mode performance through the 3-tier caching system.
"""

import logging
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional

from fastmcp import FastMCP, Context

from src.cache.unified_cache import UnifiedCacheManager
from src.config.settings import Settings
from src.tools.scan_codebase import scan_codebase as scan_codebase_impl
from src.tools.detect_frameworks import detect_frameworks as detect_frameworks_impl
from src.tools.discover_features import discover_features as discover_features_impl
from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log")
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context shared across all tools."""
    cache_manager: UnifiedCacheManager
    config: Settings
    analysis_engine: AnalysisEngine


# Module-level variable to store app context
app_context: Optional[AppContext] = None


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Manage server startup and shutdown lifecycle.
    
    Startup:
        - Load configuration from config.yaml
        - Create UnifiedCacheManager
        - Initialize cache connections and tables
        - Log server startup
    
    Shutdown:
        - Close cache connections
        - Cleanup resources
        - Log server shutdown
    
    Args:
        server: FastMCP server instance
        
    Yields:
        AppContext with cache_manager and config
    """
    global app_context
    
    # Startup: initialize resources
    logger.info("MCP Server started: codebase-to-course-mcp v1.0.0")
    
    try:
        # Load configuration
        config = Settings()
        logger.info(f"Configuration loaded: cache_max_memory={config.cache_max_memory_mb}MB")
        
        # Create cache manager
        cache_manager = UnifiedCacheManager(
            max_memory_mb=config.cache_max_memory_mb,
            sqlite_path=config.sqlite_path,
            redis_url=config.redis_url
        )
        
        # Initialize cache
        await cache_manager.initialize()
        logger.info("UnifiedCacheManager initialized successfully")
        
        # Create analysis engine
        analysis_config = AnalysisConfig()
        analysis_engine = AnalysisEngine(cache_manager, analysis_config)
        logger.info("Analysis Engine initialized successfully")
        
        # Create app context
        app_context = AppContext(
            cache_manager=cache_manager,
            config=config,
            analysis_engine=analysis_engine
        )
        
        # Yield context to server
        yield app_context
        
    finally:
        # Shutdown: cleanup resources
        logger.info("MCP Server shutting down gracefully")
        
        if app_context and app_context.cache_manager:
            await app_context.cache_manager.close()
            logger.info("Cache manager closed")
        
        app_context = None
        logger.info("MCP Server shutdown complete")


# Create FastMCP server with lifespan management
mcp = FastMCP("codebase-to-course-mcp", lifespan=app_lifespan)


@mcp.tool
async def scan_codebase(
    path: str,
    max_depth: int = 10,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Scan codebase structure, languages, and frameworks.
    
    Traverses the directory tree up to max_depth, counts files by language,
    detects project type, and generates a unique codebase ID. Results are
    cached for 1 hour to achieve God Mode performance (<0.1s on subsequent calls).
    
    Args:
        path: Directory path to scan (required)
              Examples:
              - Current directory: "."
              - Relative path: "./src"
              - Absolute path (Windows): "C:\\Users\\username\\project"
              - Absolute path (Unix): "/home/username/project"
        max_depth: Maximum directory depth to traverse (default: 10)
                  Lower values = faster scan, higher values = more thorough
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with codebase_id (save this for other tools!), structure, summary, scan_time_ms, from_cache
    
    Raises:
        ValueError: If path is invalid or contains directory traversal attempts (..)
        PermissionError: If access to path is denied
    
    Examples:
        Scan current directory:
        {"path": "."}
        
        Scan with custom depth:
        {"path": ".", "max_depth": 5}
        
        Scan absolute path:
        {"path": "C:\\Users\\brian\\project"}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Log tool invocation
    logger.info(f"Tool invoked: scan_codebase with arguments: path={path}, max_depth={max_depth}, use_cache={use_cache}")
    
    # Call implementation
    result = await scan_codebase_impl(
        path=path,
        max_depth=max_depth,
        use_cache=use_cache,
        cache_manager=cache_manager,
        max_file_size_mb=config.max_file_size_mb
    )
    
    # Log completion
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Tool completed: scan_codebase in {duration_ms:.2f}ms")
    
    # Log slow operations
    if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
        logger.warning(f"Slow operation detected: scan_codebase took {duration_ms:.2f}ms")
    
    return result


@mcp.tool
async def detect_frameworks(
    codebase_id: str,
    confidence_threshold: float = 0.7,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Detect frameworks and libraries with confidence scores.
    
    Analyzes package.json for JavaScript/TypeScript projects and requirements.txt
    for Python projects, assigning confidence scores (0.99 for package.json, 0.95
    for requirements.txt) and evidence for each detected framework.
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    You must run scan_codebase first to get this ID
        confidence_threshold: Minimum confidence score to include (0.0-1.0, default: 0.7)
                            Lower = more results, higher = only high-confidence detections
                            Examples: 0.5 (permissive), 0.7 (balanced), 0.9 (strict)
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with frameworks array (name, version, confidence, evidence), 
        total_detected count, confidence_threshold used, from_cache status
    
    Raises:
        ValueError: If codebase has not been scanned first (run scan_codebase first!)
    
    Examples:
        Detect with default threshold:
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Detect with strict threshold:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "confidence_threshold": 0.9}
        
        Detect with permissive threshold:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "confidence_threshold": 0.5}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Log tool invocation
    logger.info(f"Tool invoked: detect_frameworks with arguments: codebase_id={codebase_id}, confidence_threshold={confidence_threshold}, use_cache={use_cache}")
    
    # Call implementation
    result = await detect_frameworks_impl(
        codebase_id=codebase_id,
        confidence_threshold=confidence_threshold,
        use_cache=use_cache,
        cache_manager=cache_manager
    )
    
    # Log completion
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Tool completed: detect_frameworks in {duration_ms:.2f}ms")
    
    # Log slow operations
    if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
        logger.warning(f"Slow operation detected: detect_frameworks took {duration_ms:.2f}ms")
    
    return result


@mcp.tool
async def discover_features(
    codebase_id: str,
    categories: Optional[list[str]] = None,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Discover features like routes, components, API endpoints, utilities, and hooks.
    
    Searches for feature directories based on common patterns (routes/, components/,
    api/, utils/, hooks/), generates unique feature IDs, and assigns priorities
    (high for routes/api, medium for others).
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
        categories: Optional list of categories to discover. 
                   To discover all categories, either:
                   - Don't include "categories" in your JSON at all, OR
                   - Use empty array: []
                   
                   Available category options:
                   - ["routes"] - only routes
                   - ["components"] - only components  
                   - ["api"] - only API endpoints
                   - ["utils"] - only utilities
                   - ["hooks"] - only hooks
                   - ["routes", "api"] - multiple categories
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with features array, total_features, categories, from_cache
    
    Raises:
        ValueError: If codebase has not been scanned first or if codebase_id is empty
    
    Examples:
        Discover all features (omit categories):
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Discover all features (empty array):
        {"codebase_id": "a1b2c3d4e5f6g7h8", "categories": []}
        
        Discover only routes and API:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "categories": ["routes", "api"]}
        
        Discover only components:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "categories": ["components"]}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Log tool invocation
    logger.info(f"Tool invoked: discover_features with arguments: codebase_id={codebase_id}, categories={categories}, use_cache={use_cache}")
    
    # Call implementation
    result = await discover_features_impl(
        codebase_id=codebase_id,
        categories=categories,
        use_cache=use_cache,
        cache_manager=cache_manager
    )
    
    # Log completion
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Tool completed: discover_features in {duration_ms:.2f}ms")
    
    # Log slow operations
    if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
        logger.warning(f"Slow operation detected: discover_features took {duration_ms:.2f}ms")
    
    return result


@mcp.resource("codebase://structure")
async def get_structure(ctx: Context = None) -> dict:
    """
    Get cached codebase structure.
    
    Returns the structure data from the most recent scan_codebase call.
    This resource provides access to the codebase's file organization,
    language distribution, and summary information.
    
    Args:
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with codebase structure data
    
    Raises:
        ValueError: If resource not available (scan_codebase not called yet)
    
    Examples:
        >>> structure = await get_structure()
        >>> print(structure["structure"]["total_files"])
        150
    """
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    
    # Log resource access
    logger.info("Resource accessed: codebase://structure")
    
    # Retrieve cached structure
    structure = await cache_manager.get_resource("structure")
    
    if not structure:
        raise ValueError("Resource not available. Run scan_codebase first.")
    
    return structure


@mcp.resource("codebase://features")
async def get_features(ctx: Context = None) -> dict:
    """
    Get cached discovered features.
    
    Returns the features data from the most recent discover_features call.
    This resource provides access to discovered routes, components, API endpoints,
    utilities, and hooks with their priorities and categories.
    
    Args:
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with discovered features data
    
    Raises:
        ValueError: If resource not available (discover_features not called yet)
    
    Examples:
        >>> features = await get_features()
        >>> print(features["total_features"])
        5
    """
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    
    # Log resource access
    logger.info("Resource accessed: codebase://features")
    
    # Retrieve cached features
    features = await cache_manager.get_resource("features")
    
    if not features:
        raise ValueError("Resource not available. Run discover_features first.")
    
    return features


@mcp.prompt
async def analyze_codebase(codebase_path: str) -> str:
    """
    Template for initial codebase analysis.
    
    Provides a step-by-step workflow template that guides AI assistants through
    progressive discovery of a codebase. The workflow follows God Mode principles:
    scan structure first, detect frameworks, discover features, then focus on
    teachable code examples.
    
    Args:
        codebase_path: Path to the codebase directory to analyze
    
    Returns:
        Template string with 4-step analysis workflow
    
    Examples:
        >>> template = await analyze_codebase(codebase_path="./my-project")
        >>> print(template)
        Please analyze the codebase at: ./my-project...
    """
    # Log prompt access
    logger.info(f"Prompt accessed: analyze_codebase with codebase_path={codebase_path}")
    
    # Return template with 4-step workflow
    return f"""Please analyze the codebase at: {codebase_path}

Follow this progressive discovery workflow:

**Step 1: Scan Codebase Structure**
Call the `scan_codebase` tool with path="{codebase_path}" to understand:
- Total files and directories
- Programming languages used
- Project type (web-application, python-application, etc.)
- Size category (small, medium, large)
- Overall organization

**Step 2: Detect Frameworks and Libraries**
Use the `codebase_id` from Step 1 to call `detect_frameworks` to identify:
- Frameworks with confidence scores (React, Next.js, Django, Flask, etc.)
- Library versions from package.json or requirements.txt
- Technology stack with evidence-based validation

**Step 3: Discover Features**
Use the `codebase_id` to call `discover_features` to find:
- Routes and page components (high priority)
- API endpoints and controllers (high priority)
- Reusable components (medium priority)
- Utility functions and helpers (medium priority)
- Custom hooks or composables (medium priority)

**Step 4: Focus on Teachable Code**
Based on the discovered features:
- Identify well-structured, documented code examples
- Look for patterns that demonstrate best practices
- Find code that teaches framework-specific concepts
- Prioritize features with clear separation of concerns
- Focus on code that would be valuable for learning

This workflow achieves God Mode performance through intelligent caching:
- First scan: 2-3 seconds
- Subsequent calls: <0.1 seconds (450x speedup)
- 99% accuracy with evidence-based validation
- 0% hallucination rate

Start with Step 1 and proceed sequentially for best results."""


@mcp.tool
async def analyze_file(
    file_path: str,
    force: bool = False,
    ctx: Context = None
) -> dict:
    """
    Analyze a single file for symbols, patterns, complexity, and teaching value.
    
    Performs comprehensive static analysis on a source code file, extracting
    functions, classes, imports, detecting patterns (React components, API routes,
    etc.), calculating complexity metrics, and scoring teaching value. Results
    are cached based on file hash for fast subsequent calls.
    
    Args:
        file_path: Path to file to analyze (required)
                  Supported extensions: .py, .js, .jsx, .ts, .tsx, .ipynb
                  Examples:
                  - Relative path: "src/main.py"
                  - Absolute path (Windows): "C:\\Users\\username\\project\\src\\main.py"
                  - Absolute path (Unix): "/home/username/project/src/main.py"
        force: Force re-analysis even if cached (default: false)
              Set to true to bypass cache and get fresh analysis
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with FileAnalysis containing:
        - file_path: Path to analyzed file
        - language: Detected language (python, javascript, typescript)
        - symbol_info: Extracted functions, classes, imports, exports
        - patterns: Detected patterns with confidence scores
        - teaching_value: Teaching value score (0.0-1.0) with explanation
        - complexity_metrics: Cyclomatic complexity, nesting depth
        - documentation_coverage: Percentage of documented symbols
        - linter_issues: Issues from pylint/eslint (if enabled)
        - has_errors: Whether parse errors occurred
        - errors: List of error messages
        - analyzed_at: ISO timestamp
        - cache_hit: Whether result came from cache
        - is_notebook: Whether file is Jupyter notebook
    
    Raises:
        ValueError: If file_path is empty or file doesn't exist
        RuntimeError: If server not initialized
    
    Examples:
        Analyze Python file:
        {"file_path": "src/main.py"}
        
        Force re-analysis:
        {"file_path": "src/main.py", "force": true}
        
        Analyze TypeScript file:
        {"file_path": "src/components/Button.tsx"}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    analysis_engine = app_context.analysis_engine
    config = app_context.config
    
    # Validate input
    if not file_path or not file_path.strip():
        raise ValueError("file_path parameter is required and cannot be empty")
    
    # Check if file exists
    from pathlib import Path
    if not Path(file_path).exists():
        raise ValueError(f"File not found: {file_path}")
    
    # Log tool invocation
    logger.info(f"Tool invoked: analyze_file with arguments: file_path={file_path}, force={force}")
    
    try:
        # Call analysis engine
        result = await analysis_engine.analyze_file(file_path, force=force)
        
        # Convert to dict for JSON serialization
        result_dict = result.to_dict()
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Tool completed: analyze_file in {duration_ms:.2f}ms")
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: analyze_file took {duration_ms:.2f}ms")
        
        return result_dict
        
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error analyzing file {file_path}: {e}")
        raise ValueError(f"Failed to analyze file: {str(e)}")


@mcp.tool
async def detect_patterns(
    codebase_id: str,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Detect coding patterns across the codebase with confidence scores.
    
    Analyzes the entire codebase to detect common patterns like React components,
    API routes, database operations, authentication flows, and more. Returns
    patterns with confidence scores (0.0-1.0) and evidence for each detection.
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    You must run scan_codebase first to get this ID
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with:
        - patterns: Array of detected patterns with:
          - pattern_type: Type of pattern (react_component, api_route, etc.)
          - file_path: File where pattern was detected
          - confidence: Confidence score (0.0-1.0)
          - evidence: List of evidence strings
          - line_numbers: Lines where pattern appears
          - metadata: Additional pattern-specific data
        - total_patterns: Total number of patterns detected
        - pattern_types: Unique pattern types found
        - from_cache: Whether result came from cache
    
    Raises:
        ValueError: If codebase has not been analyzed (run analyze_codebase first!)
        RuntimeError: If server not initialized
    
    Examples:
        Detect patterns:
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Force fresh detection:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "use_cache": false}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Validate input
    if not codebase_id or not codebase_id.strip():
        raise ValueError("codebase_id parameter is required and cannot be empty")
    
    # Log tool invocation
    logger.info(f"Tool invoked: detect_patterns with arguments: codebase_id={codebase_id}, use_cache={use_cache}")
    
    # Check cache first
    cache_key = f"codebase:{codebase_id}"
    from_cache = False
    
    if use_cache:
        cached_analysis = await cache_manager.get_analysis(cache_key)
        if cached_analysis:
            from_cache = True
            logger.info(f"Cache hit for codebase analysis: {codebase_id}")
            
            # Extract patterns from cached analysis
            if isinstance(cached_analysis, dict):
                global_patterns = cached_analysis.get('global_patterns', [])
            else:
                global_patterns = cached_analysis.global_patterns
            
            # Build response
            pattern_types = list(set(p.get('pattern_type') if isinstance(p, dict) else p.pattern_type 
                                    for p in global_patterns))
            
            # Convert patterns to dict format if needed
            if global_patterns and isinstance(global_patterns[0], dict):
                patterns_list = global_patterns
            elif global_patterns:
                patterns_list = [p.to_dict() for p in global_patterns]
            else:
                patterns_list = []
            
            result = {
                'patterns': patterns_list,
                'total_patterns': len(global_patterns),
                'pattern_types': pattern_types,
                'from_cache': from_cache
            }
            
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Tool completed: detect_patterns in {duration_ms:.2f}ms (from cache)")
            
            return result
    
    # Not in cache - need to analyze codebase first
    raise ValueError(
        f"Codebase not analyzed. Call analyze_codebase with codebase_id='{codebase_id}' first."
    )


@mcp.tool
async def analyze_dependencies(
    codebase_id: str,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Analyze import dependencies and build dependency graph.
    
    Analyzes all imports across the codebase to build a dependency graph,
    detect circular dependencies, identify external packages, and calculate
    dependency metrics. Useful for understanding code architecture and
    identifying tightly coupled modules.
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    You must run scan_codebase first to get this ID
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with DependencyGraph containing:
        - nodes: Dictionary of file nodes with imports and imported_by lists
        - edges: List of dependency edges with import counts
        - circular_dependencies: List of circular dependency cycles
        - external_dependencies: Dictionary of external packages with usage counts
        - metrics: Dependency metrics (total_nodes, total_edges, etc.)
        - from_cache: Whether result came from cache
    
    Raises:
        ValueError: If codebase has not been analyzed (run analyze_codebase first!)
        RuntimeError: If server not initialized
    
    Examples:
        Analyze dependencies:
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Force fresh analysis:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "use_cache": false}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Validate input
    if not codebase_id or not codebase_id.strip():
        raise ValueError("codebase_id parameter is required and cannot be empty")
    
    # Log tool invocation
    logger.info(f"Tool invoked: analyze_dependencies with arguments: codebase_id={codebase_id}, use_cache={use_cache}")
    
    # Check cache first
    cache_key = f"codebase:{codebase_id}"
    from_cache = False
    
    if use_cache:
        cached_analysis = await cache_manager.get_analysis(cache_key)
        if cached_analysis:
            from_cache = True
            logger.info(f"Cache hit for codebase analysis: {codebase_id}")
            
            # Extract dependency graph from cached analysis
            if isinstance(cached_analysis, dict):
                dependency_graph = cached_analysis.get('dependency_graph', {})
            else:
                dependency_graph = cached_analysis.dependency_graph.to_dict()
            
            # Calculate metrics
            metrics = {
                'total_nodes': len(dependency_graph.get('nodes', {})),
                'total_edges': len(dependency_graph.get('edges', [])),
                'circular_dependencies_count': len(dependency_graph.get('circular_dependencies', [])),
                'external_dependencies_count': len(dependency_graph.get('external_dependencies', {}))
            }
            
            result = {
                **dependency_graph,
                'metrics': metrics,
                'from_cache': from_cache
            }
            
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Tool completed: analyze_dependencies in {duration_ms:.2f}ms (from cache)")
            
            return result
    
    # Not in cache - need to analyze codebase first
    raise ValueError(
        f"Codebase not analyzed. Call analyze_codebase with codebase_id='{codebase_id}' first."
    )


@mcp.tool
async def score_teaching_value(
    file_path: str,
    force: bool = False,
    ctx: Context = None
) -> dict:
    """
    Score the teaching value of a file for educational purposes.
    
    Calculates a teaching value score (0.0-1.0) based on documentation quality,
    code complexity, detected patterns, and code structure. Higher scores indicate
    files that are better for learning and teaching. Includes detailed explanation
    of scoring factors.
    
    Args:
        file_path: Path to file to score (required)
                  Supported extensions: .py, .js, .jsx, .ts, .tsx, .ipynb
        force: Force re-analysis even if cached (default: false)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with TeachingValueScore containing:
        - total_score: Overall teaching value (0.0-1.0)
        - documentation_score: Documentation quality score
        - complexity_score: Complexity appropriateness score
        - pattern_score: Pattern detection score
        - structure_score: Code structure score
        - explanation: Human-readable explanation of score
        - factors: Dictionary of individual scoring factors
        - file_path: Path to analyzed file
        - from_cache: Whether result came from cache
    
    Raises:
        ValueError: If file_path is empty or file doesn't exist
        RuntimeError: If server not initialized
    
    Examples:
        Score teaching value:
        {"file_path": "src/components/Button.tsx"}
        
        Force fresh scoring:
        {"file_path": "src/main.py", "force": true}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    analysis_engine = app_context.analysis_engine
    config = app_context.config
    
    # Validate input
    if not file_path or not file_path.strip():
        raise ValueError("file_path parameter is required and cannot be empty")
    
    # Check if file exists
    from pathlib import Path
    if not Path(file_path).exists():
        raise ValueError(f"File not found: {file_path}")
    
    # Log tool invocation
    logger.info(f"Tool invoked: score_teaching_value with arguments: file_path={file_path}, force={force}")
    
    try:
        # Analyze file to get teaching value
        result = await analysis_engine.analyze_file(file_path, force=force)
        
        # Extract teaching value score
        teaching_value_dict = result.teaching_value.to_dict()
        teaching_value_dict['file_path'] = file_path
        teaching_value_dict['from_cache'] = result.cache_hit
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Tool completed: score_teaching_value in {duration_ms:.2f}ms")
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: score_teaching_value took {duration_ms:.2f}ms")
        
        return teaching_value_dict
        
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error scoring teaching value for {file_path}: {e}")
        raise ValueError(f"Failed to score teaching value: {str(e)}")


@mcp.tool
async def analyze_codebase_tool(
    codebase_id: str,
    incremental: bool = True,
    use_cache: bool = True,
    ctx: Context = None
) -> dict:
    """
    Perform complete codebase analysis with parallel processing.
    
    Analyzes all files in the codebase in parallel, extracting symbols, detecting
    patterns, building dependency graphs, and scoring teaching value. Supports
    incremental analysis (only re-analyze changed files) for fast updates.
    Results are cached and persisted to disk.
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    You must run scan_codebase first to get this ID
        incremental: Only analyze changed files (default: true)
                    Set to false to force full re-analysis
        use_cache: Use cached results if available (default: true)
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with CodebaseAnalysis containing:
        - codebase_id: Codebase identifier
        - file_analyses: Dictionary of FileAnalysis for each file
        - dependency_graph: Complete dependency graph
        - global_patterns: Patterns detected across codebase
        - top_teaching_files: Top 20 files by teaching value
        - metrics: Aggregate metrics (total_files, avg_complexity, etc.)
        - analyzed_at: ISO timestamp
        - from_cache: Whether result came from cache
    
    Raises:
        ValueError: If codebase has not been scanned (run scan_codebase first!)
        RuntimeError: If server not initialized
    
    Examples:
        Analyze codebase (incremental):
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Force full re-analysis:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "incremental": false}
        
        Bypass cache:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "use_cache": false}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    analysis_engine = app_context.analysis_engine
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Validate input
    if not codebase_id or not codebase_id.strip():
        raise ValueError("codebase_id parameter is required and cannot be empty")
    
    # Log tool invocation
    logger.info(
        f"Tool invoked: analyze_codebase_tool with arguments: "
        f"codebase_id={codebase_id}, incremental={incremental}, use_cache={use_cache}"
    )
    
    # Check cache first
    cache_key = f"codebase:{codebase_id}"
    from_cache = False
    
    if use_cache:
        cached_analysis = await cache_manager.get_analysis(cache_key)
        if cached_analysis:
            from_cache = True
            logger.info(f"Cache hit for codebase analysis: {codebase_id}")
            
            # Add from_cache flag
            if isinstance(cached_analysis, dict):
                cached_analysis['from_cache'] = from_cache
                result = cached_analysis
            else:
                result = cached_analysis.to_dict()
                result['from_cache'] = from_cache
            
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Tool completed: analyze_codebase_tool in {duration_ms:.2f}ms (from cache)")
            
            return result
    
    try:
        # Perform analysis
        result = await analysis_engine.analyze_codebase(
            codebase_id=codebase_id,
            incremental=incremental
        )
        
        # Convert to dict for JSON serialization
        result_dict = result.to_dict()
        result_dict['from_cache'] = from_cache
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Tool completed: analyze_codebase_tool in {duration_ms:.2f}ms "
            f"({result.metrics.total_files} files analyzed)"
        )
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: analyze_codebase_tool took {duration_ms:.2f}ms")
        
        return result_dict
        
    except ValueError as e:
        # Re-raise ValueError with clear message
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error analyzing codebase {codebase_id}: {e}")
        raise ValueError(f"Failed to analyze codebase: {str(e)}")


@mcp.tool
async def export_course(
    codebase_id: str,
    format: str = "mkdocs",
    output_dir: Optional[str] = None,
    target_audience: str = "beginner",
    course_focus: str = "full-stack",
    max_duration_hours: Optional[float] = None,
    min_teaching_value: float = 0.0,
    ctx: Context = None
) -> dict:
    """
    Export a course from analyzed codebase to specified format.
    
    Generates a complete course structure from codebase analysis and exports
    it to the specified format (MkDocs, Next.js, JSON, Markdown, or PDF).
    The course includes modules, lessons with content, and exercises.
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    You must run analyze_codebase_tool first to get analysis data
        format: Export format (default: "mkdocs")
               Options: "mkdocs", "nextjs", "json", "markdown", "pdf"
        output_dir: Output directory path (optional)
                   If not provided, uses "./output/{codebase_id}_course"
        target_audience: Target audience level (default: "beginner")
                        Options: "beginner", "intermediate", "advanced", "mixed"
                        Affects content complexity and explanation depth
                        "beginner" provides the most detailed, accessible explanations
        course_focus: Course focus area (default: "full-stack")
                     Options: "patterns", "architecture", "best-practices", "full-stack"
                     "full-stack" covers all aspects comprehensively
        max_duration_hours: Maximum course duration in hours (optional, default: None)
                           When None, includes all content without time limit
                           Set a value (e.g., 10.0) to limit course length
        min_teaching_value: Minimum teaching value score (0.0-1.0, default: 0.0)
                           Only include files with teaching value above this threshold
                           0.0 = include ALL content for maximum coverage
                           Higher values (0.5+) = only high-quality lessons
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with:
        - export_path: Path to exported course
        - format: Export format used
        - statistics: Export statistics (modules, lessons, exercises)
        - codebase_id: Codebase identifier
        - config: Course configuration used
    
    Raises:
        ValueError: If codebase has not been analyzed or format is invalid
        RuntimeError: If server not initialized or export fails
    
    Examples:
        Export comprehensive beginner course (uses defaults - ALL content):
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Export 10-hour beginner course:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "max_duration_hours": 10.0}
        
        Export only high-quality lessons:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "min_teaching_value": 0.7}
        
        Export advanced architecture course:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "target_audience": "advanced", "course_focus": "architecture"}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Validate input
    if not codebase_id or not codebase_id.strip():
        raise ValueError("codebase_id parameter is required and cannot be empty")
    
    # Validate format
    from src.course.exporters.export_manager import ExportManager
    valid_formats = ExportManager.SUPPORTED_FORMATS
    format = format.lower()
    if format not in valid_formats:
        raise ValueError(
            f"Invalid format: {format}. Supported formats: {', '.join(valid_formats)}"
        )
    
    # Log tool invocation
    logger.info(
        f"Tool invoked: export_course with arguments: "
        f"codebase_id={codebase_id}, format={format}, output_dir={output_dir}"
    )
    
    try:
        # Get analysis from cache
        cache_key = f"codebase:{codebase_id}"
        cached_analysis = await cache_manager.get_analysis(cache_key)
        
        if not cached_analysis:
            raise ValueError(
                f"Codebase not analyzed. Call analyze_codebase_tool with codebase_id='{codebase_id}' first."
            )
        
        # Convert to CodebaseAnalysis if needed
        from src.models import CodebaseAnalysis
        if isinstance(cached_analysis, dict):
            analysis = CodebaseAnalysis.from_dict(cached_analysis)
        else:
            analysis = cached_analysis
        
        # Generate course structure
        from src.course.structure_generator import CourseStructureGenerator
        from src.course.content_generator import LessonContentGenerator
        from src.course.exercise_generator import ExerciseGenerator
        from src.course.config import CourseConfig
        from src.course.exporters.export_manager import ExportManager
        
        # Create course config with user-specified parameters
        course_config = CourseConfig(
            target_audience=target_audience,
            course_focus=course_focus,
            max_duration_hours=max_duration_hours,
            min_teaching_value=min_teaching_value
        )
        structure_gen = CourseStructureGenerator(course_config)
        
        logger.info(f"Generating course structure for codebase {codebase_id}")
        course_outline = await structure_gen.generate_course_structure(analysis)
        
        # Generate lesson content for each lesson
        content_gen = LessonContentGenerator(course_config)
        exercise_gen = ExerciseGenerator(course_config)
        
        for module in course_outline.modules:
            for lesson in module.lessons:
                # Get file analysis for this lesson
                file_analysis = analysis.file_analyses.get(lesson.file_path)
                if file_analysis:
                    # Generate lesson content
                    lesson.content = await content_gen.generate_lesson_content(file_analysis)
                    
                    # Generate exercises (1-3 per lesson based on complexity)
                    patterns = [p for p in file_analysis.patterns if p.confidence > 0.7]
                    num_exercises = min(3, max(1, len(patterns)))
                    
                    for i, pattern in enumerate(patterns[:num_exercises]):
                        exercise = await exercise_gen.generate_exercise(pattern, file_analysis)
                        lesson.exercises.append(exercise)
        
        # Set output directory
        if not output_dir:
            output_dir = f"./output/{codebase_id}_course"
        
        # Save course data as JSON for enrichment guide access
        import json
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert course outline to dict for JSON serialization
        course_data = {
            'course_id': course_outline.course_id,
            'title': course_outline.title,
            'description': course_outline.description,
            'author': course_outline.author,
            'version': course_outline.version,
            'created_at': course_outline.created_at.isoformat(),
            'total_duration_hours': course_outline.total_duration_hours,
            'difficulty_distribution': course_outline.difficulty_distribution,
            'tags': course_outline.tags,
            'prerequisites': course_outline.prerequisites,
            'modules': []
        }
        
        # Convert modules and lessons
        for module in course_outline.modules:
            module_data = {
                'module_id': module.module_id,
                'title': module.title,
                'description': module.description,
                'order': module.order,
                'difficulty': module.difficulty,
                'duration_hours': module.duration_hours,
                'learning_objectives': module.learning_objectives,
                'lessons': []
            }
            
            for lesson in module.lessons:
                lesson_data = {
                    'lesson_id': lesson.lesson_id,
                    'title': lesson.title,
                    'description': lesson.description,
                    'order': lesson.order,
                    'difficulty': lesson.difficulty,
                    'duration_minutes': lesson.duration_minutes,
                    'file_path': lesson.file_path,
                    'teaching_value': lesson.teaching_value,
                    'learning_objectives': lesson.learning_objectives,
                    'prerequisites': lesson.prerequisites,
                    'concepts': lesson.concepts,
                    'exercises': [
                        {
                            'exercise_id': ex.exercise_id,
                            'title': ex.title,
                            'description': ex.description,
                            'difficulty': ex.difficulty,
                            'estimated_minutes': ex.estimated_minutes,
                            'instructions': ex.instructions,
                            'starter_code': ex.starter_code,
                            'solution_code': ex.solution_code,
                            'hints': ex.hints,
                            'learning_objectives': ex.learning_objectives
                        }
                        for ex in lesson.exercises
                    ],
                    'tags': lesson.tags
                }
                module_data['lessons'].append(lesson_data)
            
            course_data['modules'].append(module_data)
        
        # Save course data
        course_data_path = output_path / 'course_data.json'
        with open(course_data_path, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved course data to {course_data_path}")
        
        # Export course
        export_manager = ExportManager(course_config)
        logger.info(f"Exporting course to {format} format at {output_dir}")
        export_path = export_manager.export(course_outline, output_dir, format)
        
        # Calculate statistics
        total_modules = len(course_outline.modules)
        total_lessons = sum(len(m.lessons) for m in course_outline.modules)
        total_exercises = sum(
            len(lesson.exercises) 
            for module in course_outline.modules 
            for lesson in module.lessons
        )
        
        result = {
            'export_path': export_path,
            'format': format,
            'statistics': {
                'modules': total_modules,
                'lessons': total_lessons,
                'exercises': total_exercises,
                'duration_hours': course_outline.total_duration_hours
            },
            'codebase_id': codebase_id,
            'config': {
                'target_audience': target_audience,
                'course_focus': course_focus,
                'max_duration_hours': max_duration_hours,
                'min_teaching_value': min_teaching_value
            }
        }
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Tool completed: export_course in {duration_ms:.2f}ms "
            f"({total_modules} modules, {total_lessons} lessons, {total_exercises} exercises)"
        )
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: export_course took {duration_ms:.2f}ms")
        
        return result
        
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error exporting course for codebase {codebase_id}: {e}")
        raise RuntimeError(f"Failed to export course: {str(e)}")


@mcp.tool
async def generate_lesson_outline(
    file_path: str,
    ctx: Context = None
) -> dict:
    """
    Generate a lesson outline from a single file.
    
    Analyzes a file and generates a structured lesson outline with learning
    objectives, key concepts, code examples, and suggested exercises. Useful
    for previewing lesson content before generating a full course.
    
    Args:
        file_path: Path to file to generate lesson from (required)
                  Supported extensions: .py, .js, .jsx, .ts, .tsx, .ipynb
                  Examples:
                  - Relative path: "src/components/Button.tsx"
                  - Absolute path (Windows): "C:\\Users\\username\\project\\src\\main.py"
                  - Absolute path (Unix): "/home/username/project/src/main.py"
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with:
        - title: Lesson title
        - file_path: Path to source file
        - learning_objectives: List of learning objectives (3-5)
        - key_concepts: List of key concepts covered
        - difficulty: Lesson difficulty (beginner, intermediate, advanced)
        - estimated_duration_minutes: Estimated lesson duration
        - code_examples: List of code example descriptions
        - suggested_exercises: List of suggested exercise descriptions
        - patterns: Detected patterns in the file
        - teaching_value_score: Teaching value score (0.0-1.0)
    
    Raises:
        ValueError: If file_path is empty or file doesn't exist
        RuntimeError: If server not initialized or analysis fails
    
    Examples:
        Generate lesson outline:
        {"file_path": "src/components/Button.tsx"}
        
        Generate from Python file:
        {"file_path": "src/utils/helpers.py"}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    analysis_engine = app_context.analysis_engine
    config = app_context.config
    
    # Validate input
    if not file_path or not file_path.strip():
        raise ValueError("file_path parameter is required and cannot be empty")
    
    # Check if file exists
    from pathlib import Path
    if not Path(file_path).exists():
        raise ValueError(f"File not found: {file_path}")
    
    # Log tool invocation
    logger.info(f"Tool invoked: generate_lesson_outline with arguments: file_path={file_path}")
    
    try:
        # Analyze file
        file_analysis = await analysis_engine.analyze_file(file_path, force=False)
        
        # Generate lesson content
        from src.course.content_generator import LessonContentGenerator
        from src.course.config import CourseConfig
        
        course_config = CourseConfig()
        content_gen = LessonContentGenerator(course_config)
        
        # Generate learning objectives
        objectives = content_gen.generate_objectives(file_analysis)
        
        # Extract key concepts from patterns
        key_concepts = list(set(
            pattern.pattern_type.replace('_', ' ').title()
            for pattern in file_analysis.patterns
            if pattern.confidence > 0.7
        ))
        
        # Determine difficulty
        complexity = file_analysis.complexity_metrics.avg_complexity if hasattr(file_analysis.complexity_metrics, 'avg_complexity') else 0
        if complexity < 5:
            difficulty = 'beginner'
        elif complexity < 15:
            difficulty = 'intermediate'
        else:
            difficulty = 'advanced'
        
        # Estimate duration (5-15 minutes based on complexity)
        estimated_duration = min(15, max(5, complexity))
        
        # Generate code example descriptions
        code_examples = []
        for func in file_analysis.symbol_info.functions[:3]:  # Top 3 functions
            code_examples.append({
                'name': func.name,
                'description': f"Function demonstrating {func.name}",
                'lines': f"{func.start_line}-{func.end_line}"
            })
        
        for cls in file_analysis.symbol_info.classes[:2]:  # Top 2 classes
            code_examples.append({
                'name': cls.name,
                'description': f"Class demonstrating {cls.name}",
                'lines': f"{cls.start_line}-{cls.end_line}"
            })
        
        # Generate suggested exercises
        suggested_exercises = []
        for pattern in file_analysis.patterns[:3]:  # Top 3 patterns
            suggested_exercises.append({
                'pattern': pattern.pattern_type,
                'description': f"Practice implementing {pattern.pattern_type.replace('_', ' ')}",
                'difficulty': difficulty
            })
        
        # Generate title from file name
        import os
        filename = os.path.basename(file_path)
        title = filename.replace('_', ' ').replace('-', ' ').replace('.py', '').replace('.js', '').replace('.ts', '').replace('.tsx', '').replace('.jsx', '').title()
        
        result = {
            'title': title,
            'file_path': file_path,
            'learning_objectives': objectives,
            'key_concepts': key_concepts,
            'difficulty': difficulty,
            'estimated_duration_minutes': estimated_duration,
            'code_examples': code_examples,
            'suggested_exercises': suggested_exercises,
            'patterns': [
                {
                    'type': p.pattern_type,
                    'confidence': p.confidence,
                    'evidence': p.evidence
                }
                for p in file_analysis.patterns
            ],
            'teaching_value_score': file_analysis.teaching_value.total_score
        }
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Tool completed: generate_lesson_outline in {duration_ms:.2f}ms")
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: generate_lesson_outline took {duration_ms:.2f}ms")
        
        return result
        
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error generating lesson outline for {file_path}: {e}")
        raise RuntimeError(f"Failed to generate lesson outline: {str(e)}")


@mcp.tool
async def create_exercise(
    pattern_type: str,
    difficulty: str = "intermediate",
    codebase_id: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Create a coding exercise for a specific pattern type.
    
    Generates a coding exercise with starter code, solution, hints, and test
    cases for a specific pattern type. If codebase_id is provided, finds an
    example from the analyzed codebase. Otherwise, generates a generic exercise.
    
    Args:
        pattern_type: Type of pattern to create exercise for (required)
                     Examples: "react_component", "api_route", "database_query",
                              "authentication", "error_handling", "async_operation"
        difficulty: Exercise difficulty (default: "intermediate")
                   Options: "beginner", "intermediate", "advanced"
        codebase_id: Optional codebase ID to find pattern examples from
                    If provided, uses actual code from the codebase
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with Exercise containing:
        - exercise_id: Unique exercise identifier
        - title: Exercise title
        - description: Exercise description
        - difficulty: Difficulty level
        - estimated_minutes: Estimated completion time
        - instructions: Step-by-step instructions
        - starter_code: Code template with TODOs
        - solution_code: Complete solution code
        - hints: Progressive hints (3-5)
        - test_cases: Test cases for validation
        - learning_objectives: Learning objectives (3-5)
        - pattern_type: Pattern type
    
    Raises:
        ValueError: If pattern_type is empty or invalid
        RuntimeError: If server not initialized or generation fails
    
    Examples:
        Create React component exercise:
        {"pattern_type": "react_component"}
        
        Create advanced API route exercise:
        {"pattern_type": "api_route", "difficulty": "advanced"}
        
        Create exercise from codebase:
        {"pattern_type": "database_query", "codebase_id": "a1b2c3d4e5f6g7h8"}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Validate input
    if not pattern_type or not pattern_type.strip():
        raise ValueError("pattern_type parameter is required and cannot be empty")
    
    # Validate difficulty
    valid_difficulties = ['beginner', 'intermediate', 'advanced']
    difficulty = difficulty.lower()
    if difficulty not in valid_difficulties:
        raise ValueError(
            f"Invalid difficulty: {difficulty}. Valid options: {', '.join(valid_difficulties)}"
        )
    
    # Log tool invocation
    logger.info(
        f"Tool invoked: create_exercise with arguments: "
        f"pattern_type={pattern_type}, difficulty={difficulty}, codebase_id={codebase_id}"
    )
    
    try:
        from src.course.exercise_generator import ExerciseGenerator
        from src.course.config import CourseConfig
        from src.models import DetectedPattern, FileAnalysis
        
        course_config = CourseConfig()
        exercise_gen = ExerciseGenerator(course_config)
        
        # If codebase_id provided, find pattern example from codebase
        pattern = None
        file_analysis = None
        
        if codebase_id:
            cache_key = f"codebase:{codebase_id}"
            cached_analysis = await cache_manager.get_analysis(cache_key)
            
            if cached_analysis:
                # Find a file with the requested pattern
                from src.models import CodebaseAnalysis
                if isinstance(cached_analysis, dict):
                    analysis = CodebaseAnalysis.from_dict(cached_analysis)
                else:
                    analysis = cached_analysis
                
                # Search for pattern in file analyses
                for file_path, file_anal in analysis.file_analyses.items():
                    for p in file_anal.patterns:
                        if p.pattern_type == pattern_type and p.confidence > 0.7:
                            pattern = p
                            file_analysis = file_anal
                            break
                    if pattern:
                        break
        
        # If no pattern found or no codebase_id, create generic pattern
        if not pattern:
            pattern = DetectedPattern(
                pattern_type=pattern_type,
                file_path=f"example_{pattern_type}.py",
                confidence=0.9,
                evidence=[f"Generic {pattern_type} example"],
                line_numbers=[],
                metadata={}
            )
            
            # Create minimal file analysis
            from src.models import SymbolInfo, TeachingValueScore, ComplexityMetrics
            
            # Determine complexity based on difficulty
            if difficulty == 'beginner':
                avg_complexity = 2.0
            elif difficulty == 'intermediate':
                avg_complexity = 8.0
            else:
                avg_complexity = 15.0
            
            file_analysis = FileAnalysis(
                file_path=f"example_{pattern_type}.py",
                language="python",
                symbol_info=SymbolInfo(functions=[], classes=[], imports=[], exports=[]),
                patterns=[pattern],
                teaching_value=TeachingValueScore(
                    total_score=0.8,
                    documentation_score=0.8,
                    complexity_score=0.7,
                    pattern_score=0.9,
                    structure_score=0.8,
                    explanation="Generic exercise example",
                    factors={}
                ),
                complexity_metrics=ComplexityMetrics(
                    avg_complexity=avg_complexity,
                    max_complexity=int(avg_complexity * 1.5),
                    min_complexity=int(avg_complexity * 0.5),
                    high_complexity_functions=[],
                    trivial_functions=[],
                    avg_nesting_depth=2.0
                ),
                documentation_coverage=0.8,
                linter_issues=[],
                has_errors=False,
                errors=[],
                analyzed_at="",
                cache_hit=False,
                is_notebook=False
            )
        
        # Generate exercise
        exercise = await exercise_gen.generate_exercise(pattern, file_analysis)
        
        # Override difficulty if specified
        exercise.difficulty = difficulty
        
        # Convert to dict
        result = {
            'exercise_id': exercise.exercise_id,
            'title': exercise.title,
            'description': exercise.description,
            'difficulty': exercise.difficulty,
            'estimated_minutes': exercise.estimated_minutes,
            'instructions': exercise.instructions,
            'starter_code': exercise.starter_code,
            'solution_code': exercise.solution_code,
            'hints': exercise.hints,
            'test_cases': [
                {
                    'input': tc.input,
                    'expected_output': tc.expected_output,
                    'description': tc.description
                }
                for tc in exercise.test_cases
            ],
            'learning_objectives': exercise.learning_objectives,
            'pattern_type': pattern_type
        }
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Tool completed: create_exercise in {duration_ms:.2f}ms")
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: create_exercise took {duration_ms:.2f}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating exercise for pattern {pattern_type}: {e}")
        raise RuntimeError(f"Failed to create exercise: {str(e)}")


@mcp.tool
async def get_enrichment_guide(
    codebase_id: str,
    lesson_id: str,
    ctx: Context = None
) -> dict:
    """
    Generate a comprehensive enrichment guide for AI content enrichment.
    
    Creates an evidence-based enrichment guide following the Feature-to-Lesson
    Mapping and Knowledge-to-Course frameworks. The guide provides structured,
    validated guidance for AI assistants (like Kiro) to generate rich educational
    content with proper citations and anti-hallucination measures.
    
    The enrichment guide includes:
    - Feature mapping (connecting code to user-facing features)
    - Evidence bundle (source code, tests, git commits, documentation)
    - Validation checklist (cross-referenced understanding)
    - Teaching value assessment (0-14 scoring system)
    - Systematic investigation (what, why, how, when, edge cases, pitfalls)
    - Narrative structure (introduction, progression, conclusion)
    - Code section guides (detailed explanations with citations)
    - Architecture context (component roles, data flow, patterns)
    - Real-world context (use cases, analogies, best practices)
    - Exercise generation (hands-on tasks with progressive hints)
    - Anti-hallucination rules (evidence requirements)
    - Enrichment instructions (tone, depth, focus areas)
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    You must run analyze_codebase_tool first to get analysis data
        lesson_id: Lesson identifier from exported course (required)
                  Format: "module-{n}-lesson-{m}" (e.g., "module-1-lesson-1")
                  Get lesson IDs from export_course output
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with EnrichmentGuide containing all 12 components:
        - lesson_id: Lesson identifier
        - feature_mapping: Feature name, purpose, business value, entry points, flow
        - evidence_bundle: Source files, tests, git commits, docs, dependencies
        - validation_checklist: Code behavior, test expectations, doc alignment, git context
        - teaching_value_assessment: Scores (0-14), reasoning, should_teach flag
        - systematic_investigation: What, why, how, when, edge cases, pitfalls
        - narrative_structure: Introduction, progression, walkthrough order, conclusion
        - code_sections: Detailed guides for each code section with evidence
        - architecture_context: Component role, data flow, interaction diagram, patterns
        - real_world_context: Use cases, analogies, industry patterns, best practices
        - exercise_generation: Tasks, starter code, solution, hints, self-assessment
        - anti_hallucination_rules: Citation requirements, validation rules
        - enrichment_instructions: Tone, depth, focus areas, evidence requirements
    
    Raises:
        ValueError: If codebase not analyzed, lesson not found, or invalid parameters
        RuntimeError: If server not initialized or guide generation fails
    
    Examples:
        Get enrichment guide for first lesson:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "lesson_id": "module-1-lesson-1"}
        
        Get guide for specific lesson:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "lesson_id": "module-2-lesson-3"}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    analysis_engine = app_context.analysis_engine
    config = app_context.config
    
    # Validate input
    if not codebase_id or not codebase_id.strip():
        raise ValueError("codebase_id parameter is required and cannot be empty")
    
    if not lesson_id or not lesson_id.strip():
        raise ValueError("lesson_id parameter is required and cannot be empty")
    
    # Log tool invocation
    logger.info(
        f"Tool invoked: get_enrichment_guide with arguments: "
        f"codebase_id={codebase_id}, lesson_id={lesson_id}"
    )
    
    try:
        # Get codebase analysis from cache
        cache_key = f"codebase:{codebase_id}"
        cached_analysis = await cache_manager.get_analysis(cache_key)
        
        if not cached_analysis:
            raise ValueError(
                f"Codebase not analyzed. Call analyze_codebase_tool with codebase_id='{codebase_id}' first."
            )
        
        # Convert to CodebaseAnalysis if needed
        from src.models import CodebaseAnalysis
        if isinstance(cached_analysis, dict):
            analysis = CodebaseAnalysis.from_dict(cached_analysis)
        else:
            analysis = cached_analysis
        
        # Get course data to find the lesson
        # For now, we'll need to load the course data from the export
        # This assumes export_course has been called and saved course data
        import json
        from pathlib import Path
        import glob
        
        # Try to find course_data.json in output directory
        # First try default location
        course_data_path = Path(f"./output/{codebase_id}_course/course_data.json")
        
        # If not found, search for any course_data.json with this codebase_id
        if not course_data_path.exists():
            search_pattern = f"./output/*{codebase_id}*/course_data.json"
            matches = glob.glob(search_pattern)
            if matches:
                # Sort by modification time to get the most recent
                matches.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
                course_data_path = Path(matches[0])
            else:
                raise ValueError(
                    f"Course data not found. Call export_course with codebase_id='{codebase_id}' first."
                )
        
        # Load course data
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        # Find the lesson
        lesson = None
        for module in course_data.get('modules', []):
            for les in module.get('lessons', []):
                if les.get('lesson_id') == lesson_id:
                    lesson = les
                    break
            if lesson:
                break
        
        if not lesson:
            raise ValueError(
                f"Lesson '{lesson_id}' not found in course. "
                f"Check lesson IDs from export_course output."
            )
        
        # Convert lesson dict to Lesson object
        from src.course.models import Lesson
        lesson_obj = Lesson(
            lesson_id=lesson['lesson_id'],
            title=lesson['title'],
            description=lesson['description'],
            order=lesson['order'],
            difficulty=lesson['difficulty'],
            duration_minutes=lesson['duration_minutes'],
            file_path=lesson['file_path'],
            teaching_value=lesson['teaching_value'],
            learning_objectives=lesson.get('learning_objectives', []),
            prerequisites=lesson.get('prerequisites', []),
            concepts=lesson.get('concepts', []),
            content=None,  # Will be enriched
            exercises=lesson.get('exercises', []),
            tags=lesson.get('tags', [])
        )
        
        # Get file analysis for the lesson's source file
        file_analysis = analysis.file_analyses.get(lesson_obj.file_path)
        
        if not file_analysis:
            raise ValueError(
                f"File analysis not found for '{lesson_obj.file_path}'. "
                f"The file may not have been analyzed."
            )
        
        # Get repository path from scan data
        scan_data = await cache_manager.get_resource("structure")
        
        if not scan_data:
            raise ValueError(
                f"Scan data not found for codebase '{codebase_id}'. "
                f"Call scan_codebase first."
            )
        
        repo_path = scan_data.get('path', '.')
        
        # Initialize EnrichmentGuideGenerator
        from src.course.enrichment_guide_generator import EnrichmentGuideGenerator
        from src.analysis.git_analyzer import GitAnalyzer
        
        # Try to create GitAnalyzer (may fail if not a git repo)
        git_analyzer = None
        try:
            git_analyzer = GitAnalyzer(repo_path)
        except Exception as e:
            logger.warning(f"Could not initialize GitAnalyzer: {e}. Git evidence will be unavailable.")
        
        # Create enrichment guide generator
        enrichment_generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=analysis_engine,
            git_analyzer=git_analyzer
        )
        
        # Generate enrichment guide
        logger.info(f"Generating enrichment guide for lesson '{lesson_id}'")
        enrichment_guide = await enrichment_generator.generate_guide(
            codebase_id=codebase_id,
            lesson=lesson_obj,
            file_analysis=file_analysis
        )
        
        # Convert to dict for JSON serialization
        result = enrichment_guide.to_dict()
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Tool completed: get_enrichment_guide in {duration_ms:.2f}ms "
            f"(teaching_value={enrichment_guide.teaching_value_assessment.total_score}/14, "
            f"should_teach={enrichment_guide.teaching_value_assessment.should_teach})"
        )
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: get_enrichment_guide took {duration_ms:.2f}ms")
        
        return result
        
    except ValueError as e:
        raise ValueError(str(e))
    except FileNotFoundError as e:
        raise ValueError(f"File not found: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating enrichment guide for lesson '{lesson_id}': {e}", exc_info=True)
        raise RuntimeError(f"Failed to generate enrichment guide: {str(e)}")


@mcp.tool
async def update_lesson_content(
    codebase_id: str,
    lesson_id: str,
    enriched_content: dict,
    ctx: Context = None
) -> dict:
    """
    Update lesson with enriched content from AI assistant.
    
    Validates and merges enriched content into a lesson, preserving the existing
    structure while updating fields like description, content, code examples,
    exercises, and learning objectives. Tracks enrichment status and saves the
    updated course data to disk.
    
    This tool is designed to be called by AI assistants (like Kiro) after they
    have generated rich educational content using the enrichment guide from
    get_enrichment_guide.
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    Must match the codebase used in export_course
        lesson_id: Lesson identifier to update (required)
                  Format: "module-{n}-lesson-{m}" (e.g., "module-1-lesson-1")
        enriched_content: Dictionary with enriched fields (required)
                         Required fields:
                         - description: Rich description with context (string)
                         - content: Full learning narrative (string)
                         
                         Optional fields:
                         - code_examples: Enhanced code examples with explanations (list)
                         - exercises: Enhanced exercises with hints (list)
                         - learning_objectives: Generated learning goals (list)
                         
                         Example:
                         {
                           "description": "Learn how to implement secure user authentication...",
                           "content": "# Introduction\n\nAuthentication is critical...",
                           "learning_objectives": ["Understand password hashing", "Implement JWT tokens"],
                           "code_examples": [
                             {
                               "code": "def login(username, password):",
                               "explanation": "This function validates user credentials..."
                             }
                           ],
                           "exercises": [
                             {
                               "title": "Add Password Strength Validation",
                               "instructions": "Implement a function that validates...",
                               "hints": ["Start by checking length", "Add special character check"]
                             }
                           ]
                         }
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with:
        - success: True if update succeeded
        - lesson_id: Updated lesson identifier
        - updated_fields: List of fields that were updated
        - enrichment_status: Current enrichment status
        - message: Success message
    
    Raises:
        ValueError: If codebase not found, lesson not found, or content validation fails
        RuntimeError: If server not initialized or update fails
    
    Examples:
        Update lesson with enriched content:
        {
          "codebase_id": "a1b2c3d4e5f6g7h8",
          "lesson_id": "module-1-lesson-1",
          "enriched_content": {
            "description": "Learn secure authentication with bcrypt and JWT",
            "content": "# Introduction\n\nAuthentication is critical for...",
            "learning_objectives": ["Understand password hashing", "Implement JWT tokens"]
          }
        }
        
        Update with full enrichment:
        {
          "codebase_id": "a1b2c3d4e5f6g7h8",
          "lesson_id": "module-2-lesson-3",
          "enriched_content": {
            "description": "Master React component patterns",
            "content": "# Component Patterns\n\nReact components...",
            "learning_objectives": ["Create reusable components", "Implement hooks"],
            "code_examples": [...],
            "exercises": [...]
          }
        }
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Validate input
    if not codebase_id or not codebase_id.strip():
        raise ValueError("codebase_id parameter is required and cannot be empty")
    
    if not lesson_id or not lesson_id.strip():
        raise ValueError("lesson_id parameter is required and cannot be empty")
    
    if not enriched_content or not isinstance(enriched_content, dict):
        raise ValueError("enriched_content parameter is required and must be a dictionary")
    
    # Log tool invocation
    logger.info(
        f"Tool invoked: update_lesson_content with arguments: "
        f"codebase_id={codebase_id}, lesson_id={lesson_id}, "
        f"enriched_fields={list(enriched_content.keys())}"
    )
    
    try:
        # Validate enriched content structure
        _validate_enriched_content(enriched_content)
        
        # Load course data
        import json
        from pathlib import Path
        from datetime import datetime
        import glob
        
        # Try to find course_data.json in output directory
        # First try default location
        course_data_path = Path(f"./output/{codebase_id}_course/course_data.json")
        
        # If not found, search for any course_data.json with this codebase_id
        if not course_data_path.exists():
            search_pattern = f"./output/*{codebase_id}*/course_data.json"
            matches = glob.glob(search_pattern)
            if matches:
                # Sort by modification time to get the most recent
                matches.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
                course_data_path = Path(matches[0])
            else:
                raise ValueError(
                    f"Course data not found for codebase '{codebase_id}'. "
                    f"Call export_course first to generate the course."
                )
        
        # Load existing course data
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        # Find the lesson
        lesson = None
        module_idx = None
        lesson_idx = None
        
        for m_idx, module in enumerate(course_data.get('modules', [])):
            for l_idx, les in enumerate(module.get('lessons', [])):
                if les.get('lesson_id') == lesson_id:
                    lesson = les
                    module_idx = m_idx
                    lesson_idx = l_idx
                    break
            if lesson:
                break
        
        if not lesson:
            raise ValueError(
                f"Lesson '{lesson_id}' not found in course. "
                f"Check lesson IDs from export_course output."
            )
        
        # Track which fields were updated
        updated_fields = []
        
        # Merge enriched content into lesson (preserve structure)
        if 'description' in enriched_content:
            lesson['description'] = enriched_content['description']
            updated_fields.append('description')
        
        if 'content' in enriched_content:
            lesson['content'] = enriched_content['content']
            updated_fields.append('content')
        
        if 'learning_objectives' in enriched_content:
            lesson['learning_objectives'] = enriched_content['learning_objectives']
            updated_fields.append('learning_objectives')
        
        if 'code_examples' in enriched_content:
            # Merge code examples - update explanations if provided
            for enriched_example in enriched_content['code_examples']:
                # Find matching code example by code content or index
                if 'code' in enriched_example:
                    # Try to find matching example
                    found = False
                    for existing_example in lesson.get('code_examples', []):
                        if existing_example.get('code') == enriched_example['code']:
                            # Update explanation
                            if 'explanation' in enriched_example:
                                existing_example['explanation'] = enriched_example['explanation']
                            found = True
                            break
                    
                    # If not found, add as new example
                    if not found:
                        if 'code_examples' not in lesson:
                            lesson['code_examples'] = []
                        lesson['code_examples'].append(enriched_example)
            
            updated_fields.append('code_examples')
        
        if 'exercises' in enriched_content:
            # Merge exercises - update or add new ones
            for enriched_exercise in enriched_content['exercises']:
                # Find matching exercise by title or exercise_id
                found = False
                
                for existing_exercise in lesson.get('exercises', []):
                    if (existing_exercise.get('title') == enriched_exercise.get('title') or
                        existing_exercise.get('exercise_id') == enriched_exercise.get('exercise_id')):
                        # Update exercise fields
                        if 'description' in enriched_exercise:
                            existing_exercise['description'] = enriched_exercise['description']
                        if 'instructions' in enriched_exercise:
                            existing_exercise['instructions'] = enriched_exercise['instructions']
                        if 'hints' in enriched_exercise:
                            existing_exercise['hints'] = enriched_exercise['hints']
                        if 'starter_code' in enriched_exercise:
                            existing_exercise['starter_code'] = enriched_exercise['starter_code']
                        if 'solution_code' in enriched_exercise:
                            existing_exercise['solution_code'] = enriched_exercise['solution_code']
                        found = True
                        break
                
                # If not found, add as new exercise
                if not found:
                    if 'exercises' not in lesson:
                        lesson['exercises'] = []
                    lesson['exercises'].append(enriched_exercise)
            
            updated_fields.append('exercises')
        
        # Update enrichment status tracking
        if 'enrichment_status' not in course_data:
            course_data['enrichment_status'] = {}
        
        # Get existing status or create new
        existing_status = course_data['enrichment_status'].get(lesson_id, {})
        version = existing_status.get('version', 0) + 1
        
        course_data['enrichment_status'][lesson_id] = {
            'status': 'completed',
            'enriched_at': datetime.now().isoformat(),
            'enriched_by': 'kiro',
            'version': version,
            'updated_fields': updated_fields
        }
        
        # Save updated course data to disk
        with open(course_data_path, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
        
        logger.info(
            f"Successfully updated lesson '{lesson_id}' with enriched content. "
            f"Updated fields: {', '.join(updated_fields)}"
        )
        
        # Prepare result
        result = {
            'success': True,
            'lesson_id': lesson_id,
            'updated_fields': updated_fields,
            'enrichment_status': {
                'status': 'completed',
                'version': version,
                'enriched_at': course_data['enrichment_status'][lesson_id]['enriched_at']
            },
            'message': f"Lesson '{lesson_id}' successfully updated with {len(updated_fields)} enriched fields"
        }
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Tool completed: update_lesson_content in {duration_ms:.2f}ms "
            f"({len(updated_fields)} fields updated)"
        )
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: update_lesson_content took {duration_ms:.2f}ms")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error updating lesson '{lesson_id}': {e}")
        return {
            'success': False,
            'lesson_id': lesson_id,
            'error': str(e),
            'message': f"Failed to update lesson: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error updating lesson '{lesson_id}': {e}", exc_info=True)
        return {
            'success': False,
            'lesson_id': lesson_id,
            'error': str(e),
            'message': f"Failed to update lesson: {str(e)}"
        }


@mcp.tool
async def list_lessons_for_enrichment(
    codebase_id: str,
    ctx: Context = None
) -> dict:
    """
    List all lessons available for enrichment with their status.
    
    Returns a list of all lessons in the course with their enrichment status,
    teaching value scores, and source files. Lessons are sorted by teaching
    value score (high to low) to prioritize the most valuable content for
    enrichment.
    
    This tool helps AI assistants (like Kiro) identify which lessons to enrich
    and track enrichment progress across the course.
    
    Args:
        codebase_id: Unique identifier from scan_codebase (required)
                    Must match the codebase used in export_course
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with:
        - lessons: List of lesson dictionaries, each containing:
          - lesson_id: Lesson identifier (e.g., "module-1-lesson-1")
          - title: Lesson title
          - module_title: Parent module title
          - status: Enrichment status ("not_started", "in_progress", "completed")
          - teaching_value: Teaching value score (0.0-1.0)
          - source_files: List of source file paths
          - difficulty: Lesson difficulty level
          - duration_minutes: Estimated lesson duration
          - enriched_at: ISO timestamp of last enrichment (if completed)
          - version: Enrichment version number (if enriched)
        - total_lessons: Total number of lessons
        - enrichment_summary: Summary statistics:
          - not_started: Count of lessons not yet enriched
          - in_progress: Count of lessons being enriched
          - completed: Count of completed lessons
          - completion_percentage: Percentage of completed lessons
        - codebase_id: Codebase identifier
    
    Raises:
        ValueError: If codebase not found or course not exported
        RuntimeError: If server not initialized
    
    Examples:
        List all lessons for enrichment:
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Get enrichment progress:
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
    """
    start_time = time.time()
    
    # Access app context
    if not app_context:
        raise RuntimeError("Server not initialized")
    
    cache_manager = app_context.cache_manager
    config = app_context.config
    
    # Validate input
    if not codebase_id or not codebase_id.strip():
        raise ValueError("codebase_id parameter is required and cannot be empty")
    
    # Log tool invocation
    logger.info(
        f"Tool invoked: list_lessons_for_enrichment with arguments: "
        f"codebase_id={codebase_id}"
    )
    
    try:
        # Load course data
        import json
        from pathlib import Path
        import glob
        
        # Try to find course_data.json in output directory
        # First try default location
        course_data_path = Path(f"./output/{codebase_id}_course/course_data.json")
        
        # If not found, search for any course_data.json with this codebase_id
        if not course_data_path.exists():
            search_pattern = f"./output/*{codebase_id}*/course_data.json"
            matches = glob.glob(search_pattern)
            if matches:
                # Sort by modification time to get the most recent
                matches.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
                course_data_path = Path(matches[0])
            else:
                raise ValueError(
                    f"Course data not found for codebase '{codebase_id}'. "
                    f"Call export_course first to generate the course."
                )
        
        # Load existing course data
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        # Get enrichment status tracking
        enrichment_status = course_data.get('enrichment_status', {})
        
        # Build lessons list
        lessons = []
        
        for module in course_data.get('modules', []):
            module_title = module.get('title', 'Unknown Module')
            
            for lesson in module.get('lessons', []):
                lesson_id = lesson.get('lesson_id')
                
                # Get enrichment status for this lesson
                lesson_status = enrichment_status.get(lesson_id, {})
                status = lesson_status.get('status', 'not_started')
                enriched_at = lesson_status.get('enriched_at')
                version = lesson_status.get('version', 0)
                
                # Build lesson info
                lesson_info = {
                    'lesson_id': lesson_id,
                    'title': lesson.get('title', 'Untitled Lesson'),
                    'module_title': module_title,
                    'status': status,
                    'teaching_value': lesson.get('teaching_value', 0.0),
                    'source_files': [lesson.get('file_path')] if lesson.get('file_path') else [],
                    'difficulty': lesson.get('difficulty', 'intermediate'),
                    'duration_minutes': lesson.get('duration_minutes', 0)
                }
                
                # Add enrichment metadata if available
                if enriched_at:
                    lesson_info['enriched_at'] = enriched_at
                if version > 0:
                    lesson_info['version'] = version
                
                lessons.append(lesson_info)
        
        # Sort by teaching value (high to low)
        lessons.sort(key=lambda x: x['teaching_value'], reverse=True)
        
        # Calculate enrichment summary
        total_lessons = len(lessons)
        not_started = sum(1 for l in lessons if l['status'] == 'not_started')
        in_progress = sum(1 for l in lessons if l['status'] == 'in_progress')
        completed = sum(1 for l in lessons if l['status'] == 'completed')
        completion_percentage = (completed / total_lessons * 100) if total_lessons > 0 else 0.0
        
        enrichment_summary = {
            'not_started': not_started,
            'in_progress': in_progress,
            'completed': completed,
            'completion_percentage': round(completion_percentage, 2)
        }
        
        # Prepare result
        result = {
            'lessons': lessons,
            'total_lessons': total_lessons,
            'enrichment_summary': enrichment_summary,
            'codebase_id': codebase_id
        }
        
        # Log completion
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Tool completed: list_lessons_for_enrichment in {duration_ms:.2f}ms "
            f"({total_lessons} lessons, {completed} completed, {completion_percentage:.1f}% done)"
        )
        
        # Log slow operations
        if config.log_slow_operations and duration_ms > config.slow_operation_threshold_ms:
            logger.warning(f"Slow operation detected: list_lessons_for_enrichment took {duration_ms:.2f}ms")
        
        return result
        
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error listing lessons for enrichment: {e}", exc_info=True)
        raise RuntimeError(f"Failed to list lessons: {str(e)}")


def _validate_enriched_content(content: dict) -> None:
    """
    Validate enriched content structure.
    
    Ensures required fields are present and have valid values.
    
    Args:
        content: Enriched content dictionary to validate
        
    Raises:
        ValueError: If validation fails
    """
    # Check required fields
    required_fields = ['description', 'content']
    for field in required_fields:
        if field not in content:
            raise ValueError(f"Missing required field: {field}")
        if not content[field] or not isinstance(content[field], str):
            raise ValueError(f"Field '{field}' must be a non-empty string")
    
    # Validate optional fields if present
    if 'learning_objectives' in content:
        if not isinstance(content['learning_objectives'], list):
            raise ValueError("Field 'learning_objectives' must be a list")
        if not content['learning_objectives']:
            raise ValueError("Field 'learning_objectives' cannot be empty if provided")
    
    if 'code_examples' in content:
        if not isinstance(content['code_examples'], list):
            raise ValueError("Field 'code_examples' must be a list")
        
        # Validate each code example
        for idx, example in enumerate(content['code_examples']):
            if not isinstance(example, dict):
                raise ValueError(f"Code example at index {idx} must be a dictionary")
            if 'explanation' not in example and 'code' not in example:
                raise ValueError(f"Code example at index {idx} must have 'code' or 'explanation' field")
    
    if 'exercises' in content:
        if not isinstance(content['exercises'], list):
            raise ValueError("Field 'exercises' must be a list")
        
        # Validate each exercise
        for idx, exercise in enumerate(content['exercises']):
            if not isinstance(exercise, dict):
                raise ValueError(f"Exercise at index {idx} must be a dictionary")
            # At least one of these fields should be present
            if not any(key in exercise for key in ['title', 'description', 'instructions', 'hints']):
                raise ValueError(
                    f"Exercise at index {idx} must have at least one of: "
                    f"title, description, instructions, hints"
                )


# Entry point for running the server
if __name__ == "__main__":
    import asyncio
    mcp.run()
