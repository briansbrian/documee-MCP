"""
Linter Integration for Analysis Engine.

This module integrates external linters (pylint, eslint) to provide
additional code quality insights without blocking the analysis pipeline.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Optional

from src.models.analysis_models import LinterIssue
from src.analysis.config import AnalysisConfig

logger = logging.getLogger(__name__)


class LinterIntegration:
    """
    Integrates external linters asynchronously.
    
    This class runs linters (pylint for Python, eslint for JavaScript/TypeScript)
    in a non-blocking manner. If a linter fails or is not installed, the analysis
    continues without linter results.
    
    Example:
        config = AnalysisConfig(enable_linters=True)
        linter = LinterIntegration(config)
        issues = await linter.run_linters("src/main.py", "python")
    """
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize linter integration.
        
        Args:
            config: Analysis configuration with linter settings
        """
        self.config = config
        self.enabled = config.enable_linters
        
        # Map languages to linter functions
        self._linter_map = {
            'python': self._run_pylint,
            'javascript': self._run_eslint,
            'typescript': self._run_eslint
        }
    
    async def run_linters(self, file_path: str, language: str) -> List[LinterIssue]:
        """
        Run appropriate linters for the given file.
        
        This method is non-blocking and gracefully handles linter failures.
        If linters are disabled or the linter fails, an empty list is returned.
        
        Args:
            file_path: Path to the file to lint
            language: Programming language of the file
        
        Returns:
            List of LinterIssue objects, or empty list if linting fails
        
        Example:
            issues = await linter.run_linters("src/main.py", "python")
            for issue in issues:
                print(f"{issue.severity}: {issue.message} at line {issue.line}")
        """
        if not self.enabled:
            logger.debug("Linters disabled in configuration")
            return []
        
        # Get the appropriate linter function
        linter_func = self._linter_map.get(language)
        if not linter_func:
            logger.debug(f"No linter available for language: {language}")
            return []
        
        try:
            logger.info(f"Running linter for {file_path}")
            issues = await linter_func(file_path)
            logger.info(f"Found {len(issues)} linter issues in {file_path}")
            return issues
        except Exception as e:
            # Graceful degradation: log warning but don't fail analysis
            logger.warning(f"Linter failed for {file_path}: {e}")
            return []
    
    async def _run_pylint(self, file_path: str) -> List[LinterIssue]:
        """
        Run pylint on a Python file.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            List of LinterIssue objects from pylint output
        
        Raises:
            Exception: If pylint execution fails
        """
        try:
            # Run pylint with JSON output format
            proc = await asyncio.create_subprocess_exec(
                'pylint',
                file_path,
                '--output-format=json',
                '--score=no',  # Don't include score in output
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            # Pylint exit codes:
            # 0: No errors
            # 1: Fatal message issued
            # 2: Error message issued
            # 4: Warning message issued
            # 8: Refactor message issued
            # 16: Convention message issued
            # 32: Usage error
            if proc.returncode == 32:
                raise Exception(f"Pylint usage error: {stderr.decode()}")
            
            # Parse JSON output
            if stdout:
                issues_data = json.loads(stdout.decode())
                issues = []
                
                for issue in issues_data:
                    issues.append(LinterIssue(
                        tool='pylint',
                        severity=self._map_pylint_severity(issue.get('type', 'warning')),
                        message=issue.get('message', ''),
                        line=issue.get('line', 0),
                        column=issue.get('column', 0),
                        rule=issue.get('message-id', 'unknown')
                    ))
                
                return issues
            
            return []
            
        except FileNotFoundError:
            raise Exception("pylint not found. Install with: pip install pylint")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse pylint output: {e}")
    
    async def _run_eslint(self, file_path: str) -> List[LinterIssue]:
        """
        Run eslint on a JavaScript/TypeScript file.
        
        Args:
            file_path: Path to JavaScript/TypeScript file
        
        Returns:
            List of LinterIssue objects from eslint output
        
        Raises:
            Exception: If eslint execution fails
        """
        try:
            # Run eslint with JSON output format
            proc = await asyncio.create_subprocess_exec(
                'eslint',
                file_path,
                '--format=json',
                '--no-color',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            # ESLint exit codes:
            # 0: No errors
            # 1: One or more errors
            # 2: Configuration error
            if proc.returncode == 2:
                raise Exception(f"ESLint configuration error: {stderr.decode()}")
            
            # Parse JSON output
            if stdout:
                results = json.loads(stdout.decode())
                issues = []
                
                for result in results:
                    for message in result.get('messages', []):
                        issues.append(LinterIssue(
                            tool='eslint',
                            severity=self._map_eslint_severity(message.get('severity', 1)),
                            message=message.get('message', ''),
                            line=message.get('line', 0),
                            column=message.get('column', 0),
                            rule=message.get('ruleId', 'unknown')
                        ))
                
                return issues
            
            return []
            
        except FileNotFoundError:
            raise Exception("eslint not found. Install with: npm install -g eslint")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse eslint output: {e}")
    
    def _map_pylint_severity(self, pylint_type: str) -> str:
        """
        Map pylint message type to standard severity.
        
        Args:
            pylint_type: Pylint message type (error, warning, etc.)
        
        Returns:
            Standard severity string: 'error', 'warning', or 'info'
        """
        mapping = {
            'error': 'error',
            'fatal': 'error',
            'warning': 'warning',
            'refactor': 'info',
            'convention': 'info',
            'info': 'info'
        }
        return mapping.get(pylint_type.lower(), 'warning')
    
    def _map_eslint_severity(self, eslint_severity: int) -> str:
        """
        Map eslint severity number to standard severity.
        
        Args:
            eslint_severity: ESLint severity (0, 1, or 2)
        
        Returns:
            Standard severity string: 'error', 'warning', or 'info'
        """
        mapping = {
            0: 'info',
            1: 'warning',
            2: 'error'
        }
        return mapping.get(eslint_severity, 'warning')
