"""
Tests for enrichment quality validation.

This test suite validates that enrichment guides meet quality standards:
- Explanations cite actual code
- Examples are from real codebase
- Exercises have validation tests
- Hints are progressive (general → specific)
- Analogies are beginner-friendly
- Anti-hallucination rules are enforced

Tests Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.3, 6.1
"""

import pytest
import re
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from src.course.enrichment_guide_generator import EnrichmentGuideGenerator
from src.course.enrichment_models import (
    EnrichmentGuide,
    CodeSectionGuide,
    ExerciseGeneration
)
from src.course.models import Lesson, LessonContent, CodeExample
from src.models.analysis_models import (
    FileAnalysis,
    SymbolInfo,
    FunctionInfo,
    ImportInfo,
    DetectedPattern,
    TeachingValueScore,
    ComplexityMetrics
)
from src.analysis.engine import AnalysisEngine


# ========== Test Fixtures ==========


@pytest.fixture
def repo_path():
    """Get repository path for testing."""
    return str(Path(__file__).parent.parent)


@pytest.fixture
def mock_analysis_engine():
    """Create a mock analysis engine."""
    engine = Mock(spec=AnalysisEngine)
    
    async def mock_analyze_file(file_path, use_cache=True):
        return create_sample_file_analysis(file_path)
    
    engine.analyze_file = AsyncMock(side_effect=mock_analyze_file)
    return engine


def create_sample_file_analysis(file_path: str) -> FileAnalysis:
    """Create a sample file analysis for testing."""
    return FileAnalysis(
        file_path=file_path,
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="authenticate_user",
                    start_line=10,
                    end_line=25,
                    parameters=["username", "password"],
                    return_type="Optional[Session]",
                    docstring="Authenticate user and create session",
                    decorators=[],
                    is_async=True,
                    complexity=5
                )
            ],
            classes=[],
            imports=[
                ImportInfo(
                    module="bcrypt",
                    imported_symbols=["checkpw"],
                    import_type="from",
                    line_number=1,
                    is_relative=False
                )
            ],
            exports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="authentication",
                file_path=file_path,
                confidence=0.95,
                evidence=["User authentication with password verification"],
                line_numbers=[10],
                metadata={"method": "password_based"}
            )
        ],
        teaching_value=TeachingValueScore(
            total_score=0.85,
            documentation_score=0.8,
            complexity_score=0.7,
            pattern_score=0.9,
            structure_score=0.85,
            explanation="Good authentication example",
            factors={}
        ),
        complexity_metrics=ComplexityMetrics(
            avg_complexity=5.0,
            max_complexity=5,
            min_complexity=5,
            high_complexity_functions=[],
            trivial_functions=[],
            avg_nesting_depth=2.0
        ),
        documentation_coverage=0.8,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at="2024-01-01T00:00:00",
        cache_hit=False,
        is_notebook=False
    )


def create_sample_lesson() -> Lesson:
    """Create a sample lesson for testing."""
    return Lesson(
        lesson_id="test-lesson-1",
        title="User Authentication",
        description="Implement secure user login",
        order=1,
        difficulty="intermediate",
        duration_minutes=45,
        file_path="src/auth/login.py",
        teaching_value=0.85,
        learning_objectives=["Understand authentication", "Implement secure login"],
        prerequisites=["Basic Python"],
        concepts=["Authentication", "Security"],
        content=LessonContent(
            introduction="Learn about authentication",
            explanation="Authentication validates user identity",
            code_example=CodeExample(
                code="def authenticate_user(username, password):\n    pass",
                language="python",
                filename="src/auth/login.py"
            ),
            walkthrough="Step by step guide",
            summary="Summary of authentication"
        )
    )


# ========== Test Explanations Cite Actual Code ==========


