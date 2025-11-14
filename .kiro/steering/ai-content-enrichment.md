# AI Content Enrichment Guidelines

## Purpose

This steering file guides Kiro through the process of enriching course content with comprehensive, evidence-based educational materials. The enrichment process transforms basic course structures into rich learning experiences by leveraging systematic investigation, validation, and beginner-friendly explanations.

## Core Principles

### 1. Evidence-Based Content
- **Always cite sources**: Every claim must reference actual code, tests, commits, or documentation
- **Validate understanding**: Cross-reference multiple sources (code, tests, docs, git history) before explaining
- **Distinguish facts from inferences**: Clearly mark when you're inferring vs. stating facts
- **Never guess**: If you don't have evidence, say so explicitly

### 2. Beginner-Friendly Approach
- **Use simple language**: Avoid jargon unless you define it first
- **Build progressively**: Start with simple concepts, gradually introduce complexity
- **Provide context**: Explain why something matters before diving into how it works
- **Use analogies**: Connect technical concepts to familiar real-world scenarios
- **Define everything**: Don't assume prior knowledge

### 3. Systematic Investigation
Before enriching any lesson, answer these questions with evidence:
- **What does it do?** (cite code sections)
- **Why does it exist?** (cite git commits, documentation)
- **How does it work?** (cite implementation details)
- **When is it used?** (cite call sites, usage examples)
- **What are edge cases?** (cite tests)
- **What are common pitfalls?** (cite comments, test failures)

## Enrichment Workflow

### Step 1: Get Enrichment Guide
```
Call: get_enrichment_guide(codebase_id, lesson_id)
```

This returns a comprehensive guide containing:
- Feature mapping (what users do with this code)
- Evidence bundle (source files, tests, commits, docs)
- Validation checklist (consistency across sources)
- Teaching value assessment (why this is worth teaching)
- Systematic investigation (what, why, how, when, edge cases, pitfalls)
- Narrative structure (how to organize the explanation)
- Code section guides (detailed guidance for each code snippet)
- Architecture context (how it fits in the system)
- Real-world context (practical use cases, analogies)
- Exercise generation (hands-on practice with hints)

### Step 2: Review Evidence
Before writing anything, review:
- **Source code**: What does the code actually do?
- **Tests**: What behavior do tests expect?
- **Git commits**: Why was this code written?
- **Documentation**: What do comments/docs say?
- **Dependencies**: What does this code depend on?

Verify consistency across all sources. If sources conflict, investigate why.

### Step 3: Enrich Content
Generate rich content following these guidelines:

#### Description Enhancement
Transform basic descriptions into engaging introductions:
- Set context: Why does this topic matter?
- State learning goals: What will learners be able to do?
- Preview key concepts: What will be covered?
- Connect to real-world: Where is this used in practice?

**Example:**
```
Basic: "This lesson covers user authentication."

Enriched: "User authentication is the foundation of secure web applications, 
ensuring that only authorized users can access protected resources. In this 
lesson, you'll learn how to implement JWT-based authentication, a widely-used 
industry standard that balances security with performance. By the end, you'll 
understand how to generate tokens, validate them, and protect API routes—skills 
essential for any full-stack developer."
```

#### Content (Learning Narrative)
Create a progressive learning narrative:

1. **Introduction** (2-3 paragraphs)
   - Context and motivation
   - Real-world relevance
   - Learning objectives

2. **Concept Explanation** (simple → complex)
   - Start with the "what" and "why"
   - Build to the "how"
   - Use analogies for complex concepts
   - Define all technical terms

3. **Code Walkthrough** (with evidence)
   - Explain each code section in plain language
   - Cite line numbers and file paths
   - Connect code to concepts
   - Highlight key patterns and best practices

4. **Architecture Context**
   - Show how this fits in the larger system
   - Explain data flow
   - Identify dependencies and relationships

5. **Real-World Application**
   - Practical use cases
   - Industry patterns
   - Best practices and anti-patterns

6. **Summary** (2-3 paragraphs)
   - Reinforce key takeaways
   - Connect to next steps
   - Encourage practice

#### Code Example Enhancement
For each code example, provide:
- **Purpose**: What does this code accomplish? (cite tests)
- **Key concepts**: What programming concepts does it demonstrate?
- **Line-by-line explanation**: Plain language walkthrough
- **Why it matters**: Connection to real-world usage
- **Common mistakes**: Pitfalls to avoid (cite evidence)
- **Related code**: Links to related sections with context

