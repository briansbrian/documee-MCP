"""
Tests for enrichment data models.
"""

import pytest
from datetime import datetime
from src.course.enrichment_models import (
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
    EnrichmentInstructions,
    EnrichmentGuide,
    EnrichmentStatus
)


class TestFeatureMapping:
    """Test FeatureMapping model."""
    
    def test_create_feature_mapping(self):
        """Test creating a FeatureMapping instance."""
        mapping = FeatureMapping(
            feature_name="User Authentication",
            user_facing_purpose="Allow users to log in securely",
            business_value="Protect user data and enable personalization",
            entry_points=["POST /api/login", "LoginForm component"],
            feature_flow=["User enters credentials", "Validate password", "Create session"]
        )
        
        assert mapping.feature_name == "User Authentication"
        assert len(mapping.entry_points) == 2
        assert len(mapping.feature_flow) == 3
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        mapping = FeatureMapping(
            feature_name="Test Feature",
            user_facing_purpose="Test purpose",
            business_value="Test value",
            entry_points=["entry1"],
            feature_flow=["step1", "step2"]
        )
        
        data = mapping.to_dict()
        assert isinstance(data, dict)
        assert data['feature_name'] == "Test Feature"
        
        restored = FeatureMapping.from_dict(data)
        assert restored.feature_name == mapping.feature_name
        assert restored.entry_points == mapping.entry_points


class TestEvidenceBundle:
    """Test EvidenceBundle model."""
    
    def test_create_evidence_bundle(self):
        """Test creating an EvidenceBundle instance."""
        bundle = EvidenceBundle(
            source_files=[{"path": "test.py", "lines": [1, 10], "code": "def test(): pass"}],
            test_files=[{"path": "test_test.py", "tests": ["test_function"]}],
            git_commits=[{"hash": "abc123", "message": "Add feature"}],
            documentation=[{"type": "docstring", "content": "Test function"}],
            dependencies=[{"name": "requests", "reason": "HTTP calls"}],
            dependents=[{"name": "api.py", "usage": "calls test()"}]
        )
        
        assert len(bundle.source_files) == 1
        assert len(bundle.git_commits) == 1
        assert bundle.source_files[0]['path'] == "test.py"
    
    def test_serialization(self):
        """Test to_dict and from_dict."""
        bundle = EvidenceBundle(
            source_files=[],
            test_files=[],
            git_commits=[],
            documentation=[],
            dependencies=[],
            dependents=[]
        )
        
        data = bundle.to_dict()
        restored = EvidenceBundle.from_dict(data)
        assert restored.source_files == bundle.source_files


class TestTeachingValueAssessment:
    """Test TeachingValueAssessment model."""
    
    def test_create_assessment(self):
        """Test creating a TeachingValueAssessment."""
        assessment = TeachingValueAssessment(
            scores={
                "reusability": 3,
                "best_practice": 2,
                "fundamentality": 3,
                "uniqueness": 1,
                "junior_dev": 2
            },
            total_score=11,
            should_teach=True,
            reasoning="High reusability and fundamental concept"
        )
        
        assert assessment.total_score == 11
        assert assessment.should_teach is True
        assert assessment.scores['reusability'] == 3
    
    def test_should_teach_threshold(self):
        """Test should_teach logic."""
        # Score > 7 should teach
        high_score = TeachingValueAssessment(
            scores={"reusability": 3, "best_practice": 3, "fundamentality": 2, "uniqueness": 1, "junior_dev": 2},
            total_score=11,
            should_teach=True,
            reasoning="High value"
        )
        assert high_score.should_teach is True
        
        # Score <= 7 should not teach
        low_score = TeachingValueAssessment(
            scores={"reusability": 1, "best_practice": 1, "fundamentality": 1, "uniqueness": 0, "junior_dev": 1},
            total_score=4,
            should_teach=False,
            reasoning="Low value"
        )
        assert low_score.should_teach is False


class TestCodeSectionGuide:
    """Test CodeSectionGuide model."""
    
    def test_create_code_section_guide(self):
        """Test creating a CodeSectionGuide."""
        guide = CodeSectionGuide(
            file_path="src/auth.py",
            line_range=(10, 25),
            code_snippet="def login(user, password): ...",
            purpose="Authenticate user credentials",
            key_concepts=["authentication", "password hashing"],
            explanation_approach=["Explain password hashing first", "Then session creation"],
            related_code=[{"path": "src/session.py", "context": "Creates session"}],
            test_evidence=[{"test_name": "test_login", "description": "Tests valid login"}],
            git_evidence=[{"commit": "abc123", "message": "Add login"}],
            common_mistakes=["Don't store plain passwords"]
        )
        
        assert guide.file_path == "src/auth.py"
        assert guide.line_range == (10, 25)
        assert len(guide.key_concepts) == 2
    
    def test_line_range_serialization(self):
        """Test that line_range tuple is properly serialized."""
        guide = CodeSectionGuide(
            file_path="test.py",
            line_range=(1, 10),
            code_snippet="code",
            purpose="test",
            key_concepts=[],
            explanation_approach=[],
            related_code=[],
            test_evidence=[],
            git_evidence=[],
            common_mistakes=[]
        )
        
        data = guide.to_dict()
        assert isinstance(data['line_range'], list)
        assert data['line_range'] == [1, 10]
        
        restored = CodeSectionGuide.from_dict(data)
        assert isinstance(restored.line_range, tuple)
        assert restored.line_range == (1, 10)


