# Investigation Checklist: Codebase → Course

## Use this checklist for EVERY concept you want to teach

---

## Phase 1: Understanding & Validation

### □ Read the Code
- [ ] Locate the file(s) containing this concept
- [ ] Read the implementation thoroughly
- [ ] Identify key functions/classes/components
- [ ] Note any complexity or patterns
- [ ] List all dependencies/imports

**Evidence collected:**
- File path: ________________
- Lines: ________________
- Key functions: ________________

### □ Verify with Tests
- [ ] Find related test files
- [ ] Read test descriptions
- [ ] Understand expected behavior
- [ ] Note edge cases tested
- [ ] Check test coverage

**Evidence collected:**
- Test file: ________________
- Key tests: ________________
- Coverage: ________________

### □ Check Documentation
- [ ] Read inline comments
- [ ] Check JSDoc/docstrings
- [ ] Review README mentions
- [ ] Look for architecture docs
- [ ] Find API documentation

**Evidence collected:**
- Documentation quotes: ________________
- Stated purpose: ________________

### □ Review Git History
- [ ] Find commits that introduced this code
- [ ] Read commit messages
- [ ] Check PR descriptions
- [ ] Look for related issues
- [ ] Understand the "why"

**Evidence collected:**
- Commit: ________________
- Reason: ________________

### □ Cross-Reference
- [ ] Find where this is used
- [ ] Check how many files import it
- [ ] Look for similar patterns elsewhere
- [ ] Verify consistency
- [ ] Identify dependencies

**Evidence collected:**
- Used by: ________________ files
- Similar patterns: ________________

---

## Phase 2: Teaching Value Assessment

### □ Reusability (0-3 points)
- [ ] 0: One-off, specific to this project
- [ ] 1: Could be reused with modifications
- [ ] 2: Reusable pattern
- [ ] 3: Universal, applicable anywhere

**Score: ___/3**

### □ Best Practice (0-3 points)
- [ ] 0: Workaround or hack
- [ ] 1: Acceptable approach
- [ ] 2: Good practice
- [ ] 3: Industry best practice

**Score: ___/3**

### □ Fundamentality (0-3 points)
- [ ] 0: Advanced/niche concept
- [ ] 1: Intermediate concept
- [ ] 2: Important concept
- [ ] 3: Fundamental/essential

**Score: ___/3**

### □ Uniqueness (0-2 points)
- [ ] 0: Standard boilerplate
- [ ] 1: Interesting implementation
- [ ] 2: Unique/innovative approach

**Score: ___/2**

### □ Junior Dev Value (0-3 points)
- [ ] 0: Not relevant for juniors
- [ ] 1: Nice to know
- [ ] 2: Should know
- [ ] 3: Must know

**Score: ___/3**

**Total Teaching Value: ___/14**

**Decision: Teach if score ≥ 7**

---

## Phase 3: Placement & Structure

### □ Prerequisites
List concepts that must be learned first:
1. ________________
2. ________________
3. ________________

### □ Skill Level
- [ ] Beginner (no prior knowledge needed)
- [ ] Intermediate (requires basic understanding)
- [ ] Advanced (requires deep knowledge)

### □ Time Estimate
- [ ] 15 minutes (quick concept)
- [ ] 30 minutes (standard lesson)
- [ ] 45 minutes (complex topic)
- [ ] 60+ minutes (major topic)

### □ Module Assignment
Which major topic does this belong to?
- Module: ________________
- Lesson order: _____ of _____

### □ Learning Objectives
What should students be able to do after this lesson?
1. ________________
2. ________________
3. ________________

---

## Phase 4: Content Creation

### □ Explanation
Write a clear explanation that:
- [ ] Explains what it does (cite code)
- [ ] Explains why it exists (cite docs/git)
- [ ] Explains how it works (cite implementation)
- [ ] Uses simple language
- [ ] Avoids jargon (or defines it)

**Draft explanation:**
________________

**Evidence citations:**
- Code: ________________
- Docs: ________________
- Git: ________________

### □ Working Example
Create a minimal example that:
- [ ] Is extracted from actual codebase
- [ ] Runs without errors
- [ ] Demonstrates the concept clearly
- [ ] Includes necessary imports/setup
- [ ] Is as simple as possible

**Example code:**
```
________________
```

**Tested:** [ ] Yes [ ] No

### □ Exercise
Design an exercise that:
- [ ] Reinforces the concept
- [ ] Has clear requirements
- [ ] Has a verifiable solution
- [ ] Builds on the example
- [ ] Is achievable in estimated time

**Exercise description:**
________________

**Solution:**
```
________________
```

**Tested:** [ ] Yes [ ] No

### □ Validation Tests
Create tests that:
- [ ] Verify correct implementation
- [ ] Check edge cases
- [ ] Provide helpful feedback
- [ ] Run automatically
- [ ] Are based on actual codebase tests

**Test code:**
```
________________
```

### □ Hints & Support
Provide hints that:
- [ ] Guide without giving away solution
- [ ] Are progressively disclosed
- [ ] Address common mistakes
- [ ] Link to relevant resources
- [ ] Build confidence

**Hints:**
1. ________________
2. ________________
3. ________________

---

## Phase 5: Quality Assurance

