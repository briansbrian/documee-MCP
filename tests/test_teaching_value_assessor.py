"""
Tests for teaching value assessor.
"""

import pytest
from src.course.teaching_value_assessor import TeachingValueAssessor
from src.course.enrichment_models import (
    FeatureMapping,
    EvidenceBundle,
    TeachingValueAssessment
)
from src.models.analysis_models import (
    DetectedPattern,
    FileAnalysis,
    SymbolInfo,
    ComplexityMetrics,
    TeachingValueScore,
    FunctionInfo
)


@pytest.fixture
def assessor():
    """Create a TeachingValueAssessor instance."""
    return TeachingValueAssessor()


@pytest.fixture
def sample_feature():
    """Create a sample feature mapping."""
    return FeatureMapping(
        feature_name="User Authentication",
        user_facing_purpose="Allow users to log in securely",
        business_value="Protect user data and enable personalization",
        entry_points=["POST /api/login", "LoginForm component"],
        feature_flow=["User enters credentials", "Validate password", "Create session"]
    )


@pytest.fixture
def sample_evidence():
    """Create a sample evidence bundle."""
    return EvidenceBundle(
        source_files=[
            {
                "path": "src/auth.py",
                "lines": [1, 50],
                "code": "def login(user, password):\n    try:\n        validate(user)\n        return True\n    except Exception as e:\n        logger.error(e)\n        raise"
            }
        ],
        test_files=[
            {
                "path": "tests/test_auth.py",
                "tests": ["test_login_success", "test_login_failure"],
                "descriptions": ["Test successful login", "Test failed login"]
            }
        ],
        git_commits=[
            {
                "hash": "abc123",
                "message": "Add user authentication",
                "date": "2024-01-01",
                "author": "dev"
            }
        ],
        documentation=[
            {
                "type": "docstring",
                "content": "Authenticate user credentials",
                "location": "src/auth.py:1"
            }
        ],
        dependencies=[{"name": "bcrypt", "reason": "Password hashing"}],
        dependents=[{"name": "api.py", "usage": "Calls login()"}]
    )


