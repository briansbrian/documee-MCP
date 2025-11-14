# AI Content Enrichment System

## Overview

The AI Content Enrichment system transforms basic course structures into comprehensive, evidence-based educational materials by leveraging Kiro (the AI assistant) to generate rich explanations, narratives, and exercises. Instead of building LLM integration directly into the Python codebase, this system provides MCP tools that enable Kiro to read course structures, analyze code with full context, and write enriched content back to the course files.

**Key Design Principle**: The MCP server generates basic course structure with placeholders, and Kiro enriches the content by reading code, understanding context through systematic investigation, and writing educational narratives grounded in evidence.

## Why This Approach?

### Advantages
- **Simplicity**: No need to integrate OpenAI/Anthropic SDKs into Python codebase
- **Flexibility**: Kiro can adapt enrichment style based on conversation context
- **Cost-Effective**: No additional API costs beyond existing Kiro usage
- **Iterative**: Easy to refine enrichment quality through steering files
- **Context-Aware**: Kiro has full access to codebase and can read any related files
- **Evidence-Based**: Systematic investigation ensures all content is grounded in actual code, tests, and documentation

### Core Principles

1. **Evidence-Based Content**: Every claim must reference actual code, tests, commits, or documentation
2. **Beginner-Friendly**: Use simple language, build progressively, provide context
3. **Systematic Investigation**: Answer what, why, how, when, edge cases, and pitfalls with evidence
4. **Anti-Hallucination**: Require citations, validate against tests, cross-reference sources

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Course Generator Tools                       │  │
│  │  - scan_codebase                                     │  │
│  │  - analyze_file                                      │  │
│  │  - export_course (generates basic structure)        │  │
│  │  - get_enrichment_guide (NEW)                       │  │
│  │  - update_lesson_content (NEW)                      │  │
│  │  - list_lessons_for_enrichment (NEW)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ MCP Protocol
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Kiro (AI Assistant)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Content Enrichment Workflow                  │  │
│  │  1. Call export_course to generate basic structure  │  │
│  │  2. For each lesson:                                 │  │
│  │     - Call get_enrichment_guide                      │  │
│  │     - Review evidence bundle (code, tests, commits)  │  │
│  │     - Validate understanding across sources          │  │
│  │     - Generate rich explanations with citations      │  │
│  │     - Write learning narratives                      │  │
│  │     - Create detailed exercises with hints           │  │
│  │     - Call update_lesson_content with enriched data  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## MCP Tools

### 1. get_enrichment_guide

Generates a comprehensive, evidence-based enrichment guide for AI assistants to use when creating educational content.

**Signature:**
```python
@mcp.tool()
async def get_enrichment_guide(
    codebase_id: str,
    lesson_id: str
) -> Dict[str, Any]
```

**Parameters:**
- `codebase_id`: Codebase identifier from scan_codebase
- `lesson_id`: Lesson identifier (e.g., "module-1-lesson-1")

**Returns:** Comprehensive enrichment guide containing:

#### 1. Feature Mapping
Maps code to user-facing functionality:
- `feature_name`: Name of the feature this lesson teaches
- `user_facing_purpose`: What users do with this feature
- `business_value`: Why this feature exists
- `entry_points`: Where users/code interact with this feature
- `feature_flow`: Step-by-step user/data flow


#### 2. Evidence Bundle
Collection of evidence for validation:
- `source_files`: List of files with line ranges and code
- `test_files`: Tests that validate behavior
- `git_commits`: Relevant commits explaining "why"
- `documentation`: Inline comments, JSDoc, README sections
- `dependencies`: What this depends on (with evidence)
- `dependents`: What depends on this (with evidence)

#### 3. Validation Checklist
Validates understanding against multiple sources:
- `code_behavior`: What the code actually does (cite tests)
- `expected_behavior`: What tests expect (cite test descriptions)
- `documentation_alignment`: What docs say (cite comments)
- `git_context`: Why it was built (cite commits)
- `consistency_check`: Cross-file validation results

#### 4. Teaching Value Assessment
Scores teaching value (0-14 scale):
- `reusability_score`: 0-3 (is this pattern reusable?)
- `best_practice_score`: 0-3 (is this a best practice?)
- `fundamentality_score`: 0-3 (is this fundamental?)
- `uniqueness_score`: 0-2 (is this unique/interesting?)
- `junior_dev_score`: 0-3 (valuable for junior devs?)
- `total_score`: 0-14 (teach if > 7)
- `reasoning`: Why these scores

#### 5. Systematic Investigation
Answers key questions with evidence:
- `what_it_does`: Factual description (cite code)
- `why_it_exists`: Business/technical reason (cite commits/docs)
- `how_it_works`: Technical implementation (cite code sections)
- `when_its_used`: Usage scenarios (cite call sites)
- `edge_cases`: Special handling (cite tests)
- `common_pitfalls`: Known issues (cite comments/tests)

#### 6. Narrative Structure
Guides lesson organization:
- `introduction_points`: Context and motivation
- `learning_progression`: Ordered concepts (simple → complex)
- `code_walkthrough_order`: Which code to explain when
- `conclusion_points`: Key takeaways
- `next_steps`: What to learn next


#### 7. Code Sections
List of code sections with comprehensive evidence. Each section includes:
- `file_path`: Source file
- `line_range`: [start, end]
- `code_snippet`: Actual code
- `purpose`: What it does (cite tests)
- `key_concepts`: Concepts demonstrated
- `explanation_approach`: How to explain (simple → complex)
- `related_code`: Links to related sections (with context)
- `test_evidence`: Tests that validate this code
- `git_evidence`: Commits that explain why
- `common_mistakes`: Pitfalls to highlight

#### 8. Architecture Context
Shows how code fits in the system:
- `component_role`: Role in system (cite dependency graph)
- `data_flow`: How data moves (cite code)
- `interaction_diagram`: Mermaid diagram
- `dependencies`: What it needs (cite imports)
- `dependents`: What needs it (cite usage)
- `design_patterns`: Patterns used (cite evidence)

#### 9. Real-World Context
Practical applications and analogies:
- `practical_use_cases`: Real scenarios
- `analogies`: Beginner-friendly comparisons
- `industry_patterns`: Standard approaches
- `best_practices`: What to emphasize
- `anti_patterns`: What to avoid

#### 10. Exercise Generation
Hands-on practice from actual codebase:
- `hands_on_tasks`: Progressive exercises
- `starter_code`: Template to complete
- `solution_code`: Complete solution (from codebase)
- `test_cases`: Validation tests (from codebase)
- `progressive_hints`: 3-5 hints (general → specific)
- `self_assessment`: Questions to check understanding

#### 11. Anti-Hallucination Rules
Guidelines to prevent hallucination:
- `always_cite`: "Never explain without citing evidence"
- `distinguish_fact_inference`: "Mark inferences clearly"
- `validate_against_tests`: "Check tests before explaining"
- `cross_reference`: "Verify across multiple files"
- `avoid_assumptions`: "Don't guess the 'why'"


