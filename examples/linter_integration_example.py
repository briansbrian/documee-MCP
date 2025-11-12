"""
Example: Using LinterIntegration

This example demonstrates how to use the LinterIntegration class
to run linters on code files.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.linter_integration import LinterIntegration
from src.analysis.config import AnalysisConfig


async def main():
    """Demonstrate linter integration usage."""
    
    print("=" * 70)
    print("LinterIntegration Example")
    print("=" * 70)
    
    # Create configuration with linters enabled
    config = AnalysisConfig(enable_linters=True)
    linter = LinterIntegration(config)
    
    # Example 1: Analyze a Python file
    print("\n1. Analyzing Python file...")
    print("-" * 70)
    
    python_file = "src/analysis/linter_integration.py"
    issues = await linter.run_linters(python_file, "python")
    
    print(f"File: {python_file}")
    print(f"Issues found: {len(issues)}")
    
    if issues:
        print("\nSample issues:")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"  Line {issue.line}: [{issue.severity}] {issue.message}")
            print(f"    Rule: {issue.rule}")
    else:
        print("No issues found (or linter not installed)")
    
    # Example 2: Analyze a JavaScript file
    print("\n2. Analyzing JavaScript file...")
    print("-" * 70)
    
    # Create a sample JS file with intentional issues
    js_file = Path("temp_example.js")
    js_file.write_text("""
function test() {
    var x = 1;  // var instead of const/let
    console.log(x)
}

function unused() {  // Unused function
    return 42;
}
""")
    
    try:
        issues = await linter.run_linters(str(js_file), "javascript")
        
        print(f"File: {js_file}")
        print(f"Issues found: {len(issues)}")
        
        if issues:
            print("\nSample issues:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"  Line {issue.line}: [{issue.severity}] {issue.message}")
                print(f"    Rule: {issue.rule}")
        else:
            print("No issues found (or linter not installed)")
    finally:
        # Clean up
        if js_file.exists():
            js_file.unlink()
    
    # Example 3: Demonstrate graceful failure
    print("\n3. Demonstrating graceful failure...")
    print("-" * 70)
    
    # Try to lint a non-existent file
    issues = await linter.run_linters("nonexistent.py", "python")
    print(f"Linting non-existent file: {len(issues)} issues")
    print("✓ Gracefully handled without crashing")
    
    # Example 4: Linters disabled
    print("\n4. With linters disabled...")
    print("-" * 70)
    
    config_disabled = AnalysisConfig(enable_linters=False)
    linter_disabled = LinterIntegration(config_disabled)
    
    issues = await linter_disabled.run_linters(python_file, "python")
    print(f"Issues found: {len(issues)}")
    print("✓ Returns empty list when disabled")
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)
    print("\nNote: To use linters, install them:")
    print("  Python: pip install pylint")
    print("  JavaScript/TypeScript: npm install -g eslint")


if __name__ == "__main__":
    asyncio.run(main())
