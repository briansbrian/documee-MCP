"""
Example demonstrating the Documentation Coverage Analyzer.

This script shows how to use the DocumentationCoverageAnalyzer to measure
documentation quality in code files.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.documentation_coverage import DocumentationCoverageAnalyzer
from src.analysis.symbol_extractor import SymbolInfo, FunctionInfo, ClassInfo


def example_well_documented():
    """Example with well-documented code."""
    print("\n" + "="*60)
    print("Example 1: Well-Documented Code")
    print("="*60)
    
    symbols = SymbolInfo(
        functions=[
            FunctionInfo(
                name="calculate_sum",
                docstring="Calculate the sum of two numbers and return the result.",
                parameters=["a", "b"],
                start_line=1,
                end_line=5
            ),
            FunctionInfo(
                name="format_output",
                docstring="Format the output string with proper indentation and styling.",
                parameters=["text", "indent"],
                start_line=7,
                end_line=12
            ),
        ],
        classes=[
            ClassInfo(
                name="DataProcessor",
                docstring="Process and transform data from various sources.",
                methods=[
                    FunctionInfo(
                        name="process",
                        docstring="Process the input data and return transformed result.",
                        parameters=["data"]
                    ),
                    FunctionInfo(
                        name="validate",
                        docstring="Validate the data meets all required constraints.",
                        parameters=["data"]
                    ),
                ]
            )
        ]
    )
    
    file_content = """
def calculate_sum(a, b):
    '''Calculate the sum of two numbers and return the result.'''
    # Initialize result variable
    result = a + b
    # Return the calculated sum
    return result

def format_output(text, indent):
    '''Format the output string with proper indentation and styling.'''
    # Apply indentation to each line
    lines = text.split('\\n')
    # Join with proper spacing
    return '\\n'.join(' ' * indent + line for line in lines)

class DataProcessor:
    '''Process and transform data from various sources.'''
    
    def process(self, data):
        '''Process the input data and return transformed result.'''
        # Transform the data
        return data.upper()
    
    def validate(self, data):
        '''Validate the data meets all required constraints.'''
        # Check data is not empty
        return len(data) > 0
