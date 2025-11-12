"""
Unit tests for pattern detection.

Tests each pattern detector with known examples, verifies confidence scoring,
and tests false positive rate.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 14.4
"""

import pytest
from dataclasses import dataclass, field
from typing import List, Optional

from src.analysis.pattern_detector import (
    PatternDetector,
    BasePatternDetector,
    ReactPatternDetector,
    APIPatternDetector,
    DatabasePatternDetector,
    AuthPatternDetector,
    DetectedPattern
)


# Mock SymbolInfo and related classes for testing
@dataclass
class ImportInfo:
    module: str
    imported_symbols: List[str] = field(default_factory=list)
    is_relative: bool = False
    import_type: str = "import"
    line_number: int = 1


@dataclass
class FunctionInfo:
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    start_line: int = 1
    end_line: int = 10
    complexity: int = 1
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    start_line: int = 1
    end_line: int = 20
    decorators: List[str] = field(default_factory=list)


@dataclass
class SymbolInfo:
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


# ============================================================================
# React Pattern Detection Tests
# ============================================================================

class TestReactPatternDetector:
    """Test React pattern detection (Requirement 3.1)."""
    
    def test_detect_functional_component_with_hooks(self):
        """Test detection of React functional component with hooks."""
        detector = ReactPatternDetector()
        
        # Create symbol info for a React component
        symbol_info = SymbolInfo(
            imports=[
                ImportInfo(module="react", imported_symbols=["useState", "useEffect"], line_number=1)
            ],
            functions=[
                FunctionInfo(
                    name="UserProfile",
                    parameters=["{name, age}"],
                    start_line=5,
                    end_line=15
                )
            ]
        )
        
        file_content = """import React, { useState, useEffect } from 'react';

function UserProfile({name, age}) {
    const [count, setCount] = useState(0);
    
    useEffect(() => {
        console.log('mounted');
    }, []);
    
    return <div>{name}: {count}</div>;
}

export default UserProfile;
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/UserProfile.tsx")
        
        # Should detect component and hooks
        assert len(patterns) == 2
        
        # Check component pattern
        component_pattern = next(p for p in patterns if p.pattern_type == "react_component")
        assert component_pattern.confidence > 0.5
        assert any("PascalCase function name" in e for e in component_pattern.evidence)
        assert any("Props parameter" in e for e in component_pattern.evidence)
        assert any("Returns JSX" in e for e in component_pattern.evidence)
        assert any("Uses hooks" in e for e in component_pattern.evidence)
        assert component_pattern.metadata["component_name"] == "UserProfile"
        assert component_pattern.metadata["returns_jsx"] is True
        
        # Check hooks pattern
        hooks_pattern = next(p for p in patterns if p.pattern_type == "react_hooks")
        assert hooks_pattern.confidence > 0.5
        assert "useState" in hooks_pattern.metadata["hooks"]
        assert "useEffect" in hooks_pattern.metadata["hooks"]
    
    def test_detect_functional_component_without_props(self):
        """Test detection of React component without props."""
        detector = ReactPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="react", line_number=1)],
            functions=[
                FunctionInfo(name="App", parameters=[], start_line=3, end_line=7)
            ]
        )
        
        file_content = """import React from 'react';

function App() {
    return <div>Hello World</div>;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/App.tsx")
        
        # Should still detect component
        component_patterns = [p for p in patterns if p.pattern_type == "react_component"]
        assert len(component_patterns) == 1
        assert component_patterns[0].confidence > 0.3
    
    def test_no_react_import_no_detection(self):
        """Test that components without React import are not detected."""
        detector = ReactPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[],
            functions=[
                FunctionInfo(name="Helper", parameters=[], start_line=1, end_line=5)
            ]
        )
        
        file_content = """function Helper() {
    return <div>Test</div>;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/helper.ts")
        
        # Should not detect without React import
        assert len(patterns) == 0
    
    def test_lowercase_function_not_component(self):
        """Test that lowercase functions are not detected as components."""
        detector = ReactPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="react", line_number=1)],
            functions=[
                FunctionInfo(name="helper", parameters=[], start_line=3, end_line=7)
            ]
        )
        
        file_content = """import React from 'react';

