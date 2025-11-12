# Design Document - Course Generator

## Overview

The Course Generator is the content generation layer of Documee that transforms codebase analysis results into structured educational courses. It bridges the gap between code analysis and teaching by automatically creating lesson outlines, exercises, and complete course materials in multiple formats (MkDocs, Next.js, JSON, Markdown).

**Key Innovation**: Every feature in the codebase becomes a lesson in the course. The Course Generator uses teaching value scores, pattern detection, and complexity metrics from the Analysis Engine to automatically create a logical learning progression.

### Architecture

```
Course Generator Architecture:
┌─────────────────────────────────────────────────────────────┐
│                     MCP Tools Layer                          │
│  export_course | generate_lesson_outline | create_exercise  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Course Generator Core                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Course     │  │   Lesson     │  │   Exercise   │     │
│  │  Structure   │  │   Content    │  │  Generator   │     │
│  │  Generator   │  │  Generator   │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Template Engine (Jinja2)                  │
│         Verified API: Environment, DictLoader, Filters      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Export Layer                              │
│  MkDocs (Primary) | Next.js | JSON | Markdown              │
│  Verified API: mkdocs.yml, plugins, themes                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Analysis Engine (Input)                     │
│  CodebaseAnalysis | TeachableCode | Patterns | Metrics     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **CourseStructureGenerator**: Organizes analysis results into modules and lessons
2. **LessonContentGenerator**: Creates educational content from code examples
3. **ExerciseGenerator**: Generates coding challenges and solutions
4. **TemplateEngine**: Renders content using Jinja2 (verified API patterns)
5. **MkDocsExporter**: Exports to MkDocs format (verified configuration patterns)
6. **ExportManager**: Handles export to multiple formats
7. **MCP Tools**: Provides AI assistant integration (FastMCP verified patterns)

### Design Principles

1. **Feature-to-Lesson Mapping**: Every feature becomes a lesson
2. **Evidence-Based Content**: All content cites actual code from the codebase
3. **Progressive Difficulty**: Lessons ordered by complexity and dependencies
4. **Hands-On Learning**: Every lesson includes practical exercises
5. **Verified APIs**: All external dependencies use Context7-verified patterns

## Data Models

### Core Models


```python
@dataclass
class CourseOutline:
    """Complete course structure with modules and lessons."""
    course_id: str
    title: str
    description: str
    author: str
    version: str
    created_at: datetime
    modules: List[Module]
    total_duration_hours: float
    difficulty_distribution: Dict[str, int]  # beginner: 5, intermediate: 10, advanced: 3
    tags: List[str]
    prerequisites: List[str]
    
@dataclass
class Module:
    """A collection of related lessons."""
    module_id: str
    title: str
    description: str
    order: int
    lessons: List[Lesson]
    difficulty: str  # beginner, intermediate, advanced
    duration_hours: float
    learning_objectives: List[str]
    
@dataclass
class Lesson:
    """A single educational unit."""
    lesson_id: str
    title: str
    description: str
    order: int
    difficulty: str
    duration_minutes: int
    file_path: str  # Source file this lesson is based on
    teaching_value: float
    learning_objectives: List[str]
    prerequisites: List[str]
    concepts: List[str]
    content: LessonContent
    exercises: List[Exercise]
    tags: List[str]
    
@dataclass
class LessonContent:
    """The actual lesson content."""
    introduction: str
    explanation: str
    code_example: CodeExample
    walkthrough: str
    summary: str
    further_reading: List[str]
    
@dataclass
class CodeExample:
    """A code example with annotations."""
    code: str
    language: str
    filename: str
    highlights: List[CodeHighlight]  # Lines to emphasize
    annotations: Dict[int, str]  # Line number -> explanation
    
@dataclass
class CodeHighlight:
    """A highlighted section of code."""
    start_line: int
    end_line: int
    description: str
    
@dataclass
class Exercise:
    """A coding exercise for students."""
    exercise_id: str
    title: str
    description: str
    difficulty: str
    estimated_minutes: int
    instructions: List[str]
    starter_code: str
    solution_code: str
    hints: List[str]
    test_cases: List[TestCase]
    learning_objectives: List[str]
    
@dataclass
class TestCase:
    """A test case for validating exercise solutions."""
    input: str
    expected_output: str
    description: str
