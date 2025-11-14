"""
Tests for Enrichment Guide Generator.

Tests the main orchestrator that generates comprehensive, evidence-based
enrichment guides for AI content enrichment.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from src.course.enrichment_guide_generator import (
    EnrichmentGuideGenerator,
    create_enrichment_guide_generator
)
from src.course.enrichment_models import (
    EnrichmentGuide,
    FeatureMapping,
    EvidenceBundle,
    ValidationChecklist,
    TeachingValueAssessment,
    SystematicInvestigation,
    NarrativeStructure,
    CodeSectionGuide,
    ArchitectureContext,
    RealWorldContext,
    ExerciseGeneration,
    AntiHallucinationRules,
    EnrichmentInstructions
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


@pytest.fixture
def repo_path():
    """Get repository path for testing."""
    return str(Path(__file__).parent.parent)


@pytest.fixture
def mock_analysis_engine():
    """Create a mock analysis engine."""
    engine = Mock(spec=AnalysisEngine)
    
    # Create async mock for analyze_file
    async def mock_analyze_file(file_path, use_cache=True):
        return create_sample_file_analysis(file_path)
    
    engine.analyze_file = AsyncMock(side_effect=mock_analyze_file)
    return engine


@pytest.fixture
def mock_git_analyzer():
    """Create a mock git analyzer."""
    analyzer = Mock()
    analyzer.get_relevant_commits = Mock(return_value=[
        {
            'hash': 'abc123def456',
            'author': 'Test Developer',
            'date': '2024-01-15T10:30:00Z',
            'subject': 'Add authentication feature',
            'message': 'Add authentication feature\n\nImplements secure login with JWT tokens.',
            'files': ['src/auth/login.py']
        }
    ])
    return analyzer


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


class TestEnrichmentGuideGenerator:
    """Test suite for EnrichmentGuideGenerator class."""
    
    def test_initialization(self, repo_path, mock_analysis_engine):
        """Test generator initialization."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        assert generator is not None
        assert generator.repo_path == Path(repo_path).resolve()
        assert generator.analysis_engine == mock_analysis_engine
        assert generator.feature_mapper is not None
        assert generator.evidence_collector is not None
        assert generator.validation_engine is not None
    
    def test_initialization_with_git_analyzer(self, repo_path, mock_analysis_engine, mock_git_analyzer):
        """Test generator initialization with git analyzer."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine,
            git_analyzer=mock_git_analyzer
        )
        
        assert generator.git_analyzer == mock_git_analyzer
    
    def test_factory_function(self, repo_path, mock_analysis_engine):
        """Test factory function creates valid instance."""
        generator = create_enrichment_guide_generator(
            repo_path,
            mock_analysis_engine
        )
        
        assert isinstance(generator, EnrichmentGuideGenerator)
    
    @pytest.mark.asyncio
    async def test_generate_guide_complete(self, repo_path, mock_analysis_engine, mock_git_analyzer):
        """Test generating a complete enrichment guide."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine,
            git_analyzer=mock_git_analyzer
        )
        
        lesson = create_sample_lesson()
        
        guide = await generator.generate_guide(
            codebase_id="test-codebase",
            lesson=lesson
        )
        
        # Verify guide structure
        assert isinstance(guide, EnrichmentGuide)
        assert guide.lesson_id == lesson.lesson_id
        
        # Verify all components are present
        assert isinstance(guide.feature_mapping, FeatureMapping)
        assert isinstance(guide.evidence_bundle, EvidenceBundle)
        assert isinstance(guide.validation_checklist, ValidationChecklist)
        assert isinstance(guide.teaching_value_assessment, TeachingValueAssessment)
        assert isinstance(guide.systematic_investigation, SystematicInvestigation)
        assert isinstance(guide.narrative_structure, NarrativeStructure)
        assert isinstance(guide.code_sections, list)
        assert isinstance(guide.architecture_context, ArchitectureContext)
        assert isinstance(guide.real_world_context, RealWorldContext)
        assert isinstance(guide.exercise_generation, ExerciseGeneration)
        assert isinstance(guide.anti_hallucination_rules, AntiHallucinationRules)
        assert isinstance(guide.enrichment_instructions, EnrichmentInstructions)
    
    @pytest.mark.asyncio
    async def test_generate_guide_with_file_analysis(self, repo_path, mock_analysis_engine):
        """Test generating guide with pre-computed file analysis."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        file_analysis = create_sample_file_analysis(lesson.file_path)
        
        guide = await generator.generate_guide(
            codebase_id="test-codebase",
            lesson=lesson,
            file_analysis=file_analysis
        )
        
        assert isinstance(guide, EnrichmentGuide)
        # Should not call analyze_file since we provided it
        mock_analysis_engine.analyze_file.assert_not_called()


class TestFeatureMapping:
    """Test feature mapping phase."""
    
    @pytest.mark.asyncio
    async def test_feature_mapping_generated(self, repo_path, mock_analysis_engine):
        """Test that feature mapping is generated."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        feature_mapping = guide.feature_mapping
        assert feature_mapping.feature_name == lesson.title
        assert len(feature_mapping.user_facing_purpose) > 0
        assert len(feature_mapping.business_value) > 0
        assert len(feature_mapping.entry_points) > 0
        assert len(feature_mapping.feature_flow) > 0


