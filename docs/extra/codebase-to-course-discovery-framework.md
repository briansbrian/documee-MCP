# Codebase-to-Course Discovery Framework

## Objective
Transform any existing codebase (unknown framework/language) into an interactive course/tutorial platform with minimal effort.

---

## Phase 1: Codebase Discovery & Analysis

### 1.1 Initial Reconnaissance Questions

#### Language & Framework Detection
- [ ] What programming language(s) are used?
- [ ] What framework(s) are present? (React, Vue, Angular, Django, Rails, Spring, etc.)
- [ ] What's the primary language by file count/LOC?
- [ ] Are there multiple languages (polyglot codebase)?
- [ ] What's the framework version? (Legacy vs modern)

#### Project Structure Analysis
- [ ] What's the directory structure pattern?
- [ ] Is there a clear separation of concerns? (MVC, Clean Architecture, etc.)
- [ ] Where are the main entry points?
- [ ] What's the build system? (Webpack, Vite, Maven, Gradle, etc.)
- [ ] Is there a package manager? (npm, yarn, pip, composer, etc.)

#### Existing Documentation
- [ ] Is there a README?
- [ ] Are there inline code comments?
- [ ] Is there API documentation?
- [ ] Are there existing tutorials or guides?
- [ ] Is there a CONTRIBUTING.md or developer guide?

#### Complexity Assessment
- [ ] How many files/modules?
- [ ] What's the cyclomatic complexity?
- [ ] Are there clear boundaries between components?
- [ ] What's the dependency graph like?
- [ ] Are there tests? (Unit, integration, e2e)

---

## Phase 2: Automated Discovery Tools

### 2.1 File System Analysis

```bash
# Language detection
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn

# Count lines of code by language
cloc . --json

# Find configuration files
find . -maxdepth 2 -name "*.json" -o -name "*.yaml" -o -name "*.toml" -o -name "*.config.*"

# Identify framework markers
ls -la | grep -E "package.json|requirements.txt|Gemfile|pom.xml|build.gradle|composer.json|go.mod|Cargo.toml"
```

### 2.2 Framework Detection Patterns

#### JavaScript/TypeScript
```bash
# Check package.json for framework
cat package.json | jq '.dependencies'

# Common frameworks to look for:
# - react, next, vue, nuxt, angular, svelte, express, nestjs, fastify
```

#### Python
```bash
# Check requirements.txt or pyproject.toml
cat requirements.txt

# Common frameworks:
# - django, flask, fastapi, pyramid, tornado
```

#### Ruby
```bash
# Check Gemfile
cat Gemfile

# Common frameworks:
# - rails, sinatra, hanami
```

#### Java
```bash
# Check pom.xml or build.gradle
cat pom.xml | grep -A 5 "<dependencies>"

# Common frameworks:
# - spring-boot, quarkus, micronaut, jakarta-ee
```

#### PHP
```bash
# Check composer.json
cat composer.json | jq '.require'

# Common frameworks:
# - laravel, symfony, codeigniter, yii
```

#### Go
```bash
# Check go.mod
cat go.mod

# Common frameworks:
# - gin, echo, fiber, chi
```

### 2.3 Dependency Analysis Tools

```bash
# JavaScript
npm list --depth=0
npx depcheck

# Python
pip list
pipdeptree

# Ruby
bundle list

# Java
mvn dependency:tree

# Go
go list -m all
```

---

## Phase 3: Strategic Questions for Course Design

### 3.1 Content Extraction Strategy

#### What Can Be Taught?
- [ ] Is this a library/framework to teach?
- [ ] Is this an application to explain?
- [ ] Are there reusable patterns to demonstrate?
- [ ] Are there best practices embedded in the code?
- [ ] What problems does this codebase solve?

#### Learning Path Identification
- [ ] What's the natural progression? (Beginner → Advanced)
- [ ] What are the core concepts?
- [ ] What are the dependencies between concepts?
- [ ] What can be learned independently?
- [ ] What requires hands-on practice?