function helper() {
    return <div>Not a component</div>;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/helper.ts")
        
        # Should not detect lowercase function as component
        component_patterns = [p for p in patterns if p.pattern_type == "react_component"]
        assert len(component_patterns) == 0
    
    def test_confidence_scoring_increases_with_evidence(self):
        """Test that confidence score increases with more evidence."""
        detector = ReactPatternDetector()
        
        # Component with minimal evidence
        minimal_symbol_info = SymbolInfo(
            imports=[ImportInfo(module="react", line_number=1)],
            functions=[FunctionInfo(name="Simple", parameters=[], start_line=3, end_line=5)]
        )
        minimal_content = """import React from 'react';

function Simple() {
    return <div>Test</div>;
}
"""
        
        minimal_patterns = detector.detect(minimal_symbol_info, minimal_content, "src/Simple.tsx")
        minimal_confidence = next(
            (p.confidence for p in minimal_patterns if p.pattern_type == "react_component"),
            0
        )
        
        # Component with maximum evidence
        maximal_symbol_info = SymbolInfo(
            imports=[ImportInfo(module="react", imported_symbols=["useState"], line_number=1)],
            functions=[
                FunctionInfo(
                    name="Complex",
                    parameters=["{props}"],
                    start_line=3,
                    end_line=10
                )
            ]
        )
        maximal_content = """import React, { useState } from 'react';

function Complex({props}) {
    const [state, setState] = useState(0);
    return <div>{state}</div>;
}
"""
        
        maximal_patterns = detector.detect(maximal_symbol_info, maximal_content, "src/Complex.tsx")
        maximal_confidence = next(
            (p.confidence for p in maximal_patterns if p.pattern_type == "react_component"),
            0
        )
        
        # Maximal should have higher confidence
        assert maximal_confidence > minimal_confidence


# ============================================================================
# API Pattern Detection Tests
# ============================================================================

class TestAPIPatternDetector:
    """Test API pattern detection (Requirement 3.2)."""
    
    def test_detect_express_routes(self):
        """Test detection of Express.js routes."""
        detector = APIPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="express", line_number=1)]
        )
        
        file_content = """const express = require('express');
const app = express();

app.get('/users', (req, res) => {
    res.json({ users: [] });
});

app.post('/users', (req, res) => {
    res.status(201).json({ created: true });
});

router.delete('/users/:id', (req, res) => {
    res.status(204).send();
});
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/routes/users.js")
        
        # Should detect Express API pattern
        express_patterns = [p for p in patterns if p.pattern_type == "express_api"]
        assert len(express_patterns) == 1
        
        pattern = express_patterns[0]
        assert pattern.confidence > 0.5
        assert "Imports express" in pattern.evidence
        assert pattern.metadata["framework"] == "express"
        assert pattern.metadata["route_count"] == 3
        
        # Check routes
        routes = pattern.metadata["routes"]
        assert any(r["method"] == "GET" and r["path"] == "/users" for r in routes)
        assert any(r["method"] == "POST" and r["path"] == "/users" for r in routes)
        assert any(r["method"] == "DELETE" for r in routes)
    
    def test_detect_fastapi_endpoints(self):
        """Test detection of FastAPI endpoints."""
        detector = APIPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="fastapi", imported_symbols=["FastAPI"], line_number=1)],
            functions=[
                FunctionInfo(
                    name="get_users",
                    decorators=["@app.get('/users')"],
                    is_async=True,
                    start_line=5
                ),
                FunctionInfo(
                    name="create_user",
                    decorators=["@app.post('/users')"],
                    is_async=True,
                    start_line=10
                )
            ]
        )
        
        file_content = """from fastapi import FastAPI

app = FastAPI()

@app.get('/users')
async def get_users():
    return {"users": []}

