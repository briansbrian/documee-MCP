# Quick Start - Documee MCP Server

## 🚀 5-Minute Setup

### 1. Verify Installation

```bash
# Check Python version (need 3.12+)
python --version

# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Verify dependencies
pip list | grep fastmcp
```

### 2. Test Locally

**Important:** Don't run `python -m src.server` directly - it will appear to "hang" (this is normal, it's waiting for JSON-RPC messages).

Instead, use one of these:

```bash
# Option A: Quick integration test (30 seconds)
python test_mcp_local.py

# Expected output:
# ✓ Scan complete! (65.71ms, 389 files)
# ✓ Detection complete! (1 framework found)
# ✓ Discovery complete! (2 features found)
# ✓ All tests passed!

# Option B: MCP Inspector (interactive testing)
npx @modelcontextprotocol/inspector python -m src.server
# Opens browser at http://localhost:5173
```

### 3. Integrate with Kiro

```bash
# Copy config
cp examples/kiro_config.json .kiro/settings/mcp.json

# Restart Kiro

# Test in Kiro chat:
# "Analyze this codebase using the documee MCP server."
```

## 🔧 Available Tools

### Core Discovery Tools (Spec 1)

1. **scan_codebase** - Analyze directory structure
   ```json
   {"path": ".", "max_depth": 5, "use_cache": true}
   ```

2. **detect_frameworks** - Identify tech stack
   ```json
   {"codebase_id": "<id>", "confidence_threshold": 0.7, "use_cache": true}
   ```

3. **discover_features** - Find routes, components, APIs
   ```json
   {"codebase_id": "<id>", "categories": [], "use_cache": true}
   ```

### Analysis Tools (Spec 2)

4. **analyze_file** - Deep file analysis
   ```json
   {"file_path": "src/main.py", "force": false}
   ```

5. **detect_patterns** - Pattern detection
   ```json
   {"codebase_id": "<id>", "use_cache": true}
   ```

6. **analyze_dependencies** - Dependency graph
   ```json
   {"codebase_id": "<id>", "use_cache": true}
   ```

7. **score_teaching_value** - Teaching value scoring
   ```json
   {"file_path": "src/main.py", "force": false}
   ```

### Course Generation Tools (Spec 3)

8. **generate_course_outline** - Course structure
   ```json
   {"codebase_id": "<id>", "target_audience": "intermediate"}
   ```

9. **generate_lesson_content** - Lesson content
   ```json
   {"lesson_id": "<id>", "include_exercises": true}
   ```

10. **generate_exercise** - Hands-on exercises
    ```json
    {"lesson_id": "<id>", "difficulty": "medium"}
    ```

11. **export_course** - Export to MkDocs/Next.js/JSON
    ```json
    {"codebase_id": "<id>", "format": "mkdocs", "output_path": "./output"}
    ```

## 📊 Performance

| Operation | Time | Status |
|-----------|------|--------|
| scan_codebase | 65ms | ✅ |
| detect_frameworks | ~50ms | ✅ |
| discover_features | ~50ms | ✅ |
| Cache hit | <10ms | ✅ |

## 🐛 Troubleshooting

### Server won't start
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check for errors
python -m src.server
```

### Cache not working
```bash
# Clear cache
rm cache_db/cache.db

# Restart server
```

### MCP Inspector won't connect
```bash
# Check Node.js version
node --version  # Need 18+

# Try different port
npx @modelcontextprotocol/inspector --port 5174 python -m src.server
```

## 📚 Documentation

- **README.md** - Complete documentation
- **LOCAL_TEST_GUIDE.md** - Testing guide
- **TESTING_COMPLETE.md** - Test results
- **docs/** - Technical docs

## 🎯 Next Steps

1. ✅ Test locally (done!)
2. ⏳ Integrate with Kiro/Claude
3. ⏳ Test with real codebases
4. ⏳ Create Spec 4 (Azure Deployment)

## 💡 Tips

- Always run `scan_codebase` first to get `codebase_id`
- Use `use_cache: true` for faster subsequent calls
- Check `server.log` for detailed logs
- Use MCP Inspector for interactive testing

---

**Status:** ✅ Ready to use  
**Version:** 1.0.0  
**Last Updated:** November 13, 2025
