"""
Tests for Documentation Coverage Analyzer.
"""

import pytest
from src.analysis.documentation_coverage import (
    DocumentationCoverageAnalyzer,
    DocumentationCoverage
)
from src.analysis.symbol_extractor import (
    SymbolInfo,
    FunctionInfo,
    ClassInfo
)


class TestDocumentationCoverageAnalyzer:
    """Test suite for DocumentationCoverageAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = DocumentationCoverageAnalyzer()
    
    def test_empty_file(self):
        """Test coverage calculation for empty file."""
        symbols = SymbolInfo()
        coverage = self.analyzer.calculate_coverage(symbols)
        
        assert coverage.total_score == 0.0
        assert coverage.function_coverage == 0.0
        assert coverage.class_coverage == 0.0
        assert coverage.total_functions == 0
        assert coverage.total_classes == 0
    
    def test_fully_documented_functions(self):
        """Test coverage for fully documented functions."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(
                    name="func1",
                    docstring="This is a well-documented function that does something useful."
                ),
                FunctionInfo(
                    name="func2",
                    docstring="Another documented function with clear description."
                ),
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="python")
        
        assert coverage.total_functions == 2
        assert coverage.documented_functions == 2
        assert coverage.function_coverage == 1.0
        assert coverage.total_score == 1.0
    
    def test_partially_documented_functions(self):
        """Test coverage for partially documented functions."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(
                    name="func1",
                    docstring="This function is documented properly."
                ),
                FunctionInfo(
                    name="func2",
                    docstring=None  # No documentation
                ),
                FunctionInfo(
                    name="func3",
                    docstring="Another documented function."
                ),
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="python")
        
        assert coverage.total_functions == 3
        assert coverage.documented_functions == 2
        assert coverage.function_coverage == pytest.approx(0.667, rel=0.01)
        assert coverage.total_score == pytest.approx(0.667, rel=0.01)
    
    def test_undocumented_functions(self):
        """Test coverage for undocumented functions."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring=None),
                FunctionInfo(name="func2", docstring=""),
                FunctionInfo(name="func3", docstring="   "),  # Whitespace only
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="python")
        
        assert coverage.total_functions == 3
        assert coverage.documented_functions == 0
        assert coverage.function_coverage == 0.0
        assert coverage.total_score == 0.0
    
    def test_placeholder_docstrings_not_counted(self):
        """Test that placeholder docstrings are not counted as documentation."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="TODO"),
                FunctionInfo(name="func2", docstring="FIXME: implement this"),
                FunctionInfo(name="func3", docstring="..."),
                FunctionInfo(name="func4", docstring="TBD"),
                FunctionInfo(name="func5", docstring="This is proper documentation."),
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="python")
        
        assert coverage.total_functions == 5
        assert coverage.documented_functions == 1  # Only func5
        assert coverage.function_coverage == 0.2
    
    def test_minimum_length_requirement(self):
        """Test that very short docstrings are not counted."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="Short"),  # Too short
                FunctionInfo(name="func2", docstring="A bit longer description here."),  # Good
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="python")
        
        assert coverage.total_functions == 2
        assert coverage.documented_functions == 1  # Only func2
        assert coverage.function_coverage == 0.5
    
    def test_class_documentation_coverage(self):
        """Test coverage for class documentation."""
        symbols = SymbolInfo(
            classes=[
                ClassInfo(
                    name="Class1",
                    docstring="This is a documented class."
                ),
                ClassInfo(
                    name="Class2",
                    docstring=None  # No documentation
                ),
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="python")
        
        assert coverage.total_classes == 2
        assert coverage.documented_classes == 1
        assert coverage.class_coverage == 0.5
        assert coverage.total_score == 0.5
    
    def test_method_documentation_coverage(self):
        """Test coverage for method documentation within classes."""
        symbols = SymbolInfo(
            classes=[
                ClassInfo(
                    name="MyClass",
                    docstring="A documented class.",
                    methods=[
                        FunctionInfo(
                            name="method1",
                            docstring="Documented method."
                        ),
                        FunctionInfo(
                            name="method2",
                            docstring=None  # Undocumented
                        ),
                        FunctionInfo(
                            name="method3",
                            docstring="Another documented method."
                        ),
                    ]
                )
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="python")
        
        assert coverage.total_classes == 1
        assert coverage.documented_classes == 1
        assert coverage.total_methods == 3
        assert coverage.documented_methods == 2
        assert coverage.method_coverage == pytest.approx(0.667, rel=0.01)
    
    def test_mixed_functions_classes_methods(self):
        """Test coverage with mix of functions, classes, and methods."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="Documented function."),
                FunctionInfo(name="func2", docstring=None),
            ],
            classes=[
                ClassInfo(
                    name="Class1",
                    docstring="Documented class.",
                    methods=[
                        FunctionInfo(name="method1", docstring="Documented method."),
                        FunctionInfo(name="method2", docstring=None),
                    ]
                )
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="python")
        
        # Functions: 1/2 = 0.5 (40% weight)
        # Classes: 1/1 = 1.0 (30% weight)
        # Methods: 1/2 = 0.5 (30% weight)
        # Total: (0.5 * 0.4 + 1.0 * 0.3 + 0.5 * 0.3) = 0.65
        assert coverage.total_functions == 2
        assert coverage.documented_functions == 1
        assert coverage.total_classes == 1
        assert coverage.documented_classes == 1
        assert coverage.total_methods == 2
        assert coverage.documented_methods == 1
        assert coverage.total_score == pytest.approx(0.65, rel=0.01)
    
    def test_inline_comments_detection_python(self):
        """Test detection of inline comments in Python code."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="Documented function.")
            ]
        )
        
        file_content = """
def func1():
    '''Documented function.'''
    x = 10  # Initialize counter
    # This loop processes each item in the list
    for i in range(x):
        # Calculate the square of the number
        result = i * i
        print(result)  # Output the result
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="python"
        )
        
        assert coverage.has_inline_comments is True
        assert coverage.inline_comment_bonus == 0.1
        # Base score 1.0 + 0.1 bonus, capped at 1.0
        assert coverage.total_score == 1.0
    
    def test_inline_comments_detection_javascript(self):
        """Test detection of inline comments in JavaScript code."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="myFunc", docstring="/** Documented function */")
            ]
        )
        
        file_content = """
function myFunc() {
    let x = 10;  // Initialize counter
    // This loop processes each item
    for (let i = 0; i < x; i++) {
        // Calculate the square
        const result = i * i;
        console.log(result);  // Output result
    }
}
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="javascript"
        )
        
        assert coverage.has_inline_comments is True
        assert coverage.inline_comment_bonus == 0.1
    
    def test_no_inline_comments(self):
        """Test when there are no inline comments."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="Documented function.")
            ]
        )
        
        file_content = """
def func1():
    '''Documented function.'''
    x = 10
    for i in range(x):
        result = i * i
        print(result)
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="python"
        )
        
        assert coverage.has_inline_comments is False
        assert coverage.inline_comment_bonus == 0.0
        assert coverage.total_score == 1.0  # Just the base score
    
    def test_section_headers_not_counted_as_inline(self):
        """Test that section headers are not counted as inline comments."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="Documented function.")
            ]
        )
        
        file_content = """
# ============================================
# Section: Main Functions
# ============================================

def func1():
    '''Documented function.'''
    # TODO: implement this
    # FIXME: bug here
    pass
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="python"
        )
        
        # Section headers and TODO/FIXME should not count
        assert coverage.has_inline_comments is False
    
    def test_weighted_scoring_functions_only(self):
        """Test scoring when only functions are present."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="Documented."),
                FunctionInfo(name="func2", docstring=None),
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols)
        
        # Only functions present, so function coverage = total score
        assert coverage.function_coverage == 0.5
        assert coverage.total_score == 0.5
    
    def test_weighted_scoring_classes_only(self):
        """Test scoring when only classes are present."""
        symbols = SymbolInfo(
            classes=[
                ClassInfo(name="Class1", docstring="Documented."),
                ClassInfo(name="Class2", docstring=None),
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols)
        
        # Only classes present, so class coverage = total score
        assert coverage.class_coverage == 0.5
        assert coverage.total_score == 0.5
    
    def test_javascript_jsdoc_detection(self):
        """Test JSDoc detection for JavaScript/TypeScript."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(
                    name="myFunc",
                    docstring="This function does something useful and important."
                ),
            ]
        )
        
        coverage = self.analyzer.calculate_coverage(symbols, language="javascript")
        
        assert coverage.documented_functions == 1
        assert coverage.function_coverage == 1.0
    
    def test_score_capped_at_one(self):
        """Test that total score is capped at 1.0 even with bonus."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="Fully documented function.")
            ]
        )
        
        file_content = """
def func1():
    '''Fully documented function.'''
    # This is an explanatory comment about the algorithm
    x = 10
    # Another comment explaining the logic here
    for i in range(x):
        # Yet another explanatory comment
        result = i * i
        # And one more for good measure
        print(result)
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="python"
        )
        
        # Base score 1.0 + 0.1 bonus should be capped at 1.0
        assert coverage.total_score == 1.0
    
    def test_well_documented_code_with_all_elements(self):
        """Test coverage for well-documented code with functions, classes, and methods."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(
                    name="helper_function",
                    docstring="A well-documented helper function that performs calculations."
                ),
                FunctionInfo(
                    name="process_data",
                    docstring="Process data with comprehensive documentation explaining the algorithm."
                ),
            ],
            classes=[
                ClassInfo(
                    name="DataProcessor",
                    docstring="A comprehensive class for processing data with detailed documentation.",
                    methods=[
                        FunctionInfo(
                            name="__init__",
                            docstring="Initialize the DataProcessor with configuration parameters."
                        ),
                        FunctionInfo(
                            name="process",
                            docstring="Process the input data and return transformed results."
                        ),
                        FunctionInfo(
                            name="validate",
                            docstring="Validate the input data before processing."
                        ),
                    ]
                ),
                ClassInfo(
                    name="DataValidator",
                    docstring="Validates data according to specified rules and constraints.",
                    methods=[
                        FunctionInfo(
                            name="check_format",
                            docstring="Check if data format matches expected schema."
                        ),
                    ]
                ),
            ]
        )
        
        file_content = """
def helper_function(x):
    '''A well-documented helper function that performs calculations.'''
    # Initialize the result accumulator
    result = 0
    # Iterate through each element and apply transformation
    for i in range(x):
        # Calculate the square and add to result
        result += i * i
    return result

class DataProcessor:
    '''A comprehensive class for processing data with detailed documentation.'''
    
    def __init__(self, config):
        '''Initialize the DataProcessor with configuration parameters.'''
        # Store configuration for later use
        self.config = config
    
    def process(self, data):
        '''Process the input data and return transformed results.'''
        # Validate input before processing
        if not self.validate(data):
            raise ValueError("Invalid data")
        # Apply transformation logic
        return [x * 2 for x in data]
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="python"
        )
        
        # All functions documented: 2/2 = 1.0
        assert coverage.function_coverage == 1.0
        # All classes documented: 2/2 = 1.0
        assert coverage.class_coverage == 1.0
        # All methods documented: 4/4 = 1.0
        assert coverage.method_coverage == 1.0
        # Has inline comments
        assert coverage.has_inline_comments is True
        # Total score should be 1.0 (capped)
        assert coverage.total_score == 1.0
    
    def test_completely_undocumented_code(self):
        """Test coverage for completely undocumented code."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring=None),
                FunctionInfo(name="func2", docstring=""),
                FunctionInfo(name="func3", docstring="   "),
            ],
            classes=[
                ClassInfo(
                    name="MyClass",
                    docstring=None,
                    methods=[
                        FunctionInfo(name="method1", docstring=None),
                        FunctionInfo(name="method2", docstring=""),
                    ]
                ),
            ]
        )
        
        file_content = """
def func1(x):
    return x * 2

def func2(y):
    return y + 1

class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        return 42
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="python"
        )
        
        # No functions documented
        assert coverage.function_coverage == 0.0
        assert coverage.documented_functions == 0
        # No classes documented
        assert coverage.class_coverage == 0.0
        assert coverage.documented_classes == 0
        # No methods documented
        assert coverage.method_coverage == 0.0
        assert coverage.documented_methods == 0
        # No inline comments
        assert coverage.has_inline_comments is False
        # Total score should be 0.0
        assert coverage.total_score == 0.0
    
    def test_inline_comments_minimum_threshold(self):
        """Test that inline comments require minimum count to be detected."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(name="func1", docstring="Documented function.")
            ]
        )
        
        # Only 2 inline comments (below threshold of 3)
        file_content = """
def func1():
    '''Documented function.'''
    x = 10  # Initialize counter
    # This is one explanatory comment
    for i in range(x):
        result = i * i
        print(result)
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="python"
        )
        
        # Should not detect inline comments (below threshold)
        assert coverage.has_inline_comments is False
        assert coverage.inline_comment_bonus == 0.0
    
    def test_typescript_documentation_coverage(self):
        """Test documentation coverage for TypeScript code."""
        symbols = SymbolInfo(
            functions=[
                FunctionInfo(
                    name="processUser",
                    docstring="Process user data and return formatted result."
                ),
                FunctionInfo(
                    name="validateEmail",
                    docstring=None
                ),
            ],
            classes=[
                ClassInfo(
                    name="UserService",
                    docstring="Service for managing user operations.",
                    methods=[
                        FunctionInfo(
                            name="getUser",
                            docstring="Retrieve user by ID from database."
                        ),
                        FunctionInfo(
                            name="deleteUser",
                            docstring=None
                        ),
                    ]
                ),
            ]
        )
        
        file_content = """
