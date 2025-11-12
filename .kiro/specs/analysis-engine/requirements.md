# Requirements Document - Analysis Engine

## Introduction

The Analysis Engine is the intelligence layer of the Documee MCP Server that transforms basic codebase scanning into deep, meaningful analysis. While Spec 1 provided basic file counting and framework detection, Spec 3 adds sophisticated code understanding through AST parsing, pattern detection, dependency analysis, and teaching value scoring. This enables the system to identify not just what code exists, but which code is most valuable for teaching and learning.

## Glossary

- **AST (Abstract Syntax Tree)**: A tree representation of source code structure that enables programmatic code analysis
- **Analysis Engine**: The intelligent layer that performs deep code analysis beyond basic file scanning
- **Teaching Value Score**: A numeric score (0.0-1.0) indicating how valuable a code file is for educational purposes
- **Pattern Detector**: Component that identifies common coding patterns and architectural decisions
- **Dependency Analyzer**: Component that maps relationships between code files and external packages
- **Code Complexity**: Measure of code difficulty based on cyclomatic complexity, nesting depth, and other metrics
- **tree-sitter**: Fast, incremental parsing library that generates ASTs for multiple languages
- **Import Graph**: Visual representation of how files import and depend on each other

## Requirements

### Requirement 1: AST Parser for Multi-Language Support

**User Story:** As a developer, I want the system to parse code files into ASTs, so that I can analyze code structure programmatically across multiple languages.

#### Acceptance Criteria

1. WHEN THE System receives a file path with .py extension, THE Analysis Engine SHALL parse the file using tree-sitter Python grammar and return an AST
2. WHEN THE System receives a file path with .js or .jsx extension, THE Analysis Engine SHALL parse the file using tree-sitter JavaScript grammar and return an AST
3. WHEN THE System receives a file path with .ts or .tsx extension, THE Analysis Engine SHALL parse the file using tree-sitter TypeScript grammar and return an AST
4. WHEN THE System encounters a syntax error during parsing, THE Analysis Engine SHALL log the error and return a partial AST with error nodes
5. WHEN THE System parses a file larger than max_file_size_mb, THE Analysis Engine SHALL raise a ValueError with message "File too large for parsing"

### Requirement 2: Function and Class Extraction

**User Story:** As a developer, I want to extract all functions and classes from code files, so that I can understand the code's structure and identify teachable components.

#### Acceptance Criteria

1. WHEN THE System parses a Python file, THE Analysis Engine SHALL extract all function definitions with name, parameters, return type, docstring, line numbers, and complexity score
2. WHEN THE System parses a Python file, THE Analysis Engine SHALL extract all class definitions with name, methods, base classes, docstring, and line numbers
3. WHEN THE System parses a JavaScript/TypeScript file, THE Analysis Engine SHALL extract all function declarations and arrow functions with name, parameters, and line numbers
4. WHEN THE System parses a JavaScript/TypeScript file, THE Analysis Engine SHALL extract all class declarations with name, methods, and extends clause
5. WHEN THE System extracts a function, THE Analysis Engine SHALL calculate cyclomatic complexity based on control flow statements (if, for, while, case)

### Requirement 3: Pattern Detection

**User Story:** As a developer, I want to detect common coding patterns in the codebase, so that I can identify architectural decisions and best practices worth teaching.

#### Acceptance Criteria

1. WHEN THE System analyzes a codebase, THE Pattern Detector SHALL identify React component patterns (functional components, hooks usage, props destructuring)
2. WHEN THE System analyzes a codebase, THE Pattern Detector SHALL identify API route patterns (Express routes, FastAPI endpoints, Next.js API routes)
3. WHEN THE System analyzes a codebase, THE Pattern Detector SHALL identify database patterns (ORM models, query builders, migrations)
4. WHEN THE System analyzes a codebase, THE Pattern Detector SHALL identify authentication patterns (JWT, OAuth, session-based)
5. WHEN THE System detects a pattern, THE Pattern Detector SHALL assign a confidence score (0.0-1.0) based on evidence strength

### Requirement 4: Dependency Analysis

**User Story:** As a developer, I want to analyze dependencies between files and packages, so that I can understand code relationships and identify tightly coupled components.

#### Acceptance Criteria

1. WHEN THE System analyzes a Python file, THE Dependency Analyzer SHALL extract all import statements (import, from...import) with module names and imported symbols
2. WHEN THE System analyzes a JavaScript/TypeScript file, THE Dependency Analyzer SHALL extract all import statements (import, require) with module names and imported symbols
3. WHEN THE System analyzes a codebase, THE Dependency Analyzer SHALL build an import graph showing which files import which other files
4. WHEN THE System analyzes a codebase, THE Dependency Analyzer SHALL identify circular dependencies and log warnings
5. WHEN THE System analyzes a codebase, THE Dependency Analyzer SHALL categorize dependencies as internal (project files) or external (npm/pip packages)