**Example:**
```python
# Code: src/auth/jwt_handler.py, lines 15-25
def generate_token(user_id: str, expires_in: int = 3600) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

**Enriched Explanation:**
"This function creates a JWT (JSON Web Token) for authenticated users. Think of 
a JWT like a secure ID badge—it contains information about who you are (user_id) 
and when it expires (exp).

Line 16-19: We create a 'payload' dictionary with two pieces of information:
- user_id: Identifies which user this token belongs to
- exp: Sets an expiration time (default 1 hour from now)

Line 20: We 'encode' this payload using a SECRET_KEY (like sealing the badge 
with a tamper-proof seal) and return the token string.

**Why this matters**: JWTs are stateless—the server doesn't need to store 
session data in a database. This makes them perfect for scalable APIs.

**Common mistake**: Never store sensitive data in the payload! JWTs are encoded, 
not encrypted—anyone can decode and read them. (See test_jwt_security.py:45 
for validation of this principle.)"

#### Exercise Enhancement
Transform basic exercises into guided learning experiences:

1. **Clear instructions**: Number steps, be specific
2. **Progressive hints**: Start general, get more specific
   - Hint 1: Conceptual guidance
   - Hint 2: Point to relevant code/docs
   - Hint 3: Specific implementation detail
   - Hint 4: Near-solution guidance
3. **Expected outcomes**: What should happen when correct?
4. **Common pitfalls**: What mistakes do learners often make?
5. **Self-assessment**: Questions to verify understanding

**Example:**
```
Basic Exercise: "Implement token validation"

Enriched Exercise:
Title: "Validate JWT Tokens"

Description: "Now that you understand how tokens are generated, let's implement 
the validation logic. This is crucial for protecting API routes—you'll verify 
that tokens are valid, not expired, and properly signed."

Instructions:
1. Create a function called validate_token(token: str) → dict
2. Decode the JWT using the SECRET_KEY
3. Check if the token has expired
4. Return the payload if valid, raise an exception if invalid
5. Test your implementation with the provided test cases

Starter Code:
[Provided from codebase]

Progressive Hints:
1. "Remember that JWTs have three parts: header, payload, and signature. The 
   jwt.decode() function handles all three."
2. "Check the jwt library documentation for the decode() method. You'll need 
   to pass the token, SECRET_KEY, and specify the algorithm."
3. "The decode() function automatically checks expiration if you include 
   'exp' in the payload. It will raise jwt.ExpiredSignatureError if expired."
4. "Wrap your decode call in a try-except block to catch jwt.InvalidTokenError 
   and jwt.ExpiredSignatureError exceptions."

Expected Outcome:
"When you run the tests, all 5 test cases should pass:
- test_valid_token_returns_payload ✓
- test_expired_token_raises_error ✓
- test_invalid_signature_raises_error ✓
- test_malformed_token_raises_error ✓
- test_missing_token_raises_error ✓"

