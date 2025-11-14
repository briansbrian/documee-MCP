"""
AI Content Enrichment Example

This example demonstrates how to use the enrichment system to generate
comprehensive, evidence-based enrichment guides for AI assistants to create
rich educational content.

The enrichment workflow:
1. Generate a basic course structure with export_course
2. Get enrichment guide for a lesson with get_enrichment_guide
3. Use the guide to enrich lesson content (manually or with AI)
4. Update the lesson with enriched content using update_lesson_content

Note: This example simulates MCP tool calls. In production, these would be
called by an MCP client (like Claude Desktop or MCP Inspector).

Requirements:
- Python 3.12+
- Analysis engine and course generator components
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


async def simulate_mcp_tool_call(tool_name: str, arguments: dict):
    """
    Simulate an MCP tool call.
    
    In production, this would be handled by the MCP server and client.
    """
    print(f"\n📞 MCP Tool Call: {tool_name}")
    print(f"   Arguments: {arguments}")
    
    # Simulate tool responses with mock data
    if tool_name == "scan_codebase":
        return {
            "codebase_id": "example_codebase_abc123",
            "structure": {
                "total_files": 45,
                "total_directories": 12,
                "total_size_mb": 2.3,
                "languages": {"Python": 40, "JSON": 3, "Markdown": 2},
                "file_types": {".py": 40, ".json": 3, ".md": 2}
            },
            "summary": {
                "primary_language": "Python",
                "project_type": "python-application",
                "has_tests": True,
                "size_category": "small"
            },
            "scan_time_ms": 150.0,
            "from_cache": False
        }
    
    elif tool_name == "export_course":
        return {
            "success": True,
            "output_path": arguments["output_path"],
            "modules_count": 3,
            "lessons_count": 12,
            "format": arguments["format"]
        }
    
    elif tool_name == "list_lessons_for_enrichment":
        # Simulate this tool (would be implemented in the enrichment system)
        return {
            "total_lessons": 12,
            "pending_count": 10,
            "completed_count": 2,
            "lessons": [
                {
                    "lesson_id": "module-1-lesson-1",
                    "title": "Understanding Data Models",
                    "enrichment_status": "pending",
                    "teaching_value": 0.85,
                    "source_files": ["src/course/enrichment_models.py"]
                },
                {
                    "lesson_id": "module-2-lesson-3", 
                    "title": "User Authentication System",
                    "enrichment_status": "pending",
                    "teaching_value": 0.92,
                    "source_files": ["src/auth/login.py", "src/auth/session.py"]
                }
            ]
        }
    
    elif tool_name == "get_enrichment_guide":
        # Load the sample enrichment guide
        guide_path = Path(__file__).parent / "enrichment_guide_sample.json"
        with open(guide_path, 'r') as f:
            guide_data = json.load(f)
        return guide_data
    
    elif tool_name == "update_lesson_content":
        # Simulate successful update
        return {
            "success": True,
            "lesson_id": arguments["lesson_id"],
            "updated_fields": ["description", "content", "learning_objectives", "code_examples", "exercises"],
            "enrichment_status": "completed"
        }
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}


async def example_enrichment_workflow():
    """
    Complete enrichment workflow example.
    
    This demonstrates the full process of enriching course content:
    1. Export basic course structure
    2. List lessons available for enrichment
    3. Get enrichment guide for a specific lesson
    4. Simulate content enrichment
    5. Update lesson with enriched content
    """
    
    print("=" * 80)
    print("AI Content Enrichment Workflow Example")
    print("=" * 80)
    print("\nNote: This example simulates MCP tool calls for demonstration.")
    print("In production, these would be called by an MCP client.\n")
    
    print("✓ Simulating MCP server connection")
            
    # Step 1: Scan and analyze a codebase
    print("\n" + "=" * 80)
    print("STEP 1: Scan Codebase")
    print("=" * 80)
    
    scan_data = await simulate_mcp_tool_call(
        "scan_codebase",
        {
            "path": "src/course",
            "max_depth": 3,
            "use_cache": True
        }
    )
    codebase_id = scan_data['codebase_id']
    
    print(f"\n✓ Scanned codebase: {codebase_id}")
    print(f"  Files: {scan_data['structure']['total_files']}")
    print(f"  Primary Language: {scan_data['summary']['primary_language']}")
    
    # Step 2: Export basic course structure
    print("\n" + "=" * 80)
    print("STEP 2: Export Basic Course Structure")
    print("=" * 80)
    
    export_data = await simulate_mcp_tool_call(
        "export_course",
        {
            "codebase_id": codebase_id,
            "output_path": "output/enrichment_example",
            "format": "json",
            "config": {
                "target_audience": "intermediate",
                "course_focus": "patterns",
                "max_duration_hours": 10.0
            }
        }
    )
            
    print(f"\n✓ Exported basic course structure")
    print(f"  Output: {export_data.get('output_path', 'output/enrichment_example')}")
    print(f"  Modules: {export_data.get('modules_count', 3)}")
    print(f"  Lessons: {export_data.get('lessons_count', 12)}")
    
    # Step 3: List lessons available for enrichment
    print("\n" + "=" * 80)
    print("STEP 3: List Lessons for Enrichment")
    print("=" * 80)
    
    lessons_data = await simulate_mcp_tool_call(
        "list_lessons_for_enrichment",
        {
            "codebase_id": codebase_id
        }
    )
            
    print(f"\n✓ Found {lessons_data['total_lessons']} lessons")
    print(f"  Pending: {lessons_data['pending_count']}")
    print(f"  Completed: {lessons_data['completed_count']}")
    
    if lessons_data['lessons']:
        print("\n  Top lessons by teaching value:")
        for lesson in lessons_data['lessons'][:3]:
            print(f"    - {lesson['lesson_id']}: {lesson['title']}")
            print(f"      Status: {lesson['enrichment_status']}")
            print(f"      Teaching Value: {lesson['teaching_value']:.2f}")
            print(f"      Source Files: {len(lesson['source_files'])}")
        
        # Select first lesson for enrichment
        target_lesson = lessons_data['lessons'][0]
        lesson_id = target_lesson['lesson_id']
    else:
        print("\n  No lessons available for enrichment")
        return
    
    # Step 4: Get enrichment guide
    print("\n" + "=" * 80)
    print("STEP 4: Get Enrichment Guide")
    print("=" * 80)
    print(f"\nGetting enrichment guide for: {lesson_id}")
    
    guide_data = await simulate_mcp_tool_call(
        "get_enrichment_guide",
        {
            "codebase_id": codebase_id,
            "lesson_id": lesson_id
        }
    )
    
    print(f"\n✓ Generated enrichment guide")
    print(f"  Lesson: {guide_data['lesson_id']}")
    
    # Display guide structure
    print("\n  Guide Contents:")
    print(f"    - Feature Mapping: {guide_data['feature_mapping']['feature_name']}")
    print(f"    - Evidence Bundle:")
    print(f"      • Source Files: {len(guide_data['evidence_bundle']['source_files'])}")
    print(f"      • Test Files: {len(guide_data['evidence_bundle']['test_files'])}")
    print(f"      • Git Commits: {len(guide_data['evidence_bundle']['git_commits'])}")
    print(f"      • Documentation: {len(guide_data['evidence_bundle']['documentation'])}")
    
    print(f"    - Teaching Value: {guide_data['teaching_value_assessment']['total_score']}/14")
    print(f"      Should Teach: {guide_data['teaching_value_assessment']['should_teach']}")
    
    print(f"    - Systematic Investigation:")
    print(f"      • What it does: {guide_data['systematic_investigation']['what_it_does'][:80]}...")
    print(f"      • Why it exists: {guide_data['systematic_investigation']['why_it_exists'][:80]}...")
    
    print(f"    - Narrative Structure:")
    print(f"      • Introduction Points: {len(guide_data['narrative_structure']['introduction_points'])}")
    print(f"      • Learning Progression: {len(guide_data['narrative_structure']['learning_progression'])}")
    
    print(f"    - Code Sections: {len(guide_data['code_sections'])}")
    if guide_data['code_sections']:
        section = guide_data['code_sections'][0]
        print(f"      • First section: {section['file_path']} (lines {section['line_range'][0]}-{section['line_range'][1]})")
        print(f"      • Key Concepts: {len(section['key_concepts'])}")
    
    print(f"    - Architecture Context:")
    print(f"      • Component Role: {guide_data['architecture_context']['component_role'][:80]}...")
    print(f"      • Dependencies: {len(guide_data['architecture_context']['dependencies'])}")
    
    print(f"    - Real-World Context:")
    print(f"      • Use Cases: {len(guide_data['real_world_context']['practical_use_cases'])}")
    print(f"      • Analogies: {len(guide_data['real_world_context']['analogies'])}")
    
    print(f"    - Exercise Generation:")
    print(f"      • Hands-on Tasks: {len(guide_data['exercise_generation']['hands_on_tasks'])}")
    print(f"      • Progressive Hints: {len(guide_data['exercise_generation']['progressive_hints'])}")
    
    # Save guide to file for reference
    guide_path = Path("output/enrichment_example/enrichment_guide.json")
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide_path.write_text(json.dumps(guide_data, indent=2))
    print(f"\n  ✓ Saved enrichment guide to: {guide_path}")
    
    # Step 5: Simulate content enrichment
    print("\n" + "=" * 80)
    print("STEP 5: Enrich Lesson Content")
    print("=" * 80)
    print("\nIn a real workflow, an AI assistant (like Kiro) would:")
    print("  1. Read the enrichment guide")
    print("  2. Review all evidence (code, tests, commits, docs)")
    print("  3. Generate rich explanations following the narrative structure")
    print("  4. Create detailed code walkthroughs with citations")
    print("  5. Write progressive exercises with hints")
    print("  6. Ensure all content is beginner-friendly and evidence-based")
    
    # Simulate enriched content
    enriched_content = {
                "description": f"Enhanced description for {target_lesson['title']} with context and learning goals based on evidence from the codebase.",
                "content": f"""# Introduction

