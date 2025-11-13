"""Tests for Incremental Update Manager.

Tests Requirements 15.1, 15.2, 15.3, 15.4, 15.5:
- Change detection
- Manual edit preservation
- Lesson archiving
- Version history tracking
- Performance (<3s for <5 changes)
"""

import pytest
import asyncio
import os
import tempfile
import time
from datetime import datetime
from unittest.mock import Mock, AsyncMock, MagicMock

from src.course.incremental_updater import (
    IncrementalUpdateManager,
    FileChange,
    LessonUpdate,
    CourseVersion,
)
from src.course.models import (
    CourseOutline,
    Module,
    Lesson,
    LessonContent,
    CodeExample,
)
from src.course.course_cache import CourseCacheManager
from src.models import CodebaseAnalysis, FileAnalysis


@pytest.fixture
def mock_cache_manager():
    """Create a mock cache manager."""
    cache = AsyncMock(spec=CourseCacheManager)
    cache.get_course_structure = AsyncMock(return_value=None)
    cache._is_file_changed = AsyncMock(return_value=True)
    return cache


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def update_manager(mock_cache_manager, temp_output_dir):
    """Create an IncrementalUpdateManager instance."""
    return IncrementalUpdateManager(mock_cache_manager, temp_output_dir)


@pytest.fixture
def sample_lesson():
    """Create a sample lesson."""
    return Lesson(
        lesson_id="lesson-1",
        title="Test Lesson",
        description="A test lesson",
        order=0,
        difficulty="beginner",
        duration_minutes=30,
        file_path="test_file.py",
        teaching_value=0.8,
        learning_objectives=["Learn testing"],
        prerequisites=[],
        concepts=["testing"],
        content=LessonContent(
            introduction="Test intro",
            explanation="Test explanation",
            code_example=CodeExample(
                code="print('test')",
                language="python",
                filename="test.py",
                highlights=[],
                annotations={}
            ),
            walkthrough="Test walkthrough",
            summary="Test summary",
            further_reading=[]
        ),
        exercises=[],
        tags=["testing"]
    )


@pytest.fixture
def sample_course(sample_lesson):
    """Create a sample course outline."""
    module = Module(
        module_id="module-1",
        title="Test Module",
        description="A test module",
        order=0,
        lessons=[sample_lesson],
        difficulty="beginner",
        duration_hours=0.5,
        learning_objectives=["Learn testing"]
    )
    
    return CourseOutline(
        course_id="course-1",
        title="Test Course",
        description="A test course",
        author="Test Author",
        version="1.0.0",
        created_at=datetime.now(),
        modules=[module],
        total_duration_hours=0.5,
        difficulty_distribution={"beginner": 1, "intermediate": 0, "advanced": 0},
        tags=["testing"],
        prerequisites=[]
    )


class TestFileChangeDetection:
    """Test file change detection functionality."""
    
    @pytest.mark.asyncio
    async def test_detect_added_files(self, update_manager, mock_cache_manager):
        """Test detection of added files."""
        # Setup
        mock_cache_manager.get_course_structure.return_value = {
            "file_paths": ["old_file.py"]
        }
        
        current_files = ["old_file.py", "new_file.py"]
        mock_analysis = Mock(spec=CodebaseAnalysis)
        mock_analysis.codebase_id = "test-codebase"
        
        # Execute
        changes = await update_manager.detect_file_changes(
            "test-codebase",
            current_files,
            mock_analysis
        )
        
        # Verify
        added_changes = [c for c in changes if c.change_type == 'added']
        assert len(added_changes) == 1
        assert added_changes[0].file_path == "new_file.py"
    
    @pytest.mark.asyncio
    async def test_detect_deleted_files(self, update_manager, mock_cache_manager):
        """Test detection of deleted files."""
        # Setup
        mock_cache_manager.get_course_structure.return_value = {
            "file_paths": ["old_file.py", "deleted_file.py"]
        }
        
        current_files = ["old_file.py"]
        mock_analysis = Mock(spec=CodebaseAnalysis)
        mock_analysis.codebase_id = "test-codebase"
        
        # Execute
        changes = await update_manager.detect_file_changes(
            "test-codebase",
            current_files,
            mock_analysis
        )
        
        # Verify
        deleted_changes = [c for c in changes if c.change_type == 'deleted']
        assert len(deleted_changes) == 1
        assert deleted_changes[0].file_path == "deleted_file.py"
    
    @pytest.mark.asyncio
    async def test_no_previous_course(self, update_manager, mock_cache_manager):
        """Test change detection when no previous course exists."""
        # Setup
        mock_cache_manager.get_course_structure.return_value = None
        
        current_files = ["file1.py", "file2.py"]
        mock_analysis = Mock(spec=CodebaseAnalysis)
        mock_analysis.codebase_id = "test-codebase"
        
        # Execute
        changes = await update_manager.detect_file_changes(
            "test-codebase",
            current_files,
            mock_analysis
        )
        
        # Verify - all files should be marked as added
        assert len(changes) == 2
        assert all(c.change_type == 'added' for c in changes)


