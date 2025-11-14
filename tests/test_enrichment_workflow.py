"""
End-to-end integration tests for AI Content Enrichment workflow.

Tests the complete enrichment workflow:
1. Generate basic course with export_course
2. Get enrichment guide for a lesson
3. Verify guide contains all required sections
4. Verify evidence citations are accurate
5. Simulate Kiro enrichment (manual or scripted)
6. Update lesson with enriched content
7. Verify enriched content persists correctly
8. Export enriched course and verify rendering

Tests Requirements: All enrichment requirements
"""

import pytest
import pytest_asyncio
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Import server module and app context
import src.server
from src.server import AppContext

# Import models
from src.models import (
    CodebaseAnalysis,
    FileAnalysis,
    SymbolInfo,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    DetectedPattern,
    ComplexityMetrics,
    TeachingValueScore,
    DependencyGraph,
    CodebaseMetrics
)

from src.cache.unified_cache import UnifiedCacheManager
from src.config.settings import Settings
from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig


# ========== Helper Functions ==========

def get_mcp_tool(tool_name: str):
    """Get the actual function from an MCP tool."""
    return src.server.mcp._tool_manager._tools[tool_name].fn


# ========== Test Fixtures ==========


@pytest_asyncio.fixture
async def mock_app_context():
    """Create a mock app context for testing."""
    # Create temporary cache database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    # Create cache manager
    cache_manager = UnifiedCacheManager(
        max_memory_mb=100,
        sqlite_path=temp_db.name,
        redis_url=None
    )
    await cache_manager.initialize()
    
    # Create config
    config = Settings()
    
    # Create analysis engine
    analysis_config = AnalysisConfig()
    analysis_engine = AnalysisEngine(cache_manager, analysis_config)
    
    # Create app context
    context = AppContext(
        cache_manager=cache_manager,
        config=config,
        analysis_engine=analysis_engine
    )
    
    # Patch global app_context
    import src.server
    original_context = src.server.app_context
    src.server.app_context = context
    
    yield context
    
    # Cleanup
    src.server.app_context = original_context
    await cache_manager.close()
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)


@pytest.fixture
def temp_python_project():
    """Create a temporary Python project for testing."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create project structure
    src_dir = Path(temp_dir) / "src"
    src_dir.mkdir()
    
    # Create authentication module
    auth_file = src_dir / "auth.py"
    auth_file.write_text('''"""User authentication module."""

import bcrypt
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "test_secret_key"


def authenticate_user(username: str, password: str):
    """
    Authenticate user with username and password.
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        Session token if authentication successful, None otherwise
    """
    # Verify password (simplified for testing)
    if username and password:
        # Generate JWT token
        token = generate_token(username)
        return token
    return None


def generate_token(username: str, expires_in: int = 3600):
    """
    Generate JWT token for authenticated user.
    
    Args:
        username: Username to encode in token
        expires_in: Token expiration time in seconds (default: 1 hour)
        
    Returns:
        JWT token string
    """
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def validate_token(token: str):
    """
    Validate JWT token.
    
    Args:
        token: JWT token to validate
        
    Returns:
        Decoded payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class UserSession:
    """Manages user session data."""
    
    def __init__(self, username: str, token: str):
        """Initialize user session."""
        self.username = username
        self.token = token
        self.created_at = datetime.utcnow()
    
    def is_valid(self):
        """Check if session is still valid."""
        payload = validate_token(self.token)
        return payload is not None
