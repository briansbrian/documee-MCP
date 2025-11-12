"""Debug test for analyze_codebase_tool to see what's being returned."""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_codebase_tool():
    server_params = StdioServerParameters(
        command=r".\venv\Scripts\python.exe",
        args=["-m", "src.server"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[OK] Session initialized\n")
            
            # Scan codebase first
            print("[1] Scanning codebase...")
            result = await session.call_tool(
                "scan_codebase",
                arguments={"path": ".", "max_depth": 3}
            )
            
            result_data = json.loads(result.content[0].text)
            codebase_id = result_data.get("codebase_id")
            print(f"[OK] Codebase ID: {codebase_id}\n")
            
            # Try analyze_codebase_tool
            print("[2] Calling analyze_codebase_tool...")
            print("    (This may take 10-30 seconds...)\n")
            
            try:
                result = await session.call_tool(
                    "analyze_codebase_tool",
                    arguments={"codebase_id": codebase_id, "incremental": True}
                )
                
                print(f"[DEBUG] Result type: {type(result)}")
                print(f"[DEBUG] Has isError: {hasattr(result, 'isError')}")
                if hasattr(result, 'isError'):
                    print(f"[DEBUG] isError: {result.isError}")
                print(f"[DEBUG] Content length: {len(result.content)}")
                print(f"[DEBUG] Content[0] type: {type(result.content[0])}")
                print(f"[DEBUG] Content[0] text length: {len(result.content[0].text)}")
                print(f"[DEBUG] Content[0] text (first 500 chars):")
                print(result.content[0].text[:500])
                print()
                
                if result.content[0].text:
                    result_data = json.loads(result.content[0].text)
                    print(f"[OK] Successfully parsed JSON")
                    print(f"[OK] Keys: {list(result_data.keys())}")
                else:
                    print("[FAIL] Empty response")
                    
            except json.JSONDecodeError as e:
                print(f"[FAIL] JSON decode error: {e}")
                print(f"[DEBUG] Raw text: '{result.content[0].text}'")
            except Exception as e:
                print(f"[FAIL] Error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_codebase_tool())