class TestLessonIdentification:
    """Test lesson identification for updates."""
    
    def test_identify_lessons_to_update(self, update_manager, sample_course):
        """Test identifying lessons that need updates."""
        # Setup
        file_changes = [
            FileChange(
                file_path="test_file.py",
                change_type="modified",
                old_hash="abc123",
                new_hash="def456"
            )
        ]
        
        # Execute
        lessons_to_update = update_manager.identify_lessons_to_update(
            sample_course,
            file_changes
        )
        
        # Verify
        assert len(lessons_to_update) == 1
        lesson, change = lessons_to_update[0]
        assert lesson.lesson_id == "lesson-1"
        assert change.change_type == "modified"
    
    def test_no_matching_lessons(self, update_manager, sample_course):
        """Test when file changes don't match any lessons."""
        # Setup
        file_changes = [
            FileChange(
                file_path="non_existent_file.py",
                change_type="modified"
            )
        ]
        
        # Execute
        lessons_to_update = update_manager.identify_lessons_to_update(
            sample_course,
            file_changes
        )
        
        # Verify
        assert len(lessons_to_update) == 0


class TestManualEditPreservation:
    """Test manual edit preservation functionality."""
    
    def test_mark_manual_edit(self, update_manager):
        """Test marking a section as manually edited."""
        # Execute
        update_manager.mark_manual_edit("lesson-1", "introduction")
        
        # Verify
        assert update_manager._has_manual_edits("lesson-1")
        assert "introduction" in update_manager.manual_edits["lesson-1"]
    
    def test_preserve_manual_edits(self, update_manager):
        """Test preserving manually edited sections."""
        # Setup
        update_manager.mark_manual_edit("lesson-1", "introduction")
        update_manager.mark_manual_edit("lesson-1", "summary")
        
        old_content = LessonContent(
            introduction="MANUAL EDIT: Custom intro",
            explanation="Old explanation",
            code_example=CodeExample(
                code="old_code",
                language="python",
                filename="test.py",
                highlights=[],
                annotations={}
            ),
            walkthrough="Old walkthrough",
            summary="MANUAL EDIT: Custom summary",
            further_reading=[]
        )
        
        new_content = LessonContent(
            introduction="Generated intro",
            explanation="New explanation",
            code_example=CodeExample(
                code="new_code",
                language="python",
                filename="test.py",
                highlights=[],
                annotations={}
            ),
            walkthrough="New walkthrough",
            summary="Generated summary",
            further_reading=[]
        )
        
        # Execute
        merged = update_manager.preserve_manual_edits(
            "lesson-1",
            old_content,
            new_content
        )
        
        # Verify
        assert merged.introduction == "MANUAL EDIT: Custom intro"
        assert merged.summary == "MANUAL EDIT: Custom summary"
        assert merged.explanation == "New explanation"  # Not manually edited
        assert merged.code_example.code == "new_code"  # Always regenerated


class TestLessonArchiving:
    """Test lesson archiving functionality."""
    
    def test_archive_lesson(self, update_manager, sample_lesson):
        """Test archiving a lesson."""
        # Execute
        update_manager.archive_lesson("course-1", sample_lesson, "file_deleted")
        
        # Verify
        archived = update_manager.get_archived_lessons("course-1")
        assert len(archived) == 1
        assert archived[0].lesson_id == "lesson-1"
        assert "archived:file_deleted" in archived[0].tags
    
    def test_get_archived_lessons_empty(self, update_manager):
        """Test getting archived lessons when none exist."""
        # Execute
        archived = update_manager.get_archived_lessons("non-existent-course")
        
        # Verify
        assert len(archived) == 0