"""
    
    analyzer = DocumentationCoverageAnalyzer()
    coverage = analyzer.calculate_coverage(symbols, file_content, language="python")
    
    print(f"\nTotal Score: {coverage.total_score:.2%}")
    print(f"Function Coverage: {coverage.function_coverage:.2%} ({coverage.documented_functions}/{coverage.total_functions})")
    print(f"Class Coverage: {coverage.class_coverage:.2%} ({coverage.documented_classes}/{coverage.total_classes})")
    print(f"Method Coverage: {coverage.method_coverage:.2%} ({coverage.documented_methods}/{coverage.total_methods})")
    print(f"Inline Comments: {'Yes' if coverage.has_inline_comments else 'No'}")
    print(f"Inline Comment Bonus: +{coverage.inline_comment_bonus:.1%}")


def example_poorly_documented():
    """Example with poorly documented code."""
    print("\n" + "="*60)
    print("Example 2: Poorly Documented Code")
    print("="*60)
    
    symbols = SymbolInfo(
        functions=[
            FunctionInfo(
                name="func1",
                docstring=None,  # No documentation
                parameters=["x", "y"]
            ),
            FunctionInfo(
                name="func2",
                docstring="TODO",  # Placeholder
                parameters=["data"]
            ),
            FunctionInfo(
                name="func3",
                docstring="",  # Empty
                parameters=[]
            ),
        ],
        classes=[
            ClassInfo(
                name="MyClass",
                docstring=None,  # No documentation
                methods=[
                    FunctionInfo(name="method1", docstring=None),
                    FunctionInfo(name="method2", docstring="FIXME"),
                ]
            )
        ]
    )
    
    analyzer = DocumentationCoverageAnalyzer()
    coverage = analyzer.calculate_coverage(symbols, language="python")
    
    print(f"\nTotal Score: {coverage.total_score:.2%}")
    print(f"Function Coverage: {coverage.function_coverage:.2%} ({coverage.documented_functions}/{coverage.total_functions})")
    print(f"Class Coverage: {coverage.class_coverage:.2%} ({coverage.documented_classes}/{coverage.total_classes})")
    print(f"Method Coverage: {coverage.method_coverage:.2%} ({coverage.documented_methods}/{coverage.total_methods})")


def example_mixed_documentation():
    """Example with mixed documentation quality."""
    print("\n" + "="*60)
    print("Example 3: Mixed Documentation Quality")
    print("="*60)
    
    symbols = SymbolInfo(
        functions=[
            FunctionInfo(
                name="well_documented",
                docstring="This function is properly documented with clear description.",
                parameters=["param1", "param2"]
            ),
            FunctionInfo(
                name="no_docs",
                docstring=None,
                parameters=["x"]
            ),
            FunctionInfo(
                name="short_docs",
                docstring="Short",  # Too short
                parameters=[]
            ),
        ],
        classes=[
            ClassInfo(
                name="DocumentedClass",
                docstring="A well-documented class with clear purpose.",
                methods=[
                    FunctionInfo(
                        name="documented_method",
                        docstring="This method does something useful."
                    ),
                    FunctionInfo(
                        name="undocumented_method",
                        docstring=None
                    ),
                ]
            )
        ]
    )
    
    analyzer = DocumentationCoverageAnalyzer()
    coverage = analyzer.calculate_coverage(symbols, language="python")
    
    print(f"\nTotal Score: {coverage.total_score:.2%}")
    print(f"Function Coverage: {coverage.function_coverage:.2%} ({coverage.documented_functions}/{coverage.total_functions})")
    print(f"Class Coverage: {coverage.class_coverage:.2%} ({coverage.documented_classes}/{coverage.total_classes})")
    print(f"Method Coverage: {coverage.method_coverage:.2%} ({coverage.documented_methods}/{coverage.total_methods})")
    
    # Breakdown
    print("\nDetailed Breakdown:")
    print(f"  - Functions: 1 documented, 2 undocumented (1 too short)")
    print(f"  - Classes: 1 documented, 0 undocumented")
    print(f"  - Methods: 1 documented, 1 undocumented")
    print(f"  - Weighted Score: (0.33 * 0.4) + (1.0 * 0.3) + (0.5 * 0.3) = {coverage.total_score:.2f}")


def example_javascript():
    """Example with JavaScript/TypeScript code."""
    print("\n" + "="*60)
    print("Example 4: JavaScript/TypeScript Documentation")
    print("="*60)
    
    symbols = SymbolInfo(
        functions=[
            FunctionInfo(
                name="fetchData",
                docstring="Fetch data from the API endpoint and return parsed JSON.",
                parameters=["url", "options"],
                is_async=True
            ),
            FunctionInfo(
                name="processResponse",
                docstring="Process the API response and extract relevant data.",
                parameters=["response"]
            ),
        ],
        classes=[
            ClassInfo(
                name="ApiClient",
                docstring="Client for interacting with the REST API.",
                methods=[
                    FunctionInfo(
                        name="get",
                        docstring="Send GET request to the specified endpoint.",
                        parameters=["endpoint"]
                    ),
                    FunctionInfo(
                        name="post",
                        docstring="Send POST request with data to the endpoint.",
                        parameters=["endpoint", "data"]
                    ),
                ]
            )
        ]
    )
    
    file_content = """
/**
 * Fetch data from the API endpoint and return parsed JSON.
 */
async function fetchData(url, options) {
    const response = await fetch(url, options);  // Make API call
    // Parse the JSON response
    return await response.json();
}

/**
 * Process the API response and extract relevant data.
 */
function processResponse(response) {
    // Extract data field
    const data = response.data;
    // Transform to required format
    return data.map(item => item.value);
}

/**
 * Client for interacting with the REST API.
 */
class ApiClient {
    /**
     * Send GET request to the specified endpoint.
     */
    get(endpoint) {
        // Construct full URL
        const url = this.baseUrl + endpoint;
        return fetchData(url, { method: 'GET' });
    }
    
    /**
     * Send POST request with data to the endpoint.
     */
    post(endpoint, data) {
        // Construct request options
        const options = {
            method: 'POST',
            body: JSON.stringify(data)
        };
        return fetchData(this.baseUrl + endpoint, options);
    }
}
"""
    
    analyzer = DocumentationCoverageAnalyzer()
    coverage = analyzer.calculate_coverage(symbols, file_content, language="javascript")
    
    print(f"\nTotal Score: {coverage.total_score:.2%}")
    print(f"Function Coverage: {coverage.function_coverage:.2%} ({coverage.documented_functions}/{coverage.total_functions})")
    print(f"Class Coverage: {coverage.class_coverage:.2%} ({coverage.documented_classes}/{coverage.total_classes})")
    print(f"Method Coverage: {coverage.method_coverage:.2%} ({coverage.documented_methods}/{coverage.total_methods})")
    print(f"Inline Comments: {'Yes' if coverage.has_inline_comments else 'No'}")
    print(f"Inline Comment Bonus: +{coverage.inline_comment_bonus:.1%}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Documentation Coverage Analyzer Examples")
    print("="*60)
    
    example_well_documented()
    example_poorly_documented()
    example_mixed_documentation()
    example_javascript()
    
    print("\n" + "="*60)
    print("Examples Complete!")
    print("="*60 + "\n")