#### Code Segmentation
- [ ] Can the code be broken into modules/lessons?
- [ ] Are there clear examples in the codebase?
- [ ] Can features be isolated for teaching?
- [ ] Are there different complexity levels?
- [ ] What's the minimum viable example?

### 3.2 Integration Approach Questions

#### Minimal Disruption Strategy
- [ ] Can we add a `/docs` or `/tutorial` route without touching core code?
- [ ] Can we run the course platform as a separate service?
- [ ] Can we use the existing build system?
- [ ] Can we leverage existing authentication?
- [ ] Can we reuse existing UI components?

#### Embedding vs Standalone
- [ ] Should the course be embedded in the existing app?
- [ ] Should it be a separate subdomain?
- [ ] Should it be a completely separate project?
- [ ] What's the deployment strategy?
- [ ] How do we handle versioning?

---

## Phase 4: Universal Integration Patterns

### 4.1 Pattern A: Documentation Site Overlay

**Best for:** Any codebase with clear module boundaries

```
Strategy:
1. Create a separate Next.js/Docusaurus site
2. Import code snippets from the main codebase
3. Use iframe/sandboxes for live examples
4. Link to actual codebase for reference

Pros:
- Zero impact on main codebase
- Full control over course UX
- Easy to maintain separately

Cons:
- Code can get out of sync
- Requires manual updates
```

**Implementation:**
```
project/
├── main-app/          # Original codebase (untouched)
├── course-platform/   # New Next.js site
│   ├── content/
│   │   ├── lessons/
│   │   └── exercises/
│   ├── components/
│   │   ├── CodeEditor.tsx
│   │   └── LivePreview.tsx
│   └── scripts/
│       └── sync-code-snippets.js  # Auto-extract from main-app
```

### 4.2 Pattern B: Monorepo with Shared Packages

**Best for:** Modern codebases with package management

```
Strategy:
1. Convert to monorepo (if not already)
2. Extract reusable code into packages
3. Course platform imports these packages
4. Students interact with real code

Pros:
- Always in sync
- Students use actual production code
- Shared types/utilities

Cons:
- Requires refactoring
- More complex setup
```

**Implementation:**
```
monorepo/
├── packages/
│   ├── core/           # Extracted from original
│   ├── ui-components/  # Extracted from original
│   └── utils/          # Extracted from original
├── apps/
│   ├── main-app/       # Original app (refactored)
│   └── course/         # New course platform
└── package.json        # Workspace config
```

### 4.3 Pattern C: API-First Approach

**Best for:** Backend-heavy applications

```
Strategy:
1. Expose existing functionality via API
2. Course platform makes API calls
3. Students learn by interacting with real API
4. Sandbox environment for safe experimentation

Pros:
- Minimal backend changes
- Real-world API experience
- Safe for production

Cons:
- Requires API design
- Need sandbox/staging environment
```

**Implementation:**
```
Architecture:
┌─────────────────┐
│ Course Platform │ (Next.js)
│  - Lessons      │
│  - Exercises    │
│  - Code Editor  │
└────────┬────────┘
         │ API Calls
         ▼
┌─────────────────┐
│  Main App API   │ (Existing backend)
│  - /api/v1/*    │
│  - Sandbox mode │
└─────────────────┘
```

### 4.4 Pattern D: Component Showcase

**Best for:** UI libraries, component libraries, design systems

```
Strategy:
1. Create Storybook-like environment
2. Import components from main codebase
3. Interactive playground for each component
4. Live code editing with instant preview

Pros:
- Perfect for UI-focused learning
- Visual feedback
- Component isolation

Cons:
- Limited to frontend
- Requires component architecture
```

**Implementation:**
```
course-platform/
├── showcase/
│   ├── Button/
│   │   ├── lesson.mdx
│   │   ├── examples/
│   │   └── playground.tsx
│   └── Form/
│       ├── lesson.mdx
│       └── examples/
└── import from '../main-app/components'
```