#### 12. Enrichment Instructions
Specific guidance for AI:
- `tone`: "casual" (beginner-friendly)
- `depth`: "detailed" (explain thoroughly)
- `focus_areas`: What to emphasize
- `avoid_topics`: What not to mention
- `evidence_requirements`: "Cite for every claim"

**Example Usage:**
```python
# Get enrichment guide for a lesson
guide = await get_enrichment_guide(
    codebase_id="my-project-abc123",
    lesson_id="module-2-lesson-3"
)

# Guide contains all evidence and instructions
print(guide["feature_mapping"]["feature_name"])
print(guide["evidence_bundle"]["source_files"])
print(guide["systematic_investigation"]["what_it_does"])
```

### 2. update_lesson_content

Updates a lesson with enriched content generated by AI.

**Signature:**
```python
@mcp.tool()
async def update_lesson_content(
    codebase_id: str,
    lesson_id: str,
    enriched_content: Dict[str, Any]
) -> Dict[str, Any]
```

**Parameters:**
- `codebase_id`: Codebase identifier
- `lesson_id`: Lesson identifier
- `enriched_content`: Dictionary with enriched fields:
  - `description`: Rich description with context
  - `content`: Full learning narrative
  - `code_examples`: Enhanced with detailed explanations
  - `exercises`: Enhanced with hints and instructions
  - `learning_objectives`: Generated learning goals

**Returns:**
```python
{
    "success": True,
    "lesson_id": "module-2-lesson-3",
    "updated_fields": ["description", "content", "code_examples", "exercises"]
}
```


**Example Usage:**
```python
# Enrich lesson content
enriched = {
    "description": "User authentication is the foundation of secure web applications...",
    "content": "# Introduction\n\nAuthentication ensures that only authorized users...",
    "code_examples": [
        {
            "explanation": "This function validates user credentials by comparing..."
        }
    ],
    "exercises": [
        {
            "description": "Implement token validation to protect API routes",
            "instructions": "1. Create a validate_token function\n2. Decode the JWT...",
            "hints": [
                "Remember that JWTs have three parts",
                "Check the jwt library documentation",
                "The decode() function automatically checks expiration"
            ]
        }
    ],
    "learning_objectives": [
        "Generate secure JWT tokens with appropriate expiration times",
        "Validate JWT tokens and handle authentication errors gracefully"
    ]
}

result = await update_lesson_content(
    codebase_id="my-project-abc123",
    lesson_id="module-2-lesson-3",
    enriched_content=enriched
)
```

### 3. list_lessons_for_enrichment

Lists all lessons in a course with their enrichment status.

**Signature:**
```python
@mcp.tool()
async def list_lessons_for_enrichment(
    codebase_id: str
) -> List[Dict[str, Any]]
```

**Parameters:**
- `codebase_id`: Codebase identifier

**Returns:** List of lessons with:
- `lesson_id`: Unique identifier
- `title`: Lesson title
- `module`: Parent module name
- `status`: "pending", "in_progress", or "completed"
- `source_files`: Files covered in this lesson
- `teaching_value_score`: Score (0.0-1.0)
- `enriched_at`: Timestamp of last enrichment (if completed)


**Example Usage:**
```python
# List all lessons for enrichment
lessons = await list_lessons_for_enrichment(codebase_id="my-project-abc123")

# Filter by status
pending = [l for l in lessons if l["status"] == "pending"]
completed = [l for l in lessons if l["status"] == "completed"]

# Sort by teaching value
high_value = sorted(lessons, key=lambda x: x["teaching_value_score"], reverse=True)
```

## Enrichment Workflow

### Step-by-Step Process

#### 1. Generate Basic Course Structure
```python
# First, generate the basic course structure
course = await export_course(
    codebase_id="my-project-abc123",
    format="json",
    config={
        "target_audience": "beginner",
        "course_focus": "full-stack"
    }
)
```

#### 2. List Lessons for Enrichment
```python
# Get all lessons that need enrichment
lessons = await list_lessons_for_enrichment(codebase_id="my-project-abc123")

# Prioritize by teaching value
for lesson in sorted(lessons, key=lambda x: x["teaching_value_score"], reverse=True):
    if lesson["status"] == "pending":
        print(f"Next to enrich: {lesson['title']}")
```

#### 3. Get Enrichment Guide
```python
# Get comprehensive guide for a specific lesson
guide = await get_enrichment_guide(
    codebase_id="my-project-abc123",
    lesson_id="module-2-lesson-3"
)

# Review evidence
print("Feature:", guide["feature_mapping"]["feature_name"])
print("Source files:", len(guide["evidence_bundle"]["source_files"]))
print("Test files:", len(guide["evidence_bundle"]["test_files"]))
print("Teaching value:", guide["teaching_value_assessment"]["total_score"])
```


#### 4. Review Evidence and Validate Understanding
```python
# Validate understanding across sources
validation = guide["validation_checklist"]

# Check consistency
if validation["consistency_check"]:
    print("✓ All sources are consistent")
else:
    print("⚠ Sources have conflicts - investigate further")

# Review systematic investigation
investigation = guide["systematic_investigation"]
print("What it does:", investigation["what_it_does"])
print("Why it exists:", investigation["why_it_exists"])
print("How it works:", investigation["how_it_works"])
```

#### 5. Generate Enriched Content
Using the enrichment guide, create rich educational content:

```python
# Use narrative structure to organize content
narrative = guide["narrative_structure"]

# Build introduction
intro = f"""
# {lesson_title}

{narrative["introduction_points"][0]}

In this lesson, you'll learn:
{chr(10).join(f"- {obj}" for obj in learning_objectives)}
"""

# Build main content following learning progression
content = intro
for concept in narrative["learning_progression"]:
    # Explain each concept with evidence
    content += explain_concept_with_evidence(concept, guide)

# Add code walkthroughs
for section in guide["code_sections"]:
    content += create_code_walkthrough(section)

# Add conclusion
content += f"""
## Summary

{chr(10).join(narrative["conclusion_points"])}

## Next Steps

{chr(10).join(narrative["next_steps"])}
"""
```


#### 6. Enhance Code Examples
```python
# Enhance each code example with detailed explanations
enriched_examples = []
for section in guide["code_sections"]:
    enriched_examples.append({
        "code": section["code_snippet"],
        "language": "python",
        "file_path": section["file_path"],
        "line_start": section["line_range"][0],
        "line_end": section["line_range"][1],
        "explanation": f"""
**Purpose**: {section["purpose"]}

**Key Concepts**: {", ".join(section["key_concepts"])}

**Detailed Explanation**:
{create_line_by_line_explanation(section)}

**Why This Matters**: {explain_real_world_relevance(section)}

**Common Mistakes**:
{chr(10).join(f"- {mistake}" for mistake in section["common_mistakes"])}

**Related Code**: See {", ".join(section["related_code"])}
"""
    })
```

