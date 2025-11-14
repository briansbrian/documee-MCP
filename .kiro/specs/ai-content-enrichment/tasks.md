# Implementation Plan

## Overview
Implement AI content enrichment by creating MCP tools that provide comprehensive, evidence-based enrichment guides for Kiro to use when generating rich educational content. The system follows the Feature-to-Lesson Mapping and Knowledge-to-Course frameworks to ensure accurate, validated content generation.

---



always use venv\Scripts\python.exe

## Phase 1: Core Data Models & Evidence Collection

- [x] 1. Create enrichment data models













  - Create `src/course/enrichment_models.py` with all dataclass models
  - Implement FeatureMapping, EvidenceBundle, ValidationChecklist models
  - Implement TeachingValueAssessment, SystematicInvestigation models
  - Implement NarrativeStructure, CodeSectionGuide models
  - Implement ArchitectureContext, RealWorldContext models
  - Implement ExerciseGeneration, AntiHallucinationRules models
  - Implement EnrichmentInstructions, EnrichmentGuide models
  - Add to_dict() and from_dict() methods for JSON serialization
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1_




- [x] 2. Implement Git analyzer for evidence collection










  - Create `src/analysis/git_analyzer.py` module
  - Implement get_relevant_commits(file_paths) to find commits for files
  - Implement get_commit_context(commit_hash) to extract commit details
  - Implement find_feature_commits(feature_name) to search commit messages
  - Handle git repository detection and error cases
  - _Requirements: 2.1, 2.2, 2.3_





- [x] 3. Implement evidence collection utilities








  - Create `src/course/evidence_collector.py` module
  - Implement collect_source_evidence(lesson) to gather code with line numbers
  - Implement collect_test_evidence(lesson) to find and parse related tests
  - Implement collect_documentation_evidence(file_analysis) to extract comments/docs
  - Implement collect_dependency_evidence(file_analysis) to map dependencies
  - _Requirements: 2.1, 2.2, 2.3_



---

## Phase 2: Feature Mapping & Investigation




- [x] 4. Implement feature mapping analyzer








  - Create `src/course/feature_mapper.py` module

  - Implement identify_feature_from_code(lesson, file_analysis) to detect features
  - Implement extract_user_flow(feature) to trace user interactions
  - Implement extract_business_value(feature, evidence) from docs/commits
  - Implement find_entry_points(feature) for UI/API/CLI entry points

  - _Requirements: 2.1, 2.2, 4.1, 4.2_

- [x] 5. Implement systematic investigation engine











  - Create `src/course/investigation_engine.py` module
  - Implement investigate_what_it_does(evidence) with code citations
  - Implement investigate_why_it_exists(evidence) with git/doc citations
  - Implement investigate_how_it_works(evidence) with code section analysis
  - Implement investigate_when_used(evidence) with call site analysis
  - Implement investigate_edge_cases(evidence) from test analysis
  - Implement investigate_pitfalls(evidence) from comments/tests
  - _Requirements: 2.1, 2.2, 2.3, 4.1_


- [x] 6. Implement teaching value scorer







  - Create `src/course/teaching_value_assessor.py` module
  - Implement score_reusability(patterns) → 0-3 points
  - Implement score_best_practice(evidence) → 0-3 points
  - Implement score_fundamentality(feature) → 0-3 points
  - Implement score_uniqueness(analysis) → 0-2 points
  - Implement score_junior_dev_value(feature, analysis) → 0-3 points
  - Implement calculate_total_score() and should_teach() logic
  - _Requirements: 3.1, 3.2, 3.3, 6.1_

---

## Phase 3: Enrichment Guide Generator



