"""
Tests for Linter Integration.

Tests pylint integration, eslint integration, and graceful failure handling.
"""

import pytest
import asyncio
import os
import tempfile
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.analysis.linter_integration import LinterIntegration
from src.analysis.config import AnalysisConfig
from src.models.analysis_models import LinterIssue


def create_test_file(content: str, extension: str) -> str:
    """Create a temporary test file."""
    fd, path = tempfile.mkstemp(suffix=extension, text=True)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


@pytest.fixture
def config_enabled():
    """Create test configuration with linters enabled."""
    config = AnalysisConfig()
    config.enable_linters = True
    return config


@pytest.fixture
def config_disabled():
    """Create test configuration with linters disabled."""
    config = AnalysisConfig()
    config.enable_linters = False
    return config


@pytest.fixture
def linter_enabled(config_enabled):
    """Create linter integration with linters enabled."""
    return LinterIntegration(config_enabled)


@pytest.fixture
def linter_disabled(config_disabled):
    """Create linter integration with linters disabled."""
    return LinterIntegration(config_disabled)


class TestPylintIntegration:
    """Test pylint integration with sample Python files."""
    
    @pytest.mark.asyncio
    async def test_pylint_with_valid_python_file(self, linter_enabled):
        """Test pylint on a valid Python file."""
        code = '''def hello_world():
    """A simple function."""
    print("Hello, World!")
    return True
'''
        path = create_test_file(code, '.py')
        try:
            # Mock subprocess to simulate pylint output
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b'[]', b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            # Valid file should have no issues (or empty list)
            assert isinstance(issues, list)
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_pylint_with_issues(self, linter_enabled):
        """Test pylint detecting issues in Python file."""
        code = '''def bad_function():
    x = 1
    y = 2
    # Unused variables should trigger pylint warnings
'''
        path = create_test_file(code, '.py')
        try:
            # Mock pylint output with issues
            pylint_output = json.dumps([
                {
                    'type': 'warning',
                    'message': 'Unused variable x',
                    'line': 2,
                    'column': 4,
                    'message-id': 'W0612'
                },
                {
                    'type': 'warning',
                    'message': 'Unused variable y',
                    'line': 3,
                    'column': 4,
                    'message-id': 'W0612'
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 4  # Warning exit code
            mock_proc.communicate = AsyncMock(return_value=(pylint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            assert len(issues) == 2
            assert all(isinstance(issue, LinterIssue) for issue in issues)
            assert issues[0].tool == 'pylint'
            assert issues[0].severity == 'warning'
            assert issues[0].line == 2
            assert issues[0].rule == 'W0612'
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_pylint_with_errors(self, linter_enabled):
        """Test pylint detecting errors in Python file."""
        code = '''def error_function():
    # This will trigger errors
    undefined_variable
'''
        path = create_test_file(code, '.py')
        try:
            # Mock pylint output with errors
            pylint_output = json.dumps([
                {
                    'type': 'error',
                    'message': 'Undefined variable: undefined_variable',
                    'line': 3,
                    'column': 4,
                    'message-id': 'E0602'
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 2  # Error exit code
            mock_proc.communicate = AsyncMock(return_value=(pylint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            assert len(issues) == 1
            assert issues[0].severity == 'error'
            assert issues[0].tool == 'pylint'
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_pylint_severity_mapping(self, linter_enabled):
        """Test pylint severity mapping to standard severities."""
        path = create_test_file('# dummy', '.py')
        try:
            # Mock pylint output with different severity types
            pylint_output = json.dumps([
                {'type': 'error', 'message': 'Error', 'line': 1, 'column': 0, 'message-id': 'E0001'},
                {'type': 'fatal', 'message': 'Fatal', 'line': 1, 'column': 0, 'message-id': 'F0001'},
                {'type': 'warning', 'message': 'Warning', 'line': 1, 'column': 0, 'message-id': 'W0001'},
                {'type': 'refactor', 'message': 'Refactor', 'line': 1, 'column': 0, 'message-id': 'R0001'},
                {'type': 'convention', 'message': 'Convention', 'line': 1, 'column': 0, 'message-id': 'C0001'},
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(pylint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            assert len(issues) == 5
            # Check severity mapping
            assert issues[0].severity == 'error'  # error -> error
            assert issues[1].severity == 'error'  # fatal -> error
            assert issues[2].severity == 'warning'  # warning -> warning
            assert issues[3].severity == 'info'  # refactor -> info
            assert issues[4].severity == 'info'  # convention -> info
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestEslintIntegration:
    """Test eslint integration with sample JavaScript files."""
    
    @pytest.mark.asyncio
    async def test_eslint_with_valid_javascript_file(self, linter_enabled):
        """Test eslint on a valid JavaScript file."""
        code = '''function helloWorld() {
    console.log("Hello, World!");
    return true;
}
'''
        path = create_test_file(code, '.js')
        try:
            # Mock subprocess to simulate eslint output
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b'[]', b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'javascript')
            
            # Valid file should have no issues (or empty list)
            assert isinstance(issues, list)
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_eslint_with_issues(self, linter_enabled):
        """Test eslint detecting issues in JavaScript file."""
        code = '''function badFunction() {
    var x = 1;
    var y = 2;
    // Unused variables
}
'''
        path = create_test_file(code, '.js')
        try:
            # Mock eslint output with issues
            eslint_output = json.dumps([
                {
                    'filePath': path,
                    'messages': [
                        {
                            'severity': 1,
                            'message': "'x' is assigned a value but never used.",
                            'line': 2,
                            'column': 9,
                            'ruleId': 'no-unused-vars'
                        },
                        {
                            'severity': 1,
                            'message': "'y' is assigned a value but never used.",
                            'line': 3,
                            'column': 9,
                            'ruleId': 'no-unused-vars'
                        }
                    ]
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 1  # Issues found
            mock_proc.communicate = AsyncMock(return_value=(eslint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'javascript')
            
            assert len(issues) == 2
            assert all(isinstance(issue, LinterIssue) for issue in issues)
            assert issues[0].tool == 'eslint'
            assert issues[0].severity == 'warning'
            assert issues[0].line == 2
            assert issues[0].rule == 'no-unused-vars'
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_eslint_with_typescript_file(self, linter_enabled):
        """Test eslint on TypeScript file."""
        code = '''function greet(name: string): string {
    return `Hello, ${name}!`;
}
'''
        path = create_test_file(code, '.ts')
        try:
            # Mock eslint output
            eslint_output = json.dumps([
                {
                    'filePath': path,
                    'messages': []
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(eslint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'typescript')
            
            assert isinstance(issues, list)
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_eslint_severity_mapping(self, linter_enabled):
        """Test eslint severity mapping to standard severities."""
        path = create_test_file('// dummy', '.js')
        try:
            # Mock eslint output with different severity levels
            eslint_output = json.dumps([
                {
                    'filePath': path,
                    'messages': [
                        {'severity': 0, 'message': 'Info', 'line': 1, 'column': 1, 'ruleId': 'info-rule'},
                        {'severity': 1, 'message': 'Warning', 'line': 1, 'column': 1, 'ruleId': 'warn-rule'},
                        {'severity': 2, 'message': 'Error', 'line': 1, 'column': 1, 'ruleId': 'error-rule'},
                    ]
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 1
            mock_proc.communicate = AsyncMock(return_value=(eslint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'javascript')
            
            assert len(issues) == 3
            # Check severity mapping
            assert issues[0].severity == 'info'  # 0 -> info
            assert issues[1].severity == 'warning'  # 1 -> warning
            assert issues[2].severity == 'error'  # 2 -> error
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestGracefulFailureHandling:
    """Test graceful failure handling for linter integration."""
    
    @pytest.mark.asyncio
    async def test_linters_disabled(self, linter_disabled):
        """Test that linters return empty list when disabled."""
        path = create_test_file('# test', '.py')
        try:
            issues = await linter_disabled.run_linters(path, 'python')
            
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_unsupported_language(self, linter_enabled):
        """Test graceful handling of unsupported language."""
        path = create_test_file('/* test */', '.cpp')
        try:
            issues = await linter_enabled.run_linters(path, 'cpp')
            
            # Should return empty list for unsupported language
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_pylint_not_installed(self, linter_enabled):
        """Test graceful handling when pylint is not installed."""
        path = create_test_file('# test', '.py')
        try:
            # Mock FileNotFoundError to simulate pylint not installed
            with patch('asyncio.create_subprocess_exec', side_effect=FileNotFoundError()):
                issues = await linter_enabled.run_linters(path, 'python')
            
            # Should return empty list and not crash
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_eslint_not_installed(self, linter_enabled):
        """Test graceful handling when eslint is not installed."""
        path = create_test_file('// test', '.js')
        try:
            # Mock FileNotFoundError to simulate eslint not installed
            with patch('asyncio.create_subprocess_exec', side_effect=FileNotFoundError()):
                issues = await linter_enabled.run_linters(path, 'javascript')
            
            # Should return empty list and not crash
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_pylint_usage_error(self, linter_enabled):
        """Test handling of pylint usage error (exit code 32)."""
        path = create_test_file('# test', '.py')
        try:
            # Mock pylint usage error
            mock_proc = AsyncMock()
            mock_proc.returncode = 32
            mock_proc.communicate = AsyncMock(return_value=(b'', b'Usage error'))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            # Should return empty list and not crash
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_eslint_configuration_error(self, linter_enabled):
        """Test handling of eslint configuration error (exit code 2)."""
        path = create_test_file('// test', '.js')
        try:
            # Mock eslint configuration error
            mock_proc = AsyncMock()
            mock_proc.returncode = 2
            mock_proc.communicate = AsyncMock(return_value=(b'', b'Configuration error'))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'javascript')
            
            # Should return empty list and not crash
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_invalid_json_output(self, linter_enabled):
        """Test handling of invalid JSON output from linter."""
        path = create_test_file('# test', '.py')
        try:
            # Mock invalid JSON output
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b'invalid json', b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            # Should return empty list and not crash
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_empty_output(self, linter_enabled):
        """Test handling of empty output from linter."""
        path = create_test_file('# test', '.py')
        try:
            # Mock empty output
            mock_proc = AsyncMock()
            mock_proc.returncode = 0
            mock_proc.communicate = AsyncMock(return_value=(b'', b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            # Should return empty list
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_linter_timeout(self, linter_enabled):
        """Test handling of linter timeout."""
        path = create_test_file('# test', '.py')
        try:
            # Mock timeout exception
            with patch('asyncio.create_subprocess_exec', side_effect=asyncio.TimeoutError()):
                issues = await linter_enabled.run_linters(path, 'python')
            
            # Should return empty list and not crash
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_generic_exception(self, linter_enabled):
        """Test handling of generic exception during linting."""
        path = create_test_file('# test', '.py')
        try:
            # Mock generic exception
            with patch('asyncio.create_subprocess_exec', side_effect=Exception('Generic error')):
                issues = await linter_enabled.run_linters(path, 'python')
            
            # Should return empty list and not crash
            assert issues == []
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestLinterConfiguration:
    """Test linter configuration and initialization."""
    
    def test_linter_enabled_initialization(self, config_enabled):
        """Test initialization with linters enabled."""
        linter = LinterIntegration(config_enabled)
        
        assert linter.enabled is True
        assert linter.config == config_enabled
        assert 'python' in linter._linter_map
        assert 'javascript' in linter._linter_map
        assert 'typescript' in linter._linter_map
    
    def test_linter_disabled_initialization(self, config_disabled):
        """Test initialization with linters disabled."""
        linter = LinterIntegration(config_disabled)
        
        assert linter.enabled is False
        assert linter.config == config_disabled
    
    @pytest.mark.asyncio
    async def test_language_mapping(self, linter_enabled):
        """Test that languages are correctly mapped to linter functions."""
        # Python should use pylint
        assert 'python' in linter_enabled._linter_map
        
        # JavaScript and TypeScript should use eslint
        assert 'javascript' in linter_enabled._linter_map
        assert 'typescript' in linter_enabled._linter_map
        
        # Both should point to the same function
        assert linter_enabled._linter_map['javascript'] == linter_enabled._linter_map['typescript']


class TestLinterIssueCreation:
    """Test creation of LinterIssue objects."""
    
    @pytest.mark.asyncio
    async def test_pylint_issue_fields(self, linter_enabled):
        """Test that pylint issues have all required fields."""
        path = create_test_file('# test', '.py')
        try:
            pylint_output = json.dumps([
                {
                    'type': 'warning',
                    'message': 'Test message',
                    'line': 10,
                    'column': 5,
                    'message-id': 'W1234'
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 4
            mock_proc.communicate = AsyncMock(return_value=(pylint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            assert len(issues) == 1
            issue = issues[0]
            assert issue.tool == 'pylint'
            assert issue.severity == 'warning'
            assert issue.message == 'Test message'
            assert issue.line == 10
            assert issue.column == 5
            assert issue.rule == 'W1234'
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_eslint_issue_fields(self, linter_enabled):
        """Test that eslint issues have all required fields."""
        path = create_test_file('// test', '.js')
        try:
            eslint_output = json.dumps([
                {
                    'filePath': path,
                    'messages': [
                        {
                            'severity': 2,
                            'message': 'Test error message',
                            'line': 15,
                            'column': 8,
                            'ruleId': 'no-undef'
                        }
                    ]
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 1
            mock_proc.communicate = AsyncMock(return_value=(eslint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'javascript')
            
            assert len(issues) == 1
            issue = issues[0]
            assert issue.tool == 'eslint'
            assert issue.severity == 'error'
            assert issue.message == 'Test error message'
            assert issue.line == 15
            assert issue.column == 8
            assert issue.rule == 'no-undef'
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_missing_optional_fields(self, linter_enabled):
        """Test handling of missing optional fields in linter output."""
        path = create_test_file('# test', '.py')
        try:
            # Pylint output with missing optional fields
            pylint_output = json.dumps([
                {
                    'type': 'warning',
                    'message': 'Test message',
                    'line': 1,
                    'column': 0
                    # Missing 'message-id'
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 4
            mock_proc.communicate = AsyncMock(return_value=(pylint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            assert len(issues) == 1
            issue = issues[0]
            assert issue.rule == 'unknown'  # Default value for missing field
        finally:
            try:
                os.unlink(path)
            except:
                pass


class TestMultipleIssues:
    """Test handling of multiple issues from linters."""
    
    @pytest.mark.asyncio
    async def test_multiple_pylint_issues(self, linter_enabled):
        """Test handling multiple issues from pylint."""
        path = create_test_file('# test', '.py')
        try:
            pylint_output = json.dumps([
                {'type': 'error', 'message': 'Error 1', 'line': 1, 'column': 0, 'message-id': 'E0001'},
                {'type': 'warning', 'message': 'Warning 1', 'line': 2, 'column': 0, 'message-id': 'W0001'},
                {'type': 'warning', 'message': 'Warning 2', 'line': 3, 'column': 0, 'message-id': 'W0002'},
                {'type': 'info', 'message': 'Info 1', 'line': 4, 'column': 0, 'message-id': 'I0001'},
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 6  # Error (2) + Warning (4)
            mock_proc.communicate = AsyncMock(return_value=(pylint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'python')
            
            assert len(issues) == 4
            assert issues[0].severity == 'error'
            assert issues[1].severity == 'warning'
            assert issues[2].severity == 'warning'
            assert issues[3].severity == 'info'
        finally:
            try:
                os.unlink(path)
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_multiple_eslint_issues(self, linter_enabled):
        """Test handling multiple issues from eslint."""
        path = create_test_file('// test', '.js')
        try:
            eslint_output = json.dumps([
                {
                    'filePath': path,
                    'messages': [
                        {'severity': 2, 'message': 'Error 1', 'line': 1, 'column': 1, 'ruleId': 'rule1'},
                        {'severity': 1, 'message': 'Warning 1', 'line': 2, 'column': 1, 'ruleId': 'rule2'},
                        {'severity': 1, 'message': 'Warning 2', 'line': 3, 'column': 1, 'ruleId': 'rule3'},
                    ]
                }
            ]).encode()
            
            mock_proc = AsyncMock()
            mock_proc.returncode = 1
            mock_proc.communicate = AsyncMock(return_value=(eslint_output, b''))
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
                issues = await linter_enabled.run_linters(path, 'javascript')
            
            assert len(issues) == 3
            assert issues[0].severity == 'error'
            assert issues[1].severity == 'warning'
            assert issues[2].severity == 'warning'
        finally:
            try:
                os.unlink(path)
            except:
                pass
