# Feature-to-Lesson Mapping: Teaching Every Feature & Logic

## The Core Insight

**For junior developers: Every feature = A topic to teach**

Not just "how to use React hooks" but:
- "How the login feature works"
- "How the shopping cart calculates totals"
- "How the search filters products"
- "How the notification system sends alerts"

## Critical Questions to Investigate

### Category 1: Feature Discovery

#### Q1.1: How do we identify all features in a codebase?
**Sub-questions:**
- What constitutes a "feature"?
- How do we distinguish features from infrastructure?
- How do we find user-facing vs internal features?
- How do we map code to features?
- How do we prioritize which features to teach?

**Investigation approach:**
```
1. Read user-facing code (UI components, API endpoints)
2. Check routes/navigation (what pages exist?)
3. Review tests (what behaviors are tested?)
4. Analyze git history (what features were added?)
5. Check documentation (what features are documented?)
6. Look at database schema (what entities exist?)
```

**Evidence needed:**
- [ ] List of all routes/pages
- [ ] List of all API endpoints
- [ ] List of all database tables
- [ ] List of all major components
- [ ] Git commits grouped by feature
- [ ] User stories/requirements (if available)

---

#### Q1.2: How do we map features to code?
**Sub-questions:**
- Which files implement this feature?
- What's the entry point for this feature?
- What's the data flow for this feature?
- What dependencies does this feature have?
- What tests validate this feature?

**Investigation approach:**
```
For each feature:
1. Find the UI entry point (button, page, component)
2. Trace the code flow (what happens when user clicks?)
3. Identify all involved files
4. Map the data flow (input → processing → output)
5. Find related tests
6. Document dependencies
```

**Example: Login Feature**
```
Entry point: LoginForm.tsx
    ↓
Calls: handleLogin() function
    ↓
Uses: useAuth() hook
    ↓
Calls: POST /api/auth/login
    ↓
Updates: User context
    ↓
Redirects: to /dashboard
    ↓
Tests: login.test.ts (8 tests)
```

---

#### Q1.3: How do we understand the business logic?
**Sub-questions:**
- What problem does this feature solve?
- What are the business rules?
- What are the edge cases?
- What validations are required?
- What are the success/failure scenarios?

**Investigation approach:**
```
1. Read the code implementation
2. Check validation logic
3. Review error handling
4. Analyze conditional logic
5. Study test cases (they reveal business rules!)
6. Check comments for "why" explanations
```

**Evidence needed:**
- [ ] Business rules extracted from code
- [ ] Validation rules documented
- [ ] Edge cases identified
- [ ] Error scenarios mapped
- [ ] Success criteria defined

---

### Category 2: Logic Extraction

#### Q2.1: How do we break down complex logic into teachable chunks?
**Sub-questions:**
- What's the simplest version of this logic?
- What are the building blocks?
- What can be learned independently?
- What must be learned in sequence?
- How do we scaffold complexity?

**Investigation approach:**
```
For complex logic:
1. Identify the core algorithm/pattern
2. Strip away edge cases (teach separately)
3. Remove optimizations (teach separately)
4. Extract the essence
5. Build up complexity progressively
```

**Example: Shopping Cart Total Calculation**
```
Level 1 (Beginner): Sum of item prices
Level 2 (Intermediate): Apply discounts
Level 3 (Advanced): Handle tax, shipping, coupons
Level 4 (Expert): Optimize for performance
```

---

#### Q2.2: How do we explain "why" the logic exists?
**Sub-questions:**
- What problem does this solve?
- Why this approach vs alternatives?
- What are the trade-offs?
- What would break without this logic?
- What's the business context?

**Investigation approach:**
```
1. Read git commit messages (why was this added?)
2. Check PR descriptions (what problem did it solve?)
3. Look for comments explaining "why"
4. Analyze what breaks if removed
5. Compare with alternative approaches
6. Understand business requirements
```

**Evidence needed:**
- [ ] Git commit explaining why
- [ ] PR description with context
- [ ] Comments explaining rationale
- [ ] Tests showing what would break
- [ ] Business requirement documented

---

#### Q2.3: How do we teach logic patterns vs specific implementations?
**Sub-questions:**
- What's reusable knowledge vs project-specific?
- What's a pattern vs a one-off?
- What's a best practice vs a workaround?
- What's fundamental vs advanced?
- What's universal vs framework-specific?

**Investigation approach:**
```
For each piece of logic:
1. Identify the underlying pattern
2. Separate pattern from implementation
3. Find similar patterns elsewhere in codebase
4. Determine if it's a known design pattern
5. Assess reusability
```

