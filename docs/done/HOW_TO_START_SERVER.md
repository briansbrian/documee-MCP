# How to Start the MCP Server

## Understanding MCP Server Architecture

The Documee MCP Server uses **stdio transport**, which means:
- It communicates via standard input/output (not HTTP)
- It's **event-driven** - waits for JSON-RPC messages
- It's **managed by a client** (Kiro, Claude Desktop, or MCP Inspector)
- You don't "start" it like a web server - clients start it automatically

## ❌ What NOT to Do

```bash
# This will appear to "hang" - it's waiting for JSON-RPC input
python -m src.server

# This is normal! The server is running, just waiting for messages.
```

## ✅ How to Actually Use the Server

### Option 1: MCP Inspector (Best for Testing)

**What it does:** Starts the server AND provides a web UI for testing

```bash
npx @modelcontextprotocol/inspector python -m src.server
```

**Result:**
- Opens browser at `http://localhost:5173`
- Shows all tools, resources, and prompts
- Lets you test with custom parameters
- Displays responses in nice format

**Use this for:**
- Testing individual tools
- Debugging
- Exploring capabilities
- Verifying server works

### Option 2: Kiro IDE (Best for Development)

**What it does:** Automatically starts/stops the server as needed

**Setup:**
1. Copy config:
```bash
cp examples/kiro_config.json .kiro/settings/mcp.json
```

2. Restart Kiro

3. Use in chat:
```
Analyze this codebase using the documee MCP server.
```

**How it works:**
- Kiro reads `.kiro/settings/mcp.json`
- Kiro starts `python -m src.server` automatically
- Kiro sends JSON-RPC messages to the server
- Kiro displays results in chat
- Kiro stops the server when done

**Use this for:**
- Real development work
- Analyzing codebases
- Generating courses
- Production use

### Option 3: Claude Desktop (Best for End Users)

**What it does:** Same as Kiro, but for Claude Desktop

**Setup:**
1. Edit config file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add server:
```json
{
  "mcpServers": {
    "documee": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "C:\\Users\\brian\\OneDrive\\Documents\\Apps\\Documee_mcp"
    }
  }
}
```

3. Restart Claude Desktop

4. Look for 🔌 icon

5. Use in chat:
```
Analyze the codebase at C:\Users\brian\OneDrive\Documents\Apps\Documee_mcp
```

**Use this for:**
- Non-technical users
- Natural language interface
- Consumer applications

### Option 4: Programmatic Testing

**What it does:** Test the server from Python code

```bash
# Run the test script
python test_mcp_local.py
```

This script:
- Initializes the cache manager
- Calls tools directly (bypassing MCP protocol)
- Tests the complete workflow
- Shows performance metrics

**Use this for:**
- Unit testing
- Performance benchmarking
- CI/CD pipelines
- Automated testing

## Why Does `python -m src.server` Appear to Hang?

It's not hanging! It's working correctly. Here's what's happening:

1. **Server starts** - Initializes cache, loads config
2. **Server waits** - Listens on stdin for JSON-RPC messages
3. **No output** - Won't print anything until it receives a message
4. **Event-driven** - Only responds when client sends requests

This is the **correct behavior** for an MCP server!

## How Clients Start the Server

When Kiro or Claude Desktop starts the server, they:

1. Run: `python -m src.server`
2. Server process starts (appears to "hang")
3. Client sends JSON-RPC initialize message
4. Server responds with capabilities
5. Client sends tool requests
6. Server responds with results
7. Client terminates server when done

## Testing the Server is Working

### Quick Test (30 seconds)

```bash
# Run integration test
python test_mcp_local.py
```

**Expected output:**
```
============================================================
Testing MCP Server Locally
============================================================

[Test 1] Scanning codebase...
✓ Scan complete!
  - Codebase ID: 803c025b281694d1
  - Total files: 389
  - Languages: ['Python', 'JavaScript']
  - Scan time: 65.71ms

[Test 2] Detecting frameworks...
✓ Detection complete!
  - Frameworks found: 1

[Test 3] Discovering features...
✓ Discovery complete!
  - Features found: 2

[Test 4] Testing cache performance...
✓ Cache test complete!

✓ All tests passed!
```

### Full Test (2 minutes)

```bash
# Start MCP Inspector
npx @modelcontextprotocol/inspector python -m src.server
```

**Expected result:**
- Browser opens at `http://localhost:5173`
- Shows 11 tools, 2 resources, 1 prompt
- Can test each tool interactively

## Common Questions

### Q: Why doesn't the server print anything?

**A:** MCP servers use stdio for communication. All output goes through JSON-RPC messages, not console prints. Logs go to `server.log`.

### Q: How do I know if the server is running?

**A:** 
- If started by Inspector: Check browser at `http://localhost:5173`
- If started by Kiro: Check MCP Server view in Kiro
- If started manually: Check `server.log` for startup messages

### Q: Can I run the server as a web service?

**A:** Not directly. MCP uses stdio transport. For web access, you'd need to:
1. Deploy to Azure (Spec 4)
2. Use Azure Container Instances
3. Expose via HTTP endpoint
4. Use MCP HTTP transport (different from stdio)

### Q: How do I stop the server?

**A:**
- Inspector: Close browser tab, server stops automatically
- Kiro: Server stops when Kiro closes or reloads config
- Manual: Press Ctrl+C
- Programmatic: Process terminates when client disconnects

## Summary

**Don't start the server manually!** Let the client (Inspector, Kiro, Claude) manage it.

**For testing:** Use `python test_mcp_local.py` or MCP Inspector

**For production:** Use Kiro or Claude Desktop

**The server is working correctly** - it's just waiting for JSON-RPC messages!

---

**Quick Reference:**

| Use Case | Command |
|----------|---------|
| Testing | `npx @modelcontextprotocol/inspector python -m src.server` |
| Development | Configure in Kiro, use in chat |
| End Users | Configure in Claude Desktop |
| Unit Tests | `python test_mcp_local.py` |
| Debugging | Check `server.log` |

---

**Status:** ✅ Server is working correctly  
**Next:** Test with MCP Inspector or integrate with Kiro