{guide_data['narrative_structure']['introduction_points'][0] if guide_data['narrative_structure']['introduction_points'] else 'This lesson covers important concepts.'}

## What You'll Learn

{chr(10).join(f"- {point}" for point in guide_data['narrative_structure']['learning_progression'][:3])}

## Understanding the Code

{guide_data['systematic_investigation']['what_it_does']}

### Why This Matters

{guide_data['systematic_investigation']['why_it_exists']}

### How It Works

{guide_data['systematic_investigation']['how_it_works']}

## Real-World Applications

{guide_data['real_world_context']['practical_use_cases'][0] if guide_data['real_world_context']['practical_use_cases'] else 'This pattern is widely used in production applications.'}

## Key Takeaways

{chr(10).join(f"- {point}" for point in guide_data['narrative_structure']['conclusion_points'][:3])}
""",
                "learning_objectives": guide_data['narrative_structure']['learning_progression'][:5],
                "code_examples": [
                    {
                        "explanation": f"{section['purpose']}\n\nKey concepts: {', '.join(section['key_concepts'][:3])}"
                    }
                    for section in guide_data['code_sections'][:2]
                ],
                "exercises": [
                    {
                        "description": task['description'],
                        "instructions": f"Complete this exercise to practice {task['title']}",
                        "hints": guide_data['exercise_generation']['progressive_hints'][:3]
                    }
                    for task in guide_data['exercise_generation']['hands_on_tasks'][:2]
            ]
        }
    
    print("\n✓ Generated enriched content:")
    print(f"  Description: {len(enriched_content['description'])} chars")
    print(f"  Content: {len(enriched_content['content'])} chars")
    print(f"  Learning Objectives: {len(enriched_content['learning_objectives'])}")
    print(f"  Enhanced Code Examples: {len(enriched_content['code_examples'])}")
    print(f"  Enhanced Exercises: {len(enriched_content['exercises'])}")
            
    # Step 6: Update lesson with enriched content
    print("\n" + "=" * 80)
    print("STEP 6: Update Lesson with Enriched Content")
    print("=" * 80)
    
    update_data = await simulate_mcp_tool_call(
        "update_lesson_content",
        {
            "codebase_id": codebase_id,
            "lesson_id": lesson_id,
            "enriched_content": enriched_content
        }
    )
            
    if update_data['success']:
        print(f"\n✓ Successfully updated lesson: {update_data['lesson_id']}")
        print(f"  Updated Fields: {', '.join(update_data['updated_fields'])}")
        print(f"  Enrichment Status: {update_data['enrichment_status']}")
    else:
        print(f"\n✗ Failed to update lesson: {update_data.get('error', 'Unknown error')}")
    
    # Step 7: Verify enrichment
    print("\n" + "=" * 80)
    print("STEP 7: Verify Enrichment")
    print("=" * 80)
    
    # List lessons again to see updated status
    verify_data = await simulate_mcp_tool_call(
        "list_lessons_for_enrichment",
        {
            "codebase_id": codebase_id
        }
    )
            
    print(f"\n✓ Enrichment Status:")
    print(f"  Total Lessons: {verify_data['total_lessons']}")
    print(f"  Pending: {verify_data['pending_count'] - 1}")  # One less pending since we enriched one
    print(f"  Completed: {verify_data['completed_count'] + 1}")  # One more completed
    
    # Find our enriched lesson
    enriched_lesson = next(
        (l for l in verify_data['lessons'] if l['lesson_id'] == lesson_id),
        None
    )
    
    if enriched_lesson:
        print(f"\n  Enriched Lesson: {enriched_lesson['title']}")
        print(f"    Status: completed")  # Updated status
        print(f"    Teaching Value: {enriched_lesson['teaching_value']:.2f}")
    
    print("\n" + "=" * 80)
    print("Enrichment Workflow Complete!")
    print("=" * 80)
    print("\nSummary:")
    print(f"  ✓ Scanned codebase: {codebase_id}")
    print(f"  ✓ Exported basic course structure")
    print(f"  ✓ Generated enrichment guide with comprehensive evidence")
    print(f"  ✓ Enriched lesson content with AI-generated materials")
    print(f"  ✓ Updated lesson with enriched content")
    print(f"  ✓ Verified enrichment status")
    
    print("\nNext Steps:")
    print("  1. Review the enriched course in output/enrichment_example/")
    print("  2. Continue enriching remaining lessons")
    print("  3. Export enriched course to MkDocs or other formats")
    print("  4. Iterate on content quality based on feedback")


async def example_get_enrichment_guide():
    """
    Example: Get enrichment guide for a specific lesson.
    
    This demonstrates how to retrieve a comprehensive enrichment guide
    that provides all the context and evidence needed for AI to generate
    rich educational content.
    """
    
    print("\n" + "=" * 80)
    print("Example: Get Enrichment Guide")
    print("=" * 80)
    
    # Assume we have a codebase_id and lesson_id
    codebase_id = "example_codebase"
    lesson_id = "module-1-lesson-1"
    
    print(f"\nRequesting enrichment guide for:")
    print(f"  Codebase: {codebase_id}")
    print(f"  Lesson: {lesson_id}")
    
    try:
        guide = await simulate_mcp_tool_call(
            "get_enrichment_guide",
            {
                "codebase_id": codebase_id,
                "lesson_id": lesson_id
            }
        )
                
        print("\n✓ Enrichment Guide Retrieved")
        print("\nGuide Structure:")
        print(f"  1. Feature Mapping")
        print(f"     - Feature: {guide['feature_mapping']['feature_name']}")
        print(f"     - Purpose: {guide['feature_mapping']['user_facing_purpose'][:60]}...")
        
        print(f"\n  2. Evidence Bundle")
        print(f"     - Source Files: {len(guide['evidence_bundle']['source_files'])}")
        print(f"     - Test Files: {len(guide['evidence_bundle']['test_files'])}")
        print(f"     - Git Commits: {len(guide['evidence_bundle']['git_commits'])}")
        
        print(f"\n  3. Validation Checklist")
        print(f"     - Consistency: {guide['validation_checklist']['consistency_check']}")
        
        print(f"\n  4. Teaching Value Assessment")
        print(f"     - Total Score: {guide['teaching_value_assessment']['total_score']}/14")
        print(f"     - Should Teach: {guide['teaching_value_assessment']['should_teach']}")
        
        print(f"\n  5. Systematic Investigation")
        print(f"     - What: {guide['systematic_investigation']['what_it_does'][:60]}...")
        print(f"     - Why: {guide['systematic_investigation']['why_it_exists'][:60]}...")
        
        print(f"\n  6. Narrative Structure")
        print(f"     - Introduction Points: {len(guide['narrative_structure']['introduction_points'])}")
        print(f"     - Learning Progression: {len(guide['narrative_structure']['learning_progression'])}")
        
        print(f"\n  7. Code Sections: {len(guide['code_sections'])}")
        
        print(f"\n  8. Architecture Context")
        print(f"     - Role: {guide['architecture_context']['component_role'][:60]}...")
        
        print(f"\n  9. Real-World Context")
        print(f"     - Use Cases: {len(guide['real_world_context']['practical_use_cases'])}")
        
        print(f"\n  10. Exercise Generation")
        print(f"      - Tasks: {len(guide['exercise_generation']['hands_on_tasks'])}")
        
        print(f"\n  11. Anti-Hallucination Rules")
        print(f"      - {guide['anti_hallucination_rules']['always_cite']}")
        
        print(f"\n  12. Enrichment Instructions")
        print(f"      - Tone: {guide['enrichment_instructions']['tone']}")
        print(f"      - Depth: {guide['enrichment_instructions']['depth']}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def example_update_lesson():
    """
    Example: Update lesson with enriched content.
    
    This demonstrates how to update a lesson after enriching its content
    with AI-generated materials.
    """
    
    print("\n" + "=" * 80)
    print("Example: Update Lesson Content")
    print("=" * 80)
    
    codebase_id = "example_codebase"
    lesson_id = "module-1-lesson-1"
            
    # Enriched content example
    enriched_content = {
                "description": "A comprehensive introduction to data models in Python, covering dataclasses, type hints, and serialization patterns used in modern applications.",
                "content": """# Understanding Data Models