@app.post('/users')
async def create_user():
    return {"created": True}
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/api/users.py")
        
        # Should detect FastAPI pattern
        fastapi_patterns = [p for p in patterns if p.pattern_type == "fastapi_endpoint"]
        assert len(fastapi_patterns) == 1
        
        pattern = fastapi_patterns[0]
        assert pattern.confidence > 0.3
        assert pattern.metadata["framework"] == "fastapi"
        assert pattern.metadata["endpoint_count"] == 2
        
        # Check endpoints
        endpoints = pattern.metadata["endpoints"]
        assert any(e["method"] == "GET" and e["function"] == "get_users" for e in endpoints)
        assert any(e["method"] == "POST" and e["function"] == "create_user" for e in endpoints)
    
    def test_detect_nextjs_api_routes(self):
        """Test detection of Next.js API routes."""
        detector = APIPatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[
                FunctionInfo(
                    name="handler",
                    parameters=["req", "res"],
                    start_line=3
                )
            ]
        )
        
        file_content = """// pages/api/users.js

export default function handler(req, res) {
    if (req.method === 'GET') {
        res.status(200).json({ users: [] });
    }
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "pages/api/users.js")
        
        # Should detect Next.js API route
        nextjs_patterns = [p for p in patterns if p.pattern_type == "nextjs_api_route"]
        assert len(nextjs_patterns) == 1
        
        pattern = nextjs_patterns[0]
        assert pattern.confidence > 0.5
        assert pattern.metadata["framework"] == "nextjs"
        assert pattern.metadata["handler_name"] == "handler"
    
    def test_no_api_pattern_in_regular_file(self):
        """Test that regular files don't trigger false positives."""
        detector = APIPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="lodash", line_number=1)],
            functions=[FunctionInfo(name="helper", start_line=3)]
        )
        
        file_content = """import _ from 'lodash';

function helper() {
    return _.map([1, 2, 3], x => x * 2);
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/utils/helper.js")
        
        # Should not detect any API patterns
        assert len(patterns) == 0


# ============================================================================
# Database Pattern Detection Tests
# ============================================================================

class TestDatabasePatternDetector:
    """Test database pattern detection (Requirement 3.3)."""
    
    def test_detect_sqlalchemy_orm_models(self):
        """Test detection of SQLAlchemy ORM models."""
        detector = DatabasePatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[
                ImportInfo(
                    module="sqlalchemy",
                    imported_symbols=["Column", "Integer", "String"],
                    line_number=1
                )
            ],
            classes=[
                ClassInfo(
                    name="User",
                    base_classes=["Base"],
                    start_line=5,
                    end_line=10
                )
            ]
        )
        
        file_content = """from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/models/user.py")
        
        # Should detect ORM model
        orm_patterns = [p for p in patterns if p.pattern_type == "orm_model"]
        assert len(orm_patterns) == 1
        
        pattern = orm_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["orm_framework"] == "sqlalchemy"
        assert pattern.metadata["model_count"] == 1
        assert any("User" in str(m) for m in pattern.metadata["models"])
    
    def test_detect_django_orm_models(self):
        """Test detection of Django ORM models."""
        detector = DatabasePatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[
                ImportInfo(module="django.db", imported_symbols=["models"], line_number=1)
            ],
            classes=[
                ClassInfo(
                    name="Article",
                    base_classes=["models.Model"],
                    start_line=3,
                    end_line=7
                )
            ]
        )
        
        file_content = """from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/models.py")
        
        # Should detect Django ORM model
        orm_patterns = [p for p in patterns if p.pattern_type == "orm_model"]
        assert len(orm_patterns) == 1
        
        pattern = orm_patterns[0]
        assert pattern.metadata["orm_framework"] == "django"
    
    def test_detect_query_builder(self):
        """Test detection of query builder usage."""
        detector = DatabasePatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="knex", line_number=1)]
        )
        
        file_content = """const knex = require('knex');

const users = await knex('users')
    .select('*')
    .where('active', true)
    .orderBy('created_at', 'desc');

const result = await knex('posts')
    .insert({ title: 'New Post' })
    .returning('*');
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/db/queries.js")
        
        # Should detect query builder
        query_patterns = [p for p in patterns if p.pattern_type == "query_builder"]
        assert len(query_patterns) == 1
        
        pattern = query_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["builder"] == "knex"
        assert pattern.metadata["query_count"] > 0
    
    def test_detect_database_migration(self):
        """Test detection of database migrations."""
        detector = DatabasePatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[
                FunctionInfo(name="upgrade", start_line=5),
                FunctionInfo(name="downgrade", start_line=12)
            ]
        )
        
        file_content = """\"\"\"Add users table

Revision ID: abc123
\"\"\"

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True)
    )

def downgrade():
    op.drop_table('users')
"""
        
        patterns = detector.detect(symbol_info, file_content, "migrations/versions/001_add_users.py")
        
        # Should detect migration
        migration_patterns = [p for p in patterns if p.pattern_type == "database_migration"]
        assert len(migration_patterns) == 1
        
        pattern = migration_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["migration_type"] == "alembic"