### Requirement 5: Teaching Value Scoring

**User Story:** As a developer, I want to score code files by their teaching value, so that I can prioritize which code to include in educational content.

#### Acceptance Criteria

1. WHEN THE System scores a code file, THE Teaching Value Scorer SHALL assign higher scores (0.7-1.0) to files with clear structure, good documentation, and moderate complexity
2. WHEN THE System scores a code file, THE Teaching Value Scorer SHALL assign medium scores (0.4-0.7) to files with some documentation and reasonable complexity
3. WHEN THE System scores a code file, THE Teaching Value Scorer SHALL assign lower scores (0.0-0.4) to files with poor documentation, extreme complexity, or generated code
4. WHEN THE System calculates teaching value, THE Teaching Value Scorer SHALL consider factors: documentation coverage, code complexity, pattern usage, and file size
5. WHEN THE System scores a file with docstrings covering >70% of functions, THE Teaching Value Scorer SHALL increase the score by 0.2

### Requirement 6: Code Complexity Metrics

**User Story:** As a developer, I want to measure code complexity, so that I can identify code that is too simple (trivial) or too complex (overwhelming) for teaching.

#### Acceptance Criteria

1. WHEN THE System analyzes a function, THE Analysis Engine SHALL calculate cyclomatic complexity by counting decision points (if, for, while, case, and, or)
2. WHEN THE System analyzes a function, THE Analysis Engine SHALL calculate nesting depth by measuring maximum indentation levels
3. WHEN THE System analyzes a file, THE Analysis Engine SHALL calculate average complexity across all functions
4. WHEN THE System encounters a function with complexity >10, THE Analysis Engine SHALL flag it as "high complexity"
5. WHEN THE System encounters a function with complexity <2, THE Analysis Engine SHALL flag it as "trivial"

### Requirement 7: Documentation Coverage Analysis

**User Story:** As a developer, I want to measure documentation coverage, so that I can identify well-documented code suitable for teaching.

#### Acceptance Criteria

1. WHEN THE System analyzes a Python file, THE Analysis Engine SHALL count functions with docstrings and calculate documentation coverage percentage
2. WHEN THE System analyzes a JavaScript/TypeScript file, THE Analysis Engine SHALL count functions with JSDoc comments and calculate documentation coverage percentage
3. WHEN THE System analyzes a class, THE Analysis Engine SHALL check for class-level documentation and method-level documentation separately
4. WHEN THE System calculates documentation coverage, THE Analysis Engine SHALL return a score from 0.0 (no docs) to 1.0 (all documented)
5. WHEN THE System finds inline comments explaining complex logic, THE Analysis Engine SHALL increase the documentation score by 0.1

### Requirement 8: Caching for Analysis Results

**User Story:** As a developer, I want analysis results to be cached, so that repeated analysis of the same files is fast.

#### Acceptance Criteria

1. WHEN THE System analyzes a file, THE Analysis Engine SHALL cache the AST with key "ast:{file_hash}" and TTL of 3600 seconds
2. WHEN THE System analyzes a file, THE Analysis Engine SHALL cache extracted functions/classes with key "symbols:{file_hash}" and TTL of 3600 seconds
3. WHEN THE System analyzes a file, THE Analysis Engine SHALL cache teaching value score with key "teaching_value:{file_hash}" and TTL of 3600 seconds
4. WHEN THE System receives a request for cached analysis, THE Analysis Engine SHALL return cached results in <100ms
5. WHEN THE System detects a file has changed (different hash), THE Analysis Engine SHALL invalidate cached results and re-analyze

### Requirement 9: Error Handling and Graceful Degradation

**User Story:** As a developer, I want the analysis engine to handle errors gracefully, so that one bad file doesn't break the entire analysis.

#### Acceptance Criteria

1. WHEN THE System encounters a syntax error during parsing, THE Analysis Engine SHALL log the error and continue with partial analysis
2. WHEN THE System cannot parse a file, THE Analysis Engine SHALL return an empty analysis result with error flag set to True
3. WHEN THE System encounters an unsupported file type, THE Analysis Engine SHALL skip the file and log a warning
4. WHEN THE System encounters a file permission error, THE Analysis Engine SHALL log the error and continue with other files
5. WHEN THE System completes analysis with errors, THE Analysis Engine SHALL include an errors array in the response with file paths and error messages

### Requirement 10: Performance Requirements

**User Story:** As a developer, I want analysis to be fast, so that I can analyze large codebases without long wait times.

#### Acceptance Criteria

