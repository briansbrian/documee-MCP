"""
Symbol Extractor for extracting functions, classes, and other symbols from AST.

This module extracts structured information about code symbols (functions, classes,
imports, etc.) from parsed Abstract Syntax Trees across multiple languages.
"""

import logging
from typing import List, Optional, Any
from dataclasses import dataclass, field

from .ast_parser import ParseResult

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """Information about a function or method.
    
    Attributes:
        name: Function name
        parameters: List of parameter names
        return_type: Return type annotation (if available)
        docstring: Function docstring/documentation
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        complexity: Cyclomatic complexity score
        is_async: Whether function is async
        decorators: List of decorator names
    """
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    complexity: int = 1
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """Information about a class.
    
    Attributes:
        name: Class name
        methods: List of methods in the class
        base_classes: List of parent class names
        docstring: Class docstring/documentation
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        decorators: List of decorator names
    """
    name: str
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    decorators: List[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    """Information about an import statement.
    
    Attributes:
        module: Module name being imported
        imported_symbols: List of specific symbols imported (empty for 'import x')
        is_relative: Whether this is a relative import
        import_type: Type of import ('import', 'from_import', 'require', 'es6_import')
        line_number: Line number of the import
    """
    module: str
    imported_symbols: List[str] = field(default_factory=list)
    is_relative: bool = False
    import_type: str = "import"
    line_number: int = 0


@dataclass
class SymbolInfo:
    """Complete symbol information for a file.
    
    Attributes:
        functions: List of functions found in the file
        classes: List of classes found in the file
        imports: List of import statements
        exports: List of exported symbols (for JS/TS)
    """
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


class SymbolExtractor:
    """
    Extracts functions, classes, and other symbols from AST.
    
    Supports multiple languages with language-specific extraction logic.
    """
    
    def __init__(self):
        """Initialize the Symbol Extractor."""
        logger.debug("SymbolExtractor initialized")
    
    def extract_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """
        Extract all symbols from parsed file.
        
        Args:
            parse_result: Result from AST parser
        
        Returns:
            SymbolInfo containing all extracted symbols
        
        Example:
            >>> symbols = extractor.extract_symbols(parse_result)
            >>> print(f"Found {len(symbols.functions)} functions")
        """
        language = parse_result.language
        
        # Route to language-specific extractor
        if language == 'python':
            return self._extract_python_symbols(parse_result)
        elif language in ['javascript', 'typescript', 'tsx']:
            return self._extract_javascript_symbols(parse_result)
        elif language == 'java':
            return self._extract_java_symbols(parse_result)
        elif language == 'go':
            return self._extract_go_symbols(parse_result)
        elif language == 'rust':
            return self._extract_rust_symbols(parse_result)
        elif language in ['cpp', 'c']:
            return self._extract_cpp_symbols(parse_result)
        elif language == 'c_sharp':
            return self._extract_csharp_symbols(parse_result)
        elif language == 'ruby':
            return self._extract_ruby_symbols(parse_result)
        elif language == 'php':
            return self._extract_php_symbols(parse_result)
        else:
            logger.warning(f"No symbol extractor for language: {language}")
            return SymbolInfo()
    
    def _extract_python_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """
        Extract symbols from Python AST.
        
        Args:
            parse_result: Parsed Python file
        
        Returns:
            SymbolInfo with Python symbols
        """
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract imports
        symbols.imports = self._extract_python_imports(root_node)
        
        # Extract top-level functions and classes
        for node in root_node.children:
            if node.type == 'function_definition':
                func_info = self._extract_python_function(node)
                if func_info:
                    symbols.functions.append(func_info)
            
            elif node.type == 'class_definition':
                class_info = self._extract_python_class(node)
                if class_info:
                    symbols.classes.append(class_info)
        
        logger.debug(
            f"Extracted {len(symbols.functions)} functions, "
            f"{len(symbols.classes)} classes, "
            f"{len(symbols.imports)} imports from Python file"
        )
        
        return symbols
    
    def _extract_python_function(self, node: Any) -> Optional[FunctionInfo]:
        """
        Extract function information from Python function_definition node.
        
        Args:
            node: tree-sitter function_definition node
        
        Returns:
            FunctionInfo or None if extraction fails
        """
        try:
            # Get function name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get parameters
            parameters = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                parameters = self._extract_python_parameters(params_node)
            
            # Get return type
            return_type = None
            return_type_node = node.child_by_field_name('return_type')
            if return_type_node:
                return_type = return_type_node.text.decode('utf-8')
            
            # Get docstring
            docstring = self._extract_python_docstring(node)
            
            # Get line numbers (tree-sitter uses 0-indexed, convert to 1-indexed)
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Check if async
            is_async = False
            for child in node.children:
                if child.type == 'async' or child.text == b'async':
                    is_async = True
                    break
            
            # Get decorators
            decorators = self._extract_python_decorators(node)
            
            # Calculate complexity
            complexity = self._calculate_complexity(node)
            
            return FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=return_type,
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                complexity=complexity,
                is_async=is_async,
                decorators=decorators
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract Python function: {e}")
            return None
    
    def _extract_python_parameters(self, params_node: Any) -> List[str]:
        """Extract parameter names from Python parameters node."""
        parameters = []
        
        for child in params_node.children:
            if child.type == 'identifier':
                parameters.append(child.text.decode('utf-8'))
            elif child.type in ['typed_parameter', 'default_parameter', 'typed_default_parameter']:
                # Get the parameter name from typed/default parameters
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        parameters.append(subchild.text.decode('utf-8'))
                        break
        
        return parameters
    
    def _extract_python_docstring(self, node: Any) -> Optional[str]:
        """Extract docstring from Python function or class."""
        # Look for string as first statement in body
        body_node = node.child_by_field_name('body')
        if not body_node:
            return None
        
        for child in body_node.children:
            if child.type == 'expression_statement':
                for subchild in child.children:
                    if subchild.type == 'string':
                        # Remove quotes and decode
                        docstring = subchild.text.decode('utf-8')
                        # Remove triple quotes
                        for quote in ['"""', "'''", '"', "'"]:
                            if docstring.startswith(quote) and docstring.endswith(quote):
                                docstring = docstring[len(quote):-len(quote)]
                                break
                        return docstring.strip()
                break
        
        return None
    
    def _extract_python_decorators(self, node: Any) -> List[str]:
        """Extract decorator names from Python function or class."""
        decorators = []
        
        # Look for decorated_definition parent
        parent = node.parent
        if parent and parent.type == 'decorated_definition':
            for child in parent.children:
                if child.type == 'decorator':
                    # Get decorator name (skip @ symbol)
                    decorator_text = child.text.decode('utf-8')
                    if decorator_text.startswith('@'):
                        decorator_text = decorator_text[1:]
                    decorators.append(decorator_text.strip())
        
        return decorators
    
    def _extract_python_class(self, node: Any) -> Optional[ClassInfo]:
        """
        Extract class information from Python class_definition node.
        
        Args:
            node: tree-sitter class_definition node
        
        Returns:
            ClassInfo or None if extraction fails
        """
        try:
            # Get class name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get base classes
            base_classes = []
            superclasses_node = node.child_by_field_name('superclasses')
            if superclasses_node:
                base_classes = self._extract_python_base_classes(superclasses_node)
            
            # Get docstring
            docstring = self._extract_python_docstring(node)
            
            # Get line numbers
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Get decorators
            decorators = self._extract_python_decorators(node)
            
            # Extract methods
            methods = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.children:
                    if child.type == 'function_definition':
                        method_info = self._extract_python_function(child)
                        if method_info:
                            methods.append(method_info)
            
            return ClassInfo(
                name=name,
                methods=methods,
                base_classes=base_classes,
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                decorators=decorators
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract Python class: {e}")
            return None
    
    def _extract_python_base_classes(self, superclasses_node: Any) -> List[str]:
        """Extract base class names from Python superclasses node."""
        base_classes = []
        
        for child in superclasses_node.children:
            if child.type == 'identifier':
                base_classes.append(child.text.decode('utf-8'))
            elif child.type == 'attribute':
                # Handle qualified names like 'module.Class'
                base_classes.append(child.text.decode('utf-8'))
        
        return base_classes
    
    def _extract_python_imports(self, root_node: Any) -> List[ImportInfo]:
        """Extract import statements from Python AST."""
        imports = []
        
        for node in root_node.children:
            if node.type == 'import_statement':
                # import x, y, z
                for child in node.children:
                    if child.type == 'dotted_name':
                        module = child.text.decode('utf-8')
                        imports.append(ImportInfo(
                            module=module,
                            imported_symbols=[],
                            is_relative=False,
                            import_type='import',
                            line_number=node.start_point[0] + 1
                        ))
            
            elif node.type == 'import_from_statement':
                # from x import y, z
                module = None
                imported_symbols = []
                is_relative = False
                
                for child in node.children:
                    if child.type == 'dotted_name':
                        module = child.text.decode('utf-8')
                    elif child.type == 'relative_import':
                        module = child.text.decode('utf-8')
                        is_relative = True
                    elif child.type == 'identifier':
                        imported_symbols.append(child.text.decode('utf-8'))
                    elif child.type == 'aliased_import':
                        # Handle 'import x as y'
                        for subchild in child.children:
                            if subchild.type == 'identifier':
                                imported_symbols.append(subchild.text.decode('utf-8'))
                                break
                
                if module:
                    imports.append(ImportInfo(
                        module=module,
                        imported_symbols=imported_symbols,
                        is_relative=is_relative,
                        import_type='from_import',
                        line_number=node.start_point[0] + 1
                    ))
        
        return imports
    
    def _calculate_complexity(self, node: Any) -> int:
        """
        Calculate cyclomatic complexity for a function.
        
        Complexity starts at 1 and increases by 1 for each:
        - if, elif
        - for, while
        - and, or (in conditions)
        - except
        - case (in match statements)
        
        Args:
            node: Function node to analyze
        
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1
        
        # Decision point node types
        decision_nodes = {
            'if_statement', 'elif_clause',
            'for_statement', 'while_statement',
            'except_clause',
            'case_clause',  # Python 3.10+ match statements
            'boolean_operator'  # and, or
        }
        
        # Recursively count decision points
        def count_decisions(n: Any) -> int:
            count = 0
            
            if n.type in decision_nodes:
                count += 1
            
            for child in n.children:
                count += count_decisions(child)
            
            return count
        
        complexity += count_decisions(node)
        
        return complexity
    
    def _extract_javascript_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """
        Extract symbols from JavaScript/TypeScript AST.
        
        Args:
            parse_result: Parsed JavaScript/TypeScript file
        
        Returns:
            SymbolInfo with JavaScript/TypeScript symbols
        """
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract imports
        symbols.imports = self._extract_javascript_imports(root_node)
        
        # Extract exports
        symbols.exports = self._extract_javascript_exports(root_node)
        
        # Extract top-level functions and classes
        self._traverse_javascript_node(root_node, symbols, is_top_level=True)
        
        logger.debug(
            f"Extracted {len(symbols.functions)} functions, "
            f"{len(symbols.classes)} classes, "
            f"{len(symbols.imports)} imports, "
            f"{len(symbols.exports)} exports from JavaScript/TypeScript file"
        )
        
        return symbols
    
    def _traverse_javascript_node(self, node: Any, symbols: SymbolInfo, is_top_level: bool = False):
        """Traverse JavaScript AST and extract symbols."""
        # Extract functions
        if node.type in ['function_declaration', 'function']:
            func_info = self._extract_javascript_function(node)
            if func_info and is_top_level:
                symbols.functions.append(func_info)
        
        # Extract arrow functions (const x = () => {})
        elif node.type == 'lexical_declaration' and is_top_level:
            func_info = self._extract_javascript_arrow_function(node)
            if func_info:
                symbols.functions.append(func_info)
        
        # Extract classes
        elif node.type in ['class_declaration', 'class']:
            class_info = self._extract_javascript_class(node)
            if class_info and is_top_level:
                symbols.classes.append(class_info)
        
        # Traverse children for top-level declarations
        if is_top_level or node.type == 'program':
            for child in node.children:
                self._traverse_javascript_node(child, symbols, is_top_level=True)
    
    def _extract_javascript_function(self, node: Any) -> Optional[FunctionInfo]:
        """Extract function information from JavaScript function node."""
        try:
            # Get function name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get parameters
            parameters = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                parameters = self._extract_javascript_parameters(params_node)
            
            # Get JSDoc comment
            docstring = self._extract_jsdoc(node)
            
            # Get line numbers
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Check if async
            is_async = False
            for child in node.children:
                if child.type == 'async' or child.text == b'async':
                    is_async = True
                    break
            
            # Calculate complexity
            complexity = self._calculate_complexity(node)
            
            return FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=None,  # TypeScript return types handled separately
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                complexity=complexity,
                is_async=is_async,
                decorators=[]
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract JavaScript function: {e}")
            return None
    
    def _extract_javascript_arrow_function(self, node: Any) -> Optional[FunctionInfo]:
        """Extract arrow function from lexical declaration (const x = () => {})."""
        try:
            # Look for variable_declarator with arrow_function
            for child in node.children:
                if child.type == 'variable_declarator':
                    name_node = child.child_by_field_name('name')
                    value_node = child.child_by_field_name('value')
                    
                    if name_node and value_node and value_node.type == 'arrow_function':
                        name = name_node.text.decode('utf-8')
                        
                        # Get parameters
                        parameters = []
                        params_node = value_node.child_by_field_name('parameters')
                        if params_node:
                            parameters = self._extract_javascript_parameters(params_node)
                        elif value_node.child_by_field_name('parameter'):
                            # Single parameter without parentheses
                            param_node = value_node.child_by_field_name('parameter')
                            parameters = [param_node.text.decode('utf-8')]
                        
                        # Get JSDoc
                        docstring = self._extract_jsdoc(node)
                        
                        # Get line numbers
                        start_line = node.start_point[0] + 1
                        end_line = node.end_point[0] + 1
                        
                        # Check if async
                        is_async = False
                        for subchild in value_node.children:
                            if subchild.type == 'async' or subchild.text == b'async':
                                is_async = True
                                break
                        
                        # Calculate complexity
                        complexity = self._calculate_complexity(value_node)
                        
                        return FunctionInfo(
                            name=name,
                            parameters=parameters,
                            return_type=None,
                            docstring=docstring,
                            start_line=start_line,
                            end_line=end_line,
                            complexity=complexity,
                            is_async=is_async,
                            decorators=[]
                        )
            
            return None
        
        except Exception as e:
            logger.warning(f"Failed to extract JavaScript arrow function: {e}")
            return None
    
    def _extract_javascript_parameters(self, params_node: Any) -> List[str]:
        """Extract parameter names from JavaScript parameters node."""
        parameters = []
        
        for child in params_node.children:
            if child.type == 'identifier':
                parameters.append(child.text.decode('utf-8'))
            elif child.type == 'required_parameter':
                # TypeScript typed parameter
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        parameters.append(subchild.text.decode('utf-8'))
                        break
            elif child.type == 'optional_parameter':
                # TypeScript optional parameter
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        parameters.append(subchild.text.decode('utf-8'))
                        break
            elif child.type == 'rest_pattern':
                # Rest parameters (...args)
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        parameters.append(f"...{subchild.text.decode('utf-8')}")
                        break
        
        return parameters
    
    def _extract_jsdoc(self, node: Any) -> Optional[str]:
        """Extract JSDoc comment from JavaScript node."""
        # Look for comment before the node
        prev_sibling = node.prev_sibling
        
        # Check multiple previous siblings for comments
        for _ in range(3):
            if not prev_sibling:
                break
            
            if prev_sibling.type == 'comment':
                comment_text = prev_sibling.text.decode('utf-8')
                # Check if it's a JSDoc comment (starts with /**)
                if comment_text.startswith('/**') and comment_text.endswith('*/'):
                    # Clean up JSDoc
                    lines = comment_text[3:-2].strip().split('\n')
                    cleaned_lines = []
                    for line in lines:
                        line = line.strip()
                        if line.startswith('*'):
                            line = line[1:].strip()
                        if line and not line.startswith('@'):
                            cleaned_lines.append(line)
                    return ' '.join(cleaned_lines)
            
            prev_sibling = prev_sibling.prev_sibling
        
        return None
    
    def _extract_javascript_class(self, node: Any) -> Optional[ClassInfo]:
        """Extract class information from JavaScript class node."""
        try:
            # Get class name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get base class (extends)
            base_classes = []
            heritage_node = node.child_by_field_name('heritage')
            if heritage_node:
                for child in heritage_node.children:
                    if child.type == 'identifier':
                        base_classes.append(child.text.decode('utf-8'))
            
            # Get JSDoc
            docstring = self._extract_jsdoc(node)
            
            # Get line numbers
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Extract methods
            methods = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.children:
                    if child.type in ['method_definition', 'field_definition']:
                        method_info = self._extract_javascript_method(child)
                        if method_info:
                            methods.append(method_info)
            
            return ClassInfo(
                name=name,
                methods=methods,
                base_classes=base_classes,
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                decorators=[]
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract JavaScript class: {e}")
            return None
    
    def _extract_javascript_method(self, node: Any) -> Optional[FunctionInfo]:
        """Extract method information from JavaScript method_definition node."""
        try:
            # Get method name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get parameters
            parameters = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                parameters = self._extract_javascript_parameters(params_node)
            
            # Get JSDoc
            docstring = self._extract_jsdoc(node)
            
            # Get line numbers
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Check if async
            is_async = False
            for child in node.children:
                if child.type == 'async' or child.text == b'async':
                    is_async = True
                    break
            
            # Calculate complexity
            complexity = self._calculate_complexity(node)
            
            return FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=None,
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                complexity=complexity,
                is_async=is_async,
                decorators=[]
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract JavaScript method: {e}")
            return None
    
    def _extract_javascript_imports(self, root_node: Any) -> List[ImportInfo]:
        """Extract import statements from JavaScript/TypeScript AST."""
        imports = []
        
        for node in root_node.children:
            if node.type == 'import_statement':
                # import x from 'module' or import { x, y } from 'module'
                module = None
                imported_symbols = []
                
                # Get module source
                source_node = node.child_by_field_name('source')
                if source_node:
                    module = source_node.text.decode('utf-8').strip('"\'')
                
                # Get imported symbols
                for child in node.children:
                    if child.type == 'import_clause':
                        for subchild in child.children:
                            if subchild.type == 'identifier':
                                # Default import
                                imported_symbols.append(subchild.text.decode('utf-8'))
                            elif subchild.type == 'named_imports':
                                # Named imports { x, y }
                                for spec in subchild.children:
                                    if spec.type == 'import_specifier':
                                        for id_node in spec.children:
                                            if id_node.type == 'identifier':
                                                imported_symbols.append(id_node.text.decode('utf-8'))
                                                break
                
                if module:
                    is_relative = module.startswith('.') or module.startswith('/')
                    imports.append(ImportInfo(
                        module=module,
                        imported_symbols=imported_symbols,
                        is_relative=is_relative,
                        import_type='es6_import',
                        line_number=node.start_point[0] + 1
                    ))
            
            elif node.type == 'expression_statement':
                # require() statements
                for child in node.children:
                    if child.type == 'call_expression':
                        func_node = child.child_by_field_name('function')
                        if func_node and func_node.text == b'require':
                            args_node = child.child_by_field_name('arguments')
                            if args_node:
                                for arg in args_node.children:
                                    if arg.type == 'string':
                                        module = arg.text.decode('utf-8').strip('"\'')
                                        is_relative = module.startswith('.') or module.startswith('/')
                                        imports.append(ImportInfo(
                                            module=module,
                                            imported_symbols=[],
                                            is_relative=is_relative,
                                            import_type='require',
                                            line_number=node.start_point[0] + 1
                                        ))
        
        return imports
    
    def _extract_javascript_exports(self, root_node: Any) -> List[str]:
        """Extract export statements from JavaScript/TypeScript AST."""
        exports = []
        
        for node in root_node.children:
            if node.type == 'export_statement':
                # export { x, y } or export default x
                for child in node.children:
                    if child.type == 'identifier':
                        exports.append(child.text.decode('utf-8'))
                    elif child.type == 'export_clause':
                        for subchild in child.children:
                            if subchild.type == 'export_specifier':
                                for id_node in subchild.children:
                                    if id_node.type == 'identifier':
                                        exports.append(id_node.text.decode('utf-8'))
                                        break
                    elif child.type in ['function_declaration', 'class_declaration']:
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            exports.append(name_node.text.decode('utf-8'))
        
        return exports
    
    def _extract_java_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """Extract symbols from Java AST."""
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract imports
        symbols.imports = self._extract_java_imports(root_node)
        
        # Extract classes
        self._traverse_java_node(root_node, symbols)
        
        logger.debug(
            f"Extracted {len(symbols.functions)} methods, "
            f"{len(symbols.classes)} classes from Java file"
        )
        
        return symbols
    
    def _traverse_java_node(self, node: Any, symbols: SymbolInfo):
        """Traverse Java AST and extract symbols."""
        if node.type == 'class_declaration':
            class_info = self._extract_java_class(node)
            if class_info:
                symbols.classes.append(class_info)
        
        for child in node.children:
            self._traverse_java_node(child, symbols)
    
    def _extract_java_class(self, node: Any) -> Optional[ClassInfo]:
        """Extract class information from Java class node."""
        try:
            # Get class name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get base classes (extends/implements)
            base_classes = []
            superclass_node = node.child_by_field_name('superclass')
            if superclass_node:
                for child in superclass_node.children:
                    if child.type == 'type_identifier':
                        base_classes.append(child.text.decode('utf-8'))
            
            interfaces_node = node.child_by_field_name('interfaces')
            if interfaces_node:
                for child in interfaces_node.children:
                    if child.type == 'type_identifier':
                        base_classes.append(child.text.decode('utf-8'))
            
            # Get Javadoc
            docstring = self._extract_javadoc(node)
            
            # Get line numbers
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Extract methods
            methods = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.children:
                    if child.type == 'method_declaration':
                        method_info = self._extract_java_method(child)
                        if method_info:
                            methods.append(method_info)
            
            return ClassInfo(
                name=name,
                methods=methods,
                base_classes=base_classes,
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                decorators=[]
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract Java class: {e}")
            return None
    
    def _extract_java_method(self, node: Any) -> Optional[FunctionInfo]:
        """Extract method information from Java method node."""
        try:
            # Get method name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get parameters
            parameters = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for child in params_node.children:
                    if child.type == 'formal_parameter':
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            parameters.append(name_node.text.decode('utf-8'))
            
            # Get return type
            return_type = None
            type_node = node.child_by_field_name('type')
            if type_node:
                return_type = type_node.text.decode('utf-8')
            
            # Get Javadoc
            docstring = self._extract_javadoc(node)
            
            # Get line numbers
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Calculate complexity
            complexity = self._calculate_complexity(node)
            
            return FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=return_type,
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                complexity=complexity,
                is_async=False,
                decorators=[]
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract Java method: {e}")
            return None
    
    def _extract_javadoc(self, node: Any) -> Optional[str]:
        """Extract Javadoc comment from Java node."""
        prev_sibling = node.prev_sibling
        
        for _ in range(3):
            if not prev_sibling:
                break
            
            if prev_sibling.type == 'comment':
                comment_text = prev_sibling.text.decode('utf-8')
                if comment_text.startswith('/**') and comment_text.endswith('*/'):
                    lines = comment_text[3:-2].strip().split('\n')
                    cleaned_lines = []
                    for line in lines:
                        line = line.strip()
                        if line.startswith('*'):
                            line = line[1:].strip()
                        if line and not line.startswith('@'):
                            cleaned_lines.append(line)
                    return ' '.join(cleaned_lines)
            
            prev_sibling = prev_sibling.prev_sibling
        
        return None
    
    def _extract_java_imports(self, root_node: Any) -> List[ImportInfo]:
        """Extract import statements from Java AST."""
        imports = []
        
        for node in root_node.children:
            if node.type == 'import_declaration':
                # Get the imported class/package
                for child in node.children:
                    if child.type in ['scoped_identifier', 'identifier']:
                        module = child.text.decode('utf-8')
                        imports.append(ImportInfo(
                            module=module,
                            imported_symbols=[],
                            is_relative=False,
                            import_type='import',
                            line_number=node.start_point[0] + 1
                        ))
        
        return imports
    
    def _extract_go_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """Extract symbols from Go AST."""
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract imports
        symbols.imports = self._extract_go_imports(root_node)
        
        # Extract functions and types
        for node in root_node.children:
            if node.type == 'function_declaration':
                func_info = self._extract_go_function(node)
                if func_info:
                    symbols.functions.append(func_info)
            elif node.type == 'method_declaration':
                func_info = self._extract_go_method(node)
                if func_info:
                    symbols.functions.append(func_info)
            elif node.type == 'type_declaration':
                # Go doesn't have classes, but has type declarations
                # We'll treat struct types as classes
                class_info = self._extract_go_type(node)
                if class_info:
                    symbols.classes.append(class_info)
        
        logger.debug(
            f"Extracted {len(symbols.functions)} functions, "
            f"{len(symbols.classes)} types from Go file"
        )
        
        return symbols
    
    def _extract_go_function(self, node: Any) -> Optional[FunctionInfo]:
        """Extract function information from Go function node."""
        try:
            # Get function name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get parameters
            parameters = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for child in params_node.children:
                    if child.type == 'parameter_declaration':
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            parameters.append(name_node.text.decode('utf-8'))
            
            # Get return type
            return_type = None
            result_node = node.child_by_field_name('result')
            if result_node:
                return_type = result_node.text.decode('utf-8')
            
            # Get comment (Go uses // comments)
            docstring = self._extract_go_comment(node)
            
            # Get line numbers
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Calculate complexity
            complexity = self._calculate_complexity(node)
            
            return FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=return_type,
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                complexity=complexity,
                is_async=False,
                decorators=[]
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract Go function: {e}")
            return None
    
    def _extract_go_method(self, node: Any) -> Optional[FunctionInfo]:
        """Extract method information from Go method node."""
        # Similar to function but with receiver
        return self._extract_go_function(node)
    
    def _extract_go_type(self, node: Any) -> Optional[ClassInfo]:
        """Extract type information from Go type declaration."""
        try:
            # Get type name
            spec_node = node.child_by_field_name('type')
            if not spec_node:
                return None
            
            name_node = spec_node.child_by_field_name('name')
            if not name_node:
                return None
            name = name_node.text.decode('utf-8')
            
            # Get comment
            docstring = self._extract_go_comment(node)
            
            # Get line numbers
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            return ClassInfo(
                name=name,
                methods=[],  # Methods are separate in Go
                base_classes=[],
                docstring=docstring,
                start_line=start_line,
                end_line=end_line,
                decorators=[]
            )
        
        except Exception as e:
            logger.warning(f"Failed to extract Go type: {e}")
            return None
    
    def _extract_go_comment(self, node: Any) -> Optional[str]:
        """Extract comment from Go node."""
        prev_sibling = node.prev_sibling
        
        for _ in range(5):
            if not prev_sibling:
                break
            
            if prev_sibling.type == 'comment':
                comment_text = prev_sibling.text.decode('utf-8')
                # Remove // or /* */
                if comment_text.startswith('//'):
                    return comment_text[2:].strip()
                elif comment_text.startswith('/*') and comment_text.endswith('*/'):
                    return comment_text[2:-2].strip()
            
            prev_sibling = prev_sibling.prev_sibling
        
        return None
    
    def _extract_go_imports(self, root_node: Any) -> List[ImportInfo]:
        """Extract import statements from Go AST."""
        imports = []
        
        for node in root_node.children:
            if node.type == 'import_declaration':
                for child in node.children:
                    if child.type == 'import_spec':
                        path_node = child.child_by_field_name('path')
                        if path_node:
                            module = path_node.text.decode('utf-8').strip('"')
                            imports.append(ImportInfo(
                                module=module,
                                imported_symbols=[],
                                is_relative=False,
                                import_type='import',
                                line_number=node.start_point[0] + 1
                            ))
        
        return imports
    
    def _extract_rust_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """Extract symbols from Rust AST."""
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract functions and structs/impls
        for node in root_node.children:
            if node.type == 'function_item':
                func_info = self._extract_rust_function(node)
                if func_info:
                    symbols.functions.append(func_info)
            elif node.type in ['struct_item', 'impl_item']:
                class_info = self._extract_rust_struct(node)
                if class_info:
                    symbols.classes.append(class_info)
        
        logger.debug(f"Extracted {len(symbols.functions)} functions, {len(symbols.classes)} structs from Rust file")
        return symbols
    
    def _extract_rust_function(self, node: Any) -> Optional[FunctionInfo]:
        """Extract function from Rust AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            name = name_node.text.decode('utf-8')
            parameters = []
            
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for child in params_node.children:
                    if child.type == 'parameter':
                        pattern_node = child.child_by_field_name('pattern')
                        if pattern_node:
                            parameters.append(pattern_node.text.decode('utf-8'))
            
            return FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=None,
                docstring=self._extract_rust_comment(node),
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                complexity=self._calculate_complexity(node),
                is_async=False,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract Rust function: {e}")
            return None
    
    def _extract_rust_struct(self, node: Any) -> Optional[ClassInfo]:
        """Extract struct/impl from Rust AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            return ClassInfo(
                name=name_node.text.decode('utf-8'),
                methods=[],
                base_classes=[],
                docstring=self._extract_rust_comment(node),
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract Rust struct: {e}")
            return None
    
    def _extract_rust_comment(self, node: Any) -> Optional[str]:
        """Extract Rust doc comment."""
        prev_sibling = node.prev_sibling
        for _ in range(3):
            if not prev_sibling:
                break
            if prev_sibling.type == 'line_comment':
                text = prev_sibling.text.decode('utf-8')
                if text.startswith('///'):
                    return text[3:].strip()
            prev_sibling = prev_sibling.prev_sibling
        return None
    
    def _extract_cpp_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """Extract symbols from C/C++ AST."""
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract functions and classes
        for node in root_node.children:
            if node.type == 'function_definition':
                func_info = self._extract_cpp_function(node)
                if func_info:
                    symbols.functions.append(func_info)
            elif node.type == 'class_specifier':
                class_info = self._extract_cpp_class(node)
                if class_info:
                    symbols.classes.append(class_info)
        
        logger.debug(f"Extracted {len(symbols.functions)} functions, {len(symbols.classes)} classes from C/C++ file")
        return symbols
    
    def _extract_cpp_function(self, node: Any) -> Optional[FunctionInfo]:
        """Extract function from C/C++ AST."""
        try:
            declarator = node.child_by_field_name('declarator')
            if not declarator:
                return None
            
            # Find function name in declarator
            name = None
            for child in declarator.children:
                if child.type == 'identifier':
                    name = child.text.decode('utf-8')
                    break
                elif child.type == 'function_declarator':
                    for subchild in child.children:
                        if subchild.type == 'identifier':
                            name = subchild.text.decode('utf-8')
                            break
            
            if not name:
                return None
            
            return FunctionInfo(
                name=name,
                parameters=[],
                return_type=None,
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                complexity=self._calculate_complexity(node),
                is_async=False,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract C/C++ function: {e}")
            return None
    
    def _extract_cpp_class(self, node: Any) -> Optional[ClassInfo]:
        """Extract class from C/C++ AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            return ClassInfo(
                name=name_node.text.decode('utf-8'),
                methods=[],
                base_classes=[],
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract C/C++ class: {e}")
            return None
    
    def _extract_csharp_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """Extract symbols from C# AST."""
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract classes and methods
        self._traverse_csharp_node(root_node, symbols)
        
        logger.debug(f"Extracted {len(symbols.functions)} methods, {len(symbols.classes)} classes from C# file")
        return symbols
    
    def _traverse_csharp_node(self, node: Any, symbols: SymbolInfo):
        """Traverse C# AST."""
        if node.type == 'class_declaration':
            class_info = self._extract_csharp_class(node)
            if class_info:
                symbols.classes.append(class_info)
        
        for child in node.children:
            self._traverse_csharp_node(child, symbols)
    
    def _extract_csharp_class(self, node: Any) -> Optional[ClassInfo]:
        """Extract class from C# AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            methods = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.children:
                    if child.type == 'method_declaration':
                        method_info = self._extract_csharp_method(child)
                        if method_info:
                            methods.append(method_info)
            
            return ClassInfo(
                name=name_node.text.decode('utf-8'),
                methods=methods,
                base_classes=[],
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract C# class: {e}")
            return None
    
    def _extract_csharp_method(self, node: Any) -> Optional[FunctionInfo]:
        """Extract method from C# AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            return FunctionInfo(
                name=name_node.text.decode('utf-8'),
                parameters=[],
                return_type=None,
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                complexity=self._calculate_complexity(node),
                is_async=False,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract C# method: {e}")
            return None
    
    def _extract_ruby_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """Extract symbols from Ruby AST."""
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract methods and classes
        for node in root_node.children:
            if node.type == 'method':
                func_info = self._extract_ruby_method(node)
                if func_info:
                    symbols.functions.append(func_info)
            elif node.type == 'class':
                class_info = self._extract_ruby_class(node)
                if class_info:
                    symbols.classes.append(class_info)
        
        logger.debug(f"Extracted {len(symbols.functions)} methods, {len(symbols.classes)} classes from Ruby file")
        return symbols
    
    def _extract_ruby_method(self, node: Any) -> Optional[FunctionInfo]:
        """Extract method from Ruby AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            parameters = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for child in params_node.children:
                    if child.type == 'identifier':
                        parameters.append(child.text.decode('utf-8'))
            
            return FunctionInfo(
                name=name_node.text.decode('utf-8'),
                parameters=parameters,
                return_type=None,
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                complexity=self._calculate_complexity(node),
                is_async=False,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract Ruby method: {e}")
            return None
    
    def _extract_ruby_class(self, node: Any) -> Optional[ClassInfo]:
        """Extract class from Ruby AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            methods = []
            for child in node.children:
                if child.type == 'method':
                    method_info = self._extract_ruby_method(child)
                    if method_info:
                        methods.append(method_info)
            
            return ClassInfo(
                name=name_node.text.decode('utf-8'),
                methods=methods,
                base_classes=[],
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract Ruby class: {e}")
            return None
    
    def _extract_php_symbols(self, parse_result: ParseResult) -> SymbolInfo:
        """Extract symbols from PHP AST."""
        symbols = SymbolInfo()
        root_node = parse_result.root_node
        
        # Extract functions and classes
        self._traverse_php_node(root_node, symbols)
        
        logger.debug(f"Extracted {len(symbols.functions)} functions, {len(symbols.classes)} classes from PHP file")
        return symbols
    
    def _traverse_php_node(self, node: Any, symbols: SymbolInfo):
        """Traverse PHP AST."""
        if node.type == 'function_definition':
            func_info = self._extract_php_function(node)
            if func_info:
                symbols.functions.append(func_info)
        elif node.type == 'class_declaration':
            class_info = self._extract_php_class(node)
            if class_info:
                symbols.classes.append(class_info)
        
        for child in node.children:
            self._traverse_php_node(child, symbols)
    
    def _extract_php_function(self, node: Any) -> Optional[FunctionInfo]:
        """Extract function from PHP AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            parameters = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for child in params_node.children:
                    if child.type == 'simple_parameter':
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            parameters.append(name_node.text.decode('utf-8'))
            
            return FunctionInfo(
                name=name_node.text.decode('utf-8'),
                parameters=parameters,
                return_type=None,
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                complexity=self._calculate_complexity(node),
                is_async=False,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract PHP function: {e}")
            return None
    
    def _extract_php_class(self, node: Any) -> Optional[ClassInfo]:
        """Extract class from PHP AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            methods = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.children:
                    if child.type == 'method_declaration':
                        method_info = self._extract_php_method(child)
                        if method_info:
                            methods.append(method_info)
            
            return ClassInfo(
                name=name_node.text.decode('utf-8'),
                methods=methods,
                base_classes=[],
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract PHP class: {e}")
            return None
    
    def _extract_php_method(self, node: Any) -> Optional[FunctionInfo]:
        """Extract method from PHP AST."""
        try:
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None
            
            return FunctionInfo(
                name=name_node.text.decode('utf-8'),
                parameters=[],
                return_type=None,
                docstring=None,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                complexity=self._calculate_complexity(node),
                is_async=False,
                decorators=[]
            )
        except Exception as e:
            logger.warning(f"Failed to extract PHP method: {e}")
            return None