# ============================================================================
# Auth Pattern Detection Tests
# ============================================================================

class TestAuthPatternDetector:
    """Test authentication pattern detection (Requirement 3.4)."""
    
    def test_detect_jwt_authentication(self):
        """Test detection of JWT authentication."""
        detector = AuthPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="jwt", line_number=1)],
            functions=[
                FunctionInfo(name="create_access_token", start_line=5),
                FunctionInfo(name="verify_token", start_line=10)
            ]
        )
        
        file_content = """import jwt
from datetime import datetime, timedelta

SECRET_KEY = "secret"

def create_access_token(user_id):
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/auth/jwt.py")
        
        # Should detect JWT pattern
        jwt_patterns = [p for p in patterns if p.pattern_type == "jwt_authentication"]
        assert len(jwt_patterns) == 1
        
        pattern = jwt_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["auth_type"] == "jwt"
        assert "jwt.encode" in pattern.metadata["operations"] or "jwt.decode" in pattern.metadata["operations"]
    
    def test_detect_oauth_authentication(self):
        """Test detection of OAuth authentication."""
        detector = AuthPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="authlib", line_number=1)]
        )
        
        file_content = """from authlib.integrations.flask_client import OAuth

oauth = OAuth()

oauth.register(
    'google',
    client_id='CLIENT_ID',
    client_secret='CLIENT_SECRET',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    token_url='https://oauth2.googleapis.com/token'
)
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/auth/oauth.py")
        
        # Should detect OAuth pattern
        oauth_patterns = [p for p in patterns if p.pattern_type == "oauth_authentication"]
        assert len(oauth_patterns) == 1
        
        pattern = oauth_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["auth_type"] == "oauth"
    
    def test_detect_session_authentication(self):
        """Test detection of session-based authentication."""
        detector = AuthPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="flask", imported_symbols=["session"], line_number=1)]
        )
        
        file_content = """from flask import Flask, session

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    session['user_id'] = user.id
    return {'success': True}

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return {'success': True}
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/auth/session.py")
        
        # Should detect session pattern
        session_patterns = [p for p in patterns if p.pattern_type == "session_authentication"]
        assert len(session_patterns) == 1
        
        pattern = session_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["auth_type"] == "session"
    
    def test_detect_api_key_authentication(self):
        """Test detection of API key authentication."""
        detector = AuthPatternDetector()
        
        symbol_info = SymbolInfo(
            functions=[FunctionInfo(name="validate_api_key", start_line=3)]
        )
        
        file_content = """from flask import request

def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in valid_keys:
        return False
    return True
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/auth/api_key.py")
        
        # Should detect API key pattern
        api_key_patterns = [p for p in patterns if p.pattern_type == "api_key_authentication"]
        assert len(api_key_patterns) == 1
        
        pattern = api_key_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["auth_type"] == "api_key"
    
    def test_detect_password_hashing(self):
        """Test detection of password hashing."""
        detector = AuthPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="bcrypt", line_number=1)],
            functions=[
                FunctionInfo(name="hash_password", start_line=5),
                FunctionInfo(name="verify_password", start_line=10)
            ]
        )
        
        file_content = """import bcrypt

SALT_ROUNDS = 12

def hash_password(password):
    salt = bcrypt.gensalt(rounds=SALT_ROUNDS)
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)
"""
        
        patterns = detector.detect(symbol_info, file_content, "src/auth/password.py")
        
        # Should detect password hashing
        password_patterns = [p for p in patterns if p.pattern_type == "password_hashing"]
        assert len(password_patterns) == 1
        
        pattern = password_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["auth_type"] == "password"
        assert "bcrypt" in pattern.metadata["algorithms"]


# ============================================================================
# Pattern Detector Integration Tests
# ============================================================================