1. WHEN THE System analyzes a single file, THE Analysis Engine SHALL complete parsing in <500ms for files under 1000 lines
2. WHEN THE System analyzes a codebase with 100 files, THE Analysis Engine SHALL complete full analysis in <30 seconds on first run
3. WHEN THE System analyzes a codebase with cached results, THE Analysis Engine SHALL complete in <3 seconds
4. WHEN THE System analyzes files in parallel, THE Analysis Engine SHALL process at least 10 files concurrently
5. WHEN THE System completes analysis, THE Analysis Engine SHALL log performance metrics including total_time_ms, files_analyzed, cache_hit_rate

### Requirement 11: MCP Tool Integration

**User Story:** As a developer, I want to access analysis features through MCP tools, so that I can integrate with AI assistants like Claude.

#### Acceptance Criteria

1. WHEN THE System registers MCP tools, THE Analysis Engine SHALL expose an analyze_file tool that accepts file_path and returns AST, functions, classes, and teaching_value
2. WHEN THE System registers MCP tools, THE Analysis Engine SHALL expose a detect_patterns tool that accepts codebase_id and returns detected patterns with confidence scores
3. WHEN THE System registers MCP tools, THE Analysis Engine SHALL expose an analyze_dependencies tool that accepts codebase_id and returns import graph and dependency metrics
4. WHEN THE System registers MCP tools, THE Analysis Engine SHALL expose a score_teaching_value tool that accepts file_path and returns teaching value score with explanation
5. WHEN THE System calls any analysis tool, THE Analysis Engine SHALL validate inputs and return clear error messages for invalid parameters

### Requirement 12: Configuration and Customization

**User Story:** As a developer, I want to configure analysis behavior, so that I can tune the engine for different types of codebases.

#### Acceptance Criteria

1. WHEN THE System loads configuration, THE Analysis Engine SHALL read max_complexity_threshold from config.yaml (default: 10)
2. WHEN THE System loads configuration, THE Analysis Engine SHALL read min_documentation_coverage from config.yaml (default: 0.5)
3. WHEN THE System loads configuration, THE Analysis Engine SHALL read teaching_value_weights from config.yaml for documentation, complexity, and pattern factors
4. WHEN THE System loads configuration, THE Analysis Engine SHALL read supported_languages from config.yaml (default: ["python", "javascript", "typescript"])
5. WHEN THE System loads configuration, THE Analysis Engine SHALL validate all configuration values and use defaults for invalid values

### Requirement 13: Logging and Diagnostics

**User Story:** As a developer, I want detailed logging of analysis operations, so that I can debug issues and monitor performance.

#### Acceptance Criteria

1. WHEN THE System starts analysis, THE Analysis Engine SHALL log "Starting analysis for file: {file_path}" at INFO level
2. WHEN THE System completes analysis, THE Analysis Engine SHALL log "Analysis complete: {file_path} in {duration_ms}ms" at INFO level
3. WHEN THE System encounters an error, THE Analysis Engine SHALL log the full error with stack trace at ERROR level
4. WHEN THE System detects slow analysis (>1000ms), THE Analysis Engine SHALL log a warning with file path and duration
5. WHEN THE System completes batch analysis, THE Analysis Engine SHALL log summary statistics: total_files, successful, failed, total_time_ms, avg_time_per_file_ms

### Requirement 14: Testing and Validation

**User Story:** As a developer, I want to validate analysis accuracy, so that I can trust the results for educational content generation.

#### Acceptance Criteria

1. WHEN THE System is tested with sample Python files, THE Analysis Engine SHALL correctly extract 100% of function and class definitions
2. WHEN THE System is tested with sample JavaScript files, THE Analysis Engine SHALL correctly extract 100% of function and class definitions
3. WHEN THE System is tested with files containing syntax errors, THE Analysis Engine SHALL handle errors gracefully without crashing
4. WHEN THE System is tested with pattern detection, THE Analysis Engine SHALL achieve >90% accuracy on known patterns
5. WHEN THE System is tested with teaching value scoring, THE Analysis Engine SHALL assign consistent scores (variance <0.1) for the same file across multiple runs

### Requirement 15: Integration with Existing Tools

**User Story:** As a developer, I want the analysis engine to integrate with existing scan_codebase results, so that I can build on previous work.

#### Acceptance Criteria

1. WHEN THE System receives a codebase_id, THE Analysis Engine SHALL retrieve the scan results from cache using key "scan:{codebase_id}"
2. WHEN THE System analyzes a codebase, THE Analysis Engine SHALL use the file list from scan_codebase to determine which files to analyze
3. WHEN THE System completes analysis, THE Analysis Engine SHALL store results as a resource "codebase://analysis" accessible via MCP
4. WHEN THE System detects that scan_codebase has not been run, THE Analysis Engine SHALL raise ValueError with message "Codebase not scanned. Call scan_codebase first."
5. WHEN THE System stores analysis results, THE Analysis Engine SHALL include metadata: analyzed_at timestamp, total_files_analyzed, analysis_version