```



## Component Design

### 1. CourseStructureGenerator

**Purpose**: Transform CodebaseAnalysis into a structured CourseOutline

**Algorithm**:
```python
def generate_course_structure(analysis: CodebaseAnalysis, config: CourseConfig) -> CourseOutline:
    # 1. Extract teachable files sorted by teaching value
    teachable_files = sorted(
        analysis.top_teaching_files,
        key=lambda x: x[1],
        reverse=True
    )
    
    # 2. Group files by patterns and concepts
    grouped_files = group_by_patterns(teachable_files, analysis.file_analyses)
    
    # 3. Determine module count (3-8 modules)
    module_count = calculate_module_count(len(teachable_files))
    
    # 4. Create modules with balanced difficulty progression
    modules = []
    for i in range(module_count):
        module_files = grouped_files[i]
        module = create_module(module_files, i, analysis)
        modules.append(module)
    
    # 5. Sort modules by difficulty (beginner → advanced)
    modules = sort_by_difficulty(modules)
    
    # 6. Create course outline
    return CourseOutline(
        course_id=generate_id(),
        title=generate_title(analysis),
        modules=modules,
        total_duration_hours=sum(m.duration_hours for m in modules)
    )
```

**Key Methods**:
- `group_by_patterns()`: Group files by detected patterns
- `calculate_module_count()`: Determine optimal module count
- `create_module()`: Create a module from grouped files
- `sort_by_difficulty()`: Order modules by difficulty
- `generate_title()`: Create course title from codebase name

### 2. LessonContentGenerator

**Purpose**: Generate educational content from TeachableCode

**Algorithm**:
```python
def generate_lesson_content(file_analysis: FileAnalysis, config: CourseConfig) -> LessonContent:
    # 1. Extract code example
    code_example = extract_code_example(file_analysis)
    
    # 2. Generate learning objectives from patterns
    objectives = generate_objectives(file_analysis.patterns, file_analysis.symbol_info)
    
    # 3. Create introduction
    introduction = generate_introduction(file_analysis, objectives)
    
    # 4. Generate explanation
    explanation = generate_explanation(file_analysis, config.target_audience)
    
    # 5. Create code walkthrough with annotations
    walkthrough = generate_walkthrough(code_example, file_analysis)
    
    # 6. Generate summary
    summary = generate_summary(objectives, file_analysis)
    
    return LessonContent(
        introduction=introduction,
        explanation=explanation,
        code_example=code_example,
        walkthrough=walkthrough,
        summary=summary
    )
```

**Key Methods**:
- `extract_code_example()`: Get relevant code with syntax highlighting
- `generate_objectives()`: Create learning objectives from patterns
- `generate_introduction()`: Write lesson introduction
- `generate_explanation()`: Explain concepts in simple language
- `generate_walkthrough()`: Create step-by-step code explanation
- `add_annotations()`: Add inline comments to code

### 3. ExerciseGenerator

**Purpose**: Create coding exercises from patterns

**Algorithm**:
```python
def generate_exercise(pattern: DetectedPattern, file_analysis: FileAnalysis) -> Exercise:
    # 1. Identify the pattern to practice
    pattern_type = pattern.pattern_type
    
    # 2. Extract relevant code as solution
    solution_code = extract_pattern_code(pattern, file_analysis)
    
    # 3. Create starter code with TODOs
    starter_code = create_starter_code(solution_code, pattern_type)
    
    # 4. Generate instructions
    instructions = generate_instructions(pattern, pattern_type)
    
    # 5. Create hints
    hints = generate_hints(solution_code, pattern_type)
    
    # 6. Generate test cases
    test_cases = generate_test_cases(pattern, solution_code)
    
    return Exercise(
        exercise_id=generate_id(),
        title=f"Practice: {pattern_type}",
        starter_code=starter_code,
        solution_code=solution_code,
        instructions=instructions,
        hints=hints,
        test_cases=test_cases
    )
```

**Key Methods**:
- `extract_pattern_code()`: Get code demonstrating the pattern
- `create_starter_code()`: Remove implementation, add TODOs
- `generate_instructions()`: Create step-by-step guidance
- `generate_hints()`: Create progressive hints
- `generate_test_cases()`: Create validation tests



### 4. TemplateEngine

**Purpose**: Render content using Jinja2 templates

**Templates**:

**lesson.md.j2**:
```markdown
# {{ lesson.title }}

**Difficulty**: {{ lesson.difficulty }} | **Duration**: {{ lesson.duration_minutes }} minutes

## Learning Objectives

{% for objective in lesson.learning_objectives %}
- {{ objective }}
{% endfor %}

## Introduction

{{ lesson.content.introduction }}

## Explanation

{{ lesson.content.explanation }}

## Code Example

```{{ lesson.content.code_example.language }}
{{ lesson.content.code_example.code }}
```

## Walkthrough

{{ lesson.content.walkthrough }}

## Summary

{{ lesson.content.summary }}

{% if lesson.exercises %}
## Exercises

