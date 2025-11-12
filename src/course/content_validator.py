"""Content Validator - Validates course content quality and completeness."""

import ast
import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from .models import CourseOutline, Module, Lesson, Exercise, LessonContent


@dataclass
class ValidationIssue:
    """Represents a validation issue found in course content."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'learning_objectives', 'code_examples', 'syntax', 'links'
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report with all issues found."""
    total_issues: int
    errors: int
    warnings: int
    info: int
    issues: List[ValidationIssue] = field(default_factory=list)
    passed: bool = True
    
    def add_issue(self, issue: ValidationIssue):
        """Add an issue to the report."""
        self.issues.append(issue)
        self.total_issues += 1
        
        if issue.severity == 'error':
            self.errors += 1
            self.passed = False
        elif issue.severity == 'warning':
            self.warnings += 1
        elif issue.severity == 'info':
            self.info += 1
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary format."""
        return {
            'total_issues': self.total_issues,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'passed': self.passed,
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'message': issue.message,
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'suggestion': issue.suggestion
                }
                for issue in self.issues
            ]
        }


class ContentValidator:
    """Validates course content for quality and completeness.
    
    This class implements Requirements 13.1, 13.2, 13.3, 13.4, 13.5:
    - Validates each lesson has learning objectives
    - Validates each lesson has code examples
    - Validates exercise starter code syntax
    - Validates internal links
    - Generates validation report with issues
    """
    
    def __init__(self):
        """Initialize the content validator."""
        self.report = ValidationReport(
            total_issues=0,
            errors=0,
            warnings=0,
            info=0
        )
    
    def validate_course(self, course: CourseOutline) -> ValidationReport:
        """Validate complete course content.
        
        This is the main validation method that checks all aspects of the course.
        Implements Requirements 13.1, 13.2, 13.3, 13.4, 13.5.
        
        Args:
            course: CourseOutline to validate
            
        Returns:
            ValidationReport with all issues found
        """
        # Reset report
        self.report = ValidationReport(
            total_issues=0,
            errors=0,
            warnings=0,
            info=0
        )
        
        # Validate course structure
        self._validate_course_structure(course)
        
        # Validate each module
        for module in course.modules:
            self._validate_module(module, course)
        
        # Validate internal links across all lessons
        self._validate_internal_links(course)
        
        return self.report
    
    def validate_lesson(self, lesson: Lesson) -> ValidationReport:
        """Validate a single lesson.
        
        Args:
            lesson: Lesson to validate
            
        Returns:
            ValidationReport with issues found in this lesson
        """
        # Reset report
        self.report = ValidationReport(
            total_issues=0,
            errors=0,
            warnings=0,
            info=0
        )
        
        self._validate_lesson_structure(lesson)
        
        return self.report
    
    # ========== Requirement 13.1: Validate Learning Objectives ==========
    
    def _validate_learning_objectives(self, lesson: Lesson):
        """Validate that lesson has learning objectives.
        
        Implements Requirement 13.1: Validates each lesson has at least one
        learning objective.
        
        Args:
            lesson: Lesson to validate
        """
        if not lesson.learning_objectives:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='learning_objectives',
                message=f"Lesson '{lesson.title}' has no learning objectives",
                file_path=lesson.file_path,
                suggestion="Add at least one learning objective using action verbs (understand, implement, apply, analyze)"
            ))
        elif len(lesson.learning_objectives) < 2:
            self.report.add_issue(ValidationIssue(
                severity='warning',
                category='learning_objectives',
                message=f"Lesson '{lesson.title}' has only {len(lesson.learning_objectives)} learning objective",
                file_path=lesson.file_path,
                suggestion="Consider adding 2-5 learning objectives for better clarity"
            ))
        elif len(lesson.learning_objectives) > 5:
            self.report.add_issue(ValidationIssue(
                severity='warning',
                category='learning_objectives',
                message=f"Lesson '{lesson.title}' has {len(lesson.learning_objectives)} learning objectives (recommended: 3-5)",
                file_path=lesson.file_path,
                suggestion="Consider consolidating objectives to focus on key learning outcomes"
            ))
        
        # Validate objective quality
        action_verbs = {
            'understand', 'implement', 'apply', 'analyze', 'create', 'design',
            'develop', 'build', 'explain', 'demonstrate', 'use', 'write',
            'identify', 'compare', 'evaluate', 'master', 'learn', 'practice'
        }
        
        for obj in lesson.learning_objectives:
            first_word = obj.split()[0].lower() if obj.split() else ''
            if first_word not in action_verbs:
                self.report.add_issue(ValidationIssue(
                    severity='info',
                    category='learning_objectives',
                    message=f"Learning objective in '{lesson.title}' doesn't start with action verb: '{obj}'",
                    file_path=lesson.file_path,
                    suggestion=f"Start with action verbs like: {', '.join(list(action_verbs)[:5])}"
                ))
    
    # ========== Requirement 13.2: Validate Code Examples ==========
    
    def _validate_code_examples(self, lesson: Lesson):
        """Validate that lesson has code examples.
        
        Implements Requirement 13.2: Validates each lesson has at least one
        code example.
        
        Args:
            lesson: Lesson to validate
        """
        if not lesson.content:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='code_examples',
                message=f"Lesson '{lesson.title}' has no content",
                file_path=lesson.file_path,
                suggestion="Generate lesson content with code examples"
            ))
            return
        
        if not lesson.content.code_example:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='code_examples',
                message=f"Lesson '{lesson.title}' has no code example",
                file_path=lesson.file_path,
                suggestion="Add at least one code example to demonstrate concepts"
            ))
        elif not lesson.content.code_example.code or len(lesson.content.code_example.code.strip()) == 0:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='code_examples',
                message=f"Lesson '{lesson.title}' has empty code example",
                file_path=lesson.file_path,
                suggestion="Ensure code example contains actual code"
            ))
        else:
            # Validate code example quality
            code = lesson.content.code_example.code
            lines = code.split('\n')
            
            # Check if code is too short
            if len(lines) < 5:
                self.report.add_issue(ValidationIssue(
                    severity='warning',
                    category='code_examples',
                    message=f"Code example in '{lesson.title}' is very short ({len(lines)} lines)",
                    file_path=lesson.file_path,
                    suggestion="Consider adding more context or a more complete example"
                ))
            
            # Check if code is too long (Requirement 7.2: max 50 lines)
            if len(lines) > 50:
                self.report.add_issue(ValidationIssue(
                    severity='warning',
                    category='code_examples',
                    message=f"Code example in '{lesson.title}' is very long ({len(lines)} lines, recommended: ≤50)",
                    file_path=lesson.file_path,
                    suggestion="Consider breaking into smaller examples or truncating less important sections"
                ))
            
            # Check if language is specified
            if not lesson.content.code_example.language:
                self.report.add_issue(ValidationIssue(
                    severity='warning',
                    category='code_examples',
                    message=f"Code example in '{lesson.title}' has no language specified",
                    file_path=lesson.file_path,
                    suggestion="Specify programming language for proper syntax highlighting"
                ))
    
    # ========== Requirement 13.3: Validate Exercise Starter Code Syntax ==========
    
    def _validate_exercise_syntax(self, exercise: Exercise, lesson: Lesson):
        """Validate exercise starter code syntax.
        
        Implements Requirement 13.3: Validates exercise starter code is
        syntactically valid.
        
        Args:
            exercise: Exercise to validate
            lesson: Parent lesson (for context)
        """
        if not exercise.starter_code:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='syntax',
                message=f"Exercise '{exercise.title}' in lesson '{lesson.title}' has no starter code",
                file_path=lesson.file_path,
                suggestion="Add starter code with TODO comments for students"
            ))
            return
        
        # Determine language from lesson content
        language = 'python'  # Default
        if lesson.content and lesson.content.code_example:
            language = lesson.content.code_example.language
        
        # Validate syntax based on language
        if language == 'python':
            self._validate_python_syntax(
                exercise.starter_code,
                f"Exercise '{exercise.title}' starter code",
                lesson.file_path
            )
            
            # Also validate solution code
            if exercise.solution_code:
                self._validate_python_syntax(
                    exercise.solution_code,
                    f"Exercise '{exercise.title}' solution code",
                    lesson.file_path
                )
        elif language in ['javascript', 'typescript', 'jsx', 'tsx']:
            self._validate_javascript_syntax(
                exercise.starter_code,
                f"Exercise '{exercise.title}' starter code",
                lesson.file_path
            )
        # For other languages, do basic validation
        else:
            self._validate_basic_syntax(
                exercise.starter_code,
                f"Exercise '{exercise.title}' starter code",
                lesson.file_path
            )
    
    def _validate_python_syntax(self, code: str, context: str, file_path: str):
        """Validate Python code syntax.
        
        Args:
            code: Python code to validate
            context: Context description for error messages
            file_path: File path for error reporting
        """
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='syntax',
                message=f"{context} has Python syntax error: {e.msg}",
                file_path=file_path,
                line_number=e.lineno,
                suggestion=f"Fix syntax error at line {e.lineno}: {e.text.strip() if e.text else 'check code'}"
            ))
        except Exception as e:
            self.report.add_issue(ValidationIssue(
                severity='warning',
                category='syntax',
                message=f"{context} could not be parsed: {str(e)}",
                file_path=file_path,
                suggestion="Verify code syntax is valid"
            ))
    
    def _validate_javascript_syntax(self, code: str, context: str, file_path: str):
        """Validate JavaScript/TypeScript code syntax (basic checks).
        
        Args:
            code: JavaScript code to validate
            context: Context description for error messages
            file_path: File path for error reporting
        """
        # Basic syntax checks for JavaScript
        # Check for unmatched braces
        brace_count = code.count('{') - code.count('}')
        if brace_count != 0:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='syntax',
                message=f"{context} has unmatched braces ({brace_count} {'extra opening' if brace_count > 0 else 'extra closing'})",
                file_path=file_path,
                suggestion="Ensure all opening braces have matching closing braces"
            ))
        
        # Check for unmatched parentheses
        paren_count = code.count('(') - code.count(')')
        if paren_count != 0:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='syntax',
                message=f"{context} has unmatched parentheses",
                file_path=file_path,
                suggestion="Ensure all opening parentheses have matching closing parentheses"
            ))
        
        # Check for unmatched brackets
        bracket_count = code.count('[') - code.count(']')
        if bracket_count != 0:
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='syntax',
                message=f"{context} has unmatched brackets",
                file_path=file_path,
                suggestion="Ensure all opening brackets have matching closing brackets"
            ))
    
    def _validate_basic_syntax(self, code: str, context: str, file_path: str):
        """Validate basic code syntax (language-agnostic checks).
        
        Args:
            code: Code to validate
            context: Context description for error messages
            file_path: File path for error reporting
        """
        # Check for common syntax issues
        lines = code.split('\n')
        
        # Check if code is empty
        if not code.strip():
            self.report.add_issue(ValidationIssue(
                severity='error',
                category='syntax',
                message=f"{context} is empty",
                file_path=file_path,
                suggestion="Add code content"
            ))
            return
        
        # Check for balanced braces/brackets/parens
        for char_pair in [('{', '}'), ('(', ')'), ('[', ']')]:
            open_char, close_char = char_pair
            if code.count(open_char) != code.count(close_char):
                self.report.add_issue(ValidationIssue(
                    severity='warning',
                    category='syntax',
                    message=f"{context} may have unmatched {open_char}{close_char}",
                    file_path=file_path,
                    suggestion=f"Check that all {open_char} have matching {close_char}"
                ))
    
    # ========== Requirement 13.4: Validate Internal Links ==========
    
    def _validate_internal_links(self, course: CourseOutline):
        """Validate internal links in course content.
        
        Implements Requirement 13.4: Validates all internal links in generated
        content are valid.
        
        Args:
            course: CourseOutline to validate
        """
        # Build a set of valid lesson IDs and titles
        valid_lesson_ids: Set[str] = set()
        valid_lesson_titles: Set[str] = set()
        lesson_map: Dict[str, Lesson] = {}
        
        for module in course.modules:
            for lesson in module.lessons:
                valid_lesson_ids.add(lesson.lesson_id)
                valid_lesson_titles.add(lesson.title.lower())
                lesson_map[lesson.lesson_id] = lesson
        
        # Check prerequisite links
        for module in course.modules:
            for lesson in module.lessons:
                for prereq_id in lesson.prerequisites:
                    if prereq_id not in valid_lesson_ids:
                        self.report.add_issue(ValidationIssue(
                            severity='error',
                            category='links',
                            message=f"Lesson '{lesson.title}' references invalid prerequisite: {prereq_id}",
                            file_path=lesson.file_path,
                            suggestion="Ensure prerequisite lesson ID exists in the course"
                        ))
                
                # Check for circular prerequisites
                if self._has_circular_prerequisites(lesson, lesson_map, set()):
                    self.report.add_issue(ValidationIssue(
                        severity='error',
                        category='links',
                        message=f"Lesson '{lesson.title}' has circular prerequisite dependencies",
                        file_path=lesson.file_path,
                        suggestion="Remove circular dependencies in prerequisites"
                    ))
                
                # Check content for markdown links
                if lesson.content:
                    self._validate_markdown_links(
                        lesson.content.introduction,
                        f"Lesson '{lesson.title}' introduction",
                        lesson.file_path,
                        valid_lesson_titles
                    )
                    self._validate_markdown_links(
                        lesson.content.explanation,
                        f"Lesson '{lesson.title}' explanation",
                        lesson.file_path,
                        valid_lesson_titles
                    )
                    self._validate_markdown_links(
                        lesson.content.walkthrough,
                        f"Lesson '{lesson.title}' walkthrough",
                        lesson.file_path,
                        valid_lesson_titles
                    )
                    self._validate_markdown_links(
                        lesson.content.summary,
                        f"Lesson '{lesson.title}' summary",
                        lesson.file_path,
                        valid_lesson_titles
                    )
    
    def _has_circular_prerequisites(
        self,
        lesson: Lesson,
        lesson_map: Dict[str, Lesson],
        visited: Set[str]
    ) -> bool:
        """Check if lesson has circular prerequisite dependencies.
        
        Args:
            lesson: Lesson to check
            lesson_map: Map of lesson IDs to lessons
            visited: Set of visited lesson IDs
            
        Returns:
            True if circular dependency detected
        """
        if lesson.lesson_id in visited:
            return True
        
        visited.add(lesson.lesson_id)
        
        for prereq_id in lesson.prerequisites:
            if prereq_id in lesson_map:
                prereq_lesson = lesson_map[prereq_id]
                if self._has_circular_prerequisites(prereq_lesson, lesson_map, visited.copy()):
                    return True
        
        return False
    
    def _validate_markdown_links(
        self,
        content: str,
        context: str,
        file_path: str,
        valid_titles: Set[str]
    ):
        """Validate markdown links in content.
        
        Args:
            content: Content to check for links
            context: Context description for error messages
            file_path: File path for error reporting
            valid_titles: Set of valid lesson titles
        """
        # Find markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.finditer(link_pattern, content)
        
        for match in matches:
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Check internal links (relative paths or #anchors)
            if link_url.startswith('#') or (not link_url.startswith('http://') and not link_url.startswith('https://')):
                # Check if it references a valid lesson
                link_lower = link_url.lower().replace('-', ' ').replace('_', ' ').strip('#')
                
                # Skip if it's a valid anchor or file reference
                if link_url.startswith('#') or '.' in link_url:
                    continue
                
                # Check if it matches a lesson title
                if link_lower not in valid_titles:
                    self.report.add_issue(ValidationIssue(
                  