#### 7. Create Enhanced Exercises
```python
# Generate exercises with progressive hints
enriched_exercises = []
for task in guide["exercise_generation"]["hands_on_tasks"]:
    enriched_exercises.append({
        "title": task["title"],
        "description": task["description"],
        "instructions": create_numbered_instructions(task),
        "starter_code": guide["exercise_generation"]["starter_code"],
        "solution_code": guide["exercise_generation"]["solution_code"],
        "hints": guide["exercise_generation"]["progressive_hints"],
        "difficulty": task.get("difficulty", "intermediate")
    })
```

#### 8. Update Lesson Content
```python
# Package enriched content
enriched_content = {
    "description": enhanced_description,
    "content": content,
    "code_examples": enriched_examples,
    "exercises": enriched_exercises,
    "learning_objectives": learning_objectives
}

# Save enriched content
result = await update_lesson_content(
    codebase_id="my-project-abc123",
    lesson_id="module-2-lesson-3",
    enriched_content=enriched_content
)

if result["success"]:
    print(f"✓ Enriched lesson: {result['lesson_id']}")
    print(f"  Updated fields: {', '.join(result['updated_fields'])}")
```


## Evidence-Based Approach

### Core Principle
Every claim in enriched content must be grounded in evidence from actual code, tests, commits, or documentation. This prevents hallucination and ensures accuracy.

### Evidence Sources

#### 1. Source Code
- **What to extract**: Actual implementation, function signatures, class structures
- **How to cite**: File path and line numbers (e.g., "auth.py:42-58")
- **Use for**: Explaining what code does, how it works

**Example:**
```
"The login() function validates credentials by comparing the hashed password 
(line 42 in src/auth/login.py) with the stored hash from the database."
```

#### 2. Test Files
- **What to extract**: Test descriptions, expected behavior, edge cases
- **How to cite**: Test file and test name (e.g., "test_auth.py::test_invalid_password")
- **Use for**: Validating understanding, identifying edge cases

**Example:**
```
"According to test_auth.py::test_expired_token (line 67), the system correctly 
rejects tokens that have passed their expiration time."
```

#### 3. Git Commits
- **What to extract**: Commit messages, author intent, historical context
- **How to cite**: Commit hash and message (e.g., "commit abc123f: 'Add rate limiting'")
- **Use for**: Explaining why code exists, design decisions

**Example:**
```
"Rate limiting was added in commit abc123f to prevent brute force attacks, 
as noted in the commit message: 'Add rate limiting to login endpoint after 
security audit.'"
```

#### 4. Documentation
- **What to extract**: Inline comments, docstrings, README sections
- **How to cite**: File and section (e.g., "README.md:Authentication section")
- **Use for**: Understanding intended usage, design philosophy

**Example:**
```
"As documented in the README (Authentication section), tokens expire after 
1 hour for security reasons."
```


### Validation Process

#### Step 1: Collect Evidence
Gather all relevant sources:
```python
evidence = guide["evidence_bundle"]
source_files = evidence["source_files"]  # What code does
test_files = evidence["test_files"]      # What tests expect
git_commits = evidence["git_commits"]    # Why it exists
documentation = evidence["documentation"] # Intended usage
```

#### Step 2: Cross-Reference Sources
Verify consistency:
```python
# Check if code behavior matches test expectations
code_behavior = validation["code_behavior"]
expected_behavior = validation["expected_behavior"]

if code_behavior == expected_behavior:
    # Sources are consistent - safe to explain
    pass
else:
    # Sources conflict - investigate further
    # Check git history for context
    # Note the discrepancy in enriched content
```

#### Step 3: Distinguish Facts from Inferences
Mark inferences clearly:
```python
# GOOD: Factual statement with citation
"The authenticate() function uses bcrypt for password hashing (auth.py:42)"

# GOOD: Inference marked clearly
"Based on the test file (test_auth.py:67), it appears this function is designed 
to handle rate limiting, though the implementation isn't visible in the current 
code snapshot."

# BAD: Inference presented as fact
"The authenticate() function handles rate limiting"
```

#### Step 4: Validate Against Tests
Always check tests before explaining:
```python
# Read implementation
def login(username, password):
    user = db.get_user(username)
    if bcrypt.checkpw(password, user.password_hash):
        return create_session(user)
    return None

# Read tests
def test_login_with_valid_credentials():
    result = login("alice", "correct_password")
    assert result is not None
    assert result.user_id == "alice"

# Explanation validated by both sources
"The login() function validates credentials using bcrypt (auth.py:15) and 
returns a session object on success (test_auth.py:23 validates this behavior)."
```


## Anti-Hallucination Measures

### Rule 1: Always Cite Evidence
Every claim must reference actual code, tests, commits, or documentation.

**Implementation:**
```python
# Template for evidence-based explanations
def create_explanation(claim, evidence):
    return f"{claim} (see {evidence['file']}:{evidence['line']})"

# Example
explanation = create_explanation(
    "The function validates user credentials",
    {"file": "auth.py", "line": 42}
)
# Output: "The function validates user credentials (see auth.py:42)"
```

**Checklist:**
- [ ] Every technical claim has a citation
- [ ] Citations include file path and line numbers
- [ ] Test evidence validates behavior claims
- [ ] Git commits explain "why" decisions

### Rule 2: Distinguish Facts from Inferences
Mark inferences clearly and explain reasoning.

**Good Examples:**
```
✓ "The code uses bcrypt for hashing (auth.py:42)"  [FACT - visible in code]

✓ "Based on test_auth.py:67, it appears rate limiting is handled elsewhere"  
  [INFERENCE - marked clearly]

✓ "The commit message (abc123f) suggests this was added for security"  
  [INFERENCE - cites source]
```

**Bad Examples:**
```
✗ "The code probably uses bcrypt"  [INFERENCE presented as fact]

✗ "This handles rate limiting"  [CLAIM without evidence]

✗ "Users prefer this approach"  [ASSUMPTION without basis]
```

### Rule 3: Validate Against Tests
Before explaining what code does, check what tests expect.

**Process:**
1. Read the code implementation
2. Read the related tests
3. Verify they align
4. Explain based on both sources
5. Note any discrepancies

**Example:**
```python
# Code says:
def calculate_discount(user_tier):
    if user_tier == "premium":
        return 0.20
    return 0.10

# Tests say:
def test_free_tier_discount():
    assert calculate_discount("free") == 0.0  # ⚠ Discrepancy!

# Enriched explanation:
"The calculate_discount() function returns different discounts based on user tier.
According to the tests (test_pricing.py:34-45):
- Premium users: 20% off
- Standard users: 10% off  
- Free users: 0% off

⚠ Note: The current implementation (pricing.py:78) doesn't handle the 'free' 
tier explicitly, defaulting to 10%. This appears to be a bug, as the test 
expects 0% for free users."
```