### 4.5 Pattern E: Git-Based Learning

**Best for:** Any codebase with good Git history

```
Strategy:
1. Use Git commits as lesson progression
2. Each lesson = specific commit/branch
3. Students checkout branches to see evolution
4. Diff-based explanations

Pros:
- Leverages existing history
- Shows real development process
- Minimal additional work

Cons:
- Requires clean Git history
- Not interactive
```

**Implementation:**
```
Git Structure:
main
├── lesson-01-setup
├── lesson-02-basic-routing
├── lesson-03-authentication
└── lesson-04-database

Course Platform:
- Displays commit diffs
- Explains changes
- Links to specific files/lines
```

---

## Phase 5: Technology-Agnostic Integration Layer

### 5.1 Universal Course Platform Stack

**Recommended Stack (Works with ANY backend):**

```
Frontend: Next.js 15 + React
- Universal: Works regardless of main app tech
- Can proxy to any backend
- Can embed any framework via iframes
- Monaco Editor for code editing

Backend: Supabase or Firebase
- Separate from main app
- Handles course-specific data:
  - User progress
  - Exercise submissions
  - Comments/discussions
- No interference with main app

Code Execution: Docker + API
- Language-agnostic
- Runs any code safely
- Isolated from main app
```

### 5.2 Integration Bridge Patterns

#### For Any Framework:

**Option 1: Reverse Proxy**
```nginx
# nginx.conf
location /course {
    proxy_pass http://course-platform:3000;
}

location / {
    proxy_pass http://main-app:8080;
}
```

**Option 2: Subdomain**
```
Main app:     app.example.com
Course:       learn.example.com
API:          api.example.com
```

**Option 3: Iframe Embedding**
```tsx
// In main app
<iframe src="https://course.example.com/embed/lesson-1" />

// Course platform has /embed routes
```

---

## Phase 6: Automated Content Generation

### 6.1 Code-to-Lesson Pipeline

```javascript
// Pseudo-code for automated lesson generation

async function generateLessonsFromCodebase(codebasePath) {
  // 1. Analyze codebase structure
  const structure = await analyzeStructure(codebasePath);
  
  // 2. Extract key concepts
  const concepts = await extractConcepts(structure);
  
  // 3. Identify code examples
  const examples = await findExamples(codebasePath, concepts);
  
  // 4. Generate lesson outline
  const lessons = await generateOutline(concepts, examples);
  
  // 5. Create interactive exercises
  const exercises = await createExercises(examples);
  
  return { lessons, exercises };
}
```

### 6.2 AST-Based Analysis

```javascript
// Use Abstract Syntax Tree to understand code

import { parse } from '@babel/parser';
import traverse from '@babel/traverse';

function analyzeJavaScriptFile(code) {
  const ast = parse(code, {
    sourceType: 'module',
    plugins: ['jsx', 'typescript']
  });
  
  const analysis = {
    functions: [],
    classes: [],
    imports: [],
    exports: []
  };
  
  traverse(ast, {
    FunctionDeclaration(path) {
      analysis.functions.push({
        name: path.node.id.name,
        params: path.node.params,
        complexity: calculateComplexity(path)
      });
    },
    ClassDeclaration(path) {
      analysis.classes.push({
        name: path.node.id.name,
        methods: extractMethods(path)
      });
    }
  });
  
  return analysis;
}
```

### 6.3 Documentation Extraction

```javascript
// Extract JSDoc, docstrings, comments

function extractDocumentation(codebasePath) {
  const docs = {
    functions: {},
    classes: {},
    modules: {}
  };
  
  // For JavaScript/TypeScript
  const jsDocComments = extractJSDoc(codebasePath);
  
  // For Python
  const docstrings = extractDocstrings(codebasePath);
  
  // For Java
  const javadoc = extractJavadoc(codebasePath);
  
  return docs;
}
```

---

## Phase 7: Decision Matrix

### 7.1 Choose Your Approach