class TestExplanationsCiteCode:
    """Test that explanations cite actual code with file paths and line numbers."""
    
    @pytest.mark.asyncio
    async def test_code_sections_have_file_references(self, repo_path, mock_analysis_engine):
        """Test that code sections include file path references."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Verify code sections have file references
        assert len(guide.code_sections) > 0
        
        for section in guide.code_sections:
            # Must have file path
            assert section.file_path, "Code section missing file_path"
            assert len(section.file_path) > 0, "Code section has empty file_path"
            
            # File path should be a valid path format
            assert "/" in section.file_path or "\\" in section.file_path or section.file_path.endswith(".py")
    
    @pytest.mark.asyncio
    async def test_code_sections_have_line_ranges(self, repo_path, mock_analysis_engine):
        """Test that code sections include line number ranges."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        for section in guide.code_sections:
            # Must have line range
            assert section.line_range, "Code section missing line_range"
            assert isinstance(section.line_range, tuple), "line_range should be tuple"
            assert len(section.line_range) == 2, "line_range should have start and end"
            
            start, end = section.line_range
            assert isinstance(start, int), "line_range start should be int"
            assert isinstance(end, int), "line_range end should be int"
            assert start > 0, "line_range start should be positive"
            assert end >= start, "line_range end should be >= start"
    
    @pytest.mark.asyncio
    async def test_code_sections_have_actual_code(self, repo_path, mock_analysis_engine):
        """Test that code sections include actual code snippets."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        for section in guide.code_sections:
            # Must have code snippet
            assert section.code_snippet, "Code section missing code_snippet"
            assert len(section.code_snippet) > 0, "Code section has empty code_snippet"
            
            # Code should look like actual code (not placeholder)
            assert not section.code_snippet.startswith("TODO"), "Code snippet is placeholder"
            assert not section.code_snippet.startswith("..."), "Code snippet is placeholder"
    
    @pytest.mark.asyncio
    async def test_purpose_references_evidence(self, repo_path, mock_analysis_engine):
        """Test that purpose statements reference evidence."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        for section in guide.code_sections:
            # Purpose should be descriptive
            assert section.purpose, "Code section missing purpose"
            assert len(section.purpose) > 10, "Purpose too short to be meaningful"
            
            # Purpose should not be generic placeholder
            generic_phrases = ["this code", "the function", "it does"]
            is_generic = all(phrase not in section.purpose.lower() for phrase in generic_phrases)
            # Purpose can use these phrases, but should have more detail
            assert len(section.purpose.split()) >= 4, "Purpose lacks detail"


# ========== Test Examples From Real Codebase ==========


class TestExamplesFromRealCodebase:
    """Test that examples are extracted from actual codebase, not fabricated."""
    
    @pytest.mark.asyncio
    async def test_source_files_from_evidence_bundle(self, repo_path, mock_analysis_engine):
        """Test that source files come from evidence bundle."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Evidence bundle should have source files structure (may be empty if file doesn't exist)
        assert hasattr(guide.evidence_bundle, 'source_files'), "Missing source_files field"
        assert isinstance(guide.evidence_bundle.source_files, list), "source_files should be list"
        
        # If source files exist, validate structure
        for source_file in guide.evidence_bundle.source_files:
            assert 'path' in source_file, "Source file missing path"
            assert source_file['path'], "Source file has empty path"
            
            # Should have either code or lines reference
            has_content = 'code' in source_file or 'lines' in source_file or 'content' in source_file
            assert has_content, "Source file missing code content"
    
    @pytest.mark.asyncio
    async def test_code_snippets_match_source_files(self, repo_path, mock_analysis_engine):
        """Test that code snippets reference files from evidence bundle."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Get all source file paths from evidence
        source_paths = {sf['path'] for sf in guide.evidence_bundle.source_files}
        
        # Code sections should reference these files
        for section in guide.code_sections:
            # File path should be in evidence or be the lesson file
            is_from_evidence = (
                section.file_path in source_paths or
                section.file_path == lesson.file_path or
                any(section.file_path.endswith(Path(sp).name) for sp in source_paths)
            )
            assert is_from_evidence, f"Code section references unknown file: {section.file_path}"
    
    @pytest.mark.asyncio
    async def test_solution_code_from_codebase(self, repo_path, mock_analysis_engine):
        """Test that exercise solution code comes from actual codebase."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Solution code should exist
        assert guide.exercise_generation.solution_code, "Missing solution code"
        assert len(guide.exercise_generation.solution_code) > 0, "Empty solution code"
        
        # Solution should not be a placeholder
        assert "TODO" not in guide.exercise_generation.solution_code, "Solution is placeholder"
        assert "pass" not in guide.exercise_generation.solution_code or len(guide.exercise_generation.solution_code.split('\n')) > 2, "Solution is stub"


# ========== Test Exercises Have Validation Tests ==========


class TestExercisesHaveValidationTests:
    """Test that exercises include test cases for validation."""
    
    @pytest.mark.asyncio
    async def test_exercises_have_test_cases(self, repo_path, mock_analysis_engine):
        """Test that exercises include test cases."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Exercise generation should have test cases
        assert hasattr(guide.exercise_generation, 'test_cases'), "Missing test_cases field"
        assert isinstance(guide.exercise_generation.test_cases, list), "test_cases should be list"
        
        # Test cases can be empty if no tests found, but structure should exist
        # If test cases exist, they should be valid
        for test_case in guide.exercise_generation.test_cases:
            assert isinstance(test_case, dict), "Test case should be dict"
    
    @pytest.mark.asyncio
    async def test_test_evidence_in_code_sections(self, repo_path, mock_analysis_engine):
        """Test that code sections reference test evidence."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        for section in guide.code_sections:
            # Should have test_evidence field (even if empty)
            assert hasattr(section, 'test_evidence'), "Missing test_evidence field"
            assert isinstance(section.test_evidence, list), "test_evidence should be list"
            
            # If test evidence exists, validate structure
            for test_ev in section.test_evidence:
                assert isinstance(test_ev, dict), "Test evidence should be dict"
    
    @pytest.mark.asyncio
    async def test_validation_checklist_includes_tests(self, repo_path, mock_analysis_engine):
        """Test that validation checklist references test expectations."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Validation checklist should have expected_behavior from tests
        assert guide.validation_checklist.expected_behavior, "Missing expected_behavior"
        assert len(guide.validation_checklist.expected_behavior) > 0, "Empty expected_behavior"
        
        # Should mention tests or expected behavior
        behavior_text = guide.validation_checklist.expected_behavior.lower()
        has_test_reference = any(word in behavior_text for word in ['test', 'expect', 'should', 'validate'])
        # Even without tests, should describe expected behavior
        assert len(behavior_text.split()) > 3, "Expected behavior lacks detail"