Common Pitfalls:
"⚠️ Don't forget to specify the algorithm in decode()—it's required for security.
⚠️ Handle exceptions properly—never let token errors crash your application.
⚠️ Validate the payload structure after decoding—ensure required fields exist."
```

### Step 4: Update Lesson Content
```
Call: update_lesson_content(codebase_id, lesson_id, enriched_content)
```

Pass the enriched content as a dictionary:
```python
{
    "description": "Enhanced description with context and goals",
    "content": "Full learning narrative with progressive explanation",
    "code_examples": [
        {
            "explanation": "Enhanced explanation with evidence citations"
        }
    ],
    "exercises": [
        {
            "description": "Clear, engaging description",
            "instructions": "Numbered, specific steps",
            "hints": ["Progressive hints from general to specific"]
        }
    ],
    "learning_objectives": [
        "Specific, measurable learning goals"
    ]
}
```

## Anti-Hallucination Rules

### Rule 1: Always Cite Evidence
Every claim must reference actual code, tests, commits, or documentation.

**Good:**
"The authenticate() function validates user credentials by comparing the hashed 
password (line 42 in auth.py) with the stored hash from the database."

**Bad:**
"The authenticate() function probably uses bcrypt to hash passwords."

### Rule 2: Distinguish Facts from Inferences
Mark inferences clearly and explain your reasoning.

**Good:**
"Based on the test file (test_auth.py:67), it appears this function is designed 
to handle rate limiting, though the implementation isn't visible in the current 
code snapshot."

**Bad:**
"This function handles rate limiting."

### Rule 3: Validate Against Tests
Before explaining what code does, check what tests expect.

**Process:**
1. Read the code implementation
2. Read the related tests
3. Verify they align
4. Explain based on both sources

**Example:**
"The calculate_discount() function returns a percentage discount based on user 
tier. According to test_pricing.py:34-45, premium users get 20% off, standard 
users get 10% off, and free users get 0% off. The implementation (pricing.py:78) 
confirms this logic."

### Rule 4: Cross-Reference Sources
Verify consistency across code, tests, docs, and git history.

**If sources conflict:**
- Note the discrepancy explicitly
- Investigate the git history for context
- Prioritize: tests > code > docs > comments
- Explain the conflict to learners

**Example:**
"⚠️ Note: The documentation (README.md:45) states that tokens expire after 24 
hours, but the code (jwt_handler.py:18) sets expiration to 1 hour, and tests 
(test_jwt.py:23) validate 1-hour expiration. Based on git commit abc123f from 
last week, the expiration was reduced for security reasons, but the README 
wasn't updated."

### Rule 5: Avoid Assumptions
If you don't have evidence, say so explicitly.

**Good:**
"The error handling strategy isn't clear from the available code. The function 
might raise an exception or return None—we'd need to see the test file to 
confirm."

**Bad:**
"The function returns None on error."

## Content Guidelines

### Tone
- **Conversational**: Write like you're explaining to a friend
- **Encouraging**: Celebrate progress, normalize mistakes
- **Precise**: Be technically accurate while staying accessible
- **Enthusiastic**: Show genuine interest in the topic

### Structure
- **Short paragraphs**: 2-4 sentences max
- **Frequent headings**: Break content into scannable sections
- **Code-text balance**: Alternate between explanation and code
- **Visual aids**: Use diagrams, tables, lists for clarity

### Language
- **Active voice**: "The function validates..." not "The validation is performed..."
- **Present tense**: "The code creates..." not "The code will create..."
- **Second person**: "You'll implement..." not "We will implement..."
- **Concrete examples**: Show, don't just tell

### Depth
- **Explain the "why"**: Don't just describe what code does
- **Connect concepts**: Link to previously learned material
- **Provide context**: Show how it fits in the bigger picture
- **Anticipate questions**: Address common confusion points

## Example Enrichment Process

### Input: Basic Lesson
```
Title: "User Authentication"
Description: "Learn about user authentication"
Content: "This lesson covers JWT authentication."
Code Examples: [JWT generation code]
Exercises: [Basic token validation exercise]
```

### Process:

1. **Call get_enrichment_guide**
   - Receive comprehensive evidence bundle
   - Review feature mapping: "User login flow"
   - Check teaching value: 12/14 (high value)
   - Read systematic investigation results

2. **Review Evidence**
   - Source: src/auth/jwt_handler.py (token generation)
   - Tests: tests/test_auth.py (validates behavior)
   - Commits: "Add JWT auth for API security" (explains why)
   - Docs: README.md section on authentication

3. **Validate Understanding**
   - Code creates tokens with user_id and expiration
   - Tests expect 1-hour expiration, HS256 algorithm
   - Git history shows security was the motivation
   - All sources consistent ✓

4. **Enrich Content**
   - Write engaging introduction with real-world context
   - Create progressive explanation (concept → implementation)
   - Add detailed code walkthrough with line-by-line explanation
   - Include architecture context (how auth fits in the API)
   - Provide practical use cases and best practices
   - Write comprehensive summary with next steps

5. **Enhance Exercises**
   - Add clear, numbered instructions
   - Create 4 progressive hints
   - Specify expected outcomes
   - Highlight common pitfalls
   - Add self-assessment questions

6. **Call update_lesson_content**
   - Pass enriched description, content, code explanations, exercises
   - Verify successful update

### Output: Enriched Lesson
```
Title: "User Authentication with JWT"

Description: "User authentication is the foundation of secure web applications. 
In this lesson, you'll learn how to implement JWT-based authentication, a 
widely-used industry standard that balances security with performance. You'll 
understand how to generate tokens, validate them, and protect API routes—skills 
essential for any full-stack developer."

Content: [Full learning narrative with:
- Introduction explaining why authentication matters
- Progressive explanation of JWT concepts
- Detailed code walkthrough with evidence citations
- Architecture context showing how auth fits in the system
- Real-world use cases and best practices
- Summary reinforcing key takeaways]

