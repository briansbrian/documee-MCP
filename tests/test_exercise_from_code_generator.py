"""Unit tests for Exercise From Code Generator."""

import pytest
from src.course.exercise_from_code_generator import (
    ExerciseFromCodeGenerator,
    create_exercise_generator
)
from src.course.enrichment_models import (
    FeatureMapping,
    EvidenceBundle,
    ExerciseGeneration
)


# ========== Test Fixtures ==========

@pytest.fixture
def exercise_generator():
    """Create an exercise generator instance."""
    return ExerciseFromCodeGenerator()


@pytest.fixture
def sample_feature_mapping():
    """Create a sample feature mapping."""
    return FeatureMapping(
        feature_name="User Authentication",
        user_facing_purpose="Allow users to securely log in to the application",
        business_value="Protects user data and enables personalized experiences",
        entry_points=["POST /api/login", "LoginForm component"],
        feature_flow=[
            "User enters credentials",
            "System validates credentials",
            "System creates session token",
            "User receives authentication token"
        ]
    )


@pytest.fixture
def sample_solution_code():
    """Sample solution code for testing."""
    return '''"""User authentication module."""

import bcrypt
from datetime import datetime, timedelta


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        password: Plain text password to verify
        hashed: Hashed password to check against
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )


class SessionManager:
    """Manages user sessions."""
    
    def __init__(self, expiry_hours=24):
        """Initialize session manager.
        
        Args:
            expiry_hours: Hours until session expires
        """
        self.sessions = {}
        self.expiry_hours = expiry_hours
    
    def create_session(self, user_id: str) -> str:
        """Create a new session for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session token
        """
        import secrets
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=self.expiry_hours)
        
        self.sessions[token] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'expires_at': expiry
        }
        
        return token
    
    def validate_session(self, token: str) -> bool:
        """Validate a session token.
        
        Args:
            token: Session token to validate
            
        Returns:
            True if valid, False otherwise
        """
        if token not in self.sessions:
            return False
        
        session = self.sessions[token]
        if datetime.now() > session['expires_at']:
            del self.sessions[token]
            return False
        
        return True
'''


@pytest.fixture
def sample_evidence_bundle(sample_solution_code):
    """Create a sample evidence bundle."""
    return EvidenceBundle(
        source_files=[
            {
                'path': 'src/auth/session.py',
                'code': sample_solution_code,
                'lines': len(sample_solution_code.split('\n')),
                'language': 'python',
                'sections': [
                    {
                        'start_line': 1,
                        'end_line': len(sample_solution_code.split('\n')),
                        'description': 'Complete authentication module',
                        'code': sample_solution_code
                    }
                ]
            }
        ],
        test_files=[
            {
                'path': 'tests/test_auth.py',
                'test_cases': [
                    {
                        'name': 'test_hash_password_creates_valid_hash',
                        'description': 'Should create a valid bcrypt hash',
                        'type': 'function'
                    },
                    {
                        'name': 'test_verify_password_with_correct_password',
                        'description': 'Should return True for correct password',
                        'type': 'function'
                    },
                    {
                        'name': 'test_verify_password_with_incorrect_password',
                        'description': 'Should return False for incorrect password',
                        'type': 'function'
                    },
                    {
                        'name': 'test_create_session_returns_token',
                        'description': 'Should return a session token',
                        'type': 'function'
                    },
                    {
                        'name': 'test_validate_session_with_valid_token',
                        'description': 'Should return True for valid token',
                        'type': 'function'
                    },
                    {
                        'name': 'test_validate_session_with_expired_token',
                        'description': 'Should return False for expired token',
                        'type': 'function'
                    }
                ],
                'framework': 'pytest',
                'coverage': [
                    'Should create a valid bcrypt hash',
                    'Should return True for correct password',
                    'Should return False for incorrect password',
                    'Should return a session token',
                    'Should return True for valid token',
                    'Should return False for expired token'
                ],
                'total_tests': 6
            }
        ],
        git_commits=[
            {
                'hash': 'abc123',
                'message': 'Add password hashing with bcrypt',
                'date': '2024-01-15',
                'author': 'dev@example.com'
            }
        ],
        documentation=[
            {
                'type': 'docstring',
                'content': 'Hash a password using bcrypt',
                'location': 'Function: hash_password',
                'context': 'Documents function hash_password'
            }
        ],
        dependencies=[
            {
                'name': 'bcrypt',
                'symbols': ['gensalt', 'hashpw', 'checkpw'],
                'reason': 'Password hashing functionality',
                'evidence': 'Line 3: import',
                'type': 'third_party'
            }
        ],
        dependents=[]
    )