### Rule 4: Cross-Reference Sources
Verify consistency across code, tests, docs, and git history.

**Priority Order (when sources conflict):**
1. **Tests** - What the code is expected to do
2. **Code** - What the code actually does
3. **Docs** - What the documentation says
4. **Comments** - What developers noted

**Handling Conflicts:**
```python
# Example conflict
code_says = "Token expires in 1 hour (jwt_handler.py:18)"
docs_say = "Tokens expire after 24 hours (README.md:45)"
tests_validate = "1 hour expiration (test_jwt.py:23)"

# Resolution
explanation = """
⚠ Documentation Discrepancy: The README states tokens expire after 24 hours, 
but the implementation (jwt_handler.py:18) sets expiration to 1 hour, and 
tests (test_jwt.py:23) validate 1-hour expiration. 

Based on git commit abc123f from last week, the expiration was reduced for 
security reasons, but the README wasn't updated. The actual behavior is 
1-hour expiration.
"""
```

### Rule 5: Avoid Assumptions
If you don't have evidence, say so explicitly.

**Good Examples:**
```
✓ "The error handling strategy isn't clear from the available code. The 
   function might raise an exception or return None—we'd need to see the 
   test file to confirm."

✓ "The performance characteristics aren't documented. Based on the algorithm 
   (O(n) iteration), it should scale linearly, but benchmarks would be needed 
   to confirm."

✓ "The original motivation for this design isn't captured in the git history. 
   The earliest commit (abc123f) shows it was present from the start."
```

**Bad Examples:**
```
✗ "The function returns None on error"  [ASSUMPTION]

✗ "This is optimized for performance"  [ASSUMPTION]

✗ "Users requested this feature"  [ASSUMPTION]
```

## Enrichment Guide Structure

### Complete Example

Here's a complete enrichment guide for a user authentication lesson:

