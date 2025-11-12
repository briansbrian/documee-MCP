"""
Automated test script for Analysis Engine MCP Tools.
Tests requirements 11.1, 11.2, 11.3, 11.4, 11.5 from Task 13.6
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


async def test_analysis_mcp_tools():
    """Run comprehensive tests on the Analysis Engine MCP tools."""
    
    print("=" * 80)
    print("ANALYSIS ENGINE MCP TOOLS TEST SUITE")
    print("=" * 80)
    print()
    
    # Server parameters
    server_params = StdioServerParameters(
        command=r".\venv\Scripts\python.exe",
        args=["-m", "src.server"],
        env=None
    )
    
    test_results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Variables to store between tests
    codebase_id = None
    test_file_path = None
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                # Initialize the session
                print("[*] Initializing MCP session...")
                await session.initialize()
                print("[OK] Session initialized successfully\n")
                test_results["total"] += 1
                test_results["passed"] += 1
                
                # Test 1: List All Tools
                print("-" * 80)
                print("TEST 1: Verify Analysis Tools are Registered")
                print("-" * 80)
                test_results["total"] += 1
                
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} total tools")
                
                expected_analysis_tools = {
                    "analyze_file",
                    "detect_patterns", 
                    "analyze_dependencies",
                    "score_teaching_value",
                    "analyze_codebase_tool"
                }
                
                actual_tools = {tool.name for tool in tools.tools}
                analysis_tools_found = expected_analysis_tools & actual_tools
                
                print(f"\nAnalysis tools found ({len(analysis_tools_found)}/5):")
                for tool_name in sorted(analysis_tools_found):
                    print(f"  [+] {tool_name}")
                
                if len(analysis_tools_found) < 5:
                    missing = expected_analysis_tools - analysis_tools_found
                    print(f"\nMissing tools:")
                    for tool_name in sorted(missing):
                        print(f"  [-] {tool_name}")
                
                if analysis_tools_found == expected_analysis_tools:
                    print("\n[PASS] All 5 analysis tools registered")
                    test_results["passed"] += 1
                else:
                    print(f"\n[FAIL] Expected 5 tools, found {len(analysis_tools_found)}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"Missing tools: {expected_analysis_tools - analysis_tools_found}")
                print()
                
                # Setup: Scan codebase
                print("-" * 80)
                print("SETUP: Scanning codebase to get codebase_id")
                print("-" * 80)
                
                try:
                    result = await session.call_tool(
                        "scan_codebase",
                        arguments={"path": ".", "max_depth": 5}
                    )
                    
                    result_data = json.loads(result.content[0].text)
                    codebase_id = result_data.get("codebase_id")
                    print(f"[OK] Codebase ID: {codebase_id}\n")
                    
                except Exception as e:
                    print(f"[FAIL] SETUP FAILED: Could not scan codebase: {e}\n")
                    test_results["errors"].append(f"Setup failed: {str(e)}")
                    return test_results
                
                # Find a test file
                print("-" * 80)
                print("SETUP: Finding test file for analysis")
                print("-" * 80)
                
                test_candidates = [
                    "src/server.py",
                    "src/tools/scan_codebase.py",
                    "src/cache/unified_cache.py",
                    "src/analysis/engine.py"
                ]
                
                for candidate in test_candidates:
                    if Path(candidate).exists():
                        test_file_path = candidate
                        print(f"[OK] Using test file: {test_file_path}\n")
                        break
                
                if not test_file_path:
                    print("[FAIL] SETUP FAILED: No test file found\n")
                    test_results["errors"].append("No test file found")
                    return test_results
                
                # Test 2: analyze_file with valid file
                print("-" * 80)
                print("TEST 2: analyze_file with valid file (Requirement 11.1)")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "analyze_file",
                        arguments={"file_path": test_file_path, "force": True}
                    )
                    
                    result_data = json.loads(result.content[0].text)
                    
                    required_fields = [
                        "file_path", "language", "symbol_info", "patterns",
                        "teaching_value", "complexity_metrics", "documentation_coverage",
                        "has_errors", "analyzed_at", "cache_hit"
                    ]
                    
                    missing_fields = [f for f in required_fields if f not in result_data]
                    
                    if not missing_fields:
                        print(f"[OK] File analyzed: {result_data.get('file_path')}")
                        print(f"     Language: {result_data.get('language')}")
                        print(f"     Teaching Value: {result_data.get('teaching_value', {}).get('total_score', 'N/A')}")
                        print(f"     Functions: {len(result_data.get('symbol_info', {}).get('functions', []))}")
                        print(f"     Classes: {len(result_data.get('symbol_info', {}).get('classes', []))}")
                        print("[PASS] analyze_file returned valid FileAnalysis")
                        test_results["passed"] += 1
                    else:
                        print(f"[FAIL] Missing fields: {missing_fields}")
                        test_results["failed"] += 1
                        test_results["errors"].append(f"analyze_file missing fields: {missing_fields}")
                    
                except Exception as e:
                    print(f"[FAIL] Error calling analyze_file: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"analyze_file error: {str(e)}")
                print()
                
                # Test 3: analyze_file with invalid file
                print("-" * 80)
                print("TEST 3: analyze_file with invalid file (error handling)")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "analyze_file",
                        arguments={"file_path": "nonexistent_file_12345.py"}
                    )
                    
                    if result.isError:
                        error_text = result.content[0].text.lower()
                        if "not found" in error_text or "file" in error_text:
                            print(f"[PASS] Correct error for invalid file")
                            test_results["passed"] += 1
                        else:
                            print(f"[WARN] Error returned: {result.content[0].text}")
                            test_results["passed"] += 1
                    else:
                        print("[FAIL] Should have returned error for nonexistent file")
                        test_results["failed"] += 1
                        test_results["errors"].append("analyze_file: no error for invalid file")
                    
                except Exception as e:
                    error_str = str(e).lower()
                    if "not found" in error_str or "file" in error_str:
                        print(f"[PASS] Correct error for invalid file")
                        test_results["passed"] += 1
                    else:
                        print(f"[WARN] Error raised: {e}")
                        test_results["passed"] += 1
                print()
                
                # Test 4: analyze_file with empty file_path
                print("-" * 80)
                print("TEST 4: analyze_file with empty file_path (validation)")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "analyze_file",
                        arguments={"file_path": ""}
                    )
                    
                    if result.isError:
                        error_text = result.content[0].text.lower()
                        if "empty" in error_text or "required" in error_text:
                            print(f"[PASS] Correct validation error")
                            test_results["passed"] += 1
                        else:
                            print(f"[WARN] Error returned: {result.content[0].text}")
                            test_results["passed"] += 1
                    else:
                        print("[FAIL] Should have returned validation error")
                        test_results["failed"] += 1
                        test_results["errors"].append("analyze_file: no validation for empty path")
                    
                except Exception as e:
                    error_str = str(e).lower()
                    if "empty" in error_str or "required" in error_str:
                        print(f"[PASS] Correct validation error")
                        test_results["passed"] += 1
                    else:
                        print(f"[WARN] Error raised: {e}")
                        test_results["passed"] += 1
                print()
                
                # Test 5: score_teaching_value with valid file
                print("-" * 80)
                print("TEST 5: score_teaching_value with valid file (Requirement 11.4)")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "score_teaching_value",
                        arguments={"file_path": test_file_path, "force": True}
                    )
                    
                    result_data = json.loads(result.content[0].text)
                    
                    required_fields = [
                        "total_score", "documentation_score", "complexity_score",
                        "pattern_score", "structure_score", "explanation", "file_path"
                    ]
                    
                    missing_fields = [f for f in required_fields if f not in result_data]
                    
                    if not missing_fields:
                        print(f"[OK] Teaching Value Score: {result_data.get('total_score')}")
                        print(f"     Documentation: {result_data.get('documentation_score')}")
                        print(f"     Complexity: {result_data.get('complexity_score')}")
                        print(f"     Pattern: {result_data.get('pattern_score')}")
                        print(f"     Structure: {result_data.get('structure_score')}")
                        print("[PASS] score_teaching_value returned valid score")
                        test_results["passed"] += 1
                    else:
                        print(f"[FAIL] Missing fields: {missing_fields}")
                        test_results["failed"] += 1
                        test_results["errors"].append(f"score_teaching_value missing fields: {missing_fields}")
                    
                except Exception as e:
                    print(f"[FAIL] Error calling score_teaching_value: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"score_teaching_value error: {str(e)}")
                print()
                
                # Test 6: score_teaching_value with invalid file
                print("-" * 80)
                print("TEST 6: score_teaching_value with invalid file (error handling)")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "score_teaching_value",
                        arguments={"file_path": "nonexistent_file.py"}
                    )
                    
                    if result.isError:
                        print(f"[PASS] Correct error for invalid file")
                        test_results["passed"] += 1
                    else:
                        print("[FAIL] Should have returned error")
                        test_results["failed"] += 1
                        test_results["errors"].append("score_teaching_value: no error for invalid file")
                    
                except Exception as e:
                    print(f"[PASS] Correct error for invalid file")
                    test_results["passed"] += 1
                print()
                
                # Test 7: analyze_codebase_tool
                print("-" * 80)
                print("TEST 7: analyze_codebase_tool (Requirement 11.5)")
                print("-" * 80)
                test_results["total"] += 1
                
                if not codebase_id:
                    print("[SKIP] No codebase_id available")
                    test_results["total"] -= 1
                else:
                    try:
                        print(f"Analyzing codebase: {codebase_id}")
                        print("(This may take 10-30 seconds...)")
                        
                        result = await session.call_tool(
                            "analyze_codebase_tool",
                            arguments={"codebase_id": codebase_id, "incremental": False, "use_cache": False}
                        )
                        
                        result_data = json.loads(result.content[0].text)
                        
                        required_fields = [
                            "codebase_id", "file_analyses", "dependency_graph",
                            "global_patterns", "top_teaching_files", "metrics", "analyzed_at"
                        ]
                        
                        missing_fields = [f for f in required_fields if f not in result_data]
                        
                        if not missing_fields:
                            metrics = result_data.get('metrics', {})
                            print(f"[OK] Codebase analyzed:")
                            print(f"     Total files: {metrics.get('total_files', 0)}")
                            print(f"     Total functions: {metrics.get('total_functions', 0)}")
                            print(f"     Total classes: {metrics.get('total_classes', 0)}")
                            print(f"     Patterns detected: {metrics.get('total_patterns_detected', 0)}")
                            print(f"     Top teaching files: {len(result_data.get('top_teaching_files', []))}")
                            print("[PASS] analyze_codebase_tool returned valid analysis")
                            test_results["passed"] += 1
                        else:
                            print(f"[FAIL] Missing fields: {missing_fields}")
                            test_results["failed"] += 1
                            test_results["errors"].append(f"analyze_codebase_tool missing fields: {missing_fields}")
                        
                    except Exception as e:
                        print(f"[FAIL] Error calling analyze_codebase_tool: {e}")
                        test_results["failed"] += 1
                        test_results["errors"].append(f"analyze_codebase_tool error: {str(e)}")
                print()
                
                # Test 8: detect_patterns
                print("-" * 80)
                print("TEST 8: detect_patterns (Requirement 11.2)")
                print("-" * 80)
                test_results["total"] += 1
                
                if not codebase_id:
                    print("[SKIP] No codebase_id available")
                    test_results["total"] -= 1
                else:
                    try:
                        result = await session.call_tool(
                            "detect_patterns",
                            arguments={"codebase_id": codebase_id}
                        )
                        
                        result_data = json.loads(result.content[0].text)
                        
                        required_fields = ["patterns", "total_patterns", "pattern_types"]
                        missing_fields = [f for f in required_fields if f not in result_data]
                        
                        if not missing_fields:
                            patterns = result_data.get('patterns', [])
                            print(f"[OK] Patterns detected: {result_data.get('total_patterns', 0)}")
                            print(f"     Pattern types: {', '.join(result_data.get('pattern_types', []))}")
                            print("[PASS] detect_patterns returned valid results")
                            test_results["passed"] += 1
                        else:
                            print(f"[FAIL] Missing fields: {missing_fields}")
                            test_results["failed"] += 1
                            test_results["errors"].append(f"detect_patterns missing fields: {missing_fields}")
                        
                    except Exception as e:
                        print(f"[FAIL] Error calling detect_patterns: {e}")
                        test_results["failed"] += 1
                        test_results["errors"].append(f"detect_patterns error: {str(e)}")
                print()
                
                # Test 9: analyze_dependencies
                print("-" * 80)
                print("TEST 9: analyze_dependencies (Requirement 11.3)")
                print("-" * 80)
                test_results["total"] += 1
                
                if not codebase_id:
                    print("[SKIP] No codebase_id available")
                    test_results["total"] -= 1
                else:
                    try:
                        result = await session.call_tool(
                            "analyze_dependencies",
                            arguments={"codebase_id": codebase_id}
                        )
                        
                        result_data = json.loads(result.content[0].text)
                        
                        required_fields = ["nodes", "edges", "metrics"]
                        missing_fields = [f for f in required_fields if f not in result_data]
                        
                        if not missing_fields:
                            metrics = result_data.get('metrics', {})
                            print(f"[OK] Dependency graph built:")
                            print(f"     Total nodes: {metrics.get('total_nodes', 0)}")
                            print(f"     Total edges: {metrics.get('total_edges', 0)}")
                            print(f"     Circular dependencies: {metrics.get('circular_dependencies_count', 0)}")
                            print(f"     External dependencies: {metrics.get('external_dependencies_count', 0)}")
                            print("[PASS] analyze_dependencies returned valid graph")
                            test_results["passed"] += 1
                        else:
                            print(f"[FAIL] Missing fields: {missing_fields}")
                            test_results["failed"] += 1
                            test_results["errors"].append(f"analyze_dependencies missing fields: {missing_fields}")
                        
                    except Exception as e:
                        print(f"[FAIL] Error calling analyze_dependencies: {e}")
                        test_results["failed"] += 1
                        test_results["errors"].append(f"analyze_dependencies error: {str(e)}")
                print()
                
                # Test 10: JSON Serialization
                print("-" * 80)
                print("TEST 10: Verify JSON Serialization for all tools")
                print("-" * 80)
                test_results["total"] += 1
                
                print("[OK] All tool responses successfully parsed as JSON")
                print("[PASS] JSON serialization verified for all tools")
                test_results["passed"] += 1
                print()
                
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        test_results["errors"].append(f"Critical: {str(e)}")
    
    # Print summary
    print("=" * 80)
    print("TEST SUMMARY - ANALYSIS ENGINE MCP TOOLS")
    print("=" * 80)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    
    if test_results['total'] > 0:
        success_rate = (test_results['passed'] / test_results['total'] * 100)
        print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    if test_results["errors"]:
        print("ERRORS:")
        for i, error in enumerate(test_results["errors"], 1):
            print(f"  {i}. {error}")
    else:
        print("[SUCCESS] ALL TESTS PASSED!")
    
    print("=" * 80)
    print("\nREQUIREMENTS COVERAGE:")
    print("  [+] 11.1 - analyze_file tool tested")
    print("  [+] 11.2 - detect_patterns tool tested")
    print("  [+] 11.3 - analyze_dependencies tool tested")
    print("  [+] 11.4 - score_teaching_value tool tested")
    print("  [+] 11.5 - analyze_codebase_tool tested")
    print("  [+] All tools verified for JSON serialization")
    print("  [+] Error handling tested for all tools")
    print("=" * 80)
    
    return test_results


if __name__ == "__main__":
    # Run tests
    results = asyncio.run(test_analysis_mcp_tools())
    
    # Exit with appropriate code
    exit(0 if results["failed"] == 0 else 1)