# ========== Test Extract Solution Code ==========

def test_extract_solution_code_from_evidence(exercise_generator, sample_evidence_bundle):
    """Test extracting solution code from evidence bundle."""
    solution = exercise_generator.extract_solution_code(sample_evidence_bundle)
    
    assert solution is not None
    assert len(solution) > 0
    assert 'def hash_password' in solution
    assert 'class SessionManager' in solution


def test_extract_solution_code_with_no_source_files(exercise_generator):
    """Test extracting solution code when no source files available."""
    empty_evidence = EvidenceBundle(
        source_files=[],
        test_files=[],
        git_commits=[],
        documentation=[],
        dependencies=[],
        dependents=[]
    )
    
    solution = exercise_generator.extract_solution_code(empty_evidence)
    assert solution == "# No solution code available"


# ========== Test Create Starter Code ==========

def test_create_starter_code_preserves_structure(exercise_generator, sample_solution_code):
    """Test that starter code preserves function and class structure."""
    starter = exercise_generator.create_starter_code(sample_solution_code)
    
    # Should preserve imports
    assert 'import bcrypt' in starter
    assert 'from datetime import' in starter
    
    # Should preserve function definitions
    assert 'def hash_password' in starter
    assert 'def verify_password' in starter
    
    # Should preserve class definition
    assert 'class SessionManager' in starter
    
    # Should preserve docstrings
    assert '"""Hash a password using bcrypt."""' in starter or 'Hash a password using bcrypt' in starter


def test_create_starter_code_removes_implementation(exercise_generator, sample_solution_code):
    """Test that starter code removes implementation details."""
    starter = exercise_generator.create_starter_code(sample_solution_code)
    
    # Should add TODO comments
    assert 'TODO' in starter
    assert 'pass' in starter
    
    # Should not have full implementation
    assert 'bcrypt.gensalt()' not in starter
    assert 'secrets.token_urlsafe' not in starter


def test_create_starter_code_with_empty_solution(exercise_generator):
    """Test creating starter code from empty solution."""
    starter = exercise_generator.create_starter_code("")
    
    assert 'TODO' in starter
    assert 'pass' in starter


# ========== Test Extract Requirements from Tests ==========

def test_extract_requirements_from_tests(exercise_generator, sample_evidence_bundle):
    """Test extracting requirements from test cases."""
    requirements = exercise_generator.extract_requirements_from_tests(
        sample_evidence_bundle.test_files
    )
    
    assert len(requirements) > 0
    assert any('hash' in req.lower() for req in requirements)
    assert any('password' in req.lower() for req in requirements)


def test_extract_requirements_converts_test_descriptions(exercise_generator):
    """Test that test descriptions are converted to requirements."""
    test_files = [
        {
            'test_cases': [
                {
                    'name': 'test_should_validate_input',
                    'description': 'should validate user input'
                }
            ]
        }
    ]
    
    requirements = exercise_generator.extract_requirements_from_tests(test_files)
    
    assert len(requirements) > 0
    # Should convert "should" to "Must"
    assert any('Must' in req or 'validate' in req.lower() for req in requirements)


def test_extract_requirements_with_no_tests(exercise_generator):
    """Test extracting requirements when no tests available."""
    requirements = exercise_generator.extract_requirements_from_tests([])
    
    # Should return generic requirements
    assert len(requirements) > 0
    assert any('functionality' in req.lower() for req in requirements)


# ========== Test Generate Progressive Hints ==========

def test_generate_progressive_hints_count(exercise_generator, sample_solution_code):
    """Test that 3-5 progressive hints are generated."""
    requirements = ["Must hash passwords", "Must verify passwords"]
    hints = exercise_generator.generate_progressive_hints(sample_solution_code, requirements)
    
    assert len(hints) >= 3
    assert len(hints) <= 5


def test_generate_progressive_hints_are_progressive(exercise_generator, sample_solution_code):
    """Test that hints progress from general to specific."""
    requirements = ["Must hash passwords", "Must verify passwords"]
    hints = exercise_generator.generate_progressive_hints(sample_solution_code, requirements)
    
    # First hint should be more general
    first_hint = hints[0].lower()
    assert any(word in first_hint for word in ['think', 'consider', 'start', 'focus'])
    
    # Later hints should be more specific
    if len(hints) > 2:
        later_hint = hints[-1].lower()
        # Should mention specific concepts or edge cases
        assert len(later_hint) > 20  # More detailed