```json
{
  "lesson_id": "module-2-lesson-3",
  "feature_mapping": {
    "feature_name": "User Authentication System",
    "user_facing_purpose": "Secure user login and session management",
    "business_value": "Protects user data and ensures only authorized access",
    "entry_points": [
      "POST /api/auth/login",
      "POST /api/auth/logout",
      "GET /api/auth/verify"
    ],
    "feature_flow": [
      "User submits credentials",
      "Server validates against database",
      "Server generates JWT token",
      "Client stores token",
      "Client includes token in subsequent requests",
      "Server validates token for protected routes"
    ]
  },
  "evidence_bundle": {
    "source_files": [
      {
        "path": "src/auth/login.py",
        "lines": [15, 35],
        "code": "def login(username, password):\n    user = db.get_user(username)\n    if not user:\n        return None\n    if bcrypt.checkpw(password, user.password_hash):\n        return create_session(user)\n    return None"
      },
      {
        "path": "src/auth/session.py",
        "lines": [8, 20],
        "code": "def create_session(user):\n    token = jwt.encode({'user_id': user.id}, SECRET_KEY)\n    session = Session(token=token, user_id=user.id)\n    db.save(session)\n    return token"
      }
    ],
    "test_files": [
      {
        "path": "tests/test_auth.py",
        "tests": [
          {
            "name": "test_login_with_valid_credentials",
            "description": "Validates that correct credentials return a session token",
            "line": 23
          },
          {
            "name": "test_login_with_invalid_password",
            "description": "Validates that incorrect password returns None",
            "line": 34
          },
          {
            "name": "test_login_with_nonexistent_user",
            "description": "Validates that nonexistent username returns None",
            "line": 45
          }
        ]
      }
    ],
    "git_commits": [
      {
        "hash": "abc123f",
        "message": "Add JWT-based authentication for API security",
        "date": "2024-01-15",
        "author": "Alice Developer"
      },
      {
        "hash": "def456a",
        "message": "Fix timing attack vulnerability in password comparison",
        "date": "2024-01-20",
        "author": "Bob Security"
      }
    ],
    "documentation": [
      {
        "type": "docstring",
        "content": "Validates user credentials and creates a session token",
        "location": "src/auth/login.py:15"
      },
      {
        "type": "readme",
        "content": "Authentication uses JWT tokens with 1-hour expiration",
        "location": "README.md:Authentication"
      }
    ],
    "dependencies": [
      {
        "name": "bcrypt",
        "reason": "Secure password hashing",
        "evidence": "import bcrypt (login.py:3)"
      },
      {
        "name": "PyJWT",
        "reason": "JWT token generation",
        "evidence": "import jwt (session.py:2)"
      }
    ]
  },
  "validation_checklist": {
    "code_behavior": "Validates credentials using bcrypt, returns session token on success",
    "expected_behavior": "Tests expect token on valid credentials, None on invalid",
    "documentation_alignment": "Docstrings and README align with implementation",
    "git_context": "Added for API security, timing attack fix applied",
    "consistency_check": true
  },
  "teaching_value_assessment": {
    "scores": {
      "reusability": 3,
      "best_practice": 3,
      "fundamentality": 3,
      "uniqueness": 1,
      "junior_dev": 3
    },
    "total_score": 13,
    "should_teach": true,
    "reasoning": "High teaching value: demonstrates security best practices (bcrypt, JWT), fundamental concept (authentication), highly reusable pattern, essential for junior developers"
  },
  "systematic_investigation": {
    "what_it_does": "Validates user credentials by comparing hashed passwords and generates JWT session tokens (login.py:15-35, session.py:8-20)",
    "why_it_exists": "Provides secure authentication for API endpoints, protecting user data from unauthorized access (commit abc123f)",
    "how_it_works": "Uses bcrypt for timing-safe password comparison, generates JWT tokens with user_id payload, stores sessions in database (login.py:19, session.py:10-12)",
    "when_its_used": "Called by POST /api/auth/login endpoint when users attempt to log in (routes.py:45)",
    "edge_cases": [
      "Nonexistent username returns None (test_auth.py:45)",
      "Invalid password returns None (test_auth.py:34)",
      "Database connection failure handled by db layer"
    ],
    "common_pitfalls": [
      "Using == for password comparison (timing attacks) - fixed in commit def456a",
      "Not setting token expiration (security risk)",
      "Storing sensitive data in JWT payload"
    ]
  },
  "narrative_structure": {
    "introduction_points": [
      "Authentication is critical for protecting user data",
      "This lesson covers password hashing and session tokens",
      "You'll learn industry-standard security practices"
    ],
    "learning_progression": [
      "Understanding authentication vs authorization",
      "Password hashing with bcrypt",
      "Session token generation with JWT",
      "Secure session storage",
      "Login flow implementation",
      "Common security vulnerabilities"
    ],
    "code_walkthrough_order": [
      "login() function overview",
      "User lookup and validation",
      "Password comparison with bcrypt",
      "Session creation",
      "JWT token generation",
      "Error handling"
    ],
    "conclusion_points": [
      "Never store passwords in plain text",
      "Always use secure session tokens",
      "Implement rate limiting for protection"
    ],
    "next_steps": [
      "Implement token refresh mechanism",
      "Add multi-factor authentication",
      "Learn about OAuth2 integration"
    ]
  },
  "code_sections": [
    {
      "file_path": "src/auth/login.py",
      "line_range": [15, 35],
      "code_snippet": "def login(username, password):\n    user = db.get_user(username)\n    if not user:\n        return None\n    if bcrypt.checkpw(password, user.password_hash):\n        return create_session(user)\n    return None",
      "purpose": "Validates user credentials and creates a session (validated by test_auth.py:23-45)",
      "key_concepts": [
        "Password verification",
        "Secure hashing comparison",
        "Session creation",
        "Error handling"
      ],
      "explanation_approach": [
        "Start by explaining why we don't check if password is correct first",
        "Emphasize timing attack prevention",
        "Explain bcrypt.checkpw vs simple comparison",
        "Walk through the happy path and error cases",
        "Connect to session creation in next section"
      ],
      "related_code": [
        {
          "path": "src/auth/session.py:create_session",
          "context": "Called when credentials are valid",
          "relationship": "dependency"
        },
        {
          "path": "src/models/user.py:User.password_hash",
          "context": "Stores hashed password",
          "relationship": "data model"
        }
      ],
      "test_evidence": [
        {
          "test_name": "test_login_with_valid_credentials",
          "description": "Validates that correct credentials return a session token",
          "file": "tests/test_auth.py:23"
        },
        {
          "test_name": "test_login_with_invalid_password",
          "description": "Validates that incorrect password returns None",
          "file": "tests/test_auth.py:34"
        }
      ],
      "git_evidence": [
        {
          "commit": "def456a",
          "message": "Fix timing attack vulnerability in password comparison",
          "date": "2024-01-20"
        }
      ],
      "common_mistakes": [
        "Using == to compare passwords (timing attacks)",
        "Returning different errors for invalid username vs password",
        "Not rate limiting login attempts"
      ]
    }
  ],
  "architecture_context": {
    "component_role": "Handles user authentication and session management for the application",
    "data_flow": "User credentials → Login validation → Password check → Session creation → Token return → Client storage",
    "interaction_diagram": "```mermaid\nsequenceDiagram\n    Client->>API: POST /login\n    API->>AuthService: login(username, password)\n    AuthService->>Database: get_user(username)\n    Database-->>AuthService: User object\n    AuthService->>AuthService: bcrypt.checkpw()\n    AuthService->>SessionService: create_session(user)\n    SessionService->>Database: save(session)\n    SessionService-->>AuthService: token\n    AuthService-->>API: token\n    API-->>Client: {token: 'jwt...'}\n```",
    "dependencies": [
      {
        "name": "Database layer",
        "reason": "User lookup and session storage",
        "evidence": "import db (login.py:2)"
      },
      {
        "name": "bcrypt",
        "reason": "Secure password hashing",
        "evidence": "import bcrypt (login.py:3)"
      }
    ],
    "dependents": [
      {
        "name": "API routes",
        "usage": "POST /api/auth/login endpoint",
        "evidence": "routes.py:45"
      }
    ],
    "design_patterns": [
      {
        "pattern": "Service Layer",
        "evidence": "Separates auth logic from API routes",
        "explanation": "Enables reuse and testing"
      }
    ]
  },
  "real_world_context": {
    "practical_use_cases": [
      "Web application login systems",
      "Mobile app authentication",
      "API authentication for third-party integrations",
      "Single sign-on (SSO) systems"
    ],
    "analogies": [
      "Password hashing is like a one-way safe - you can put things in but can't get them back out, only verify if what you put in matches",
      "Session tokens are like movie tickets - they prove you paid (authenticated) without needing to show your credit card every time",
      "Rate limiting is like a bank vault time delay - even if someone has the combination, they can't try it repeatedly"
    ],
    "industry_patterns": [
      "Token-based authentication (JWT)",
      "Password hashing with bcrypt/argon2",
      "Session management patterns",
      "Defense in depth security"
    ],
    "best_practices": [
      "Use bcrypt or argon2 for password hashing",
      "Implement rate limiting on login endpoints",
      "Use HTTPS for all authentication requests",
      "Set appropriate token expiration times",
      "Implement refresh token rotation"
    ],
    "anti_patterns": [
      "Storing passwords in plain text",
      "Using MD5 or SHA1 for password hashing",
      "Not implementing rate limiting",
      "Storing sensitive data in JWT payload"
    ]
  },
  "exercise_generation": {
    "hands_on_tasks": [
      {
        "title": "Add Password Strength Validation",
        "description": "Implement a function that validates password strength (length, special chars, etc.) before hashing",
        "difficulty": "beginner"
      },
      {
        "title": "Implement Token Refresh",
        "description": "Add a refresh token mechanism to extend sessions without requiring re-login",
        "difficulty": "intermediate"
      },
      {
        "title": "Add Rate Limiting",
        "description": "Implement rate limiting to prevent brute force attacks (max 5 attempts per minute)",
        "difficulty": "intermediate"
      }
    ],
    "starter_code": "def validate_token(token: str) -> dict:\n    # TODO: Decode JWT token\n    # TODO: Check expiration\n    # TODO: Return payload if valid\n    pass",
    "solution_code": "def validate_token(token: str) -> dict:\n    try:\n        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n        return payload\n    except jwt.ExpiredSignatureError:\n        raise AuthError('Token has expired')\n    except jwt.InvalidTokenError:\n        raise AuthError('Invalid token')",
    "test_cases": [
      {
        "name": "test_valid_token_returns_payload",
        "description": "Valid token should return payload",
        "file": "tests/test_jwt.py:15"
      },
      {
        "name": "test_expired_token_raises_error",
        "description": "Expired token should raise error",
        "file": "tests/test_jwt.py:23"
      }
    ],
    "progressive_hints": [
      "Remember that JWTs have three parts: header, payload, and signature. The jwt.decode() function handles all three.",
      "Check the jwt library documentation for the decode() method. You'll need to pass the token, SECRET_KEY, and specify the algorithm.",
      "The decode() function automatically checks expiration if you include 'exp' in the payload. It will raise jwt.ExpiredSignatureError if expired.",
      "Wrap your decode call in a try-except block to catch jwt.InvalidTokenError and jwt.ExpiredSignatureError exceptions."
    ],
    "self_assessment": [
      "Why do we use bcrypt instead of SHA256 for password hashing?",
      "What security vulnerability does timing-safe comparison prevent?",
      "Why should JWT tokens have an expiration time?",
      "What's the difference between authentication and authorization?"
    ]
  },
  "anti_hallucination_rules": {
    "always_cite": "Never explain without citing evidence from code, tests, commits, or documentation",
    "distinguish_fact_inference": "Mark inferences clearly with phrases like 'appears to', 'suggests', 'based on'",
    "validate_against_tests": "Check tests before explaining behavior - tests define expected behavior",
    "cross_reference": "Verify consistency across code, tests, docs, and git history before explaining",
    "avoid_assumptions": "If you don't have evidence, say so explicitly rather than guessing"
  },
  "enrichment_instructions": {
    "tone": "casual",
    "depth": "detailed",
    "focus_areas": [
      "Security implications of each design choice",
      "Why certain approaches are better than alternatives",
      "Common mistakes and how to avoid them",
      "Real-world applications of these patterns"
    ],
    "avoid_topics": [
      "Overly academic security theory",
      "Cryptography mathematics",
      "Framework-specific implementation details",
      "Deprecated security practices"
    ],
    "evidence_requirements": "Cite file paths and line numbers for every technical claim"
  }
}
```

