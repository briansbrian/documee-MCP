"""Manual Test for Task 8: MCP Tools

This script verifies the three MCP tools are properly implemented:
1. export_course - exports a course from analyzed codebase
2. generate_lesson_outline - generates lesson outline from a file
3. create_exercise - creates an exercise for a pattern type
"""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def verify_tools():
    """Verify that all three MCP tools are registered in server.py."""
    print("\n" + "="*80)
    print("TASK 8: MCP TOOLS VERIFICATION")
    print("="*80)
    
    # Read server.py and find all @mcp.tool decorators
    server_file = Path("src/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return 1
    
    content = server_file.read_text(encoding='utf-8')
    
    # Find all tool definitions
    tool_pattern = r'@mcp\.tool\s+async def (\w+)\('
    tools = re.findall(tool_pattern, content)
    
    print(f"\nTotal tools registered: {len(tools)}")
    print("\nAll registered tools:")
    for tool in tools:
        print(f"  - {tool}")
    
    # Check for Task 8 tools
    print("\n" + "="*80)
    print("TASK 8 TOOLS CHECK")
    print("="*80)
    
    required_tools = {
        'export_course': 'Export a course from analyzed codebase to specified format',
        'generate_lesson_outline': 'Generate a lesson outline from a single file',
        'create_exercise': 'Create a coding exercise for a specific pattern type'
    }
    
    results = []
    
    for tool_name, description in required_tools.items():
        if tool_name in tools:
            print(f"\n✅ {tool_name}")
            print(f"   {description}")
            
            # Find the function signature
            func_pattern = rf'async def {tool_name}\((.*?)\):'
            match = re.search(func_pattern, content, re.DOTALL)
            if match:
                params = match.group(1)
                # Extract parameter names (simplified)
                param_names = [p.strip().split(':')[0].strip() for p in params.split(',') if p.strip() and not p.strip().startswith('ctx')]
                print(f"   Parameters: {', '.join(param_names)}")
            
            results.append(True)
        else:
            print(f"\n❌ {tool_name} - NOT FOUND")
            results.append(False)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTools implemented: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TASK 8 TOOLS ARE IMPLEMENTED")
        print("\nTo test the tools:")
        print("1. Start the MCP server: fastmcp dev src/server.py")
        print("2. Use an MCP client to call the tools")
        print("\nExample tool calls:")
        print('\n1. generate_lesson_outline:')
        print('   {"file_path": "src/course/structure_generator.py"}')
        print('\n2. create_exercise:')
        print('   {"pattern_type": "react_component", "difficulty": "intermediate"}')
        print('\n3. export_course (requires analyzed codebase):')
        print('   {"codebase_id": "your_codebase_id", "format": "json"}')
        
        # Check implementation details
        print("\n" + "="*80)
        print("IMPLEMENTATION DETAILS")
        print("="*80)
        
        # Check if tools have proper error handling
        error_handling_checks = [
            ('ValueError', 'Input validation'),
            ('RuntimeError', 'Server initialization check'),
            ('logger.info', 'Logging'),
            ('logger.error', 'Error logging')
        ]
        
        print("\nError handling and logging:")
        for check, desc in error_handling_checks:
            if check in content:
                print(f"  ✅ {desc} ({check})")
            else:
                print(f"  ⚠️  {desc} ({check}) - not found")
        
        return 0
    else:
        print(f"\n❌ {total - passed} TOOL(S) MISSING")
        return 1


if __name__ == "__main__":
    exit_code = verify_tools()
    sys.exit(exit_code)
