"""
Tests for Code Section Guide Generator.
"""

import pytest
from src.course.code_section_guide_generator import CodeSectionGuideGenerator
from src.course.models import CodeExample
from src.course.enrichment_models import EvidenceBundle, CodeSectionGuide


class TestCodeSectionGuideGenerator:
    """Test CodeSectionGuideGenerator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = CodeSectionGuideGenerator()
    
    def test_generate_section_guide_basic(self):
        """Test generating a basic section guide."""
        # Create a simple code example
        code_example = CodeExample(
            code="def add(a, b):\n    return a + b",
            language="python",
            filename="math_utils.py"
        )
        
        # Create minimal evidence bundle
        evidence = EvidenceBundle(
            source_files=[{"path": "math_utils.py", "code": code_example.code}],
            test_files=[],
            git_commits=[],
            documentation=[],
            dependencies=[],
            dependents=[]
        )
        
        # Generate guide
        guide = self.generator.generate_section_guide(code_example, evidence)
        
        # Verify guide structure
        assert isinstance(guide, CodeSectionGuide)
        assert guide.file_path == "math_utils.py"
        assert guide.code_snippet == code_example.code
        assert len(guide.purpose) > 0
        assert isinstance(guide.key_concepts, list)
        assert isinstance(guide.explanation_approach, list)
    
    def test_describe_purpose_with_evidence(self):
        """Test describing purpose with test evidence."""
        code_example = CodeExample(
            code="def login(username, password):\n    return authenticate(username, password)",
            language="python",
            filename="auth.py"
        )
        
        tests = [
            {
                "test_name": "test_login_success",
                "description": "Valid credentials return user",
                "file": "test_auth.py"
            }
        ]
        
        purpose = self.generator.describe_purpose_with_evidence(code_example, tests)
        
        assert "login" in purpose.lower()
        assert "test" in purpose.lower()
    
    def test_extract_key_concepts_python(self):
        """Test extracting key concepts from Python code."""
        code_example = CodeExample(
            code="""
async def fetch_data():
    try:
        data = await api.get()
        return [item for item in data if item.active]
    except Exception as e:
        logger.error(e)
        return []
""",
            language="python",
            filename="api.py"
        )
        
        concepts = self.generator.extract_key_concepts(code_example)
        
        assert "Asynchronous Programming" in concepts
        assert "Error Handling" in concepts
        assert "Lists/Arrays" in concepts
    
    def test_extract_key_concepts_javascript(self):
        """Test extracting key concepts from JavaScript code."""
        code_example = CodeExample(
            code="""
const fetchUser = async (id) => {
    try {
        const response = await fetch(`/api/users/${id}`);
        return response.json();
    } catch (error) {
        console.error(error);
    }
};
""",
            language="javascript",
            filename="api.js"
        )
        
        concepts = self.generator.extract_key_concepts(code_example)
        
        assert "Asynchronous Programming" in concepts
        assert "Error Handling" in concepts
        assert "Arrow Functions" in concepts
    
    def test_suggest_explanation_approach(self):
        """Test suggesting explanation approach."""
        code_example = CodeExample(
            code="""
class UserManager:
    def __init__(self, db):
        self.db = db
    
    async def create_user(self, username, email):
        user = User(username=username, email=email)
        await self.db.save(user)
        return user
""",
            language="python",
            filename="user_manager.py"
        )
        
        approach = self.generator.suggest_explanation_approach(code_example)
        
        assert isinstance(approach, list)
        assert len(approach) > 0
        assert any("class" in step.lower() for step in approach)
    
    def test_find_related_code(self):
        """Test finding related code."""
        code_example = CodeExample(
            code="from database import db\nfrom models import User\n\ndef get_user(id):\n    return db.query(User).get(id)",
            language="python",
            filename="user_service.py"
        )
        
        evidence = EvidenceBundle(
            source_files=[
                {"path": "user_service.py"},
                {"path": "user_controller.py"}
            ],
            test_files=[],
            git_commits=[],
            documentation=[],
            dependencies=[
                {"name": "database", "reason": "Database access"},
                {"name": "models", "reason": "Data models"}
            ],
            dependents=[
                {"name": "api.py", "usage": "Calls get_user"}
            ]
        )
        
        related = self.generator.find_related_code(code_example, evidence)
        
        assert isinstance(related, list)
        # Should find dependencies and dependents
        assert len(related) > 0
    
    def test_identify_common_mistakes_python(self):
        """Test identifying common mistakes in Python code."""
        code_example = CodeExample(
            code="""