- [x] 7. Implement validation engine






  - Create `src/course/validation_engine.py` module
  - Implement validate_code_behavior(source_files) to analyze actual behavior
  - Implement validate_test_expectations(test_files) to extract expected behavior
  - Implement validate_documentation_alignment(docs) to check consistency
  - Implement validate_git_context(commits) to extract historical context
  - Implement cross_reference_sources(evidence) to verify consistency
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 8. Implement narrative structure builder









  - Create `src/course/narrative_builder.py` module
  - Implement build_introduction_points(investigation) for context/motivation
  - Implement build_learning_progression(concepts) ordered simple → complex
  - Implement build_code_walkthrough_order(code_sections) for explanation flow
  - Implement build_conclusion_points(investigation) for key takeaways
  - Implement suggest_next_steps(lesson, course_outline) for progression
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 9. Implement code section guide generator





  - Create `src/course/code_section_guide_generator.py` module
  - Implement generate_section_guide(code_example, evidence) with full citations
  - Implement describe_purpose_with_evidence(code, tests) citing test results
  - Implement extract_key_concepts(code) from patterns and structure
  - Implement suggest_explanation_approach(code) for progressive disclosure
  - Implement find_related_code(code, evidence) with context
  - Implement identify_common_mistakes(code, tests) from test failures
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 3.1_

- [x] 10. Implement architecture context extractor





  - Create `src/course/architecture_extractor.py` module
  - Implement extract_component_role(file, dependency_graph) with evidence
  - Implement extract_data_flow(file, evidence) tracing data movement
  - Implement generate_interaction_diagram(dependencies) as Mermaid
  - Implement extract_dependencies_with_evidence(file) citing imports
  - Implement extract_design_patterns(file, patterns) with evidence
  - _Requirements: 2.2, 2.3, 4.1_

- [x] 11. Implement real-world context suggester





  - Create `src/course/real_world_context_suggester.py` module
  - Implement suggest_use_cases(feature) for practical scenarios
  - Implement suggest_analogies(feature, skill_level) for beginners
  - Implement identify_industry_patterns(patterns) for standard approaches
  - Implement extract_best_practices(evidence) from code quality
  - Implement identify_anti_patterns(evidence) from issues/comments
  - _Requirements: 4.1, 4.2, 6.1_

- [x] 12. Implement exercise generator from codebase





  - Create `src/course/exercise_from_code_generator.py` module
  - Implement extract_solution_code(evidence) from actual codebase
  - Implement create_starter_code(solution) by removing implementation
  - Implement extract_requirements_from_tests(tests) for exercise specs
  - Implement generate_progressive_hints(solution, requirements) 3-5 hints
  - Implement create_assessment_questions(feature, evidence) for self-check
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 13. Implement main enrichment guide generator





  - Create `src/course/enrichment_guide_generator.py` module
  - Implement generate_guide(codebase_id, lesson_id) orchestrating all components
  - Integrate feature mapping, evidence collection, validation
  - Integrate teaching value assessment, systematic investigation
  - Integrate narrative building, code section guides, architecture context
  - Integrate real-world context, exercise generation
  - Add anti-hallucination rules and enrichment instructions
  - Return complete EnrichmentGuide dataclass
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 5.1, 6.1_

---

## Phase 4: MCP Tool Integration

- [x] 14. Add get_enrichment_guide MCP tool






  - Add tool to `src/server.py` with @mcp.tool() decorator
  - Implement get_enrichment_guide(codebase_id, lesson_id) function
  - Initialize EnrichmentGuideGenerator with required dependencies
  - Call generator.generate_guide() and return result as dict
  - Add comprehensive error handling and logging
  - Add parameter validation (codebase_id exists, lesson_id valid)
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 4.1, 5.1, 6.1_

- [x] 15. Add update_lesson_content MCP tool





  - Add tool to `src/server.py` with @mcp.tool() decorator
  - Implement update_lesson_content(codebase_id, lesson_id, enriched_content)
  - Validate enriched_content structure (required fields present)
  - Load existing course data and find target lesson
  - Merge enriched content into lesson (preserve structure)
  - Save updated course data to disk
  - Update enrichment status tracking
  - Return success status with updated fields list
  - _Requirements: 1.1, 1.2, 1.3, 3.1_

