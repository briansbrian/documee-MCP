"""
Example: Using the AST Parser Manager

This example demonstrates how to use the ASTParserManager to parse
code files and extract AST information.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis import ASTParserManager, AnalysisConfig


def main():
    """Demonstrate AST parser usage."""
    print("=" * 60)
    print("AST Parser Manager Example")
    print("=" * 60)
    
    # Initialize the parser
    config = AnalysisConfig()
    parser = ASTParserManager(config)
    
    print(f"\n✓ Initialized parser with {len(parser.get_supported_languages())} languages")
    print(f"  Supported: {', '.join(parser.get_supported_languages())}")
    
    # Example 1: Parse a Python file
    print("\n" + "-" * 60)
    print("Example 1: Parsing a Python file")
    print("-" * 60)
    
    # Use this example file itself
    example_file = __file__
    
    try:
        result = parser.parse_file(example_file)
        
        print(f"✓ Successfully parsed: {Path(example_file).name}")
        print(f"  Language: {result.language}")
        print(f"  Root node type: {result.root_node.type}")
        print(f"  Parse time: {result.parse_time_ms:.2f}ms")
        print(f"  Has errors: {result.has_errors}")
        print(f"  Number of children: {len(result.root_node.children)}")
        
        # Show first few child nodes
        print(f"\n  First 5 child nodes:")
        for i, child in enumerate(result.root_node.children[:5]):
            print(f"    {i+1}. {child.type} (line {child.start_point[0] + 1})")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 2: Check if files are supported
    print("\n" + "-" * 60)
    print("Example 2: Checking file support")
    print("-" * 60)
    
    test_files = [
        "example.py",
        "example.js",
        "example.ts",
        "example.java",
        "example.txt",
        "example.md"
    ]
    
    for file in test_files:
        supported = parser.is_supported_file(file)
        status = "✓" if supported else "✗"
        support_text = "Supported" if supported else "Not supported"
        print(f"  {status} {file}: {support_text}")
    
    # Example 3: Language detection
    print("\n" + "-" * 60)
    print("Example 3: Language detection")
    print("-" * 60)
    
    extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs']
    for ext in extensions:
        lang = parser._detect_language(f"test{ext}")
        print(f"  {ext} -> {lang}")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
