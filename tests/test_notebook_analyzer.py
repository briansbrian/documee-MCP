"""
Tests for Jupyter Notebook Analyzer.

Tests code cell extraction, line mapping, and notebook parsing.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

from src.analysis.notebook_analyzer import (
    NotebookAnalyzer,
    NotebookCode,
    CodeCell
)


@pytest.fixture
def sample_notebook_content():
    """Create a sample notebook JSON structure."""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "# Test Notebook"
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": "import numpy as np\nimport pandas as pd"
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [],
                "source": "def calculate_sum(a, b):\n    \"\"\"Calculate sum of two numbers.\"\"\"\n    return a + b"
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "## Analysis"
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [],
                "source": "result = calculate_sum(10, 20)\nprint(f\"Result: {result}\")"
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ""
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


@pytest.fixture
def temp_notebook(sample_notebook_content):
    """Create a temporary notebook file."""
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.ipynb',
        delete=False,
        encoding='utf-8'
    ) as f:
        json.dump(sample_notebook_content, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass


@pytest.fixture
def analyzer():
    """Create a NotebookAnalyzer instance."""
    return NotebookAnalyzer()


class TestNotebookAnalyzerInitialization:
    """Test NotebookAnalyzer initialization."""
    
    def test_initialization(self, analyzer):
        """Test that analyzer initializes correctly."""
        assert analyzer is not None
        # nbformat should be available in our environment
        assert analyzer.nbformat_available is True
    
    def test_initialization_without_nbformat(self, monkeypatch):
        """Test initialization when nbformat is not available."""
        # Mock nbformat as None
        import src.analysis.notebook_analyzer as nb_module
        monkeypatch.setattr(nb_module, 'nbformat', None)
        
        analyzer = NotebookAnalyzer()
        assert analyzer.nbformat_available is False


class TestExtractCode:
    """Test code extraction from notebooks."""
    
    def test_extract_code_basic(self, analyzer, temp_notebook):
        """Test basic code extraction from notebook."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        assert notebook_code is not None
        assert notebook_code.notebook_path == temp_notebook
        assert notebook_code.total_cells == 4  # 4 code cells (including empty)
        assert len(notebook_code.cells) == 4
    
    def test_extract_code_content(self, analyzer, temp_notebook):
        """Test that extracted code content is correct."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        # Check first code cell
        assert notebook_code.cells[0].content == "import numpy as np\nimport pandas as pd"
        assert notebook_code.cells[0].execution_count == 1
        assert notebook_code.cells[0].cell_index == 0
        
        # Check second code cell
        assert "def calculate_sum" in notebook_code.cells[1].content
        assert notebook_code.cells[1].execution_count == 2
        assert notebook_code.cells[1].cell_index == 1
        
        # Check third code cell
        assert "result = calculate_sum" in notebook_code.cells[2].content
        assert notebook_code.cells[2].execution_count == 3
        
        # Check empty cell
        assert notebook_code.cells[3].content == ""
        assert notebook_code.cells[3].execution_count is None
    
    def test_extract_code_line_boundaries(self, analyzer, temp_notebook):
        """Test that line boundaries are tracked correctly."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        # First cell: 2 lines (0-1)
        assert notebook_code.cells[0].start_line == 0
        assert notebook_code.cells[0].end_line == 1
        
        # Second cell: 3 lines (3-5), +1 for cell boundary
        assert notebook_code.cells[1].start_line == 3
        assert notebook_code.cells[1].end_line == 5
        
        # Third cell: 2 lines (7-8)
        assert notebook_code.cells[2].start_line == 7
        assert notebook_code.cells[2].end_line == 8
    
    def test_extract_code_concatenation(self, analyzer, temp_notebook):
        """Test that full code is concatenated correctly."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        # Full code should contain all code cells joined by newlines
        assert "import numpy as np" in notebook_code.full_code
        assert "def calculate_sum" in notebook_code.full_code
        assert "result = calculate_sum" in notebook_code.full_code
        
        # Should not contain markdown
        assert "# Test Notebook" not in notebook_code.full_code
        assert "## Analysis" not in notebook_code.full_code
    
    def test_extract_code_nonexistent_file(self, analyzer):
        """Test extraction from non-existent file."""
        with pytest.raises(FileNotFoundError):
            analyzer.extract_code("nonexistent_notebook.ipynb")
    
    def test_extract_code_invalid_json(self, analyzer):
        """Test extraction from invalid JSON file."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.ipynb',
            delete=False
        ) as f:
            f.write("invalid json content")
            temp_path = f.name
        
        try:
            # nbformat raises NotJSONError, not json.JSONDecodeError
            with pytest.raises(Exception):  # Catch any exception from nbformat
                analyzer.extract_code(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_extract_code_without_nbformat(self, analyzer, temp_notebook, monkeypatch):
        """Test extraction when nbformat is not available."""
        # Mock nbformat as unavailable
        analyzer.nbformat_available = False
        
        with pytest.raises(ValueError, match="nbformat is required"):
            analyzer.extract_code(temp_notebook)


class TestMapLineToCell:
    """Test line number to cell mapping."""
    
    def test_map_line_to_cell_first_cell(self, analyzer, temp_notebook):
        """Test mapping lines in first cell."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        # Lines 0-1 should map to cell 0
        assert analyzer.map_line_to_cell(0, notebook_code) == 0
        assert analyzer.map_line_to_cell(1, notebook_code) == 0
    
    def test_map_line_to_cell_middle_cell(self, analyzer, temp_notebook):
        """Test mapping lines in middle cell."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        # Lines 3-5 should map to cell 1
        assert analyzer.map_line_to_cell(3, notebook_code) == 1
        assert analyzer.map_line_to_cell(4, notebook_code) == 1
        assert analyzer.map_line_to_cell(5, notebook_code) == 1
    
    def test_map_line_to_cell_boundary(self, analyzer, temp_notebook):
        """Test mapping lines at cell boundaries."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        # Line 2 is a cell boundary (between cells 0 and 1)
        result = analyzer.map_line_to_cell(2, notebook_code)
        assert result is None
    
    def test_map_line_to_cell_out_of_range(self, analyzer, temp_notebook):
        """Test mapping line number out of range."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        # Line 1000 doesn't exist
        result = analyzer.map_line_to_cell(1000, notebook_code)
        assert result is None


class TestGetCellByIndex:
    """Test getting cells by index."""
    
    def test_get_cell_by_index_valid(self, analyzer, temp_notebook):
        """Test getting cell by valid index."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        cell = analyzer.get_cell_by_index(0, notebook_code)
        assert cell is not None
        assert cell.cell_index == 0
        assert "import numpy" in cell.content
        
        cell = analyzer.get_cell_by_index(1, notebook_code)
        assert cell is not None
        assert cell.cell_index == 1
        assert "def calculate_sum" in cell.content
    
    def test_get_cell_by_index_invalid(self, analyzer, temp_notebook):
        """Test getting cell by invalid index."""
        notebook_code = analyzer.extract_code(temp_notebook)
        
        cell = analyzer.get_cell_by_index(999, notebook_code)
        assert cell is None


class TestIsNotebookFile:
    """Test notebook file detection."""
    
    def test_is_notebook_file_valid(self, analyzer):
        """Test detection of valid notebook files."""
        assert analyzer.is_notebook_file("test.ipynb") is True
        assert analyzer.is_notebook_file("path/to/notebook.ipynb") is True
        assert analyzer.is_notebook_file("NOTEBOOK.IPYNB") is True
    
    def test_is_notebook_file_invalid(self, analyzer):
        """Test detection of non-notebook files."""
        assert analyzer.is_notebook_file("test.py") is False
        assert analyzer.is_notebook_file("test.js") is False
        assert analyzer.is_notebook_file("test.txt") is False
        assert analyzer.is_notebook_file("test") is False


class TestCodeCellDataclass:
    """Test CodeCell dataclass."""
    
    def test_code_cell_creation(self):
        """Test creating a CodeCell."""
        cell = CodeCell(
            content="print('hello')",
            start_line=0,
            end_line=0,
            execution_count=1,
            cell_index=0
        )
        
        assert cell.content == "print('hello')"
        assert cell.start_line == 0
        assert cell.end_line == 0
        assert cell.execution_count == 1
        assert cell.cell_index == 0


class TestNotebookCodeDataclass:
    """Test NotebookCode dataclass."""
    
    def test_notebook_code_creation(self):
        """Test creating a NotebookCode."""
        cells = [
            CodeCell("code1", 0, 0, 1, 0),
            CodeCell("code2", 2, 2, 2, 1)
        ]
        
        notebook_code = NotebookCode(
            notebook_path="test.ipynb",
            cells=cells,
            full_code="code1\ncode2",
            total_cells=2
        )
        
        assert notebook_code.notebook_path == "test.ipynb"
        assert len(notebook_code.cells) == 2
        assert notebook_code.full_code == "code1\ncode2"
        assert notebook_code.total_cells == 2