- [x] 16. Add list_lessons_for_enrichment MCP tool








  - Add tool to `src/server.py` with @mcp.tool() decorator
  - Implement list_lessons_for_enrichment(codebase_id)
  - Load course data and extract all lessons
  - Check enrichment status for each lesson
  - Return list with lesson_id, title, status, source_files
  - Sort by teaching value score (high to low)
  - _Requirements: 1.1, 3.1, 6.1_

---

## Phase 5: Configuration & Documentation

- [x] 17. Add enrichment configuration





  - Extend `config.yaml` with ai_enrichment section
  - Add defaults: skill_level="beginner", tone="casual", depth="detailed"
  - Add content_options: include_analogies, include_diagrams, etc.
  - Update `src/config/settings.py` to load enrichment config
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 18. Create enrichment steering file





  - Create `.kiro/steering/ai-content-enrichment.md`
  - Document enrichment workflow for Kiro
  - Include content guidelines (beginner-friendly, evidence-based)
  - Include anti-hallucination rules (always cite, validate against tests)
  - Include example enrichment process
  - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2, 3.3, 6.1_

---

## Phase 6: Testing & Validation

- [x] 19. Write unit tests for enrichment components





  - Create `tests/test_enrichment_guide_generator.py`
  - Test feature mapping with mock data
  - Test evidence collection from sample files
  - Test validation engine with consistent/inconsistent data
  - Test teaching value scoring with various patterns
  - Test narrative structure building
  - Test code section guide generation with citations
  - _Requirements: All_

- [x] 20. Write integration tests for MCP tools





  - Create `tests/test_enrichment_mcp_tools.py`
  - Test get_enrichment_guide with real codebase
  - Verify all evidence fields are populated
  - Verify citations are present and accurate
  - Test update_lesson_content with enriched data
  - Test list_lessons_for_enrichment returns correct status
  - Verify enrichment status tracking works
  - _Requirements: All_

- [x] 21. Test end-to-end enrichment workflow





  - Create `tests/test_enrichment_workflow.py`
  - Generate basic course with export_course
  - Get enrichment guide for a lesson
  - Verify guide contains all required sections
  - Verify evidence citations are accurate
  - Simulate Kiro enrichment (manual or scripted)
  - Update lesson with enriched content
  - Verify enriched content persists correctly
  - Export enriched course and verify rendering
  - _Requirements: All_

- [x] 22. Validate enrichment quality





  - Create `tests/test_enrichment_quality.py`
  - Test that explanations cite actual code
  - Test that examples are from real codebase
  - Test that exercises have validation tests
  - Test that hints are progressive (general → specific)
  - Test that analogies are beginner-friendly
  - Test anti-hallucination rules are enforced
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.3, 6.1_

---

## Phase 7: Documentation & Examples

- [x] 23. Document enrichment system




  - Create `docs/AI_CONTENT_ENRICHMENT.md`
  - Document the enrichment workflow
  - Document MCP tools (get_enrichment_guide, update_lesson_content)
  - Document enrichment guide structure
  - Document evidence-based approach
  - Document anti-hallucination measures
  - Include examples of enrichment guides
  - _Requirements: All_

- [x] 24. Create enrichment examples





  - Create `examples/enrichment_example.py`
  - Show how to get enrichment guide
  - Show how to use guide for content generation
  - Show how to update lesson with enriched content
  - Create `examples/enrichment_guide_sample.json`
  - Include complete sample enrichment guide
  - _Requirements: All_

- [x] 25. Update main documentation





  - Update `README.md` with enrichment feature
  - Update `docs/START_HERE.md` with enrichment workflow
  - Update `docs/PROJECT_STATUS_AND_ROADMAP.md` with completion status
  - Update MCP tool list in documentation
  - Add enrichment to feature list
  - _Requirements: All_

---

## Notes

- Each task builds on previous tasks
- Evidence collection is critical for anti-hallucination
- All explanations must cite sources (code, tests, commits, docs)
- Teaching value scoring determines what gets taught
- Enrichment guides provide structure, Kiro provides content
- Focus on beginner-friendly, evidence-based content

always use venv\Scripts\python.exe