/**
 * Process user data and return formatted result.
 */
function processUser(user: User): FormattedUser {
    // Validate user data before processing
    if (!validateEmail(user.email)) {
        throw new Error('Invalid email');
    }
    // Transform user object to formatted output
    return {
        id: user.id,
        name: user.name.toUpperCase()
    };
}

class UserService {
    /**
     * Service for managing user operations.
     */
    
    /**
     * Retrieve user by ID from database.
     */
    getUser(id: string): User {
        // Query database for user record
        return db.query('SELECT * FROM users WHERE id = ?', [id]);
    }
    
    deleteUser(id: string): void {
        db.query('DELETE FROM users WHERE id = ?', [id]);
    }
}
"""
        
        coverage = self.analyzer.calculate_coverage(
            symbols, file_content, language="typescript"
        )
        
        # Functions: 1/2 = 0.5
        assert coverage.function_coverage == 0.5
        # Classes: 1/1 = 1.0
        assert coverage.class_coverage == 1.0
        # Methods: 1/2 = 0.5
        assert coverage.method_coverage == 0.5
        # Has inline comments
        assert coverage.has_inline_comments is True
        # Score calculation: (0.5 * 0.4 + 1.0 * 0.3 + 0.5 * 0.3) + 0.1 = 0.65 + 0.1 = 0.75
        assert coverage.total_score == pytest.approx(0.75, rel=0.01)