## Best Practices

### For AI Assistants (Kiro)

1. **Always Start with Evidence**
   - Read the enrichment guide completely before writing
   - Review all evidence sources (code, tests, commits, docs)
   - Validate understanding across sources
   - Note any conflicts or gaps

2. **Follow the Narrative Structure**
   - Use the provided learning progression
   - Build from simple to complex concepts
   - Connect each section to the next
   - Maintain consistent terminology

3. **Cite Everything**
   - Include file paths and line numbers
   - Reference test names and descriptions
   - Quote commit messages when explaining "why"
   - Link to related code sections

4. **Write for Beginners**
   - Define all technical terms
   - Use analogies for complex concepts
   - Provide step-by-step explanations
   - Anticipate common questions

5. **Create Progressive Hints**
   - Start with conceptual guidance
   - Point to relevant documentation
   - Provide specific implementation details
   - Give near-solution guidance last


### For Course Creators

1. **Generate Quality Basic Structure First**
   - Run thorough codebase analysis
   - Configure appropriate target audience
   - Set meaningful course focus
   - Ensure good teaching value scores

2. **Prioritize High-Value Lessons**
   - Use teaching value scores to prioritize
   - Enrich core concepts before advanced topics
   - Focus on reusable patterns first
   - Save unique/specialized content for later

3. **Review Enriched Content**
   - Verify citations are accurate
   - Check that explanations match code
   - Ensure exercises are achievable
   - Test hints are actually helpful

4. **Iterate on Quality**
   - Refine enrichment instructions based on output
   - Update steering files with lessons learned
   - Re-enrich lessons when code changes significantly
   - Gather learner feedback and adjust

### For System Implementers

1. **Implement Evidence Collection First**
   - Git analyzer for commit history
   - Test file discovery and parsing
   - Documentation extraction
   - Dependency analysis

2. **Build Validation Layer**
   - Cross-reference sources
   - Detect conflicts
   - Verify consistency
   - Flag missing evidence

3. **Create Comprehensive Guides**
   - Include all 12 sections
   - Provide rich evidence bundles
   - Generate clear instructions
   - Add anti-hallucination rules

4. **Test End-to-End**
   - Verify guides are complete
   - Test enrichment workflow
   - Validate enriched content quality
   - Check export formats

## Common Pitfalls and Solutions

### Pitfall 1: Hallucinating Features
**Problem**: AI explains features that don't exist in the code.

**Solution**: 
- Always require citations
- Validate against tests
- Cross-reference sources
- Mark inferences clearly

**Example:**
```
❌ "This function includes rate limiting and caching"
✓ "This function validates credentials (auth.py:15). Rate limiting is 
   handled by middleware (middleware.py:67), and caching isn't implemented 
   for authentication."
```


### Pitfall 2: Assuming Prior Knowledge
**Problem**: Explanations use jargon without defining terms.

**Solution**:
- Define all technical terms on first use
- Use analogies for complex concepts
- Build progressively from simple to complex
- Provide context before diving into details

**Example:**
```
❌ "Use the JWT library to decode the token"
✓ "JWT (JSON Web Token) is a secure way to transmit information between 
   parties. Think of it like a sealed envelope—you can see who it's for, 
   but only the recipient can open it. We'll use the jwt library to decode 
   (open) the token."
```

### Pitfall 3: Vague Explanations
**Problem**: Explanations are too general and don't provide specifics.

**Solution**:
- Include specific file paths and line numbers
- Explain what each line of code does
- Connect code to real-world usage
- Provide concrete examples

**Example:**
```
❌ "This code handles authentication"
✓ "This code validates user credentials by comparing the provided password 
   with the stored hash (line 42 in auth.py). If they match, it generates 
   a JWT token (line 48) that the client can use for subsequent requests."
```

### Pitfall 4: Missing Context
**Problem**: Jumping straight to implementation without explaining why.

**Solution**:
- Start with motivation and context
- Explain the problem being solved
- Show real-world relevance
- Then dive into implementation

**Example:**
```
❌ "Here's how to implement token validation"
✓ "Now that you understand how tokens are generated, let's implement 
   validation. This is crucial for protecting API routes—every protected 
   endpoint needs to verify that the token is valid, not expired, and 
   properly signed. Here's how..."
```

### Pitfall 5: Generic Hints
**Problem**: Exercise hints are too vague to be helpful.

**Solution**:
- Create 3-5 progressive hints
- Start with conceptual guidance
- Point to specific documentation
- Provide implementation details
- Give near-solution guidance last

**Example:**
```
❌ "Look at the documentation"
✓ Hint 1: "JWT tokens have three parts—header, payload, and signature"
✓ Hint 2: "The jwt.decode() function handles all three parts automatically"
✓ Hint 3: "Check the jwt library docs for the decode() method parameters"
✓ Hint 4: "You'll need to pass the token, SECRET_KEY, and specify 
           algorithms=['HS256']"
```


## Testing and Validation

### Unit Tests
Test individual components of the enrichment system:

```python
# Test enrichment guide generation
def test_get_enrichment_guide():
    guide = await get_enrichment_guide("test-codebase", "module-1-lesson-1")
    
    # Verify all sections present
    assert "feature_mapping" in guide
    assert "evidence_bundle" in guide
    assert "validation_checklist" in guide
    assert "teaching_value_assessment" in guide
    assert "systematic_investigation" in guide
    
    # Verify evidence is populated
    assert len(guide["evidence_bundle"]["source_files"]) > 0
    assert len(guide["evidence_bundle"]["test_files"]) > 0
    
    # Verify citations are present
    for section in guide["code_sections"]:
        assert section["file_path"]
        assert section["line_range"]
        assert len(section["test_evidence"]) > 0

# Test lesson content update
def test_update_lesson_content():
    enriched = {
        "description": "Enhanced description",
        "content": "Full learning narrative",
        "code_examples": [{"explanation": "Detailed explanation"}],
        "exercises": [{"hints": ["Hint 1", "Hint 2"]}]
    }
    
    result = await update_lesson_content(
        "test-codebase",
        "module-1-lesson-1",
        enriched
    )
    
    assert result["success"] == True
    assert "description" in result["updated_fields"]
```

