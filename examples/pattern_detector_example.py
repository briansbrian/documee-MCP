"""
Example demonstrating the Pattern Detector functionality.

This example shows how to use the pattern detector to identify
React components, API routes, database models, and authentication patterns.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.pattern_detector import (
    PatternDetector,
    ReactPatternDetector,
    APIPatternDetector,
    DatabasePatternDetector,
    AuthPatternDetector,
    DetectedPattern
)
from src.analysis.symbol_extractor import SymbolInfo, FunctionInfo, ImportInfo


def example_react_detection():
    """Example: Detect React component patterns."""
    print("=" * 60)
    print("Example 1: React Component Detection")
    print("=" * 60)
    
    # Create sample React component code
    react_code = """
import React, { useState, useEffect } from 'react';

function UserProfile({ userId, name }) {
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        fetchUser(userId);
    }, [userId]);
    
    return (
        <div className="profile">
            <h1>{name}</h1>
        </div>
    );
}

export default UserProfile;
"""
    
    # Create symbol info
    symbol_info = SymbolInfo(
        functions=[
            FunctionInfo(
                name="UserProfile",
                parameters=["{userId, name}"],
                start_line=3,
                end_line=15
            )
        ],
        imports=[
            ImportInfo(
                module="react",
                imported_symbols=["useState", "useEffect"],
                line_number=1
            )
        ]
    )
    
    # Detect patterns
    detector = ReactPatternDetector()
    patterns = detector.detect(symbol_info, react_code, "src/components/UserProfile.jsx")
    
    print(f"\nDetected {len(patterns)} React patterns:\n")
    for pattern in patterns:
        print(f"Pattern Type: {pattern.pattern_type}")
        print(f"Confidence: {pattern.confidence:.2f}")
        print(f"Evidence:")
        for evidence in pattern.evidence:
            print(f"  - {evidence}")
        print(f"Metadata: {pattern.metadata}")
        print()


def example_api_detection():
    """Example: Detect API route patterns."""
    print("=" * 60)
    print("Example 2: API Route Detection")
    print("=" * 60)
    
    # Create sample Express API code
    express_code = """
const express = require('express');
const router = express.Router();

router.get('/users', async (req, res) => {
    const users = await User.findAll();
    res.json(users);
});

router.post('/users', async (req, res) => {
    const user = await User.create(req.body);
    res.json(user);
});

module.exports = router;
"""
    
    # Create symbol info
    symbol_info = SymbolInfo(
        imports=[
            ImportInfo(
                module="express",
                imported_symbols=[],
                line_number=1
            )
        ]
    )
    
    # Detect patterns
    detector = APIPatternDetector()
    patterns = detector.detect(symbol_info, express_code, "src/routes/users.js")
    
    print(f"\nDetected {len(patterns)} API patterns:\n")
    for pattern in patterns:
        print(f"Pattern Type: {pattern.pattern_type}")
        print(f"Confidence: {pattern.confidence:.2f}")
        print(f"Evidence:")
        for evidence in pattern.evidence:
            print(f"  - {evidence}")
        print(f"Metadata: {pattern.metadata}")
        print()


def example_database_detection():
    """Example: Detect database ORM patterns."""
    print("=" * 60)
    print("Example 3: Database ORM Detection")
    print("=" * 60)
    
    # Create sample SQLAlchemy model code
    sqlalchemy_code = """
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100))
    posts = relationship('Post', back_populates='author')

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    author_id = Column(Integer, ForeignKey('users.id'))
    author = relationship('User', back_populates='posts')
