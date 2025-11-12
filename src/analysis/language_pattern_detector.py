"""
Language-Specific Pattern Detectors using Tree-sitter Queries.

This module provides pattern detectors for language-specific constructs
like decorators, generators, async/await, comprehensions, etc.
"""

import logging
from typing import List, Optional, Dict, Any
from tree_sitter import Language, Query

from .pattern_detector import BasePatternDetector, DetectedPattern
from .symbol_extractor import SymbolInfo

logger = logging.getLogger(__name__)


class PythonPatternDetector(BasePatternDetector):
    """
    Detects Python-specific patterns using tree-sitter queries.
    
    Patterns detected:
    - Decorators (property, staticmethod, classmethod, custom)
    - Context managers (with statements)
    - Generators (yield statements)
    - Async/await patterns
    - List/dict comprehensions
    - Lambda functions
    """
    
    def detect(
        self,
        symbol_info: SymbolInfo,
        file_content: str,
        file_path: str
    ) -> List[DetectedPattern]:
        """Detect Python-specific patterns."""
        patterns = []
        
        # Only process Python files
        if not file_path.endswith('.py'):
            return patterns
        
        # Detect decorators
        decorator_pattern = self._detect_decorators(symbol_info, file_content, file_path)
        if decorator_pattern:
            patterns.append(decorator_pattern)
        
        # Detect context managers
        context_pattern = self._detect_context_managers(file_content, file_path)
        if context_pattern:
            patterns.append(context_pattern)
        
        # Detect generators
        generator_pattern = self._detect_generators(symbol_info, file_content, file_path)
        if generator_pattern:
            patterns.append(generator_pattern)
        
        # Detect async/await
        async_pattern = self._detect_async_patterns(symbol_info, file_content, file_path)
        if async_pattern:
            patterns.append(async_pattern)
        
        # Detect comprehensions
        comprehension_pattern = self._detect_comprehensions(file_content, file_path)
        if comprehension_pattern:
            patterns.append(comprehension_pattern)
        
        return patterns
    
    def _detect_decorators(
        self,
        symbol_info: SymbolInfo,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect decorator usage."""
        evidence = []
        line_numbers = []
        decorator_types = set()
        decorator_count = 0
        
        # Check functions
        for func in symbol_info.functions:
            if func.decorators:
                decorator_count += len(func.decorators)
                for dec in func.decorators:
                    decorator_types.add(dec)
                    if len(line_numbers) < 10:
                        line_numbers.append(func.start_line)
        
        # Check class methods
        for cls in symbol_info.classes:
            for method in cls.methods:
                if method.decorators:
                    decorator_count += len(method.decorators)
                    for dec in method.decorators:
                        decorator_types.add(dec)
                        if len(line_numbers) < 10:
                            line_numbers.append(method.start_line)
        
        if decorator_count == 0:
            return None
        
        # Categorize decorators
        builtin_decorators = {'property', 'staticmethod', 'classmethod', 'abstractmethod'}
        found_builtins = decorator_types & builtin_decorators
        custom_decorators = decorator_types - builtin_decorators
        
        if found_builtins:
            evidence.append(f"Uses built-in decorators: {', '.join(sorted(found_builtins))}")
        if custom_decorators:
            evidence.append(f"Uses custom decorators ({len(custom_decorators)} types)")
        evidence.append(f"Total decorators: {decorator_count}")
        
        confidence = min(1.0, decorator_count * 0.15)
        
        return DetectedPattern(
            pattern_type="python_decorators",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "decorator_count": decorator_count,
                "builtin_decorators": list(found_builtins),
                "custom_decorator_count": len(custom_decorators)
            }
        )
    
    def _detect_context_managers(
        self,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect context manager usage (with statements)."""
        evidence = []
        line_numbers = []
        with_count = 0
        
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('with ') and ':' in stripped:
                with_count += 1
                if len(line_numbers) < 10:
                    line_numbers.append(i)
        
        if with_count == 0:
            return None
        
        evidence.append(f"Uses context managers ({with_count} with statements)")
        
        # Check for common patterns
        content_lower = file_content.lower()
        if 'with open(' in content_lower:
            evidence.append("File handling with context managers")
        if 'with lock' in content_lower or 'with threading' in content_lower:
            evidence.append("Thread synchronization with context managers")
        
        confidence = min(1.0, with_count * 0.2)
        
        return DetectedPattern(
            pattern_type="python_context_managers",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "with_statement_count": with_count
            }
        )
    
    def _detect_generators(
        self,
        symbol_info: SymbolInfo,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect generator functions (yield statements)."""
        evidence = []
        line_numbers = []
        generator_count = 0
        
        # Check for yield in file content
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'yield' in line and not line.strip().startswith('#'):
                generator_count += 1
                if len(line_numbers) < 10:
                    line_numbers.append(i)
        
        if generator_count == 0:
            return None
        
        evidence.append(f"Uses generators ({generator_count} yield statements)")
        
        # Check for generator expressions
        if '(' in file_content and 'for' in file_content and 'in' in file_content:
            if any(line.count('(') > 0 and 'for' in line and 'in' in line 
                   for line in lines if not line.strip().startswith('#')):
                evidence.append("Uses generator expressions")
        
        confidence = min(1.0, generator_count * 0.25)
        
        return DetectedPattern(
            pattern_type="python_generators",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "yield_count": generator_count
            }
        )
    
    def _detect_async_patterns(
        self,
        symbol_info: SymbolInfo,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect async/await patterns."""
        evidence = []
        line_numbers = []
        async_func_count = 0
        await_count = 0
        
        # Count async functions
        for func in symbol_info.functions:
            if func.is_async:
                async_func_count += 1
                if len(line_numbers) < 10:
                    line_numbers.append(func.start_line)
        
        for cls in symbol_info.classes:
            for method in cls.methods:
                if method.is_async:
                    async_func_count += 1
                    if len(line_numbers) < 10:
                        line_numbers.append(method.start_line)
        
        # Count await statements
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'await ' in line and not line.strip().startswith('#'):
                await_count += 1
        
        if async_func_count == 0 and await_count == 0:
            return None
        
        if async_func_count > 0:
            evidence.append(f"Async functions: {async_func_count}")
        if await_count > 0:
            evidence.append(f"Await statements: {await_count}")
        
        # Check for asyncio usage
        for imp in symbol_info.imports:
            if 'asyncio' in imp.module.lower():
                evidence.append("Uses asyncio library")
                break
        
        confidence = min(1.0, (async_func_count * 0.2) + (await_count * 0.1))
        
        return DetectedPattern(
            pattern_type="python_async_await",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "async_function_count": async_func_count,
                "await_count": await_count
            }
        )
    
    def _detect_comprehensions(
        self,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect list/dict/set comprehensions."""
        evidence = []
        line_numbers = []
        comprehension_count = 0
        
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            
            # Simple heuristic: look for [... for ... in ...] or {... for ... in ...}
            if ' for ' in line and ' in ' in line:
                if ('[' in line and ']' in line) or ('{' in line and '}' in line):
                    comprehension_count += 1
                    if len(line_numbers) < 10:
                        line_numbers.append(i)
        
        if comprehension_count == 0:
            return None
        
        evidence.append(f"Uses comprehensions ({comprehension_count} occurrences)")
        
        confidence = min(1.0, comprehension_count * 0.15)
        
        return DetectedPattern(
            pattern_type="python_comprehensions",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "comprehension_count": comprehension_count
            }
        )


class JavaScriptPatternDetector(BasePatternDetector):
    """
    Detects JavaScript/TypeScript-specific patterns.
    
    Patterns detected:
    - Promises (then/catch chains)
    - Async/await
    - Arrow functions
    - Destructuring
    - Spread operators
    - ES6 classes
    """
    
    def detect(
        self,
        symbol_info: SymbolInfo,
        file_content: str,
        file_path: str
    ) -> List[DetectedPattern]:
        """Detect JavaScript-specific patterns."""
        patterns = []
        
        # Only process JS/TS files
        if not (file_path.endswith('.js') or file_path.endswith('.ts') or 
                file_path.endswith('.jsx') or file_path.endswith('.tsx')):
            return patterns
        
        # Detect promises
        promise_pattern = self._detect_promises(file_content, file_path)
        if promise_pattern:
            patterns.append(promise_pattern)
        
        # Detect async/await
        async_pattern = self._detect_async_await(symbol_info, file_content, file_path)
        if async_pattern:
            patterns.append(async_pattern)
        
        # Detect arrow functions
        arrow_pattern = self._detect_arrow_functions(file_content, file_path)
        if arrow_pattern:
            patterns.append(arrow_pattern)
        
        # Detect destructuring
        destructuring_pattern = self._detect_destructuring(file_content, file_path)
        if destructuring_pattern:
            patterns.append(destructuring_pattern)
        
        # Detect spread operators
        spread_pattern = self._detect_spread_operators(file_content, file_path)
        if spread_pattern:
            patterns.append(spread_pattern)
        
        return patterns
    
    def _detect_promises(
        self,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect Promise usage."""
        evidence = []
        line_numbers = []
        promise_count = 0
        
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            if '.then(' in line or '.catch(' in line or 'new Promise(' in line:
                promise_count += 1
                if len(line_numbers) < 10:
                    line_numbers.append(i)
        
        if promise_count == 0:
            return None
        
        evidence.append(f"Uses Promises ({promise_count} occurrences)")
        
        if '.then(' in file_content:
            evidence.append("Promise chaining with .then()")
        if '.catch(' in file_content:
            evidence.append("Error handling with .catch()")
        if 'Promise.all(' in file_content:
            evidence.append("Parallel promises with Promise.all()")
        
        confidence = min(1.0, promise_count * 0.2)
        
        return DetectedPattern(
            pattern_type="javascript_promises",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "promise_count": promise_count
            }
        )
    
    def _detect_async_await(
        self,
        symbol_info: SymbolInfo,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect async/await patterns."""
        evidence = []
        line_numbers = []
        async_func_count = 0
        await_count = 0
        
        # Count async functions
        for func in symbol_info.functions:
            if func.is_async:
                async_func_count += 1
                if len(line_numbers) < 10:
                    line_numbers.append(func.start_line)
        
        # Count await statements
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'await ' in line:
                await_count += 1
        
        if async_func_count == 0 and await_count == 0:
            return None
        
        if async_func_count > 0:
            evidence.append(f"Async functions: {async_func_count}")
        if await_count > 0:
            evidence.append(f"Await statements: {await_count}")
        
        confidence = min(1.0, (async_func_count * 0.2) + (await_count * 0.1))
        
        return DetectedPattern(
            pattern_type="javascript_async_await",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "async_function_count": async_func_count,
                "await_count": await_count
            }
        )
    
    def _detect_arrow_functions(
        self,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect arrow function usage."""
        evidence = []
        line_numbers = []
        arrow_count = 0
        
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            if '=>' in line and not line.strip().startswith('//'):
                arrow_count += 1
                if len(line_numbers) < 10:
                    line_numbers.append(i)
        
        if arrow_count == 0:
            return None
        
        evidence.append(f"Uses arrow functions ({arrow_count} occurrences)")
        
        confidence = min(1.0, arrow_count * 0.1)
        
        return DetectedPattern(
            pattern_type="javascript_arrow_functions",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "arrow_function_count": arrow_count
            }
        )
    
    def _detect_destructuring(
        self,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect destructuring patterns."""
        evidence = []
        line_numbers = []
        destructuring_count = 0
        
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            
            # Look for { ... } = or [ ... ] =
            if (('const {' in line or 'let {' in line or 'var {' in line) or
                ('const [' in line or 'let [' in line or 'var [' in line)):
                destructuring_count += 1
                if len(line_numbers) < 10:
                    line_numbers.append(i)
        
        if destructuring_count == 0:
            return None
        
        evidence.append(f"Uses destructuring ({destructuring_count} occurrences)")
        
        confidence = min(1.0, destructuring_count * 0.15)
        
        return DetectedPattern(
            pattern_type="javascript_destructuring",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "destructuring_count": destructuring_count
            }
        )
    
    def _detect_spread_operators(
        self,
        file_content: str,
        file_path: str
    ) -> Optional[DetectedPattern]:
        """Detect spread operator usage."""
        evidence = []
        line_numbers = []
        spread_count = 0
        
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            if '...' in line and not line.strip().startswith('//'):
                spread_count += 1
                if len(line_numbers) < 10:
                    line_numbers.append(i)
        
        if spread_count == 0:
            return None
        
        evidence.append(f"Uses spread operator ({spread_count} occurrences)")
        
        confidence = min(1.0, spread_count * 0.15)
        
        return DetectedPattern(
            pattern_type="javascript_spread_operator",
            file_path=file_path,
            confidence=confidence,
            evidence=evidence,
            line_numbers=line_numbers[:10],
            metadata={
                "spread_count": spread_count
            }
        )
