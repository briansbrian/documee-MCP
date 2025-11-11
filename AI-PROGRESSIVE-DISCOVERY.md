# AI Progressive Discovery: Working with Limited Context

## The Core Problem

**As an AI, I have:**
- ❌ Limited context window (can't hold entire codebase)
- ❌ No persistent memory (forget between sessions)
- ❌ Sequential processing (can't read everything at once)

**What I need:**
- ✅ Progressive discovery (learn incrementally)
- ✅ Minimal cache (track what I've learned)
- ✅ Smart prioritization (read important things first)
- ✅ Context management (stay within limits)

## The Solution: Progressive Discovery with Caching

### Phase 0: Initial Reconnaissance (The Missing Step!)

**Before analyzing anything, I need to:**

#### Step 0.1: Get the Big Picture
```
1. List directory structure (depth 2-3)
   → Understand organization
   → Identify major sections
   → See file counts
   
2. Create initial cache
   → Save structure to memory
   → Track what I've seen
   → Plan next steps
```

**Example:**
```bash
# First command I should run
listDirectory(path, depth=2)

# Output:
project/
├── src/ (150 files)
│   ├── components/ (45 files)
│   ├── hooks/ (12 files)
│   ├── pages/ (20 files)
│   ├── api/ (15 files)
│   └── utils/ (10 files)
├── tests/ (80 files)
├── docs/ (5 files)
├── package.json
└── README.md

# Now I know:
# - This is a React project (src/components, src/hooks)
# - It has pages (likely Next.js)
# - It has API routes
# - It's well-tested (80 test files)
# - Total ~235 files (manageable)
```

#### Step 0.2: Create Discovery Cache
```json
{
  "discovery_cache": {
    "timestamp": "2024-01-01T10:00:00Z",
    "project_path": "/path/to/project",
    "structure": {
      "total_files": 235,
      "main_directories": ["src", "tests", "docs"],
      "likely_framework": "Next.js",
      "entry_points_to_check": [
        "package.json",
        "README.md",
        "src/pages/index.tsx",
        "src/app/page.tsx"
      ]
    },
    "progress": {
      "phase": "initial_reconnaissance",
      "files_read": 0,
      "features_discovered": 0,
      "lessons_created": 0
    },
    "next_steps": [
      "Read package.json",
      "Read README.md",
      "Scan src/pages for routes",
      "Scan src/api for endpoints"
    ]
  }
}
```

---

## The Progressive Discovery Process

### Phase 1: Foundation (Read 5-10 files)

**Goal:** Understand what this project is

**Files to read (in order):**
1. `package.json` - Dependencies, scripts, framework
2. `README.md` - Project description, setup
3. Main entry point - `src/index.tsx` or `src/app/page.tsx`
4. Config files - `tsconfig.json`, `next.config.js`
5. Database schema - `schema.prisma`, `migrations/`

**Cache after Phase 1:**
```json
{
  "foundation": {
    "framework": "Next.js 14",
    "language": "TypeScript",
    "database": "PostgreSQL with Prisma",
    "key_dependencies": ["react", "next", "prisma", "supabase"],
    "project_type": "E-commerce platform",
    "main_features": ["auth", "products", "cart", "checkout"]
  },
  "files_read": 5,
  "context_used": "15%"
}
```

---

### Phase 2: Feature Discovery (Read 10-20 files)

**Goal:** Identify all features

**Strategy:**
```
1. Scan routes/pages (don't read content yet)
   → List all pages
   → Infer features from names
   
2. Scan API endpoints (don't read content yet)
   → List all endpoints
   → Infer operations
   
3. Scan components (top-level only)
   → List major components
   → Infer UI features
```

**Example:**
```bash
# Scan pages
listDirectory('src/pages', depth=1)
# Output:
# - login.tsx
# - register.tsx
# - products/index.tsx
# - products/[id].tsx
# - cart.tsx
# - checkout.tsx

# Inferred features:
# - Authentication (login, register)
# - Product catalog (products list, detail)
# - Shopping cart
# - Checkout
```

**Cache after Phase 2:**
```json
{
  "features_discovered": [
    {
      "name": "Authentication",
      "pages": ["login.tsx", "register.tsx"],
      "priority": "high",
      "status": "not_analyzed"
    },
    {
      "name": "Product Catalog",
      "pages": ["products/index.tsx", "products/[id].tsx"],
      "priority": "high",
      "status": "not_analyzed"
    },
    {
      "name": "Shopping Cart",
      "pages": ["cart.tsx"],
      "priority": "medium",
      "status": "not_analyzed"
    },
    {
      "name": "Checkout",
      "pages": ["checkout.tsx"],
      "priority": "high",
      "status": "not_analyzed"
    }
  ],
  "files_read": 15,
  "context_used": "30%"
}
```

---

### Phase 3: Feature Analysis (Read 5-10 files per feature)

**Goal:** Understand one feature at a time

**Strategy:**
```
For each feature (starting with highest priority):
1. Read entry point (page/component)
2. Trace dependencies (hooks, utils, API)
3. Read tests
4. Document understanding
5. Clear context (move to cache)
6. Move to next feature
```

**Example: Analyzing Login Feature**
```
Iteration 1: Login Feature
├─ Read: src/pages/login.tsx (entry point)
├─ Read: src/hooks/useAuth.ts (dependency)
├─ Read: src/api/auth.ts (API)
├─ Read: src/context/AuthContext.tsx (state)
├─ Read: tests/login.test.tsx (validation)
└─ Document in cache

Context used: 45%
Clear context, save to cache
Context used: 5% (only cache remains)

Iteration 2: Product Catalog
├─ Read: src/pages/products/index.tsx
├─ Read: src/hooks/useProducts.ts
├─ Read: src/api/products.ts
├─ Read: tests/products.test.tsx
└─ Document in cache

Context used: 45%
Clear context, save to cache
Context used: 5%
```

**Cache after analyzing Login:**
```json
{
  "features": {
    "authentication": {
      "status": "analyzed",
      "entry_point": "src/pages/login.tsx",
      "files": [
        "src/pages/login.tsx",
        "src/hooks/useAuth.ts",
        "src/api/auth.ts",
        "src/context/AuthContext.tsx"
      ],
      "flow": [
        "User enters credentials",
        "Form validates input",
        "useAuth.login() called",
        "API POST /auth/login",
        "Token stored in localStorage",
        "AuthContext updated",
        "Redirect to dashboard"
      ],
      "business_logic": {
        "validation": ["email format", "password 8+ chars"],
        "error_handling": ["invalid credentials", "network error"],
        "success_criteria": ["token received", "user object returned"]
      },
      "tests": {
        "file": "tests/login.test.tsx",
        "count": 8,
        "coverage": "95%"
      },
      "teaching_value": 10,
      "lesson_created": false
    }
  },
  "files_read": 20,
  "context_used": "5%"
}
```

---

### Phase 4: Lesson Generation (Use cached knowledge)

**Goal:** Create lessons from cached feature knowledge

**Strategy:**
```
For each analyzed feature:
1. Load from cache
2. Generate lesson outline
3. Create exercises
4. Write tests
5. Save lesson
6. Mark as complete in cache
```

**No need to re-read files!** Everything is in cache.

---

## The Minimal Cache Structure

### cache.json
```json
{
  "metadata": {
    "project_name": "E-commerce Platform",
    "analyzed_at": "2024-01-01T10:00:00Z",
    "total_files": 235,
    "files_analyzed": 45,
    "progress": "60%"
  },
  
  "structure": {
    "framework": "Next.js 14",
    "language": "TypeScript",
    "database": "PostgreSQL",
    "architecture": "Pages Router",
    "directories": {
      "src/pages": "Routes",
      "src/components": "UI Components",
      "src/hooks": "Custom Hooks",
      "src/api": "API Routes",
      "src/utils": "Utilities"
    }
  },
  
  "features": {
    "authentication": {
      "status": "analyzed",
      "priority": "high",
      "complexity": "medium",
      "files": [...],
      "flow": [...],
      "business_logic": {...},
      "tests": {...},
      "teaching_value": 10,
      "lesson_status": "created"
    },
    "product_catalog": {
      "status": "analyzed",
      "priority": "high",
      "complexity": "medium",
      "files": [...],
      "flow": [...],
      "business_logic": {...},
      "tests": {...},
      "teaching_value": 9,
      "lesson_status": "in_progress"
    },
    "shopping_cart": {
      "status": "pending",
      "priority": "medium",
      "estimated_complexity": "high"
    }
  },
  
  "lessons": {
    "lesson_2_1_user_login": {
      "feature": "authentication",
      "title": "Building a Login Feature",
      "duration": "30 minutes",
      "difficulty": "intermediate",
      "status": "complete",
      "file_path": "course/lessons/2.1-user-login.md"
    }
  },
  
  "next_actions": [
    "Analyze shopping_cart feature",
    "Create lesson for product_catalog",
    "Review and test all lessons"
  ]
}
```

---

## Context Management Strategy

### Rule 1: Never Exceed 70% Context
```
If context > 70%:
  1. Save current analysis to cache
  2. Clear context
  3. Load only cache (minimal)
  4. Continue with next feature
```

### Rule 2: Read Files in Batches
```
Batch 1: Foundation (5 files)
  → Save to cache
  → Clear context
  
Batch 2: Feature 1 (5-10 files)
  → Save to cache
  → Clear context
  
Batch 3: Feature 2 (5-10 files)
  → Save to cache
  → Clear context
```

### Rule 3: Prioritize by Impact
```
High Priority (read first):
- Entry points
- Core features
- Well-tested code
- Documented code

Low Priority (read later):
- Utilities
- Helpers
- Edge cases
- Legacy code
```

---

## Practical Workflow for AI

### Session 1: Initial Discovery
```
1. listDirectory(path, depth=2)
   → Get structure
   
2. readFile('package.json')
   → Identify framework
   
3. readFile('README.md')
   → Understand project
   
4. Create cache.json
   → Save findings
   
5. Plan next session
   → List features to analyze
```

**Output:** cache.json with structure and plan

---

### Session 2: Feature Discovery
```
1. Load cache.json
   → Remember what I learned
   
2. listDirectory('src/pages')
   → Find all routes
   
3. listDirectory('src/api')
   → Find all endpoints
   
4. Update cache.json
   → Add features list
   
5. Prioritize features
   → High/medium/low
```

**Output:** cache.json with features list

---

### Session 3: Analyze Feature 1
```
1. Load cache.json
   → Get feature list
   
2. Read feature files (5-10)
   → Entry point
   → Dependencies
   → Tests
   
3. Document understanding
   → Flow
   → Logic
   → Tests
   
4. Update cache.json
   → Mark feature as analyzed
   
5. Clear context
   → Keep only cache
```

**Output:** cache.json with Feature 1 analyzed

---

### Session 4: Analyze Feature 2
```
1. Load cache.json
   → Remember Feature 1
   
2. Read Feature 2 files
   → Same process
   
3. Update cache.json
   → Mark Feature 2 as analyzed
   
4. Clear context
```

**Output:** cache.json with Features 1-2 analyzed

---

### Session 5: Generate Lessons
```
1. Load cache.json
   → Get all analyzed features
   
2. For each feature:
   → Generate lesson outline
   → Create exercises
   → Write tests
   
3. Update cache.json
   → Mark lessons as created
```

**Output:** Complete course + cache.json

---

## The Cache File Format

### Minimal Version (Always Keep in Context)
```json
{
  "project": "E-commerce Platform",
  "framework": "Next.js",
  "features_analyzed": 5,
  "features_pending": 3,
  "current_phase": "lesson_generation",
  "next_action": "Create lesson for shopping_cart"
}
```

### Full Version (Load when needed)
```json
{
  "metadata": {...},
  "structure": {...},
  "features": {
    "feature_1": {...},
    "feature_2": {...}
  },
  "lessons": {...},
  "next_actions": [...]
}
```

---

## Tools I Need

### Tool 1: Smart Directory Scanner
```typescript
scanDirectory(path: string, options: {
  depth: number,
  includeFileCount: boolean,
  inferPurpose: boolean
}): DirectoryStructure

// Returns:
{
  path: "src/",
  files: 150,
  subdirectories: [
    { name: "components", files: 45, purpose: "UI Components" },
    { name: "hooks", files: 12, purpose: "Custom Hooks" },
    { name: "pages", files: 20, purpose: "Routes" }
  ]
}
```

### Tool 2: Cache Manager
```typescript
saveToCache(key: string, data: any): void
loadFromCache(key: string): any
clearContext(): void  // Keep only cache
getContextUsage(): number  // % of context used
```

### Tool 3: Progressive File Reader
```typescript
readFilesInBatch(files: string[], batchSize: number): {
  batch: FileContent[],
  remaining: string[],
  contextUsage: number
}

// Automatically stops if context > 70%
```

---

## Example: Complete Discovery Session

### Step 1: Initial Scan
```typescript
// AI: Let me start by understanding the structure
const structure = await listDirectory('.', { depth: 2 });

// AI: I see this is a Next.js project with ~200 files
// Let me save this to cache
await saveToCache('structure', structure);

// Context used: 5%
```

### Step 2: Read Foundation
```typescript
// AI: Now let me read the key files
const foundation = await readFilesInBatch([
  'package.json',
  'README.md',
  'src/pages/_app.tsx',
  'next.config.js'
], 5);

// AI: I understand the framework and dependencies
await saveToCache('foundation', foundation);

// Context used: 20%
```

### Step 3: Discover Features
```typescript
// AI: Let me scan for features
const pages = await listDirectory('src/pages', { depth: 1 });
const api = await listDirectory('src/api', { depth: 1 });

// AI: I found 8 features
const features = inferFeaturesFromStructure(pages, api);
await saveToCache('features', features);

// Context used: 30%
```

### Step 4: Analyze Feature 1
```typescript
// AI: Let me analyze the login feature
const loginFiles = await readFilesInBatch([
  'src/pages/login.tsx',
  'src/hooks/useAuth.ts',
  'src/api/auth.ts',
  'tests/login.test.tsx'
], 5);

// AI: I understand how login works
const loginAnalysis = analyzeFeature(loginFiles);
await saveToCache('features.login', loginAnalysis);

// Context used: 60%
// AI: Getting close to limit, let me clear context
await clearContext();  // Keep only cache

// Context used: 5%
```

### Step 5: Continue with Feature 2
```typescript
// AI: Load cache to remember what I learned
const cache = await loadFromCache('all');

// AI: Now analyze shopping cart
const cartFiles = await readFilesInBatch([
  'src/pages/cart.tsx',
  'src/hooks/useCart.ts',
  'src/api/cart.ts'
], 5);

// ... repeat process
```

---

## Summary: The Missing First Step

### What I Should Do FIRST:

1. **List directory structure** (depth 2-3)
   - Understand organization
   - Count files
   - Identify major sections

2. **Create initial cache**
   - Save structure
   - Plan discovery
   - Track progress

3. **Read foundation files** (5-10 files)
   - package.json
   - README.md
   - Main entry point
   - Config files

4. **Discover features** (scan, don't read)
   - List all pages/routes
   - List all API endpoints
   - List all components
   - Infer features from names

5. **Analyze progressively** (one feature at a time)
   - Read 5-10 files per feature
   - Document in cache
   - Clear context
   - Move to next feature

6. **Generate lessons** (from cache)
   - Load cached knowledge
   - Create lessons
   - No need to re-read files

### Key Principles:

✅ **Progressive:** Learn incrementally, not all at once
✅ **Cached:** Save what I learn, don't forget
✅ **Prioritized:** Important things first
✅ **Bounded:** Stay within context limits
✅ **Efficient:** Read each file only once

**This is the missing foundation that makes everything else possible!**