### □ Accuracy Check
- [ ] Explanation matches code behavior
- [ ] Example actually works
- [ ] Exercise solution is correct
- [ ] Tests validate properly
- [ ] No hallucinated information

**Verified by:** ________________

### □ Clarity Check
- [ ] Language is simple and clear
- [ ] Jargon is explained
- [ ] Examples are easy to follow
- [ ] Instructions are unambiguous
- [ ] Junior dev can understand

**Reviewed by:** ________________

### □ Completeness Check
- [ ] All prerequisites listed
- [ ] All concepts explained
- [ ] All code is runnable
- [ ] All tests pass
- [ ] All resources linked

**Checklist complete:** [ ] Yes [ ] No

### □ Beta Test
- [ ] Tested with real junior dev
- [ ] Completion time recorded: _____ minutes
- [ ] Feedback collected
- [ ] Issues identified
- [ ] Improvements made

**Beta tester:** ________________
**Feedback:** ________________

### □ Alignment Check
Does this align with course-platform-research.md?
- [ ] 80/20 hands-on/theory split
- [ ] Progressive difficulty
- [ ] Immediate feedback (automated tests)
- [ ] Real-world context (from actual codebase)
- [ ] Multiple attempts allowed

---

## Phase 6: Integration

### □ Course Structure
Where does this fit?
```
Course: ________________
  └─ Module: ________________
      └─ Lesson: ________________
          ├─ Theory (10%)
          ├─ Example (10%)
          ├─ Exercise (60%)
          └─ Tests (20%)
```

### □ Dependencies
What must be completed before this?
- Previous lesson: ________________
- Prerequisites: ________________

### □ Next Steps
What comes after this?
- Next lesson: ________________
- Related topics: ________________

### □ Resources
What additional resources are needed?
- [ ] Documentation links
- [ ] External tutorials
- [ ] Video explanations
- [ ] Cheat sheets
- [ ] Reference materials

---

## Phase 7: Maintenance

### □ Version Tracking
- [ ] Linked to codebase version: ________________
- [ ] Git commit hash: ________________
- [ ] Last updated: ________________

### □ Change Detection
- [ ] Automated monitoring set up
- [ ] Update triggers defined
- [ ] Notification system configured

### □ Feedback Loop
- [ ] Metrics tracked (completion rate, time, etc.)
- [ ] Student feedback collected
- [ ] Improvement backlog maintained
- [ ] Regular review scheduled

---

## Final Checklist

Before publishing this lesson:

- [ ] All evidence is cited
- [ ] All code is tested
- [ ] All explanations are accurate
- [ ] All exercises are validated
- [ ] Beta tested with junior dev
- [ ] Aligned with course structure
- [ ] Integrated into learning path
- [ ] Maintenance plan in place

**Approved by:** ________________
**Date:** ________________

---

## Anti-Hallucination Verification

For each statement in your lesson, ask:

1. **"Can I cite evidence for this?"**
   - [ ] Yes → Include citation
   - [ ] No → Remove or mark as inference

2. **"Is this fact or inference?"**
   - [ ] Fact → Cite source
   - [ ] Inference → Mark clearly as interpretation

3. **"Does this match the tests?"**
   - [ ] Yes → Good
   - [ ] No → Revise understanding

4. **"Is this consistent across the codebase?"**
   - [ ] Yes → Good
   - [ ] No → Investigate discrepancy

5. **"Would a junior dev understand this?"**
   - [ ] Yes → Good
   - [ ] No → Simplify

---

## Example: Completed Checklist

### Concept: useAuth Custom Hook

#### Phase 1: Understanding ✅
- Code: `src/hooks/useAuth.ts` (lines 1-45)
- Tests: `src/hooks/useAuth.test.ts` (12 tests, 95% coverage)
- Docs: JSDoc says "Manages authentication state"
- Git: Commit abc123 "Centralize auth logic"
- Used by: 12 components

#### Phase 2: Teaching Value ✅
- Reusability: 3/3 (universal pattern)
- Best Practice: 3/3 (React best practice)
- Fundamentality: 2/3 (intermediate)
- Uniqueness: 1/2 (well-implemented)
- Junior Dev: 3/3 (essential)
- **Total: 12/14 → TEACH**

#### Phase 3: Placement ✅
- Prerequisites: React basics, useState, useEffect
- Skill Level: Intermediate
- Time: 45 minutes
- Module: React Hooks
- Order: Lesson 4 of 8

#### Phase 4: Content ✅
- Explanation: Written with citations
- Example: Extracted and tested
- Exercise: Designed and validated
- Tests: 5 automated tests
- Hints: 3 progressive hints

#### Phase 5: Quality ✅
- Accuracy: Verified by senior dev
- Clarity: Reviewed by tech writer
- Completeness: All items checked
- Beta test: Completed in 42 min, positive feedback
- Alignment: Matches all criteria

#### Phase 6: Integration ✅
- Structure: Course → React → Hooks → useAuth
- Dependencies: Lessons 1-3 required
- Next: Lesson 5 (Advanced Hooks)
- Resources: React docs linked

#### Phase 7: Maintenance ✅
- Version: v1.0.0, commit abc123
- Monitoring: Automated
- Feedback: Tracked
- Review: Quarterly

**Status: APPROVED FOR PUBLICATION** ✅

---

Use this checklist for EVERY concept to ensure quality, accuracy, and effectiveness!
