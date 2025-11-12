# Design Document - Course Generator (Part 2)

## Export Formats (Continued)

### Next.js Export

```python
def export_to_nextjs(course: CourseOutline, output_dir: str):
    # 1. Create Next.js project structure
    create_nextjs_structure(output_dir)
    
    # 2. Generate pages for each lesson
    for module in course.modules:
        for lesson in module.lessons:
            component = generate_lesson_component(lesson)
            write_file(
                f"{output_dir}/pages/lessons/{lesson.lesson_id}.tsx",
                component
            )
    
    # 3. Generate course data as JSON
    course_data = course.to_dict()
    write_file(
        f"{output_dir}/data/course.json",
        json.dumps(course_data, indent=2)
    )
    
    # 4. Generate navigation component
    nav_component = generate_navigation(course)
    write_file(f"{output_dir}/components/Navigation.tsx", nav_component)
```

### Markdown Export

```python
def export_to_markdown(course: CourseOutline, output_dir: str):
    # Create one markdown file per lesson
    for module in course.modules:
        module_dir = f"{output_dir}/{module.title.lower().replace(' ', '-')}"
        os.makedirs(module_dir, exist_ok=True)
        
        for lesson in module.lessons:
            lesson_md = render_template("lesson.md.j2", lesson=lesson)
            write_file(
                f"{module_dir}/{lesson.title.lower().replace(' ', '-')}.md",
                lesson_md
            )
    
    # Generate README with course overview
    readme = generate_readme(course)
    write_file(f"{output_dir}/README.md", readme)
```

## MCP Tool Integration

### Tool 1: export_course

```python
@mcp.tool
async def export_course(
    codebase_id: str,
    format: str = "mkdocs",
    output_path: str = "./course-output",
    config: Optional[dict] = None,
    ctx: Context = None
) -> dict:
    """
    Export analyzed codebase as a complete course.
    
    Args:
        codebase_id: ID from scan_codebase
        format: Export format (mkdocs, nextjs, json, markdown, pdf)
        output_path: Where to save the course
        config: Optional course configuration
    
    Returns:
        Export result with file paths and statistics
    """
    # 1. Get analysis from cache
    analysis = await get_codebase_analysis(codebase_id)
    
    # 2. Generate course structure
    course_config = CourseConfig.from_dict(config or {})
    course = course_generator.generate_course_structure(analysis, course_config)
    
    # 3. Generate lesson content
    for module in course.modules:
        for lesson in module.lessons:
            lesson.content = lesson_generator.generate_content(
                analysis.file_analyses[lesson.file_path],
                course_config
            )
    
    # 4. Generate exercises
    for module in course.modules:
        for lesson in module.lessons:
            lesson.exercises = exercise_generator.generate_exercises(
                analysis.file_analyses[lesson.file_path],
                course_config
            )
    
    # 5. Export to specified format
    export_manager.export(course, format, output_path)
    
    return {
        "course_id": course.course_id,
        "title": course.title,
        "format": format,
        "output_path": output_path,
        "modules": len(course.modules),
        "lessons": sum(len(m.lessons) for m in course.modules),
        "duration_hours": course.total_duration_hours
    }
```

### Tool 2: generate_lesson_outline

```python
@mcp.tool
async def generate_lesson_outline(
    file_path: str,
    codebase_id: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Generate a lesson outline for a specific file.
    
    Args:
        file_path: Path to file to create lesson from
        codebase_id: Optional codebase ID for context
    
    Returns:
        Lesson outline with objectives, content structure, exercises
    """
    # 1. Analyze file if not already analyzed
    if codebase_id:
        analysis = await get_file_analysis(codebase_id, file_path)
    else:
        analysis = await analysis_engine.analyze_file(file_path)
    
    # 2. Generate lesson structure
    lesson = lesson_generator.generate_lesson_structure(analysis)
    
    # 3. Generate content outline
    content_outline = lesson_generator.generate_content_outline(analysis)
    
    # 4. Generate exercise ideas
    exercise_ideas = exercise_generator.generate_exercise_ideas(analysis)
    
    return {
        "lesson_id": lesson.lesson_id,
        "title": lesson.title,
        "difficulty": lesson.difficulty,
        "duration_minutes": lesson.duration_minutes,
        "learning_objectives": lesson.learning_objectives,
        "concepts": lesson.concepts,
        "content_outline": content_outline,
        "exercise_ideas": exercise_ideas,
        "teaching_value": analysis.teaching_value.total_score
    }
```

### Tool 3: create_exercise

```python
@mcp.tool
async def create_exercise(
    pattern_type: str,
    difficulty: str = "intermediate",
    codebase_id: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Create a coding exercise for a specific pattern.
    
    Args:
        pattern_type: Type of pattern (e.g., "custom-hooks", "api-routes")
        difficulty: Exercise difficulty (beginner, intermediate, advanced)
        codebase_id: Optional codebase ID to find examples
    
    Returns:
        Exercise with instructions, starter code, solution, hints
    """
    # 1. Find example of pattern in codebase
    if codebase_id:
        pattern_example = await find_pattern_example(codebase_id, pattern_type)
    else:
        pattern_example = get_default_pattern_example(pattern_type)
    
    # 2. Generate exercise
    exercise = exercise_generator.generate_exercise(
        pattern_example,
        difficulty
    )
    
    return {
        "exercise_id": exercise.exercise_id,
        "title": exercise.title,
        "description": exercise.description,
        "difficulty": exercise.difficulty,
        "estimated_minutes": exercise.estimated_minutes,
        "instructions": exercise.instructions,
        "starter_code": exercise.starter_code,
        "hints": exercise.hints,
        "has_solution": True,
        "test_cases": len(exercise.test_cases)
    }
```

