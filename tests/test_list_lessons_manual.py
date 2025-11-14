"""
Manual test for list_lessons_for_enrichment MCP tool.

This script tests the list_lessons_for_enrichment tool by:
1. Scanning a codebase
2. Analyzing the codebase
3. Exporting a course
4. Listing all lessons with enrichment status

Run with: venv\Scripts\python.exe tests/test_list_lessons_manual.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cache.unified_cache import UnifiedCacheManager
from src.analysis.engine import AnalysisEngine
from src.analysis.config import AnalysisConfig
from src.tools.scan_codebase import scan_codebase
from src.course.structure_generator import CourseStructureGenerator
from src.course.content_generator import LessonContentGenerator
from src.course.exercise_generator import ExerciseGenerator
from src.course.config import CourseConfig
from src.course.exporters.export_manager import ExportManager
from src.models import CodebaseAnalysis


async def test_list_lessons():
    """Test the list_lessons_for_enrichment tool."""
    
    print("=" * 80)
    print("Testing list_lessons_for_enrichment MCP Tool")
    print("=" * 80)
    
    # Initialize cache manager
    cache_manager = UnifiedCacheManager(
        max_memory_mb=100,
        sqlite_path="cache_db/test_list_lessons.db",
        redis_url=None
    )
    await cache_manager.initialize()
    
    # Initialize analysis engine
    analysis_config = AnalysisConfig()
    analysis_engine = AnalysisEngine(cache_manager, analysis_config)
    
    # Set up app context
    from src.server import AppContext
    import src.server as server_module
    from src.config.settings import Settings
    
    config = Settings()
    server_module.app_context = AppContext(
        cache_manager=cache_manager,
        config=config,
        analysis_engine=analysis_engine
    )
    
    try:
        # Step 1: Scan codebase
        print("\n1. Scanning codebase...")
        scan_result = await scan_codebase(
            path="./src",
            max_depth=5,
            use_cache=False,
            cache_manager=cache_manager,
            max_file_size_mb=10
        )
        codebase_id = scan_result['codebase_id']
        print(f"   ✓ Codebase scanned: {codebase_id}")
        print(f"   Total files: {scan_result['structure']['total_files']}")
        
        # Step 2: Analyze codebase
        print("\n2. Analyzing codebase...")
        analysis = await analysis_engine.analyze_codebase(
            codebase_id=codebase_id,
            incremental=False
        )
        print(f"   ✓ Codebase analyzed")
        print(f"   Files analyzed: {analysis.metrics.total_files}")
        
        # Step 3: Export course
        print("\n3. Exporting course...")
        course_config = CourseConfig(
            target_audience="beginner",
            course_focus="full-stack",
            max_duration_hours=None,
            min_teaching_value=0.0
        )
        
        # Generate course structure
        structure_gen = CourseStructureGenerator(course_config)
        course_outline = await structure_gen.generate_course_structure(analysis)
        
        # Generate lesson content
        content_gen = LessonContentGenerator(course_config)
        exercise_gen = ExerciseGenerator(course_config)
        
        for module in course_outline.modules:
            for lesson in module.lessons:
                file_analysis = analysis.file_analyses.get(lesson.file_path)
                if file_analysis:
                    lesson.content = await content_gen.generate_lesson_content(file_analysis)
                    patterns = [p for p in file_analysis.patterns if p.confidence > 0.7]
                    num_exercises = min(3, max(1, len(patterns)))
                    for i, pattern in enumerate(patterns[:num_exercises]):
                        exercise = await exercise_gen.generate_exercise(pattern, file_analysis)
                        lesson.exercises.append(exercise)
        
        # Save course data
        import json
        output_dir = Path(f"./output/test_list_lessons_{codebase_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        course_data = {
            'course_id': course_outline.course_id,
            'title': course_outline.title,
            'description': course_outline.description,
            'author': course_outline.author,
            'version': course_outline.version,
            'created_at': course_outline.created_at.isoformat(),
            'total_duration_hours': course_outline.total_duration_hours,
            'difficulty_distribution': course_outline.difficulty_distribution,
            'tags': course_outline.tags,
            'prerequisites': course_outline.prerequisites,
            'modules': []
        }
        
        for module in course_outline.modules:
            module_data = {
                'module_id': module.module_id,
                'title': module.title,
                'description': module.description,
                'order': module.order,
                'difficulty': module.difficulty,
                'duration_hours': module.duration_hours,
                'learning_objectives': module.learning_objectives,
                'lessons': []
            }
            
            for lesson in module.lessons:
                lesson_data = {
                    'lesson_id': lesson.lesson_id,
                    'title': lesson.title,
                    'description': lesson.description,
                    'order': lesson.order,
                    'difficulty': lesson.difficulty,
                    'duration_minutes': lesson.duration_minutes,
                    'file_path': lesson.file_path,
                    'teaching_value': lesson.teaching_value,
                    'learning_objectives': lesson.learning_objectives,
                    'prerequisites': lesson.prerequisites,
                    'concepts': lesson.concepts,
                    'exercises': [],
                    'tags': lesson.tags
                }
                module_data['lessons'].append(lesson_data)
            
            course_data['modules'].append(module_data)
        
        course_data_path = output_dir / 'course_data.json'
        with open(course_data_path, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
        
        total_modules = len(course_outline.modules)
        total_lessons = sum(len(m.lessons) for m in course_outline.modules)
        total_exercises = sum(len(lesson.exercises) for module in course_outline.modules for lesson in module.lessons)
        
        print(f"   ✓ Course exported")
        print(f"   Modules: {total_modules}")
        print(f"   Lessons: {total_lessons}")
        print(f"   Exercises: {total_exercises}")
        
        # Step 4: List lessons for enrichment
        print("\n4. Listing lessons for enrichment...")
        
        # Load course data
        with open(course_data_path, 'r', encoding='utf-8') as f:
            loaded_course_data = json.load(f)
        
        # Get enrichment status
        enrichment_status = loaded_course_data.get('enrichment_status', {})
        
        # Build lessons list
        lessons = []
        for module in loaded_course_data.get('modules', []):
            module_title = module.get('title', 'Unknown Module')
            for lesson in module.get('lessons', []):
                lesson_id = lesson.get('lesson_id')
                lesson_status = enrichment_status.get(lesson_id, {})
                status = lesson_status.get('status', 'not_started')
                enriched_at = lesson_status.get('enriched_at')
                version = lesson_status.get('version', 0)
                
                lesson_info = {
                    'lesson_id': lesson_id,
                    'title': lesson.get('title', 'Untitled Lesson'),
                    'module_title': module_title,
                    'status': status,
                    'teaching_value': lesson.get('teaching_value', 0.0),
                    'source_files': [lesson.get('file_path')] if lesson.get('file_path') else [],
                    'difficulty': lesson.get('difficulty', 'intermediate'),
                    'duration_minutes': lesson.get('duration_minutes', 0)
                }
                
                if enriched_at:
                    lesson_info['enriched_at'] = enriched_at
                if version > 0:
                    lesson_info['version'] = version
                
                lessons.append(lesson_info)
        
        # Sort by teaching value
        lessons.sort(key=lambda x: x['teaching_value'], reverse=True)
        
        # Calculate summary
        total_lessons_count = len(lessons)
        not_started = sum(1 for l in lessons if l['status'] == 'not_started')
        in_progress = sum(1 for l in lessons if l['status'] == 'in_progress')
        completed = sum(1 for l in lessons if l['status'] == 'completed')
        completion_percentage = (completed / total_lessons_count * 100) if total_lessons_count > 0 else 0.0
        
        list_result = {
            'lessons': lessons,
            'total_lessons': total_lessons_count,
            'enrichment_summary': {
                'not_started': not_started,
                'in_progress': in_progress,
                'completed': completed,
                'completion_percentage': round(completion_percentage, 2)
            },
            'codebase_id': codebase_id
        }
        
        print(f"   ✓ Lessons listed")
        print(f"\n   Total lessons: {list_result['total_lessons']}")
        print(f"\n   Enrichment Summary:")
        summary = list_result['enrichment_summary']
        print(f"     - Not started: {summary['not_started']}")
        print(f"     - In progress: {summary['in_progress']}")
        print(f"     - Completed: {summary['completed']}")
        print(f"     - Completion: {summary['completion_percentage']:.1f}%")
        
        # Display top 5 lessons by teaching value
        print(f"\n   Top 5 Lessons by Teaching Value:")
        for i, lesson in enumerate(list_result['lessons'][:5], 1):
            print(f"     {i}. {lesson['lesson_id']}: {lesson['title']}")
            print(f"        Module: {lesson['module_title']}")
            print(f"        Teaching Value: {lesson['teaching_value']:.3f}")
            print(f"        Status: {lesson['status']}")
            print(f"        Difficulty: {lesson['difficulty']}")
            print(f"        Duration: {lesson['duration_minutes']} min")
            if lesson.get('source_files'):
                print(f"        Source: {lesson['source_files'][0]}")
            print()
        
        print("\n" + "=" * 80)
        print("✓ Test completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        await cache_manager.close()


if __name__ == "__main__":
    asyncio.run(test_list_lessons())
