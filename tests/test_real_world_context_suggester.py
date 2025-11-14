"""
Tests for real-world context suggester.
"""

import pytest
from src.course.real_world_context_suggester import RealWorldContextSuggester
from src.course.enrichment_models import FeatureMapping, EvidenceBundle, RealWorldContext
from src.models.analysis_models import DetectedPattern


class TestRealWorldContextSuggester:
    """Test RealWorldContextSuggester functionality."""
    
    @pytest.fixture
    def suggester(self):
        """Create a suggester instance."""
        return RealWorldContextSuggester()
    
    @pytest.fixture
    def sample_feature(self):
        """Create a sample feature mapping."""
        return FeatureMapping(
            feature_name="User Authentication",
            user_facing_purpose="Allow users to log in securely with username and password",
            business_value="Protect user data and enable personalized experiences",
            entry_points=["POST /api/login", "LoginForm component"],
            feature_flow=[
                "User enters credentials",
                "Validate password hash",
                "Create session token",
                "Return token to client"
            ]
        )
    
    @pytest.fixture
    def sample_patterns(self):
        """Create sample detected patterns."""
        return [
            DetectedPattern(
                pattern_type="authentication",
                file_path="src/auth/login.py",
                confidence=0.9,
                evidence=["bcrypt.checkpw", "jwt.encode", "session token"],
                line_numbers=[10, 15, 20]
            ),
            DetectedPattern(
                pattern_type="api_route",
                file_path="src/api/routes.py",
                confidence=0.95,
                evidence=["POST /login", "request validation", "error handling"],
                line_numbers=[5, 10, 15]
            )
        ]
    
    @pytest.fixture
    def sample_evidence(self):
        """Create sample evidence bundle."""
        return EvidenceBundle(
            source_files=[
                {
                    "path": "src/auth/login.py",
                    "lines": list(range(1, 51)),
                    "code": "def login(username, password):\n    try:\n        user = get_user(username)\n        if bcrypt.checkpw(password, user.hash):\n            return create_session(user)\n    except Exception as e:\n        logger.error(f'Login failed: {e}')\n        raise"
                }
            ],
            test_files=[
                {
                    "path": "tests/test_auth.py",
                    "tests": ["test_valid_login", "test_invalid_password"],
                    "descriptions": ["Tests successful login", "Tests failed login"]
                }
            ],
            git_commits=[
                {
                    "hash": "abc123",
                    "message": "Add user authentication with bcrypt password hashing",
                    "date": "2024-01-15",
                    "author": "dev@example.com"
                }
            ],
            documentation=[
                {
                    "type": "docstring",
                    "content": '"""Authenticates user with username and password. Returns session token on success."""',
                    "location": "src/auth/login.py:5"
                }
            ],
            dependencies=[
                {"name": "bcrypt", "reason": "Password hashing", "evidence": "import bcrypt"},
                {"name": "jwt", "reason": "Token generation", "evidence": "import jwt"}
            ],
            dependents=[
                {"name": "api.routes", "usage": "Calls login()", "evidence": "from auth import login"}
            ]
        )
    
    def test_suggest_use_cases_authentication(self, suggester, sample_feature):
        """Test use case suggestions for authentication feature."""
        use_cases = suggester.suggest_use_cases(sample_feature)
        
        assert isinstance(use_cases, list)
        assert len(use_cases) > 0
        assert any("login" in uc.lower() or "auth" in uc.lower() for uc in use_cases)
    
    def test_suggest_use_cases_generic(self, suggester):
        """Test use case suggestions for generic feature."""
        feature = FeatureMapping(
            feature_name="Data Export",
            user_facing_purpose="Allow users to export their data to CSV format",
            business_value="Enable data portability and analysis",
            entry_points=["GET /api/export"],
            feature_flow=["Fetch user data", "Format as CSV", "Return file"]
        )
        
        use_cases = suggester.suggest_use_cases(feature)
        assert isinstance(use_cases, list)
        assert len(use_cases) > 0
    
    def test_suggest_analogies_beginner(self, suggester, sample_feature):
        """Test analogy suggestions for beginners."""
        analogies = suggester.suggest_analogies(sample_feature, skill_level="beginner")
        
        assert isinstance(analogies, list)
        assert len(analogies) > 0
        # Beginner analogies should use simple language
        assert any("like" in analogy.lower() for analogy in analogies)
    
    def test_suggest_analogies_advanced(self, suggester, sample_feature):
        """Test analogy suggestions for advanced users."""
        analogies = suggester.suggest_analogies(sample_feature, skill_level="advanced")
        
        assert isinstance(analogies, list)
        # Advanced users get fewer simple analogies
        # (may be empty or have more technical comparisons)
    
    def test_identify_industry_patterns(self, suggester, sample_patterns):
        """Test industry pattern identification."""
        patterns = suggester.identify_industry_patterns(sample_patterns)
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        # Should identify authentication-related patterns
        assert any("auth" in p.lower() or "token" in p.lower() for p in patterns)
    
    def test_identify_industry_patterns_empty(self, suggester):
        """Test with no patterns."""
        patterns = suggester.identify_industry_patterns([])
        
        assert isinstance(patterns, list)
        assert len(patterns) == 0
    
    def test_extract_best_practices(self, suggester, sample_evidence):
        """Test best practice extraction."""
        best_practices = suggester.extract_best_practices(sample_evidence)
        
        assert isinstance(best_practices, list)
        assert len(best_practices) > 0
        # Should identify testing as a best practice
        assert any("test" in bp.lower() for bp in best_practices)
    
    def test_extract_best_practices_with_docs(self, suggester, sample_evidence):
        """Test best practice extraction recognizes documentation."""
        best_practices = suggester.extract_best_practices(sample_evidence)
        
        # Should recognize documentation practices
        assert any("doc" in bp.lower() or "comment" in bp.lower() for bp in best_practices)
    
    def test_identify_anti_patterns(self, suggester, sample_evidence):
        """Test anti-pattern identification."""
        anti_patterns = suggester.identify_anti_patterns(sample_evidence)
        
        assert isinstance(anti_patterns, list)
        # May or may not find anti-patterns in clean code
    
    def test_identify_anti_patterns_with_issues(self, suggester):
        """Test anti-pattern identification with problematic code."""
        evidence = EvidenceBundle(
            source_files=[
                {
                    "path": "bad_code.py",
                    "lines": list(range(1, 100)),
                    "code": "def long_function():\n" + "    " * 10 + "nested_code = True\n" + "global bad_var\n"
                }
            ],
            test_files=[],
            git_commits=[],
            documentation=[
                {"type": "comment", "content": "TODO: Fix this hack later", "location": "bad_code.py:5"}
            ],
            dependencies=[],
            dependents=[]
        )
        
        anti_patterns = suggester.identify_anti_patterns(evidence)
        
        assert len(anti_patterns) > 0
        # Should identify issues like TODOs, deep nesting, globals
        assert any("todo" in ap.lower() or "nest" in ap.lower() or "global" in ap.lower() for ap in anti_patterns)
    
    def test_generate_context_complete(self, suggester, sample_feature, sample_patterns, sample_evidence):
        """Test complete context generation."""
        context = suggester.generate_context(
            feature=sample_feature,
            patterns=sample_patterns,
            evidence=sample_evidence,
            skill_level="beginner"
        )
        
        assert isinstance(context, RealWorldContext)
        assert len(context.practical_use_cases) > 0
        assert len(context.analogies) > 0
        assert len(context.industry_patterns) > 0
        assert len(context.best_practices) > 0
        # anti_patterns may be empty for clean code
        assert isinstance(context.anti_patterns, list)
    
    def test_generate_context_serialization(self, suggester, sample_feature, sample_patterns, sample_evidence):
        """Test that generated context can be serialized."""
        context = suggester.generate_context(
            feature=sample_feature,
            patterns=sample_patterns,
            evidence=sample_evidence
        )
        
        # Should be serializable to dict
        data = context.to_dict()
        assert isinstance(data, dict)
        assert 'practical_use_cases' in data
        assert 'analogies' in data
        assert 'industry_patterns' in data
        assert 'best_practices' in data
        assert 'anti_patterns' in data
        
        # Should be deserializable
        restored = RealWorldContext.from_dict(data)
        assert restored.practical_use_cases == context.practical_use_cases


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