"""
    
    # Create symbol info
    from src.analysis.symbol_extractor import ClassInfo
    
    symbol_info = SymbolInfo(
        classes=[
            ClassInfo(
                name="User",
                base_classes=["Base"],
                start_line=7,
                end_line=13
            ),
            ClassInfo(
                name="Post",
                base_classes=["Base"],
                start_line=15,
                end_line=21
            )
        ],
        imports=[
            ImportInfo(
                module="sqlalchemy",
                imported_symbols=["Column", "Integer", "String", "ForeignKey"],
                line_number=1
            )
        ]
    )
    
    # Detect patterns
    detector = DatabasePatternDetector()
    patterns = detector.detect(symbol_info, sqlalchemy_code, "src/models/user.py")
    
    print(f"\nDetected {len(patterns)} database patterns:\n")
    for pattern in patterns:
        print(f"Pattern Type: {pattern.pattern_type}")
        print(f"Confidence: {pattern.confidence:.2f}")
        print(f"Evidence:")
        for evidence in pattern.evidence:
            print(f"  - {evidence}")
        print(f"Metadata: {pattern.metadata}")
        print()


def example_auth_detection():
    """Example: Detect authentication patterns."""
    print("=" * 60)
    print("Example 4: Authentication Pattern Detection")
    print("=" * 60)
    
    # Create sample JWT authentication code
    jwt_code = """
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
"""
    
    # Create symbol info
    symbol_info = SymbolInfo(
        functions=[
            FunctionInfo(
                name="create_access_token",
                parameters=["data"],
                start_line=8,
                end_line=13
            ),
            FunctionInfo(
                name="verify_token",
                parameters=["token"],
                start_line=15,
                end_line=20
            )
        ],
        imports=[
            ImportInfo(
                module="jwt",
                imported_symbols=[],
                line_number=1
            )
        ]
    )
    
    # Detect patterns
    detector = AuthPatternDetector()
    patterns = detector.detect(symbol_info, jwt_code, "src/auth/jwt.py")
    
    print(f"\nDetected {len(patterns)} authentication patterns:\n")
    for pattern in patterns:
        print(f"Pattern Type: {pattern.pattern_type}")
        print(f"Confidence: {pattern.confidence:.2f}")
        print(f"Evidence:")
        for evidence in pattern.evidence:
            print(f"  - {evidence}")
        print(f"Metadata: {pattern.metadata}")
        print()


def example_pattern_detector_orchestration():
    """Example: Using PatternDetector to orchestrate multiple detectors."""
    print("=" * 60)
    print("Example 5: Pattern Detector Orchestration")
    print("=" * 60)
    
    # Create a pattern detector with all detectors
    pattern_detector = PatternDetector()
    
    # Register all detectors
    pattern_detector.register_detector(ReactPatternDetector())
    pattern_detector.register_detector(APIPatternDetector())
    pattern_detector.register_detector(DatabasePatternDetector())
    pattern_detector.register_detector(AuthPatternDetector())
    
    print(f"\nRegistered {len(pattern_detector.detectors)} pattern detectors:")
    for detector in pattern_detector.detectors:
        print(f"  - {detector.__class__.__name__}")
    
    # Example: Detect patterns in a file with multiple patterns
    mixed_code = """
import jwt
from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))

def create_token(user_id: int):
    return jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
"""
    
    from src.analysis.symbol_extractor import ClassInfo
    
    symbol_info = SymbolInfo(
        classes=[
            ClassInfo(name="User", base_classes=["Base"], start_line=9, end_line=12)
        ],
        functions=[
            FunctionInfo(name="create_token", parameters=["user_id"], start_line=14, end_line=15),
            FunctionInfo(name="get_user", parameters=["user_id"], start_line=17, end_line=18, decorators=["@app.get"])
        ],
        imports=[
            ImportInfo(module="jwt", line_number=1),
            ImportInfo(module="fastapi", imported_symbols=["FastAPI", "Depends"], line_number=2),
            ImportInfo(module="sqlalchemy", imported_symbols=["Column", "Integer", "String"], line_number=3)
        ]
    )
    
    # Detect all patterns
    all_patterns = pattern_detector.detect_patterns_in_file(
        symbol_info, mixed_code, "src/api/users.py"
    )
    
    print(f"\n\nDetected {len(all_patterns)} total patterns in file:\n")
    for pattern in all_patterns:
        print(f"  - {pattern.pattern_type} (confidence: {pattern.confidence:.2f})")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Pattern Detector Examples")
    print("=" * 60 + "\n")
    
    example_react_detection()
    example_api_detection()
    example_database_detection()
    example_auth_detection()
    example_pattern_detector_orchestration()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")
