# Course Generator Spec

## Overview

The Course Generator is Phase 2 of the Documee MCP Server project. It transforms codebase analysis results from the Analysis Engine into structured educational courses with lessons, exercises, and multiple export formats.

**Status**: 📝 Spec Complete - Ready for Implementation

## What It Does

The Course Generator takes the output from the Analysis Engine (teaching value scores, patterns, dependencies, complexity metrics) and automatically creates:

1. **Course Structure** - Organized modules and lessons
2. **Lesson Content** - Educational content with code examples
3. **Exercises** - Hands-on coding challenges with solutions
4. **Multiple Exports** - MkDocs, Next.js, JSON, Markdown, PDF

## Key Features

### 🎯 Automatic Course Generation
- Analyzes teaching value scores to identify best content
- Groups related lessons into modules
- Creates logical learning progression (beginner → advanced)
- Estimates lesson duration and difficulty

### 📚 Rich Lesson Content
- Learning objectives from detected patterns
- Code examples with syntax highlighting
- Step-by-step walkthroughs with annotations
- Summaries and further reading

### 💪 Hands-On Exercises
- Coding challenges based on patterns
- Starter code with TODO comments
- Progressive hints
- Test cases for validation
- Complete solutions with explanations

### 🚀 Multiple Export Formats
- **MkDocs** - Professional static site with Material theme
- **Next.js** - Interactive web app with React components
- **JSON** - Structured data for custom UIs
- **Markdown** - Standalone files for any platform
- **PDF** - Printable course materials

### 🔧 Customization
- Target audience (beginner, intermediate, advanced)
- Course focus (patterns, architecture, best practices)
- Custom templates (Jinja2)
- Maximum course duration

### ⚡ Performance
- Course outline generation: <5 seconds
- Lesson generation: <2 seconds
- Exercise generation: <3 seconds
- MkDocs export: <10 seconds

## Architecture

```
Input: CodebaseAnalysis (from Analysis Engine)
  ↓
CourseStructureGenerator → CourseOutline
  ↓
LessonContentGenerator → Lesson Content
  ↓
ExerciseGenerator → Exercises
  ↓
TemplateEngine (Jinja2) → Rendered Content
  ↓
ExportManager → MkDocs | Next.js | JSON | Markdown | PDF
  ↓
Output: Complete Course
```

## MCP Tools

### 1. export_course
Export analyzed codebase as a complete course.

```python
await mcp.call_tool("export_course", {
    "codebase_id": "abc123",
    "format": "mkdocs",
    "output_path": "./my-course"
})
```

### 2. generate_lesson_outline
Generate a lesson outline for a specific file.

```python
await mcp.call_tool("generate_lesson_outline", {
    "file_path": "src/hooks/useAuth.ts",
    "codebase_id": "abc123"
})
```

### 3. create_exercise
Create a coding exercise for a specific pattern.

```python
await mcp.call_tool("create_exercise", {
    "pattern_type": "custom-hooks",
    "difficulty": "intermediate"
})
```

## Documents

### 📋 Requirements
**File**: `requirements.md`

Defines 15 core requirements with 75 acceptance criteria using EARS syntax:
- Course structure generation
- Lesson content generation
- Exercise generation
- MkDocs integration
- Multi-format export
- Learning progression
- Content quality
- Customization
- Template system
- MCP tool integration
- Performance targets
- Error handling
- Content validation
- Metadata generation
- Incremental updates

### 🏗️ Design
**Files**: `design.md`, `design-part2.md`

Comprehensive design covering:
- Architecture and components
- Data models (CourseOutline, Module, Lesson, Exercise)
- Algorithms for course generation
- Template system (Jinja2)
- Export implementations
- MCP tool specifications

### ✅ Tasks
**File**: `tasks.md`

Implementation plan with 14 main tasks and 40+ subtasks:
1. Project structure setup
2. Course structure generator
3. Lesson content generator
4. Exercise generator
5. Template engine
6. MkDocs export
7. Multi-format export
8. MCP tools
9. Content validation
10. Metadata generation
11. Performance optimization
12. Incremental updates
13. Configuration
14. Documentation

## Implementation Timeline

### Week 1: Foundation
- Set up project structure
- Implement data models
- Build course structure generator
- Create module and lesson organization

### Week 2: Content Generation
- Implement lesson content generator
- Build exercise generator
- Set up template engine
- Create default templates

### Week 3: Export & Integration
- Implement MkDocs export
- Add JSON and Markdown export
- Build MCP tools
- Add content validation

### Week 4: Polish & Optimization
- Add Next.js export (optional)
- Implement performance optimization
- Add incremental updates
- Write documentation

## Example Output

### MkDocs Course Structure
```
my-course/
├── mkdocs.yml
├── docs/
│   ├── index.md
│   ├── module-1-react-fundamentals/
│   │   ├── lesson-1-custom-hooks.md
│   │   ├── lesson-2-context-api.md
│   │   └── lesson-3-state-management.md
│   ├── module-2-advanced-patterns/
│   │   ├── lesson-1-compound-components.md
│   │   └── lesson-2-render-props.md
│   └── exercises/
│       ├── exercise-1-build-custom-hook.md
│       └── exercise-2-implement-context.md
```

### Lesson Example
```markdown
# Building Custom Hooks

**Difficulty**: Intermediate | **Duration**: 30 minutes

## Learning Objectives

- Understand the custom hook pattern
- Learn state management in hooks
- Handle side effects properly
- Create reusable hook logic

## Introduction

Custom hooks are a powerful pattern in React that allow you to extract
component logic into reusable functions...

## Code Example

```typescript
function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Check authentication status
    checkAuth().then(setUser).finally(() => setLoading(false));
  }, []);
  
  return { user, loading };
}
```

## Walkthrough

1. **State Management**: We use `useState` to track user and loading state
2. **Side Effects**: `useEffect` runs once on mount to check auth
3. **Return Value**: We return an object with user and loading status

## Exercise

Build your own `useLocalStorage` hook that syncs state with localStorage...
```

## Dependencies

### Required
- **Jinja2** - Template engine
- **markdown** - Markdown processing
- **pyyaml** - YAML generation for mkdocs.yml

### Optional
- **weasyprint** - PDF export
- **next** - Next.js export validation

## Success Criteria

The Course Generator is successful when:

1. ✅ Can generate complete course from analysis in <5 seconds
2. ✅ Exports to MkDocs with proper navigation and theme
3. ✅ Generates clear, educational lesson content
4. ✅ Creates practical coding exercises
5. ✅ Supports multiple export formats
6. ✅ Integrates with MCP tools
7. ✅ Validates content quality
8. ✅ Handles errors gracefully

## Next Steps

1. **Review this spec** - Ensure requirements and design are complete
2. **Start implementation** - Begin with Task 1 (project structure)
3. **Iterate** - Build incrementally, test frequently
4. **Integrate** - Connect with Analysis Engine
5. **Test** - Validate with real codebases
6. **Document** - Create usage examples

## Questions?

- How should we handle very large codebases (1000+ files)?
- Should we support video generation for code walkthroughs?
- Do we need AI-powered explanations for complex code?
- Should exercises be interactive (run in browser)?

---

**Created**: November 12, 2025
**Status**: Ready for Implementation
**Estimated Effort**: 3-4 weeks
**Priority**: High - Core feature for project vision
