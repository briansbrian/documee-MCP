# Quick Start Guide: Transform Any Codebase into a Course Platform

## 🚀 5-Minute Discovery Process

### Step 1: Run Discovery (2 minutes)

```powershell
# Windows PowerShell
.\discover-codebase.ps1 path/to/your/codebase

# This will generate a report showing:
# - Languages used
# - Frameworks detected
# - Project structure
# - Recommended approach
```

### Step 2: Choose Your Pattern (1 minute)

Based on the discovery report, pick one:

| Your Codebase | Choose This Pattern | Time to MVP |
|---------------|-------------------|-------------|
| **Any codebase** | Pattern A: Documentation Overlay | 1-2 weeks |
| **React/Vue/Angular** | Pattern B: Monorepo | 4-6 weeks |
| **Backend API** | Pattern C: API-First | 2-3 weeks |
| **UI Components** | Pattern D: Component Showcase | 1-2 weeks |
| **Good Git history** | Pattern E: Git-Based | 1 week |

### Step 3: Set Up Course Platform (2 minutes)

```bash
# Create Next.js course platform
npx create-next-app@latest course-platform --typescript --tailwind --app

cd course-platform

# Install essential packages
npm install @monaco-editor/react @supabase/supabase-js
npm install react-markdown remark-gfm

# Create basic structure
mkdir -p content/lessons
mkdir -p components/CodeEditor
mkdir -p lib/exercises
```

---

## 📋 Pattern A: Documentation Overlay (Recommended for Most)

**Best for:** Any codebase, minimal disruption, fastest implementation

### Setup (30 minutes)

```bash
# 1. Create course platform
npx create-next-app@latest course-platform

# 2. Install dependencies
cd course-platform
npm install @monaco-editor/react @supabase/supabase-js
npm install gray-matter remark remark-html

# 3. Create content structure
mkdir -p content/lessons/{beginner,intermediate,advanced}
mkdir -p public/code-examples
```

### Create Your First Lesson (15 minutes)

```markdown
<!-- content/lessons/beginner/01-introduction.md -->
---
title: "Getting Started"
description: "Learn the basics"
difficulty: "beginner"
duration: "10 minutes"
---

# Getting Started

## What You'll Learn
- Core concept 1
- Core concept 2
- Core concept 3

## Code Example

```javascript
// Example from your codebase
function example() {
  return "Hello World";
}
```

## Exercise

Implement the function above with your own twist.

## Solution

```javascript
function example() {
  return "Hello from " + name;
}
```
```

### Add Code Editor Component (10 minutes)

```tsx
// components/CodeEditor.tsx
'use client';

import Editor from '@monaco-editor/react';
import { useState } from 'react';

export default function CodeEditor({ 
  initialCode = '', 
  language = 'javascript' 
}) {
  const [code, setCode] = useState(initialCode);

  return (
    <div className="border rounded-lg overflow-hidden">
      <Editor
        height="400px"
        language={language}
        value={code}
        onChange={(value) => setCode(value || '')}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
        }}
      />
    </div>
  );
}
```

### Create Lesson Page (10 minutes)

```tsx
// app/lessons/[slug]/page.tsx
import { readFile } from 'fs/promises';
import { join } from 'path';
import ReactMarkdown from 'react-markdown';
import CodeEditor from '@/components/CodeEditor';

export default async function LessonPage({ 
  params 
}: { 
  params: { slug: string } 
}) {
  const content = await readFile(
    join(process.cwd(), 'content/lessons', `${params.slug}.md`),
    'utf-8'
  );

  return (
    <div className="max-w-4xl mx-auto p-8">
      <ReactMarkdown>{content}</ReactMarkdown>
      <CodeEditor initialCode="// Start coding here" />
    </div>
  );
}
```

### Deploy (5 minutes)

```bash
# Push to GitHub
git init
git add .
git commit -m "Initial course platform"
git push origin main

# Deploy to Vercel
npx vercel --prod
```

**Total Time: ~70 minutes to working course platform!**

---

## 🎯 Pattern B: Monorepo (For Modern React/Vue Apps)

### Setup (1 hour)

```bash
# 1. Convert to monorepo
npm install -g turbo
npx create-turbo@latest

# 2. Restructure
mkdir -p apps/main-app apps/course-platform
mkdir -p packages/ui packages/core

# 3. Move existing code
mv your-existing-app/* apps/main-app/

# 4. Extract shared code
# Move reusable components to packages/ui
# Move business logic to packages/core
```

### Package Structure

```
monorepo/
├── apps/
│   ├── main-app/          # Your original app
│   └── course-platform/   # New course site
├── packages/
│   ├── ui/                # Shared components
│   ├── core/              # Business logic
│   └── config/            # Shared configs
└── turbo.json
```

### Share Components

```tsx
// packages/ui/Button.tsx
export function Button({ children, onClick }) {
  return <button onClick={onClick}>{children}</button>;
}

// apps/course-platform/app/page.tsx
import { Button } from '@repo/ui';

export default function Home() {
  return <Button>Click me</Button>;
}
```

---

## 🔌 Pattern C: API-First (For Backend Apps)

### Setup (30 minutes)

```bash
# 1. Create course platform (frontend only)
npx create-next-app@latest course-platform

# 2. Configure API proxy
# In next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://your-backend:8000/api/:path*'
      }
    ];
  }
};
```

### Create API Playground

```tsx
// app/playground/page.tsx
'use client';

import { useState } from 'react';

export default function APIPlayground() {
  const [response, setResponse] = useState('');

  const testAPI = async () => {
    const res = await fetch('/api/users');
    const data = await res.json();
    setResponse(JSON.stringify(data, null, 2));
  };

  return (
    <div>
      <button onClick={testAPI}>Test API</button>
      <pre>{response}</pre>
    </div>
  );
}
```

