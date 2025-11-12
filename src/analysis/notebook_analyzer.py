"""
Jupyter Notebook Analyzer

Extracts code cells from .ipynb files for analysis.
Handles cell concatenation and line number mapping.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

try:
    import nbformat
except ImportError:
    nbformat = None

logger = logging.getLogger(__name__)


@dataclass
class CodeCell:
    """Represents a single code cell from a Jupyter notebook."""
    content: str
    start_line: int
    end_line: int
    execution_count: Optional[int]
    cell_index: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        from dataclasses import asdict
        return asdict(self)


@dataclass
class NotebookCode:
    """Represents extracted code from a Jupyter notebook."""
    notebook_path: str
    cells: List[CodeCell]
    full_code: str
    total_cells: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        from dataclasses import asdict
        return asdict(self)


class NotebookAnalyzer:
    """Analyzes Jupyter notebooks by extracting code cells.
    
    This class handles .ipynb files by:
    1. Parsing the notebook JSON structure
    2. Extracting only code cells (ignoring markdown, raw)
    3. Concatenating cells into a single code string
    4. Tracking cell boundaries for line number mapping
    
    Example:
        analyzer = NotebookAnalyzer()
        notebook_code = analyzer.extract_code("analysis.ipynb")
        print(f"Total cells: {notebook_code.total_cells}")
        print(f"Full code length: {len(notebook_code.full_code)}")
    """
    
    def __init__(self):
        """Initialize the notebook analyzer."""
        if nbformat is None:
            logger.warning(
                "nbformat not installed. Jupyter notebook support disabled. "
                "Install with: pip install nbformat>=5.9.0"
            )
        self.nbformat_available = nbformat is not None
    
    def extract_code(self, notebook_path: str) -> NotebookCode:
        """Extract code cells from a Jupyter notebook.
        
        Args:
            notebook_path: Path to the .ipynb file
            
        Returns:
            NotebookCode containing extracted cells and concatenated code
            
        Raises:
            ValueError: If nbformat is not installed
            FileNotFoundError: If notebook file doesn't exist
            json.JSONDecodeError: If notebook file is invalid JSON
        """
        if not self.nbformat_available:
            raise ValueError(
                "nbformat is required for notebook analysis. "
                "Install with: pip install nbformat>=5.9.0"
            )
        
        notebook_path_obj = Path(notebook_path)
        if not notebook_path_obj.exists():
            raise FileNotFoundError(f"Notebook not found: {notebook_path}")
        
        logger.info(f"Extracting code from notebook: {notebook_path}")
        
        # Read and parse notebook
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid notebook JSON: {notebook_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to read notebook {notebook_path}: {e}")
            raise
        
        # Extract code cells
        code_cells = []
        line_offset = 0
        cell_index = 0
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                source = cell.source
                
                # Handle empty cells
                if not source:
                    source = ""
                
                # Split into lines to calculate boundaries
                lines = source.split('\n')
                num_lines = len(lines)
                
                code_cells.append(CodeCell(
                    content=source,
                    start_line=line_offset,
                    end_line=line_offset + num_lines - 1,
                    execution_count=cell.get('execution_count'),
                    cell_index=cell_index
                ))
                
                # Update line offset (+1 for cell boundary)
                line_offset += num_lines + 1
                cell_index += 1
        
        # Concatenate all code cells with newline separator
        full_code = '\n'.join(cell.content for cell in code_cells)
        
        logger.info(
            f"Extracted {len(code_cells)} code cells from {notebook_path} "
            f"({len(full_code)} characters)"
        )
        
        return NotebookCode(
            notebook_path=notebook_path,
            cells=code_cells,
            full_code=full_code,
            total_cells=len(code_cells)
        )
    
    def map_line_to_cell(
        self, 
        line_number: int, 
        notebook_code: NotebookCode
    ) -> Optional[int]:
        """Map a line number in concatenated code to its cell index.
        
        This is useful for mapping error messages or analysis results
        back to the original notebook cell.
        
        Args:
            line_number: Line number in the concatenated code (0-indexed)
            notebook_code: NotebookCode object from extract_code()
            
        Returns:
            Cell index (0-indexed) or None if line is in cell boundary
            
        Example:
            notebook_code = analyzer.extract_code("notebook.ipynb")
            cell_idx = analyzer.map_line_to_cell(42, notebook_code)
            if cell_idx is not None:
                print(f"Line 42 is in cell {cell_idx}")
        """
        for cell in notebook_code.cells:
            if cell.start_line <= line_number <= cell.end_line:
                return cell.cell_index
        
        # Line is in a cell boundary (the newline between cells)
        return None
    
    def get_cell_by_index(
        self, 
        cell_index: int, 
        notebook_code: NotebookCode
    ) -> Optional[CodeCell]:
        """Get a code cell by its index.
        
        Args:
            cell_index: Index of the cell (0-indexed)
            notebook_code: NotebookCode object from extract_code()
            
        Returns:
            CodeCell or None if index is out of range
        """
        for cell in notebook_code.cells:
            if cell.cell_index == cell_index:
                return cell
        return None
    
    def is_notebook_file(self, file_path: str) -> bool:
        """Check if a file is a Jupyter notebook.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file has .ipynb extension
        """
        return Path(file_path).suffix.lower() == '.ipynb'
