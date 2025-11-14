"""
Systematic Investigation Engine for AI Content Enrichment.

This module implements a structured approach to understanding code by
systematically investigating what it does, why it exists, how it works,
when it's used, edge cases, and common pitfalls - all with evidence citations.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.course.enrichment_models import (
    SystematicInvestigation,
    EvidenceBundle,
    FeatureMapping,
    ValidationChecklist
)

logger = logging.getLogger(__name__)


class InvestigationEngine:
    """
    Systematically investigates code to answer key questions with evidence.
    
    Implements the systematic investigation framework that ensures all
    generated content is grounded in evidence from code, tests, git history,
    and documentation.
    """
    
    def __init__(self):
        """Initialize the investigation engine."""
        logger.info("Initialized InvestigationEngine")
    
    def investigate(
        self,
        feature: FeatureMapping,
        evidence: EvidenceBundle,
        validation: ValidationChecklist
    ) -> SystematicInvestigation:
        """
        Perform systematic investigation of code with evidence.
        
        Answers six key questions:
        1. What does it do? (factual, cite code)
        2. Why does it exist? (cite commits/docs)
        3. How does it work? (cite code sections)
        4. When is it used? (cite call sites)
        5. What are edge cases? (cite tests)
        6. What are pitfalls? (cite comments/tests)
        
        Args:
            feature: Feature mapping with user-facing context
            evidence: Evidence bundle with all sources
            validation: Validation checklist with cross-referenced understanding
            
        Returns:
            SystematicInvestigation with all answers and citations
        """
        logger.info(f"Starting systematic investigation for feature: {feature.feature_name}")
        
        # Investigate what the code does
        what_it_does = self.investigate_what_it_does(evidence)
        
        # Investigate why it exists
        why_it_exists = self.investigate_why_it_exists(evidence)
        
        # Investigate how it works
        how_it_works = self.investigate_how_it_works(evidence)
        
        # Investigate when it's used
        when_its_used = self.investigate_when_used(evidence)
        
        # Investigate edge cases
        edge_cases = self.investigate_edge_cases(evidence)
        
        # Investigate common pitfalls
        common_pitfalls = self.investigate_pitfalls(evidence)
        
        investigation = SystematicInvestigation(
            what_it_does=what_it_does,
            why_it_exists=why_it_exists,
            how_it_works=how_it_works,
            when_its_used=when_its_used,
            edge_cases=edge_cases,
            common_pitfalls=common_pitfalls
        )
        
        logger.info(f"Completed systematic investigation for feature: {feature.feature_name}")
        
        return investigation
    
    def investigate_what_it_does(self, evidence: EvidenceBundle) -> str:
        """
        Describe what the code does with factual citations to code sections.
        
        Analyzes source code and test expectations to create a factual
        description of functionality with precise line number citations.
        
        Args:
            evidence: Evidence bundle with source files and tests
            
        Returns:
            Factual description with code citations
        """
        descriptions = []
        
        # Analyze source files
        for source_file in evidence.source_files:
            file_path = source_file['path']
            language = source_file.get('language', 'unknown')
            
            # Extract high-level functionality from code structure
            for section in source_file.get('sections', []):
                start_line = section.get('start_line', 1)
                end_line = section.get('end_line', 1)
                code = section.get('code', '')
                
                # Analyze code structure
                functionality = self._analyze_code_functionality(code, language)
                
                if functionality:
                    citation = f"[{file_path}:{start_line}-{end_line}]"
                    descriptions.append(f"{functionality} {citation}")
        
        # Cross-reference with test expectations
        for test_file in evidence.test_files:
            test_path = test_file['path']
            coverage = test_file.get('coverage', [])
            
            if coverage:
                # Add test-validated behaviors
                for behavior in coverage[:3]:  # Top 3 most important
                    citation = f"[validated by {test_path}]"
                    descriptions.append(f"{behavior} {citation}")
        
        # Combine into coherent description
        if descriptions:
            result = "This code " + "; ".join(descriptions[:5])  # Top 5 descriptions
        else:
            result = "This code provides functionality as defined in the source files."
        
        logger.debug(f"Generated 'what it does' description with {len(descriptions)} citations")
        
        return result

    
    def investigate_why_it_exists(self, evidence: EvidenceBundle) -> str:
        """
        Explain why the code exists with citations to git commits or documentation.
        
        Extracts business/technical rationale from commit messages and
        documentation to explain the purpose and motivation.
        
        Args:
            evidence: Evidence bundle with git commits and documentation
            
        Returns:
            Explanation with git/doc citations
        """
        reasons = []
        
        # Extract from git commit messages
        for commit in evidence.git_commits[:5]:  # Top 5 most relevant commits
            commit_hash = commit.get('hash', '')[:8]
            message = commit.get('message', '')
            subject = commit.get('subject', '')
            
            # Extract purpose from commit message
            purpose = self._extract_purpose_from_commit(message or subject)
            
            if purpose:
                citation = f"[commit {commit_hash}]"
                reasons.append(f"{purpose} {citation}")
        
        # Extract from documentation
        for doc in evidence.documentation[:3]:  # Top 3 most relevant docs
            content = doc.get('content', '')
            location = doc.get('location', '')
            
            # Extract purpose from docstrings/comments
            purpose = self._extract_purpose_from_documentation(content)
            
            if purpose:
                citation = f"[{location}]"
                reasons.append(f"{purpose} {citation}")
        
        # Combine into coherent explanation
        if reasons:
            result = "This code exists to: " + "; ".join(reasons[:3])  # Top 3 reasons
        else:
            result = "This code exists to provide functionality as part of the system architecture."
        
        logger.debug(f"Generated 'why it exists' explanation with {len(reasons)} citations")
        
        return result
    
    def investigate_how_it_works(self, evidence: EvidenceBundle) -> str:
        """
        Explain how the code works with citations to implementation details.
        
        Analyzes code structure, algorithms, and patterns to explain
        the technical implementation approach.
        
        Args:
            evidence: Evidence bundle with source files
            
        Returns:
            Technical explanation with code section citations
        """
        explanations = []
        
        # Analyze each source file
        for source_file in evidence.source_files:
            file_path = source_file['path']
            language = source_file.get('language', 'unknown')
            
            for section in source_file.get('sections', []):
                start_line = section.get('start_line', 1)
                end_line = section.get('end_line', 1)
                code = section.get('code', '')
                
                # Analyze implementation approach
                implementation = self._analyze_implementation(code, language)
                
                if implementation:
                    citation = f"[{file_path}:{start_line}-{end_line}]"
                    explanations.append(f"{implementation} {citation}")
        
        # Analyze dependencies to understand integration
        if evidence.dependencies:
            dep_names = [dep['name'] for dep in evidence.dependencies[:3]]
            if dep_names:
                deps_str = ", ".join(dep_names)
                explanations.append(f"Integrates with {deps_str} for extended functionality")
        
        # Combine into coherent explanation
        if explanations:
            result = "Implementation approach: " + "; ".join(explanations[:4])  # Top 4 explanations
        else:
            result = "Implementation follows standard patterns for the language and framework."
        
        logger.debug(f"Generated 'how it works' explanation with {len(explanations)} citations")
        
        return result
    
    def investigate_when_used(self, evidence: EvidenceBundle) -> List[str]:
        """
        Identify when the code is used with citations to call sites.
        
        Analyzes dependents and usage patterns to identify scenarios
        where this code is invoked.
        
        Args:
            evidence: Evidence bundle with dependents information
            
        Returns:
            List of usage scenarios with citations
        """
        usage_scenarios = []
        
        # Analyze dependents (what calls this code)
        for dependent in evidence.dependents:
            dep_name = dependent.get('name', '')
            usage = dependent.get('usage', '')
            evidence_str = dependent.get('evidence', '')
            
            if usage:
                citation = f"[called by {dep_name}]"
                scenario = f"{usage} {citation}"
                usage_scenarios.append(scenario)
        
        # Analyze test files for usage patterns
        for test_file in evidence.test_files:
            test_path = test_file['path']
            test_cases = test_file.get('test_cases', [])
            
            # Extract usage scenarios from test descriptions
            for test_case in test_cases[:3]:  # Top 3 test cases
                description = test_case.get('description', '')
                
                if description:
                    # Convert test description to usage scenario
                    scenario = self._test_to_usage_scenario(description)
                    citation = f"[tested in {test_path}]"
                    usage_scenarios.append(f"{scenario} {citation}")
        
        # If no specific usage found, provide general scenarios
        if not usage_scenarios:
            usage_scenarios.append("Used as part of the application's core functionality")
        
        logger.debug(f"Identified {len(usage_scenarios)} usage scenarios")
        
        return usage_scenarios[:5]  # Return top 5 scenarios
    
    def investigate_edge_cases(self, evidence: EvidenceBundle) -> List[str]:
        """
        Identify edge cases with citations from test analysis.
        
        Extracts special handling, boundary conditions, and edge cases
        from test files and code comments.
        
        Args:
            evidence: Evidence bundle with test files
            
        Returns:
            List of edge cases with test citations
        """
        edge_cases = []
        
        # Analyze test files for edge case handling
        for test_file in evidence.test_files:
            test_path = test_file['path']
            test_cases = test_file.get('test_cases', [])
            
            for test_case in test_cases:
                description = test_case.get('description', '').lower()
                
                # Look for edge case indicators
                if self._is_edge_case_test(description):
                    edge_case = self._extract_edge_case(description)
                    citation = f"[{test_path}: {test_case.get('name', 'test')}]"
                    edge_cases.append(f"{edge_case} {citation}")
        
        # Extract from code comments
        for doc in evidence.documentation:
            content = doc.get('content', '').lower()
            location = doc.get('location', '')
            
            # Look for edge case mentions in comments
            if any(keyword in content for keyword in ['edge case', 'special case', 'boundary', 'corner case']):
                edge_case = self._extract_edge_case_from_doc(content)
                if edge_case:
                    citation = f"[{location}]"
                    edge_cases.append(f"{edge_case} {citation}")
        
        # If no edge cases found
        if not edge_cases:
            edge_cases.append("No specific edge cases documented in tests or comments")
        
        logger.debug(f"Identified {len(edge_cases)} edge cases")
        
        return edge_cases[:5]  # Return top 5 edge cases
    
    def investigate_pitfalls(self, evidence: EvidenceBundle) -> List[str]:
        """
        Identify common pitfalls with citations from comments and tests.
        
        Extracts warnings, gotchas, and common mistakes from code comments,
        documentation, and test failure scenarios.
        
        Args:
            evidence: Evidence bundle with documentation and tests
            
        Returns:
            List of common pitfalls with citations
        """
        pitfalls = []
        
        # Extract from documentation and comments
        for doc in evidence.documentation:
            content = doc.get('content', '').lower()
            location = doc.get('location', '')
            
            # Look for warning indicators
            if self._contains_warning(content):
                pitfall = self._extract_pitfall_from_doc(content)
                if pitfall:
                    citation = f"[{location}]"
                    pitfalls.append(f"{pitfall} {citation}")
        
        # Extract from test descriptions (tests often reveal pitfalls)
        for test_file in evidence.test_files:
            test_path = test_file['path']
            test_cases = test_file.get('test_cases', [])
            
            for test_case in test_cases:
                description = test_case.get('description', '').lower()
                
                # Look for pitfall indicators
                if self._is_pitfall_test(description):
                    pitfall = self._extract_pitfall_from_test(description)
                    citation = f"[{test_path}: {test_case.get('name', 'test')}]"
                    pitfalls.append(f"{pitfall} {citation}")
        
        # Extract from git commits (bug fixes reveal pitfalls)
        for commit in evidence.git_commits:
            message = commit.get('message', '').lower()
            commit_hash = commit.get('hash', '')[:8]
            
            if self._is_bug_fix_commit(message):
                pitfall = self._extract_pitfall_from_commit(message)
                if pitfall:
                    citation = f"[commit {commit_hash}]"
                    pitfalls.append(f"{pitfall} {citation}")
        
        # If no pitfalls found
        if not pitfalls:
            pitfalls.append("No specific pitfalls documented in comments or tests")
        
        logger.debug(f"Identified {len(pitfalls)} common pitfalls")
        
        return pitfalls[:5]  # Return top 5 pitfalls
    
    # Helper methods for code analysis
    
    def _analyze_code_functionality(self, code: str, language: str) -> Optional[str]:
        """
        Analyze code to determine its primary functionality.
        
        Args:
            code: Source code snippet
            language: Programming language
            
        Returns:
            Description of functionality or None
        """
        if not code.strip():
            return None
        
        # Look for common patterns
        code_lower = code.lower()
        
        # Function/class definitions
        if language == 'python':
            if 'def ' in code and 'class ' not in code:
                # Extract function name
                match = re.search(r'def\s+(\w+)\s*\(', code)
                if match:
                    func_name = match.group(1)
                    return f"defines function '{func_name}'"
            elif 'class ' in code:
                match = re.search(r'class\s+(\w+)', code)
                if match:
                    class_name = match.group(1)
                    return f"defines class '{class_name}'"
        
        elif language in ['javascript', 'typescript']:
            if 'function ' in code or '=>' in code:
                match = re.search(r'function\s+(\w+)\s*\(', code)
                if match:
                    func_name = match.group(1)
                    return f"defines function '{func_name}'"
                elif 'const ' in code or 'let ' in code:
                    return "defines a function"
            elif 'class ' in code:
                match = re.search(r'class\s+(\w+)', code)
                if match:
                    class_name = match.group(1)
                    return f"defines class '{class_name}'"
        
        # Common operations
        if 'return' in code_lower:
            return "performs computation and returns result"
        if 'async' in code_lower or 'await' in code_lower:
            return "performs asynchronous operations"
        if 'fetch' in code_lower or 'request' in code_lower or 'http' in code_lower:
            return "makes HTTP requests"
        if 'database' in code_lower or 'query' in code_lower or 'select' in code_lower:
            return "performs database operations"
        if 'validate' in code_lower or 'check' in code_lower:
            return "validates data or conditions"
        if 'parse' in code_lower or 'transform' in code_lower:
            return "parses or transforms data"
        
        return "provides functionality"

    
    def _extract_purpose_from_commit(self, message: str) -> Optional[str]:
        """
        Extract purpose/rationale from commit message.
        
        Args:
            message: Commit message
            
        Returns:
            Purpose statement or None
        """
        if not message:
            return None
        
        # Clean up message
        message = message.strip()
        lines = message.split('\n')
        
        # Use first line (subject) as primary source
        subject = lines[0].strip()
        
        # Look for common patterns
        patterns = [
            (r'^add(?:ed)?\s+(.+)', 'add'),
            (r'^implement(?:ed)?\s+(.+)', 'implement'),
            (r'^create(?:d)?\s+(.+)', 'create'),
            (r'^fix(?:ed)?\s+(.+)', 'fix'),
            (r'^update(?:d)?\s+(.+)', 'update'),
            (r'^improve(?:d)?\s+(.+)', 'improve'),
            (r'^refactor(?:ed)?\s+(.+)', 'refactor'),
        ]
        
        for pattern, action in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                what = match.group(1).strip()
                return f"{action} {what}"
        
        # If no pattern matched, use subject as-is
        if len(subject) > 10:
            return subject
        
        return None
    
    def _extract_purpose_from_documentation(self, content: str) -> Optional[str]:
        """
        Extract purpose from documentation/docstring.
        
        Args:
            content: Documentation content
            
        Returns:
            Purpose statement or None
        """
        if not content:
            return None
        
        # Clean up content
        content = content.strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # First line is usually the summary
        first_line = lines[0]
        
        # Remove common docstring markers
        first_line = first_line.strip('"""\'')
        
        # If it's a reasonable length, use it
        if 10 < len(first_line) < 200:
            return first_line
        
        return None
    
    def _analyze_implementation(self, code: str, language: str) -> Optional[str]:
        """
        Analyze implementation approach from code.
        
        Args:
            code: Source code snippet
            language: Programming language
            
        Returns:
            Implementation description or None
        """
        if not code.strip():
            return None
        
        code_lower = code.lower()
        approaches = []
        
        # Detect patterns
        if 'async' in code_lower or 'await' in code_lower:
            approaches.append("uses asynchronous programming")
        
        if 'class' in code_lower:
            approaches.append("uses object-oriented design")
        
        if 'try' in code_lower and 'except' in code_lower:
            approaches.append("includes error handling")
        elif 'try' in code_lower and 'catch' in code_lower:
            approaches.append("includes error handling")
        
        if 'decorator' in code_lower or '@' in code:
            approaches.append("uses decorators")
        
        if 'generator' in code_lower or 'yield' in code_lower:
            approaches.append("uses generators")
        
        if 'lambda' in code_lower or '=>' in code:
            approaches.append("uses functional programming")
        
        if 'cache' in code_lower or 'memo' in code_lower:
            approaches.append("implements caching")
        
        if 'validate' in code_lower or 'schema' in code_lower:
            approaches.append("validates input data")
        
        if approaches:
            return ", ".join(approaches)
        
        return None
    
    def _test_to_usage_scenario(self, test_description: str) -> str:
        """
        Convert test description to usage scenario.
        
        Args:
            test_description: Test case description
            
        Returns:
            Usage scenario description
        """
        # Remove test-specific language
        scenario = test_description.lower()
        scenario = scenario.replace('should ', '')
        scenario = scenario.replace('test ', '')
        scenario = scenario.replace('it ', '')
        
        # Capitalize first letter
        if scenario:
            scenario = scenario[0].upper() + scenario[1:]
        
        return scenario
    
    def _is_edge_case_test(self, description: str) -> bool:
        """
        Check if test description indicates an edge case.
        
        Args:
            description: Test description
            
        Returns:
            True if edge case test
        """
        edge_case_keywords = [
            'edge case', 'corner case', 'boundary',
            'empty', 'null', 'none', 'zero',
            'invalid', 'error', 'exception',
            'maximum', 'minimum', 'limit',
            'special case', 'unusual'
        ]
        
        return any(keyword in description for keyword in edge_case_keywords)
    
    def _extract_edge_case(self, description: str) -> str:
        """
        Extract edge case description from test.
        
        Args:
            description: Test description
            
        Returns:
            Edge case description
        """
        # Clean up description
        edge_case = description.replace('should ', '')
        edge_case = edge_case.replace('test ', '')
        
        # Capitalize
        if edge_case:
            edge_case = edge_case[0].upper() + edge_case[1:]
        
        return edge_case
    
    def _extract_edge_case_from_doc(self, content: str) -> Optional[str]:
        """
        Extract edge case from documentation.
        
        Args:
            content: Documentation content
            
        Returns:
            Edge case description or None
        """
        # Look for sentences mentioning edge cases
        sentences = content.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ['edge case', 'special case', 'boundary']):
                return sentence.strip()
        
        return None
    
    def _contains_warning(self, content: str) -> bool:
        """
        Check if documentation contains warnings.
        
        Args:
            content: Documentation content
            
        Returns:
            True if contains warning
        """
        warning_keywords = [
            'warning', 'caution', 'note', 'important',
            'careful', 'avoid', 'don\'t', 'do not',
            'pitfall', 'gotcha', 'beware', 'watch out'
        ]
        
        return any(keyword in content for keyword in warning_keywords)
    
    def _extract_pitfall_from_doc(self, content: str) -> Optional[str]:
        """
        Extract pitfall from documentation.
        
        Args:
            content: Documentation content
            
        Returns:
            Pitfall description or None
        """
        # Look for sentences with warning keywords
        sentences = content.split('.')
        
        for sentence in sentences:
            if self._contains_warning(sentence):
                # Clean up and return
                pitfall = sentence.strip()
                if len(pitfall) > 10:
                    return pitfall
        
        return None
    
    def _is_pitfall_test(self, description: str) -> bool:
        """
        Check if test description indicates a pitfall.
        
        Args:
            description: Test description
            
        Returns:
            True if pitfall test
        """
        pitfall_keywords = [
            'error', 'fail', 'invalid', 'incorrect',
            'wrong', 'bad', 'reject', 'throw',
            'prevent', 'avoid', 'handle'
        ]
        
        return any(keyword in description for keyword in pitfall_keywords)
    
    def _extract_pitfall_from_test(self, description: str) -> str:
        """
        Extract pitfall from test description.
        
        Args:
            description: Test description
            
        Returns:
            Pitfall description
        """
        # Convert test to pitfall warning
        pitfall = description.replace('should ', '')
        pitfall = pitfall.replace('test ', '')
        
        # Add warning context
        if 'error' in pitfall or 'fail' in pitfall:
            pitfall = f"Avoid: {pitfall}"
        
        # Capitalize
        if pitfall:
            pitfall = pitfall[0].upper() + pitfall[1:]
        
        return pitfall
    
    def _is_bug_fix_commit(self, message: str) -> bool:
        """
        Check if commit message indicates a bug fix.
        
        Args:
            message: Commit message
            
        Returns:
            True if bug fix commit
        """
        bug_keywords = [
            'fix', 'bug', 'issue', 'problem',
            'error', 'crash', 'fail', 'broken',
            'resolve', 'patch', 'correct'
        ]
        
        return any(keyword in message for keyword in bug_keywords)
    
    def _extract_pitfall_from_commit(self, message: str) -> Optional[str]:
        """
        Extract pitfall from bug fix commit.
        
        Args:
            message: Commit message
            
        Returns:
            Pitfall description or None
        """
        # Extract what was fixed
        patterns = [
            r'fix(?:ed)?\s+(.+)',
            r'resolve(?:d)?\s+(.+)',
            r'correct(?:ed)?\s+(.+)',
            r'patch(?:ed)?\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                what_was_fixed = match.group(1).strip()
                # Convert to warning
                return f"Avoid: {what_was_fixed}"
        
        return None


def create_investigation_engine() -> InvestigationEngine:
    """
    Factory function to create an InvestigationEngine instance.
    
    Returns:
        InvestigationEngine instance
    """
    return InvestigationEngine()
