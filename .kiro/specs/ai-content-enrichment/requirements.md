# Requirements Document

## Introduction

This feature enhances the course generator by creating comprehensive, evidence-based enrichment guides that enable AI assistants (like Kiro) to generate accurate, educational content. Instead of directly generating content, the system collects evidence from multiple sources (code, tests, git history, documentation), validates understanding, assesses teaching value, and packages everything into structured guides that AI can use to create rich explanations, narratives, and exercises.

**Key Approach**: The system follows a systematic investigation framework that ensures all generated content is grounded in evidence, preventing hallucinations and maintaining accuracy. The enrichment guides include anti-hallucination rules requiring citations for every claim, validation checklists to ensure consistency across sources, and comprehensive context to enable beginner-friendly explanations.

## Glossary

- **Course Generator**: The system that transforms codebase analysis into educational course materials
- **Content Enrichment Engine**: The component that generates evidence-based enrichment guides for AI assistants to create educational content
- **Enrichment Guide**: A comprehensive, evidence-based document containing all context, evidence, and instructions needed for AI to enrich lesson content
- **Evidence Bundle**: A collection of source code, tests, git commits, and documentation that validates understanding of code functionality
- **Feature Mapping**: The process of connecting code implementation to user-facing features and business value
- **Teaching Value Assessment**: A scoring system (0-14) that evaluates whether code is worth teaching based on reusability, best practices, fundamentality, uniqueness, and junior developer value
- **Systematic Investigation**: A structured approach to understanding code by answering what, why, how, when, edge cases, and pitfalls with evidence citations
- **Git Analyzer**: A component that extracts git commit history to provide context about why code was written
- **Anti-Hallucination Rules**: Guidelines that require AI to cite evidence for all claims and distinguish facts from inferences

## Requirements

### Requirement 1

**User Story:** As a course creator, I want AI to automatically generate comprehensive explanations for code snippets, so that learners understand what the code does without needing to decipher it themselves

#### Acceptance Criteria

1. WHEN the Course Generator processes a code file, THE Content Enrichment Engine SHALL generate a plain-language explanation of what the code accomplishes
2. WHEN generating explanations, THE Content Enrichment Engine SHALL identify the primary purpose and functionality of each code section
3. WHEN a code snippet is included in a lesson, THE Content Enrichment Engine SHALL provide context about how it fits into the larger application
4. THE Content Enrichment Engine SHALL generate explanations that are appropriate for the target audience skill level
5. THE Content Enrichment Engine SHALL avoid technical jargon unless it is defined and explained

### Requirement 2

**User Story:** As a course creator, I want the system to collect evidence from multiple sources (code, tests, git history, documentation), so that AI-generated content is accurate and grounded in facts

#### Acceptance Criteria

1. WHEN analyzing code for enrichment, THE Content Enrichment Engine SHALL collect source code files with line number references
2. WHEN analyzing code for enrichment, THE Content Enrichment Engine SHALL identify and collect related test files that validate behavior
3. WHEN analyzing code for enrichment, THE Content Enrichment Engine SHALL retrieve relevant git commits that explain the "why" behind code changes
4. WHEN analyzing code for enrichment, THE Content Enrichment Engine SHALL extract inline documentation, comments, and README sections
5. WHEN analyzing code for enrichment, THE Content Enrichment Engine SHALL identify dependencies and dependents with evidence of their relationships

### Requirement 3

**User Story:** As a course creator, I want the system to validate understanding against multiple evidence sources, so that generated content is consistent and accurate

#### Acceptance Criteria

1. WHEN validating code understanding, THE Content Enrichment Engine SHALL analyze what the code actually does by reading the implementation
2. WHEN validating code understanding, THE Content Enrichment Engine SHALL analyze what tests expect the code to do
3. WHEN validating code understanding, THE Content Enrichment Engine SHALL check alignment between code behavior and documentation
4. WHEN validating code understanding, THE Content Enrichment Engine SHALL extract context from git commit messages explaining why code exists
5. WHEN validating code understanding, THE Content Enrichment Engine SHALL cross-reference all evidence sources to ensure consistency

### Requirement 4

**User Story:** As a course creator, I want the system to assess teaching value of code sections, so that lessons focus on the most educational and reusable patterns

#### Acceptance Criteria

