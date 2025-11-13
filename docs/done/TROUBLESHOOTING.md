# Troubleshooting Guide

## ❌ Error: "ModuleNotFoundError: No module named 'fastmcp'"

### Symptom
When starting the MCP server (via Inspector or Kiro), you see:
```
ModuleNotFoundError: No module named 'fastmcp'
```

### Cause
The server is being started with the **system Python** instead of your **virtual environment Python**. The `fastmcp` module is installed in your venv, but the system Python doesn't have it.

### Solution

**Option 1: Use Full Path to venv Python (Recommended)**

Update your config to use the full path to the venv Python:

**For Kiro** (`.kiro/settings/mcp.json`):
```json
{
  "mcpServers": {
    "codebase-to-course-mcp": {
      "command": "C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe",
      "args": ["-m", "src.server"],
      "cwd": "C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp",
      "disabled": false,
      "env": {
        "CACHE_MAX_SIZE_MB": "500",
        "MAX_FILE_SIZE_MB": "10"
      },
      "autoApprove": [
        "scan_codebase",
        "detect_frameworks",
        "discover_features"
      ]
    }
  }
}
```

**For MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe -m src.server
```

**For Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "documee": {
      "command": "C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe",
      "args": ["-m", "src.server"],
      "cwd": "C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp"
    }
  }
}
```

**Option 2: Install Dependencies Globally (Not Recommended)**

```bash
# Install fastmcp globally (not recommended)
pip install -r requirements.txt
```

This works but pollutes your global Python environment.

### Quick Fix

I've created a fixed config file for you:

```bash
# Copy the fixed config
cp kiro_config_FIXED.json ~/.kiro/settings/mcp.json

# Or manually edit your Kiro config
# Change "command": "python" to full path
```

---

## ❌ Error: Server Appears to "Hang"

### Symptom
Running `python -m src.server` shows no output and appears frozen.

### Cause
This is **normal behavior**! MCP servers use stdio transport and wait for JSON-RPC messages.

### Solution
Don't run the server directly. Use one of these instead:

1. **MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe -m src.server
```

2. **Quick Test:**
```bash
python test_mcp_local.py
```

3. **Kiro Integration:**
Configure in `.kiro/settings/mcp.json` and use in Kiro chat.

---

## ❌ Error: Cache Database Locked

### Symptom
```
sqlite3.OperationalError: database is locked
```

### Cause
Multiple server instances trying to access the same cache database.

### Solution
```bash
# Stop all server instances
# Delete cache database
rm cache_db/cache.db

# Restart server
```

---

## ❌ Error: Permission Denied

### Symptom
```
PermissionError: [Errno 13] Permission denied: '/path/to/file'
```

### Cause
The server doesn't have permission to read certain files.

### Solution
- The server automatically skips files it can't read
- Check file permissions: `ls -la /path/to/file`
- Add directory to `blocked_patterns` in `config.yaml`

---

## ❌ Error: MCP Inspector Won't Connect

### Symptom
Inspector shows "Failed to connect to MCP server"

### Cause
- Server not starting correctly
- Port conflict
- Node.js version too old

### Solution

1. **Check Node.js version:**
```bash
node --version  # Need 18+
```

2. **Try different port:**
```bash
npx @modelcontextprotocol/inspector --port 5174 C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe -m src.server
```

3. **Check server starts:**
```bash
# Test server directly
python test_mcp_local.py
```

4. **Check logs:**
```bash
# View server logs
cat server.log
```

---

## ❌ Error: Slow Performance

### Symptom
- Scans taking >10 seconds
- Cache hit rate <50%

### Solution

1. **Increase cache size** (`config.yaml`):
```yaml
cache:
  memory:
    max_size_mb: 1000
```

2. **Enable Redis** (optional):
```yaml
cache:
  redis:
    enabled: true
    url: redis://localhost:6379
```

3. **Check logs:**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m src.server
```

---

## ❌ Error: Framework Detection Not Working

### Symptom
```json
{
  "frameworks": [],
  "total_detected": 0
}
```

### Cause
- No `package.json` or `requirements.txt` in project
- File is malformed
- Codebase not scanned first

### Solution

1. **Ensure codebase scanned first:**
```bash
# Must call scan_codebase before detect_frameworks
```

2. **Check files exist:**
```bash
ls package.json
ls requirements.txt
```

3. **Verify file format:**
```bash
# Check package.json is valid JSON
cat package.json | python -m json.tool
```

---

## 🔍 Debug Mode

Enable detailed logging:

**Environment Variable:**
```bash
export LOG_LEVEL=DEBUG
```

**Config File** (`config.yaml`):
```yaml
logging:
  level: DEBUG
```

**Check Logs:**
```bash
tail -f server.log
```

---

## ✅ Verify Installation

Run these checks:

```bash
# 1. Check Python version
python --version  # Need 3.12+

# 2. Check venv activated
which python  # Should show venv path

# 3. Check dependencies
pip list | grep fastmcp

# 4. Run tests
pytest tests/ -v

# 5. Run integration test
python test_mcp_local.py

# 6. Check server starts
npx @modelcontextprotocol/inspector C:/Users/brian/OneDrive/Documents/Apps/Documee_mcp/venv/Scripts/python.exe -m src.server
```

---

## 📞 Still Having Issues?

1. **Check logs:** `server.log` has detailed error information
2. **Run tests:** `pytest tests/ -v` to verify installation
3. **Check config:** Verify paths in config files are correct
4. **Try fresh install:**
```bash
# Delete venv
rm -rf venv

# Recreate venv
python -m venv venv

# Activate venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt

# Test
python test_mcp_local.py
```

---

## 🎯 Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| ModuleNotFoundError | Use full path to venv Python in config |
| Server hangs | Normal! Use Inspector or test script |
| Cache locked | Delete `cache_db/cache.db` |
| Permission denied | Server skips files automatically |
| Inspector won't connect | Check Node.js version, try different port |
| Slow performance | Increase cache size in config.yaml |
| No frameworks detected | Run scan_codebase first |

---

**Most Common Issue:** Using system Python instead of venv Python

**Quick Fix:** Use `kiro_config_FIXED.json` which has the full path to venv Python
