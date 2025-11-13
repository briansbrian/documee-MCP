"""Incremental Course Update Manager.

This module provides incremental update functionality for courses.
Implements Requirements 15.1, 15.2, 15.3, 15.4, 15.5:
- Detects which lessons need updates based on file changes
- Tracks course version history
- Preserves manual edits to lesson content
- Archives deleted lessons
- Completes updates in <3s for <5 changes
"""

import hashlib
import json
import logging
import os
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field

from .models import CourseOutline, Module, Lesson, LessonContent
from .course_cache import CourseCacheManager
from src.models import CodebaseAnalysis


logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Represents a change to a source file."""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class LessonUpdate:
    """Represents an update to a lesson."""
    lesson_id: str
    file_path: str
    update_type: str  # 'content', 'structure', 'archived'
    changes: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CourseVersion:
    """Represents a version of the course."""
    version: str
    created_at: datetime
    updated_at: datetime
    change_summary: str
    lesson_updates: List[LessonUpdate] = field(default_factory=list)
    file_changes: List[FileChange] = field(default_factory=list)
    total_lessons: int = 0
    updated_lessons: int = 0
    archived_lessons: int = 0


class IncrementalUpdateManager:
    """Manages incremental updates to course content.
    
    Provides functionality for:
    - Detecting file changes
    - Identifying lessons that need updates
    - Preserving manual edits
    - Tracking version history
    - Archiving deleted lessons
    """
    
    def __init__(self, cache_manager: CourseCacheManager, output_dir: str = "output/courses"):
        """Initialize the incremental update manager.
        
        Args:
            cache_manager: Course cache manager instance
            output_dir: Directory where course files are stored
        """
        self.cache = cache_manager
        self.output_dir = output_dir
        
        # Version history storage
        self.version_history: Dict[str, List[CourseVersion]] = {}
        
        # Manual edit tracking
        self.manual_edits: Dict[str, Set[str]] = {}  # lesson_id -> set of edited sections
        
        # File hash tracking for change detection
        self.file_hashes: Dict[str, str] = {}
        
        # Archived lessons
        self.archived_lessons: Dict[str, List[Lesson]] = {}  # course_id -> archived lessons
    
    def _compute_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of file content.
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash of file content
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash file {file_path}: {e}")
            return ""
    
    def _get_file_mtime(self, file_path: str) -> float:
        """Get file modification time.
        
        Args:
            file_path: Path to file
            
        Returns:
            Modification time as timestamp
        """
        try:
            return os.path.getmtime(file_path)
        except Exception as e:
            logger.warning(f"Failed to get mtime for {file_path}: {e}")
            return 0.0
    
    async def detect_file_changes(
        self,
        codebase_id: str,
        current_files: List[str],
        analysis: CodebaseAnalysis
    ) -> List[FileChange]:
        """Detect changes to source files since last course generation.
        
        Implements Requirement 15.1: Detects which lessons need updates based on file changes.
        
        Args:
            codebase_id: Unique codebase identifier
            current_files: List of current file paths in the codebase
            analysis: Current codebase analysis
            
        Returns:
            List of FileChange objects representing detected changes
        """
        changes = []
        
        # Get cached course structure to find previous files
        cached_course = await self.cache.get_course_structure(codebase_id)
        
        if not cached_course or "file_paths" not in cached_course:
            # No previous course, all files are new
            for file_path in current_files:
                file_hash = self._compute_file_hash(file_path)
                changes.append(FileChange(
                    file_path=file_path,
                    change_type='added',
                    new_hash=file_hash
                ))
            return changes
        
        previous_files = set(cached_course["file_paths"])
        current_files_set = set(current_files)
        
        # Detect added files
        added_files = current_files_set - previous_files
        for file_path in added_files:
            file_hash = self._compute_file_hash(file_path)
            changes.append(FileChange(
                file_path=file_path,
                change_type='added',
                new_hash=file_hash
            ))
            logger.info(f"Detected added file: {file_path}")
        
        # Detect deleted files
        deleted_files = previous_files - current_files_set
        for file_path in deleted_files:
            old_hash = self.file_hashes.get(file_path, "")
            changes.append(FileChange(
                file_path=file_path,
                change_type='deleted',
                old_hash=old_hash
            ))
            logger.info(f"Detected deleted file: {file_path}")
        
        # Detect modified files
        for file_path in current_files_set & previous_files:
            current_hash = self._compute_file_hash(file_path)
            
            # Check if file has changed using cache
            if await self.cache._is_file_changed(file_path):
                old_hash = self.file_hashes.get(file_path, "")
                if current_hash != old_hash:
                    changes.append(FileChange(
                        file_path=file_path,
                        change_type='modified',
                        old_hash=old_hash,
                        new_hash=current_hash
                    ))
                    logger.info(f"Detected modified file: {file_path}")
            
            # Update hash tracking
            self.file_hashes[file_path] = current_hash
        
        logger.info(
            f"Detected {len(changes)} file changes: "
            f"{len(added_files)} added, {len(deleted_files)} deleted, "
            f"{len([c for c in changes if c.change_type == 'modified'])} modified"
        )
        
        return changes
    
    def identify_lessons_to_update(
        self,
        course: CourseOutline,
        file_changes: List[FileChange]
    ) -> List[Tuple[Lesson, FileChange]]:
        """Identify which lessons need updates based on file changes.
        
        Implements Requirement 15.1: Detects which lessons need updates.
        
        Args:
            course: Current course outline
            file_changes: List of detected file changes
            
        Returns:
            List of (Lesson, FileChange) tuples for lessons that need updates
        """
        lessons_to_update = []
        
        # Build map of file_path -> lesson
        file_to_lesson: Dict[str, Lesson] = {}
        for module in course.modules:
            for lesson in module.lessons:
                file_to_lesson[lesson.file_path] = lesson
        
        # Match file changes to lessons
        for change in file_changes:
            if change.file_path in file_to_lesson:
                lesson = file_to_lesson[change.file_path]
                
                # Check if lesson has manual edits that should be preserved
                if self._has_manual_edits(lesson.lesson_id):
                    logger.info(
                        f"Lesson {lesson.lesson_id} has manual edits, "
                        f"will preserve during update"
                    )
                
                lessons_to_update.append((lesson, change))
        
        logger.info(f"Identified {len(lessons_to_update)} lessons to update")
        return lessons_to_update
    
    def _has_manual_edits(self, lesson_id: str) -> bool:
        """Check if a lesson has manual edits.
        
        Implements Requirement 15.2: Preserves manual edits.
        
        Args:
            lesson_id: Lesson identifier
            
        Returns:
            True if lesson has manual edits, False otherwise
        """
        return lesson_id in self.manual_edits and len(self.manual_edits[lesson_id]) > 0
    
    def mark_manual_edit(self, lesson_id: str, section: str):
        """Mark a section of a lesson as manually edited.
        
        Implements Requirement 15.2: Tracks manual edits to preserve them.
        
        Args:
            lesson_id: Lesson identifier
            section: Section name that was edited (e.g., 'introduction', 'explanation')
        """
        if lesson_id not in self.manual_edits:
            self.manual_edits[lesson_id] = set()
        
        self.manual_edits[lesson_id].add(section)
        logger.info(f"Marked manual edit: {lesson_id}.{section}")
    
    def preserve_manual_edits(
        self,
        lesson_id: str,
        old_content: LessonContent,
        new_content: LessonContent
    ) -> LessonContent:
        """Preserve manually edited sections when updating lesson content.
        
        Implements Requirement 15.2: Preserves manual edits to lesson content.
        
        Args:
            lesson_id: Lesson identifier
            old_content: Previous lesson content (may have manual edits)
            new_content: Newly generated lesson content
            
        Returns:
            Merged lesson content with manual edits preserved
        """
        if not self._has_manual_edits(lesson_id):
            return new_content
        
        edited_sections = self.manual_edits[lesson_id]
        
        # Create a copy of new content
        merged_content = LessonContent(
            introduction=new_content.introduction,
            explanation=new_content.explanation,
            code_example=new_content.code_example,
            walkthrough=new_content.walkthrough,
            summary=new_content.summary,
            further_reading=new_content.further_reading
        )
        
        # Preserve manually edited sections
        if 'introduction' in edited_sections:
            merged_content.introduction = old_content.introduction
            logger.info(f"Preserved manual edit: {lesson_id}.introduction")
        
        if 'explanation' in edited_sections:
            merged_content.explanation = old_content.explanation
            logger.info(f"Preserved manual edit: {lesson_id}.explanation")
        
        if 'walkthrough' in edited_sections:
            merged_content.walkthrough = old_content.walkthrough
            logger.info(f"Preserved manual edit: {lesson_id}.walkthrough")
        
        if 'summary' in edited_sections:
            merged_content.summary = old_content.summary
            logger.info(f"Preserved manual edit: {lesson_id}.summary")
        
        if 'further_reading' in edited_sections:
            merged_content.further_reading = old_content.further_reading
            logger.info(f"Preserved manual edit: {lesson_id}.further_reading")
        
        # Note: code_example is always regenerated from source
        
        return merged_content
    
    def archive_lesson(self, course_id: str, lesson: Lesson, reason: str = "file_deleted"):
        """Archive a lesson instead of deleting it.
        
        Implements Requirement 15.3: Archives deleted lessons rather than deleting them.
        
        Args:
            course_id: Course identifier
            lesson: Lesson to archive
            reason: Reason for archiving
        """
        if course_id not in self.archived_lessons:
            self.archived_lessons[course_id] = []
        
        # Add archive metadata
        lesson.tags.append(f"archived:{reason}")
        lesson.tags.append(f"archived_at:{datetime.now().isoformat()}")
        
        self.archived_lessons[course_id].append(lesson)
        
        logger.info(
            f"Archived lesson {lesson.lesson_id} ({lesson.title}) "
            f"from course {course_id}: {reason}"
        )
    
    def get_archived_lessons(self, course_id: str) -> List[Lesson]:
        """Get archived lessons for a course.
        
        Args:
            course_id: Course identifier
            
        Returns:
            List of archived lessons
        """
        return self.archived_lessons.get(course_id, [])
    
    def create_version(
        self,
        course_id: str,
        version: str,
        change_summary: str,
        lesson_updates: List[LessonUpdate],
        file_changes: List[FileChange],
        total_lessons: int
    ) -> CourseVersion:
        """Create a new course version entry.
        
        Implements Requirement 15.4: Tracks course version history.
        
        Args:
            course_id: Course identifier
            version: Version string (e.g., "1.0.1")
            change_summary: Summary of changes
            lesson_updates: List of lesson updates
            file_changes: List of file changes
            total_lessons: Total number of lessons in course
            
        Returns:
            CourseVersion object
        """
        now = datetime.now()
        
        course_version = CourseVersion(
            version=version,
            created_at=now,
            updated_at=now,
            change_summary=change_summary,
            lesson_updates=lesson_updates,
            file_changes=file_changes,
            total_lessons=total_lessons,
            updated_lessons=len(lesson_updates),
            archived_lessons=len([u for u in lesson_updates if u.update_type == 'archived'])
        )
        
        # Add to version history
        if course_id not in self.version_history:
            self.version_history[course_id] = []
        
        self.version_history[course_id].append(course_version)
        
        logger.info(
            f"Created course version {version} for {course_id}: "
            f"{course_version.updated_lessons} lessons updated, "
            f"{course_version.archived_lessons} lessons archived"
        )
        
        return course_version
    
    def get_version_history(self, course_id: str) -> List[CourseVersion]:
        """Get version history for a course.
        
        Implements Requirement 15.4: Provides access to course version history.
        
        Args:
            course_id: Course identifier
            
        Returns:
            List of CourseVersion objects, newest first (in reverse order of creation)
        """
        history = self.version_history.get(course_id, [])
        # Return in reverse order (newest first) since versions are appended chronologically
        return list(reversed(history))
    
    def get_latest_version(self, course_id: str) -> Optional[CourseVersion]:
        """Get the latest version for a course.
        
        Args:
            course_id: Course identifier
            
        Returns:
            Latest CourseVersion or None if no versions exist
        """
        history = self.get_version_history(course_id)
        return history[0] if history else None
    
    def increment_version(self, current_version: str, change_type: str = "minor") -> str:
        """Increment version number based on change type.
        
        Args:
            current_version: Current version string (e.g., "1.0.0")
            change_type: Type of change ('major', 'minor', 'patch')
            
        Returns:
            New version string
        """
        try:
            parts = current_version.split('.')
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            if change_type == 'major':
                major += 1
                minor = 0
                patch = 0
            elif change_type == 'minor':
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
            
            return f"{major}.{minor}.{patch}"
        except Exception as e:
            logger.warning(f"Failed to increment version {current_version}: {e}")
            return current_version
    
    def save_version_history(self, course_id: str, output_path: Optional[str] = None):
        """Save version history to disk.
        
        Args:
            course_id: Course identifier
            output_path: Optional custom output path
        """
        if output_path is None:
            output_path = os.path.join(
                self.output_dir,
                course_id,
                "version_history.json"
            )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        history = self.get_version_history(course_id)
        
        # Serialize to JSON
        history_data = []
        for version in history:
            history_data.append({
                "version": version.version,
                "created_at": version.created_at.isoformat(),
                "updated_at": version.updated_at.isoformat(),
                "change_summary": version.change_summary,
                "total_lessons": version.total_lessons,
                "updated_lessons": version.updated_lessons,
                "archived_lessons": version.archived_lessons,
                "lesson_updates": [
                    {
                        "lesson_id": u.lesson_id,
                        "file_path": u.file_path,
                        "update_type": u.update_type,
                        "changes": u.changes,
                        "timestamp": u.timestamp.isoformat()
                    }
                    for u in version.lesson_updates
                ],
                "file_changes": [
                    {
                        "file_path": c.file_path,
                        "change_type": c.change_type,
                        "old_hash": c.old_hash,
                        "new_hash": c.new_hash,
                        "detected_at": c.detected_at.isoformat()
                    }
                    for c in version.file_changes
                ]
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2)
        
        logger.info(f"Saved version history to {output_path}")
    
    def load_version_history(self, course_id: str, input_path: Optional[str] = None):
        """Load version history from disk.
        
        Args:
            course_id: Course identifier
            input_path: Optional custom input path
        """
        if input_path is None:
            input_path = os.path.join(
                self.output_dir,
                course_id,
                "version_history.json"
            )
        
        if not os.path.exists(input_path):
            logger.debug(f"No version history file found at {input_path}")
            return
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            # Deserialize from JSON
            versions = []
            for data in history_data:
                version = CourseVersion(
                    version=data["version"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                    change_summary=data["change_summary"],
                    total_lessons=data["total_lessons"],
                    updated_lessons=data["updated_lessons"],
                    archived_lessons=data["archived_lessons"],
                    lesson_updates=[
                        LessonUpdate(
                            lesson_id=u["lesson_id"],
                            file_path=u["file_path"],
                            update_type=u["update_type"],
                            changes=u["changes"],
                            timestamp=datetime.fromisoformat(u["timestamp"])
                        )
                        for u in data["lesson_updates"]
                    ],
                    file_changes=[
                        FileChange(
                            file_path=c["file_path"],
                            change_type=c["change_type"],
                            old_hash=c.get("old_hash"),
                            new_hash=c.get("new_hash"),
                            detected_at=datetime.fromisoformat(c["detected_at"])
                        )
                        for c in data["file_changes"]
                    ]
                )
                versions.append(version)
            
            self.version_history[course_id] = versions
            logger.info(f"Loaded {len(versions)} versions from {input_path}")
            
        except Exception as e:
            logger.error(f"Failed to load version history from {input_path}: {e}")


    async def update_course_incrementally(
        self,
        course: CourseOutline,
        analysis: CodebaseAnalysis,
        file_changes: List[FileChange],
        content_generator,
        structure_generator
    ) -> Tuple[CourseOutline, CourseVersion]:
        """Update course incrementally based on file changes.
        
        Implements Requirements 15.1, 15.2, 15.3, 15.5:
        - Updates only changed lessons
        - Preserves manual edits
        - Archives deleted lessons
        - Completes updates in <3s for <5 changes
        
        Args:
            course: Current course outline
            analysis: Current codebase analysis
            file_changes: List of detected file changes
            content_generator: LessonContentGenerator instance
            structure_generator: CourseStructureGenerator instance
            
        Returns:
            Tuple of (updated CourseOutline, CourseVersion)
        """
        start_time = time.time()
        
        logger.info(
            f"Starting incremental update for course {course.course_id} "
            f"with {len(file_changes)} file changes"
        )
        
        # Identify lessons to update
        lessons_to_update = self.identify_lessons_to_update(course, file_changes)
        
        # Track updates
        lesson_updates: List[LessonUpdate] = []
        
        # Process each lesson update
        for lesson, change in lessons_to_update:
            if change.change_type == 'deleted':
                # Archive the lesson
                self.archive_lesson(course.course_id, lesson, "file_deleted")
                lesson_updates.append(LessonUpdate(
                    lesson_id=lesson.lesson_id,
                    file_path=lesson.file_path,
                    update_type='archived',
                    changes=['File deleted, lesson archived']
                ))
            
            elif change.change_type in ['added', 'modified']:
                # Update lesson content
                update = await self._update_lesson_content(
                    lesson,
                    analysis,
                    content_generator
                )
                lesson_updates.append(update)
        
        # Remove archived lessons from course
        course = self._remove_archived_lessons(course, lesson_updates)
        
        # Update course metadata
        course.version = self.increment_version(
            course.version,
            'minor' if len(file_changes) > 5 else 'patch'
        )
        course.created_at = datetime.now()  # Update timestamp
        
        # Create version entry
        change_summary = self._generate_change_summary(file_changes, lesson_updates)
        version = self.create_version(
            course.course_id,
            course.version,
            change_summary,
            lesson_updates,
            file_changes,
            self._count_total_lessons(course)
        )
        
        # Save version history
        self.save_version_history(course.course_id)
        
        elapsed_time = time.time() - start_time
        logger.info(
            f"Incremental update completed in {elapsed_time:.2f}s: "
            f"{len(lesson_updates)} lessons updated"
        )
        
        # Verify performance requirement (Req 15.5)
        if len(file_changes) < 5 and elapsed_time > 3.0:
            logger.warning(
                f"Update took {elapsed_time:.2f}s for {len(file_changes)} changes, "
                f"exceeding 3s target"
            )
        
        return course, version
    
    async def _update_lesson_content(
        self,
        lesson: Lesson,
        analysis: CodebaseAnalysis,
        content_generator
    ) -> LessonUpdate:
        """Update content for a single lesson.
        
        Implements Requirement 15.2: Preserves manual edits during update.
        
        Args:
            lesson: Lesson to update
            analysis: Current codebase analysis
            content_generator: LessonContentGenerator instance
            
        Returns:
            LessonUpdate describing the changes
        """
        changes = []
        
        # Get file analysis
        file_analysis = analysis.file_analyses.get(lesson.file_path)
        if not file_analysis:
            logger.warning(f"No analysis found for {lesson.file_path}")
            return LessonUpdate(
                lesson_id=lesson.lesson_id,
                file_path=lesson.file_path,
                update_type='content',
                changes=['No analysis available']
            )
        
        # Store old content if it exists
        old_content = lesson.content
        
        # Generate new content
        new_content = await content_generator.generate_lesson_content(file_analysis)
        
        # Preserve manual edits if any
        if old_content and self._has_manual_edits(lesson.lesson_id):
            merged_content = self.preserve_manual_edits(
                lesson.lesson_id,
                old_content,
                new_content
            )
            lesson.content = merged_content
            changes.append("Preserved manual edits")
        else:
            lesson.content = new_content
            changes.append("Regenerated content")
        
        # Update lesson metadata
        lesson.teaching_value = file_analysis.teaching_value.score
        
        # Update learning objectives if patterns changed
        old_patterns = set(lesson.concepts)
        new_patterns = set(p.pattern_type for p in file_analysis.patterns)
        
        if old_patterns != new_patterns:
            lesson.concepts = list(new_patterns)
            lesson.tags = list(new_patterns)
            changes.append(f"Updated patterns: {new_patterns - old_patterns}")
        
        # Update complexity-based difficulty
        new_difficulty = self._calculate_difficulty(file_analysis)
        if new_difficulty != lesson.difficulty:
            old_diff = lesson.difficulty
            lesson.difficulty = new_difficulty
            changes.append(f"Difficulty changed: {old_diff} -> {new_difficulty}")
        
        return LessonUpdate(
            lesson_id=lesson.lesson_id,
            file_path=lesson.file_path,
            update_type='content',
            changes=changes
        )
    
    def _calculate_difficulty(self, file_analysis) -> str:
        """Calculate lesson difficulty from file analysis.
        
        Args:
            file_analysis: FileAnalysis object
            
        Returns:
            Difficulty level string
        """
        avg_complexity = file_analysis.complexity_metrics.avg_complexity
        
        if avg_complexity <= 5:
            return "beginner"
        elif avg_complexity <= 10:
            return "intermediate"
        else:
            return "advanced"
    
    def _remove_archived_lessons(
        self,
        course: CourseOutline,
        lesson_updates: List[LessonUpdate]
    ) -> CourseOutline:
        """Remove archived lessons from course structure.
        
        Args:
            course: Course outline
            lesson_updates: List of lesson updates
            
        Returns:
            Updated course outline
        """
        archived_ids = {
            u.lesson_id for u in lesson_updates
            if u.update_type == 'archived'
        }
        
        if not archived_ids:
            return course
        
        # Remove archived lessons from modules
        for module in course.modules:
            module.lessons = [
                lesson for lesson in module.lessons
                if lesson.lesson_id not in archived_ids
            ]
            
            # Update lesson order after removal
            for idx, lesson in enumerate(module.lessons):
                lesson.order = idx
            
            # Update module duration
            module.duration_hours = sum(l.duration_minutes for l in module.lessons) / 60.0
        
        # Remove empty modules
        course.modules = [m for m in course.modules if len(m.lessons) > 0]
        
        # Update module order
        for idx, module in enumerate(course.modules):
            module.order = idx
        
        # Update course duration
        course.total_duration_hours = sum(m.duration_hours for m in course.modules)
        
        # Update difficulty distribution
        course.difficulty_distribution = self._calculate_difficulty_distribution(course)
        
        logger.info(f"Removed {len(archived_ids)} archived lessons from course")
        
        return course
    
    def _calculate_difficulty_distribution(self, course: CourseOutline) -> Dict[str, int]:
        """Calculate difficulty distribution across all lessons.
        
        Args:
            course: Course outline
            
        Returns:
            Dictionary mapping difficulty levels to counts
        """
        distribution = {"beginner": 0, "intermediate": 0, "advanced": 0}
        
        for module in course.modules:
            for lesson in module.lessons:
                distribution[lesson.difficulty] += 1
        
        return distribution
    
    def _count_total_lessons(self, course: CourseOutline) -> int:
        """Count total lessons in course.
        
        Args:
            course: Course outline
            
        Returns:
            Total number of lessons
        """
        return sum(len(module.lessons) for module in course.modules)
    
    def _generate_change_summary(
        self,
        file_changes: List[FileChange],
        lesson_updates: List[LessonUpdate]
    ) -> str:
        """Generate a human-readable summary of changes.
        
        Args:
            file_changes: List of file changes
            lesson_updates: List of lesson updates
            
        Returns:
            Change summary string
        """
        parts = []
        
        # Count change types
        added = len([c for c in file_changes if c.change_type == 'added'])
        modified = len([c for c in file_changes if c.change_type == 'modified'])
        deleted = len([c for c in file_changes if c.change_type == 'deleted'])
        
        if added > 0:
            parts.append(f"{added} file(s) added")
        if modified > 0:
            parts.append(f"{modified} file(s) modified")
        if deleted > 0:
            parts.append(f"{deleted} file(s) deleted")
        
        # Count update types
        content_updates = len([u for u in lesson_updates if u.update_type == 'content'])
        archived = len([u for u in lesson_updates if u.update_type == 'archived'])
        
        if content_updates > 0:
            parts.append(f"{content_updates} lesson(s) updated")
        if archived > 0:
            parts.append(f"{archived} lesson(s) archived")
        
        return ", ".join(parts) if parts else "No changes"
    
    async def check_for_updates(
        self,
        course_id: str,
        current_files: List[str],
        analysis: CodebaseAnalysis
    ) -> Tuple[bool, List[FileChange]]:
        """Check if course needs updates.
        
        Args:
            course_id: Course identifier
            current_files: List of current file paths
            analysis: Current codebase analysis
            
        Returns:
            Tuple of (needs_update, file_changes)
        """
        file_changes = await self.detect_file_changes(
            course_id,
            current_files,
            analysis
        )
        
        needs_update = len(file_changes) > 0
        
        return needs_update, file_changes
    
    def get_update_statistics(self, course_id: str) -> Dict[str, Any]:
        """Get statistics about course updates.
        
        Args:
            course_id: Course identifier
            
        Returns:
            Dictionary with update statistics
        """
        history = self.get_version_history(course_id)
        
        if not history:
            return {
                "total_versions": 0,
                "total_updates": 0,
                "total_archived": 0,
                "latest_version": None,
                "last_updated": None
            }
        
        total_updates = sum(v.updated_lessons for v in history)
        total_archived = sum(v.archived_lessons for v in history)
        latest = history[0]
        
        return {
            "total_versions": len(history),
            "total_updates": total_updates,
            "total_archived": total_archived,
            "latest_version": latest.version,
            "last_updated": latest.updated_at.isoformat(),
            "manual_edits": len(self.manual_edits),
            "archived_lessons": len(self.archived_lessons.get(course_id, []))
        }