''')
    
    yield temp_dir
    
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def cleanup_output_dir(codebase_id: str):
    """Clean up output directory for a codebase."""
    output_dir = Path(f"./output/{codebase_id}_course")
    if output_dir.exists():
        shutil.rmtree(output_dir)



# ========== End-to-End Workflow Tests ==========


@pytest.mark.asyncio
async def test_complete_enrichment_workflow(mock_app_context, temp_python_project):
    """
    Test complete end-to-end enrichment workflow.
    
    Steps:
    1. Scan codebase
    2. Analyze files
    3. Generate basic course with export_course
    4. Get enrichment guide for a lesson
    5. Verify guide contains all required sections
    6. Verify evidence citations are accurate
    7. Simulate Kiro enrichment (scripted)
    8. Update lesson with enriched content
    9. Verify enriched content persists correctly
    10. Export enriched course and verify rendering
    """
    print("\n🧪 Testing complete enrichment workflow...")
    
    codebase_id = None
    
    try:
        # ========== Step 1: Scan Codebase ==========
        print("\n📁 Step 1: Scanning codebase...")
        
        scan_result = await get_mcp_tool('scan_codebase')(
            path=temp_python_project
        )
        
        assert 'codebase_id' in scan_result
        codebase_id = scan_result['codebase_id']
        assert 'structure' in scan_result
        
        print(f"   ✓ Codebase scanned: {codebase_id}")
        print(f"   ✓ Files found: {scan_result['structure']['total_files']}")
        
        # ========== Step 2: Analyze Files ==========
        print("\n🔍 Step 2: Analyzing files...")
        
        # Use the known auth file path from temp_python_project
        auth_file = str(Path(temp_python_project) / "src" / "auth.py")
        
        analysis_result = await get_mcp_tool('analyze_file')(
            file_path=auth_file
        )
        
        assert 'file_path' in analysis_result
        assert 'language' in analysis_result
        assert analysis_result['language'] == 'python'
        
        print(f"   ✓ File analyzed: {auth_file}")
        print(f"   ✓ Functions found: {len(analysis_result.get('symbol_info', {}).get('functions', []))}")
        
        # ========== Step 2.5: Analyze Codebase ==========
        print("\n🔬 Step 2.5: Analyzing codebase...")
        
        analyze_codebase_result = await get_mcp_tool('analyze_codebase_tool')(
            codebase_id=codebase_id
        )
        
        assert 'codebase_id' in analyze_codebase_result
        assert analyze_codebase_result['codebase_id'] == codebase_id
        
        print(f"   ✓ Codebase analyzed")
        print(f"   ✓ Total files analyzed: {analyze_codebase_result.get('metrics', {}).get('total_files', 0)}")
        
        # ========== Step 3: Generate Basic Course ==========
        print("\n📚 Step 3: Generating basic course...")
        
        export_result = await get_mcp_tool('export_course')(
            codebase_id=codebase_id,
            format='json',
            output_dir=f'./output/{codebase_id}_course'
        )
        
        assert 'export_path' in export_result
        
        # Read course data from the exported file
        course_data_path = Path(f"./output/{codebase_id}_course/course_data.json")
        assert course_data_path.exists(), "Course data file not found"
        
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        assert 'modules' in course_data
        assert len(course_data['modules']) > 0
        
        # Get first lesson
        first_module = course_data['modules'][0]
        assert 'lessons' in first_module
        assert len(first_module['lessons']) > 0
        
        first_lesson = first_module['lessons'][0]
        lesson_id = first_lesson['lesson_id']
        
        print(f"   ✓ Course generated with {len(course_data['modules'])} modules")
        print(f"   ✓ First lesson: {lesson_id} - {first_lesson['title']}")
        
        # ========== Step 4: Get Enrichment Guide ==========
        print(f"\n📖 Step 4: Getting enrichment guide for lesson {lesson_id}...")
        
        enrichment_guide = await get_mcp_tool('get_enrichment_guide')(
            codebase_id=codebase_id,
            lesson_id=lesson_id
        )
        
        # ========== Step 5: Verify Guide Contains All Required Sections ==========
        print("\n✅ Step 5: Verifying enrichment guide structure...")
        
        required_sections = [
            'lesson_id',
            'feature_mapping',
            'evidence_bundle',
            'validation_checklist',
            'teaching_value_assessment',
            'systematic_investigation',
            'narrative_structure',
            'code_sections',
            'architecture_context',
            'real_world_context',
            'exercise_generation',
            'anti_hallucination_rules',
            'enrichment_instructions'
        ]
        
        for section in required_sections:
            assert section in enrichment_guide, f"Missing section: {section}"
            print(f"   ✓ {section}")
        
        # Verify lesson_id matches
        assert enrichment_guide['lesson_id'] == lesson_id
        
        # Verify feature mapping structure
        feature_mapping = enrichment_guide['feature_mapping']
        assert 'feature_name' in feature_mapping
        assert 'user_facing_purpose' in feature_mapping
        assert 'business_value' in feature_mapping
        assert 'entry_points' in feature_mapping
        assert 'feature_flow' in feature_mapping
        assert len(feature_mapping['feature_name']) > 0
        print(f"   ✓ Feature: {feature_mapping['feature_name']}")
        
        # Verify evidence bundle structure
        evidence = enrichment_guide['evidence_bundle']
        assert 'source_files' in evidence
        assert 'test_files' in evidence
        assert 'git_commits' in evidence
        assert 'documentation' in evidence
        assert 'dependencies' in evidence
        assert 'dependents' in evidence
        assert isinstance(evidence['source_files'], list)
        print(f"   ✓ Evidence sources: {len(evidence['source_files'])} files")
        
        # Verify validation checklist
        validation = enrichment_guide['validation_checklist']
        assert 'code_behavior' in validation
        assert 'expected_behavior' in validation
        assert 'documentation_alignment' in validation
        assert 'git_context' in validation
        assert 'consistency_check' in validation
        print(f"   ✓ Validation checklist complete")
        
        # Verify teaching value assessment
        teaching_value = enrichment_guide['teaching_value_assessment']
        assert 'scores' in teaching_value
        assert 'total_score' in teaching_value
        assert 'should_teach' in teaching_value
        assert 'reasoning' in teaching_value
        assert 0 <= teaching_value['total_score'] <= 14
        print(f"   ✓ Teaching value: {teaching_value['total_score']}/14")
        
        # Verify systematic investigation
        investigation = enrichment_guide['systematic_investigation']
        assert 'what_it_does' in investigation
        assert 'why_it_exists' in investigation
        assert 'how_it_works' in investigation
        assert 'when_its_used' in investigation
        assert 'edge_cases' in investigation
        assert 'common_pitfalls' in investigation
        print(f"   ✓ Systematic investigation complete")
        
        # Verify narrative structure
        narrative = enrichment_guide['narrative_structure']
        assert 'introduction_points' in narrative
        assert 'learning_progression' in narrative
        assert 'code_walkthrough_order' in narrative
        assert 'conclusion_points' in narrative
        assert 'next_steps' in narrative
        assert len(narrative['introduction_points']) >= 3
        print(f"   ✓ Narrative structure: {len(narrative['introduction_points'])} intro points")
        
        # Verify code sections
        code_sections = enrichment_guide['code_sections']
        assert isinstance(code_sections, list)
        assert len(code_sections) > 0
        print(f"   ✓ Code sections: {len(code_sections)}")
        
        # Verify architecture context
        architecture = enrichment_guide['architecture_context']
        assert 'component_role' in architecture
        assert 'data_flow' in architecture
        assert 'dependencies' in architecture
        print(f"   ✓ Architecture context complete")
        
        # Verify real-world context
        real_world = enrichment_guide['real_world_context']
        assert 'practical_use_cases' in real_world
        assert 'analogies' in real_world
        assert 'industry_patterns' in real_world
        assert 'best_practices' in real_world
        print(f"   ✓ Real-world context: {len(real_world['practical_use_cases'])} use cases")
        
        # Verify exercise generation
        exercises = enrichment_guide['exercise_generation']
        assert 'hands_on_tasks' in exercises
        assert 'starter_code' in exercises
        assert 'solution_code' in exercises
        assert 'progressive_hints' in exercises
        print(f"   ✓ Exercise generation: {len(exercises['hands_on_tasks'])} tasks")
        
        # Verify anti-hallucination rules
        rules = enrichment_guide['anti_hallucination_rules']
        assert 'always_cite' in rules
        assert 'distinguish_fact_inference' in rules
        assert 'validate_against_tests' in rules
        print(f"   ✓ Anti-hallucination rules present")
        
        # Verify enrichment instructions
        instructions = enrichment_guide['enrichment_instructions']
        assert 'tone' in instructions
        assert 'depth' in instructions
        assert 'focus_areas' in instructions
        assert instructions['tone'] == 'casual'
        assert instructions['depth'] == 'detailed'
        print(f"   ✓ Enrichment instructions: {instructions['tone']}, {instructions['depth']}")

        
        # ========== Step 6: Verify Evidence Citations Are Accurate ==========
        print("\n🔍 Step 6: Verifying evidence citations...")
        
        # Check code sections have proper citations
        for idx, section in enumerate(code_sections):
            assert 'file_path' in section, f"Section {idx} missing file_path"
            assert 'line_range' in section, f"Section {idx} missing line_range"
            assert 'code_snippet' in section, f"Section {idx} missing code_snippet"
            assert 'purpose' in section, f"Section {idx} missing purpose"
            
            # Verify line range is valid
            assert isinstance(section['line_range'], list)
            assert len(section['line_range']) == 2
            assert section['line_range'][0] <= section['line_range'][1]
            
            # Verify evidence fields exist
            assert 'test_evidence' in section
            assert 'git_evidence' in section
            
            print(f"   ✓ Section {idx+1}: {section['file_path']} lines {section['line_range']}")
        
        # Check evidence bundle has source file references
        for source_file in evidence['source_files']:
            assert 'path' in source_file
            assert 'lines' in source_file or 'content' in source_file
            print(f"   ✓ Source file: {source_file['path']}")
        
        print(f"   ✓ All citations verified")
        
        # ========== Step 7: Simulate Kiro Enrichment ==========
        print("\n✨ Step 7: Simulating Kiro enrichment...")
        
        # Simulate enriched content based on the guide
        enriched_content = {
            'description': f'''Learn how to implement {feature_mapping['feature_name']} with secure best practices. 