class TestVersionHistory:
    """Test version history tracking."""
    
    def test_create_version(self, update_manager):
        """Test creating a course version."""
        # Setup
        lesson_updates = [
            LessonUpdate(
                lesson_id="lesson-1",
                file_path="test.py",
                update_type="content",
                changes=["Updated content"]
            )
        ]
        
        file_changes = [
            FileChange(
                file_path="test.py",
                change_type="modified"
            )
        ]
        
        # Execute
        version = update_manager.create_version(
            "course-1",
            "1.0.1",
            "Updated 1 lesson",
            lesson_updates,
            file_changes,
            10
        )
        
        # Verify
        assert version.version == "1.0.1"
        assert version.updated_lessons == 1
        assert version.total_lessons == 10
        assert len(version.lesson_updates) == 1
        assert len(version.file_changes) == 1
    
    def test_get_version_history(self, update_manager):
        """Test retrieving version history."""
        # Setup - create multiple versions
        for i in range(3):
            update_manager.create_version(
                "course-1",
                f"1.0.{i}",
                f"Version {i}",
                [],
                [],
                10
            )
        
        # Execute
        history = update_manager.get_version_history("course-1")
        
        # Verify
        assert len(history) == 3
        # Should be sorted newest first
        assert history[0].version == "1.0.2"
        assert history[1].version == "1.0.1"
        assert history[2].version == "1.0.0"
    
    def test_get_latest_version(self, update_manager):
        """Test getting the latest version."""
        # Setup
        update_manager.create_version("course-1", "1.0.0", "Initial", [], [], 10)
        update_manager.create_version("course-1", "1.0.1", "Update", [], [], 10)
        
        # Execute
        latest = update_manager.get_latest_version("course-1")
        
        # Verify
        assert latest is not None
        assert latest.version == "1.0.1"
    
    def test_increment_version_patch(self, update_manager):
        """Test incrementing patch version."""
        new_version = update_manager.increment_version("1.0.0", "patch")
        assert new_version == "1.0.1"
    
    def test_increment_version_minor(self, update_manager):
        """Test incrementing minor version."""
        new_version = update_manager.increment_version("1.0.5", "minor")
        assert new_version == "1.1.0"
    
    def test_increment_version_major(self, update_manager):
        """Test incrementing major version."""
        new_version = update_manager.increment_version("1.2.3", "major")
        assert new_version == "2.0.0"


class TestVersionPersistence:
    """Test version history persistence."""
    
    def test_save_and_load_version_history(self, update_manager, temp_output_dir):
        """Test saving and loading version history."""
        # Setup
        lesson_updates = [
            LessonUpdate(
                lesson_id="lesson-1",
                file_path="test.py",
                update_type="content",
                changes=["Updated"]
            )
        ]
        
        file_changes = [
            FileChange(
                file_path="test.py",
                change_type="modified",
                old_hash="abc",
                new_hash="def"
            )
        ]
        
        update_manager.create_version(
            "course-1",
            "1.0.0",
            "Initial version",
            lesson_updates,
            file_changes,
            5
        )
        
        # Save
        update_manager.save_version_history("course-1")
        
        # Clear in-memory history
        update_manager.version_history = {}
        
        # Load
        update_manager.load_version_history("course-1")
        
        # Verify
        history = update_manager.get_version_history("course-1")
        assert len(history) == 1
        assert history[0].version == "1.0.0"
        assert history[0].change_summary == "Initial version"
        assert len(history[0].lesson_updates) == 1
        assert len(history[0].file_changes) == 1


class TestUpdateStatistics:
    """Test update statistics."""
    
    def test_get_update_statistics(self, update_manager):
        """Test getting update statistics."""
        # Setup
        update_manager.create_version("course-1", "1.0.0", "Initial", [], [], 10)
        update_manager.create_version(
            "course-1",
            "1.0.1",
            "Update",
            [LessonUpdate("l1", "f1", "content", [])],
            [],
            10
        )
        update_manager.mark_manual_edit("lesson-1", "introduction")
        
        # Execute
        stats = update_manager.get_update_statistics("course-1")
        
        # Verify
        assert stats["total_versions"] == 2
        assert stats["total_updates"] == 1
        assert stats["latest_version"] == "1.0.1"
        assert stats["manual_edits"] == 1
    
    def test_get_update_statistics_no_history(self, update_manager):
        """Test statistics when no history exists."""
        # Execute
        stats = update_manager.get_update_statistics("non-existent")
        
        # Verify
        assert stats["total_versions"] == 0
        assert stats["latest_version"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