def test_generate_progressive_hints_with_simple_code(exercise_generator):
    """Test hint generation for simple code."""
    simple_code = '''def add(a, b):
    return a + b
'''
    requirements = ["Must add two numbers"]
    hints = exercise_generator.generate_progressive_hints(simple_code, requirements)
    
    # Should still generate at least 3 hints
    assert len(hints) >= 3


# ========== Test Create Assessment Questions ==========

def test_create_assessment_questions(
    exercise_generator,
    sample_feature_mapping,
    sample_evidence_bundle
):
    """Test creating self-assessment questions."""
    questions = exercise_generator.create_assessment_questions(
        sample_feature_mapping,
        sample_evidence_bundle
    )
    
    assert len(questions) > 0
    # Should ask about purpose
    assert any('purpose' in q.lower() or 'why' in q.lower() for q in questions)


def test_create_assessment_questions_includes_feature_name(
    exercise_generator,
    sample_feature_mapping,
    sample_evidence_bundle
):
    """Test that questions reference the feature name."""
    questions = exercise_generator.create_assessment_questions(
        sample_feature_mapping,
        sample_evidence_bundle
    )
    
    # At least one question should mention the feature
    assert any(sample_feature_mapping.feature_name in q for q in questions)


def test_create_assessment_questions_covers_multiple_aspects(
    exercise_generator,
    sample_feature_mapping,
    sample_evidence_bundle
):
    """Test that questions cover different aspects."""
    questions = exercise_generator.create_assessment_questions(
        sample_feature_mapping,
        sample_evidence_bundle
    )
    
    # Should have questions about different aspects
    question_text = ' '.join(questions).lower()
    
    # Should cover purpose, implementation, edge cases, etc.
    aspects_covered = sum([
        'purpose' in question_text or 'why' in question_text,
        'approach' in question_text or 'how' in question_text,
        'edge' in question_text or 'case' in question_text,
        'improve' in question_text or 'optimization' in question_text
    ])
    
    assert aspects_covered >= 2  # At least 2 different aspects


# ========== Test Generate Exercises Integration ==========

def test_generate_exercises_complete(
    exercise_generator,
    sample_feature_mapping,
    sample_evidence_bundle
):
    """Test complete exercise generation."""
    exercise = exercise_generator.generate_exercises(
        sample_feature_mapping,
        sample_evidence_bundle
    )
    
    assert isinstance(exercise, ExerciseGeneration)
    assert exercise.solution_code is not None
    assert exercise.starter_code is not None
    assert len(exercise.progressive_hints) >= 3
    assert len(exercise.self_assessment) > 0
    assert len(exercise.hands_on_tasks) > 0


def test_generate_exercises_has_valid_structure(
    exercise_generator,
    sample_feature_mapping,
    sample_evidence_bundle
):
    """Test that generated exercise has valid structure."""
    exercise = exercise_generator.generate_exercises(
        sample_feature_mapping,
        sample_evidence_bundle
    )
    
    # Starter code should be shorter than solution
    assert len(exercise.starter_code) < len(exercise.solution_code)
    
    # Should have test cases
    assert len(exercise.test_cases) > 0
    
    # Hints should be progressive (increasing specificity)
    assert len(exercise.progressive_hints) >= 3


def test_generate_exercises_preserves_evidence(
    exercise_generator,
    sample_feature_mapping,
    sample_evidence_bundle
):
    """Test that exercise generation preserves evidence from tests."""
    exercise = exercise_generator.generate_exercises(
        sample_feature_mapping,
        sample_evidence_bundle
    )
    
    # Test cases should match evidence
    assert len(exercise.test_cases) == len(sample_evidence_bundle.test_files[0]['test_cases'])
    
    # Should reference test framework
    assert any(
        tc.get('framework') == 'pytest'
        for tc in exercise.test_cases
    )


# ========== Test Factory Function ==========

def test_create_exercise_generator():
    """Test factory function creates valid generator."""
    generator = create_exercise_generator()
    
    assert isinstance(generator, ExerciseFromCodeGenerator)
    assert hasattr(generator, 'generate_exercises')
    assert hasattr(generator, 'extract_solution_code')
    assert hasattr(generator, 'create_starter_code')