1. WHEN assessing code for teaching value, THE Content Enrichment Engine SHALL score reusability on a scale of 0-3 based on pattern applicability
2. WHEN assessing code for teaching value, THE Content Enrichment Engine SHALL score best practice adherence on a scale of 0-3
3. WHEN assessing code for teaching value, THE Content Enrichment Engine SHALL score fundamentality on a scale of 0-3 based on concept importance
4. WHEN assessing code for teaching value, THE Content Enrichment Engine SHALL score uniqueness on a scale of 0-2 based on interesting or novel aspects
5. WHEN assessing code for teaching value, THE Content Enrichment Engine SHALL score junior developer value on a scale of 0-3 based on learning benefit
6. WHEN total teaching value score exceeds 7 out of 14, THE Content Enrichment Engine SHALL recommend including the code in the course

### Requirement 5

**User Story:** As a course creator, I want the system to systematically investigate code to answer key questions, so that enrichment guides provide comprehensive understanding

#### Acceptance Criteria

1. WHEN investigating code, THE Content Enrichment Engine SHALL describe what the code does with factual citations to code sections
2. WHEN investigating code, THE Content Enrichment Engine SHALL explain why the code exists with citations to git commits or documentation
3. WHEN investigating code, THE Content Enrichment Engine SHALL explain how the code works with citations to implementation details
4. WHEN investigating code, THE Content Enrichment Engine SHALL identify when the code is used with citations to call sites
5. WHEN investigating code, THE Content Enrichment Engine SHALL identify edge cases with citations to test files
6. WHEN investigating code, THE Content Enrichment Engine SHALL identify common pitfalls with citations to comments or test cases

### Requirement 6

**User Story:** As a course creator, I want the system to generate comprehensive enrichment guides with evidence, so that AI assistants have all necessary context to create accurate content

#### Acceptance Criteria

1. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include feature mapping that connects code to user-facing functionality
2. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include an evidence bundle with source files, tests, git commits, and documentation
3. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include a validation checklist confirming understanding consistency
4. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include teaching value assessment with scoring and reasoning
5. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include systematic investigation results answering what, why, how, when, and edge cases
6. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include narrative structure with introduction points, learning progression, and conclusion points
7. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include code section guides with purpose, concepts, explanation approach, and evidence citations
8. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include architecture context with component roles, data flow, and interaction diagrams
9. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include real-world context with use cases, analogies, and best practices
10. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include exercise generation with starter code, solutions, hints, and test cases from the codebase
11. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include anti-hallucination rules requiring evidence citations for all claims
12. WHEN generating an enrichment guide, THE Content Enrichment Engine SHALL include enrichment instructions specifying tone, depth, focus areas, and evidence requirements

### Requirement 7

**User Story:** As a course creator, I want MCP tools to retrieve and update lesson content, so that AI assistants can enrich courses through the MCP protocol

#### Acceptance Criteria

1. THE Content Enrichment Engine SHALL provide an MCP tool named get_enrichment_guide that accepts codebase_id and lesson_id parameters
2. WHEN get_enrichment_guide is called, THE Content Enrichment Engine SHALL return a comprehensive enrichment guide following the structure defined in Requirement 6
3. THE Content Enrichment Engine SHALL provide an MCP tool named update_lesson_content that accepts codebase_id, lesson_id, and enriched_content parameters
4. WHEN update_lesson_content is called with valid enriched content, THE Content Enrichment Engine SHALL validate the content structure
5. WHEN update_lesson_content is called with valid enriched content, THE Content Enrichment Engine SHALL merge the enriched content into the lesson data
6. WHEN update_lesson_content is called with valid enriched content, THE Content Enrichment Engine SHALL persist the updated lesson to storage
7. WHEN update_lesson_content is called with invalid content, THE Content Enrichment Engine SHALL return an error message describing the validation failure

### Requirement 8

**User Story:** As a course creator, I want the system to analyze git history, so that enrichment guides include context about why code was written

#### Acceptance Criteria

1. THE Content Enrichment Engine SHALL provide a git analyzer component that detects if a directory is a git repository
2. WHEN analyzing files for enrichment, THE Content Enrichment Engine SHALL retrieve git commits that modified those files
3. WHEN retrieving git commits, THE Content Enrichment Engine SHALL extract commit hash, message, author, and date
4. WHEN searching for feature-related commits, THE Content Enrichment Engine SHALL search commit messages for feature names or keywords
5. WHEN a directory is not a git repository, THE Content Enrichment Engine SHALL handle the error gracefully and continue without git evidence
6. WHEN git commands fail, THE Content Enrichment Engine SHALL log the error and return empty results rather than failing the entire enrichment process