### Integration Tests
Test the complete enrichment workflow:

```python
def test_enrichment_workflow():
    # 1. Generate basic course
    course = await export_course("test-codebase", format="json")
    
    # 2. List lessons
    lessons = await list_lessons_for_enrichment("test-codebase")
    assert len(lessons) > 0
    
    # 3. Get enrichment guide
    guide = await get_enrichment_guide("test-codebase", lessons[0]["lesson_id"])
    
    # 4. Verify guide quality
    assert guide["teaching_value_assessment"]["total_score"] > 0
    assert len(guide["code_sections"]) > 0
    
    # 5. Simulate enrichment
    enriched = simulate_kiro_enrichment(guide)
    
    # 6. Update lesson
    result = await update_lesson_content(
        "test-codebase",
        lessons[0]["lesson_id"],
        enriched
    )
    assert result["success"] == True
    
    # 7. Verify persistence
    updated_course = await export_course("test-codebase", format="json")
    lesson = find_lesson(updated_course, lessons[0]["lesson_id"])
    assert lesson["description"] == enriched["description"]
```


### Quality Validation
Test enriched content quality:

```python
def test_enrichment_quality():
    guide = await get_enrichment_guide("test-codebase", "module-1-lesson-1")
    
    # Test that explanations cite actual code
    for section in guide["code_sections"]:
        assert section["file_path"]
        assert section["line_range"]
        assert section["purpose"]
        # Verify citations in purpose
        assert any(section["file_path"] in evidence["file"] 
                  for evidence in section["test_evidence"])
    
    # Test that examples are from real codebase
    for source in guide["evidence_bundle"]["source_files"]:
        assert os.path.exists(source["path"])
        with open(source["path"]) as f:
            content = f.read()
            assert source["code"] in content
    
    # Test that exercises have validation tests
    assert len(guide["exercise_generation"]["test_cases"]) > 0
    
    # Test that hints are progressive
    hints = guide["exercise_generation"]["progressive_hints"]
    assert len(hints) >= 3
    assert len(hints) <= 5
    # First hint should be more general than last
    assert len(hints[0]) < len(hints[-1])
    
    # Test anti-hallucination rules are present
    rules = guide["anti_hallucination_rules"]
    assert "always_cite" in rules
    assert "validate_against_tests" in rules
```

## Performance Considerations

### Caching Strategy
- Cache enrichment guides for 1 hour (configurable)
- Invalidate cache when source code changes
- Use codebase_id + lesson_id as cache key
- Store in SQLite for persistence

### Batch Processing
- Support enriching multiple lessons in one session
- Maintain context across related lessons
- Reuse evidence bundles for related code
- Parallelize evidence collection where possible

### Incremental Updates
- Track enrichment status per lesson
- Support re-enrichment when code changes
- Preserve manual edits during re-enrichment
- Version enriched content for rollback

## Configuration

### Enrichment Settings (config.yaml)
```yaml
ai_enrichment:
  # Default enrichment settings
  defaults:
    skill_level: "beginner"  # beginner, intermediate, advanced
    tone: "casual"           # casual, formal, technical
    depth: "detailed"        # brief, moderate, detailed
  
  # Content options
  content_options:
    include_analogies: true
    include_diagrams: true
    include_real_world_examples: true
    include_common_mistakes: true
  
  # Evidence requirements
  evidence:
    require_test_citations: true
    require_git_context: true
    require_code_citations: true
    min_evidence_sources: 2
  
  # Teaching value thresholds
  teaching_value:
    min_score_to_teach: 7
    prioritize_high_value: true
  
  # Cache settings
  cache:
    ttl_seconds: 3600
    invalidate_on_code_change: true
```


### Steering File (.kiro/steering/ai-content-enrichment.md)
The steering file provides guidelines for Kiro when enriching content. See `.kiro/steering/ai-content-enrichment.md` for the complete enrichment guidelines that Kiro follows.

Key sections include:
- Core principles (evidence-based, beginner-friendly, systematic investigation)
- Enrichment workflow (step-by-step process)
- Anti-hallucination rules (always cite, validate, cross-reference)
- Content guidelines (tone, structure, language, depth)
- Quality checklist (evidence requirements, completeness, accuracy)

## Troubleshooting

### Issue: Enrichment guide is incomplete
**Symptoms**: Missing evidence, empty sections, no citations

**Solutions**:
1. Check that codebase analysis completed successfully
2. Verify test files are discoverable (naming conventions)
3. Ensure git repository is initialized and has history
4. Check file permissions for reading source files
5. Review analysis configuration (file size limits, patterns)

### Issue: Citations are inaccurate
**Symptoms**: Line numbers don't match, files don't exist, tests not found

**Solutions**:
1. Verify codebase hasn't changed since analysis
2. Re-run analysis to update file information
3. Check that file paths are relative to project root
4. Ensure test discovery patterns match your test structure
5. Validate git commit hashes are accessible

### Issue: Teaching value scores are too low
**Symptoms**: No lessons recommended for teaching, all scores < 7

**Solutions**:
1. Review teaching value criteria (may be too strict)
2. Adjust scoring weights in configuration
3. Check that code has documentation (affects scores)
4. Verify pattern detection is working (affects reusability)
5. Consider if codebase is suitable for teaching

### Issue: Enriched content is too technical
**Symptoms**: Jargon not defined, assumes prior knowledge, not beginner-friendly

**Solutions**:
1. Review enrichment instructions (tone, depth, skill_level)
2. Update steering file with more beginner-friendly guidelines
3. Add more analogies to real_world_context
4. Increase focus on fundamentals in teaching value assessment
5. Provide example enrichments as templates

### Issue: Validation fails (sources conflict)
**Symptoms**: consistency_check is false, conflicting evidence

**Solutions**:
1. Review git history for context on conflicts
2. Prioritize tests over documentation
3. Note conflicts explicitly in enriched content
4. Update outdated documentation
5. Add comments explaining discrepancies


## Future Enhancements

### Planned Features

1. **Automated Quality Scoring**
   - Readability analysis of enriched content
   - Citation coverage metrics
   - Beginner-friendliness scoring
   - Automated quality reports

2. **Interactive Enrichment**
   - Real-time preview of enriched content
   - Inline editing with validation
   - Collaborative enrichment workflows
   - Version comparison and rollback

3. **Advanced Evidence Collection**
   - Code execution traces
   - Performance profiling data
   - User interaction analytics
   - Production error logs

4. **Multi-Language Support**
   - Translate enriched content
   - Localize analogies and examples
   - Cultural context adaptation
   - Language-specific best practices