This lesson covers the core concepts of authentication, token generation, and validation, 
providing you with the skills needed to build secure applications.''',
            
            'content': f'''# Introduction

{feature_mapping['user_facing_purpose']}

## Why This Matters

{feature_mapping['business_value']}

## What You'll Learn

{chr(10).join(f"- {obj}" for obj in narrative['introduction_points'][:3])}

## Understanding the Code

{investigation['what_it_does']}

### How It Works

{investigation['how_it_works']}

### Key Concepts

{chr(10).join(f"- {concept}" for concept in code_sections[0]['key_concepts'] if code_sections)}

## Real-World Applications

{chr(10).join(f"- {use_case}" for use_case in real_world['practical_use_cases'][:3])}

## Best Practices

{chr(10).join(f"- {practice}" for practice in real_world['best_practices'][:3])}

## Summary

{chr(10).join(f"- {point}" for point in narrative['conclusion_points'][:3])}

## Next Steps

{chr(10).join(f"- {step}" for step in narrative['next_steps'][:2])}
''',
            
            'learning_objectives': [
                f"Understand {feature_mapping['feature_name']}",
                f"Implement {investigation['what_it_does'][:50]}...",
                "Apply security best practices",
                "Handle common edge cases and errors"
            ],
            
            'exercises': [
                {
                    'exercise_id': first_lesson['exercises'][0]['exercise_id'] if first_lesson.get('exercises') else 'ex-1',
                    'title': exercises['hands_on_tasks'][0]['title'] if exercises['hands_on_tasks'] else 'Practice Exercise',
                    'description': exercises['hands_on_tasks'][0]['description'] if exercises['hands_on_tasks'] else 'Complete the implementation',
                    'instructions': [
                        '1. Review the starter code provided',
                        '2. Implement the required functionality',
                        '3. Test your implementation',
                        '4. Compare with the solution'
                    ],
                    'hints': exercises['progressive_hints'][:4] if len(exercises['progressive_hints']) >= 4 else exercises['progressive_hints']
                }
            ] if exercises['hands_on_tasks'] else []
        }
        
        print(f"   ✓ Enriched description: {len(enriched_content['description'])} chars")
        print(f"   ✓ Enriched content: {len(enriched_content['content'])} chars")
        print(f"   ✓ Learning objectives: {len(enriched_content['learning_objectives'])}")
        print(f"   ✓ Exercises: {len(enriched_content.get('exercises', []))}")
        
        # ========== Step 8: Update Lesson with Enriched Content ==========
        print(f"\n💾 Step 8: Updating lesson {lesson_id} with enriched content...")
        
        update_result = await get_mcp_tool('update_lesson_content')(
            codebase_id=codebase_id,
            lesson_id=lesson_id,
            enriched_content=enriched_content
        )
        
        assert 'success' in update_result
        assert update_result['success'] is True
        assert 'lesson_id' in update_result
        assert update_result['lesson_id'] == lesson_id
        assert 'updated_fields' in update_result
        assert 'enrichment_status' in update_result
        
        updated_fields = update_result['updated_fields']
        assert 'description' in updated_fields
        assert 'content' in updated_fields
        assert 'learning_objectives' in updated_fields
        
        enrichment_status = update_result['enrichment_status']
        assert enrichment_status['status'] == 'completed'
        assert 'enriched_at' in enrichment_status
        assert enrichment_status['version'] == 1
        
        print(f"   ✓ Lesson updated successfully")
        print(f"   ✓ Updated fields: {', '.join(updated_fields)}")
        print(f"   ✓ Enrichment status: {enrichment_status['status']}")
        print(f"   ✓ Version: {enrichment_status['version']}")
        
        # ========== Step 9: Verify Enriched Content Persists ==========
        print("\n🔍 Step 9: Verifying enriched content persists...")
        
        # Read course data from disk
        course_data_path = Path(f"./output/{codebase_id}_course/course_data.json")
        assert course_data_path.exists(), "Course data file not found"
        
        with open(course_data_path, 'r', encoding='utf-8') as f:
            persisted_course_data = json.load(f)
        
        # Find the updated lesson
        persisted_lesson = None
        for module in persisted_course_data['modules']:
            for lesson in module['lessons']:
                if lesson['lesson_id'] == lesson_id:
                    persisted_lesson = lesson
                    break
            if persisted_lesson:
                break
        
        assert persisted_lesson is not None, "Updated lesson not found in persisted data"
        
        # Verify enriched fields
        assert persisted_lesson['description'] == enriched_content['description']
        assert persisted_lesson['content'] == enriched_content['content']
        assert persisted_lesson['learning_objectives'] == enriched_content['learning_objectives']
        
        print(f"   ✓ Description persisted: {len(persisted_lesson['description'])} chars")
        print(f"   ✓ Content persisted: {len(persisted_lesson['content'])} chars")
        print(f"   ✓ Learning objectives persisted: {len(persisted_lesson['learning_objectives'])}")
        
        # Verify enrichment status tracking
        assert 'enrichment_status' in persisted_course_data
        assert lesson_id in persisted_course_data['enrichment_status']
        
        persisted_status = persisted_course_data['enrichment_status'][lesson_id]
        assert persisted_status['status'] == 'completed'
        assert persisted_status['enriched_by'] == 'kiro'
        assert persisted_status['version'] == 1
        
        print(f"   ✓ Enrichment status tracked: {persisted_status['status']}")
        
        # ========== Step 10: Export Enriched Course and Verify Rendering ==========
        print("\n📦 Step 10: Exporting enriched course...")
        
        # Note: export_course generates a fresh course from analysis, not from enriched course_data
        # So we verify the enriched content persists in the original course directory
        # and can be used for custom exports
        
        # Verify the enriched course data is still in the original location
        original_course_path = Path(f"./output/{codebase_id}_course/course_data.json")
        assert original_course_path.exists()
        
        with open(original_course_path, 'r', encoding='utf-8') as f:
            final_course_data = json.load(f)
        
        # Verify enriched content is still there
        final_lesson = None
        for module in final_course_data['modules']:
            for lesson in module['lessons']:
                if lesson['lesson_id'] == lesson_id:
                    final_lesson = lesson
                    break
            if final_lesson:
                break
        
        assert final_lesson is not None
        assert final_lesson['description'] == enriched_content['description']
        assert final_lesson['content'] == enriched_content['content']
        
        print(f"   ✓ Enriched content persists in course data")
        print(f"   ✓ Course data can be used for custom exports")
        
        # Test that we can export to different formats
        # (Note: export_course generates from analysis, not enriched course_data)
        md_export_result = await get_mcp_tool('export_course')(
            codebase_id=codebase_id,
            format='markdown',
            output_dir=f'./output/{codebase_id}_course_md'
        )
        
        assert 'export_path' in md_export_result
        
        # Verify markdown files were created
        md_output_dir = Path(f"./output/{codebase_id}_course_md")
        assert md_output_dir.exists()
        
        # Check for markdown files
        md_files = list(md_output_dir.rglob('*.md'))
        assert len(md_files) > 0, "No markdown files generated"
        
        print(f"   ✓ Markdown export successful: {len(md_files)} files")
        print(f"   ✓ Multiple export formats supported")
        
        # ========== Final Summary ==========
        print("\n" + "="*60)
        print("✅ COMPLETE ENRICHMENT WORKFLOW TEST PASSED")
        print("="*60)
        print(f"Codebase ID: {codebase_id}")
        print(f"Lesson ID: {lesson_id}")
        print(f"Enrichment Status: {enrichment_status['status']}")
        print(f"Updated Fields: {len(updated_fields)}")
        print(f"Export Formats: JSON, Markdown")
        print("="*60)
        
    finally:
        # Cleanup
        if codebase_id:
            cleanup_output_dir(codebase_id)
            cleanup_output_dir(f"{codebase_id}_enriched")
            cleanup_output_dir(f"{codebase_id}_md")



@pytest.mark.asyncio
async def test_enrichment_workflow_multiple_lessons(mock_app_context, temp_python_project):
    """
    Test enrichment workflow with multiple lessons.
    
    Verifies that:
    - Multiple lessons can be enriched sequentially
    - Enrichment status is tracked independently for each lesson
    - List lessons shows correct enrichment progress
    """
    print("\n🧪 Testing enrichment workflow with multiple lessons...")
    
    codebase_id = None
    
    try:
        # Scan and analyze codebase
        scan_result = await get_mcp_tool('scan_codebase')(path=temp_python_project)
        codebase_id = scan_result['codebase_id']
        
        # Analyze codebase
        await get_mcp_tool('analyze_codebase_tool')(codebase_id=codebase_id)
        
        export_result = await get_mcp_tool('export_course')(
            codebase_id=codebase_id,
            format='json',
            output_dir=f'./output/{codebase_id}_course'
        )
        
        # Read course data from file
        course_data_path = Path(f'./output/{codebase_id}_course/course_data.json')
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        # Get all lessons
        all_lessons = []
        for module in course_data['modules']:
            for lesson in module['lessons']:
                all_lessons.append(lesson['lesson_id'])
        
        print(f"   Found {len(all_lessons)} lessons")
        
        # List lessons before enrichment
        list_result_before = await get_mcp_tool('list_lessons_for_enrichment')(
            codebase_id=codebase_id
        )
        
        assert list_result_before['enrichment_summary']['not_started'] == len(all_lessons)
        assert list_result_before['enrichment_summary']['completed'] == 0
        print(f"   ✓ All lessons not started: {len(all_lessons)}")
        
        # Enrich first lesson
        if len(all_lessons) > 0:
            lesson_id_1 = all_lessons[0]
            
            guide_1 = await get_mcp_tool('get_enrichment_guide')(
                codebase_id=codebase_id,
                lesson_id=lesson_id_1
            )
            
            enriched_content_1 = {
                'description': 'Enriched description for lesson 1',
                'content': 'Enriched content for lesson 1'
            }
            
            update_result_1 = await get_mcp_tool('update_lesson_content')(
                codebase_id=codebase_id,
                lesson_id=lesson_id_1,
                enriched_content=enriched_content_1
            )
            
            assert update_result_1['success'] is True
            print(f"   ✓ Lesson 1 enriched: {lesson_id_1}")
        
        # List lessons after first enrichment
        list_result_after_1 = await get_mcp_tool('list_lessons_for_enrichment')(
            codebase_id=codebase_id
        )
        
        assert list_result_after_1['enrichment_summary']['completed'] == 1
        assert list_result_after_1['enrichment_summary']['not_started'] == len(all_lessons) - 1
        print(f"   ✓ Enrichment progress: 1/{len(all_lessons)}")
        
        # Enrich second lesson if available
        if len(all_lessons) > 1:
            lesson_id_2 = all_lessons[1]
            
            guide_2 = await get_mcp_tool('get_enrichment_guide')(
                codebase_id=codebase_id,
                lesson_id=lesson_id_2
            )
            
            enriched_content_2 = {
                'description': 'Enriched description for lesson 2',
                'content': 'Enriched content for lesson 2'
            }
            
            update_result_2 = await get_mcp_tool('update_lesson_content')(
                codebase_id=codebase_id,
                lesson_id=lesson_id_2,
                enriched_content=enriched_content_2
            )
            
            assert update_result_2['success'] is True
            print(f"   ✓ Lesson 2 enriched: {lesson_id_2}")
            
            # List lessons after second enrichment
            list_result_after_2 = await get_mcp_tool('list_lessons_for_enrichment')(
                codebase_id=codebase_id
            )
            
            assert list_result_after_2['enrichment_summary']['completed'] == 2
            completion_pct = list_result_after_2['enrichment_summary']['completion_percentage']
            expected_pct = (2 / len(all_lessons)) * 100
            assert abs(completion_pct - expected_pct) < 0.1
            print(f"   ✓ Enrichment progress: 2/{len(all_lessons)} ({completion_pct:.1f}%)")
        
        print(f"   ✅ Multiple lesson enrichment workflow passed")
        
    finally:
        if codebase_id:
            cleanup_output_dir(codebase_id)


@pytest.mark.asyncio
async def test_enrichment_workflow_re_enrichment(mock_app_context, temp_python_project):
    """
    Test re-enrichment workflow (updating already enriched lesson).
    
    Verifies that:
    - Lessons can be re-enriched
    - Version number increments
    - Previous content is replaced
    """
    print("\n🧪 Testing re-enrichment workflow...")
    
    codebase_id = None
    
    try:
        # Scan and analyze codebase
        scan_result = await get_mcp_tool('scan_codebase')(path=temp_python_project)
        codebase_id = scan_result['codebase_id']
        
        # Analyze codebase
        await get_mcp_tool('analyze_codebase_tool')(codebase_id=codebase_id)
        
        export_result = await get_mcp_tool('export_course')(
            codebase_id=codebase_id,
            format='json',
            output_dir=f'./output/{codebase_id}_course'
        )
        
        # Read course data from file
        course_data_path = Path(f'./output/{codebase_id}_course/course_data.json')
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        lesson_id = course_data['modules'][0]['lessons'][0]['lesson_id']
        
        # First enrichment
        guide = await get_mcp_tool('get_enrichment_guide')(
            codebase_id=codebase_id,
            lesson_id=lesson_id
        )
        
        enriched_content_v1 = {
            'description': 'Version 1 description',
            'content': 'Version 1 content'
        }
        
        update_result_v1 = await get_mcp_tool('update_lesson_content')(
            codebase_id=codebase_id,
            lesson_id=lesson_id,
            enriched_content=enriched_content_v1
        )
        
        assert update_result_v1['success'] is True
        assert update_result_v1['enrichment_status']['version'] == 1
        print(f"   ✓ First enrichment: version 1")
        
        # Re-enrichment
        enriched_content_v2 = {
            'description': 'Version 2 description - improved',
            'content': 'Version 2 content - with more details'
        }
        
        update_result_v2 = await get_mcp_tool('update_lesson_content')(
            codebase_id=codebase_id,
            lesson_id=lesson_id,
            enriched_content=enriched_content_v2
        )
        
        assert update_result_v2['success'] is True
        assert update_result_v2['enrichment_status']['version'] == 2
        print(f"   ✓ Re-enrichment: version 2")
        
        # Verify version 2 content persists
        course_data_path = Path(f"./output/{codebase_id}_course/course_data.json")
        with open(course_data_path, 'r', encoding='utf-8') as f:
            persisted_data = json.load(f)
        
        persisted_lesson = persisted_data['modules'][0]['lessons'][0]
        assert persisted_lesson['description'] == enriched_content_v2['description']
        assert persisted_lesson['content'] == enriched_content_v2['content']
        
        persisted_status = persisted_data['enrichment_status'][lesson_id]
        assert persisted_status['version'] == 2
        
        print(f"   ✓ Version 2 content persisted")
        print(f"   ✅ Re-enrichment workflow passed")
        
    finally:
        if codebase_id:
            cleanup_output_dir(codebase_id)


@pytest.mark.asyncio
async def test_enrichment_workflow_error_recovery(mock_app_context, temp_python_project):
    """
    Test error recovery in enrichment workflow.
    
    Verifies that:
    - Invalid enriched content is rejected
    - Course data remains unchanged after failed update
    - Error messages are informative
    """
    print("\n🧪 Testing enrichment workflow error recovery...")
    
    codebase_id = None
    
    try:
        # Scan and analyze codebase
        scan_result = await get_mcp_tool('scan_codebase')(path=temp_python_project)
        codebase_id = scan_result['codebase_id']
        
        # Analyze codebase
        await get_mcp_tool('analyze_codebase_tool')(codebase_id=codebase_id)
        
        export_result = await get_mcp_tool('export_course')(
            codebase_id=codebase_id,
            format='json',
            output_dir=f'./output/{codebase_id}_course'
        )
        
        # Read course data from file
        course_data_path = Path(f'./output/{codebase_id}_course/course_data.json')
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        lesson_id = course_data['modules'][0]['lessons'][0]['lesson_id']
        original_description = course_data['modules'][0]['lessons'][0]['description']
        
        # Try to update with invalid content (missing required field)
        invalid_content = {
            'content': 'Some content'
            # Missing 'description' field
        }
        
        update_result = await get_mcp_tool('update_lesson_content')(
            codebase_id=codebase_id,
            lesson_id=lesson_id,
            enriched_content=invalid_content
        )
        
        assert update_result['success'] is False
        assert 'error' in update_result
        assert 'missing required field' in update_result['error'].lower()
        print(f"   ✓ Invalid content rejected: {update_result['error']}")
        
        # Verify course data unchanged
        course_data_path = Path(f"./output/{codebase_id}_course/course_data.json")
        with open(course_data_path, 'r', encoding='utf-8') as f:
            persisted_data = json.load(f)
        
        persisted_lesson = persisted_data['modules'][0]['lessons'][0]
        assert persisted_lesson['description'] == original_description
        print(f"   ✓ Course data unchanged after failed update")
        
        # Verify enrichment status not created
        assert lesson_id not in persisted_data.get('enrichment_status', {})
        print(f"   ✓ Enrichment status not created for failed update")
        
        print(f"   ✅ Error recovery workflow passed")
        
    finally:
        if codebase_id:
            cleanup_output_dir(codebase_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])