@pytest.fixture
def sample_file_analysis():
    """Create a sample file analysis."""
    return FileAnalysis(
        file_path="src/auth.py",
        language="python",
        symbol_info=SymbolInfo(
            functions=[
                FunctionInfo(
                    name="login",
                    start_line=1,
                    end_line=10,
                    parameters=["user", "password"],
                    return_type="bool",
                    docstring="Authenticate user",
                    decorators=[],
                    is_async=False,
                    complexity=5
                )
            ],
            classes=[],
            imports=[],
            exports=[]
        ),
        patterns=[
            DetectedPattern(
                pattern_type="authentication",
                file_path="src/auth.py",
                confidence=0.9,
                evidence=["login function", "password validation"],
                line_numbers=[1, 5],
                metadata={}
            ),
            DetectedPattern(
                pattern_type="error_handling",
                file_path="src/auth.py",
                confidence=0.85,
                evidence=["try-except block"],
                line_numbers=[2, 7],
                metadata={}
            )
        ],
        teaching_value=TeachingValueScore(
            total_score=0.8,
            documentation_score=0.7,
            complexity_score=0.6,
            pattern_score=0.9,
            structure_score=0.8,
            explanation="High teaching value",
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
        documentation_coverage=0.7,
        linter_issues=[],
        has_errors=False,
        errors=[],
        analyzed_at="2024-01-01T00:00:00",
        cache_hit=False,
        is_notebook=False
    )


class TestScoreReusability:
    """Test reusability scoring."""
    
    def test_high_reusability_multiple_patterns(self, assessor):
        """Test scoring with multiple reusable patterns."""
        patterns = [
            DetectedPattern("authentication", "test.py", 0.9, [], [1], {}),
            DetectedPattern("api_route", "test.py", 0.8, [], [2], {}),
            DetectedPattern("validation", "test.py", 0.85, [], [3], {})
        ]
        
        score = assessor.score_reusability(patterns)
        assert score == 3
    
    def test_moderate_reusability_two_patterns(self, assessor):
        """Test scoring with two reusable patterns."""
        patterns = [
            DetectedPattern("caching", "test.py", 0.9, [], [1], {}),
            DetectedPattern("middleware", "test.py", 0.8, [], [2], {})
        ]
        
        score = assessor.score_reusability(patterns)
        assert score == 2
    
    def test_low_reusability_one_pattern(self, assessor):
        """Test scoring with one reusable pattern."""
        patterns = [
            DetectedPattern("decorator", "test.py", 0.9, [], [1], {})
        ]
        
        score = assessor.score_reusability(patterns)
        assert score == 1
    
    def test_no_reusability(self, assessor):
        """Test scoring with no reusable patterns."""
        patterns = [
            DetectedPattern("custom_logic", "test.py", 0.9, [], [1], {})
        ]
        
        score = assessor.score_reusability(patterns)
        assert score == 0
    
    def test_empty_patterns(self, assessor):
        """Test scoring with no patterns."""
        score = assessor.score_reusability([])
        assert score == 0


class TestScoreBestPractice:
    """Test best practice scoring."""
    
    def test_strong_best_practices(self, assessor, sample_evidence):
        """Test scoring with tests, docs, and patterns."""
        score = assessor.score_best_practice(sample_evidence)
        assert score == 3
    
    def test_moderate_best_practices(self, assessor):
        """Test scoring with only tests and docs."""
        evidence = EvidenceBundle(
            source_files=[{"path": "test.py", "code": "def test(): pass"}],
            test_files=[{"path": "test_test.py", "tests": ["test_func"]}],
            git_commits=[],
            documentation=[{"type": "docstring", "content": "Test"}],
            dependencies=[],
            dependents=[]
        )
        
        score = assessor.score_best_practice(evidence)
        assert score == 2
    
    def test_some_best_practices(self, assessor):
        """Test scoring with only error handling."""
        evidence = EvidenceBundle(
            source_files=[{"path": "test.py", "code": "try:\n    pass\nexcept:\n    pass"}],
            test_files=[],
            git_commits=[],
            documentation=[],
            dependencies=[],
            dependents=[]
        )
        
        score = assessor.score_best_practice(evidence)
        assert score == 1
    
    def test_no_best_practices(self, assessor):
        """Test scoring with no evidence."""
        evidence = EvidenceBundle(
            source_files=[{"path": "test.py", "code": "x = 1"}],
            test_files=[],
            git_commits=[],
            documentation=[],
            dependencies=[],
            dependents=[]
        )
        
        score = assessor.score_best_practice(evidence)
        assert score == 0


class TestScoreFundamentality:
    """Test fundamentality scoring."""
    
    def test_fundamental_concept_crud(self, assessor):
        """Test scoring for CRUD operations."""
        feature = FeatureMapping(
            feature_name="Create User",
            user_facing_purpose="Allow creating new users",
            business_value="User management",
            entry_points=[],
            feature_flow=[]
        )
        
        score = assessor.score_fundamentality(feature)
        assert score == 3
    
    def test_fundamental_concept_auth(self, assessor, sample_feature):
        """Test scoring for authentication."""
        score = assessor.score_fundamentality(sample_feature)
        assert score == 3
    
    def test_important_concept(self, assessor):
        """Test scoring for important but not fundamental."""
        feature = FeatureMapping(
            feature_name="Search Users",
            user_facing_purpose="Find users by name",
            business_value="Improved UX",
            entry_points=[],
            feature_flow=[]
        )
        
        score = assessor.score_fundamentality(feature)
        assert score == 2
    
    def test_useful_concept(self, assessor):
        """Test scoring for useful concept."""
        feature = FeatureMapping(
            feature_name="Analytics Dashboard",
            user_facing_purpose="View usage statistics",
            business_value="Business insights",
            entry_points=[],
            feature_flow=[]
        )
        
        score = assessor.score_fundamentality(feature)
        assert score == 1
    
    def test_niche_concept(self, assessor):
        """Test scoring for niche concept."""
        feature = FeatureMapping(
            feature_name="Custom Widget",
            user_facing_purpose="Special visualization",
            business_value="Unique feature",
            entry_points=[],
            feature_flow=[]
        )
        
        score = assessor.score_fundamentality(feature)
        assert score == 0


class TestScoreUniqueness:
    """Test uniqueness scoring."""
    
    def test_high_uniqueness(self, assessor):
        """Test scoring for highly unique code."""
        analysis = FileAnalysis(
            file_path="test.py",
            language="python",
            symbol_info=SymbolInfo([], [], [], []),
            patterns=[
                DetectedPattern("pattern1", "test.py", 0.9, [], [1], {}),
                DetectedPattern("pattern2", "test.py", 0.85, [], [2], {}),
                DetectedPattern("pattern3", "test.py", 0.95, [], [3], {})
            ],
            teaching_value=TeachingValueScore(0.8, 0.7, 0.6, 0.9, 0.8, "", {}),
            complexity_metrics=ComplexityMetrics(8.0, 15, 3, [], [], 3.0),
            documentation_coverage=0.7,
            linter_issues=[],
            has_errors=False,
            errors=[],
            analyzed_at="2024-01-01",
            cache_hit=False
        )
        
        score = assessor.score_uniqueness(analysis)
        assert score == 2
    
    def test_moderate_uniqueness(self, assessor, sample_file_analysis):
        """Test scoring for moderately unique code."""
        score = assessor.score_uniqueness(sample_file_analysis)
        assert score >= 1
    
    def test_low_uniqueness(self, assessor):
        """Test scoring for standard code."""
        analysis = FileAnalysis(
            file_path="test.py",
            language="python",
            symbol_info=SymbolInfo([], [], [], []),
            patterns=[],
            teaching_value=TeachingValueScore(0.5, 0.5, 0.5, 0.5, 0.5, "", {}),
            complexity_metrics=ComplexityMetrics(2.0, 3, 1, [], [], 1.0),
            documentation_coverage=0.5,
            linter_issues=[],
            has_errors=False,
            errors=[],
            analyzed_at="2024-01-01",
            cache_hit=False
        )
        
        score = assessor.score_uniqueness(analysis)
        assert score == 0


class TestScoreJuniorDevValue:
    """Test junior developer value scoring."""
    
    def test_high_junior_dev_value(self, assessor, sample_feature, sample_file_analysis):
        """Test scoring for high junior dev value."""
        score = assessor.score_junior_dev_value(sample_feature, sample_file_analysis)
        assert score >= 2
    
    def test_moderate_complexity_ideal(self, assessor):
        """Test that moderate complexity scores well."""
        feature = FeatureMapping(
            feature_name="User Management",
            user_facing_purpose="Manage user data",
            business_value="Core functionality",
            entry_points=[],
            feature_flow=[]
        )
        
        analysis = FileAnalysis(
            file_path="test.py",
            language="python",
            symbol_info=SymbolInfo([], [], [], []),
            patterns=[],
            teaching_value=TeachingValueScore(0.8, 0.7, 0.6, 0.9, 0.8, "", {}),
            complexity_metrics=ComplexityMetrics(5.0, 8, 2, [], [], 2.0),
            documentation_coverage=0.8,
            linter_issues=[],
            has_errors=False,
            errors=[],
            analyzed_at="2024-01-01",
            cache_hit=False
        )
        
        score = assessor.score_junior_dev_value(feature, analysis)
        assert score == 3
    
    def test_too_simple_lower_value(self, assessor):
        """Test that too simple code scores lower."""
        feature = FeatureMapping(
            feature_name="Simple Function",
            user_facing_purpose="Does one thing",
            business_value="Utility",
            entry_points=[],
            feature_flow=[]
        )
        
        analysis = FileAnalysis(
            file_path="test.py",
            language="python",
            symbol_info=SymbolInfo([], [], [], []),
            patterns=[],
            teaching_value=TeachingValueScore(0.3, 0.3, 0.3, 0.3, 0.3, "", {}),
            complexity_metrics=ComplexityMetrics(0.5, 1, 0, [], [], 0.5),
            documentation_coverage=0.2,
            linter_issues=[],
            has_errors=False,
            errors=[],
            analyzed_at="2024-01-01",
            cache_hit=False
        )
        
        score = assessor.score_junior_dev_value(feature, analysis)
        assert score <= 1
    
    def test_too_complex_lower_value(self, assessor):
        """Test that too complex code scores lower."""
        feature = FeatureMapping(
            feature_name="Complex Algorithm",
            user_facing_purpose="Advanced processing",
            business_value="Performance",
            entry_points=[],
            feature_flow=[]
        )
        
        analysis = FileAnalysis(
            file_path="test.py",
            language="python",
            symbol_info=SymbolInfo([], [], [], []),
            patterns=[],
            teaching_value=TeachingValueScore(0.8, 0.7, 0.6, 0.9, 0.8, "", {}),
            complexity_metrics=ComplexityMetrics(20.0, 35, 10, [], [], 8.0),
            documentation_coverage=0.3,
            linter_issues=[],
            has_errors=False,
            errors=[],
            analyzed_at="2024-01-01",
            cache_hit=False
        )
        
        score = assessor.score_junior_dev_value(feature, analysis)
        assert score <= 1


class TestAssessTeachingValue:
    """Test overall teaching value assessment."""
    
    def test_high_value_should_teach(self, assessor, sample_feature, sample_evidence, sample_file_analysis):
        """Test assessment for high-value code."""
        assessment = assessor.assess_teaching_value(
            sample_feature,
            sample_evidence,
            sample_file_analysis
        )
        
        assert isinstance(assessment, TeachingValueAssessment)
        assert assessment.total_score > 7
        assert assessment.should_teach is True
        assert 'reusability' in assessment.scores
        assert 'best_practice' in assessment.scores
        assert 'fundamentality' in assessment.scores
        assert 'uniqueness' in assessment.scores
        assert 'junior_dev' in assessment.scores
        assert len(assessment.reasoning) > 0
    
    def test_low_value_should_not_teach(self, assessor):
        """Test assessment for low-value code."""
        feature = FeatureMapping(
            feature_name="Utility Function",
            user_facing_purpose="Helper",
            business_value="Minor",
            entry_points=[],
            feature_flow=[]
        )
        
        evidence = EvidenceBundle(
            source_files=[{"path": "test.py", "code": "x = 1"}],
            test_files=[],
            git_commits=[],
            documentation=[],
            dependencies=[],
            dependents=[]
        )
        
        analysis = FileAnalysis(
            file_path="test.py",
            language="python",
            symbol_info=SymbolInfo([], [], [], []),
            patterns=[],
            teaching_value=TeachingValueScore(0.2, 0.2, 0.2, 0.2, 0.2, "", {}),
            complexity_metrics=ComplexityMetrics(1.0, 1, 1, [], [], 0.5),
            documentation_coverage=0.1,
            linter_issues=[],
            has_errors=False,
            errors=[],
            analyzed_at="2024-01-01",
            cache_hit=False
        )
        
        assessment = assessor.assess_teaching_value(feature, evidence, analysis)
        
        assert assessment.total_score <= 7
        assert assessment.should_teach is False
    
    def test_reasoning_generation(self, assessor, sample_feature, sample_evidence, sample_file_analysis):
        """Test that reasoning is generated."""
        assessment = assessor.assess_teaching_value(
            sample_feature,
            sample_evidence,
            sample_file_analysis
        )
        
        assert len(assessment.reasoning) > 0
        assert "reusability" in assessment.reasoning.lower() or "Reusability" in assessment.reasoning
        assert ";" in assessment.reasoning  # Multiple reasons separated by semicolons


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