| Scenario | Recommended Pattern | Effort | Maintenance |
|----------|-------------------|--------|-------------|
| **Large monolithic app** | Documentation Overlay (A) | Low | Low |
| **Modern React/Vue app** | Monorepo (B) | Medium | Medium |
| **Backend API** | API-First (C) | Low | Low |
| **Component library** | Component Showcase (D) | Low | Low |
| **Well-documented Git** | Git-Based (E) | Very Low | Very Low |
| **Legacy codebase** | Documentation Overlay (A) | Low | Low |
| **Microservices** | API-First (C) | Medium | Medium |
| **Open source library** | Documentation Overlay (A) | Low | Low |

### 7.2 Effort Estimation

#### Minimal Effort (1-2 weeks)
- Pattern A: Documentation Overlay
- Pattern E: Git-Based Learning
- Use existing code as-is
- Manual lesson creation

#### Medium Effort (4-6 weeks)
- Pattern B: Monorepo (if already modular)
- Pattern C: API-First
- Some refactoring needed
- Semi-automated content

#### High Effort (8-12 weeks)
- Pattern B: Monorepo (major refactor)
- Full integration
- Automated content generation
- Custom tooling

---

## Phase 8: Implementation Checklist

### 8.1 Pre-Implementation

- [ ] Run automated discovery tools
- [ ] Document current architecture
- [ ] Identify learning objectives
- [ ] Choose integration pattern
- [ ] Set up development environment
- [ ] Create proof of concept

### 8.2 Core Implementation

- [ ] Set up course platform (Next.js)
- [ ] Create content structure
- [ ] Implement code editor (Monaco)
- [ ] Set up code execution (Docker/Sandbox)
- [ ] Build lesson navigation
- [ ] Add progress tracking
- [ ] Implement authentication

### 8.3 Content Creation

- [ ] Extract code examples
- [ ] Write lesson content
- [ ] Create exercises
- [ ] Add tests for validation
- [ ] Record demos (if needed)
- [ ] Peer review content

### 8.4 Integration

- [ ] Connect to main codebase
- [ ] Set up deployment pipeline
- [ ] Configure routing/proxy
- [ ] Test in staging
- [ ] Monitor performance
- [ ] Gather feedback

---

## Phase 9: Universal Tools & Scripts

### 9.1 Discovery Script

```bash
#!/bin/bash
# discover-codebase.sh

echo "=== Codebase Discovery Report ==="
echo ""

echo "1. Languages:"
cloc . --json | jq '.SUM'

echo ""
echo "2. Framework Detection:"
if [ -f "package.json" ]; then
  echo "  - Node.js project detected"
  cat package.json | jq '.dependencies | keys[]' | head -5
fi

if [ -f "requirements.txt" ]; then
  echo "  - Python project detected"
  head -5 requirements.txt
fi

if [ -f "Gemfile" ]; then
  echo "  - Ruby project detected"
  grep "^gem" Gemfile | head -5
fi

if [ -f "pom.xml" ]; then
  echo "  - Java/Maven project detected"
fi

if [ -f "go.mod" ]; then
  echo "  - Go project detected"
  head -5 go.mod
fi

echo ""
echo "3. Directory Structure:"
tree -L 2 -d

echo ""
echo "4. Entry Points:"
find . -name "main.*" -o -name "index.*" -o -name "app.*" | head -10

echo ""
echo "5. Tests:"
find . -name "*test*" -o -name "*spec*" | wc -l
echo "  test files found"

echo ""
echo "6. Documentation:"
find . -name "README*" -o -name "*.md" | head -10
```

### 9.2 Code Snippet Extractor