5. **AI-Assisted Improvements**
   - Suggest better analogies
   - Identify missing explanations
   - Recommend additional exercises
   - Detect outdated content

## Related Documentation

- **[Course Generator Specification](COURSE_GENERATOR_SPEC_COMPLETE.md)**: Complete course generation system
- **[Project Status and Roadmap](PROJECT_STATUS_AND_ROADMAP.md)**: Current implementation status
- **[Start Here Guide](START_HERE.md)**: Getting started with the system
- **[Local Test Guide](LOCAL_TEST_GUIDE.md)**: Testing instructions
- **[Feature-to-Lesson Mapping](../NEW_OBJECTIVE/FEATURE-TO-LESSON-MAPPING.md)**: Framework for mapping features to lessons
- **[Knowledge-to-Course Framework](../NEW_OBJECTIVE/KNOWLEDGE-TO-COURSE-FRAMEWORK.md)**: Systematic investigation framework

## Contributing

### Adding New Evidence Sources

To add a new evidence source (e.g., API logs, user feedback):

1. Create collector in `src/course/evidence_collector.py`:
```python
def collect_api_logs(lesson: LessonContent) -> List[Dict[str, Any]]:
    """Collect API usage logs for lesson code"""
    # Implementation
    pass
```

2. Add to evidence bundle in `enrichment_guide_generator.py`:
```python
evidence_bundle = EvidenceBundle(
    # ... existing sources ...
    api_logs=self._collect_api_logs(lesson)
)
```

3. Update enrichment guide structure in `enrichment_models.py`:
```python
@dataclass
class EvidenceBundle:
    # ... existing fields ...
    api_logs: List[Dict[str, Any]]
```

4. Document in this file and update examples


### Adding New Validation Rules

To add a new validation rule:

1. Create validator in `src/course/validation_engine.py`:
```python
def validate_performance_claims(
    evidence: EvidenceBundle
) -> ValidationResult:
    """Validate performance claims against benchmarks"""
    # Implementation
    pass
```

2. Add to validation checklist in `enrichment_guide_generator.py`:
```python
validation = ValidationChecklist(
    # ... existing checks ...
    performance_validation=self._validate_performance_claims(evidence)
)
```

3. Update anti-hallucination rules to include new validation
4. Document in this file and steering file

### Improving Teaching Value Assessment

To adjust teaching value scoring:

1. Modify scoring functions in `src/course/teaching_value_assessor.py`:
```python
def score_reusability(patterns: List[Pattern]) -> int:
    """Score 0-3 based on pattern reusability"""
    # Adjust scoring logic
    pass
```

2. Update weights in configuration:
```yaml
teaching_value:
  weights:
    reusability: 3
    best_practice: 3
    fundamentality: 3
    uniqueness: 2
    junior_dev: 3
```

3. Test with various codebases to validate scores
4. Document scoring criteria in this file

## Appendix

### Glossary

- **Enrichment Guide**: Comprehensive, evidence-based document containing all context and instructions for AI to enrich lesson content
- **Evidence Bundle**: Collection of source code, tests, git commits, and documentation that validates understanding
- **Feature Mapping**: Process of connecting code implementation to user-facing features and business value
- **Systematic Investigation**: Structured approach to understanding code by answering what, why, how, when, edge cases, and pitfalls
- **Teaching Value Assessment**: Scoring system (0-14) that evaluates whether code is worth teaching
- **Anti-Hallucination Rules**: Guidelines requiring AI to cite evidence and distinguish facts from inferences
- **Validation Checklist**: Cross-reference of multiple evidence sources to ensure consistency
- **Narrative Structure**: Organized flow for lesson content (introduction, progression, conclusion)
- **Code Section Guide**: Detailed guidance for explaining a specific code section with evidence
- **Progressive Hints**: 3-5 hints that start general and become more specific

### Acronyms

- **MCP**: Model Context Protocol
- **JWT**: JSON Web Token
- **API**: Application Programming Interface
- **AST**: Abstract Syntax Tree
- **LLM**: Large Language Model
- **TTL**: Time To Live (cache duration)


### Example Enrichment Session

Here's a complete example of enriching a lesson using Kiro:

```
User: "Enrich the authentication lesson in my course"

Kiro: "I'll enrich the authentication lesson. Let me start by getting the 
enrichment guide."

[Calls get_enrichment_guide("my-project", "module-2-lesson-3")]

Kiro: "I've reviewed the enrichment guide. This lesson covers JWT-based 
authentication with a teaching value score of 13/14 (excellent). The evidence 
bundle includes:
- 2 source files (login.py, session.py)
- 3 test files with 8 test cases
- 2 git commits explaining security improvements
- Documentation from README and docstrings

All sources are consistent. I'll now create enriched content following the 
narrative structure and citing all evidence."

[Generates enriched content with citations]

Kiro: "I've created comprehensive enriched content including:
- Enhanced description with context and learning goals
- Full learning narrative (1,200 words) with progressive explanation
- Detailed code walkthroughs with line-by-line explanations
- 3 hands-on exercises with progressive hints
- Real-world analogies (password hashing as one-way safe, tokens as movie tickets)
- Common mistakes section citing actual test failures

All explanations cite specific files and line numbers. Ready to update the lesson?"

User: "Yes, update it"

[Calls update_lesson_content with enriched content]

Kiro: "✓ Successfully enriched lesson 'User Authentication with JWT'
Updated fields: description, content, code_examples, exercises, learning_objectives

The lesson now includes:
- 5 learning objectives
- 2 code examples with detailed explanations
- 3 exercises with 4 progressive hints each
- 12 citations to source code
- 8 citations to test files
- 2 citations to git commits

Would you like me to enrich the next lesson?"
```

## Summary

The AI Content Enrichment system transforms basic course structures into comprehensive educational materials through:

1. **Evidence-Based Approach**: All content grounded in actual code, tests, commits, and documentation
2. **Systematic Investigation**: Structured process answering what, why, how, when, edge cases, and pitfalls
3. **Anti-Hallucination Measures**: Strict requirements for citations and validation
4. **Beginner-Friendly Content**: Simple language, progressive explanations, real-world analogies
5. **MCP Integration**: Three tools (get_enrichment_guide, update_lesson_content, list_lessons_for_enrichment)
6. **Kiro-Driven Workflow**: Leverages Kiro's capabilities for flexible, conversational enrichment

The system ensures accuracy through comprehensive evidence collection and validation, while maintaining accessibility through beginner-friendly guidelines and progressive learning structures.

For implementation details, see the design document at `.kiro/specs/ai-content-enrichment/design.md`.

For enrichment guidelines that Kiro follows, see `.kiro/steering/ai-content-enrichment.md`.

---

**Last Updated**: 2024-01-15  
**Version**: 1.0  
**Status**: Implementation Complete