**Example: Form Validation**
```
Pattern: Input validation (universal)
Implementation: Using Zod schema (framework-specific)
Reusability: High (every form needs validation)
Teaching approach: Teach pattern first, then implementation
```

---

### Category 3: Course Structure from Features

#### Q3.1: How do we organize features into a learning path?
**Sub-questions:**
- What features should be taught first?
- What's the dependency graph of features?
- What builds confidence quickly?
- What's essential vs optional?
- How do we group related features?

**Investigation approach:**
```
1. Map feature dependencies
   - Feature A requires Feature B
   - Feature C is independent
   
2. Assess complexity
   - Simple features first
   - Complex features later
   
3. Consider user journey
   - What do users do first?
   - What's the critical path?
   
4. Group by domain
   - All auth features together
   - All payment features together
```

**Example Structure:**
```
Module 1: Core Features (Must Know)
  - User Registration
  - User Login
  - Profile Management

Module 2: Main Features (Should Know)
  - Product Browsing
  - Shopping Cart
  - Checkout

Module 3: Advanced Features (Nice to Know)
  - Wishlist
  - Reviews
  - Recommendations
```

---

#### Q3.2: How do we map features to lessons?
**Sub-questions:**
- One feature = one lesson?
- Or one feature = multiple lessons?
- How do we handle feature complexity?
- How do we handle feature dependencies?
- How do we estimate lesson time?

**Investigation approach:**
```
For each feature:
1. Assess complexity (lines of code, logic branches)
2. Count sub-features
3. Identify teachable concepts
4. Estimate learning time
5. Decide on lesson structure

Decision matrix:
- Simple feature (< 100 LOC) = 1 lesson (30 min)
- Medium feature (100-300 LOC) = 2-3 lessons (45 min each)
- Complex feature (> 300 LOC) = Module (multiple lessons)
```

**Example: Authentication Feature**
```
Feature: Authentication (Complex)
    ↓
Module: Authentication System
    ├─ Lesson 1: User Registration (30 min)
    ├─ Lesson 2: User Login (30 min)
    ├─ Lesson 3: Password Reset (45 min)
    ├─ Lesson 4: Session Management (45 min)
    └─ Project: Build Auth System (2 hours)
```

---

#### Q3.3: How do we create hands-on exercises from features?
**Sub-questions:**
- How do we turn a feature into an exercise?
- What's the right level of scaffolding?
- How do we validate the exercise?
- How do we provide helpful feedback?
- How do we handle different skill levels?

**Investigation approach:**
```
For each feature:
1. Extract the core functionality
2. Create a simplified version
3. Provide starter code
4. Define clear requirements
5. Write automated tests
6. Create progressive hints

Exercise types:
- Build from scratch (advanced)
- Fill in the blanks (intermediate)
- Fix the bugs (beginner)
- Extend existing (all levels)
```

---

### Category 4: Reading the Codebase Systematically

#### Q4.1: What's the systematic process for reading a feature?
**Sub-questions:**
- Where do we start reading?
- What order do we read files?
- How do we trace the flow?
- How do we understand the data?
- How do we verify our understanding?

**Investigation approach:**
```
Step-by-step process:
1. Identify the feature entry point
   - UI component, API endpoint, CLI command
   
2. Read the entry point file
   - Understand the interface
   - Note the inputs/outputs
   
3. Trace the execution flow
   - Follow function calls
   - Track data transformations
   
4. Read supporting files
   - Utilities, helpers, services
   
5. Check the tests
   - Understand expected behavior
   
6. Review related files
   - Types, constants, configs
   
7. Verify understanding
   - Can you explain it to someone?
   - Can you modify it?
```

---

#### Q4.2: How do we document our understanding?
**Sub-questions:**
- What format captures feature knowledge?
- How do we document the flow?
- How do we explain the logic?
- How do we cite evidence?
- How do we make it teachable?

**Investigation approach:**
```
For each feature, create:
1. Feature Overview
   - What it does
   - Why it exists
   - Who uses it
   
2. Technical Flow
   - Entry point
   - Data flow diagram
   - Key functions
   - Dependencies
   
3. Business Logic
   - Rules and validations
   - Edge cases
   - Error handling
   
4. Code Evidence
   - File paths
   - Line numbers
   - Test references
   
5. Teaching Notes
   - Key concepts
   - Prerequisites
   - Common pitfalls
```

---

#### Q4.3: How do we keep feature documentation in sync with code?
**Sub-questions:**
- What happens when code changes?
- How do we detect outdated lessons?
- How do we update efficiently?
- How do we version lessons?
- How do we notify students?

