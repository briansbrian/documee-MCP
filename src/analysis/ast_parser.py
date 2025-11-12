"""
AST Parser Manager for multi-language code parsing.

This module manages tree-sitter parsers for multiple programming languages
and provides a unified interface for parsing source files into Abstract Syntax Trees.
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from tree_sitter import Language, Parser
from tree_sitter_languages import get_language, get_parser

from .config import AnalysisConfig

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """Result of parsing a file.
    
    Attributes:
        file_path: Path to the parsed file
        language: Detected language (e.g., 'python', 'javascript')
        tree: tree-sitter Tree object
        root_node: Root node of the AST
        has_errors: Whether the parse encountered syntax errors
        error_nodes: List of error nodes found in the tree
        parse_time_ms: Time taken to parse in milliseconds
    """
    file_path: str
    language: str
    tree: Any  # tree-sitter Tree object
    root_node: Any  # tree-sitter Node object
    has_errors: bool
    error_nodes: List[Any]
    parse_time_ms: float


class ASTParserManager:
    """
    Manages tree-sitter parsers for multiple languages.
    
    Uses tree-sitter-languages for pre-built binaries (no compilation needed).
    Supports 50+ languages including Python, JavaScript, TypeScript, Java, Go,
    Rust, C++, C#, Ruby, PHP, and more.
    
    Example:
        >>> config = AnalysisConfig()
        >>> parser_manager = ASTParserManager(config)
        >>> result = parser_manager.parse_file("src/main.py")
        >>> print(result.root_node.type)  # "module"
    """
    
    # Language extension mapping
    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.cs': 'c_sharp',
        '.rb': 'ruby',
        '.php': 'php',
        '.ipynb': 'python',  # Jupyter notebooks (will be handled specially)
    }
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize the AST Parser Manager.
        
        Args:
            config: Analysis configuration containing supported languages
        """
        self.config = config
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        
        # Pre-load parsers for configured languages
        self._initialize_parsers()
        
        logger.info(f"ASTParserManager initialized with {len(self.parsers)} languages")
    
    def parse_file(self, file_path: str) -> ParseResult:
        """
        Parse a file and return AST with metadata.
        
        Args:
            file_path: Path to the file to parse
        
        Returns:
            ParseResult containing the AST and metadata
        
        Raises:
            ValueError: If file is too large or unsupported
            FileNotFoundError: If file doesn't exist
        
        Example:
            >>> result = parser_manager.parse_file("src/main.py")
            >>> print(result.root_node.type)  # "module"
            >>> print(result.has_errors)  # False
        """
        file_path_obj = Path(file_path)
        
        # Check if file exists
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size
        file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(
                f"File too large for parsing: {file_size_mb:.2f}MB "
                f"(max: {self.config.max_file_size_mb}MB)"
            )
        
        # Detect language
        language = self._detect_language(file_path)
        if language == 'unknown':
            logger.warning(f"Unsupported file type: {file_path}")
            raise ValueError(f"Unsupported file extension: {file_path_obj.suffix}")
        
        # Get parser for language
        try:
            parser = self.get_parser(language)
        except Exception as e:
            logger.error(f"Failed to get parser for {language}: {e}")
            raise ValueError(f"Parser not available for language: {language}")
        
        # Read file content
        try:
            with open(file_path, 'rb') as f:
                source_code = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
        
        # Parse the file
        start_time = time.time()
        try:
            tree = parser.parse(source_code)
            parse_time_ms = (time.time() - start_time) * 1000
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            raise ValueError(f"Parse error: {e}")
        
        # Check for errors
        root_node = tree.root_node
        has_errors = root_node.has_error
        error_nodes = self._find_error_nodes(root_node) if has_errors else []
        
        if has_errors:
            logger.warning(
                f"Parse completed with {len(error_nodes)} error(s) in {file_path}"
            )
        else:
            logger.debug(f"Successfully parsed {file_path} in {parse_time_ms:.2f}ms")
        
        return ParseResult(
            file_path=file_path,
            language=language,
            tree=tree,
            root_node=root_node,
            has_errors=has_errors,
            error_nodes=error_nodes,
            parse_time_ms=parse_time_ms
        )
    
    def get_parser(self, language: str) -> Parser:
        """
        Get or create parser for language using tree-sitter-languages.
        
        Args:
            language: Language name (e.g., 'python', 'javascript')
        
        Returns:
            Parser instance for the language
        
        Raises:
            ValueError: If language is not supported
        """
        if language not in self.parsers:
            try:
                # Use pre-built parser from tree-sitter-languages
                self.parsers[language] = get_parser(language)
                self.languages[language] = get_language(language)
                logger.debug(f"Loaded parser for {language}")
            except Exception as e:
                logger.error(f"Failed to load parser for {language}: {e}")
                raise ValueError(f"Language not supported: {language}")
        
        return self.parsers[language]
    
    def _initialize_parsers(self):
        """Pre-load parsers for configured languages."""
        for lang in self.config.supported_languages:
            try:
                self.get_parser(lang)
            except Exception as e:
                logger.warning(f"Failed to initialize parser for {lang}: {e}")
    
    def _detect_language(self, file_path: str) -> str:
        """
        Detect language from file extension.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Language name or 'unknown' if not supported
        """
        ext = Path(file_path).suffix.lower()
        return self.EXTENSION_MAP.get(ext, 'unknown')
    
    def _find_error_nodes(self, node: Any) -> List[Any]:
        """
        Recursively find all error nodes in tree.
        
        Args:
            node: tree-sitter Node to search
        
        Returns:
            List of error nodes found
        """
        errors = []
        
        # Check if this node is an error
        if node.type == 'ERROR' or node.is_missing:
            errors.append(node)
        
        # Recursively check children
        for child in node.children:
            errors.extend(self._find_error_nodes(child))
        
        return errors
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of language names
        """
        return list(self.config.supported_languages)
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of file extensions (e.g., ['.py', '.js'])
        """
        return list(self.EXTENSION_MAP.keys())
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if a file is supported for parsing.
        
        Args:
            file_path: Path to the file
        
        Returns:
            True if file extension is supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.EXTENSION_MAP