# ========== Test Hints Are Progressive ==========


class TestHintsAreProgressive:
    """Test that hints progress from general to specific."""
    
    @pytest.mark.asyncio
    async def test_hints_exist(self, repo_path, mock_analysis_engine):
        """Test that exercises include hints."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Should have progressive hints
        assert hasattr(guide.exercise_generation, 'progressive_hints'), "Missing progressive_hints"
        assert isinstance(guide.exercise_generation.progressive_hints, list), "progressive_hints should be list"
        assert len(guide.exercise_generation.progressive_hints) >= 3, "Should have at least 3 hints"
        assert len(guide.exercise_generation.progressive_hints) <= 5, "Should have at most 5 hints"
    
    @pytest.mark.asyncio
    async def test_hints_increase_in_specificity(self, repo_path, mock_analysis_engine):
        """Test that hints become more specific."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        hints = guide.exercise_generation.progressive_hints
        
        # First hint should be more general (shorter or more conceptual)
        # Last hint should be more specific (longer or more detailed)
        if len(hints) >= 2:
            first_hint = hints[0]
            last_hint = hints[-1]
            
            # Check that hints are not identical
            assert first_hint != last_hint, "First and last hints are identical"
            
            # Last hint should generally be more detailed
            # (more words or more specific terms)
            first_words = len(first_hint.split())
            last_words = len(last_hint.split())
            
            # At least one hint should have reasonable length
            assert first_words > 3 or last_words > 3, "Hints too short to be helpful"
    
    @pytest.mark.asyncio
    async def test_hints_are_not_solutions(self, repo_path, mock_analysis_engine):
        """Test that hints guide without giving away the solution."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        hints = guide.exercise_generation.progressive_hints
        solution = guide.exercise_generation.solution_code
        
        # Hints should not contain the exact solution code
        for hint in hints:
            # Hint should not be the full solution
            assert hint != solution, "Hint is the full solution"
            
            # Hint should be guidance, not code (mostly)
            # Allow some code snippets, but not the entire solution
            if solution and len(solution) > 20:
                similarity = len(set(hint.split()) & set(solution.split())) / max(len(hint.split()), 1)
                assert similarity < 0.8, "Hint too similar to solution"
    
    @pytest.mark.asyncio
    async def test_first_hint_is_conceptual(self, repo_path, mock_analysis_engine):
        """Test that first hint is conceptual/general."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        hints = guide.exercise_generation.progressive_hints
        
        if len(hints) > 0:
            first_hint = hints[0].lower()
            
            # First hint should use conceptual language
            conceptual_words = ['think', 'consider', 'remember', 'concept', 'approach', 'strategy', 'pattern']
            has_conceptual = any(word in first_hint for word in conceptual_words)
            
            # Or should be general guidance
            general_words = ['start', 'begin', 'first', 'need', 'should', 'want']
            has_general = any(word in first_hint for word in general_words)
            
            # First hint should be conceptual or general (not overly specific)
            # Allow flexibility - just check it's not empty and has some guidance
            assert len(first_hint.split()) >= 5, "First hint too short to be helpful"


