# Requirements Document - Course Generator

## Introduction

The Course Generator transforms codebase analysis results into structured educational courses. It takes the output from the Analysis Engine (teaching value scores, patterns, dependencies, complexity metrics) and generates complete course materials including lesson outlines, code examples, exercises, and exports to multiple formats (MkDocs, Next.js, JSON).

The Course Generator is the bridge between "analyzing code" and "teaching from code" - it's what makes Documee a "codebase-to-course platform" rather than just an analysis tool.

## Glossary

- **Course Generator**: The system that transforms analysis results into educational content
- **CourseOutline**: A structured representation of the complete course with modules, lessons, and exercises
- **Lesson**: A single educational unit focused on teaching one concept or pattern
- **Module**: A collection of related lessons grouped by theme or difficulty
- **Exercise**: A hands-on coding challenge for students to practice concepts
- **TeachableCode**: Code identified by the Analysis Engine as having high teaching value
- **MkDocs**: A static site generator for creating documentation and course websites
- **Export Format**: The output format for course content (MkDocs, Next.js, JSON, Markdown, PDF)
- **Learning Objective**: A specific skill or concept students will learn from a lesson
- **Prerequisite**: Knowledge or skills required before starting a lesson
- **Difficulty Level**: The complexity rating of a lesson (beginner, intermediate, advanced)
- **Content Template**: A reusable structure for generating consistent lesson content

## Requirements

### Requirement 1: Course Structure Generation

**User Story:** As a course creator, I want to automatically generate a course structure from analyzed code, so that I can quickly organize content into a logical learning progression.

#### Acceptance Criteria

1. WHEN the Course Generator receives a CodebaseAnalysis, THE Course Generator SHALL create a CourseOutline with modules organized by difficulty level.

2. WHEN organizing lessons within modules, THE Course Generator SHALL sort lessons by teaching value score in descending order.

3. WHEN determining module count, THE Course Generator SHALL create between 3 and 8 modules based on the number of teachable files.

4. WHEN assigning lessons to modules, THE Course Generator SHALL group lessons by related patterns or concepts.

5. THE Course Generator SHALL estimate total course duration based on lesson count and complexity.

### Requirement 2: Lesson Content Generation

**User Story:** As a course creator, I want to automatically generate lesson content from code examples, so that I can create comprehensive educational materials without manual writing.

#### Acceptance Criteria

1. WHEN generating a lesson from TeachableCode, THE Course Generator SHALL extract the code example with syntax highlighting.

2. WHEN creating lesson content, THE Course Generator SHALL generate 3 to 5 learning objectives based on detected patterns and concepts.

3. WHEN explaining code, THE Course Generator SHALL add inline comments to clarify complex logic.

4. WHEN structuring a lesson, THE Course Generator SHALL include sections for introduction, explanation, code walkthrough, and summary.

5. THE Course Generator SHALL generate lesson content in Markdown format with proper heading hierarchy.

### Requirement 3: Exercise Generation

**User Story:** As a course creator, I want to automatically generate coding exercises from patterns, so that students can practice the concepts they learn.

#### Acceptance Criteria

1. WHEN generating an exercise from a DetectedPattern, THE Course Generator SHALL create starter code with TODO comments.

2. WHEN creating exercise instructions, THE Course Generator SHALL provide clear step-by-step guidance.

3. WHEN generating solutions, THE Course Generator SHALL include complete working code with explanations.

4. THE Course Generator SHALL create between 1 and 3 exercises per lesson based on lesson complexity.

5. WHEN generating exercises, THE Course Generator SHALL include hints that progressively reveal solution steps.

### Requirement 4: MkDocs Integration

**User Story:** As a course creator, I want to export courses to MkDocs format, so that I can publish professional-looking course websites.

#### Acceptance Criteria

1. WHEN exporting to MkDocs, THE Course Generator SHALL generate a valid mkdocs.yml configuration file.

2. WHEN creating MkDocs navigation, THE Course Generator SHALL organize content hierarchically with modules as top-level sections.

3. WHEN generating MkDocs content, THE Course Generator SHALL use the Material for MkDocs theme with code highlighting enabled.