class TestEnrichmentGuide:
    """Test complete EnrichmentGuide model."""
    
    def test_create_enrichment_guide(self):
        """Test creating a complete EnrichmentGuide."""
        guide = EnrichmentGuide(
            lesson_id="module-1-lesson-1",
            feature_mapping=FeatureMapping(
                feature_name="Test",
                user_facing_purpose="Test",
                business_value="Test",
                entry_points=[],
                feature_flow=[]
            ),
            evidence_bundle=EvidenceBundle(
                source_files=[],
                test_files=[],
                git_commits=[],
                documentation=[],
                dependencies=[],
                dependents=[]
            ),
            validation_checklist=ValidationChecklist(
                code_behavior="Does X",
                expected_behavior="Should do X",
                documentation_alignment="Docs say X",
                git_context="Added for X",
                consistency_check=True
            ),
            teaching_value_assessment=TeachingValueAssessment(
                scores={"reusability": 2},
                total_score=2,
                should_teach=False,
                reasoning="Low value"
            ),
            systematic_investigation=SystematicInvestigation(
                what_it_does="Does X",
                why_it_exists="For Y",
                how_it_works="Using Z",
                when_its_used=[],
                edge_cases=[],
                common_pitfalls=[]
            ),
            narrative_structure=NarrativeStructure(
                introduction_points=[],
                learning_progression=[],
                code_walkthrough_order=[],
                conclusion_points=[],
                next_steps=[]
            ),
            code_sections=[],
            architecture_context=ArchitectureContext(
                component_role="Test",
                data_flow="A -> B",
                interaction_diagram="",
                dependencies=[],
                dependents=[],
                design_patterns=[]
            ),
            real_world_context=RealWorldContext(
                practical_use_cases=[],
                analogies=[],
                industry_patterns=[],
                best_practices=[],
                anti_patterns=[]
            ),
            exercise_generation=ExerciseGeneration(
                hands_on_tasks=[],
                starter_code="",
                solution_code="",
                test_cases=[],
                progressive_hints=[],
                self_assessment=[]
            ),
            anti_hallucination_rules=AntiHallucinationRules(),
            enrichment_instructions=EnrichmentInstructions()
        )
        
        assert guide.lesson_id == "module-1-lesson-1"
        assert guide.validation_checklist.consistency_check is True
    
    def test_full_serialization(self):
        """Test complete serialization and deserialization."""
        guide = EnrichmentGuide(
            lesson_id="test-lesson",
            feature_mapping=FeatureMapping("F", "P", "V", [], []),
            evidence_bundle=EvidenceBundle([], [], [], [], [], []),
            validation_checklist=ValidationChecklist("A", "B", "C", "D", True),
            teaching_value_assessment=TeachingValueAssessment({}, 0, False, ""),
            systematic_investigation=SystematicInvestigation("A", "B", "C", [], [], []),
            narrative_structure=NarrativeStructure([], [], [], [], []),
            code_sections=[],
            architecture_context=ArchitectureContext("R", "F", "D", [], [], []),
            real_world_context=RealWorldContext([], [], [], [], []),
            exercise_generation=ExerciseGeneration([], "", "", [], [], []),
            anti_hallucination_rules=AntiHallucinationRules(),
            enrichment_instructions=EnrichmentInstructions()
        )
        
        data = guide.to_dict()
        assert isinstance(data, dict)
        assert 'lesson_id' in data
        assert 'feature_mapping' in data
        
        restored = EnrichmentGuide.from_dict(data)
        assert restored.lesson_id == guide.lesson_id


class TestEnrichmentStatus:
    """Test EnrichmentStatus model."""
    
    def test_create_status(self):
        """Test creating an EnrichmentStatus."""
        status = EnrichmentStatus(
            lesson_id="lesson-1",
            status="completed",
            enriched_at=datetime.now(),
            enriched_by="kiro",
            version=1
        )
        
        assert status.lesson_id == "lesson-1"
        assert status.status == "completed"
        assert status.version == 1
    
    def test_datetime_serialization(self):
        """Test datetime serialization."""
        now = datetime.now()
        status = EnrichmentStatus(
            lesson_id="test",
            status="pending",
            enriched_at=now
        )
        
        data = status.to_dict()
        assert isinstance(data['enriched_at'], str)
        
        restored = EnrichmentStatus.from_dict(data)
        assert isinstance(restored.enriched_at, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