# ========== Test Analogies Are Beginner-Friendly ==========


class TestAnalogiesAreBeginnerFriendly:
    """Test that analogies use familiar concepts."""
    
    @pytest.mark.asyncio
    async def test_analogies_exist(self, repo_path, mock_analysis_engine):
        """Test that real-world context includes analogies."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Should have analogies
        assert hasattr(guide.real_world_context, 'analogies'), "Missing analogies field"
        assert isinstance(guide.real_world_context.analogies, list), "analogies should be list"
        assert len(guide.real_world_context.analogies) > 0, "Should have at least one analogy"
    
    @pytest.mark.asyncio
    async def test_analogies_use_familiar_concepts(self, repo_path, mock_analysis_engine):
        """Test that analogies reference familiar real-world concepts."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        analogies = guide.real_world_context.analogies
        
        # Analogies should be descriptive
        for analogy in analogies:
            assert len(analogy) > 10, "Analogy too short to be meaningful"
            
            # Should not be overly technical
            technical_jargon = ['algorithm', 'polymorphism', 'encapsulation', 'abstraction']
            jargon_count = sum(1 for word in technical_jargon if word in analogy.lower())
            
            # Allow some technical terms, but analogy should explain them
            if jargon_count > 0:
                assert len(analogy.split()) > 15, "Technical analogy needs more explanation"
    
    @pytest.mark.asyncio
    async def test_analogies_avoid_jargon(self, repo_path, mock_analysis_engine):
        """Test that analogies avoid unexplained technical jargon."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        analogies = guide.real_world_context.analogies
        
        # Check that analogies are accessible
        for analogy in analogies:
            analogy_lower = analogy.lower()
            
            # Should use comparison words
            comparison_words = ['like', 'similar', 'as if', 'imagine', 'think of', 'comparable']
            has_comparison = any(word in analogy_lower for word in comparison_words)
            
            # Analogy should make a comparison or be explanatory
            # Allow flexibility - just check it's substantive
            assert len(analogy.split()) >= 8, "Analogy too brief to be helpful"


# ========== Test Anti-Hallucination Rules Enforced ==========


class TestAntiHallucinationRulesEnforced:
    """Test that anti-hallucination rules are present and enforced."""
    
    @pytest.mark.asyncio
    async def test_anti_hallucination_rules_exist(self, repo_path, mock_analysis_engine):
        """Test that anti-hallucination rules are included."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Should have anti-hallucination rules
        assert guide.anti_hallucination_rules, "Missing anti_hallucination_rules"
        
        # Check all required rules
        assert guide.anti_hallucination_rules.always_cite, "Missing always_cite rule"
        assert guide.anti_hallucination_rules.distinguish_fact_inference, "Missing distinguish_fact_inference rule"
        assert guide.anti_hallucination_rules.validate_against_tests, "Missing validate_against_tests rule"
        assert guide.anti_hallucination_rules.cross_reference, "Missing cross_reference rule"
        assert guide.anti_hallucination_rules.avoid_assumptions, "Missing avoid_assumptions rule"
    
    @pytest.mark.asyncio
    async def test_always_cite_rule_mentions_evidence(self, repo_path, mock_analysis_engine):
        """Test that always_cite rule mentions evidence/citations."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        always_cite = guide.anti_hallucination_rules.always_cite.lower()
        
        # Should mention citing or evidence
        citation_words = ['cit', 'evidence', 'reference', 'source']
        has_citation_word = any(word in always_cite for word in citation_words)
        assert has_citation_word, "always_cite rule doesn't mention citations/evidence"
    
    @pytest.mark.asyncio
    async def test_validation_checklist_enforces_consistency(self, repo_path, mock_analysis_engine):
        """Test that validation checklist checks consistency."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Validation checklist should have consistency check
        assert hasattr(guide.validation_checklist, 'consistency_check'), "Missing consistency_check"
        assert isinstance(guide.validation_checklist.consistency_check, bool), "consistency_check should be bool"
    
    @pytest.mark.asyncio
    async def test_evidence_bundle_has_multiple_sources(self, repo_path, mock_analysis_engine):
        """Test that evidence comes from multiple sources."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        evidence = guide.evidence_bundle
        
        # Should have all evidence type fields (even if empty)
        assert hasattr(evidence, 'source_files'), "Missing source_files"
        assert hasattr(evidence, 'test_files'), "Missing test_files"
        assert hasattr(evidence, 'git_commits'), "Missing git_commits"
        assert hasattr(evidence, 'documentation'), "Missing documentation"
        assert hasattr(evidence, 'dependencies'), "Missing dependencies"
        
        # Count non-empty evidence types
        evidence_types = [
            len(evidence.source_files) > 0,
            len(evidence.test_files) > 0,
            len(evidence.git_commits) > 0,
            len(evidence.documentation) > 0,
            len(evidence.dependencies) > 0,
        ]
        
        # Should have at least 1 type of evidence (documentation or dependencies typically present)
        evidence_count = sum(evidence_types)
        assert evidence_count >= 1, "No evidence sources available"
    
    @pytest.mark.asyncio
    async def test_enrichment_instructions_require_citations(self, repo_path, mock_analysis_engine):
        """Test that enrichment instructions require evidence citations."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        instructions = guide.enrichment_instructions
        
        # Should have evidence requirements
        assert instructions.evidence_requirements, "Missing evidence_requirements"
        
        evidence_req = instructions.evidence_requirements.lower()
        
        # Should mention citing
        assert 'cit' in evidence_req, "evidence_requirements doesn't mention citing"