## Introduction

Data models are the foundation of any application, defining how information is structured and validated. In this lesson, you'll learn how to create robust data models using Python's dataclasses, a powerful feature that reduces boilerplate while maintaining type safety.

## What Are Dataclasses?

Think of dataclasses like blueprints for your data. Just as an architect creates blueprints before building a house, you define dataclasses before creating data objects. They automatically generate common methods like `__init__`, `__repr__`, and `__eq__`, saving you from writing repetitive code.

## Key Concepts

- **Type Hints**: Specify what type of data each field should hold
- **Default Values**: Provide sensible defaults for optional fields
- **Immutability**: Use `frozen=True` to create read-only objects
- **Serialization**: Convert objects to/from dictionaries for JSON

## Code Walkthrough

Let's examine a real example from our codebase...

[Detailed code explanation with line-by-line breakdown]

## Real-World Applications

Data models like these are used in:
- REST API request/response objects
- Database ORM models
- Configuration management
- Data validation pipelines

## Summary

You've learned how to create type-safe data models using dataclasses, implement serialization methods, and apply these patterns in real applications. These skills are essential for building maintainable Python applications.
""",
                "learning_objectives": [
                    "Define data models using Python dataclasses",
                    "Implement type-safe field definitions with type hints",
                    "Create serialization methods for JSON conversion",
                    "Apply dataclass patterns in real applications"
                ],
                "code_examples": [
                    {
                        "explanation": "This dataclass defines a user model with type hints and default values. The @dataclass decorator automatically generates __init__, __repr__, and other methods, reducing boilerplate code."
                    }
                ],
                "exercises": [
                    {
                        "description": "Create a Product dataclass with validation",
                        "instructions": "Define a Product dataclass with name, price, and quantity fields. Add validation to ensure price is positive and quantity is non-negative.",
                        "hints": [
                            "Use type hints for all fields (str, float, int)",
                            "Consider using __post_init__ for validation",
                            "Raise ValueError for invalid data",
                            "Test with both valid and invalid inputs"
                        ]
                    }
                ]
            }
    
    print(f"\nUpdating lesson: {lesson_id}")
    print(f"  Codebase: {codebase_id}")
    
    try:
        update_data = await simulate_mcp_tool_call(
            "update_lesson_content",
            {
                "codebase_id": codebase_id,
                "lesson_id": lesson_id,
                "enriched_content": enriched_content
            }
        )
        
        if update_data['success']:
            print("\n✓ Lesson Updated Successfully")
            print(f"  Lesson ID: {update_data['lesson_id']}")
            print(f"  Updated Fields: {', '.join(update_data['updated_fields'])}")
            print(f"  Enrichment Status: {update_data['enrichment_status']}")
        else:
            print(f"\n✗ Update Failed: {update_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def main():
    """Run all enrichment examples."""
    print("\n" + "=" * 80)
    print("AI CONTENT ENRICHMENT EXAMPLES")
    print("=" * 80)
    print("\nThese examples demonstrate the enrichment workflow:")
    print("  1. Complete workflow (scan → export → enrich → update)")
    print("  2. Get enrichment guide")
    print("  3. Update lesson content")
    
    try:
        # Run complete workflow
        await example_enrichment_workflow()
        
        # Additional examples (commented out to avoid errors if codebase doesn't exist)
        # await example_get_enrichment_guide()
        # await example_update_lesson()
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("Examples Complete!")
    print("=" * 80)
    print("\nFor more information:")
    print("  - See docs/AI_CONTENT_ENRICHMENT.md for detailed documentation")
    print("  - See .kiro/steering/ai-content-enrichment.md for enrichment guidelines")
    print("  - See examples/enrichment_guide_sample.json for a complete guide example")


if __name__ == "__main__":
    asyncio.run(main())
