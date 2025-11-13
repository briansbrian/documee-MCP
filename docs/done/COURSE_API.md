# Course Generator API Documentation

Complete API reference for the Course Generator module, including all public classes, methods, data models, and MCP tools.

## Table of Contents

- [Data Models](#data-models)
- [Core Classes](#core-classes)
- [MCP Tools](#mcp-tools)
- [Exporters](#exporters)
- [Utilities](#utilities)

---

## Data Models

All data models are defined in `src/course/models.py` and use Python dataclasses for type safety and clarity.

### CourseOutline

Complete course structure with modules and lessons.

```python
@dataclass
class CourseOutline:
    course_id: str                              # Unique course identifier (UUID)
    title: str                                  # Course title
    description: str                            # Course description
    author: str                                 # Course author name
    version: str                                # Course version (e.g., "1.0.0")
    created_at: datetime                        # Creation timestamp
    modules: List[Module]                       # List of course modules
    total_duration_hours: float                 # Total course duration in hours
    difficulty_distribution: Dict[str, int]     # Count by difficulty level
    tags: List[str]                             # Course tags
    prerequisites: List[str]                    # Course prerequisites
```

**Example:**
```python
from src.course.models import CourseOutline
from datetime import datetime

course = CourseOutline(
    course_id="550e8400-e29b-41d4-a716-446655440000",
    title="Learn Python Web Development",
    description="A comprehensive course on Python web development",
    author="Jane Doe",
    version="1.0.0",
    created_at=datetime.now(),
    modules=[],  # List of Module objects
    total_duration_hours=25.5,
    difficulty_distribution={"beginner": 5, "intermediate": 10, "advanced": 3},
    tags=["python", "web", "flask", "django"],
    prerequisites=["Basic Python knowledge"]
)
```

### Module

A collection of related lessons grouped by theme or difficulty.

```python
@dataclass
class Module:
    module_id: str                              # Unique module identifier (UUID)
    title: str                                  # Module title
    description: str                            # Module description
    order: int                                  # Module order in course (0-indexed)
    lessons: List[Lesson]                       # List of lessons in module
    difficulty: str                             # "beginner", "intermediate", or "advanced"
    duration_hours: float                       # Total module duration in hours
    learning_objectives: List[str]              # Module learning objectives
```

**Example:**
```python
from src.course.models import Module

module = Module(
    module_id="660e8400-e29b-41d4-a716-446655440001",
    title="Module 1: Flask Fundamentals",
    description="Learn the basics of Flask web framework",
    order=0,
    lessons=[],  # List of Lesson objects
    difficulty="beginner",
    duration_hours=5.5,
    learning_objectives=[
        "Understand Flask application structure",
        "Create routes and views",
        "Handle HTTP requests and responses"
    ]
)
```

### Lesson

A single educational unit focused on teaching one concept or pattern.

```python
@dataclass
class Lesson:
    lesson_id: str                              # Unique lesson identifier (UUID)
    title: str                                  # Lesson title
    description: str                            # Lesson description
    order: int                                  # Lesson order in module (0-indexed)
    difficulty: str                             # "beginner", "intermediate", or "advanced"
    duration_minutes: int                       # Lesson duration in minutes
    file_path: str                              # Source file this lesson is based on
    teaching_value: float                       # Teaching value score (0.0-1.0)
    learning_objectives: List[str]              # Lesson learning objectives
    prerequisites: List[str]                    # Prerequisite lesson IDs
    concepts: List[str]                         # Concepts covered in lesson
    content: Optional[LessonContent]            # Lesson content (None until generated)
    exercises: List[Exercise]                   # List of exercises
    tags: List[str]                             # Lesson tags
```

**Example:**
```python
from src.course.models import Lesson

lesson = Lesson(
    lesson_id="770e8400-e29b-41d4-a716-446655440002",
    title="Creating Your First Flask Route",
    description="Learn how to create routes in Flask",
    order=0,
    difficulty="beginner",
    duration_minutes=30,
    file_path="src/app.py",
    teaching_value=0.85,
    learning_objectives=[
        "Understand Flask routing",
        "Create GET and POST routes",
        "Return responses"
    ],
    prerequisites=[],
    concepts=["routing", "decorators", "http_methods"],
    content=None,  # Generated later
    exercises=[],  # Generated later
    tags=["flask", "routing", "web"]
)
```

### LessonContent

The actual lesson content with all sections.

```python
@dataclass
class LessonContent:
    introduction: str                           # Lesson introduction text
    explanation: str                            # Detailed explanation
    code_example: CodeExample                   # Code example with annotations
    walkthrough: str                            # Step-by-step code walkthrough
    summary: str                                # Lesson summary
    further_reading: List[str]                  # Further reading suggestions
```

### CodeExample

A code example with syntax highlighting and annotations.

```python
@dataclass
class CodeExample:
    code: str                                   # Source code content
    language: str                               # Programming language (e.g., "python")
    filename: str                               # Source filename
    highlights: List[CodeHighlight]             # Highlighted code sections
    annotations: Dict[int, str]                 # Line number -> annotation text
```

**Example:**
```python
from src.course.models import CodeExample, CodeHighlight

code_example = CodeExample(
    code="""from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'
""",
    language="python",
    filename="app.py",
    highlights=[
        CodeHighlight(
            start_line=5,
            end_line=7,
            description="Route decorator and handler function"
        )
    ],
    annotations={
        1: "Import Flask class",
        3: "Create Flask application instance",
        5: "Define route for root URL"
    }
)
```

### CodeHighlight

A highlighted section of code.

```python
@dataclass
class CodeHighlight:
    start_line: int                             # Starting line number (1-indexed)
    end_line: int                               # Ending line number (inclusive)
    description: str                            # Description of highlighted section
```

### Exercise

A coding exercise for students to practice concepts.

```python
@dataclass
class Exercise:
    exercise_id: str                            # Unique exercise identifier (UUID)
    title: str                                  # Exercise title
    description: str                            # Exercise description
    difficulty: str                             # "beginner", "intermediate", or "advanced"
    estimated_minutes: int                      # Estimated completion time
    instructions: List[str]                     # Step-by-step instructions
    starter_code: str                           # Starter code with TODOs
    solution_code: str                          # Complete solution code
    hints: List[str]                            # Progressive hints
    test_cases: List[TestCase]                  # Test cases for validation
    learning_objectives: List[str]              # Exercise learning objectives
```

**Example:**
```python
from src.course.models import Exercise, TestCase

exercise = Exercise(
    exercise_id="880e8400-e29b-41d4-a716-446655440003",
    title="Practice: Create a Flask Route",
    description="Create a Flask route that returns JSON data",
    difficulty="beginner",
    estimated_minutes=20,
    instructions=[
        "Import Flask and jsonify",
        "Create a Flask app instance",
        "Define a route at /api/data",
        "Return JSON response with sample data"
    ],
    starter_code="""from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    # TODO: Return JSON response
    pass
""",
    solution_code="""from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    return jsonify({'message': 'Hello', 'status': 'success'})
""",
    hints=[
        "Use the jsonify function to create JSON responses",
        "Return a dictionary with 'message' and 'status' keys"
    ],
    test_cases=[
        TestCase(
            input="GET /api/data",
            expected_output="{'message': 'Hello', 'status': 'success'}",
            description="Test successful API call"
        )
    ],
    learning_objectives=["Create JSON API endpoints"]
)
```

### TestCase

A test case for validating exercise solutions.

```python
@dataclass
class TestCase:
    input: str                                  # Test input description
    expected_output: str                        # Expected output description
    description: str                            # Test case description
```

---

## Core Classes

### CourseStructureGenerator

Generates course structure from codebase analysis results.

**Location:** `src/course/structure_generator.py`

#### Constructor

```python
def __init__(self, config: CourseConfig, course_cache=None):
    """
    Initialize the course structure generator.
    
    Args:
        config: Course generation configuration
        course_cache: Optional CourseCacheManager for caching
    """
```

#### Methods

##### `generate_course_structure()`

Generate a complete course structure from analysis results.

```python
async def generate_course_structure(self, analysis: CodebaseAnalysis) -> CourseOutline:
    """
    Generate a complete course structure from analysis results.
    
    This method implements Requirements 1.1, 1.2, 1.3, 1.4, 1.5:
    - Creates CourseOutline with modules organized by difficulty
    - Sorts lessons by teaching value score
    - Creates 3-8 modules based on teachable files
    - Groups lessons by related patterns
    - Estimates total course duration
    
    Args:
        analysis: Codebase analysis results
        
    Returns:
        CourseOutline with modules and lessons
        
    Raises:
        ValueError: If analysis is invalid or empty
    """
```

**Example:**
```python
from src.course.structure_generator import CourseStructureGenerator
from src.course.config import CourseConfig

config = CourseConfig(target_audience="intermediate")
generator = CourseStructureGenerator(config)

# Assuming you have analysis results
course_outline = await generator.generate_course_structure(analysis)

print(f"Generated course: {course_outline.title}")
print(f"Modules: {len(course_outline.modules)}")
print(f"Total lessons: {sum(len(m.lessons) for m in course_outline.modules)}")
```

##### `group_by_patterns()`

Group files by detected patterns and concepts.

```python
def group_by_patterns(
    self, 
    teachable_files: List[Tuple[str, float]], 
    analysis: CodebaseAnalysis
) -> List[List[Tuple[str, float, FileAnalysis]]]:
    """
    Group files by detected patterns and concepts.
    
    Args:
        teachable_files: List of (file_path, teaching_value) tuples
        analysis: Codebase analysis results
        
    Returns:
        List of file groups, each containing (file_path, teaching_value, FileAnalysis)
    """
```

##### `calculate_module_count()`

Calculate optimal number of modules based on file count.

```python
def calculate_module_count(self, num_teachable_files: int) -> int:
    """
    Calculate optimal number of modules based on file count.
    
    Args:
        num_teachable_files: Number of files with sufficient teaching value
        
    Returns:
        Number of modules to create (between min_modules and max_modules)
    """
```

##### `sort_by_difficulty()`

Sort modules by difficulty level.

```python
def sort_by_difficulty(self, modules: List[Module]) -> List[Module]:
    """
    Sort modules by difficulty level (beginner → intermediate → advanced).
    
    Args:
        modules: List of modules to sort
        
    Returns:
        Sorted list of modules
    """
```

##### `adjust_content_complexity()`

Adjust lesson content complexity based on target audience.

```python
def adjust_content_complexity(self, lesson: Lesson) -> Lesson:
    """
    Adjust lesson content complexity based on target audience.
    
    Implements Task 13.2: Audience filtering and content adjustment.
    
    Args:
        lesson: Lesson to adjust
        
    Returns:
        Adjusted lesson
    """
```

---

### LessonContentGenerator

Generates educational lesson content from file analysis results.

**Location:** `src/course/content_generator.py`

#### Constructor

```python
def __init__(self, config: CourseConfig, course_cache=None):
    """
    Initialize the lesson content generator.
    
    Args:
        config: Course generation configuration
        course_cache: Optional CourseCacheManager for caching
    """
```

#### Methods

##### `generate_lesson_content()`

Generate complete lesson content from file analysis.

```python
async def generate_lesson_content(self, file_analysis: FileAnalysis) -> LessonContent:
    """
    Generate complete lesson content from file analysis.
    
    Implements Requirements 2.1, 2.2, 2.3, 2.4, 2.5.
    
    Args:
        file_analysis: Analysis results for the source file
        
    Returns:
        Complete LessonContent with all sections
        
    Raises:
        ValueError: If file_analysis is invalid
        FileNotFoundError: If source file cannot be read
    """
```

**Example:**
```python
from src.course.content_generator import LessonContentGenerator
from src.course.config import CourseConfig

config = CourseConfig(
    use_simple_language=True,
    include_annotations=True,
    max_code_lines=50
)
generator = LessonContentGenerator(config)

# Assuming you have file analysis
lesson_content = await generator.generate_lesson_content(file_analysis)

print(f"Introduction: {lesson_content.introduction[:100]}...")
print(f"Code language: {lesson_content.code_example.language}")
print(f"Annotations: {len(lesson_content.code_example.annotations)}")
```

##### `extract_code_example()`

Extract relevant code example from file analysis.

```python
def extract_code_example(self, file_analysis: FileAnalysis) -> CodeExample:
    """
    Extract relevant code example from file analysis.
    
    Implements Requirement 2.1: Extracts code with syntax highlighting.
    
    Args:
        file_analysis: Analysis results for the source file
        
    Returns:
        CodeExample with code, language, and metadata
    """
```

##### `generate_objectives()`

Generate learning objectives from patterns and symbols.

```python
def generate_objectives(self, file_analysis: FileAnalysis) -> List[str]:
    """
    Generate learning objectives from patterns and symbols.
    
    Implements Requirement 2.2: Generates 3-5 learning objectives.
    
    Args:
        file_analysis: Analysis results for the source file
        
    Returns:
        List of 3-5 learning objectives using action verbs
    """
```

##### `generate_introduction()`

Generate lesson introduction.

```python
def generate_introduction(
    self,
    file_analysis: FileAnalysis,
    objectives: List[str]
) -> str:
    """
    Generate lesson introduction.
    
    Args:
        file_analysis: Analysis results for the source file
        objectives: Learning objectives for the lesson
        
    Returns:
        Introduction text in Markdown format
    """
```

##### `generate_explanation()`

Generate explanation of the code and concepts.

```python
def generate_explanation(self, file_analysis: FileAnalysis) -> str:
    """
    Generate explanation of the code and concepts.
    
    Implements Requirements 2.4, 7.1: Uses simple language appropriate
    for target difficulty level.
    
    Args:
        file_analysis: Analysis results for the source file
        
    Returns:
        Explanation text in Markdown format
    """
```

##### `generate_walkthrough()`

Generate step-by-step code walkthrough.

```python
def generate_walkthrough(
    self,
    code_example: CodeExample,
    file_analysis: FileAnalysis
) -> str:
    """
    Generate step-by-step code walkthrough.
    
    Implements Requirements 2.3, 2.4: Creates walkthrough with annotations.
    
    Args:
        code_example: The code example to walk through
        file_analysis: Analysis results for the source file
        
    Returns:
        Walkthrough text in Markdown format
    """
```

##### `generate_summary()`

Generate lesson summary.

```python
def generate_summary(
    self,
    objectives: List[str],
    file_analysis: FileAnalysis
) -> str:
    """
    Generate lesson summary.
    
    Args:
        objectives: Learning objectives for the lesson
        file_analysis: Analysis results for the source file
        
    Returns:
        Summary text in Markdown format
    """
```

---

### ExerciseGenerator

Generates coding exercises from detected patterns.

**Location:** `src/course/exercise_generator.py`

#### Constructor

```python
def __init__(self, config: CourseConfig, course_cache=None):
    """
    Initialize the exercise generator.
    
    Args:
        config: Course generation configuration
        course_cache: Optional CourseCacheManager for caching
    """
```

#### Methods

##### `generate_exercise()`

Generate a coding exercise from a detected pattern.

```python
async def generate_exercise(
    self, 
    pattern: DetectedPattern, 
    file_analysis: FileAnalysis
) -> Exercise:
    """
    Generate a coding exercise from a detected pattern.
    
    Implements Requirements 3.1, 3.2, 3.3, 3.4, 3.5.
    
    Args:
        pattern: Detected pattern to create exercise from
        file_analysis: File analysis containing the pattern
        
    Returns:
        Exercise with starter code, solution, hints, and test cases
        
    Raises:
        ValueError: If pattern or file_analysis is invalid
    """
```

**Example:**
```python
from src.course.exercise_generator import ExerciseGenerator
from src.course.config import CourseConfig

config = CourseConfig(max_exercises_per_lesson=3)
generator = ExerciseGenerator(config)

# Assuming you have a pattern and file analysis
exercise = await generator.generate_exercise(pattern, file_analysis)

print(f"Exercise: {exercise.title}")
print(f"Difficulty: {exercise.difficulty}")
print(f"Estimated time: {exercise.estimated_minutes} minutes")
print(f"Instructions: {len(exercise.instructions)} steps")
print(f"Hints: {len(exercise.hints)} available")
```

##### `generate_exercises_for_lesson()`

Generate 1-3 exercises for a lesson based on complexity.

```python
async def generate_exercises_for_lesson(
    self, 
    file_analysis: FileAnalysis, 
    max_exercises: int = 3
) -> List[Exercise]:
    """
    Generate 1-3 exercises for a lesson based on complexity.
    
    Implements Requirement 3.4: Creates 1-3 exercises per lesson.
    
    Args:
        file_analysis: File analysis to generate exercises from
        max_exercises: Maximum number of exercises to generate
        
    Returns:
        List of exercises (1-3 based on complexity)
    """
```

---

### TemplateEngine

Renders content using Jinja2 templates.

**Location:** `src/course/template_engine.py`

#### Constructor

```python
def __init__(self, config: CourseConfig):
    """
    Initialize the template engine.
    
    Args:
        config: Course generation configuration
    """
```

#### Methods

##### `render_template()`

Render a template with provided context.

```python
def render_template(self, template_name: str, **context) -> str:
    """
    Render a template with provided context.
    
    Args:
        template_name: Name of template file (e.g., "lesson.md.j2")
        **context: Template variables
        
    Returns:
        Rendered template as string
        
    Raises:
        TemplateNotFound: If template file doesn't exist
        TemplateSyntaxError: If template has syntax errors
    """
```

**Example:**
```python
from src.course.template_engine import TemplateEngine
from src.course.config import CourseConfig

config = CourseConfig(template_dir="my_templates")
engine = TemplateEngine(config)

# Render lesson template
rendered = engine.render_template(
    "lesson.md.j2",
    lesson=lesson_object,
    module=module_object
)

print(rendered)
```

##### `validate_template()`

Validate template syntax.

```python
def validate_template(self, template_name: str) -> bool:
    """
    Validate template syntax.
    
    Args:
        template_name: Name of template file
        
    Returns:
        True if template is valid
        
    Raises:
        TemplateSyntaxError: If template has syntax errors
    """
```

---

## MCP Tools

The Course Generator provides MCP tools for AI assistant integration. These tools are designed to be called via the Model Context Protocol.

**Note:** MCP tool implementations are planned for Task 8.5. The following describes the intended API.

### export_course

Export a complete course to a specified format.

```python
@mcp.tool()
async def export_course(
    codebase_id: str,
    format: str = "mkdocs",
    output_dir: str = "output/course",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Export a complete course from codebase analysis.
    
    Args:
        codebase_id: Identifier for the analyzed codebase
        format: Export format ("mkdocs", "json", "markdown", "nextjs", "pdf")
        output_dir: Output directory path
        config: Optional course configuration overrides
        
    Returns:
        Dictionary with export results:
        {
            "success": bool,
            "course_id": str,
            "title": str,
            "modules": int,
            "lessons": int,
            "output_path": str,
            "format": str,
            "duration_hours": float
        }
        
    Raises:
        ValueError: If codebase_id not found or format invalid
        IOError: If output directory not writable
    """
```

**Example Usage:**
```python
# Via MCP protocol
result = await export_course(
    codebase_id="my_project",
    format="mkdocs",
    output_dir="output/my_course",
    config={
        "target_audience": "intermediate",
        "course_focus": "patterns"
    }
)

print(f"Exported {result['lessons']} lessons to {result['output_path']}")
```

### generate_lesson_outline

Generate a lesson outline for a specific file.

```python
@mcp.tool()
async def generate_lesson_outline(
    file_path: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a lesson outline for a specific file.
    
    Args:
        file_path: Path to source file
        config: Optional course configuration overrides
        
    Returns:
        Dictionary with lesson outline:
        {
            "success": bool,
            "lesson_id": str,
            "title": str,
            "difficulty": str,
            "duration_minutes": int,
            "learning_objectives": List[str],
            "concepts": List[str],
            "teaching_value": float,
            "exercises_count": int
        }
        
    Raises:
        FileNotFoundError: If file_path doesn't exist
        ValueError: If file cannot be analyzed
    """
```

**Example Usage:**
```python
# Via MCP protocol
result = await generate_lesson_outline(
    file_path="src/app.py",
    config={"target_audience": "beginner"}
)

print(f"Lesson: {result['title']}")
print(f"Objectives: {', '.join(result['learning_objectives'])}")
```

### create_exercise

Create a coding exercise from a pattern.

```python
@mcp.tool()
async def create_exercise(
    pattern_type: str,
    file_path: Optional[str] = None,
    difficulty: str = "intermediate",
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a coding exercise from a pattern.
    
    Args:
        pattern_type: Type of pattern to create exercise for
        file_path: Optional source file containing the pattern
        difficulty: Exercise difficulty level
        config: Optional course configuration overrides
        
    Returns:
        Dictionary with exercise details:
        {
            "success": bool,
            "exercise_id": str,
            "title": str,
            "difficulty": str,
            "estimated_minutes": int,
            "instructions": List[str],
            "starter_code": str,
            "hints_count": int,
            "test_cases_count": int
        }
        
    Raises:
        ValueError: If pattern_type invalid or not found
    """
```

**Example Usage:**
```python
# Via MCP protocol
result = await create_exercise(
    pattern_type="factory_pattern",
    file_path="src/factory.py",
    difficulty="intermediate"
)

print(f"Exercise: {result['title']}")
print(f"Time: {result['estimated_minutes']} minutes")
print(f"Steps: {len(result['instructions'])}")
```

---

## Exporters

### MkDocsExporter

Export courses to MkDocs format.

**Location:** `src/course/exporters/mkdocs_exporter.py`

```python
class MkDocsExporter:
    def __init__(self, config: CourseConfig):
        """Initialize MkDocs exporter."""
        
    async def export(self, course: CourseOutline, output_dir: str) -> None:
        """
        Export course to MkDocs format.
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            
        Raises:
            IOError: If output directory not writable
        """
```

### JSONExporter

Export courses to JSON format.

**Location:** `src/course/exporters/json_exporter.py`

```python
class JSONExporter:
    def __init__(self, config: CourseConfig):
        """Initialize JSON exporter."""
        
    async def export(self, course: CourseOutline, output_file: str) -> None:
        """
        Export course to JSON format.
        
        Args:
            course: Course outline to export
            output_file: Output file path
            
        Raises:
            IOError: If output file cannot be written
        """
```

### MarkdownExporter

Export courses to standalone Markdown files.

**Location:** `src/course/exporters/markdown_exporter.py`

```python
class MarkdownExporter:
    def __init__(self, config: CourseConfig):
        """Initialize Markdown exporter."""
        
    async def export(self, course: CourseOutline, output_dir: str) -> None:
        """
        Export course to Markdown format.
        
        Args:
            course: Course outline to export
            output_dir: Output directory path
            
        Raises:
            IOError: If output directory not writable
        """
```

### ExportManager

Unified interface for all export formats.

**Location:** `src/course/exporters/export_manager.py`

```python
class ExportManager:
    def __init__(self, config: CourseConfig):
        """Initialize export manager."""
        
    async def export(
        self, 
        course: CourseOutline, 
        output_path: str, 
        format: str
    ) -> None:
        """
        Export course to specified format.
        
        Args:
            course: Course outline to export
            output_path: Output path (file or directory)
            format: Export format ("mkdocs", "json", "markdown", "nextjs", "pdf")
            
        Raises:
            ValueError: If format is invalid
            IOError: If output path not writable
        """
```

---

## Utilities

### CourseConfig

Configuration class for course generation.

**Location:** `src/course/config.py`

See [Configuration Guide](./COURSE_CONFIGURATION.md) for complete documentation.

```python
@dataclass
class CourseConfig:
    target_audience: str = "mixed"
    course_focus: str = "full-stack"
    max_duration_hours: Optional[float] = None
    template_dir: Optional[str] = None
    # ... (see configuration guide for all options)
    
    def validate(self) -> bool:
        """Validate configuration settings."""
```

### PerformanceMonitor

Monitor course generation performance.

**Location:** `src/course/performance_monitor.py`

```python
class PerformanceMonitor:
    def measure(self, operation: str, **metadata) -> ContextManager:
        """
        Measure operation performance.
        
        Args:
            operation: Operation name
            **metadata: Additional metadata
            
        Returns:
            Context manager for timing
        """
```

**Example:**
```python
from src.course.performance_monitor import get_monitor

monitor = get_monitor()

with monitor.measure("course_generation", file_count=100):
    # Generate course
    course = await generator.generate_course_structure(analysis)

# Get statistics
stats = monitor.get_stats()
print(f"Average time: {stats['course_generation']['avg_time']:.2f}s")
```

---

## Error Handling

All Course Generator methods follow consistent error handling patterns:

### Common Exceptions

- **ValueError**: Invalid input parameters or configuration
- **FileNotFoundError**: Source file not found
- **IOError**: File system errors (read/write failures)
- **TemplateNotFound**: Template file not found
- **TemplateSyntaxError**: Template syntax errors

### Example Error Handling

```python
from src.course.structure_generator import CourseStructureGenerator
from src.course.config import CourseConfig

try:
    config = CourseConfig(target_audience="invalid")
    config.validate()
except ValueError as e:
    print(f"Invalid configuration: {e}")

try:
    generator = CourseStructureGenerator(config)
    course = await generator.generate_course_structure(analysis)
except ValueError as e:
    print(f"Generation failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Type Hints

All Course Generator code uses Python type hints for better IDE support and type checking:

```python
from typing import List, Dict, Optional, Tuple
from src.course.models import CourseOutline, Module, Lesson
from src.course.config import CourseConfig

async def generate_course(
    analysis: CodebaseAnalysis,
    config: CourseConfig
) -> CourseOutline:
    """Type hints provide IDE autocomplete and type checking."""
    pass
```

Use `mypy` for static type checking:

```bash
mypy src/course/
```

---

## See Also

- [Configuration Guide](./COURSE_CONFIGURATION.md) - Complete configuration reference
- [Usage Examples](../examples/course_generator_example.py) - Practical examples
- [MCP Tools Guide](./COURSE_MCP_TOOLS.md) - MCP integration guide
- [Template Guide](./COURSE_TEMPLATES.md) - Template customization guide