class TestEvidenceCollection:
    """Test evidence collection phase."""
    
    @pytest.mark.asyncio
    async def test_evidence_bundle_collected(self, repo_path, mock_analysis_engine, mock_git_analyzer):
        """Test that evidence bundle is collected."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine,
            git_analyzer=mock_git_analyzer
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        evidence = guide.evidence_bundle
        assert isinstance(evidence.source_files, list)
        assert isinstance(evidence.test_files, list)
        assert isinstance(evidence.git_commits, list)
        assert isinstance(evidence.documentation, list)
        assert isinstance(evidence.dependencies, list)
        assert isinstance(evidence.dependents, list)
    
    @pytest.mark.asyncio
    async def test_git_commits_collected(self, repo_path, mock_analysis_engine, mock_git_analyzer):
        """Test that git commits are collected."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine,
            git_analyzer=mock_git_analyzer
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        assert len(guide.evidence_bundle.git_commits) > 0
        mock_git_analyzer.get_relevant_commits.assert_called_once()


class TestValidation:
    """Test validation phase."""
    
    @pytest.mark.asyncio
    async def test_validation_checklist_created(self, repo_path, mock_analysis_engine):
        """Test that validation checklist is created."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        validation = guide.validation_checklist
        assert len(validation.code_behavior) > 0
        assert len(validation.expected_behavior) > 0
        assert len(validation.documentation_alignment) > 0
        assert len(validation.git_context) > 0
        assert isinstance(validation.consistency_check, bool)


class TestTeachingValueAssessment:
    """Test teaching value assessment phase."""
    
    @pytest.mark.asyncio
    async def test_teaching_value_assessed(self, repo_path, mock_analysis_engine):
        """Test that teaching value is assessed."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        teaching_value = guide.teaching_value_assessment
        assert 'reusability' in teaching_value.scores
        assert 'best_practice' in teaching_value.scores
        assert 'fundamentality' in teaching_value.scores
        assert 'uniqueness' in teaching_value.scores
        assert 'junior_dev' in teaching_value.scores
        assert 0 <= teaching_value.total_score <= 14
        assert isinstance(teaching_value.should_teach, bool)
        assert len(teaching_value.reasoning) > 0


class TestSystematicInvestigation:
    """Test systematic investigation phase."""
    
    @pytest.mark.asyncio
    async def test_investigation_conducted(self, repo_path, mock_analysis_engine):
        """Test that systematic investigation is conducted."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        investigation = guide.systematic_investigation
        assert len(investigation.what_it_does) > 0
        assert len(investigation.why_it_exists) > 0
        assert len(investigation.how_it_works) > 0
        assert isinstance(investigation.when_its_used, list)
        assert isinstance(investigation.edge_cases, list)
        assert isinstance(investigation.common_pitfalls, list)


class TestNarrativeStructure:
    """Test narrative structure phase."""
    
    @pytest.mark.asyncio
    async def test_narrative_built(self, repo_path, mock_analysis_engine):
        """Test that narrative structure is built."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        narrative = guide.narrative_structure
        assert isinstance(narrative.introduction_points, list)
        assert isinstance(narrative.learning_progression, list)
        assert isinstance(narrative.code_walkthrough_order, list)
        assert isinstance(narrative.conclusion_points, list)
        assert isinstance(narrative.next_steps, list)
        assert len(narrative.introduction_points) >= 3
        assert len(narrative.conclusion_points) >= 3


class TestCodeSectionGuides:
    """Test code section guide generation."""
    
    @pytest.mark.asyncio
    async def test_code_sections_generated(self, repo_path, mock_analysis_engine):
        """Test that code section guides are generated."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        assert isinstance(guide.code_sections, list)
        assert len(guide.code_sections) > 0
        
        # Check first code section structure
        section = guide.code_sections[0]
        assert isinstance(section, CodeSectionGuide)
        assert len(section.file_path) > 0
        assert isinstance(section.line_range, tuple)
        assert len(section.code_snippet) > 0
        assert len(section.purpose) > 0
        assert isinstance(section.key_concepts, list)


class TestArchitectureContext:
    """Test architecture context extraction."""
    
    @pytest.mark.asyncio
    async def test_architecture_extracted(self, repo_path, mock_analysis_engine):
        """Test that architecture context is extracted."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        architecture = guide.architecture_context
        assert len(architecture.component_role) > 0
        assert len(architecture.data_flow) > 0
        assert isinstance(architecture.dependencies, list)
        assert isinstance(architecture.dependents, list)
        assert isinstance(architecture.design_patterns, list)


