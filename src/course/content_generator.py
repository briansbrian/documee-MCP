"""Lesson Content Generator - Creates educational content from code examples."""

from typing import List, Dict, Optional
from src.models import FileAnalysis, DetectedPattern, FunctionInfo, ClassInfo
from .models import LessonContent, CodeExample, CodeHighlight
from .config import CourseConfig
from .performance_monitor import get_monitor


class LessonContentGenerator:
    """Generates educational lesson content from file analysis results.
    
    This class implements Requirements 2.1, 2.2, 2.3, 2.4, 2.5:
    - Extracts code examples with syntax highlighting
    - Generates 3-5 learning objectives from patterns
    - Adds inline comments to clarify complex logic
    - Structures lessons with introduction, explanation, walkthrough, summary
    - Generates content in Markdown format
    """
    
    def __init__(self, config: CourseConfig, course_cache=None):
        """Initialize the lesson content generator.
        
        Args:
            config: Course generation configuration
            course_cache: Optional CourseCacheManager for caching
        """
        self.config = config
        self.course_cache = course_cache
    
    async def generate_lesson_content(self, file_analysis: FileAnalysis) -> LessonContent:
        """Generate complete lesson content from file analysis.
        
        This is the main method that orchestrates content generation.
        Implements Requirements 2.1, 2.2, 2.3, 2.4, 2.5.
        
        Args:
            file_analysis: Analysis results for the source file
            
        Returns:
            Complete LessonContent with all sections
        """
        monitor = get_monitor()
        
        with monitor.measure("lesson_content", file_path=file_analysis.file_path):
            # Check cache first
            if self.course_cache:
                cached = await self.course_cache.get_lesson_content(file_analysis.file_path)
                if cached and "data" in cached:
                    import logging
                    logging.getLogger(__name__).info(f"Using cached lesson content for {file_analysis.file_path}")
                    return self._deserialize_lesson_content(cached["data"])
            
            # 1. Extract code example (Req 2.1)
            code_example = self.extract_code_example(file_analysis)
            
            # 2. Generate learning objectives from patterns (Req 2.2)
            objectives = self.generate_objectives(file_analysis)
            
            # 3. Create introduction (Req 2.4)
            introduction = self.generate_introduction(file_analysis, objectives)
            
            # 4. Generate explanation (Req 2.4)
            explanation = self.generate_explanation(file_analysis)
            
            # 5. Create code walkthrough with annotations (Req 2.3, 2.4)
            walkthrough = self.generate_walkthrough(code_example, file_analysis)
            
            # 6. Generate summary (Req 2.4)
            summary = self.generate_summary(objectives, file_analysis)
            
            # 7. Generate further reading suggestions
            further_reading = self._generate_further_reading(file_analysis)
            
            lesson_content = LessonContent(
                introduction=introduction,
                explanation=explanation,
                code_example=code_example,
                walkthrough=walkthrough,
                summary=summary,
                further_reading=further_reading
            )
            
            # Cache the result
            if self.course_cache:
                serialized = self._serialize_lesson_content(lesson_content)
                await self.course_cache.set_lesson_content(file_analysis.file_path, serialized)
            
            return lesson_content
    
    def extract_code_example(self, file_analysis: FileAnalysis) -> CodeExample:
        """Extract relevant code example from file analysis.
        
        Implements Requirement 2.1: Extracts code with syntax highlighting.
        
        Args:
            file_analysis: Analysis results for the source file
            
        Returns:
            CodeExample with code, language, and metadata
        """
        # Read the source code
        code = self._read_file_content(file_analysis.file_path)
        
        # Determine language from file extension
        language = self._detect_language(file_analysis.file_path)
        
        # Extract filename
        import os
        filename = os.path.basename(file_analysis.file_path)
        
        # Create highlights for important sections
        highlights = self._create_highlights(file_analysis)
        
        # Generate annotations for complex code
        annotations = self._generate_annotations(file_analysis)
        
        return CodeExample(
            code=code,
            language=language,
            filename=filename,
            highlights=highlights,
            annotations=annotations
        )
    
    def generate_objectives(self, file_analysis: FileAnalysis) -> List[str]:
        """Generate learning objectives from patterns and symbols.
        
        Implements Requirement 2.2: Generates 3-5 learning objectives based on
        detected patterns and concepts.
        
        Args:
            file_analysis: Analysis results for the source file
            
        Returns:
            List of 3-5 learning objectives using action verbs
        """
        objectives = []
        
        # Prioritize patterns by focus (Task 13.3)
        patterns = self._prioritize_patterns_by_focus(file_analysis.patterns)
        
        # Generate objectives from patterns
        for pattern in patterns[:3]:  # Top 3 patterns
            objective = self._pattern_to_objective(pattern)
            if objective:
                objectives.append(objective)
        
        # Generate objectives from functions/classes
        if file_analysis.symbol_info.classes:
            objectives.append(
                f"Implement {file_analysis.symbol_info.classes[0].name} class structure"
            )
        elif file_analysis.symbol_info.functions:
            # Focus on most complex function
            complex_funcs = [
                f for f in file_analysis.symbol_info.functions
                if f.complexity > 5
            ]
            if complex_funcs:
                func = complex_funcs[0]
                objectives.append(f"Analyze {func.name} function implementation")
        
        # Add objective based on complexity
        if file_analysis.complexity_metrics.avg_complexity > 5:
            objectives.append("Apply techniques for managing code complexity")
        
        # Add objective based on documentation
        if file_analysis.documentation_coverage > 0.7:
            objectives.append("Understand documentation best practices")
        
        # Ensure we have 3-5 objectives (Req 2.2)
        if len(objectives) < 3:
            objectives.append("Understand the code structure and organization")
        if len(objectives) < 3:
            objectives.append("Apply the concepts in your own projects")
        
        # Limit to 5 objectives
        return objectives[:5]
    
    def generate_introduction(
        self,
        file_analysis: FileAnalysis,
        objectives: List[str]
    ) -> str:
        """Generate lesson introduction.
        
        Implements Requirement 2.4: Creates introduction section.
        
        Args:
            file_analysis: Analysis results for the source file
            objectives: Learning objectives for the lesson
            
        Returns:
            Introduction text in Markdown format
        """
        parts = []
        
        # Start with teaching value explanation if available
        if file_analysis.teaching_value.explanation:
            parts.append(file_analysis.teaching_value.explanation)
        else:
            parts.append(
                "This lesson explores a practical code example that demonstrates "
                "important programming concepts."
            )
        
        # Add context about what patterns are demonstrated
        if file_analysis.patterns:
            pattern_names = [
                p.pattern_type.replace('_', ' ').title()
                for p in file_analysis.patterns[:3]
            ]
            parts.append(
                f"\n\nYou'll learn about {', '.join(pattern_names)} "
                f"through hands-on code analysis."
            )
        
        # Add what students will be able to do
        if objectives:
            parts.append(
                f"\n\nBy the end of this lesson, you'll be able to:\n"
            )
            for obj in objectives:
                parts.append(f"- {obj}")
        
        return "".join(parts)

    
    def generate_explanation(self, file_analysis: FileAnalysis) -> str:
        """Generate explanation of the code and concepts.
        
        Implements Requirements 2.4, 7.1: Creates explanation section using
        simple language appropriate for target difficulty level.
        
        Args:
            file_analysis: Analysis results for the source file
            
        Returns:
            Explanation text in Markdown format
        """
        parts = []
        
        # Add audience-appropriate introduction (Task 13.2)
        if self.config.target_audience == "beginner":
            parts.append("## Understanding the Code\n\n")
            parts.append("Let's break down this code step by step.\n\n")
        elif self.config.target_audience == "advanced":
            parts.append("## Technical Overview\n\n")
        else:
            parts.append("## What This Code Does\n\n")
        
        # Explain the overall purpose
        if self.config.target_audience != "beginner":
            # Skip redundant header for non-beginners
            pass
        else:
            parts.append("### Purpose\n\n")
        
        if file_analysis.symbol_info.classes:
            # Explain class-based code
            for cls in file_analysis.symbol_info.classes[:2]:  # Top 2 classes
                parts.append(f"The `{cls.name}` class ")
                if cls.docstring:
                    # Use first sentence of docstring
                    first_sentence = cls.docstring.split('.')[0] + '.'
                    parts.append(first_sentence.lower())
                else:
                    parts.append(
                        f"provides {len(cls.methods)} methods for "
                        f"implementing its functionality."
                    )
                parts.append("\n\n")
        
        elif file_analysis.symbol_info.functions:
            # Explain function-based code
            parts.append("This file contains several functions:\n\n")
            for func in file_analysis.symbol_info.functions[:3]:  # Top 3 functions
                parts.append(f"- **{func.name}**: ")
                if func.docstring:
                    first_sentence = func.docstring.split('.')[0] + '.'
                    parts.append(first_sentence)
                else:
                    parts.append(f"Takes {len(func.parameters)} parameter(s)")
                parts.append("\n")
        
        # Explain key patterns
        if file_analysis.patterns:
            parts.append("\n## Key Patterns\n\n")
            for pattern in file_analysis.patterns[:3]:
                pattern_name = pattern.pattern_type.replace('_', ' ').title()
                parts.append(f"### {pattern_name}\n\n")
                
                # Explain the pattern
                pattern_explanation = self._explain_pattern(pattern)
                parts.append(pattern_explanation)
                parts.append("\n\n")
        
        # Explain complexity if high
        if file_analysis.complexity_metrics.avg_complexity > 5:
            parts.append("## Complexity Considerations\n\n")
            parts.append(
                f"This code has an average complexity of "
                f"{file_analysis.complexity_metrics.avg_complexity:.1f}. "
            )
            
            if file_analysis.complexity_metrics.high_complexity_functions:
                parts.append(
                    f"The most complex functions are: "
                    f"{', '.join(file_analysis.complexity_metrics.high_complexity_functions[:3])}. "
                )
            
            parts.append(
                "Pay special attention to how the code manages this complexity "
                "through clear structure and organization.\n\n"
            )
        
        return "".join(parts)
    
    def generate_walkthrough(
        self,
        code_example: CodeExample,
        file_analysis: FileAnalysis
    ) -> str:
        """Generate step-by-step code walkthrough.
        
        Implements Requirements 2.3, 2.4: Creates walkthrough with code annotations.
        
        Args:
            code_example: The code example to walk through
            file_analysis: Analysis results for the source file
            
        Returns:
            Walkthrough text in Markdown format
        """
        parts = []
        
        parts.append("## Code Walkthrough\n\n")
        parts.append("Let's walk through the code step by step:\n\n")
        
        # Walk through classes
        if file_analysis.symbol_info.classes:
            for cls in file_analysis.symbol_info.classes:
                parts.append(f"### {cls.name} Class\n\n")
                
                if cls.docstring:
                    parts.append(f"{cls.docstring}\n\n")
                
                # Explain inheritance
                if cls.base_classes:
                    parts.append(
                        f"This class inherits from: {', '.join(cls.base_classes)}\n\n"
                    )
                
                # Walk through methods
                if cls.methods:
                    parts.append("**Key Methods:**\n\n")
                    for method in cls.methods[:5]:  # Top 5 methods
                        parts.append(f"- `{method.name}(")
                        parts.append(", ".join(method.parameters))
                        parts.append(")`")
                        
                        if method.docstring:
                            # Use first line of docstring
                            first_line = method.docstring.split('\n')[0]
                            parts.append(f": {first_line}")
                        
                        parts.append("\n")
                    parts.append("\n")
        
        # Walk through standalone functions
        standalone_funcs = [
            f for f in file_analysis.symbol_info.functions
            if not any(f in cls.methods for cls in file_analysis.symbol_info.classes)
        ]
        
        if standalone_funcs:
            parts.append("### Functions\n\n")
            for func in standalone_funcs[:5]:  # Top 5 functions
                parts.append(f"**{func.name}**\n\n")
                
                if func.docstring:
                    parts.append(f"{func.docstring}\n\n")
                
                # Explain parameters
                if func.parameters:
                    parts.append("Parameters:\n")
                    for param in func.parameters:
                        parts.append(f"- `{param}`\n")
                    parts.append("\n")
                
                # Note complexity if high
                if func.complexity > 5:
                    parts.append(
                        f"*Note: This function has complexity {func.complexity}, "
                        f"so pay attention to its control flow.*\n\n"
                    )
        
        # Add annotations from code example
        if code_example.annotations:
            parts.append("### Important Code Sections\n\n")
            for line_num, annotation in sorted(code_example.annotations.items())[:5]:
                parts.append(f"**Line {line_num}**: {annotation}\n\n")
        
        return "".join(parts)
    
    def generate_summary(
        self,
        objectives: List[str],
        file_analysis: FileAnalysis
    ) -> str:
        """Generate lesson summary.
        
        Implements Requirement 2.4: Creates summary section for lesson recap.
        
        Args:
            objectives: Learning objectives for the lesson
            file_analysis: Analysis results for the source file
            
        Returns:
            Summary text in Markdown format
        """
        parts = []
        
        parts.append("## Summary\n\n")
        parts.append("In this lesson, you learned:\n\n")
        
        # Recap objectives
        for obj in objectives:
            parts.append(f"- {obj}\n")
        
        parts.append("\n")
        
        # Highlight key takeaways
        parts.append("### Key Takeaways\n\n")
        
        # Takeaway from patterns
        if file_analysis.patterns:
            pattern_names = [
                p.pattern_type.replace('_', ' ')
                for p in file_analysis.patterns[:2]
            ]
            parts.append(
                f"- Understanding {' and '.join(pattern_names)} "
                f"will help you write better code\n"
            )
        
        # Takeaway from complexity
        if file_analysis.complexity_metrics.avg_complexity > 5:
            parts.append(
                "- Managing complexity through clear structure is essential "
                "for maintainable code\n"
            )
        
        # Takeaway from documentation
        if file_analysis.documentation_coverage > 0.7:
            parts.append(
                "- Good documentation makes code easier to understand and maintain\n"
            )
        
        # Generic takeaway
        parts.append(
            "- Practice implementing these concepts in your own projects\n"
        )
        
        parts.append("\n")
        
        # Next steps
        parts.append("### Next Steps\n\n")
        parts.append(
            "Try modifying the code to experiment with different approaches. "
            "Complete the exercises to reinforce your understanding.\n"
        )
        
        return "".join(parts)
    
    # ========== Helper Methods ==========
    
    def _read_file_content(self, file_path: str) -> str:
        """Read the content of a source file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limit to max_code_lines if configured (Req 7.2)
            if self.config.max_code_lines:
                lines = content.split('\n')
                if len(lines) > self.config.max_code_lines:
                    # Take first max_code_lines
                    content = '\n'.join(lines[:self.config.max_code_lines])
                    content += f"\n\n# ... ({len(lines) - self.config.max_code_lines} more lines)"
            
            return content
        except Exception as e:
            return f"# Error reading file: {e}"
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Language identifier for syntax highlighting
        """
        import os
        ext = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.sh': 'bash',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.md': 'markdown',
        }
        
        return language_map.get(ext, 'text')
    
    def _create_highlights(self, file_analysis: FileAnalysis) -> List[CodeHighlight]:
        """Create code highlights for important sections.
        
        Implements Requirement 7.2: Creates code highlights for important sections.
        
        Args:
            file_analysis: Analysis results for the source file
            
        Returns:
            List of CodeHighlight objects
        """
        highlights = []
        
        # Highlight complex functions
        for func in file_analysis.complexity_metrics.high_complexity_functions[:3]:
            # Find the function in symbol info
            func_info = next(
                (f for f in file_analysis.symbol_info.functions if f.name == func),
                None
            )
            if func_info:
                highlights.append(CodeHighlight(
                    start_line=func_info.start_line,
                    end_line=func_info.end_line,
                    description=f"Complex function: {func} (complexity {func_info.complexity})"
                ))
        
        # Highlight pattern locations
        for pattern in file_analysis.patterns[:3]:
            if pattern.line_numbers:
                start = min(pattern.line_numbers)
                end = max(pattern.line_numbers)
                pattern_name = pattern.pattern_type.replace('_', ' ').title()
                highlights.append(CodeHighlight(
                    start_line=start,
                    end_line=end,
                    description=f"{pattern_name} pattern"
                ))
        
        return highlights
    
    def _generate_annotations(self, file_analysis: FileAnalysis) -> Dict[int, str]:
        """Generate line-by-line annotations for complex code.
        
        Implements Requirements 2.3, 7.4: Adds inline comments and generates
        line-by-line annotations.
        
        Args:
            file_analysis: Analysis results for the source file
            
        Returns:
            Dictionary mapping line numbers to annotation text
        """
        annotations = {}
        
        if not self.config.include_annotations:
            return annotations
        
        # Annotate class definitions
        for cls in file_analysis.symbol_info.classes:
            if cls.docstring:
                first_line = cls.docstring.split('\n')[0]
                annotations[cls.start_line] = f"Class definition: {first_line}"
        
        # Annotate complex functions
        for func in file_analysis.symbol_info.functions:
            if func.complexity > 5:
                annotations[func.start_line] = (
                    f"Complex function (complexity {func.complexity}): "
                    f"Pay attention to control flow"
                )
        
        # Annotate pattern locations
        for pattern in file_analysis.patterns[:3]:
            if pattern.line_numbers:
                first_line = min(pattern.line_numbers)
                pattern_name = pattern.pattern_type.replace('_', ' ').title()
                annotations[first_line] = f"{pattern_name} pattern starts here"
        
        return annotations
    
    def _pattern_to_objective(self, pattern: DetectedPattern) -> str:
        """Convert a detected pattern to a learning objective.
        
        Implements Requirement 2.2: Generates objectives from patterns using
        action verbs (understand, implement, apply, analyze).
        
        Args:
            pattern: Detected pattern
            
        Returns:
            Learning objective string
        """
        pattern_name = pattern.pattern_type.replace('_', ' ')
        
        # Choose action verb based on confidence
        if pattern.confidence > 0.8:
            verb = "Implement"
        elif pattern.confidence > 0.6:
            verb = "Apply"
        else:
            verb = "Understand"
        
        return f"{verb} {pattern_name} pattern"
    
    def _explain_pattern(self, pattern: DetectedPattern) -> str:
        """Generate explanation for a detected pattern.
        
        Implements Requirement 7.1: Uses simple language appropriate for
        target difficulty level.
        
        Args:
            pattern: Detected pattern
            
        Returns:
            Pattern explanation text
        """
        pattern_name = pattern.pattern_type.replace('_', ' ')
        
        # Build explanation from evidence
        explanation_parts = [
            f"This code demonstrates the {pattern_name} pattern. "
        ]
        
        if pattern.evidence:
            explanation_parts.append("Evidence includes: ")
            explanation_parts.append(", ".join(pattern.evidence[:3]))
            explanation_parts.append(". ")
        
        # Add confidence note
        if pattern.confidence > 0.8:
            explanation_parts.append(
                "This is a clear example of this pattern."
            )
        elif pattern.confidence > 0.6:
            explanation_parts.append(
                "This shows characteristics of this pattern."
            )
        else:
            explanation_parts.append(
                "This has some elements of this pattern."
            )
        
        return "".join(explanation_parts)
    
    def _generate_further_reading(self, file_analysis: FileAnalysis) -> List[str]:
        """Generate further reading suggestions.
        
        Args:
            file_analysis: Analysis results for the source file
            
        Returns:
            List of reading suggestions
        """
        suggestions = []
        
        # Suggest reading based on patterns
        pattern_docs = {
            'react_component': 'React Component Documentation',
            'api_route': 'API Design Best Practices',
            'database_model': 'Database Design Patterns',
            'authentication': 'Security and Authentication',
            'state_management': 'State Management Patterns',
        }
        
        for pattern in file_analysis.patterns[:3]:
            if pattern.pattern_type in pattern_docs:
                suggestions.append(pattern_docs[pattern.pattern_type])
        
        # Generic suggestions
        if file_analysis.complexity_metrics.avg_complexity > 5:
            suggestions.append('Code Complexity and Refactoring')
        
        if file_analysis.documentation_coverage > 0.7:
            suggestions.append('Documentation Best Practices')
        
        return suggestions if suggestions else ['Clean Code Principles']
    
    def _prioritize_patterns_by_focus(self, patterns: List[DetectedPattern]) -> List[DetectedPattern]:
        """Prioritize patterns based on course focus.
        
        Implements Task 13.3: Prioritizes relevant patterns by focus.
        
        Args:
            patterns: List of detected patterns
            
        Returns:
            Patterns sorted by focus relevance
        """
        focus = self.config.course_focus
        
        # If full-stack, return patterns as-is (sorted by confidence)
        if focus == "full-stack":
            return sorted(patterns, key=lambda p: p.confidence, reverse=True)
        
        # Define pattern priorities for each focus
        focus_priorities = {
            "patterns": {
                "factory_pattern": 10, "singleton_pattern": 9, "observer_pattern": 9,
                "strategy_pattern": 8, "decorator_pattern": 8, "adapter_pattern": 7,
                "mvc_pattern": 7, "repository_pattern": 6, "dependency_injection": 6
            },
            "architecture": {
                "mvc_pattern": 10, "layered_architecture": 9, "microservices": 9,
                "api_design": 8, "database_model": 8, "service_layer": 7,
                "repository_pattern": 7, "dependency_injection": 6, "modular_design": 6
            },
            "best-practices": {
                "error_handling": 10, "input_validation": 9, "logging": 9,
                "testing": 8, "documentation": 8, "code_organization": 7,
                "security": 10, "performance_optimization": 7, "clean_code": 6
            }
        }
        
        priorities = focus_priorities.get(focus, {})
        
        # Score each pattern
        scored_patterns = []
        for pattern in patterns:
            # Base score is confidence
            score = pattern.confidence
            
            # Boost by focus priority
            pattern_type = pattern.pattern_type.lower()
            for priority_pattern, priority_value in priorities.items():
                if priority_pattern.lower() in pattern_type or pattern_type in priority_pattern.lower():
                    score *= (1 + priority_value / 10)
                    break
            
            scored_patterns.append((pattern, score))
        
        # Sort by score
        scored_patterns.sort(key=lambda x: x[1], reverse=True)
        
        return [pattern for pattern, _ in scored_patterns]
    
    # ========== Cache Serialization Methods ==========
    
    def _serialize_lesson_content(self, content: LessonContent) -> dict:
        """Serialize LessonContent to dictionary for caching.
        
        Args:
            content: LessonContent to serialize
            
        Returns:
            Dictionary representation
        """
        return {
            "introduction": content.introduction,
            "explanation": content.explanation,
            "code_example": {
                "code": content.code_example.code,
                "language": content.code_example.language,
                "filename": content.code_example.filename,
                "highlights": [
                    {
                        "start_line": h.start_line,
                        "end_line": h.end_line,
                        "description": h.description
                    }
                    for h in content.code_example.highlights
                ],
                "annotations": content.code_example.annotations
            },
            "walkthrough": content.walkthrough,
            "summary": content.summary,
            "further_reading": content.further_reading
        }
    
    def _deserialize_lesson_content(self, data: dict) -> LessonContent:
        """Deserialize LessonContent from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            LessonContent instance
        """
        code_ex_data = data["code_example"]
        code_example = CodeExample(
            code=code_ex_data["code"],
            language=code_ex_data["language"],
            filename=code_ex_data["filename"],
            highlights=[
                CodeHighlight(
                    start_line=h["start_line"],
                    end_line=h["end_line"],
                    description=h["description"]
                )
                for h in code_ex_data["highlights"]
            ],
            annotations=code_ex_data["annotations"]
        )
        
        return LessonContent(
            introduction=data["introduction"],
            explanation=data["explanation"],
            code_example=code_example,
            walkthrough=data["walkthrough"],
            summary=data["summary"],
            further_reading=data["further_reading"]
        )
