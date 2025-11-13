# Task 8: MCP Tools Quick Reference

## Quick Start

### 1. Generate Lesson Outline

Get a preview of what a lesson would look like from a single file:

```json
{
  "file_path": "src/components/Button.tsx"
}
```

**Returns:** Lesson outline with objectives, concepts, examples, and exercises

### 2. Create Exercise

Generate a coding exercise for a specific pattern:

```json
{
  "pattern_type": "react_component",
  "difficulty": "intermediate"
}
```

**Pattern Types:**
- `react_component`
- `api_route`
- `database_query`
- `authentication`
- `error_handling`
- `async_operation`

**Difficulty Levels:**
- `beginner` (15 min)
- `intermediate` (20-30 min)
- `advanced` (30+ min)

### 3. Export Course

Export a comprehensive beginner course (uses defaults):

```json
{
  "codebase_id": "your_codebase_id"
}
```

**Defaults (Beginner-Friendly & Comprehensive):**
- ✅ `target_audience: "beginner"` - Simple language, detailed explanations
- ✅ `course_focus: "full-stack"` - Covers ALL aspects
- ✅ `max_duration_hours: None` - No time limit, includes everything
- ✅ `min_teaching_value: 0.0` - Includes ALL content
- ✅ `format: "mkdocs"` - Professional website

**Formats:**
- `mkdocs` - Static site with Material theme (default)
- `json` - Structured JSON data
- `markdown` - Standalone markdown files
- `nextjs` - Next.js React application
- `pdf` - Single PDF document

**Target Audience:**
- `beginner` - Simple language, detailed explanations (DEFAULT)
- `intermediate` - Balanced complexity
- `advanced` - Technical language, advanced concepts
- `mixed` - Varied difficulty levels

**Course Focus:**
- `full-stack` - Comprehensive coverage of all aspects (DEFAULT)
- `patterns` - Design patterns emphasis
- `architecture` - System architecture focus
- `best-practices` - Coding best practices

**Optional Filters:**
- `max_duration_hours` - Limit course length (e.g., 10.0 for 10 hours)
- `min_teaching_value` - Filter by quality (0.0-1.0, default: 0.0 = ALL content)

## Complete Workflow

### Step 1: Scan Codebase
```json
{
  "path": "."
}
```
**Tool:** `scan_codebase`
**Save:** `codebase_id` from response

### Step 2: Analyze Codebase
```json
{
  "codebase_id": "<from_step_1>"
}
```
**Tool:** `analyze_codebase_tool`

### Step 3: Preview Lessons (Optional)
```json
{
  "file_path": "src/main.py"
}
```
**Tool:** `generate_lesson_outline`

### Step 4: Create Exercises (Optional)
```json
{
  "pattern_type": "api_route",
  "difficulty": "intermediate",
  "codebase_id": "<from_step_1>"
}
```
**Tool:** `create_exercise`

### Step 5: Export Course (Comprehensive Beginner Course)
```json
{
  "codebase_id": "<from_step_1>"
}
```
**Note:** Defaults create a beginner-friendly course with ALL content included!

**Or customize:**
```json
{
  "codebase_id": "<from_step_1>",
  "max_duration_hours": 10.0,
  "min_teaching_value": 0.5
}
```
**Tool:** `export_course`

## Error Messages

### "Codebase not analyzed"
**Solution:** Run `analyze_codebase_tool` first with your `codebase_id`

### "File not found"
**Solution:** Check the file path is correct and file exists

### "Invalid format"
**Solution:** Use one of: mkdocs, json, markdown, nextjs, pdf

### "Invalid difficulty"
**Solution:** Use one of: beginner, intermediate, advanced

## Tips

1. **Preview First:** Use `generate_lesson_outline` to preview lessons before exporting
2. **Test Exercises:** Use `create_exercise` to test exercise generation
3. **Start Small:** Export to JSON first to see the structure
4. **Use Cache:** Analysis results are cached for fast subsequent calls
5. **Custom Output:** Specify `output_dir` to control where files are saved

## Output Structure

### MkDocs Export
```
output/
├── docs/
│   ├── index.md
│   ├── module-1/
│   │   ├── lesson-1.md
│   │   └── lesson-2.md
│   └── module-2/
│       └── lesson-1.md
└── mkdocs.yml
```

### JSON Export
```
output/
└── course.json
```

### Markdown Export
```
output/
├── README.md
├── module-1/
│   ├── lesson-1.md
│   └── lesson-2.md
└── module-2/
    └── lesson-1.md
```

## Performance

- **Lesson Outline:** < 2 seconds
- **Exercise Creation:** < 3 seconds
- **Course Export:** < 10 seconds (20 lessons)
- **Cached Calls:** < 0.1 seconds

## Support

For issues or questions:
1. Check the logs in `server.log`
2. Verify the codebase has been analyzed
3. Ensure all required parameters are provided
4. Check file paths are correct
