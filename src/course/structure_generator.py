"""Course Structure Generator - Organizes analysis results into modules and lessons."""

from typing import List, Tuple, Dict, Optional
from datetime import datetime
import uuid
from collections import defaultdict
from src.models import CodebaseAnalysis, FileAnalysis, DetectedPattern
from .models import CourseOutline, Module, Lesson
from .config import CourseConfig
from .performance_monitor import get_monitor


class CourseStructureGenerator:
    """Generates course structure from codebase analysis."""
    
    def __init__(self, config: CourseConfig, course_cache=None):
        """Initialize the course structure generator.
        
        Args:
            config: Course generation configuration
            course_cache: Optional CourseCacheManager for caching
        """
        self.config = config
        self.course_cache = course_cache
    
    async def generate_course_structure(self, analysis: CodebaseAnalysis) -> CourseOutline:
        """Generate a complete course structure from analysis results.
        
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
        """
        monitor = get_monitor()
        
        with monitor.measure("course_structure", file_count=len(analysis.file_analyses)):
            # Check cache first
            if self.course_cache:
                cached = await self.course_cache.get_course_structure(analysis.codebase_id)
                if cached and "data" in cached:
                    import logging
                    logging.getLogger(__name__).info(f"Using cached course structure for {analysis.codebase_id}")
                    # Reconstruct CourseOutline from cached data
                    return self._deserialize_course_outline(cached["data"])
            
            # 1. Extract teachable files sorted by teaching value (Req 1.2)
            teachable_files = self._filter_teachable_files(analysis)
            
            # 1.5. Apply audience filtering (Req 8.2, Task 13.2)
            teachable_files = self._filter_by_audience(teachable_files, analysis)
            
            # 1.6. Apply focus filtering (Req 8.4, Task 13.3)
            teachable_files = self._filter_by_focus(teachable_files, analysis)
        
        # 2. Group files by patterns and concepts (Req 1.4)
        grouped_files = self.group_by_patterns(teachable_files, analysis)
        
        # 3. Determine module count (3-8 modules) (Req 1.3)
        module_count = self.calculate_module_count(len(teachable_files))
        
        # 4. Create modules with balanced difficulty progression
        modules = self._create_modules(grouped_files, module_count, analysis)
        
        # 5. Sort modules by difficulty (beginner → advanced) (Req 1.1)
        modules = self.sort_by_difficulty(modules)
        
        # 6. Apply learning progression logic (Task 2.3)
        modules = self._apply_learning_progression(modules, analysis)
        
        # 7. Calculate total duration (Req 1.5)
        total_duration = sum(m.duration_hours for m in modules)
        
        # 8. Calculate difficulty distribution
        difficulty_dist = self._calculate_difficulty_distribution(modules)
        
        # 9. Generate course metadata
        course_id = str(uuid.uuid4())
        title = self._generate_course_title(analysis)
        description = self._generate_course_description(analysis, modules)
        tags = self._generate_course_tags(analysis)
        
        course_outline = CourseOutline(
            course_id=course_id,
            title=title,
            description=description,
            author=self.config.author,
            version=self.config.version,
            created_at=datetime.now(),
            modules=modules,
            total_duration_hours=total_duration,
            difficulty_distribution=difficulty_dist,
            tags=tags,
            prerequisites=[]
        )
        
        # Cache the result
        if self.course_cache:
            file_paths = [f[0] for f in teachable_files]
            serialized = self._serialize_course_outline(course_outline)
            await self.course_cache.set_course_structure(
                analysis.codebase_id,
                serialized,
                file_paths
            )
        
        return course_outline
    
    def group_by_patterns(
        self, 
        teachable_files: List[Tuple[str, float]], 
        analysis: CodebaseAnalysis
    ) -> List[List[Tuple[str, float, FileAnalysis]]]:
        """Group files by detected patterns and concepts.
        
        This method implements Requirement 1.4: Groups lessons by related patterns.
        
        Args:
            teachable_files: List of (file_path, teaching_value) tuples
            analysis: Codebase analysis results
            
        Returns:
            List of file groups, each containing (file_path, teaching_value, FileAnalysis)
        """
        # Create pattern-based groups
        pattern_groups: Dict[str, List[Tuple[str, float, FileAnalysis]]] = defaultdict(list)
        ungrouped: List[Tuple[str, float, FileAnalysis]] = []
        
        for file_path, teaching_value in teachable_files:
            file_analysis = analysis.file_analyses.get(file_path)
            if not file_analysis:
                continue
            
            # Find primary pattern for this file
            primary_pattern = self._get_primary_pattern(file_analysis)
            
            if primary_pattern:
                pattern_groups[primary_pattern].append((file_path, teaching_value, file_analysis))
            else:
                ungrouped.append((file_path, teaching_value, file_analysis))
        
        # Convert to list of groups, sorted by group size (largest first)
        grouped = sorted(pattern_groups.values(), key=len, reverse=True)
        
        # Add ungrouped files as individual groups
        if ungrouped:
            grouped.extend([[item] for item in ungrouped])
        
        return grouped
    
    def calculate_module_count(self, num_teachable_files: int) -> int:
        """Calculate optimal number of modules based on file count.
        
        This method implements Requirement 1.3: Creates 3-8 modules based on teachable files.
        
        Args:
            num_teachable_files: Number of files with sufficient teaching value
            
        Returns:
            Number of modules to create (between min_modules and max_modules)
        """
        if num_teachable_files == 0:
            return self.config.min_modules
        
        # Aim for 3-5 lessons per module
        ideal_lessons_per_module = 4
        ideal_count = max(
            self.config.min_modules,
            min(
                self.config.max_modules,
                (num_teachable_files + ideal_lessons_per_module - 1) // ideal_lessons_per_module
            )
        )
        
        return ideal_count
    
    def sort_by_difficulty(self, modules: List[Module]) -> List[Module]:
        """Sort modules by difficulty level (beginner → intermediate → advanced).
        
        This method implements Requirement 1.1: Organizes modules by difficulty level.
        
        Args:
            modules: List of modules to sort
            
        Returns:
            Sorted list of modules
        """
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        
        return sorted(
            modules,
            key=lambda m: (difficulty_order.get(m.difficulty, 1), m.order)
        )
    
    def _filter_teachable_files(self, analysis: CodebaseAnalysis) -> List[Tuple[str, float]]:
        """Filter files by teaching value threshold and sort by score.
        
        Implements Requirement 1.2: Sorts lessons by teaching value score.
        """
        teachable = [
            (file_path, score)
            for file_path, score in analysis.top_teaching_files
            if score >= self.config.min_teaching_value
        ]
        
        # Already sorted by teaching value in descending order
        return teachable
    
    def _get_primary_pattern(self, file_analysis: FileAnalysis) -> str:
        """Get the primary pattern type for a file."""
        if not file_analysis.patterns:
            return ""
        
        # Return the pattern with highest confidence
        primary = max(file_analysis.patterns, key=lambda p: p.confidence)
        return primary.pattern_type
    
    def _create_modules(
        self,
        grouped_files: List[List[Tuple[str, float, FileAnalysis]]],
        module_count: int,
        analysis: CodebaseAnalysis
    ) -> List[Module]:
        """Create modules from grouped files."""
        modules = []
        
        # Distribute groups across modules
        groups_per_module = max(1, len(grouped_files) // module_count)
        
        for i in range(module_count):
            start_idx = i * groups_per_module
            end_idx = start_idx + groups_per_module if i < module_count - 1 else len(grouped_files)
            
            if start_idx >= len(grouped_files):
                break
            
            module_groups = grouped_files[start_idx:end_idx]
            module = self._create_single_module(module_groups, i, analysis)
            modules.append(module)
        
        return modules
    
    def _create_single_module(
        self,
        file_groups: List[List[Tuple[str, float, FileAnalysis]]],
        order: int,
        analysis: CodebaseAnalysis
    ) -> Module:
        """Create a single module from file groups.
        
        This method implements Requirements 1.1, 1.2, 1.3, 1.4:
        - Groups lessons by patterns
        - Calculates module duration and difficulty
        - Generates module learning objectives
        """
        # Flatten groups into single list
        all_files = [item for group in file_groups for item in group]
        
        # Create lessons with pattern grouping (Req 1.4)
        lessons = []
        for idx, (file_path, teaching_value, file_analysis) in enumerate(all_files):
            lesson = self._create_basic_lesson(
                file_path, teaching_value, file_analysis, idx
            )
            lessons.append(lesson)
        
        # Calculate module difficulty (Req 1.1)
        difficulty = self._calculate_module_difficulty(lessons)
        
        # Calculate module duration (Req 1.3)
        duration_hours = sum(l.duration_minutes for l in lessons) / 60.0
        
        # Generate module title and description
        title = self._generate_module_title(file_groups, order)
        description = self._generate_module_description(lessons)
        
        # Generate module learning objectives (Req 1.4)
        learning_objectives = self._generate_module_objectives(lessons, file_groups)
        
        return Module(
            module_id=str(uuid.uuid4()),
            title=title,
            description=description,
            order=order,
            lessons=lessons,
            difficulty=difficulty,
            duration_hours=duration_hours,
            learning_objectives=learning_objectives
        )
    
    def _generate_module_objectives(
        self,
        lessons: List[Lesson],
        file_groups: List[List[Tuple[str, float, FileAnalysis]]]
    ) -> List[str]:
        """Generate learning objectives for a module.
        
        Implements Requirement 1.4: Generate module learning objectives.
        """
        objectives = []
        
        # Collect all patterns from the module
        pattern_counts: Dict[str, int] = defaultdict(int)
        for group in file_groups:
            for _, _, file_analysis in group:
                for pattern in file_analysis.patterns:
                    pattern_counts[pattern.pattern_type] += 1
        
        # Create objectives for top patterns
        top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for pattern_type, _ in top_patterns:
            pattern_name = pattern_type.replace('_', ' ')
            objectives.append(f"Master {pattern_name} patterns")
        
        # Add objective based on module difficulty
        difficulty = self._calculate_module_difficulty(lessons)
        if difficulty == "beginner":
            objectives.append("Build foundational programming skills")
        elif difficulty == "intermediate":
            objectives.append("Apply intermediate programming concepts")
        else:
            objectives.append("Implement advanced programming techniques")
        
        # Add objective based on lesson count
        if len(lessons) > 5:
            objectives.append("Integrate multiple concepts into cohesive solutions")
        
        return objectives if objectives else ["Learn core programming concepts"]
    
    def _create_basic_lesson(
        self,
        file_path: str,
        teaching_value: float,
        file_analysis: FileAnalysis,
        order: int
    ) -> Lesson:
        """Create a basic lesson structure (full implementation in Task 2.2)."""
        # Calculate difficulty from complexity
        difficulty = self._calculate_lesson_difficulty(file_analysis)
        
        # Estimate duration based on complexity
        duration = self._estimate_lesson_duration(file_analysis)
        
        # Generate title from file path
        title = self._generate_lesson_title(file_path, file_analysis)
        
        # Generate description
        description = self._generate_lesson_description(file_analysis)
        
        # Extract concepts from patterns
        concepts = [p.pattern_type for p in file_analysis.patterns]
        
        # Generate basic learning objectives
        learning_objectives = self._generate_basic_objectives(file_analysis)
        
        lesson = Lesson(
            lesson_id=str(uuid.uuid4()),
            title=title,
            description=description,
            order=order,
            difficulty=difficulty,
            duration_minutes=duration,
            file_path=file_path,
            teaching_value=teaching_value,
            learning_objectives=learning_objectives,
            prerequisites=[],  # Will be populated in Task 2.3
            concepts=concepts,
            content=None,  # Will be populated in Task 3
            exercises=[],  # Will be populated in Task 4
            tags=concepts
        )
        
        # Apply audience-based adjustments (Task 13.2)
        lesson = self.adjust_content_complexity(lesson)
        
        return lesson
    
    def _calculate_module_difficulty(self, lessons: List[Lesson]) -> str:
        """Calculate overall module difficulty from lessons."""
        if not lessons:
            return "beginner"
        
        difficulty_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
        for lesson in lessons:
            difficulty_counts[lesson.difficulty] += 1
        
        # Return the most common difficulty
        return max(difficulty_counts.items(), key=lambda x: x[1])[0]
    
    def _calculate_lesson_difficulty(self, file_analysis: FileAnalysis) -> str:
        """Calculate lesson difficulty from complexity metrics."""
        avg_complexity = file_analysis.complexity_metrics.avg_complexity
        
        if avg_complexity <= 5:
            return "beginner"
        elif avg_complexity <= 10:
            return "intermediate"
        else:
            return "advanced"
    
    def _estimate_lesson_duration(self, file_analysis: FileAnalysis) -> int:
        """Estimate lesson duration in minutes based on complexity."""
        # Base duration
        base_duration = 20
        
        # Add time based on number of functions/classes
        num_symbols = (
            len(file_analysis.symbol_info.functions) +
            len(file_analysis.symbol_info.classes)
        )
        symbol_time = min(num_symbols * 5, 30)
        
        # Add time based on patterns
        pattern_time = min(len(file_analysis.patterns) * 5, 20)
        
        total = base_duration + symbol_time + pattern_time
        
        # Clamp to config range
        return max(
            self.config.min_lesson_duration,
            min(self.config.max_lesson_duration, total)
        )
    
    def _generate_lesson_title(self, file_path: str, file_analysis: FileAnalysis) -> str:
        """Generate a lesson title from file path and analysis."""
        # Get filename without extension
        import os
        filename = os.path.splitext(os.path.basename(file_path))[0]
        
        # Convert snake_case or kebab-case to Title Case
        title = filename.replace('_', ' ').replace('-', ' ').title()
        
        # Add pattern context if available
        if file_analysis.patterns:
            primary_pattern = max(file_analysis.patterns, key=lambda p: p.confidence)
            pattern_name = primary_pattern.pattern_type.replace('_', ' ').title()
            title = f"{title}: {pattern_name}"
        
        return title
    
    def _generate_lesson_description(self, file_analysis: FileAnalysis) -> str:
        """Generate a lesson description from analysis."""
        parts = []
        
        # Add teaching value explanation
        if file_analysis.teaching_value.explanation:
            parts.append(file_analysis.teaching_value.explanation)
        
        # Add pattern information
        if file_analysis.patterns:
            pattern_types = [p.pattern_type for p in file_analysis.patterns]
            parts.append(f"Demonstrates: {', '.join(pattern_types)}")
        
        return " ".join(parts) if parts else "Learn from this code example."
    
    def _generate_basic_objectives(self, file_analysis: FileAnalysis) -> List[str]:
        """Generate basic learning objectives from file analysis."""
        objectives = []
        
        # Add objectives based on patterns
        for pattern in file_analysis.patterns[:3]:  # Top 3 patterns
            pattern_name = pattern.pattern_type.replace('_', ' ')
            objectives.append(f"Understand {pattern_name} pattern")
        
        # Add objective based on complexity
        if file_analysis.complexity_metrics.avg_complexity > 5:
            objectives.append("Analyze complex code structure")
        
        # Add objective based on documentation
        if file_analysis.documentation_coverage > 0.7:
            objectives.append("Learn documentation best practices")
        
        return objectives if objectives else ["Understand the code structure"]
    
    def _generate_module_title(
        self,
        file_groups: List[List[Tuple[str, float, FileAnalysis]]],
        order: int
    ) -> str:
        """Generate a module title from file groups."""
        # Get most common pattern across all files
        pattern_counts: Dict[str, int] = defaultdict(int)
        
        for group in file_groups:
            for _, _, file_analysis in group:
                for pattern in file_analysis.patterns:
                    pattern_counts[pattern.pattern_type] += 1
        
        if pattern_counts:
            primary_pattern = max(pattern_counts.items(), key=lambda x: x[1])[0]
            pattern_name = primary_pattern.replace('_', ' ').title()
            return f"Module {order + 1}: {pattern_name}"
        
        return f"Module {order + 1}: Core Concepts"
    
    def _generate_module_description(self, lessons: List[Lesson]) -> str:
        """Generate a module description from lessons."""
        if not lessons:
            return "Learn core programming concepts."
        
        # Collect unique concepts
        concepts = set()
        for lesson in lessons:
            concepts.update(lesson.concepts)
        
        if concepts:
            concept_list = ', '.join(list(concepts)[:5])
            return f"This module covers: {concept_list}"
        
        return f"This module contains {len(lessons)} lessons."
    
    def _calculate_difficulty_distribution(self, modules: List[Module]) -> Dict[str, int]:
        """Calculate distribution of difficulty levels across all lessons."""
        distribution = {"beginner": 0, "intermediate": 0, "advanced": 0}
        
        for module in modules:
            for lesson in module.lessons:
                distribution[lesson.difficulty] += 1
        
        return distribution
    
    def _generate_course_title(self, analysis: CodebaseAnalysis) -> str:
        """Generate a course title from codebase analysis."""
        # Use codebase_id as base
        base_name = analysis.codebase_id.replace('_', ' ').replace('-', ' ').title()
        return f"Learn {base_name}"
    
    def _generate_course_description(
        self,
        analysis: CodebaseAnalysis,
        modules: List[Module]
    ) -> str:
        """Generate a course description."""
        parts = [
            f"A comprehensive course with {len(modules)} modules",
            f"covering {analysis.metrics.total_files} files",
            f"and {analysis.metrics.total_patterns_detected} patterns."
        ]
        return " ".join(parts)
    
    def _generate_course_tags(self, analysis: CodebaseAnalysis) -> List[str]:
        """Generate course tags from analysis."""
        tags = set()
        
        # Add pattern types as tags
        for pattern in analysis.global_patterns[:10]:  # Top 10 patterns
            tags.add(pattern.pattern_type)
        
        return list(tags)
    
    # ========== Task 2.3: Learning Progression Logic ==========
    
    def _apply_learning_progression(
        self,
        modules: List[Module],
        analysis: CodebaseAnalysis
    ) -> List[Module]:
        """Apply learning progression logic to modules and lessons.
        
        This method implements Requirements 6.1, 6.2, 6.3, 6.4, 6.5:
        - Places beginner lessons before intermediate and advanced
        - Identifies prerequisites from imports
        - Lists prerequisite lessons in metadata
        - Ensures prerequisite lessons appear before dependent lessons
        - Uses complexity metrics for difficulty calculation
        
        Args:
            modules: List of modules with lessons
            analysis: Codebase analysis results
            
        Returns:
            Modules with updated lesson ordering and prerequisites
        """
        # Build a map of file_path -> lesson for quick lookup
        file_to_lesson: Dict[str, Lesson] = {}
        all_lessons: List[Lesson] = []
        
        for module in modules:
            for lesson in module.lessons:
                file_to_lesson[lesson.file_path] = lesson
                all_lessons.append(lesson)
        
        # Detect prerequisites for each lesson (Req 6.2, 6.3)
        for lesson in all_lessons:
            prerequisites = self._detect_prerequisites(
                lesson, file_to_lesson, analysis
            )
            lesson.prerequisites = prerequisites
        
        # Sort lessons within each module by prerequisites (Req 6.4)
        for module in modules:
            module.lessons = self._sort_lessons_by_prerequisites(module.lessons)
            # Update lesson order after sorting
            for idx, lesson in enumerate(module.lessons):
                lesson.order = idx
        
        return modules
    
    def _detect_prerequisites(
        self,
        lesson: Lesson,
        file_to_lesson: Dict[str, Lesson],
        analysis: CodebaseAnalysis
    ) -> List[str]:
        """Detect prerequisite lessons based on imports and dependencies.
        
        Implements Requirements 6.2, 6.3:
        - Analyzes lesson dependencies based on code imports
        - Lists prerequisite lessons in metadata
        
        Args:
            lesson: The lesson to analyze
            file_to_lesson: Map of file paths to lessons
            analysis: Codebase analysis results
            
        Returns:
            List of prerequisite lesson IDs
        """
        prerequisites = []
        
        # Get file analysis for this lesson
        file_analysis = analysis.file_analyses.get(lesson.file_path)
        if not file_analysis:
            return prerequisites
        
        # Check imports to find dependencies
        for import_info in file_analysis.symbol_info.imports:
            # Skip external imports
            if import_info.is_relative or self._is_internal_import(
                import_info.module, analysis
            ):
                # Try to find the imported file in our lessons
                imported_file = self._resolve_import_to_file(
                    import_info.module, lesson.file_path, analysis
                )
                
                if imported_file and imported_file in file_to_lesson:
                    prereq_lesson = file_to_lesson[imported_file]
                    # Only add if it's a different lesson and simpler
                    if (prereq_lesson.lesson_id != lesson.lesson_id and
                        self._is_simpler_lesson(prereq_lesson, lesson)):
                        prerequisites.append(prereq_lesson.lesson_id)
        
        # Also check dependency graph
        if lesson.file_path in analysis.dependency_graph.nodes:
            node = analysis.dependency_graph.nodes[lesson.file_path]
            for imported_file in node.imports:
                if imported_file in file_to_lesson:
                    prereq_lesson = file_to_lesson[imported_file]
                    if (prereq_lesson.lesson_id != lesson.lesson_id and
                        prereq_lesson.lesson_id not in prerequisites and
                        self._is_simpler_lesson(prereq_lesson, lesson)):
                        prerequisites.append(prereq_lesson.lesson_id)
        
        return prerequisites
    
    def _is_internal_import(self, module: str, analysis: CodebaseAnalysis) -> bool:
        """Check if an import is internal to the codebase."""
        # Check if any file path contains the module name
        for file_path in analysis.file_analyses.keys():
            if module.replace('.', '/') in file_path or module.replace('.', '\\') in file_path:
                return True
        return False
    
    def _resolve_import_to_file(
        self,
        module: str,
        current_file: str,
        analysis: CodebaseAnalysis
    ) -> str:
        """Resolve an import statement to an actual file path."""
        # Try to find matching file in analysis
        module_parts = module.replace('.', '/').split('/')
        
        for file_path in analysis.file_analyses.keys():
            # Check if file path ends with module path
            for i in range(len(module_parts)):
                partial_path = '/'.join(module_parts[i:])
                if partial_path in file_path.replace('\\', '/'):
                    return file_path
        
        return ""
    
    def _is_simpler_lesson(self, lesson1: Lesson, lesson2: Lesson) -> bool:
        """Check if lesson1 is simpler than lesson2.
        
        Implements Requirement 6.5: Uses complexity metrics for difficulty calculation.
        """
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        
        diff1 = difficulty_order.get(lesson1.difficulty, 1)
        diff2 = difficulty_order.get(lesson2.difficulty, 1)
        
        if diff1 < diff2:
            return True
        elif diff1 == diff2:
            # If same difficulty, use teaching value (higher = simpler/better starting point)
            return lesson1.teaching_value > lesson2.teaching_value
        
        return False
    
    def _sort_lessons_by_prerequisites(self, lessons: List[Lesson]) -> List[Lesson]:
        """Sort lessons so prerequisites appear before dependent lessons.
        
        Implements Requirements 6.1, 6.4:
        - Places beginner lessons before intermediate and advanced
        - Ensures prerequisite lessons appear before dependent lessons
        
        Uses topological sort to handle dependencies.
        """
        # Build dependency graph
        lesson_map = {lesson.lesson_id: lesson for lesson in lessons}
        in_degree = {lesson.lesson_id: 0 for lesson in lessons}
        adjacency = {lesson.lesson_id: [] for lesson in lessons}
        
        for lesson in lessons:
            for prereq_id in lesson.prerequisites:
                if prereq_id in lesson_map:
                    adjacency[prereq_id].append(lesson.lesson_id)
                    in_degree[lesson.lesson_id] += 1
        
        # Topological sort with difficulty-based tie-breaking
        sorted_lessons = []
        queue = []
        
        # Start with lessons that have no prerequisites
        for lesson in lessons:
            if in_degree[lesson.lesson_id] == 0:
                queue.append(lesson)
        
        # Sort queue by difficulty (beginner first) (Req 6.1)
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        queue.sort(key=lambda l: (difficulty_order.get(l.difficulty, 1), -l.teaching_value))
        
        while queue:
            # Take the first lesson (already sorted by difficulty)
            current = queue.pop(0)
            sorted_lessons.append(current)
            
            # Update in-degrees for dependent lessons
            for dependent_id in adjacency[current.lesson_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    dependent_lesson = lesson_map[dependent_id]
                    # Insert in sorted position by difficulty
                    inserted = False
                    for i, queued in enumerate(queue):
                        if (difficulty_order.get(dependent_lesson.difficulty, 1) <
                            difficulty_order.get(queued.difficulty, 1)):
                            queue.insert(i, dependent_lesson)
                            inserted = True
                            break
                    if not inserted:
                        queue.append(dependent_lesson)
        
        # If there are cycles, add remaining lessons sorted by difficulty
        if len(sorted_lessons) < len(lessons):
            remaining = [l for l in lessons if l not in sorted_lessons]
            remaining.sort(key=lambda l: (difficulty_order.get(l.difficulty, 1), -l.teaching_value))
            sorted_lessons.extend(remaining)
        
        return sorted_lessons
    
    # ========== Task 13.2: Audience Filtering ==========
    
    def _filter_by_audience(
        self,
        teachable_files: List[Tuple[str, float]],
        analysis: CodebaseAnalysis
    ) -> List[Tuple[str, float]]:
        """Filter lessons by difficulty based on target audience.
        
        Implements Requirement 8.2: Filters lessons to match audience level.
        
        Args:
            teachable_files: List of (file_path, teaching_value) tuples
            analysis: Codebase analysis results
            
        Returns:
            Filtered list of teachable files
        """
        # If audience is "mixed", include all lessons
        if self.config.target_audience == "mixed":
            return teachable_files
        
        # Filter based on target audience
        filtered = []
        for file_path, teaching_value in teachable_files:
            file_analysis = analysis.file_analyses.get(file_path)
            if not file_analysis:
                continue
            
            # Calculate difficulty for this file
            difficulty = self._calculate_lesson_difficulty(file_analysis)
            
            # Include based on audience
            if self._should_include_for_audience(difficulty):
                filtered.append((file_path, teaching_value))
        
        return filtered
    
    def _should_include_for_audience(self, difficulty: str) -> bool:
        """Check if a lesson should be included for the target audience.
        
        Implements Requirement 8.2: Filters lessons to match audience level.
        
        Args:
            difficulty: Lesson difficulty level
            
        Returns:
            True if lesson should be included
        """
        audience = self.config.target_audience
        
        if audience == "beginner":
            # Include only beginner and some intermediate
            return difficulty in ["beginner", "intermediate"]
        elif audience == "intermediate":
            # Include intermediate and some beginner/advanced
            return difficulty in ["beginner", "intermediate", "advanced"]
        elif audience == "advanced":
            # Include intermediate and advanced
            return difficulty in ["intermediate", "advanced"]
        else:  # mixed
            return True
    
    def adjust_content_complexity(self, lesson: Lesson) -> Lesson:
        """Adjust content complexity based on target audience.
        
        Implements Requirement 8.2: Adjusts content complexity for audience.
        
        This method modifies lesson metadata to match the target audience:
        - For beginners: Increase duration, add more objectives
        - For advanced: Decrease duration, focus on key concepts
        
        Args:
            lesson: Lesson to adjust
            
        Returns:
            Adjusted lesson
        """
        audience = self.config.target_audience
        
        if audience == "beginner":
            # Increase duration for beginners (more explanation needed)
            lesson.duration_minutes = int(lesson.duration_minutes * 1.2)
            
            # Ensure duration doesn't exceed max
            lesson.duration_minutes = min(
                lesson.duration_minutes,
                self.config.max_lesson_duration
            )
            
            # Add foundational objectives if not present
            if not any("understand" in obj.lower() for obj in lesson.learning_objectives):
                lesson.learning_objectives.insert(
                    0,
                    "Understand the fundamental concepts"
                )
        
        elif audience == "advanced":
            # Decrease duration for advanced (less explanation needed)
            lesson.duration_minutes = int(lesson.duration_minutes * 0.8)
            
            # Ensure duration doesn't go below min
            lesson.duration_minutes = max(
                lesson.duration_minutes,
                self.config.min_lesson_duration
            )
            
            # Focus on implementation objectives
            if not any("implement" in obj.lower() for obj in lesson.learning_objectives):
                lesson.learning_objectives.insert(
                    0,
                    "Implement advanced techniques"
                )
        
        return lesson
    
    # ========== Task 13.3: Focus Filtering ==========
    
    def _filter_by_focus(
        self,
        teachable_files: List[Tuple[str, float]],
        analysis: CodebaseAnalysis
    ) -> List[Tuple[str, float]]:
        """Filter and prioritize files based on course focus.
        
        Implements Requirement 8.4: Prioritizes relevant content and patterns
        based on course focus setting.
        
        Args:
            teachable_files: List of (file_path, teaching_value) tuples
            analysis: Codebase analysis results
            
        Returns:
            Filtered and re-prioritized list of teachable files
        """
        # If focus is "full-stack", include everything
        if self.config.course_focus == "full-stack":
            return teachable_files
        
        # Score each file based on focus relevance
        scored_files = []
        for file_path, teaching_value in teachable_files:
            file_analysis = analysis.file_analyses.get(file_path)
            if not file_analysis:
                continue
            
            # Calculate focus relevance score
            focus_score = self._calculate_focus_relevance(file_analysis)
            
            # Only include files with sufficient focus relevance
            if focus_score > 0:
                # Boost teaching value by focus score
                adjusted_value = teaching_value * (1 + focus_score)
                scored_files.append((file_path, adjusted_value))
        
        # Re-sort by adjusted teaching value
        scored_files.sort(key=lambda x: x[1], reverse=True)
        
        return scored_files
    
    def _calculate_focus_relevance(self, file_analysis: FileAnalysis) -> float:
        """Calculate how relevant a file is to the course focus.
        
        Implements Requirement 8.4: Prioritizes relevant patterns based on focus.
        
        Args:
            file_analysis: Analysis results for the file
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        focus = self.config.course_focus
        
        # Define pattern relevance for each focus area
        focus_patterns = {
            "patterns": [
                "factory_pattern", "singleton_pattern", "observer_pattern",
                "strategy_pattern", "decorator_pattern", "adapter_pattern",
                "mvc_pattern", "repository_pattern", "dependency_injection"
            ],
            "architecture": [
                "mvc_pattern", "layered_architecture", "microservices",
                "api_design", "database_model", "service_layer",
                "repository_pattern", "dependency_injection", "modular_design"
            ],
            "best-practices": [
                "error_handling", "input_validation", "logging",
                "testing", "documentation", "code_organization",
                "security", "performance_optimization", "clean_code"
            ]
        }
        
        relevant_patterns = focus_patterns.get(focus, [])
        if not relevant_patterns:
            return 1.0  # Full relevance if focus not recognized
        
        # Calculate relevance based on pattern matches
        relevance_score = 0.0
        pattern_count = 0
        
        for pattern in file_analysis.patterns:
            pattern_count += 1
            # Check if pattern matches focus
            pattern_type = pattern.pattern_type.lower()
            
            for relevant_pattern in relevant_patterns:
                if relevant_pattern.lower() in pattern_type or pattern_type in relevant_pattern.lower():
                    # Weight by pattern confidence
                    relevance_score += pattern.confidence
                    break
        
        # Normalize by pattern count
        if pattern_count > 0:
            relevance_score = relevance_score / pattern_count
        
        # Also consider priority tags from config
        if self.config.priority_tags:
            tag_bonus = 0.0
            for tag in self.config.priority_tags:
                if any(tag.lower() in concept.lower() for concept in file_analysis.patterns):
                    tag_bonus += 0.2
            relevance_score = min(1.0, relevance_score + tag_bonus)
        
        # Check exclude tags
        if self.config.exclude_tags:
            for tag in self.config.exclude_tags:
                if any(tag.lower() in p.pattern_type.lower() for p in file_analysis.patterns):
                    return 0.0  # Exclude this file
        
        return relevance_score
    
    def prioritize_patterns_by_focus(self, patterns: List[DetectedPattern]) -> List[DetectedPattern]:
        """Prioritize patterns based on course focus.
        
        Implements Requirement 8.4: Prioritizes relevant patterns.
        
        Args:
            patterns: List of detected patterns
            
        Returns:
            Patterns sorted by focus relevance
        """
        focus = self.config.course_focus
        
        # Define pattern priorities for each focus
        focus_priorities = {
            "patterns": {
                "factory_pattern": 10, "singleton_pattern": 9, "observer_pattern": 9,
                "strategy_pattern": 8, "decorator_pattern": 8, "adapter_pattern": 7,
                "mvc_pattern": 7, "repository_pattern": 6, "dependency_injection": 6
            },
            "architecture": {
                "mvc_pattern": 10, "layered_architecture": 9, "microservices": 9,
                "api_design": 8, "database_model": 8, "service_layer": 7,
                "repository_pattern": 7, "dependency_injection": 6, "modular_design": 6
            },
            "best-practices": {
                "error_handling": 10, "input_validation": 9, "logging": 9,
                "testing": 8, "documentation": 8, "code_organization": 7,
                "security": 10, "performance_optimization": 7, "clean_code": 6
            }
        }
        
        priorities = focus_priorities.get(focus, {})
        
        # Score each pattern
        scored_patterns = []
        for pattern in patterns:
            # Base score is confidence
            score = pattern.confidence
            
            # Boost by focus priority
            pattern_type = pattern.pattern_type.lower()
            for priority_pattern, priority_value in priorities.items():
                if priority_pattern.lower() in pattern_type or pattern_type in priority_pattern.lower():
                    score *= (1 + priority_value / 10)
                    break
            
            scored_patterns.append((pattern, score))
        
        # Sort by score
        scored_patterns.sort(key=lambda x: x[1], reverse=True)
        
        return [pattern for pattern, _ in scored_patterns]
    
    # ========== Cache Serialization Methods ==========
    
    def _serialize_course_outline(self, course: CourseOutline) -> dict:
        """Serialize CourseOutline to dictionary for caching.
        
        Args:
            course: CourseOutline to serialize
            
        Returns:
            Dictionary representation
        """
        return {
            "course_id": course.course_id,
            "title": course.title,
            "description": course.description,
            "author": course.author,
            "version": course.version,
            "created_at": course.created_at.isoformat(),
            "modules": [self._serialize_module(m) for m in course.modules],
            "total_duration_hours": course.total_duration_hours,
            "difficulty_distribution": course.difficulty_distribution,
            "tags": course.tags,
            "prerequisites": course.prerequisites
        }
    
    def _serialize_module(self, module: Module) -> dict:
        """Serialize Module to dictionary."""
        return {
            "module_id": module.module_id,
            "title": module.title,
            "description": module.description,
            "order": module.order,
            "lessons": [self._serialize_lesson(l) for l in module.lessons],
            "difficulty": module.difficulty,
            "duration_hours": module.duration_hours,
            "learning_objectives": module.learning_objectives
        }
    
    def _serialize_lesson(self, lesson: Lesson) -> dict:
        """Serialize Lesson to dictionary."""
        return {
            "lesson_id": lesson.lesson_id,
            "title": lesson.title,
            "description": lesson.description,
            "order": lesson.order,
            "difficulty": lesson.difficulty,
            "duration_minutes": lesson.duration_minutes,
            "file_path": lesson.file_path,
            "teaching_value": lesson.teaching_value,
            "learning_objectives": lesson.learning_objectives,
            "prerequisites": lesson.prerequisites,
            "concepts": lesson.concepts,
            "content": None,  # Content not cached in structure
            "exercises": [],  # Exercises cached separately
            "tags": lesson.tags
        }
    
    def _deserialize_course_outline(self, data: dict) -> CourseOutline:
        """Deserialize CourseOutline from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            CourseOutline instance
        """
        return CourseOutline(
            course_id=data["course_id"],
            title=data["title"],
            description=data["description"],
            author=data["author"],
            version=data["version"],
            created_at=datetime.fromisoformat(data["created_at"]),
            modules=[self._deserialize_module(m) for m in data["modules"]],
            total_duration_hours=data["total_duration_hours"],
            difficulty_distribution=data["difficulty_distribution"],
            tags=data["tags"],
            prerequisites=data["prerequisites"]
        )
    
    def _deserialize_module(self, data: dict) -> Module:
        """Deserialize Module from dictionary."""
        return Module(
            module_id=data["module_id"],
            title=data["title"],
            description=data["description"],
            order=data["order"],
            lessons=[self._deserialize_lesson(l) for l in data["lessons"]],
            difficulty=data["difficulty"],
            duration_hours=data["duration_hours"],
            learning_objectives=data["learning_objectives"]
        )
    
    def _deserialize_lesson(self, data: dict) -> Lesson:
        """Deserialize Lesson from dictionary."""
        return Lesson(
            lesson_id=data["lesson_id"],
            title=data["title"],
            description=data["description"],
            order=data["order"],
            difficulty=data["difficulty"],
            duration_minutes=data["duration_minutes"],
            file_path=data["file_path"],
            teaching_value=data["teaching_value"],
            learning_objectives=data["learning_objectives"],
            prerequisites=data["prerequisites"],
            concepts=data["concepts"],
            content=None,
            exercises=[],
            tags=data["tags"]
        )