```javascript
// extract-snippets.js
// Automatically extract code snippets for lessons

const fs = require('fs');
const path = require('path');
const glob = require('glob');

function extractSnippets(codebasePath, outputPath) {
  const files = glob.sync(`${codebasePath}/**/*.{js,ts,py,java,go,rb}`);
  
  const snippets = {};
  
  files.forEach(file => {
    const content = fs.readFileSync(file, 'utf8');
    const lines = content.split('\n');
    
    let currentSnippet = null;
    
    lines.forEach((line, index) => {
      // Look for special comments: // @lesson: lesson-name
      if (line.includes('@lesson:')) {
        const lessonName = line.split('@lesson:')[1].trim();
        currentSnippet = {
          lesson: lessonName,
          file: file,
          startLine: index + 1,
          code: []
        };
      } else if (line.includes('@end-lesson') && currentSnippet) {
        currentSnippet.endLine = index;
        snippets[currentSnippet.lesson] = snippets[currentSnippet.lesson] || [];
        snippets[currentSnippet.lesson].push(currentSnippet);
        currentSnippet = null;
      } else if (currentSnippet) {
        currentSnippet.code.push(line);
      }
    });
  });
  
  fs.writeFileSync(
    path.join(outputPath, 'snippets.json'),
    JSON.stringify(snippets, null, 2)
  );
  
  return snippets;
}

module.exports = { extractSnippets };
```

### 9.3 Lesson Generator Template

```typescript
// lesson-generator.ts
// Generate lesson structure from code analysis

interface LessonTemplate {
  id: string;
  title: string;
  description: string;
  concepts: string[];
  codeExample: string;
  exercise: {
    instructions: string;
    starterCode: string;
    solution: string;
    tests: string;
  };
}

function generateLesson(
  concept: string,
  codeExample: string,
  difficulty: 'beginner' | 'intermediate' | 'advanced'
): LessonTemplate {
  return {
    id: `lesson-${slugify(concept)}`,
    title: `Understanding ${concept}`,
    description: `Learn how to use ${concept} in practice`,
    concepts: [concept],
    codeExample: codeExample,
    exercise: {
      instructions: `Implement ${concept} based on the example above`,
      starterCode: generateStarterCode(codeExample),
      solution: codeExample,
      tests: generateTests(codeExample)
    }
  };
}
```

---

## Phase 10: Quick Start Templates

### 10.1 For JavaScript/TypeScript Projects

```bash
# Quick setup
npx create-next-app@latest course-platform
cd course-platform
npm install monaco-editor @monaco-editor/react
npm install @supabase/supabase-js

# Create basic structure
mkdir -p content/lessons
mkdir -p components/CodeEditor
mkdir -p lib/codebase-sync

# Link to main codebase
ln -s ../main-app ./linked-codebase
```

### 10.2 For Python Projects

```bash
# Use Sphinx or MkDocs
pip install mkdocs mkdocs-material
mkdocs new course-docs
cd course-docs

# Add code execution
pip install jupyter nbconvert
# Embed Jupyter notebooks in docs
```

### 10.3 For Any Project (Universal)

```bash
# Use Docusaurus (supports any language)
npx create-docusaurus@latest course-site classic
cd course-site

# Add interactive code blocks
npm install @docusaurus/theme-live-codeblock

# Configure to import from main codebase
# Edit docusaurus.config.js
```

---

## Summary: The Optimal Approach

### For ANY Unknown Codebase:

1. **Run Discovery** (30 minutes)
   - Use automated tools
   - Identify language/framework
   - Assess complexity

2. **Choose Pattern** (1 hour)
   - Start with Pattern A (Documentation Overlay)
   - Lowest risk, fastest implementation
   - Can always upgrade later

3. **Set Up Platform** (1 day)
   - Next.js + Monaco Editor
   - Separate from main codebase
   - No modifications needed

4. **Extract Content** (1-2 weeks)
   - Manual or semi-automated
   - Focus on key concepts
   - Create 5-10 core lessons

5. **Add Interactivity** (1 week)
   - Code editor
   - Exercise validation
   - Progress tracking

6. **Deploy & Iterate** (Ongoing)
   - Separate deployment
   - Gather feedback
   - Expand content

### The Universal Truth:
**The best approach is the one that requires the LEAST modification to the existing codebase while providing the MOST value to learners.**

Start simple, iterate based on feedback.