4. THE Course Generator SHALL create a docs/ directory structure with one markdown file per lesson.

5. WHEN configuring MkDocs, THE Course Generator SHALL enable search functionality and table of contents.

### Requirement 5: Multi-Format Export

**User Story:** As a course creator, I want to export courses in multiple formats, so that I can use the content in different platforms and contexts.

#### Acceptance Criteria

1. THE Course Generator SHALL support export to MkDocs, Next.js, JSON, Markdown, and PDF formats.

2. WHEN exporting to JSON, THE Course Generator SHALL include all course data in a structured format with schema validation.

3. WHEN exporting to Next.js, THE Course Generator SHALL generate React components for lessons and exercises.

4. WHEN exporting to Markdown, THE Course Generator SHALL create standalone markdown files with relative links.

5. WHEN exporting to PDF, THE Course Generator SHALL generate a single PDF document with proper formatting and page breaks.

### Requirement 6: Learning Progression

**User Story:** As a course creator, I want courses to follow a logical learning progression, so that students can build knowledge incrementally.

#### Acceptance Criteria

1. WHEN ordering lessons, THE Course Generator SHALL place beginner lessons before intermediate and advanced lessons.

2. WHEN identifying prerequisites, THE Course Generator SHALL analyze lesson dependencies based on code imports and patterns.

3. WHEN a lesson requires prior knowledge, THE Course Generator SHALL list prerequisite lessons in the lesson metadata.

4. THE Course Generator SHALL ensure that prerequisite lessons appear before dependent lessons in the course structure.

5. WHEN calculating difficulty, THE Course Generator SHALL use complexity metrics and pattern sophistication to assign difficulty levels.

### Requirement 7: Content Quality

**User Story:** As a course creator, I want generated content to be clear and educational, so that students can learn effectively.

#### Acceptance Criteria

1. WHEN generating explanations, THE Course Generator SHALL use simple language appropriate for the target difficulty level.

2. WHEN including code examples, THE Course Generator SHALL limit examples to 50 lines or fewer for readability.

3. WHEN creating learning objectives, THE Course Generator SHALL use action verbs (understand, implement, apply, analyze).

4. THE Course Generator SHALL include at least one code example per lesson.

5. WHEN generating content, THE Course Generator SHALL avoid jargon unless it is defined in a glossary.

### Requirement 8: Customization

**User Story:** As a course creator, I want to customize course generation settings, so that I can tailor courses to specific audiences and goals.

#### Acceptance Criteria

1. THE Course Generator SHALL accept configuration for target audience (beginner, intermediate, advanced, mixed).

2. WHEN target audience is specified, THE Course Generator SHALL filter lessons to match the audience level.

3. THE Course Generator SHALL accept configuration for course focus (patterns, architecture, best practices, full-stack).

4. WHEN course focus is specified, THE Course Generator SHALL prioritize relevant content and patterns.

5. THE Course Generator SHALL accept configuration for maximum course duration in hours.

### Requirement 9: Template System

**User Story:** As a course creator, I want to use customizable templates for content generation, so that I can maintain consistent formatting and style.

#### Acceptance Criteria

1. THE Course Generator SHALL use Jinja2 templates for generating lesson content.

2. WHEN templates are not provided, THE Course Generator SHALL use default templates for lessons, exercises, and modules.

3. THE Course Generator SHALL allow custom templates to be provided via configuration.

4. WHEN rendering templates, THE Course Generator SHALL pass lesson data, code examples, and metadata as template variables.

5. THE Course Generator SHALL validate template syntax before rendering.

### Requirement 10: MCP Tool Integration

**User Story:** As an AI assistant, I want to access course generation via MCP tools, so that I can help users create courses through natural language.

#### Acceptance Criteria

1. THE Course Generator SHALL provide an export_course MCP tool that accepts codebase_id and format parameters.

2. THE Course Generator SHALL provide a generate_lesson_outline MCP tool that accepts file_path parameter.

3. THE Course Generator SHALL provide a create_exercise MCP tool that accepts pattern_type parameter.