**Investigation approach:**
```
1. Link lessons to code versions
   - Git commit hash
   - Semantic version
   
2. Automated change detection
   - Watch for file changes
   - Detect breaking changes
   
3. Update workflow
   - Review changes
   - Update lessons
   - Re-test exercises
   
4. Version management
   - Lesson v1.0 → Code v1.0
   - Lesson v1.1 → Code v1.1
   
5. Student notification
   - "This lesson was updated"
   - "New features added"
```

---

### Category 5: Generating Course Content from Features

#### Q5.1: How do we auto-generate lesson outlines from features?
**Sub-questions:**
- Can we extract lesson structure from code?
- Can we identify key concepts automatically?
- Can we generate exercises from tests?
- Can we create explanations from comments?
- How much manual work is needed?

**Investigation approach:**
```
Automated extraction:
1. Feature name → Lesson title
2. Function names → Learning objectives
3. Test descriptions → Exercise requirements
4. Comments → Explanations
5. Type definitions → Concept definitions

Manual refinement:
1. Add context and "why"
2. Simplify language
3. Add examples
4. Create progressive exercises
5. Write helpful hints
```

---

#### Q5.2: How do we ensure every feature is covered?
**Sub-questions:**
- How do we track feature coverage?
- How do we identify gaps?
- How do we prioritize missing features?
- How do we validate completeness?
- How do we measure coverage?

**Investigation approach:**
```
Coverage tracking:
1. List all features (from code analysis)
2. List all lessons (from course outline)
3. Map features to lessons
4. Identify uncovered features
5. Prioritize by importance

Metrics:
- Feature coverage: X% of features taught
- Code coverage: X% of codebase explained
- Concept coverage: X% of patterns taught
```

---

## The Complete Feature-to-Lesson System

### Phase 1: Feature Discovery

```
Codebase
    ↓
[Scan for Features]
    ├─ Routes/Pages
    ├─ API Endpoints
    ├─ Database Tables
    ├─ Major Components
    └─ Git History
    ↓
Feature List
```

**Tools needed:**
- Route scanner
- API endpoint detector
- Database schema analyzer
- Component tree builder
- Git history analyzer

---

### Phase 2: Feature Analysis

```
Feature List
    ↓
For each feature:
    ├─ [Map to Code Files]
    ├─ [Trace Execution Flow]
    ├─ [Extract Business Logic]
    ├─ [Identify Dependencies]
    └─ [Find Tests]
    ↓
Feature Documentation
```

**Output format:**
```yaml
feature:
  name: "User Login"
  description: "Allows users to authenticate"
  entry_point: "src/components/LoginForm.tsx"
  files:
    - "src/components/LoginForm.tsx"
    - "src/hooks/useAuth.ts"
    - "src/api/auth.ts"
  flow:
    - "User enters credentials"
    - "Form validates input"
    - "API call to /auth/login"
    - "Store token in localStorage"
    - "Update user context"
    - "Redirect to dashboard"
  business_logic:
    - "Email must be valid format"
    - "Password must be 8+ characters"
    - "Max 5 login attempts"
    - "Lock account after 5 failures"
  tests:
    - "src/components/LoginForm.test.tsx"
    - "src/hooks/useAuth.test.ts"
  dependencies:
    - "Authentication context"
    - "API client"
    - "Form validation library"
```

---

### Phase 3: Logic Extraction

```
Feature Documentation
    ↓
For each feature:
    ├─ [Identify Core Logic]
    ├─ [Break Down Complexity]
    ├─ [Extract Patterns]
    ├─ [Find Reusable Concepts]
    └─ [Assess Teaching Value]
    ↓
Teachable Concepts
```

**Example extraction:**
```
Feature: Shopping Cart
    ↓
Core Logic:
    - Add item to cart
    - Remove item from cart
    - Update quantity
    - Calculate total
    ↓
Patterns:
    - State management (useState/Redux)
    - Array manipulation (map, filter, reduce)
    - Immutable updates
    - Derived state (total from items)
    ↓
Reusable Concepts:
    - Managing collections
    - Calculating aggregates
    - Handling user actions
    - Optimistic updates
    ↓
Teaching Value: 9/10 (High)
```

---

### Phase 4: Course Structure Generation

```
Teachable Concepts
    ↓
[Group by Domain]
    ├─ Authentication
    ├─ E-commerce
    ├─ User Management
    └─ Admin Features
    ↓
[Order by Dependency]
    ├─ Foundation (no dependencies)
    ├─ Core (depends on foundation)
    └─ Advanced (depends on core)
    ↓
[Map to Lessons]
    ├─ Simple feature = 1 lesson
    ├─ Medium feature = 2-3 lessons
    └─ Complex feature = 1 module
    ↓
Course Outline
```

