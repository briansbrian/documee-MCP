"""
Manual test for get_enrichment_guide MCP tool.

This script tests the get_enrichment_guide tool by:
1. Scanning a codebase
2. Analyzing the codebase
3. Exporting a course
4. Getting an enrichment guide for a lesson

Run with: venv\\Scripts\\python.exe tests/test_enrichment_guide_manual.py
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


async def test_enrichment_guide():
    """Test the get_enrichment_guide tool."""
    print("=" * 80)
    print("Testing get_enrichment_guide MCP Tool")
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
    print("✓ App context initialized")
    
    try:
        # Get MCP tools
        scan_tool = src.server.mcp._tool_manager._tools['scan_codebase'].fn
        analyze_tool = src.server.mcp._tool_manager._tools['analyze_codebase_tool'].fn
        export_tool = src.server.mcp._tool_manager._tools['export_course'].fn
        enrichment_tool = src.server.mcp._tool_manager._tools['get_enrichment_guide'].fn
        
        # Step 1: Scan codebase
        print("\n2. Scanning codebase...")
        scan_result = await scan_tool(path=".", max_depth=3, use_cache=False)
        codebase_id = scan_result['codebase_id']
        print(f"✓ Codebase scanned: {codebase_id}")
        print(f"  Total files: {scan_result['structure']['total_files']}")
        
        # Step 2: Analyze codebase
        print("\n3. Analyzing codebase...")
        analyze_result = await analyze_tool(
            codebase_id=codebase_id,
            incremental=False,
            use_cache=False
        )
        print(f"✓ Codebase analyzed")
        print(f"  Files analyzed: {analyze_result['metrics']['total_files']}")
        print(f"  Top teaching files: {len(analyze_result['top_teaching_files'])}")
        
        # Step 3: Export course
        print("\n4. Exporting course...")
        export_result = await export_tool(
            codebase_id=codebase_id,
            format="json",
            output_dir=f"./output/test_enrichment_{codebase_id}",
            target_audience="beginner",
            course_focus="full-stack",
            max_duration_hours=None,
            min_teaching_value=0.0
        )
        print(f"✓ Course exported")
        print(f"  Modules: {export_result['statistics']['modules']}")
        print(f"  Lessons: {export_result['statistics']['lessons']}")
        print(f"  Export path: {export_result['export_path']}")
        
        # Step 4: Get enrichment guide for first lesson
        print("\n5. Getting enrichment guide...")
        
        # Find first lesson ID from course data
        export_path = Path(export_result['export_path'])
        # export_path is the course.json file, get the parent directory
        course_dir = export_path.parent
        course_data_path = course_dir / 'course_data.json'
        with open(course_data_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        if not course_data['modules'] or not course_data['modules'][0]['lessons']:
            print("✗ No lessons found in course")
            return
        
        first_lesson_id = course_data['modules'][0]['lessons'][0]['lesson_id']
        print(f"  Testing with lesson: {first_lesson_id}")
        
        enrichment_result = await enrichment_tool(
            codebase_id=codebase_id,
            lesson_id=first_lesson_id
        )
        
        print(f"✓ Enrichment guide generated")
        print(f"  Lesson ID: {enrichment_result['lesson_id']}")
        print(f"  Feature: {enrichment_result['feature_mapping']['feature_name']}")
        print(f"  Teaching Value: {enrichment_result['teaching_value_assessment']['total_score']}/14")
        print(f"  Should Teach: {enrichment_result['teaching_value_assessment']['should_teach']}")
        print(f"  Code Sections: {len(enrichment_result['code_sections'])}")
        print(f"  Evidence Sources:")
        print(f"    - Source files: {len(enrichment_result['evidence_bundle']['source_files'])}")
        print(f"    - Test files: {len(enrichment_result['evidence_bundle']['test_files'])}")
        print(f"    - Git commits: {len(enrichment_result['evidence_bundle']['git_commits'])}")
        print(f"    - Documentation: {len(enrichment_result['evidence_bundle']['documentation'])}")
        
        # Save enrichment guide for inspection
        output_file = Path(f"./output/test_enrichment_{codebase_id}/enrichment_guide_{first_lesson_id}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enrichment_result, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Enrichment guide saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print("✓ All tests passed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        await cache_manager.close()
        src.server.app_context = None


if __name__ == "__main__":
    asyncio.run(test_enrichment_guide())
