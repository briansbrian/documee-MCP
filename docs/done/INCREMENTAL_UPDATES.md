# Incremental Course Updates

This document describes the incremental update functionality for the Course Generator, which allows courses to be updated efficiently when source code changes.

## Overview

The Incremental Update Manager implements Requirements 15.1-15.5:
- **Change Detection**: Automatically detects which files have been added, modified, or deleted
- **Manual Edit Preservation**: Preserves manually edited lesson sections during updates
- **Lesson Archiving**: Archives lessons instead of deleting them when files are removed
- **Version History**: Tracks all course updates with detailed change logs
- **Performance**: Completes updates in <3s for <5 file changes

## Key Components

### IncrementalUpdateManager

The main class that orchestrates incremental updates.

```python
from src.course import IncrementalUpdateManager
from src.course.course_cache import CourseCacheManager

# Initialize
cache_manager = CourseCacheManager(unified_cache)
update_manager = IncrementalUpdateManager(cache_manager, output_dir="output/courses")
```

### Data Models

- **FileChange**: Represents a change to a source file (added, modified, deleted)
- **LessonUpdate**: Represents an update to a lesson
- **CourseVersion**: Represents a version of the course with change history

## Usage Examples

### 1. Detect File Changes

```python
# Detect what has changed since last course generation
file_changes = await update_manager.detect_file_changes(
    codebase_id="my-project",
    current_files=["src/file1.py", "src/file2.py"],
    analysis=codebase_analysis
)

# Check results
for change in file_changes:
    print(f"{change.change_type}: {change.file_path}")
```

### 2. Update Course Incrementally

```python
# Perform incremental update
updated_course, version = await update_manager.update_course_incrementally(
    course=current_course,
    analysis=codebase_analysis,
    file_changes=file_changes,
    content_generator=lesson_content_generator,
    structure_generator=course_structure_generator
)

print(f"Updated to version {version.version}")
print(f"Changes: {version.change_summary}")
print(f"Updated {version.updated_lessons} lessons")
print(f"Archived {version.archived_lessons} lessons")
```

### 3. Preserve Manual Edits

```python
# Mark a section as manually edited
update_manager.mark_manual_edit("lesson-123", "introduction")
update_manager.mark_manual_edit("lesson-123", "summary")

# During update, these sections will be preserved
# The system automatically merges manual edits with regenerated content
```

### 4. Access Version History

```python
# Get version history
history = update_manager.get_version_history("course-id")

for version in history:
    print(f"Version {version.version} - {version.created_at}")
    print(f"  {version.change_summary}")
    print(f"  Updated: {version.updated_lessons} lessons")
    print(f"  Archived: {version.archived_lessons} lessons")

# Get latest version
latest = update_manager.get_latest_version("course-id")
```

### 5. View Archived Lessons

```python
# Get archived lessons
archived = update_manager.get_archived_lessons("course-id")

for lesson in archived:
    print(f"Archived: {lesson.title}")
    print(f"  Reason: {[t for t in lesson.tags if t.startswith('archived:')]}")
```

### 6. Check Update Statistics

```python
# Get statistics about updates
stats = update_manager.get_update_statistics("course-id")

print(f"Total versions: {stats['total_versions']}")
print(f"Total updates: {stats['total_updates']}")
print(f"Total archived: {stats['total_archived']}")
print(f"Latest version: {stats['latest_version']}")
print(f"Manual edits: {stats['manual_edits']}")
```

## Workflow

### Initial Course Generation

1. Generate course from codebase analysis
2. Export to desired format (MkDocs, JSON, etc.)
3. Version 1.0.0 is created automatically

### Incremental Update

1. **Detect Changes**: System detects file changes since last generation
2. **Identify Lessons**: Maps file changes to affected lessons
3. **Preserve Edits**: Checks for manual edits and preserves them
4. **Update Content**: Regenerates content for changed lessons only
5. **Archive Deleted**: Archives lessons for deleted files
6. **Create Version**: Creates new version entry with change log
7. **Export**: Re-export updated course

### Manual Edit Workflow

1. User manually edits a lesson section (e.g., introduction)
2. User marks the section as manually edited via API or UI
3. During next update, system preserves the manual edit
4. Other sections are regenerated normally

