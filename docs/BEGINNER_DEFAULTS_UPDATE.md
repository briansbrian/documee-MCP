# Beginner-Friendly Defaults Update

## Summary

Updated the `export_course` MCP tool to use beginner-friendly, comprehensive defaults that include ALL content by default.

## New Defaults

### ✅ Before (Old Defaults)
```python
target_audience = "mixed"
course_focus = "full-stack"
max_duration_hours = None
min_teaching_value = 0.5  # Excluded 50% of content
```

### ✅ After (New Defaults)
```python
target_audience = "beginner"  # Simple language, detailed explanations
course_focus = "full-stack"   # Covers ALL aspects
max_duration_hours = None     # No time limit
min_teaching_value = 0.0      # Includes ALL content (0% excluded)
```

## What This Means

### For Beginners:
- ✅ **Simple Language**: Content uses beginner-friendly explanations
- ✅ **Detailed Explanations**: More context and background information
- ✅ **Comprehensive Coverage**: ALL files included (min_teaching_value = 0.0)
- ✅ **No Time Limits**: Full course without duration restrictions

### For Your Use Case:
You mentioned wanting a "beginner website" - now the defaults are perfect for that:

```json
{
  "codebase_id": "your_id"
}
```

This single line now creates:
- A beginner-friendly course
- With ALL content from your codebase
- Using simple, accessible language
- With no artificial time limits

## Customization Still Available

You can still customize if needed:

```json
{
  "codebase_id": "your_id",
  "max_duration_hours": 10.0,        # Limit to 10 hours
  "min_teaching_value": 0.7,         # Only high-quality lessons
  "target_audience": "advanced",     # Technical language
  "course_focus": "architecture"     # Focus on architecture
}
```

## Files Updated

1. **`src/server.py`**
   - Changed `target_audience` default from `"mixed"` to `"beginner"`
   - Changed `min_teaching_value` default from `0.5` to `0.0`
   - Updated docstring with new defaults and examples

2. **`TASK_8_QUICK_REFERENCE.md`**
   - Updated documentation to reflect beginner-friendly defaults
   - Added clear explanation of what defaults do
   - Updated examples to show simplest usage

## Testing

To test the new defaults:

```bash
# 1. Scan your codebase
# 2. Analyze it
# 3. Export with just the codebase_id:

{
  "codebase_id": "067ceb9a9d7abebe"
}
```

This will now create a comprehensive beginner course with ALL content!

## Benefits

1. **Easier to Use**: Just provide `codebase_id` - that's it!
2. **More Inclusive**: Includes ALL content by default (min_teaching_value = 0.0)
3. **Beginner-Friendly**: Simple language and detailed explanations
4. **Comprehensive**: No artificial limits on duration or content
5. **Still Flexible**: Can override any default if needed

---

**Date**: 2025-11-13  
**Status**: ✅ Complete