4. WHEN MCP tools are called, THE Course Generator SHALL return results in JSON format.

5. WHEN MCP tools encounter errors, THE Course Generator SHALL return clear error messages with suggested fixes.

### Requirement 11: Performance

**User Story:** As a course creator, I want course generation to be fast, so that I can iterate quickly on course content.

#### Acceptance Criteria

1. THE Course Generator SHALL generate a complete course outline in less than 5 seconds for a 100-file codebase.

2. THE Course Generator SHALL generate a single lesson in less than 2 seconds.

3. THE Course Generator SHALL generate all exercises for a lesson in less than 3 seconds.

4. WHEN exporting to MkDocs, THE Course Generator SHALL complete export in less than 10 seconds for a 20-lesson course.

5. THE Course Generator SHALL use caching to avoid regenerating unchanged content.

### Requirement 12: Error Handling

**User Story:** As a course creator, I want clear error messages when generation fails, so that I can fix issues quickly.

#### Acceptance Criteria

1. WHEN analysis data is missing, THE Course Generator SHALL return an error message indicating which data is required.

2. WHEN export directory is not writable, THE Course Generator SHALL return an error message with the directory path.

3. WHEN template rendering fails, THE Course Generator SHALL return an error message with the template name and line number.

4. THE Course Generator SHALL validate input parameters and return clear error messages for invalid inputs.

5. WHEN generation fails, THE Course Generator SHALL log detailed error information for debugging.

### Requirement 13: Content Validation

**User Story:** As a course creator, I want generated content to be validated for quality, so that I can ensure courses meet educational standards.

#### Acceptance Criteria

1. THE Course Generator SHALL validate that each lesson has at least one learning objective.

2. THE Course Generator SHALL validate that each lesson has at least one code example.

3. THE Course Generator SHALL validate that exercise starter code is syntactically valid.

4. THE Course Generator SHALL validate that all internal links in generated content are valid.

5. WHEN validation fails, THE Course Generator SHALL return a validation report with specific issues and locations.

### Requirement 14: Metadata Generation

**User Story:** As a course creator, I want comprehensive metadata for courses and lessons, so that I can track and organize content effectively.

#### Acceptance Criteria

1. THE Course Generator SHALL generate metadata for each course including title, description, author, version, and creation date.

2. THE Course Generator SHALL generate metadata for each lesson including title, difficulty, duration, prerequisites, and learning objectives.

3. THE Course Generator SHALL generate metadata for each exercise including title, difficulty, estimated time, and solution availability.

4. THE Course Generator SHALL include tags for each lesson based on detected patterns and concepts.

5. THE Course Generator SHALL generate a course manifest file listing all lessons, modules, and resources.

### Requirement 15: Incremental Updates

**User Story:** As a course creator, I want to update courses when code changes, so that course content stays synchronized with the codebase.

#### Acceptance Criteria

1. WHEN regenerating a course, THE Course Generator SHALL detect which lessons need updates based on file changes.

2. THE Course Generator SHALL preserve manual edits to lesson content when regenerating.

3. WHEN a file is deleted, THE Course Generator SHALL mark the corresponding lesson as archived rather than deleting it.

4. THE Course Generator SHALL track course version history with timestamps and change summaries.

5. WHEN updating a course, THE Course Generator SHALL complete updates in less than 3 seconds for courses with fewer than 5 changed files.

---

## Summary

This requirements document defines 15 core requirements for the Course Generator with 75 acceptance criteria. The Course Generator transforms analysis results into educational content, supporting multiple export formats and providing a complete solution for creating courses from codebases.

**Key Capabilities:**
- Automatic course structure generation
- Lesson content generation with code examples
- Exercise generation with solutions
- MkDocs integration for professional course websites
- Multi-format export (MkDocs, Next.js, JSON, Markdown, PDF)
- Customizable templates and settings
- MCP tool integration for AI assistants
- Fast performance (<5s for course outline)
- Comprehensive validation and error handling

**Next Steps:**
1. Review and approve requirements
2. Create design document
3. Create implementation tasks
4. Begin development
