"""
Manual test for update_lesson_content MCP tool.

This script tests the update_lesson_content tool by:
1. Scanning a codebase
2. Analyzing the codebase
3. Exporting a course
4. Getting an enrichment guide for a lesson
5. Updating the lesson with enriched content

Run with: venv\\Scripts\\python.exe tests/test_update_lesson_content_manual.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cache.unified_cache import UnifiedCacheManager
from src.config.settings import Settings
from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig
from src.server import AppContext
import src.server


async def test_update_lesson_content():
    """Test the update_lesson_content tool."""
    print("=" * 80)
    print("Testing update_lesson_content MCP Tool")
    print("=" * 80)
    
    # Initialize app context
    print("\n1. Initializing app context...")
    cache_manager = UnifiedCacheManager(
        max_memory_mb=100,
        sqlite_path="cache_db/test_enrichment.db",
        redis_url=None
    )
    await cache_manager.initialize()
    
    config = Settings()
    analysis_config = AnalysisConfig()
    analysis_engine = AnalysisEngine(cache_manager, analysis_config)
    
    context = AppContext(
        cache_manager=cache_manager,
        config=config,
        analysis_engine=analysis_engine
    )
    
    # Set global app context
    src.server.app_context = context
    print("[OK] App context initialized")
    
    try:
        # Get MCP tools
        scan_tool = src.server.mcp._tool_manager._tools['scan_codebase'].fn
        analyze_tool = src.server.mcp._tool_manager._tools['analyze_codebase_tool'].fn
        export_tool = src.server.mcp._tool_manager._tools['export_course'].fn
        enrichment_tool = src.server.mcp._tool_manager._tools['get_enrichment_guide'].fn
        update_tool = src.server.mcp._tool_manager._tools['update_lesson_content'].fn
        
        # Step 1: Scan codebase
        print("\n2. Scanning codebase...")
        scan_result = await scan_tool(path=".", max_depth=3, use_cache=False)
        codebase_id = scan_result['codebase_id']
        print(f"[OK] Codebase scanned: {codebase_id}")
        print(f"  Total files: {scan_result['structure']['total_files']}")
        
        # Step 2: Analyze codebase
        print("\n3. Analyzing codebase...")
        analyze_result = await analyze_tool(
            codebase_id=codebase_id,
            incremental=False,
            use_cache=False
        )
        print(f"[OK] Codebase analyzed")
        print(f"  Files analyzed: {analyze_result['metrics']['total_files']}")
        
        # Step 3: Export course
        print("\n4. Exporting course...")
        export_result = await export_tool(
            codebase_id=codebase_id,
            format="json",
            output_dir=f"./output/test_update_{codebase_id}",
            target_audience="beginner",
            course_focus="full-stack",
            max_duration_hours=None,
            min_teaching_value=0.0
        )
        print(f"[OK] Course exported")
        print(f"  Modules: {export_result['statistics']['modules']}")
        print(f"  Lessons: {export_result['statistics']['lessons']}")
        
        # Step 4: Get enrichment guide for first lesson
        print("\n5. Getting enrichment guide...")
        
        # Find first lesson ID from course data
        export_path = Path(export_result['export_path'])
        course_dir = export_path.parent
        course_data_path = course_dir / 'course_data.json'
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        if not course_data['modules'] or not course_data['modules'][0]['lessons']:
            print("[ERROR] No lessons found in course")
            return
        
        first_lesson = course_data['modules'][0]['lessons'][0]
        first_lesson_id = first_lesson['lesson_id']
        print(f"  Testing with lesson: {first_lesson_id}")
        print(f"  Original description: {first_lesson['description'][:80]}...")
        
        enrichment_result = await enrichment_tool(
            codebase_id=codebase_id,
            lesson_id=first_lesson_id
        )
        
        print(f"[OK] Enrichment guide generated")
        print(f"  Teaching Value: {enrichment_result['teaching_value_assessment']['total_score']}/14")
        
        # Step 5: Update lesson with enriched content
        print("\n6. Updating lesson with enriched content...")
        
        # Create sample enriched content
        enriched_content = {
            'description': f"Enhanced: Learn about {enrichment_result['feature_mapping']['feature_name']} - {enrichment_result['feature_mapping']['user_facing_purpose']}",
            'content': f"""# Introduction

{enrichment_result['narrative_structure']['introduction_points'][0] if enrichment_result['narrative_structure']['introduction_points'] else 'This lesson covers important concepts.'}

## Learning Objectives

{chr(10).join('- ' + obj for obj in enrichment_result['narrative_structure']['learning_progression'][:3])}

## Key Concepts

{enrichment_result['systematic_investigation']['what_it_does']}

## Conclusion

{enrichment_result['narrative_structure']['conclusion_points'][0] if enrichment_result['narrative_structure']['conclusion_points'] else 'You have learned important concepts.'}
""",
            'learning_objectives': enrichment_result['narrative_structure']['learning_progression'][:5]
        }
        
        update_result = await update_tool(
            codebase_id=codebase_id,
            lesson_id=first_lesson_id,
            enriched_content=enriched_content
        )
        
        print(f"[OK] Lesson updated")
        print(f"  Success: {update_result['success']}")
        print(f"  Updated fields: {', '.join(update_result['updated_fields'])}")
        print(f"  Enrichment status: {update_result['enrichment_status']['status']}")
        print(f"  Version: {update_result['enrichment_status']['version']}")
        
        # Step 6: Verify the update
        print("\n7. Verifying update...")
        with open(course_data_path, 'r', encoding='utf-8') as f:
            updated_course_data = json.load(f)
        
        updated_lesson = updated_course_data['modules'][0]['lessons'][0]
        print(f"  Updated description: {updated_lesson['description'][:80]}...")
        print(f"  Content length: {len(updated_lesson.get('content', ''))} characters")
        print(f"  Learning objectives: {len(updated_lesson.get('learning_objectives', []))} items")
        
        # Check enrichment status
        enrichment_status = updated_course_data.get('enrichment_status', {}).get(first_lesson_id, {})
        print(f"  Enrichment status in course data: {enrichment_status.get('status', 'N/A')}")
        print(f"  Enriched at: {enrichment_status.get('enriched_at', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("[OK] All tests passed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        await cache_manager.close()
        src.server.app_context = None


if __name__ == "__main__":
    asyncio.run(test_update_lesson_content())
