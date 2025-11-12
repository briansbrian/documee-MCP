"""Configuration for Course Generator."""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class CourseConfig:
    """Configuration settings for course generation."""
    
    # Target audience level
    target_audience: str = "mixed"  # beginner, intermediate, advanced, mixed
    
    # Course focus area
    course_focus: str = "full-stack"  # patterns, architecture, best-practices, full-stack
    
    # Maximum course duration in hours
    max_duration_hours: Optional[float] = None
    
    # Custom template directory
    template_dir: Optional[str] = None
    
    # Author information
    author: str = "Documee Course Generator"
    
    # Course version
    version: str = "1.0.0"
    
    # Module count range
    min_modules: int = 3
    max_modules: int = 8
    
    # Lesson duration range (minutes)
    min_lesson_duration: int = 15
    max_lesson_duration: int = 60
    
    # Exercise settings
    min_exercises_per_lesson: int = 1
    max_exercises_per_lesson: int = 3
    
    # Code example settings
    max_code_lines: int = 50
    include_annotations: bool = True
    
    # Content generation settings
    use_simple_language: bool = True
    include_glossary: bool = True
    
    # Export settings
    default_export_format: str = "mkdocs"  # mkdocs, nextjs, json, markdown, pdf
    
    # Filtering settings
    min_teaching_value: float = 0.5  # Minimum teaching value score to include
    
    # Tags to prioritize
    priority_tags: List[str] = field(default_factory=list)
    
    # Tags to exclude
    exclude_tags: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        valid_audiences = ["beginner", "intermediate", "advanced", "mixed"]
        if self.target_audience not in valid_audiences:
            raise ValueError(f"target_audience must be one of {valid_audiences}")
        
        valid_focuses = ["patterns", "architecture", "best-practices", "full-stack"]
        if self.course_focus not in valid_focuses:
            raise ValueError(f"course_focus must be one of {valid_focuses}")
        
        if self.min_modules > self.max_modules:
            raise ValueError("min_modules cannot be greater than max_modules")
        
        if self.min_lesson_duration > self.max_lesson_duration:
            raise ValueError("min_lesson_duration cannot be greater than max_lesson_duration")
        
        if self.min_exercises_per_lesson > self.max_exercises_per_lesson:
            raise ValueError("min_exercises_per_lesson cannot be greater than max_exercises_per_lesson")
        
        if self.min_teaching_value < 0 or self.min_teaching_value > 1:
            raise ValueError("min_teaching_value must be between 0 and 1")
        
        return True