**Example structure:**
```
Course: E-commerce Platform

Module 1: Foundation (Week 1)
  Lesson 1.1: Project Setup (30 min)
  Lesson 1.2: Understanding the Architecture (45 min)
  Lesson 1.3: Database Schema (30 min)

Module 2: Authentication (Week 2)
  Lesson 2.1: User Registration (30 min)
    Feature: User signup
    Logic: Form validation, password hashing, email verification
    Exercise: Build registration form
    
  Lesson 2.2: User Login (30 min)
    Feature: User authentication
    Logic: Credential validation, JWT generation, session management
    Exercise: Implement login flow
    
  Lesson 2.3: Password Reset (45 min)
    Feature: Password recovery
    Logic: Token generation, email sending, password update
    Exercise: Build password reset feature

Module 3: Product Catalog (Week 3)
  Lesson 3.1: Product Listing (45 min)
    Feature: Browse products
    Logic: Pagination, filtering, sorting
    Exercise: Build product list with filters
    
  Lesson 3.2: Product Details (30 min)
    Feature: View product
    Logic: Fetch product data, display images, show reviews
    Exercise: Create product detail page
    
  Lesson 3.3: Product Search (45 min)
    Feature: Search products
    Logic: Full-text search, autocomplete, search history
    Exercise: Implement search functionality

Module 4: Shopping Cart (Week 4)
  Lesson 4.1: Cart Management (45 min)
    Feature: Add/remove items
    Logic: State management, local storage, quantity updates
    Exercise: Build shopping cart
    
  Lesson 4.2: Cart Calculations (30 min)
    Feature: Calculate totals
    Logic: Subtotal, tax, shipping, discounts
    Exercise: Implement price calculations
    
  Lesson 4.3: Checkout Process (60 min)
    Feature: Complete purchase
    Logic: Payment integration, order creation, inventory update
    Exercise: Build checkout flow

Module 5: Advanced Features (Week 5)
  Lesson 5.1: Wishlist (30 min)
  Lesson 5.2: Product Reviews (45 min)
  Lesson 5.3: Recommendations (60 min)
```

---

### Phase 5: Content Generation

```
Course Outline
    ↓
For each lesson:
    ├─ [Write Explanation]
    │   ├─ What the feature does
    │   ├─ Why it exists
    │   ├─ How it works
    │   └─ Key concepts
    │
    ├─ [Create Example]
    │   ├─ Extract from codebase
    │   ├─ Simplify if needed
    │   ├─ Add comments
    │   └─ Test it works
    │
    ├─ [Design Exercise]
    │   ├─ Define requirements
    │   ├─ Provide starter code
    │   ├─ Create solution
    │   └─ Write tests
    │
    └─ [Add Support]
        ├─ Prerequisites
        ├─ Hints
        ├─ Resources
        └─ Common pitfalls
    ↓
Complete Lesson Content
```

---

## Practical Example: Login Feature → Lesson

### Step 1: Discover the Feature

```bash
# Find login-related files
grep -r "login" src/
grep -r "auth" src/
find src/ -name "*Login*"
find src/ -name "*Auth*"

# Check routes
cat src/routes.tsx | grep login

# Check API endpoints
cat src/api/endpoints.ts | grep auth

# Check tests
find src/ -name "*login*.test.*"
```

**Found:**
- `src/components/LoginForm.tsx` (UI)
- `src/hooks/useAuth.ts` (Logic)
- `src/api/auth.ts` (API)
- `src/context/AuthContext.tsx` (State)
- `src/components/LoginForm.test.tsx` (Tests)

---

### Step 2: Analyze the Feature

```typescript
// Read LoginForm.tsx
const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    await login(email, password);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <button type="submit">Login</button>
    </form>
  );
};

// Read useAuth.ts
const useAuth = () => {
  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('token', response.data.token);
    setUser(response.data.user);
    navigate('/dashboard');
  };
  
  return { login };
};

// Read tests
test('login with valid credentials', async () => {
  const { result } = renderHook(() => useAuth());
  await result.current.login('test@example.com', 'password123');
  expect(localStorage.getItem('token')).toBeTruthy();
});
```

**Analysis:**
- Entry point: LoginForm component
- Flow: Form → useAuth hook → API call → Store token → Navigate
- Business logic: Email/password validation, token storage
- Dependencies: useAuth hook, API client, navigation
- Tests: 8 tests covering success/failure scenarios

---

### Step 3: Extract Teachable Concepts

