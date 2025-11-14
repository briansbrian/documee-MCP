"""
Simple verification that get_enrichment_guide tool exists and is registered.

Run with: venv\\Scripts\\python.exe tests/test_enrichment_guide_simple.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import src.server


def test_tool_exists():
    """Verify the get_enrichment_guide tool is registered."""
    print("=" * 80)
    print("Verifying get_enrichment_guide MCP Tool Registration")
    print("=" * 80)
    
    # Check if tool is registered
    tools = src.server.mcp._tool_manager._tools
    
    if 'get_enrichment_guide' in tools:
        print("\n✓ get_enrichment_guide tool is registered")
        
        # Get tool info
        tool = tools['get_enrichment_guide']
        print(f"  Tool name: {tool.name}")
        print(f"  Function: {tool.fn.__name__}")
        
        # Check function signature
        import inspect
        sig = inspect.signature(tool.fn)
        params = list(sig.parameters.keys())
        print(f"  Parameters: {params}")
        
        # Verify required parameters
        required_params = ['codebase_id', 'lesson_id']
        for param in required_params:
            if param in params:
                print(f"  ✓ Required parameter '{param}' present")
            else:
                print(f"  ✗ Missing required parameter '{param}'")
                return False
        
        # Check docstring
        if tool.fn.__doc__:
            doc_lines = tool.fn.__doc__.strip().split('\n')
            print(f"\n  Docstring preview:")
            print(f"    {doc_lines[0]}")
            if len(doc_lines) > 1:
                print(f"    {doc_lines[1]}")
        
        print("\n" + "=" * 80)
        print("✓ Tool verification passed!")
        print("=" * 80)
        return True
    else:
        print("\n✗ get_enrichment_guide tool is NOT registered")
        print(f"\nAvailable tools: {list(tools.keys())}")
        return False


if __name__ == "__main__":
    success = test_tool_exists()
    sys.exit(0 if success else 1)