class TestPatternDetector:
    """Test the main PatternDetector orchestrator (Requirement 3.5)."""
    
    def test_register_detector(self):
        """Test registering custom pattern detectors."""
        detector = PatternDetector()
        
        # Initially empty
        assert len(detector.detectors) == 0
        
        # Register a detector
        detector.register_detector(ReactPatternDetector())
        assert len(detector.detectors) == 1
    
    def test_detect_patterns_in_file_with_multiple_detectors(self):
        """Test detecting patterns with multiple registered detectors."""
        detector = PatternDetector()
        detector.register_detector(ReactPatternDetector())
        detector.register_detector(APIPatternDetector())
        
        symbol_info = SymbolInfo(
            imports=[
                ImportInfo(module="react", line_number=1),
                ImportInfo(module="express", line_number=2)
            ],
            functions=[
                FunctionInfo(name="App", start_line=5, end_line=10)
            ]
        )
        
        file_content = """import React from 'react';
const express = require('express');

function App() {
    return <div>Hello</div>;
}

app.get('/api/test', (req, res) => {
    res.json({ test: true });
});
"""
        
        patterns = detector.detect_patterns_in_file(symbol_info, file_content, "src/App.tsx")
        
        # Should detect patterns from both detectors
        assert len(patterns) > 0
        pattern_types = [p.pattern_type for p in patterns]
        assert any("react" in pt for pt in pattern_types)
        assert any("express" in pt for pt in pattern_types)
    
    def test_detect_global_patterns(self):
        """Test detecting global patterns across codebase."""
        detector = PatternDetector()
        
        # Mock file analyses with patterns
        file_analyses = {
            "file1.tsx": type('obj', (object,), {
                'patterns': [
                    DetectedPattern(
                        pattern_type="react_component",
                        file_path="file1.tsx",
                        confidence=0.9,
                        evidence=["test"],
                        line_numbers=[1]
                    )
                ]
            })(),
            "file2.tsx": type('obj', (object,), {
                'patterns': [
                    DetectedPattern(
                        pattern_type="react_component",
                        file_path="file2.tsx",
                        confidence=0.8,
                        evidence=["test"],
                        line_numbers=[1]
                    )
                ]
            })(),
            "file3.py": type('obj', (object,), {
                'patterns': [
                    DetectedPattern(
                        pattern_type="fastapi_endpoint",
                        file_path="file3.py",
                        confidence=0.95,
                        evidence=["test"],
                        line_numbers=[1]
                    )
                ]
            })()
        }
        
        global_patterns = detector.detect_global_patterns(file_analyses)
        
        # Should create global pattern summaries
        assert len(global_patterns) > 0
        
        # Check pattern counts
        react_global = next(
            (p for p in global_patterns if "react_component" in p.pattern_type),
            None
        )
        assert react_global is not None
        assert react_global.metadata["count"] == 2
        
        fastapi_global = next(
            (p for p in global_patterns if "fastapi_endpoint" in p.pattern_type),
            None
        )
        assert fastapi_global is not None
        assert fastapi_global.metadata["count"] == 1
    
    def test_confidence_scoring_consistency(self):
        """Test that confidence scoring is consistent (Requirement 14.4)."""
        detector = ReactPatternDetector()
        
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="react", line_number=1)],
            functions=[FunctionInfo(name="Test", start_line=3, end_line=7)]
        )
        
        file_content = """import React from 'react';

function Test() {
    return <div>Test</div>;
}
"""
        
        # Run detection multiple times
        results = []
        for _ in range(5):
            patterns = detector.detect(symbol_info, file_content, "src/Test.tsx")
            component_patterns = [p for p in patterns if p.pattern_type == "react_component"]
            if component_patterns:
                results.append(component_patterns[0].confidence)
        
        # All confidence scores should be identical
        assert len(set(results)) == 1, "Confidence scores should be consistent across runs"
    
    def test_false_positive_rate_low(self):
        """Test that false positive rate is low (Requirement 14.4)."""
        # Test all detectors with non-matching code
        detectors = [
            ReactPatternDetector(),
            APIPatternDetector(),
            DatabasePatternDetector(),
            AuthPatternDetector()
        ]
        
        # Generic utility code that shouldn't match any patterns
        symbol_info = SymbolInfo(
            imports=[ImportInfo(module="math", line_number=1)],
            functions=[FunctionInfo(name="calculate", start_line=3)]
        )
        
        file_content = """import math

def calculate(x, y):
    return math.sqrt(x ** 2 + y ** 2)
"""
        
        total_false_positives = 0
        for detector in detectors:
            patterns = detector.detect(symbol_info, file_content, "src/utils.py")
            total_false_positives += len(patterns)
        
        # Should have zero false positives
        assert total_false_positives == 0, "Should not detect patterns in generic utility code"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
