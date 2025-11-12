# Implementation Plan - Course Generator

## Overview

This implementation plan breaks down the Course Generator into discrete, manageable coding tasks. Each task builds incrementally on previous work and references specific requirements from the requirements document.

The Course Generator transforms analysis results into educational courses with lessons, exercises, and multiple export formats.

---

## Task List

- [x] 1. Set up Course Generator project structure





  - Create directory structure for course generator components
  - Create data models for CourseOutline, Module, Lesson, Exercise
  - Create configuration class for course generation settings
  - _Requirements: 1.1, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 2. Implement Course Structure Generator





- [x] 2.1 Create CourseStructureGenerator class


  - Implement generate_course_structure() method
  - Implement group_by_patterns() for organizing files
  - Implement calculate_module_count() for determining modules
  - Implement sort_by_difficulty() for ordering modules
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2.2 Implement module creation logic


  - Create create_module() method
  - Implement lesson grouping by patterns
  - Calculate module duration and difficulty
  - Generate module learning objectives
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2.3 Implement learning progression logic


  - Implement prerequisite detection from imports
  - Implement difficulty calculation from complexity
  - Ensure prerequisite lessons appear before dependent lessons
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 2.4 Write unit tests for course structure generation








  - Test module count calculation
  - Test lesson grouping by patterns
  - Test difficulty ordering
  - Test prerequisite detection
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3. Implement Lesson Content Generator





- [x] 3.1 Create LessonContentGenerator class


  - Implement generate_lesson_content() method
  - Implement extract_code_example() for code extraction
  - Implement generate_objectives() from patterns
  - Implement generate_introduction() for lesson intro
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3.2 Implement content generation methods


  - Implement generate_explanation() with simple language
  - Implement generate_walkthrough() with code annotations
  - Implement generate_summary() for lesson recap
  - Implement add_annotations() for inline comments
  - _Requirements: 2.2, 2.3, 2.4, 7.1, 7.2, 7.3_

- [x] 3.3 Implement code example extraction


  - Extract relevant code sections (max 50 lines)
  - Add syntax highlighting metadata
  - Create code highlights for important sections
  - Generate line-by-line annotations
  - _Requirements: 2.1, 7.2, 7.4_

- [x] 3.4 Write unit tests for lesson content generation






  - Test learning objective generation
  - Test code example extraction
  - Test content structure
  - Test annotation generation
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Implement Exercise Generator





- [x] 4.1 Create ExerciseGenerator class


  - Implement generate_exercise() method
  - Implement extract_pattern_code() for solution code
  - Implement create_starter_code() with TODOs
  - Implement generate_instructions() for step-by-step guidance
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.2 Implement hint and test case generation


  - Implement generate_hints() with progressive revelation
  - Implement generate_test_cases() for validation
  - Ensure 1-3 exercises per lesson based on complexity
  - _Requirements: 3.3, 3.4, 3.5_

- [x] 4.3 Write unit tests for exercise generation







  - Test starter code generation with TODOs
  - Test hint generation
  - Test test case generation
  - Test solution code extraction
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Implement Template Engine






- [x] 5.1 Set up Jinja2 template system

  - Install Jinja2 dependency
  - Create template loader and environment
  - Create default templates directory
  - Implement template validation
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 5.2 Create lesson and exercise templates


  - Create lesson.md.j2 template
  - Create exercise.md.j2 template
  - Create module.md.j2 template
  - Create index.md.j2 template
  - _Requirements: 9.1, 9.2, 9.3_

- [x] 5.3 Implement template rendering


  - Implement render_template() method
  - Pass lesson data as template variables
  - Handle template errors gracefully
  - Support custom templates from config
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 6. Implement MkDocs Export





- [x] 6.1 Create MkDocsExporter class


  - Implement export_to_mkdocs() method
  - Create directory structure (docs/, mkdocs.yml)
  - Generate mkdocs.yml configuration
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6.2 Generate MkDocs content


  - Generate lesson markdown files in docs/
  - Create navigation structure hierarchically
  - Configure Material theme with code highlighting
  - Enable search and table of contents
  - _Requirements: 4.2, 4.3, 4.4, 4.5_

- [x] 6.3 Add MkDocs configuration


  - Configure markdown extensions (pymdownx, admonition)
  - Set up code highlighting with line numbers
  - Configure theme features (navigation, search)
  - Add plugins (search, tags)
  - _Requirements: 4.3, 4.5_

- [x] 6.4 Write integration tests for MkDocs export







  - Test directory structure creation
  - Test mkdocs.yml generation
  - Test lesson file generation
  - Test navigation structure
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 7. Implement Multi-Format Export





- [x] 7.1 Create ExportManager class


  - Implement export() method with format routing
  - Support MkDocs, Next.js, JSON, Markdown, PDF formats
  - Validate output directory permissions
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7.2 Implement JSON export

  - Convert CourseOutline to dict
  - Include all course data with schema
  - Write formatted JSON with proper indentation
  - _Requirements: 5.2_

- [x] 7.3 Implement Markdown export

  - Create standalone markdown files
  - Generate README with course overview
  - Use relative links between files
  - _Requirements: 5.4_

- [x] 7.4 Implement Next.js export

  - Generate Next.js project structure
  - Create React components for lessons
  - Generate course data as JSON
  - Create navigation component
  - _Requirements: 5.3_

- [x] 7.5 Implement PDF export (optional)

  - Use markdown-to-pdf library
  - Generate single PDF with all lessons
  - Add proper formatting and page breaks
  - _Requirements: 5.5_

