"""
Automated test script for MCP Server using MCP Inspector.

This script tests all the requirements from Task 13:
- Server connection and initialization
- List tools (3 expected)
- List resources (2 expected)
- List prompts (1 expected)
- Test each tool with valid and invalid inputs
- Test resources
- Test prompts
- Verify parameter validation
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Run comprehensive tests on the MCP server."""
    
    print("=" * 80)
    print("MCP SERVER COMPREHENSIVE TEST SUITE")
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
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                # Initialize the session
                print("📡 Initializing MCP session...")
                await session.initialize()
                print("✅ Session initialized successfully\n")
                test_results["total"] += 1
                test_results["passed"] += 1
                
                # Test 1: List Tools
                print("-" * 80)
                print("TEST 1: List Tools (Expected: 3)")
                print("-" * 80)
                test_results["total"] += 1
                
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description[:60]}...")
                
                expected_tools = {"scan_codebase", "detect_frameworks", "discover_features"}
                actual_tools = {tool.name for tool in tools.tools}
                
                if actual_tools == expected_tools:
                    print("✅ PASS: All 3 expected tools found")
                    test_results["passed"] += 1
                else:
                    print(f"❌ FAIL: Expected {expected_tools}, got {actual_tools}")
                    test_results["failed"] += 1
                    test_results["errors"].append("Tool list mismatch")
                print()
                
                # Test 2: List Resources
                print("-" * 80)
                print("TEST 2: List Resources (Expected: 2)")
                print("-" * 80)
                test_results["total"] += 1
                
                resources = await session.list_resources()
                print(f"Found {len(resources.resources)} resources:")
                for resource in resources.resources:
                    print(f"  - {resource.uri}: {resource.name}")
                
                expected_resources = {"codebase://structure", "codebase://features"}
                actual_resources = {str(resource.uri) for resource in resources.resources}
                
                if actual_resources == expected_resources:
                    print("✅ PASS: All 2 expected resources found")
                    test_results["passed"] += 1
                else:
                    print(f"❌ FAIL: Expected {expected_resources}, got {actual_resources}")
                    test_results["failed"] += 1
                    test_results["errors"].append("Resource list mismatch")
                print()
                
                # Test 3: List Prompts
                print("-" * 80)
                print("TEST 3: List Prompts (Expected: 1)")
                print("-" * 80)
                test_results["total"] += 1
                
                prompts = await session.list_prompts()
                print(f"Found {len(prompts.prompts)} prompts:")
                for prompt in prompts.prompts:
                    print(f"  - {prompt.name}: {prompt.description[:60]}...")
                
                expected_prompts = {"analyze_codebase"}
                actual_prompts = {prompt.name for prompt in prompts.prompts}
                
                if actual_prompts == expected_prompts:
                    print("✅ PASS: Expected prompt 'analyze_codebase' found")
                    test_results["passed"] += 1
                else:
                    print(f"❌ FAIL: Expected {expected_prompts}, got {actual_prompts}")
                    test_results["failed"] += 1
                    test_results["errors"].append("Prompt list mismatch")
                print()
                
                # Test 4: scan_codebase with valid path
                print("-" * 80)
                print("TEST 4: scan_codebase with valid path")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "scan_codebase",
                        arguments={"path": ".", "max_depth": 5}
                    )
                    
                    # Parse result
                    result_data = json.loads(result.content[0].text)
                    codebase_id = result_data.get("codebase_id")
                    
                    print(f"Codebase ID: {codebase_id}")
                    print(f"Total files: {result_data.get('structure', {}).get('total_files', 'N/A')}")
                    print(f"Project type: {result_data.get('summary', {}).get('project_type', 'N/A')}")
                    
                    if codebase_id:
                        print("✅ PASS: scan_codebase returned valid result")
                        test_results["passed"] += 1
                        
                        # Store codebase_id for later tests
                        global stored_codebase_id
                        stored_codebase_id = codebase_id
                    else:
                        print("❌ FAIL: No codebase_id in response")
                        test_results["failed"] += 1
                        test_results["errors"].append("scan_codebase missing codebase_id")
                        
                except Exception as e:
                    print(f"❌ FAIL: Error calling scan_codebase: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"scan_codebase error: {str(e)}")
                print()
                
                # Test 5: scan_codebase with invalid path (security test)
                print("-" * 80)
                print("TEST 5: scan_codebase with invalid path (security)")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "scan_codebase",
                        arguments={"path": "../../../etc/passwd"}
                    )
                    
                    # Check if result is an error
                    if result.isError:
                        error_text = result.content[0].text.lower()
                        if "traversal" in error_text or "invalid" in error_text or "outside" in error_text:
                            print(f"✅ PASS: Correctly rejected invalid path: {result.content[0].text}")
                            test_results["passed"] += 1
                        else:
                            print(f"⚠️  PARTIAL: Error returned but message unclear: {result.content[0].text}")
                            test_results["passed"] += 1
                    else:
                        print("❌ FAIL: Should have returned an error for directory traversal")
                        test_results["failed"] += 1
                        test_results["errors"].append("Security: directory traversal not blocked")
                    
                except Exception as e:
                    error_str = str(e).lower()
                    if "traversal" in error_str or "invalid" in error_str or "outside" in error_str:
                        print(f"✅ PASS: Correctly rejected invalid path: {e}")
                        test_results["passed"] += 1
                    else:
                        print(f"⚠️  PARTIAL: Error raised but message unclear: {e}")
                        test_results["passed"] += 1
                print()
                
                # Test 6: detect_frameworks with valid codebase_id
                print("-" * 80)
                print("TEST 6: detect_frameworks with valid codebase_id")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "detect_frameworks",
                        arguments={"codebase_id": stored_codebase_id}
                    )
                    
                    result_data = json.loads(result.content[0].text)
                    frameworks = result_data.get("frameworks", [])
                    
                    print(f"Detected {len(frameworks)} frameworks:")
                    for fw in frameworks[:5]:  # Show first 5
                        print(f"  - {fw.get('name')}: {fw.get('confidence', 0):.2f}")
                    
                    print("✅ PASS: detect_frameworks returned valid result")
                    test_results["passed"] += 1
                    
                except Exception as e:
                    print(f"❌ FAIL: Error calling detect_frameworks: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"detect_frameworks error: {str(e)}")
                print()
                
                # Test 7: detect_frameworks with nonexistent codebase_id
                print("-" * 80)
                print("TEST 7: detect_frameworks with nonexistent codebase_id")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "detect_frameworks",
                        arguments={"codebase_id": "nonexistent_id_12345"}
                    )
                    
                    # Check if result is an error
                    if result.isError:
                        error_text = result.content[0].text.lower()
                        if "not scanned" in error_text or "scan_codebase" in error_text:
                            print(f"✅ PASS: Correct error message: {result.content[0].text}")
                            test_results["passed"] += 1
                        else:
                            print(f"⚠️  PARTIAL: Error returned but message unclear: {result.content[0].text}")
                            test_results["passed"] += 1
                    else:
                        print("❌ FAIL: Should have returned an error for nonexistent codebase_id")
                        test_results["failed"] += 1
                        test_results["errors"].append("detect_frameworks: no error for invalid ID")
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    if "not scanned" in error_msg or "scan_codebase" in error_msg:
                        print(f"✅ PASS: Correct error message: {e}")
                        test_results["passed"] += 1
                    else:
                        print(f"⚠️  PARTIAL: Error raised but message unclear: {e}")
                        test_results["passed"] += 1
                print()
                
                # Test 8: discover_features with valid codebase_id and categories
                print("-" * 80)
                print("TEST 8: discover_features with valid codebase_id")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "discover_features",
                        arguments={
                            "codebase_id": stored_codebase_id,
                            "categories": ["routes", "api"]
                        }
                    )
                    
                    result_data = json.loads(result.content[0].text)
                    features = result_data.get("features", [])
                    total = result_data.get("total_features", 0)
                    
                    print(f"Discovered {total} features")
                    for feat in features[:3]:  # Show first 3
                        print(f"  - {feat.get('name')} ({feat.get('category')})")
                    
                    print("✅ PASS: discover_features returned valid result")
                    test_results["passed"] += 1
                    
                except Exception as e:
                    print(f"❌ FAIL: Error calling discover_features: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"discover_features error: {str(e)}")
                print()
                
                # Test 9: discover_features with empty codebase_id
                print("-" * 80)
                print("TEST 9: discover_features with empty codebase_id")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.call_tool(
                        "discover_features",
                        arguments={"codebase_id": "", "categories": ["routes"]}
                    )
                    
                    # Check if result is an error
                    if result.isError:
                        error_text = result.content[0].text.lower()
                        if "empty" in error_text or "cannot be empty" in error_text:
                            print(f"✅ PASS: Correct validation error: {result.content[0].text}")
                            test_results["passed"] += 1
                        else:
                            print(f"⚠️  PARTIAL: Error returned: {result.content[0].text}")
                            test_results["passed"] += 1
                    else:
                        print("❌ FAIL: Should have returned validation error for empty codebase_id")
                        test_results["failed"] += 1
                        test_results["errors"].append("discover_features: no validation for empty ID")
                    
                except Exception as e:
                    error_str = str(e).lower()
                    if "empty" in error_str or "cannot be empty" in error_str or "required" in error_str:
                        print(f"✅ PASS: Correct validation error: {e}")
                        test_results["passed"] += 1
                    else:
                        print(f"⚠️  PARTIAL: Error raised: {e}")
                        test_results["passed"] += 1
                print()
                
                # Test 10: Read resource codebase://structure
                print("-" * 80)
                print("TEST 10: Read resource codebase://structure")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.read_resource("codebase://structure")
                    
                    resource_data = json.loads(result.contents[0].text)
                    print(f"Structure data keys: {list(resource_data.keys())}")
                    
                    print("✅ PASS: Resource codebase://structure readable")
                    test_results["passed"] += 1
                    
                except Exception as e:
                    print(f"❌ FAIL: Error reading resource: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"Resource structure error: {str(e)}")
                print()
                
                # Test 11: Read resource codebase://features
                print("-" * 80)
                print("TEST 11: Read resource codebase://features")
                print("-" * 80)
                test_results["total"] += 1
                
                # Note: This test depends on Test 8 (discover_features) being run first
                # The resource is populated when discover_features is called
                try:
                    result = await session.read_resource("codebase://features")
                    
                    resource_data = json.loads(result.contents[0].text)
                    print(f"Features data keys: {list(resource_data.keys())}")
                    
                    print("✅ PASS: Resource codebase://features readable")
                    test_results["passed"] += 1
                    
                except Exception as e:
                    print(f"❌ FAIL: Error reading resource: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"Resource features error: {str(e)}")
                print()
                
                # Test 12: Get prompt analyze_codebase
                print("-" * 80)
                print("TEST 12: Get prompt analyze_codebase")
                print("-" * 80)
                test_results["total"] += 1
                
                try:
                    result = await session.get_prompt(
                        "analyze_codebase",
                        arguments={"codebase_path": "./test-project"}
                    )
                    
                    prompt_text = result.messages[0].content.text
                    
                    if "./test-project" in prompt_text and "Step 1" in prompt_text:
                        print("✅ PASS: Prompt template returned with interpolated path")
                        print(f"Template length: {len(prompt_text)} characters")
                        test_results["passed"] += 1
                    else:
                        print("❌ FAIL: Prompt template missing expected content")
                        test_results["failed"] += 1
                        test_results["errors"].append("Prompt template incomplete")
                    
                except Exception as e:
                    print(f"❌ FAIL: Error getting prompt: {e}")
                    test_results["failed"] += 1
                    test_results["errors"].append(f"Prompt error: {str(e)}")
                print()
                
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        test_results["errors"].append(f"Critical: {str(e)}")
    
    # Print summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Success Rate: {(test_results['passed'] / test_results['total'] * 100):.1f}%")
    print()
    
    if test_results["errors"]:
        print("ERRORS:")
        for i, error in enumerate(test_results["errors"], 1):
            print(f"  {i}. {error}")
    else:
        print("🎉 ALL TESTS PASSED!")
    print("=" * 80)
    
    return test_results


if __name__ == "__main__":
    # Global variable to store codebase_id between tests
    stored_codebase_id = None
    
    # Run tests
    results = asyncio.run(test_mcp_server())
    
    # Exit with appropriate code
    exit(0 if results["failed"] == 0 else 1)
