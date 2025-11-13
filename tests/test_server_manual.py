"""
Manual test of MCP server via stdio.
This simulates what Kiro/Claude/Inspector do.
"""
import subprocess
import json
import sys

def test_server():
    """Test the MCP server by sending JSON-RPC messages."""
    
    # Start server process
    process = subprocess.Popen(
        [sys.executable, "-m", "src.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # Send initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialize request...")
        process.stdin.write(json.dumps(initialize_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Response: {response}")
        
        # Send tools/list request
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\nSending tools/list request...")
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Response: {response}")
        
        # Parse and show tools
        tools_response = json.loads(response)
        if "result" in tools_response and "tools" in tools_response["result"]:
            print(f"\nFound {len(tools_response['result']['tools'])} tools:")
            for tool in tools_response["result"]["tools"]:
                print(f"  - {tool['name']}")
        
    except Exception as e:
        print(f"Error: {e}")
        stderr = process.stderr.read()
        if stderr:
            print(f"Server stderr: {stderr}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_server()
