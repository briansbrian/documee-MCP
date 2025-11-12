"""Test Task 8: MCP Tools for Course Generator

This test verifies that the three MCP tools are properly implemented:
1. export_course - exports a course from analyzed codebase
2. generate_lesson_outline - generates lesson outline from a file
3. create_exercise - creates an exercise for a pattern type
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.server import (
    export_course,
    generate_lesson_outline,
    create_exercise,
    app_context,
    AppContext
)
from src.cache.unified_cache import UnifiedCacheManager
from src.config.settings import Settings
from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig


async def setup_context():
    """Setup app context for testing."""
    global app_context
    
    # Load configuration
    config = Settings()
    
    # Create cache manager
    cache_manager = UnifiedCacheManager(
        max_memory_mb=config.cache_max_memory_mb,
        sqlite_path="cache_db/test_task8.db",
        redis_url=config.redis_url
    )
    
    # Initialize cache
    await cache_manager.initialize()
    
    # Create analysis engine
    analysis_config = AnalysisConfig()
    analysis_engine = AnalysisEngine(cache_manager, analysis_config)
    
    # Set app context
    import src.server as server_module
    server_module.app_context = AppContext(
        cache_manager=cache_manager,
        config=config,
        analysis_engine=analysis_engine
    )
    
    return cache_manager


async def test_generate_lesson_outline():
    """Test generate_lesson_outline tool."""
    print("\n" + "="*80)
    print("TEST 1: generate_lesson_outline")
    print("="*80)
    
    # Test with a real file from the project
    test_file = "src/course/structure_generator.py"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        result = await generate_lesson_outline(file_path=test_file)
        
        # Verify result structure
        required_keys = [
            'title', 'file_path', 'learning_objectives', 'key_concepts',
            'difficulty', 'estimated_duration_minutes', 'code_examples',
            'suggested_exercises', 'patterns', 'teaching_value_score'
        ]
        
        missing_keys = [key for key in required_keys if key not in result]
        if missing_keys:
            print(f"❌ Missing keys in result: {missing_keys}")
            return False
        
        print(f"✅ Lesson outline generated successfully")
        print(f"   Title: {result['title']}")
        print(f"   Difficulty: {result['difficulty']}")
        print(f"   Duration: {result['estimated_duration_minutes']} minutes")
        print(f"   Learning objectives: {len(result['learning_objectives'])}")
        print(f"   Key concepts: {len(result['key_concepts'])}")
        print(f"   Code examples: {len(result['code_examples'])}")
        print(f"   Suggested exercises: {len(result['suggested_exercises'])}")
        print(f"   Teaching value: {result['teaching_value_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_create_exercise():
    """Test create_exercise tool."""
    print("\n" + "="*80)
    print("TEST 2: create_exercise")
    print("="*80)
    
    # Test creating a generic exercise
    pattern_type = "react_component"
    difficulty = "intermediate"
    
    try:
        result = await create_exercise(
            pattern_type=pattern_type,
            difficulty=difficulty
        )
        
        # Verify result structure
        required_keys = [
            'exercise_id', 'title', 'description', 'difficulty',
            'estimated_minutes', 'instructions', 'starter_code',
            'solution_code', 'hints', 'test_cases', 'learning_objectives',
            'pattern_type'
        ]
        
        missing_keys = [key for key in required_keys if key not in result]
        if missing_keys:
            print(f"❌ Missing keys in result: {missing_keys}")
            return False
        
        print(f"✅ Exercise created successfully")
        print(f"   Title: {result['title']}")
        print(f"   Pattern: {result['pattern_type']}")
        print(f"   Difficulty: {result['difficulty']}")
        print(f"   Estimated time: {result['estimated_minutes']} minutes")
        print(f"   Instructions: {len(result['instructions'])} steps")
        print(f"   Hints: {len(result['hints'])}")
        print(f"   Test cases: {len(result['test_cases'])}")
        print(f"   Learning objectives: {len(result['learning_objectives'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_export_course_error_handling():
    """Test export_course error handling."""
    print("\n" + "="*80)
    print("TEST 3: export_course error handling")
    print("="*80)
    
    # Test with non-existent codebase_id
    fake_codebase_id = "nonexistent123"
    
    try:
        result = await export_course(
            codebase_id=fake_codebase_id,
            format="json"
        )
        print(f"❌ Should have raised ValueError for non-existent codebase")
        return False
        
    except ValueError as e:
        if "not analyzed" in str(e).lower():
            print(f"✅ Correct error handling: {e}")
            return True
        else:
            print(f"❌ Wrong error message: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_create_exercise_validation():
    """Test create_exercise input validation."""
    print("\n" + "="*80)
    print("TEST 4: create_exercise input validation")
    print("="*80)
    
    # Test with invalid difficulty
    try:
        result = await create_exercise(
            pattern_type="api_route",
            difficulty="invalid_difficulty"
        )
        print(f"❌ Should have raised ValueError for invalid difficulty")
        return False
        
    except ValueError as e:
        if "invalid difficulty" in str(e).lower():
            print(f"✅ Correct validation: {e}")
            return True
        else:
            print(f"❌ Wrong error message: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("TASK 8: MCP TOOLS VERIFICATION")
    print("="*80)
    
    cache_manager = None
    
    try:
        # Setup
        cache_manager = await setup_context()
        print("✅ App context initialized")
        
        # Run tests
        results = []
        
        results.append(await test_generate_lesson_outline())
        results.append(await test_create_exercise())
        results.append(await test_export_course_error_handling())
        results.append(await test_create_exercise_validation())
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(results)
        total = len(results)
        
        print(f"Passed: {passed}/{total}")
        
        if passed == total:
            print("✅ ALL TESTS PASSED")
            return 0
        else:
            print(f"❌ {total - passed} TEST(S) FAILED")
            return 1
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        if cache_manager:
            await cache_manager.close()
            print("\n✅ Cache manager closed")


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