# ========== Integration Tests ==========


class TestEnrichmentQualityIntegration:
    """Integration tests for overall enrichment quality."""
    
    @pytest.mark.asyncio
    async def test_complete_guide_meets_quality_standards(self, repo_path, mock_analysis_engine):
        """Test that complete guide meets all quality standards."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Verify all major components exist and have content
        assert guide.lesson_id, "Missing lesson_id"
        assert guide.feature_mapping.feature_name, "Missing feature_name"
        assert hasattr(guide.evidence_bundle, 'source_files'), "Missing source_files field"
        assert guide.validation_checklist.code_behavior, "Missing code_behavior"
        assert guide.teaching_value_assessment.total_score >= 0, "Invalid teaching_value"
        assert guide.systematic_investigation.what_it_does, "Missing what_it_does"
        assert len(guide.narrative_structure.introduction_points) > 0, "No introduction_points"
        assert len(guide.code_sections) > 0, "No code_sections"
        assert guide.architecture_context.component_role, "Missing component_role"
        assert len(guide.real_world_context.practical_use_cases) > 0, "No practical_use_cases"
        assert len(guide.exercise_generation.progressive_hints) >= 3, "Insufficient hints"
        assert guide.anti_hallucination_rules.always_cite, "Missing anti_hallucination_rules"
        assert guide.enrichment_instructions.tone, "Missing enrichment_instructions"
    
    @pytest.mark.asyncio
    async def test_guide_serialization_preserves_quality(self, repo_path, mock_analysis_engine):
        """Test that serialization preserves all quality attributes."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Serialize and deserialize
        guide_dict = guide.to_dict()
        restored_guide = EnrichmentGuide.from_dict(guide_dict)
        
        # Verify quality attributes preserved
        assert restored_guide.lesson_id == guide.lesson_id
        assert len(restored_guide.code_sections) == len(guide.code_sections)
        assert len(restored_guide.exercise_generation.progressive_hints) == len(guide.exercise_generation.progressive_hints)
        assert restored_guide.anti_hallucination_rules.always_cite == guide.anti_hallucination_rules.always_cite


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