{% for exercise in lesson.exercises %}
### {{ exercise.title }}

{{ exercise.description }}

**Difficulty**: {{ exercise.difficulty }} | **Time**: {{ exercise.estimated_minutes }} minutes

#### Instructions

{% for instruction in exercise.instructions %}
{{ loop.index }}. {{ instruction }}
{% endfor %}

#### Starter Code

```{{ lesson.content.code_example.language }}
{{ exercise.starter_code }}
```

{% endfor %}
{% endif %}
```

**exercise.md.j2**:
```markdown
# Exercise: {{ exercise.title }}

{{ exercise.description }}

**Difficulty**: {{ exercise.difficulty }} | **Estimated Time**: {{ exercise.estimated_minutes }} minutes

## Instructions

{% for instruction in exercise.instructions %}
{{ loop.index }}. {{ instruction }}
{% endfor %}

## Starter Code

```python
{{ exercise.starter_code }}
```

## Hints

<details>
<summary>Hint 1</summary>
{{ exercise.hints[0] }}
</details>

{% if exercise.hints|length > 1 %}
<details>
<summary>Hint 2</summary>
{{ exercise.hints[1] }}
</details>
{% endif %}

## Test Cases

{% for test in exercise.test_cases %}
**Test {{ loop.index }}**: {{ test.description }}
- Input: `{{ test.input }}`
- Expected: `{{ test.expected_output }}`
{% endfor %}
```

### 5. ExportManager

**Purpose**: Export courses to multiple formats

**MkDocs Export**:
```python
def export_to_mkdocs(course: CourseOutline, output_dir: str):
    # 1. Create directory structure
    create_directory_structure(output_dir)
    
    # 2. Generate mkdocs.yml
    mkdocs_config = generate_mkdocs_config(course)
    write_file(f"{output_dir}/mkdocs.yml", mkdocs_config)
    
    # 3. Generate docs/ directory with lessons
    for module in course.modules:
        module_dir = f"{output_dir}/docs/{module.title.lower().replace(' ', '-')}"
        os.makedirs(module_dir, exist_ok=True)
        
        for lesson in module.lessons:
            lesson_file = f"{module_dir}/{lesson.title.lower().replace(' ', '-')}.md"
            lesson_content = render_template("lesson.md.j2", lesson=lesson)
            write_file(lesson_file, lesson_content)
    
 


```r)lt=stauefent=2, dct, f, indp(course_di   json.dum    :
  'w') as fput_file,pen(out  with oma
   with scheSON Write J #
   }
    
         ]dules
   moe. cours    for m in              }
      ]
               ons
 l in m.less      for         
        }          ]
        esl.exercise in __ for  [e.__dicts":se    "exerci               ct__,
     _dil.content._nt": te   "con                 tle,
     l.ti"title":                       
 id,n_d": l.lesson_i "lesso                  {
                 
        ssons": [le  "           itle,
   title": m.t "               d,
: m.module_iule_id"    "mod           {
           
  les": [modu    "ption,
    e.descri courson":"descripti     title,
   ": course.letit
        "se_id,urcoourse. course_id":        "cdict = {
  course_t
  o dicurse t# Convert co    tr):
t_file: sine, outpuutl: CourseOson(courset_to_j expor
def``pythont**:
`JSON Expor}
```

**{% endfor %ndfor %}

    {% emd, '-') }}.eplace(' ').rower(tle.lson.ti/{{ les}}', '-') eplace(' .rwer()itle.lo{{ module.t: tle }}esson.ti   - {{ lns %}
 ule.lesso in modfor lesson}:
    {% dule.title }{ mos %}
  - {e.module coursr module in fo

nav:
{%link: true   perma
   toc:  - n
admonitio
  - x.details - pymdownrfences
 supeownx.pymdrue
  - enums: tor_lin     anchghlight:
 mdownx.hi
  - pyions:nsown_exte
markd - tags

 
  - search
plugins:
de.copyontent.co- c   highlight
 arch.   - se
 h.suggestsearc   - and
 on.exp  - navigatitions
  n.sec navigatio    -on.tabs
igatinav  - tures:
  
  fea: indigoccentigo
    arimary: ind:
    pettel
  palateriaame: meme:
  n }}

thourse.author{ cauthor: { }}
site_ription.desc{ courseption: {escri
site_dtitle }}{{ course.site_name: ```yaml
**:
Templatel s.ym

**mkdoc
```_dir)utputopy_assets(o)
    canyif assets (Copy     # 5. 
  
  tent)x_conndemd", iocs/index.}/d"{output_dirile(f
    write_fcourse)x(te_inderantent = geneindex_co   index.md
 erate en   # 4. G