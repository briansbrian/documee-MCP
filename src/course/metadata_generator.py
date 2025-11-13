"""Metadata Generator - Creates comprehensive metadata for courses, lessons, and exercises."""

from datetime import datetime
from typing import List, Dict, Any
from .models import CourseOutline, Module, Lesson, Exercise


class MetadataGenerator:
    """Generates metadata for courses, lessons, and exercises.
    
    This class implements Requirements 14.1, 14.2, 14.3, 14.4, 14.5:
    - Generates course metadata with title, description, author, version
    - Generates lesson metadata with difficulty, duration, prerequisites
    - Generates exercise metadata with difficulty, estimated time
    - Includes tags generated from patterns
    - Creates course manifest with all metadata
    """
    
    def generate_course_metadata(self, course: CourseOutline) -> Dict[str, Any]:
        """Generate comprehensive course metadata.
        
        Implements Requirements 14.1, 14.5:
        - Creates course manifest with all metadata
        - Includes title, description, author, version
        - Adds creation date and tags
        
        Args:
            course: CourseOutline to generate metadata for
            
        Returns:
            Dictionary containing complete course metadata
        """
        # Calculate statistics
        total_lessons = sum(len(module.lessons) for module in course.modules)
        total_exercises = sum(
            len(lesson.exercises)
            for module in course.modules
            for lesson in module.lessons
        )
        
        # Collect all unique tags
        all_tags = set(course.tags)
        for module in course.modules:
            for lesson in module.lessons:
                all_tags.update(lesson.tags)
        
        # Build metadata dictionary
        metadata = {
            # Core identification (Req 14.1)
            "course_id": course.course_id,
            "title": course.title,
            "description": course.description,
            "author": course.author,
            "version": course.version,
            
            # Timestamps (Req 14.1)
            "created_at": course.created_at.isoformat(),
            "updated_at": datetime.now().isoformat(),
            
            # Structure information
            "structure": {
                "total_modules": len(course.modules),
                "total_lessons": total_lessons,
                "total_exercises": total_exercises,
                "total_duration_hours": course.total_duration_hours,
            },
            
            # Difficulty distribution (Req 14.5)
            "difficulty_distribution": course.difficulty_distribution,
            
            # Tags and categorization (Req 14.1)
            "tags": sorted(list(all_tags)),
            "prerequisites": course.prerequisites,
            
            # Module summaries
            "modules": [
                {
                    "module_id": module.module_id,
                    "title": module.title,
                    "order": module.order,
                    "difficulty": module.difficulty,
                    "lesson_count": len(module.lessons),
                    "duration_hours": module.duration_hours,
                }
                for module in course.modules
            ],
            
            # Learning path information
            "learning_path": {
                "beginner_lessons": course.difficulty_distribution.get("beginner", 0),
                "intermediate_lessons": course.difficulty_distribution.get("intermediate", 0),
                "advanced_lessons": course.difficulty_distribution.get("advanced", 0),
            },
            
            # Schema version for compatibility
            "schema_version": "1.0.0",
        }
        
        return metadata
    
    def generate_lesson_metadata(self, lesson: Lesson, module: Module) -> Dict[str, Any]:
        """Generate comprehensive lesson metadata.
        
        Implements Requirements 14.2, 14.4:
        - Includes title, difficulty, duration
        - Adds prerequisites and learning objectives
        - Generates tags from patterns
        
        Args:
            lesson: Lesson to generate metadata for
            module: Parent module containing the lesson
            
        Returns:
            Dictionary containing complete lesson metadata
        """
        metadata = {
            # Core identification (Req 14.2)
            "lesson_id": lesson.lesson_id,
            "title": lesson.title,
            "description": lesson.description,
            
            # Position in course
            "module_id": module.module_id,
            "module_title": module.title,
            "order": lesson.order,
            
            # Difficulty and duration (Req 14.2)
            "difficulty": lesson.difficulty,
            "duration_minutes": lesson.duration_minutes,
            "estimated_completion_time": self._format_duration(lesson.duration_minutes),
            
            # Learning information (Req 14.2)
            "learning_objectives": lesson.learning_objectives,
            "prerequisites": lesson.prerequisites,
            "concepts": lesson.concepts,
            
            # Tags from patterns (Req 14.4)
            "tags": lesson.tags,
            
            # Source information
            "source_file": lesson.file_path,
            "teaching_value": lesson.teaching_value,
            
            # Content availability
            "has_content": lesson.content is not None,
            "exercise_count": len(lesson.exercises),
            
            # Additional metadata
            "metadata": {
                "complexity_level": self._map_difficulty_to_complexity(lesson.difficulty),
                "recommended_for": self._get_recommended_audience(lesson.difficulty),
                "estimated_practice_time": lesson.duration_minutes + (len(lesson.exercises) * 15),
            }
        }
        
        return metadata
    
    def generate_exercise_metadata(self, exercise: Exercise, lesson: Lesson) -> Dict[str, Any]:
        """Generate comprehensive exercise metadata.
        
        Implements Requirement 14.3:
        - Includes title, difficulty, estimated time
        - Adds solution availability flag
        
        Args:
            exercise: Exercise to generate metadata for
            lesson: Parent lesson containing the exercise
            
        Returns:
            Dictionary containing complete exercise metadata
        """
        metadata = {
            # Core identification (Req 14.3)
            "exercise_id": exercise.exercise_id,
            "title": exercise.title,
            "description": exercise.description,
            
            # Parent lesson information
            "lesson_id": lesson.lesson_id,
            "lesson_title": lesson.title,
            
            # Difficulty and time (Req 14.3)
            "difficulty": exercise.difficulty,
            "estimated_minutes": exercise.estimated_minutes,
            "estimated_completion_time": self._format_duration(exercise.estimated_minutes),
            
            # Learning information
            "learning_objectives": exercise.learning_objectives,
            "instruction_count": len(exercise.instructions),
            
            # Content availability (Req 14.3)
            "has_starter_code": bool(exercise.starter_code),
            "has_solution": bool(exercise.solution_code),
            "solution_available": bool(exercise.solution_code),
            "hint_count": len(exercise.hints),
            "test_case_count": len(exercise.test_cases),
            
            # Additional metadata
            "metadata": {
                "complexity_level": self._map_difficulty_to_complexity(exercise.difficulty),
                "recommended_for": self._get_recommended_audience(exercise.difficulty),
                "practice_type": "hands-on coding",
                "validation_available": len(exercise.test_cases) > 0,
            }
        }
        
        return metadata
    
    def generate_course_manifest(self, course: CourseOutline) -> Dict[str, Any]:
        """Generate a complete course manifest with all metadata.
        
        Implements Requirements 14.1, 14.5:
        - Creates course manifest file listing all lessons, modules, and resources
        - Includes comprehensive metadata for the entire course structure
        
        Args:
            course: CourseOutline to generate manifest for
            
        Returns:
            Dictionary containing complete course manifest
        """
        # Generate course-level metadata
        course_metadata = self.generate_course_metadata(course)
        
        # Generate detailed module and lesson metadata
        modules_detail = []
        for module in course.modules:
            module_detail = {
                "module_id": module.module_id,
                "title": module.title,
                "description": module.description,
                "order": module.order,
                "difficulty": module.difficulty,
                "duration_hours": module.duration_hours,
                "learning_objectives": module.learning_objectives,
                "lessons": []
            }
            
            # Add lesson metadata
            for lesson in module.lessons:
                lesson_metadata = self.generate_lesson_metadata(lesson, module)
                
                # Add exercise metadata
                exercises_metadata = [
                    self.generate_exercise_metadata(exercise, lesson)
                    for exercise in lesson.exercises
                ]
                lesson_metadata["exercises"] = exercises_metadata
                
                module_detail["lessons"].append(lesson_metadata)
            
            modules_detail.append(module_detail)
        
        # Build complete manifest
        manifest = {
            # Course metadata
            "course": course_metadata,
            
            # Detailed structure
            "modules": modules_detail,
            
            # Quick reference indices
            "indices": {
                "lessons_by_difficulty": self._index_lessons_by_difficulty(course),
                "lessons_by_tag": self._index_lessons_by_tag(course),
                "lessons_by_duration": self._index_lessons_by_duration(course),
            },
            
            # Manifest metadata
            "manifest_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
        }
        
        return manifest
    
    # ========== Helper Methods ==========
    
    def _format_duration(self, minutes: int) -> str:
        """Format duration in minutes to human-readable string.
        
        Args:
            minutes: Duration in minutes
            
        Returns:
            Formatted duration string (e.g., "1h 30m", "45m")
        """
        if minutes < 60:
            return f"{minutes}m"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours}h"
        
        return f"{hours}h {remaining_minutes}m"
    
    def _map_difficulty_to_complexity(self, difficulty: str) -> int:
        """Map difficulty level to numeric complexity score.
        
        Args:
            difficulty: Difficulty level (beginner, intermediate, advanced)
            
        Returns:
            Numeric complexity score (1-10)
        """
        mapping = {
            "beginner": 3,
            "intermediate": 6,
            "advanced": 9,
        }
        return mapping.get(difficulty, 5)
    
    def _get_recommended_audience(self, difficulty: str) -> str:
        """Get recommended audience description for difficulty level.
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            Audience description string
        """
        mapping = {
            "beginner": "New programmers and those learning fundamentals",
            "intermediate": "Developers with basic programming experience",
            "advanced": "Experienced developers looking to master advanced concepts",
        }
        return mapping.get(difficulty, "All skill levels")
    
    def _index_lessons_by_difficulty(self, course: CourseOutline) -> Dict[str, List[str]]:
        """Create an index of lesson IDs grouped by difficulty.
        
        Args:
            course: CourseOutline to index
            
        Returns:
            Dictionary mapping difficulty levels to lesson IDs
        """
        index = {
            "beginner": [],
            "intermediate": [],
            "advanced": [],
        }
        
        for module in course.modules:
            for lesson in module.lessons:
                index[lesson.difficulty].append(lesson.lesson_id)
        
        return index
    
    def _index_lessons_by_tag(self, course: CourseOutline) -> Dict[str, List[str]]:
        """Create an index of lesson IDs grouped by tags.
        
        Args:
            course: CourseOutline to index
            
        Returns:
            Dictionary mapping tags to lesson IDs
        """
        index = {}
        
        for module in course.modules:
            for lesson in module.lessons:
                for tag in lesson.tags:
                    if tag not in index:
                        index[tag] = []
                    index[tag].append(lesson.lesson_id)
        
        return index
    
    def _index_lessons_by_duration(self, course: CourseOutline) -> Dict[str, List[str]]:
        """Create an index of lesson IDs grouped by duration ranges.
        
        Args:
            course: CourseOutline to index
            
        Returns:
            Dictionary mapping duration ranges to lesson IDs
        """
        index = {
            "short": [],      # < 30 minutes
            "medium": [],     # 30-60 minutes
            "long": [],       # > 60 minutes
        }
        
        for module in course.modules:
            for lesson in module.lessons:
                if lesson.duration_minutes < 30:
                    index["short"].append(lesson.lesson_id)
                elif lesson.duration_minutes <= 60:
                    index["medium"].append(lesson.lesson_id)
                else:
                    index["long"].append(lesson.lesson_id)
        
        return index