class TestRealWorldContext:
    """Test real-world context suggestion."""
    
    @pytest.mark.asyncio
    async def test_real_world_context_generated(self, repo_path, mock_analysis_engine):
        """Test that real-world context is generated."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        real_world = guide.real_world_context
        assert isinstance(real_world.practical_use_cases, list)
        assert isinstance(real_world.analogies, list)
        assert isinstance(real_world.industry_patterns, list)
        assert isinstance(real_world.best_practices, list)
        assert isinstance(real_world.anti_patterns, list)


class TestExerciseGeneration:
    """Test exercise generation."""
    
    @pytest.mark.asyncio
    async def test_exercises_generated(self, repo_path, mock_analysis_engine):
        """Test that exercises are generated."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        exercises = guide.exercise_generation
        assert isinstance(exercises.hands_on_tasks, list)
        assert isinstance(exercises.starter_code, str)
        assert isinstance(exercises.solution_code, str)
        assert isinstance(exercises.test_cases, list)
        assert isinstance(exercises.progressive_hints, list)
        assert isinstance(exercises.self_assessment, list)


class TestAntiHallucinationRules:
    """Test anti-hallucination rules."""
    
    @pytest.mark.asyncio
    async def test_anti_hallucination_rules_included(self, repo_path, mock_analysis_engine):
        """Test that anti-hallucination rules are included."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        rules = guide.anti_hallucination_rules
        assert len(rules.always_cite) > 0
        assert len(rules.distinguish_fact_inference) > 0
        assert len(rules.validate_against_tests) > 0
        assert len(rules.cross_reference) > 0
        assert len(rules.avoid_assumptions) > 0
        assert "cit" in rules.always_cite.lower()  # "citing" contains "cit"
        assert "evidence" in rules.always_cite.lower()


class TestEnrichmentInstructions:
    """Test enrichment instructions."""
    
    @pytest.mark.asyncio
    async def test_enrichment_instructions_included(self, repo_path, mock_analysis_engine):
        """Test that enrichment instructions are included."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        instructions = guide.enrichment_instructions
        assert instructions.tone == "casual"
        assert instructions.depth == "detailed"
        assert isinstance(instructions.focus_areas, list)
        assert isinstance(instructions.avoid_topics, list)
        assert len(instructions.evidence_requirements) > 0
        assert "cite" in instructions.evidence_requirements.lower()
    
    @pytest.mark.asyncio
    async def test_focus_areas_based_on_teaching_value(self, repo_path, mock_analysis_engine):
        """Test that focus areas are tailored to teaching value."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Should have focus areas (at least 2, or 3 if default)
        assert len(guide.enrichment_instructions.focus_areas) >= 2


class TestErrorHandling:
    """Test error handling."""
    
    @pytest.mark.asyncio
    async def test_handles_missing_git_analyzer(self, repo_path, mock_analysis_engine):
        """Test that generator handles missing git analyzer gracefully."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine,
            git_analyzer=None
        )
        
        lesson = create_sample_lesson()
        
        # Should not raise error even without git analyzer
        guide = await generator.generate_guide("test-codebase", lesson)
        assert isinstance(guide, EnrichmentGuide)
        # Git commits should be empty
        assert len(guide.evidence_bundle.git_commits) == 0
    
    @pytest.mark.asyncio
    async def test_handles_analysis_error(self, repo_path):
        """Test that generator handles analysis errors."""
        # Create mock that raises error
        mock_engine = Mock(spec=AnalysisEngine)
        mock_engine.analyze_file = AsyncMock(side_effect=Exception("Analysis failed"))
        
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_engine
        )
        
        lesson = create_sample_lesson()
        
        # Should raise the error
        with pytest.raises(Exception, match="Analysis failed"):
            await generator.generate_guide("test-codebase", lesson)


class TestSerialization:
    """Test guide serialization."""
    
    @pytest.mark.asyncio
    async def test_guide_serialization(self, repo_path, mock_analysis_engine):
        """Test that enrichment guide can be serialized."""
        generator = EnrichmentGuideGenerator(
            repo_path=repo_path,
            analysis_engine=mock_analysis_engine
        )
        
        lesson = create_sample_lesson()
        guide = await generator.generate_guide("test-codebase", lesson)
        
        # Test to_dict
        guide_dict = guide.to_dict()
        assert isinstance(guide_dict, dict)
        assert 'lesson_id' in guide_dict
        assert 'feature_mapping' in guide_dict
        assert 'evidence_bundle' in guide_dict
        assert 'validation_checklist' in guide_dict
        assert 'teaching_value_assessment' in guide_dict
        
        # Test from_dict
        restored_guide = EnrichmentGuide.from_dict(guide_dict)
        assert restored_guide.lesson_id == guide.lesson_id
        assert restored_guide.feature_mapping.feature_name == guide.feature_mapping.feature_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
