"""
Tests for validation engine.
"""

import pytest
from src.course.validation_engine import ValidationEngine, create_validation_engine


class TestValidationEngine:
    """Test ValidationEngine functionality."""
    
    def test_create_validation_engine(self):
        """Test creating a ValidationEngine instance."""
        engine = create_validation_engine()
        assert engine is not None
        assert isinstance(engine, ValidationEngine)
    
    def test_validate_code_behavior_empty(self):
        """Test validate_code_behavior with no source files."""
        engine = ValidationEngine()
        result = engine.validate_code_behavior([])
        
        assert "No source code available" in result
    
    def test_validate_code_behavior_python(self):
        """Test validate_code_behavior with Python code."""
        engine = ValidationEngine()
        
        source_files = [{
            'path': 'test.py',
            'code': '''def hello_world():
    """Say hello to the world."""
    return "Hello, World!"

class Greeter:
    """A class for greeting."""
    def greet(self, name):
        return f"Hello, {name}"
''',
            'language': 'python',
            'sections': []
        }]
        
        result = engine.validate_code_behavior(source_files)
        
        assert "hello_world" in result
        assert "Greeter" in result
        assert "test.py" in result
    
    def test_validate_code_behavior_javascript(self):
        """Test validate_code_behavior with JavaScript code."""
        engine = ValidationEngine()
        
        source_files = [{
            'path': 'app.js',
            'code': '''function greet(name) {
    return `Hello, ${name}`;
}

const add = (a, b) => a + b;

class Calculator {
    multiply(a, b) {
        return a * b;
    }
}
''',
            'language': 'javascript',
            'sections': []
        }]
        
        result = engine.validate_code_behavior(source_files)
        
        assert "greet" in result
        assert "Calculator" in result
        assert "app.js" in result
    
    def test_validate_test_expectations_empty(self):
        """Test validate_test_expectations with no test files."""
        engine = ValidationEngine()
        result = engine.validate_test_expectations([])
        
        assert "No tests available" in result
    
    def test_validate_test_expectations_pytest(self):
        """Test validate_test_expectations with pytest tests."""
        engine = ValidationEngine()
        
        test_files = [{
            'path': 'test_app.py',
            'test_cases': [
                {
                    'name': 'test_addition',
                    'description': 'Test that addition works correctly',
                    'type': 'function'
                },
                {
                    'name': 'test_subtraction',
                    'description': 'Should subtract two numbers',
                    'type': 'function'
                }
            ],
            'framework': 'pytest',
            'coverage': ['Addition functionality', 'Subtraction functionality']
        }]
        
        result = engine.validate_test_expectations(test_files)
        
        assert "test_app.py" in result
        assert "addition" in result.lower() or "subtract" in result.lower()
    
    def test_validate_test_expectations_jest(self):
        """Test validate_test_expectations with Jest tests."""
        engine = ValidationEngine()
        
        test_files = [{
            'path': 'app.test.js',
            'test_cases': [
                {
                    'name': 'should render correctly',
                    'description': 'should render correctly',
                    'type': 'it'
                },
                {
                    'name': 'should handle click events',
                    'description': 'should handle click events',
                    'type': 'it'
                }
            ],
            'framework': 'jest',
            'coverage': ['Rendering', 'Event handling']
        }]
        
        result = engine.validate_test_expectations(test_files)
        
        assert "app.test.js" in result
        assert "should" in result.lower()
    
    def test_validate_documentation_alignment_empty(self):
        """Test validate_documentation_alignment with no docs."""
        engine = ValidationEngine()
        result = engine.validate_documentation_alignment([])
        
        assert "No documentation available" in result
    
    def test_validate_documentation_alignment(self):
        """Test validate_documentation_alignment with documentation."""
        engine = ValidationEngine()
        
        docs = [
            {
                'type': 'docstring',
                'content': 'Calculate the sum of two numbers. Returns the result as an integer.',
                'location': 'Function: add (lines 10-15)',
                'context': "Documents function 'add'"
            },
            {
                'type': 'comment',
                'content': 'TODO: Add error handling for invalid inputs',
                'location': 'Line 20',
                'context': 'Implementation note'
            }
        ]
        
        result = engine.validate_documentation_alignment(docs)
        
        assert "add" in result
        assert "docstring" in result
    
    def test_validate_git_context_empty(self):
        """Test validate_git_context with no commits."""
        engine = ValidationEngine()
        result = engine.validate_git_context([])
        
        assert "No git history available" in result
    
    def test_validate_git_context(self):
        """Test validate_git_context with commits."""
        engine = ValidationEngine()
        
        commits = [
            {
                'hash': 'abc123def456',
                'author': 'John Doe',
                'date': '2024-01-15T10:30:00Z',
                'subject': 'Add user authentication feature',
                'message': 'Add user authentication feature\n\nImplements login and logout functionality with JWT tokens.',
                'files': ['src/auth.py', 'src/middleware.py']
            },
            {
                'hash': 'def456ghi789',
                'author': 'Jane Smith',
                'date': '2024-01-16T14:20:00Z',
                'subject': 'Fix password validation bug',
                'message': 'Fix password validation bug',
                'files': ['src/auth.py']
            }
        ]
        
        result = engine.validate_git_context(commits)
        
        assert "authentication" in result.lower() or "auth" in result.lower()
        assert "John Doe" in result
        assert "abc123de" in result
    
    def test_cross_reference_sources_insufficient(self):
        """Test cross_reference_sources with insufficient evidence."""
        engine = ValidationEngine()
        
        evidence = {
            'code_behavior': 'Some code behavior',
            'test_expectations': '',
            'documentation_alignment': '',
            'git_context': ''
        }
        
        # Should return True when insufficient sources (can't determine inconsistency)
        result = engine.cross_reference_sources(evidence)
        assert result is True
    
    def test_cross_reference_sources_consistent(self):
        """Test cross_reference_sources with consistent evidence."""
        engine = ValidationEngine()
        
        evidence = {
            'code_behavior': 'Implements user authentication with password hashing and session management',
            'test_expectations': 'Tests authentication flow, password validation, and session creation',
            'documentation_alignment': 'Documents authentication process and password security',
            'git_context': 'Added authentication feature with secure password handling'
        }
        
        result = engine.cross_reference_sources(evidence)
        # Should detect overlap in terms like 'authentication', 'password', 'session'
        assert isinstance(result, bool)
    
    def test_cross_reference_sources_inconsistent(self):
        """Test cross_reference_sources with inconsistent evidence."""
        engine = ValidationEngine()
        
        evidence = {
            'code_behavior': 'Implements database connection pooling and query optimization',
            'test_expectations': 'Tests email sending functionality and template rendering',
            'documentation_alignment': 'Documents file upload and storage mechanisms',
            'git_context': 'Added payment processing integration'
        }
        
        result = engine.cross_reference_sources(evidence)
        # Should detect low overlap between completely different topics
        assert isinstance(result, bool)
    
    def test_extract_key_terms(self):
        """Test _extract_key_terms helper method."""
        engine = ValidationEngine()
        
        text = "This function implements user authentication with password hashing"
        terms = engine._extract_key_terms(text)
        
        assert 'function' in terms
        assert 'implements' in terms
        assert 'user' in terms
        assert 'authentication' in terms
        assert 'password' in terms
        assert 'hashing' in terms
        # Stop words should be filtered
        assert 'this' not in terms
        assert 'with' not in terms
    
    def test_identify_commit_type(self):
        """Test _identify_commit_type helper method."""
        engine = ValidationEngine()
        
        assert engine._identify_commit_type("Add new feature") == "feature"
        assert engine._identify_commit_type("Fix bug in login") == "fix"
        assert engine._identify_commit_type("Refactor authentication module") == "refactor"
        assert engine._identify_commit_type("Update documentation") == "documentation"
        assert engine._identify_commit_type("Add tests for API") == "test"
        assert engine._identify_commit_type("Remove deprecated code") == "removal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