```
Core Concepts:
1. Form handling in React
2. Custom hooks for logic separation
3. API integration
4. Local storage for persistence
5. Context for global state
6. Navigation after success

Patterns:
1. Controlled components (form inputs)
2. Custom hooks (useAuth)
3. Async/await for API calls
4. Error handling
5. Loading states

Teaching Value: 10/10
- Reusability: 3/3 (universal pattern)
- Best Practice: 3/3 (React best practice)
- Fundamentality: 3/3 (essential for any app)
- Uniqueness: 1/2 (common but well-implemented)
- Junior Dev: 3/3 (must know)
```

---

### Step 4: Create Lesson Structure

```markdown
# Lesson: Building a Login Feature

## Prerequisites
- React basics
- useState hook
- Forms in React
- Async/await

## Learning Objectives
By the end of this lesson, you will:
1. Build a login form with controlled inputs
2. Create a custom authentication hook
3. Integrate with a backend API
4. Handle authentication state
5. Implement error handling

## Time Estimate
45 minutes

## Part 1: Understanding the Feature (10 minutes)

### What is Login?
Login allows users to authenticate and access protected features.

### Why Do We Need It?
- Verify user identity
- Protect sensitive data
- Personalize user experience
- Track user actions

### How Does It Work?
1. User enters credentials
2. Frontend validates input
3. API verifies credentials
4. Server returns token
5. Frontend stores token
6. User is redirected

**Evidence:** See `src/components/LoginForm.tsx` (lines 1-30)

## Part 2: The Code (10 minutes)

### The Login Form Component
```typescript
// Actual code from codebase
const LoginForm = () => {
  // ... (show actual implementation)
};
```

**Key concepts:**
- Controlled components (line 5-6)
- Event handling (line 8)
- Form submission (line 10)

### The Authentication Hook
```typescript
// Actual code from codebase
const useAuth = () => {
  // ... (show actual implementation)
};
```

**Key concepts:**
- Custom hooks (line 1)
- API calls (line 5)
- State management (line 7)

## Part 3: Exercise (20 minutes)

### Your Task
Build a login feature that:
1. Has email and password inputs
2. Validates input before submission
3. Calls the login API
4. Stores the token
5. Redirects on success
6. Shows errors on failure

### Starter Code
```typescript
const LoginForm = () => {
  // TODO: Add state for email and password
  // TODO: Add handleSubmit function
  // TODO: Add form JSX
};
```

### Requirements
- Email must be valid format
- Password must be 8+ characters
- Show loading state during API call
- Display error messages
- Redirect to /dashboard on success

### Tests
Your implementation should pass these tests:
```typescript
// Actual tests from codebase
test('submits form with valid credentials', async () => {
  // ...
});

test('shows error with invalid credentials', async () => {
  // ...
});
```

## Part 4: Solution & Explanation (5 minutes)

### Solution
```typescript
// Complete solution with explanations
const LoginForm = () => {
  // State management
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Custom hook for auth logic
  const { login } = useAuth();
  
  // Form submission handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      await login(email, password);
      // Redirect happens in useAuth
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <input 
        type="email" 
        value={email} 
        onChange={e => setEmail(e.target.value)}
        required
      />
      <input 
        type="password" 
        value={password} 
        onChange={e => setPassword(e.target.value)}
        minLength={8}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

### Key Takeaways
1. Separate UI from logic (component vs hook)
2. Handle loading and error states
3. Use controlled components for forms
4. Validate input before submission
5. Provide user feedback

## Resources
- [React Forms Documentation](https://react.dev/reference/react-dom/components/form)
- [Custom Hooks Guide](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [Codebase: LoginForm.tsx](src/components/LoginForm.tsx)
- [Codebase: useAuth.ts](src/hooks/useAuth.ts)

## Next Lesson
Lesson 2.3: Password Reset
```

---

## Summary: The Complete System

### Input: Codebase with Features
### Output: Structured Course with Lessons

### Process:
1. **Discover** all features systematically
2. **Analyze** each feature's code and logic
3. **Extract** teachable concepts and patterns
4. **Structure** into logical learning path
5. **Generate** lesson content with evidence
6. **Create** exercises from features
7. **Validate** with tests and beta users

### Key Principles:
- Every feature is a teaching opportunity
- Every piece of logic has a lesson
- Always cite evidence from code
- Map features to real user needs
- Build progressively from simple to complex
- Provide hands-on practice for every concept

### Tools Needed:
1. Feature scanner (routes, endpoints, components)
2. Code flow tracer (execution path)
3. Logic extractor (business rules)
4. Dependency mapper (what depends on what)
5. Test analyzer (what's validated)
6. Lesson generator (auto-create outlines)

**This ensures every feature in the codebase becomes a lesson in the course!**
