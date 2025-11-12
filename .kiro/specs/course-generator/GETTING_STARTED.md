# Getting Started with Course Generator Implementation

## Quick Start

Ready to build the Course Generator? Here's how to get started.

## Step 1: Review the Spec

Before coding, familiarize yourself with:

1. **README.md** - Overview and architecture
2. **requirements.md** - What we're building (15 requirements)
3. **design.md** + **design-part2.md** - How we're building it
4. **tasks.md** - Step-by-step implementation plan

**Time**: 30-60 minutes

## Step 2: Set Up Your Environment

### Create Directory Structure

```powershell
# Create course generator directories
New-Item -ItemType Directory -Path "src/course" -Force
New-Item -ItemType Directory -Path "src/course/generators" -Force
New-Item -ItemType Directory -Path "src/course/templates" -Force
New-Item -ItemType Directory -Path "src/course/exporters" -Force
New-Item -ItemType Directory -Path "tests/course" -Force
```

### Install Dependencies

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install required packages
.\venv\Scripts\python.exe -m pip install jinja2 pyyaml markdown

# Optional: Install for PDF export
.\venv\Scripts\python.exe -m pip install weasyprint
```

## Step 3: Start with Task 1

### Task 1: Set up Project Structure

Create the foundational files:

**1. Create data models** (`src/course/models.py`):
```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class CourseOutline:
    """Complete course structure."""
    course_id: str
    title: str
    description: str
    modules: List['Module']
    # ... (see design.md for complete model)

@dataclass
class Module:
    """A collection of related lessons."""
    module_id: str
    title: str
    lessons: List['Lesson']
    # ... (see design.md)

@dataclass
class Lesson:
    """A single educational unit."""
    lesson_id: str
    title: str
    content: 'LessonContent'
    # ... (see design.md)

# Add remaining models from design.md
```

**2. Create configuration** (`src/course/config.py`):
```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CourseConfig:
    """Configuration for course generation."""
    target_audience: str = "mixed"  # beginner, intermediate, advanced, mixed
    course_focus: str = "patterns"  # patterns, architecture, best-practices, full-stack
    max_duration_hours: Optional[float] = None
    template_dir: Optional[str] = None
    min_teaching_value: float = 5.0
    max_lessons_per_module: int = 5
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'CourseConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})
```

**3. Create package init** (`src/course/__init__.py`):
```python
"""Course Generator package."""

from .models import CourseOutline, Module, Lesson, Exercise
from .config import CourseConfig

__all__ = [
    'CourseOutline',
    'Module',
    'Lesson',
    'Exercise',
    'CourseConfig',
]
```

## Step 4: Implement Course Structure Generator (Task 2)

**Create** `src/course/generators/course_structure.py`:

```python
"""Course structure generator."""

import logging
from typing import List, Tuple
from datetime import datetime

from src.models.analysis_models import CodebaseAnalysis, FileAnalysis
from src.course.models import CourseOutline, Module, Lesson
from src.course.config import CourseConfig

logger = logging.getLogger(__name__)


