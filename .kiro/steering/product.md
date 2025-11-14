# Product Overview

## Documee MCP Server

A Model Context Protocol (MCP) server that transforms codebases into teachable course platforms through automated analysis and course generation.

## Core Capabilities

**Codebase Analysis**
- Multi-language AST parsing (Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, Ruby, PHP)
- Symbol extraction (functions, classes, imports, exports)
- Pattern detection (React components, API routes, database operations, authentication)
- Dependency graph analysis with circular dependency detection
- Teaching value scoring (0.0-1.0) based on documentation, complexity, patterns, and structure

**Course Generation**
- Automated lesson outline generation from analyzed code
- Exercise creation with starter code, solutions, hints, and test cases
- Multiple export formats: MkDocs, Next.js, JSON, Markdown, PDF
- Configurable target audience (beginner, intermediate, advanced)
- Configurable course focus (patterns, architecture, best-practices, full-stack)

**Performance**
- 3-tier caching system (Memory LRU, SQLite, Redis)
- Parallel file processing (10+ concurrent)
- Incremental analysis (only re-analyze changed files)
- Sub-100ms cached operations, 2-3s initial scans

## Target Users

- Developers creating educational content from existing codebases
- Technical educators building programming courses
- Development teams onboarding new members
- Open source maintainers documenting their projects

## Key Value Proposition

Automatically converts production code into structured learning materials with minimal manual effort, maintaining accuracy through evidence-based validation and achieving "God Mode" performance through intelligent caching.