- [x] 7.6 Write tests for export formats






  - Test JSON export structure
  - Test Markdown export
  - Test Next.js export
  - Test export error handling
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 8. Implement MCP Tools



- [x] 8.1 Implement export_course tool

  - Accept codebase_id and format parameters
  - Get analysis from cache
  - Generate course structure and content
  - Export to specified format
  - Return export statistics
  - _Requirements: 10.1, 10.4, 10.5_

- [x] 8.2 Implement generate_lesson_outline tool
  - Accept file_path parameter
  - Analyze file or get from cache
  - Generate lesson structure
  - Return lesson outline with objectives
  - _Requirements: 10.2, 10.4, 10.5_

- [x] 8.3 Implement create_exercise tool
  - Accept pattern_type and difficulty parameters
  - Find pattern example in codebase
  - Generate exercise with starter code
  - Return exercise with hints and tests
  - _Requirements: 10.3, 10.4, 10.5_

- [x] 8.4 Add MCP tool error handling
  - Validate input parameters
  - Return clear error messages
  - Handle missing analysis data
  - Handle export failures
  - _Requirements: 10.5, 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 8.5 Write integration tests for MCP tools










  - Test export_course with various formats
  - Test generate_lesson_outline
  - Test create_exercise
  - Test error handling
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [-] 9. Implement Content Validation



- [x] 9.1 Create ContentValidator class


  - Validate each lesson has learning objectives
  - Validate each lesson has code examples
  - Validate exercise starter code syntax
  - Validate internal links
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 9.2 Implement validation reporting
  - Generate validation report with issues
  - Include file paths and line numbers
  - Provide suggestions for fixes
  - _Requirements: 13.5_

- [ ]* 9.3 Write tests for content validation
  - Test validation rules
  - Test validation reporting
  - Test validation with invalid content
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 10. Implement Metadata Generation
- [ ] 10.1 Generate course metadata
  - Create course manifest with all metadata
  - Include title, description, author, version
  - Add creation date and tags
  - _Requirements: 14.1, 14.5_

- [ ] 10.2 Generate lesson metadata
  - Include title, difficulty, duration
  - Add prerequisites and learning objectives
  - Generate tags from patterns
  - _Requirements: 14.2, 14.4_

- [ ] 10.3 Generate exercise metadata
  - Include title, difficulty, estimated time
  - Add solution availability flag
  - _Requirements: 14.3_

- [ ] 11. Implement Performance Optimization
- [ ] 11.1 Add caching for generated content
  - Cache course structures
  - Cache lesson content
  - Cache exercise generation
  - Invalidate cache on file changes
  - _Requirements: 11.5, 15.1, 15.2_

- [ ] 11.2 Optimize generation speed
  - Ensure course outline generation <5s
  - Ensure lesson generation <2s
  - Ensure exercise generation <3s
  - Ensure MkDocs export <10s
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ]* 11.3 Write performance tests
  - Test course generation speed
  - Test lesson generation speed
  - Test export speed
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ] 12. Implement Incremental Updates
- [ ] 12.1 Add change detection
  - Detect which lessons need updates
  - Track course version history
  - Preserve manual edits
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [ ] 12.2 Implement update logic
  - Update only changed lessons
  - Archive deleted lessons
  - Complete updates in <3s for <5 changes
  - _Requirements: 15.1, 15.2, 15.3, 15.5_

- [ ] 13. Add Configuration and Customization
- [ ] 13.1 Create CourseConfig class
  - Add target_audience setting
  - Add course_focus setting
  - Add max_duration setting
  - Add template_dir setting
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 13.2 Implement audience filtering
  - Filter lessons by difficulty
  - Adjust content complexity
  - _Requirements: 8.2_

- [ ] 13.3 Implement focus filtering
  - Prioritize relevant patterns
  - Filter by course focus
  - _Requirements: 8.4_

- [ ] 14. Documentation and Examples
- [ ] 14.1 Create usage examples
  - Example: Export course to MkDocs
  - Example: Generate lesson outline
  - Example: Create exercise
  - Example: Custom templates

- [ ] 14.2 Document configuration options
  - Document CourseConfig settings
  - Document export formats
  - Document template customization

- [ ] 14.3 Create API documentation
  - Document all public classes
  - Document MCP tools
  - Document data models

---

## Notes

### Development Environment
**IMPORTANT:** Always use the present virtual environment (venv) for running tests and commands:
- Run tests: `.\venv\Scripts\python.exe -m pytest`
- Run Python commands: `.\venv\Scripts\python.exe`
- Install packages: `.\venv\Scripts\pip.exe install <package>`

### Implementation Order
1. Start with data models and course structure (Tasks 1-2)
2. Build content generation (Tasks 3-4)
3. Add template engine (Task 5)
4. Implement exports (Tasks 6-7)
5. Add MCP tools (Task 8)
6. Add validation and metadata (Tasks 9-10)
7. Optimize and add incremental updates (Tasks 11-12)
8. Add configuration (Task 13)
9. Document (Task 14)

### Testing Strategy
- Unit tests for each component
- Integration tests for full workflow
- Performance tests for speed targets
- Optional test tasks marked with `*`

### Dependencies
- Jinja2 for templating
- markdown library for processing
- Optional: weasyprint for PDF export
- Optional: next.js CLI for Next.js export

---

**Total Tasks:** 14 main tasks, 40+ sub-tasks
**Estimated Time:** 3-4 weeks for full implementation
**Priority:** Core functionality first (Tasks 1-8), then optimization and polish