class CourseStructureGenerator:
    """Generates course structure from codebase analysis."""
    
    def __init__(self, config: CourseConfig):
        """Initialize generator with configuration."""
        self.config = config
    
    def generate_course_structure(
        self,
        analysis: CodebaseAnalysis
    ) -> CourseOutline:
        """
        Generate course structure from analysis.
        
        Args:
            analysis: Codebase analysis results
        
        Returns:
            CourseOutline with modules and lessons
        """
        logger.info(f"Generating course structure for {analysis.codebase_id}")
        
        # 1. Extract teachable files
        teachable_files = self._extract_teachable_files(analysis)
        logger.info(f"Found {len(teachable_files)} teachable files")
        
        # 2. Group files by patterns
        grouped_files = self._group_by_patterns(teachable_files, analysis)
        
        # 3. Determine module count
        module_count = self._calculate_module_count(len(teachable_files))
        logger.info(f"Creating {module_count} modules")
        
        # 4. Create modules
        modules = self._create_modules(grouped_files, module_count, analysis)
        
        # 5. Sort by difficulty
        modules = self._sort_by_difficulty(modules)
        
        # 6. Create course outline
        course = CourseOutline(
            course_id=self._generate_course_id(analysis),
            title=self._generate_title(analysis),
            description=self._generate_description(analysis),
            author="Documee Course Generator",
            version="1.0.0",
            created_at=datetime.now(),
            modules=modules,
            total_duration_hours=sum(m.duration_hours for m in modules),
            difficulty_distribution=self._calculate_difficulty_distribution(modules),
            tags=self._extract_tags(analysis),
            prerequisites=[]
        )
        
        logger.info(
            f"Course structure generated: {len(modules)} modules, "
            f"{sum(len(m.lessons) for m in modules)} lessons"
        )
        
        return course
    
    def _extract_teachable_files(
        self,
        analysis: CodebaseAnalysis
    ) -> List[Tuple[str, float]]:
        """Extract files with high teaching value."""
        # Filter by minimum teaching value
        teachable = [
            (file_path, score)
            for file_path, score in analysis.top_teaching_files
            if score >= self.config.min_teaching_value
        ]
        
        # Sort by teaching value (descending)
        return sorted(teachable, key=lambda x: x[1], reverse=True)
    
    def _group_by_patterns(
        self,
        teachable_files: List[Tuple[str, float]],
        analysis: CodebaseAnalysis
    ) -> List[List[Tuple[str, float]]]:
        """Group files by detected patterns."""
        # TODO: Implement pattern-based grouping
        # For now, simple chunking
        chunk_size = max(1, len(teachable_files) // 5)
        return [
            teachable_files[i:i + chunk_size]
            for i in range(0, len(teachable_files), chunk_size)
        ]
    
    def _calculate_module_count(self, file_count: int) -> int:
        """Calculate optimal number of modules (3-8)."""
        if file_count <= 10:
            return 3
        elif file_count <= 20:
            return 4
        elif file_count <= 40:
            return 5
        elif file_count <= 60:
            return 6
        elif file_count <= 80:
            return 7
        else:
            return 8
    
    def _create_modules(
        self,
        grouped_files: List[List[Tuple[str, float]]],
        module_count: int,
        analysis: CodebaseAnalysis
    ) -> List[Module]:
        """Create modules from grouped files."""
        modules = []
        
        for i, file_group in enumerate(grouped_files[:module_count]):
            module = Module(
                module_id=f"module_{i+1}",
                title=f"Module {i+1}",  # TODO: Generate better titles
                description="",  # TODO: Generate descriptions
                order=i,
                lessons=[],  # TODO: Create lessons
                difficulty="intermediate",  # TODO: Calculate difficulty
                duration_hours=0.0,  # TODO: Calculate duration
                learning_objectives=[]  # TODO: Generate objectives
            )
            modules.append(module)
        
        return modules
    
    def _sort_by_difficulty(self, modules: List[Module]) -> List[Module]:
        """Sort modules by difficulty (beginner → advanced)."""
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        return sorted(modules, key=lambda m: difficulty_order.get(m.difficulty, 1))
    
    def _generate_course_id(self, analysis: CodebaseAnalysis) -> str:
        """Generate unique course ID."""
        return f"course_{analysis.codebase_id}"
    
    def _generate_title(self, analysis: CodebaseAnalysis) -> str:
        """Generate course title from codebase."""
        # TODO: Generate better titles from codebase name
        return f"Course: {analysis.codebase_id}"
    
    def _generate_description(self, analysis: CodebaseAnalysis) -> str:
        """Generate course description."""
        return f"Learn from {analysis.metrics.total_files} files with {analysis.metrics.total_functions} functions."
    
    def _calculate_difficulty_distribution(
        self,
        modules: List[Module]
    ) -> Dict[str, int]:
        """Calculate difficulty distribution."""
        distribution = {"beginner": 0, "intermediate": 0, "advanced": 0}
        for module in modules:
            distribution[module.difficulty] = distribution.get(module.difficulty, 0) + 1
        return distribution
    
    def _extract_tags(self, analysis: CodebaseAnalysis) -> List[str]:
        """Extract tags from analysis."""
        # TODO: Extract tags from patterns
        return []
```

## Step 5: Test Your Implementation

**Create** `tests/course/test_course_structure.py`:

```python
"""Tests for course structure generator."""

import pytest
from src.course.generators.course_structure import CourseStructureGenerator
from src.course.config import CourseConfig
from src.models.analysis_models import CodebaseAnalysis, CodebaseMetrics

def test_course_structure_generation():
    """Test basic course structure generation."""
    # Create mock analysis
    analysis = CodebaseAnalysis(
        codebase_id="test_codebase",
        file_analyses={},
        dependency_graph=None,
        global_patterns=[],
        top_teaching_files=[
            ("file1.py", 9.5),
            ("file2.py", 8.7),
            ("file3.py", 7.2),
        ],
        metrics=CodebaseMetrics(
            total_files=3,
            total_functions=10,
            total_classes=5,
            avg_complexity=5.0,
            avg_documentation_coverage=0.8,
            total_patterns_detected=5,
            analysis_time_ms=1000.0,
            cache_hit_rate=0.0
        ),
        analyzed_at="2025-11-12"
    )
    
    # Generate course structure
    config = CourseConfig()
    generator = CourseStructureGenerator(config)
    course = generator.generate_course_structure(analysis)
    
    # Validate
    assert course is not None
    assert course.course_id == "course_test_codebase"
    assert len(course.modules) >= 3
    assert len(course.modules) <= 8

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run the test**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/course/test_course_structure.py -v
```

## Step 6: Continue with Remaining Tasks

Follow `tasks.md` in order:
1. ✅ Task 1: Project structure (done above)
2. ✅ Task 2: Course structure generator (started above)
3. ⏭️ Task 3: Lesson content generator
4. ⏭️ Task 4: Exercise generator
5. ⏭️ Task 5: Template engine
6. ⏭️ Task 6: MkDocs export
7. ⏭️ Task 7: Multi-format export
8. ⏭️ Task 8: MCP tools
9. ⏭️ Tasks 9-14: Validation, optimization, documentation

## Tips for Success

### 1. Build Incrementally
- Complete one task at a time
- Test after each task
- Don't skip ahead

### 2. Use the Analysis Engine
- The Analysis Engine provides all the data you need
- Reference `src/analysis/` for examples
- Reuse patterns from the Analysis Engine

### 3. Test with Real Codebases
- Test with your own projects
- Start with small codebases (10-20 files)
- Gradually test with larger codebases

### 4. Follow the Design
- The design document has all the algorithms
- Copy the code patterns from design.md
- Adapt as needed for your implementation

### 5. Ask Questions
- If something is unclear, ask
- If you need to deviate from the spec, document why
- Keep the spec updated as you learn

## Common Pitfalls to Avoid

❌ **Don't**: Try to build everything at once
✅ **Do**: Build incrementally, test frequently

❌ **Don't**: Skip the data models
✅ **Do**: Start with solid data models

❌ **Don't**: Ignore the requirements
✅ **Do**: Validate against acceptance criteria

❌ **Don't**: Optimize prematurely
✅ **Do**: Get it working first, then optimize

❌ **Don't**: Skip tests
✅ **Do**: Write tests as you go

## Resources

### Documentation
- **requirements.md** - What to build
- **design.md** - How to build it
- **tasks.md** - Step-by-step plan

### Code Examples
- **src/analysis/** - Analysis Engine patterns
- **tests/analysis/** - Test patterns
- **src/tools/** - MCP tool patterns

### External Resources
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

## Getting Help

If you get stuck:
1. Review the design document
2. Check the Analysis Engine for similar patterns
3. Look at the test files for examples
4. Ask for clarification on requirements

## Success Checklist

Before moving to the next task, ensure:
- ✅ Code is written and tested
- ✅ Tests pass
- ✅ Acceptance criteria met
- ✅ Code is documented
- ✅ No obvious bugs

## Ready to Start?

You have everything you need:
- ✅ Complete specification
- ✅ Clear requirements
- ✅ Detailed design
- ✅ Step-by-step tasks
- ✅ Code examples
- ✅ Test patterns

**Let's build the Course Generator!** 🚀

---

**Next Step**: Create `src/course/models.py` with data models
**Estimated Time**: 30 minutes
**Difficulty**: Easy
