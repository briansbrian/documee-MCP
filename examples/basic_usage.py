"""
Basic MCP Client Example - Demonstrating All 3 Core Tools

This example demonstrates how to use the MCP client to interact with the
codebase-to-course-mcp server and call all 3 core discovery tools:
1. scan_codebase - Scan codebase structure and languages
2. detect_frameworks - Detect frameworks with confidence scores
3. discover_features - Find features like routes, components, API endpoints

Testing Methods:
1. MCP Inspector: npx @modelcontextprotocol/inspector python -m src.server
2. Development Mode: uv run mcp dev src/server.py
3. Direct Run: python -m src.server

Requirements:
- Python 3.12+
- mcp package installed (pip install mcp)
- Server running (python -m src.server)
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Main function demonstrating all 3 MCP tools."""
    
    # Configure server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"],
        env=None
    )
    
    print("=" * 80)
    print("MCP Client Example - Codebase Analysis Workflow")
    print("=" * 80)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("\n✓ Connected to MCP server")
            
            # List available tools
            tools = await session.list_tools()
            print(f"\n✓ Available tools: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # List available resources
            resources = await session.list_resources()
            print(f"\n✓ Available resources: {len(resources.resources)}")
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")
            
            # List available prompts
            prompts = await session.list_prompts()
            print(f"\n✓ Available prompts: {len(prompts.prompts)}")
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}: {prompt.description}")
            
            print("\n" + "=" * 80)
            print("STEP 1: Scan Codebase Structure")
            print("=" * 80)
            
            # Tool 1: scan_codebase
            scan_result = await session.call_tool(
                "scan_codebase",
                arguments={
                    "path": ".",
                    "max_depth": 5,
                    "use_cache": True
                }
            )
            
            scan_data = json.loads(scan_result.content[0].text)
            print(f"\n✓ Scan completed in {scan_data['scan_time_ms']:.2f}ms")
            print(f"  Codebase ID: {scan_data['codebase_id']}")
            print(f"  Total Files: {scan_data['structure']['total_files']}")
            print(f"  Total Directories: {scan_data['structure']['total_directories']}")
            print(f"  Total Size: {scan_data['structure']['total_size_mb']:.2f} MB")
            print(f"  Primary Language: {scan_data['summary']['primary_language']}")
            print(f"  Project Type: {scan_data['summary']['project_type']}")
            print(f"  Has Tests: {scan_data['summary']['has_tests']}")
            print(f"  Size Category: {scan_data['summary']['size_category']}")
            print(f"  From Cache: {scan_data['from_cache']}")
            
            # Display language breakdown
            print("\n  Languages detected:")
            for lang, count in scan_data['structure']['languages'].items():
                print(f"    - {lang}: {count} files")
            
            # Save codebase_id for next steps
            codebase_id = scan_data['codebase_id']
            
            print("\n" + "=" * 80)
            print("STEP 2: Detect Frameworks")
            print("=" * 80)
            
            # Tool 2: detect_frameworks
            frameworks_result = await session.call_tool(
                "detect_frameworks",
                arguments={
                    "codebase_id": codebase_id,
                    "confidence_threshold": 0.7,
                    "use_cache": True
                }
            )
            
            frameworks_data = json.loads(frameworks_result.content[0].text)
            print(f"\n✓ Detected {frameworks_data['total_detected']} frameworks")
            print(f"  Confidence Threshold: {frameworks_data['confidence_threshold']}")
            print(f"  From Cache: {frameworks_data['from_cache']}")
            
            if frameworks_data['frameworks']:
                print("\n  Frameworks found:")
                for fw in frameworks_data['frameworks']:
                    print(f"    - {fw['name']} v{fw['version']}")
                    print(f"      Confidence: {fw['confidence']:.2%}")
                    print(f"      Evidence: {', '.join(fw['evidence'])}")
            else:
                print("\n  No frameworks detected above threshold")
            
            print("\n" + "=" * 80)
            print("STEP 3: Discover Features")
            print("=" * 80)
            
            # Tool 3: discover_features (all categories)
            features_result = await session.call_tool(
                "discover_features",
                arguments={
                    "codebase_id": codebase_id,
                    "categories": ["all"],
                    "use_cache": True
                }
            )
            
            features_data = json.loads(features_result.content[0].text)
            print(f"\n✓ Discovered {features_data['total_features']} features")
            print(f"  Categories: {', '.join(features_data['categories'])}")
            print(f"  From Cache: {features_data['from_cache']}")
            
            if features_data['features']:
                print("\n  Features found:")
                # Group by category
                by_category = {}
                for feature in features_data['features']:
                    cat = feature['category']
                    if cat not in by_category:
                        by_category[cat] = []
                    by_category[cat].append(feature)
                
                for category, features in by_category.items():
                    print(f"\n    {category.upper()}:")
                    for feature in features:
                        print(f"      - {feature['name']} (Priority: {feature['priority']})")
                        print(f"        Path: {feature['path']}")
                        print(f"        ID: {feature['id']}")
            else:
                print("\n  No features discovered")
            
            print("\n" + "=" * 80)
            print("STEP 4: Access Resources")
            print("=" * 80)
            
            # Read resource: codebase://structure
            try:
                structure_resource = await session.read_resource("codebase://structure")
                print("\n✓ Retrieved codebase://structure resource")
                print(f"  MIME Type: {structure_resource.contents[0].mimeType}")
                print(f"  Data available: Yes")
            except Exception as e:
                print(f"\n✗ Failed to retrieve structure resource: {e}")
            
            # Read resource: codebase://features
            try:
                features_resource = await session.read_resource("codebase://features")
                print("\n✓ Retrieved codebase://features resource")
                print(f"  MIME Type: {features_resource.contents[0].mimeType}")
                print(f"  Data available: Yes")
            except Exception as e:
                print(f"\n✗ Failed to retrieve features resource: {e}")
            
            print("\n" + "=" * 80)
            print("STEP 5: Get Analysis Prompt")
            print("=" * 80)
            
            # Get prompt: analyze_codebase
            prompt_result = await session.get_prompt(
                "analyze_codebase",
                arguments={"codebase_path": "."}
            )
            
            print("\n✓ Retrieved analyze_codebase prompt")
            print(f"  Description: {prompt_result.description}")
            print("\n  Prompt template:")
            for message in prompt_result.messages:
                print(f"    {message.content.text[:200]}...")
            
            print("\n" + "=" * 80)
            print("Analysis Complete!")
            print("=" * 80)
            print("\nSummary:")
            print(f"  - Scanned {scan_data['structure']['total_files']} files")
            print(f"  - Detected {frameworks_data['total_detected']} frameworks")
            print(f"  - Discovered {features_data['total_features']} features")
            print(f"  - Primary language: {scan_data['summary']['primary_language']}")
            print(f"  - Project type: {scan_data['summary']['project_type']}")
            print("\n✓ All tools executed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