Code Examples: [Enhanced with:
- Purpose statements citing tests
- Line-by-line explanations in plain language
- Key concepts highlighted
- Common mistakes noted with evidence
- Related code references]

Exercises: [Enhanced with:
- Clear, numbered instructions
- 4 progressive hints (general → specific)
- Expected outcomes
- Common pitfalls
- Self-assessment questions]

Learning Objectives: [Generated from evidence:
- "Generate secure JWT tokens with appropriate expiration times"
- "Validate JWT tokens and handle authentication errors gracefully"
- "Implement protected API routes using JWT middleware"
- "Understand JWT security best practices and common vulnerabilities"]
```

## Quality Checklist

Before submitting enriched content, verify:

### Evidence Requirements
- [ ] Every claim cites specific code, tests, commits, or docs
- [ ] All code references include file paths and line numbers
- [ ] Test evidence validates explained behavior
- [ ] Git context explains the "why" behind code decisions
- [ ] Sources are consistent (or conflicts are explained)

### Beginner-Friendly
- [ ] Technical terms are defined on first use
- [ ] Concepts build progressively (simple → complex)
- [ ] Analogies connect technical concepts to familiar ideas
- [ ] No assumptions about prior knowledge
- [ ] Language is clear and conversational

### Completeness
- [ ] Description sets context and states learning goals
- [ ] Content includes introduction, explanation, walkthrough, and summary
- [ ] Code examples have detailed explanations
- [ ] Exercises have clear instructions and progressive hints
- [ ] Learning objectives are specific and measurable

### Accuracy
- [ ] Code explanations match actual implementation
- [ ] Test expectations align with code behavior
- [ ] Documentation is consistent with code
- [ ] No hallucinated features or capabilities
- [ ] Inferences are clearly marked as such

## Common Mistakes to Avoid

### ❌ Hallucinating Features
"This function includes rate limiting and caching."
(Without evidence from code or tests)

### ✅ Evidence-Based Claims
"This function validates user credentials (auth.py:42). Based on the test suite, 
it doesn't include rate limiting—that's handled by the middleware layer 
(middleware.py:67)."

---

### ❌ Assuming Knowledge
"Use the JWT library to decode the token."
(Assumes learner knows what JWT is)

### ✅ Building Knowledge
"JWT (JSON Web Token) is a secure way to transmit information between parties. 
Think of it like a sealed envelope—you can see who it's for, but only the 
recipient can open it. We'll use the jwt library to decode (open) the token."

---

### ❌ Vague Explanations
"This code handles authentication."
(Too general, no specifics)

### ✅ Specific Explanations
"This code validates user credentials by comparing the provided password with 
the stored hash (line 42). If they match, it generates a JWT token (line 48) 
that the client can use for subsequent requests."

---

### ❌ Missing Context
"Here's how to implement token validation."
(Jumps straight to implementation)

### ✅ Providing Context
"Now that you understand how tokens are generated, let's implement validation. 
This is crucial for protecting API routes—every protected endpoint needs to 
verify that the token is valid, not expired, and properly signed. Here's how..."

---

### ❌ Generic Hints
"Look at the documentation."
(Not helpful)

### ✅ Progressive Hints
"Hint 1: JWT tokens have three parts—header, payload, and signature.
Hint 2: The jwt.decode() function handles all three parts automatically.
Hint 3: Check the jwt library docs for the decode() method parameters.
Hint 4: You'll need to pass the token, SECRET_KEY, and specify algorithms=['HS256']."

## Success Criteria

Enriched content is successful when:

1. **Learners understand the "why"**: Not just what code does, but why it matters
2. **Concepts build progressively**: Each section builds on previous knowledge
3. **Evidence supports all claims**: Every explanation cites actual code/tests
4. **Exercises guide learning**: Hints help learners discover solutions
5. **Content is accessible**: Beginners can follow without prior expertise

## Remember

Your goal is to transform code into learning experiences. Every lesson should:
- **Inspire curiosity**: Make learners want to understand more
- **Build confidence**: Show that complex concepts are learnable
- **Provide clarity**: Explain technical concepts in plain language
- **Enable practice**: Give hands-on exercises with guidance
- **Ensure accuracy**: Ground all content in evidence

When in doubt, cite your sources, explain your reasoning, and prioritize clarity over cleverness.