def process_data(data):
    try:
        result = data == None
        return result
    except:
        pass
""",
            language="python",
            filename="processor.py"
        )
        
        tests = [
            {
                "test_name": "test_invalid_data_error",
                "description": "Invalid data raises ValueError",
                "file": "test_processor.py"
            }
        ]
        
        mistakes = self.generator.identify_common_mistakes(code_example, tests)
        
        assert isinstance(mistakes, list)
        # Should identify bare except
        assert any("except" in m.lower() for m in mistakes)
    
    def test_identify_common_mistakes_javascript(self):
        """Test identifying common mistakes in JavaScript code."""
        code_example = CodeExample(
            code="""
function compare(a, b) {
    if (a == b) {
        return true;
    }
    return false;
}
""",
            language="javascript",
            filename="utils.js"
        )
        
        tests = []
        
        mistakes = self.generator.identify_common_mistakes(code_example, tests)
        
        assert isinstance(mistakes, list)
        # Should identify == vs ===
        assert any("==" in m for m in mistakes)
    
    def test_generate_guide_with_full_evidence(self):
        """Test generating guide with comprehensive evidence."""
        code_example = CodeExample(
            code="""
@app.route('/api/users', methods=['POST'])
async def create_user():
    data = request.json
    user = User(**data)
    await db.save(user)
    return jsonify(user.to_dict()), 201
""",
            language="python",
            filename="routes.py"
        )
        
        evidence = EvidenceBundle(
            source_files=[{"path": "routes.py", "code": code_example.code}],
            test_files=[
                {
                    "path": "test_routes.py",
                    "tests": [
                        {
                            "name": "test_create_user_success",
                            "description": "Creating user returns 201"
                        }
                    ]
                }
            ],
            git_commits=[
                {
                    "hash": "abc123",
                    "message": "Add user creation endpoint",
                    "date": "2024-01-01",
                    "files_changed": ["routes.py"]
                }
            ],
            documentation=[
                {
                    "type": "docstring",
                    "content": "API endpoint for user creation"
                }
            ],
            dependencies=[
                {"name": "flask", "reason": "Web framework"}
            ],
            dependents=[
                {"name": "api_client.py", "usage": "Calls create_user endpoint"}
            ]
        )
        
        guide = self.generator.generate_section_guide(code_example, evidence)
        
        # Verify all components are present
        assert guide.file_path == "routes.py"
        assert len(guide.key_concepts) > 0
        assert len(guide.explanation_approach) > 0
        assert len(guide.test_evidence) > 0
        assert len(guide.git_evidence) > 0
        
        # Verify concepts include API-related items
        assert any("api" in c.lower() or "rest" in c.lower() for c in guide.key_concepts)


class TestHelperMethods:
    """Test helper methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = CodeSectionGuideGenerator()
    
    def test_extract_class_name(self):
        """Test extracting class name."""
        code = "class UserManager:\n    pass"
        name = self.generator._extract_class_name(code)
        assert name == "UserManager"
    
    def test_extract_function_name_python(self):
        """Test extracting Python function name."""
        code = "def calculate_total(items):\n    pass"
        name = self.generator._extract_function_name(code)
        assert name == "calculate_total"
    
    def test_extract_function_name_javascript(self):
        """Test extracting JavaScript function name."""
        code = "function processData(data) { }"
        name = self.generator._extract_function_name(code)
        assert name == "processData"
    
    def test_extract_imports_python(self):
        """Test extracting Python imports."""
        code = "from flask import Flask\nimport os\nfrom models import User"
        imports = self.generator._extract_imports(code, "python")
        assert "flask" in imports
        assert "os" in imports
        assert "models" in imports
    
    def test_extract_imports_javascript(self):
        """Test extracting JavaScript imports."""
        code = "import React from 'react';\nconst axios = require('axios');"
        imports = self.generator._extract_imports(code, "javascript")
        assert "react" in imports
        assert "axios" in imports
    
    def test_are_files_related_same_directory(self):
        """Test checking if files are in same directory."""
        file1 = "src/utils/helpers.py"
        file2 = "src/utils/validators.py"
        assert self.generator._are_files_related(file1, file2)
    
    def test_are_files_related_similar_names(self):
        """Test checking if files have similar names."""
        file1 = "src/user.py"
        file2 = "tests/user_test.py"
        assert self.generator._are_files_related(file1, file2)
    
    def test_are_files_not_related(self):
        """Test checking if files are not related."""
        file1 = "src/auth/login.py"
        file2 = "src/database/models.py"
        assert not self.generator._are_files_related(file1, file2)