---

## 📊 Pattern D: Component Showcase (For UI Libraries)

### Setup (20 minutes)

```bash
# Use Storybook-like approach
npx create-next-app@latest component-showcase

# Install dependencies
npm install @radix-ui/react-tabs
```

### Create Component Showcase

```tsx
// app/components/[name]/page.tsx
import { Button } from '@/your-library/Button';
import CodeEditor from '@/components/CodeEditor';

export default function ComponentPage({ params }) {
  return (
    <div className="grid grid-cols-2 gap-8">
      {/* Live Preview */}
      <div>
        <h2>Preview</h2>
        <Button>Example Button</Button>
      </div>

      {/* Code */}
      <div>
        <h2>Code</h2>
        <CodeEditor 
          initialCode={`<Button>Example Button</Button>`}
          language="tsx"
        />
      </div>
    </div>
  );
}
```

---

## 🎓 Pattern E: Git-Based (Minimal Effort)

### Setup (10 minutes)

```bash
# 1. Create lesson branches
git checkout -b lesson-01-setup
# Make changes for lesson 1
git commit -m "Lesson 1: Setup"

git checkout -b lesson-02-routing
# Make changes for lesson 2
git commit -m "Lesson 2: Routing"

# 2. Create simple viewer
npx create-next-app@latest git-course
```

### Show Git Diffs

```tsx
// app/lessons/[id]/page.tsx
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export default async function GitLesson({ params }) {
  const { stdout } = await execAsync(
    `git diff lesson-${params.id - 1} lesson-${params.id}`
  );

  return (
    <div>
      <h1>Lesson {params.id}</h1>
      <pre>{stdout}</pre>
    </div>
  );
}
```

---

## 🛠️ Essential Tools & Scripts

### 1. Code Snippet Extractor

```javascript
// scripts/extract-snippets.js
const fs = require('fs');
const glob = require('glob');

// Find all files with @lesson comments
const files = glob.sync('../main-app/**/*.{js,ts,tsx}');

files.forEach(file => {
  const content = fs.readFileSync(file, 'utf8');
  
  // Extract snippets between @lesson and @end-lesson
  const regex = /@lesson:(.*?)\n([\s\S]*?)@end-lesson/g;
  let match;
  
  while ((match = regex.exec(content)) !== null) {
    const lessonName = match[1].trim();
    const code = match[2];
    
    fs.writeFileSync(
      `./content/snippets/${lessonName}.txt`,
      code
    );
  }
});
```

### 2. Lesson Generator

```javascript
// scripts/generate-lesson.js
const fs = require('fs');

function generateLesson(title, concept, codeExample) {
  const template = `---
title: "${title}"
concept: "${concept}"
---

# ${title}

## Overview
Learn about ${concept}.

## Code Example

\`\`\`javascript
${codeExample}
\`\`\`

## Exercise
Implement ${concept} yourself.

## Tests
\`\`\`javascript
test('${concept}', () => {
  // Add tests here
});
\`\`\`
`;

  const slug = title.toLowerCase().replace(/\s+/g, '-');
  fs.writeFileSync(`./content/lessons/${slug}.md`, template);
}

// Usage
generateLesson(
  'Understanding Functions',
  'functions',
  'function greet(name) { return `Hello ${name}`; }'
);
```

### 3. Progress Tracker

```typescript
// lib/progress.ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function markLessonComplete(userId: string, lessonId: string) {
  const { data, error } = await supabase
    .from('progress')
    .upsert({
      user_id: userId,
      lesson_id: lessonId,
      completed: true,
      completed_at: new Date().toISOString()
    });

  return { data, error };
}

export async function getUserProgress(userId: string) {
  const { data, error } = await supabase
    .from('progress')
    .select('*')
    .eq('user_id', userId);

  return { data, error };
}
```

---

## 📈 Success Metrics

Track these to measure your course platform:

1. **Engagement**
   - Lessons started
   - Lessons completed
   - Time spent per lesson
   - Return rate

2. **Learning Outcomes**
   - Exercise completion rate
   - Average attempts per exercise
   - Test pass rate
   - Project submissions

3. **Technical**
   - Page load time
   - Code execution time
   - Error rates
   - API response times

---

## 🎯 Next Steps

1. **Week 1:** Set up basic platform with 3-5 lessons
2. **Week 2:** Add code editor and exercise validation
3. **Week 3:** Implement progress tracking
4. **Week 4:** Add authentication and user accounts
5. **Week 5:** Deploy and gather feedback
6. **Week 6+:** Iterate and expand content

---

## 💡 Pro Tips

1. **Start Small:** 5 great lessons > 50 mediocre ones
2. **Test Everything:** Have someone try your course before launch
3. **Iterate Fast:** Ship, gather feedback, improve
4. **Focus on Hands-On:** 80% coding, 20% reading
5. **Make it Fun:** Add gamification, achievements, progress bars

---

## 🆘 Troubleshooting

### Monaco Editor not loading?
```bash
npm install @monaco-editor/react
# Make sure you're using 'use client' directive
```

### Code execution security concerns?
```bash
# Use Docker containers
docker run --rm -i -m 256m --cpus=0.5 node:18 node -e "console.log('safe')"
```

### Slow build times?
```javascript
// Use dynamic imports
const CodeEditor = dynamic(() => import('@/components/CodeEditor'), {
  ssr: false
});
```

---

## 📚 Resources

- [Full Discovery Framework](./codebase-to-course-discovery-framework.md)
- [Course Platform Research](./course-platform-research.md)
- [Discovery Script](./discover-codebase.ps1)

---

**Remember:** The best course platform is one that actually gets built and used. Start simple, ship fast, iterate based on feedback!
