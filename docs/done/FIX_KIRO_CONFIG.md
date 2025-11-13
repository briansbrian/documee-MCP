# 🔧 Fix Kiro Configuration

## The Problem

You're getting this error:
```
ModuleNotFoundError: No module named 'fastmcp'
```

**Cause:** Kiro is using system Python instead of your venv Python.

## The Solution

### Step 1: Copy the Fixed Config

I've created a fixed config file with the full path to your venv Python:

**Windows (PowerShell):**
```powershell
# Copy to your user-level Kiro settings
Copy-Item kiro_config_FIXED.json ~\.kiro\settings\mcp.json -Force
```

**Windows (Command Prompt):**
```cmd
copy kiro_config_FIXED.json %USERPROFILE%\.kiro\settings\mcp.json
```

**macOS/Linux:**
```bash
cp kiro_config_FIXED.json ~/.kiro/settings/mcp.json
```

### Step 2: Restart Kiro

Completely quit and restart Kiro, or reload the MCP server from the MCP Server view.

### Step 3: Test

In Kiro chat:
```
Analyze this codebase using the documee MCP server.
```

## What Changed?

**Before (Broken):**
```json
{
  "command": "python",  // ❌ Uses system Python
  ...
}
```

**After (Fixed):**
```json
{
  "command": "C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe",  // ✅ Uses venv Python
  ...
}
```

## Alternative: Manual Fix

If you prefer to edit manually:

1. Open: `~/.kiro/settings/mcp.json` (or `%USERPROFILE%\.kiro\settings\mcp.json` on Windows)

2. Change this line:
```json
"command": "python",
```

3. To this:
```json
"command": "C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe",
```

4. Save and restart Kiro

## For MCP Inspector

If you're using MCP Inspector, use the full path:

```bash
npx @modelcontextprotocol/inspector C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe -m src.server
```

## Verify It Works

After fixing, you should see:
- ✅ No "ModuleNotFoundError"
- ✅ Server connects successfully
- ✅ Tools are available in Kiro

## Still Not Working?

Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.