## Performance

The system is optimized for fast updates:

- **<3s for <5 changes**: Updates complete in under 3 seconds for small changes
- **Caching**: Leverages existing cache infrastructure
- **Selective Updates**: Only regenerates changed lessons
- **Efficient Detection**: Uses file hashes and modification times

## Version History Persistence

Version history is automatically saved to disk:

```
output/courses/
  └── course-id/
      ├── version_history.json  # Complete version history
      ├── docs/                 # Course content
      └── mkdocs.yml           # MkDocs configuration
```

The version history file contains:
- All version entries
- File changes for each version
- Lesson updates for each version
- Timestamps and change summaries

## Best Practices

### 1. Mark Manual Edits Immediately

```python
# Mark edits right after making them
update_manager.mark_manual_edit(lesson_id, section_name)
```

### 2. Regular Version Saves

```python
# Save version history after updates
update_manager.save_version_history(course_id)
```

### 3. Load History on Startup

```python
# Load existing history when initializing
update_manager.load_version_history(course_id)
```

### 4. Check Before Updating

```python
# Check if updates are needed
needs_update, changes = await update_manager.check_for_updates(
    course_id,
    current_files,
    analysis
)

if needs_update:
    # Perform update
    pass
```

### 5. Review Archived Lessons

```python
# Periodically review archived lessons
archived = update_manager.get_archived_lessons(course_id)

# Decide whether to permanently delete or restore
```

## Integration with MCP Tools

The incremental update functionality can be integrated with MCP tools:

```python
@mcp.tool()
async def update_course(codebase_id: str) -> dict:
    """Update an existing course with latest code changes."""
    
    # Get current analysis
    analysis = await analyze_codebase(codebase_id)
    
    # Get current course
    course = load_course(codebase_id)
    
    # Get current files
    current_files = list(analysis.file_analyses.keys())
    
    # Check for updates
    needs_update, changes = await update_manager.check_for_updates(
        codebase_id,
        current_files,
        analysis
    )
    
    if not needs_update:
        return {"status": "up_to_date", "message": "No changes detected"}
    
    # Perform update
    updated_course, version = await update_manager.update_course_incrementally(
        course,
        analysis,
        changes,
        content_generator,
        structure_generator
    )
    
    # Export updated course
    await export_course(updated_course, format="mkdocs")
    
    return {
        "status": "updated",
        "version": version.version,
        "changes": version.change_summary,
        "updated_lessons": version.updated_lessons,
        "archived_lessons": version.archived_lessons
    }
```

## Error Handling

The system handles various error conditions:

- **Missing Files**: Gracefully handles files that can't be read
- **Invalid Hashes**: Falls back to modification time comparison
- **Missing Analysis**: Logs warnings and skips updates
- **Serialization Errors**: Catches and logs JSON errors

## Future Enhancements

Potential improvements for future versions:

1. **Conflict Resolution**: UI for resolving conflicts between manual edits and regenerated content
2. **Diff Visualization**: Show diffs between versions
3. **Rollback**: Ability to rollback to previous versions
4. **Selective Updates**: UI to choose which lessons to update
5. **Batch Updates**: Update multiple courses at once
6. **Change Notifications**: Notify users when updates are available

## Testing

Comprehensive tests are available in `tests/test_incremental_updates.py`:

```bash
# Run incremental update tests
pytest tests/test_incremental_updates.py -v

# Run with coverage
pytest tests/test_incremental_updates.py --cov=src.course.incremental_updater
```

## Requirements Mapping

- **Requirement 15.1**: `detect_file_changes()`, `identify_lessons_to_update()`
- **Requirement 15.2**: `mark_manual_edit()`, `preserve_manual_edits()`
- **Requirement 15.3**: `archive_lesson()`, `get_archived_lessons()`
- **Requirement 15.4**: `create_version()`, `get_version_history()`
- **Requirement 15.5**: Performance optimizations, caching, selective updates

## Summary

The Incremental Update Manager provides a robust solution for keeping courses synchronized with evolving codebases while preserving manual customizations and maintaining a complete history of changes.
