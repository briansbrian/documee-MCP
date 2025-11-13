"""
Example: Using MCP Tools

This example demonstrates how to use the Analysis Engine through MCP tools.
It shows how AI assistants like Claude can interact with the analysis engine.

Note: This example simulates MCP tool calls. In production, these would be
called by an MCP client (like Claude Desktop or MCP Inspector).
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def simulate_mcp_tool_call(tool_name: str, arguments: dict):
    """
    Simulate an MCP tool call.
    
    In production, this would be handled by the MCP server and client.
    """
    print(f"\n📞 MCP Tool Call: {tool_name}")
    print(f"   Arguments: {arguments}")
    
    # Import the actual tool implementations
    if tool_name == "analyze_file":
        from src.analysis import AnalysisEngine, AnalysisConfig
        from src.cache import CacheManager
        
        engine = AnalysisEngine(CacheManager(), AnalysisConfig())
        result = await engine.analyze_file(arguments["file_path"])
        
        # Return simplified result (as MCP would)
        return {
            "file_path": result.file_path,
            "language": result.language,
            "functions_count": len(result.symbol_info.functions),
            "classes_count": len(result.symbol_info.classes),
            "teaching_value": result.teaching_value.total_score,
            "patterns": [p.pattern_type for p in result.patterns],
            "complexity": {
                "average": result.complexity_metrics.avg_complexity,
                "max": result.complexity_metrics.max_complexity
            },
            "documentation_coverage": result.documentation_coverage
        }
    
    elif tool_name == "score_teaching_value":
        from src.analysis import AnalysisEngine, AnalysisConfig
        from src.cache import CacheManager
        
        engine = AnalysisEngine(CacheManager(), AnalysisConfig())
        result = await engine.analyze_file(arguments["file_path"])
        
        return {
            "file_path": result.file_path,
            "total_score": result.teaching_value.total_score,
            "documentation_score": result.teaching_value.documentation_score,
            "complexity_score": result.teaching_value.complexity_score,
            "pattern_score": result.teaching_value.pattern_score,
            "structure_score": result.teaching_value.structure_score,
            "explanation": result.teaching_value.explanation
        }
    
    elif tool_name == "detect_patterns":
        from src.analysis import AnalysisEngine, AnalysisConfig
        from src.cache import CacheManager
        from src.tools.scan_codebase import scan_codebase
        
        # Scan first
        scan_result = await scan_codebase(arguments["codebase_path"])
        
        # Analyze
        cache_manager = CacheManager()
        cache_manager.set(f"scan:{scan_result.codebase_id}", scan_result, ttl=3600)
        
        engine = AnalysisEngine(cache_manager, AnalysisConfig())
        analysis = await engine.analyze_codebase(scan_result.codebase_id)
        
        # Group patterns by type
        pattern_summary = {}
        for pattern in analysis.global_patterns:
            if pattern.pattern_type not in pattern_summary:
                pattern_summary[pattern.pattern_type] = {
                    "count": 0,
                    "files": [],
                    "avg_confidence": 0.0
                }
            pattern_summary[pattern.pattern_type]["count"] += 1
            pattern_summary[pattern.pattern_type]["files"].append(pattern.file_path)
            pattern_summary[pattern.pattern_type]["avg_confidence"] += pattern.confidence
        
        # Calculate averages
        for pattern_type in pattern_summary:
            count = pattern_summary[pattern_type]["count"]
            pattern_summary[pattern_type]["avg_confidence"] /= count
            pattern_summary[pattern_type]["files"] = pattern_summary[pattern_type]["files"][:5]  # Limit to 5
        
        return {
            "codebase_id": scan_result.codebase_id,
            "total_patterns": len(analysis.global_patterns),
            "pattern_types": len(pattern_summary),
            "patterns": pattern_summary
        }
    
    elif tool_name == "analyze_dependencies":
        from src.analysis import AnalysisEngine, AnalysisConfig
        from src.cache import CacheManager
        from src.tools.scan_codebase import scan_codebase
        
        # Scan first
        scan_result = await scan_codebase(arguments["codebase_path"])
        
        # Analyze
        cache_manager = CacheManager()
        cache_manager.set(f"scan:{scan_result.codebase_id}", scan_result, ttl=3600)
        
        engine = AnalysisEngine(cache_manager, AnalysisConfig())
        analysis = await engine.analyze_codebase(scan_result.codebase_id)
        
        dep_graph = analysis.dependency_graph
        
        return {
            "codebase_id": scan_result.codebase_id,
            "total_files": len(dep_graph.nodes),
            "total_dependencies": len(dep_graph.edges),
            "circular_dependencies": len(dep_graph.circular_dependencies),
            "external_dependencies": dict(list(dep_graph.external_dependencies.items())[:10]),
            "most_imported_files": sorted(
                [(path, len(node.imported_by)) for path, node in dep_graph.nodes.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}


async def main():
    """Demonstrate MCP tool usage."""
    print("=" * 70)
    print("MCP Tools Usage Example")
    print("=" * 70)
    print("\nThis example simulates how AI assistants interact with the")
    print("Analysis Engine through MCP tools.")
    
    # Example 1: analyze_file tool
    print("\n" + "-" * 70)
    print("Example 1: analyze_file Tool")
    print("-" * 70)
    print("\nUse case: AI wants to understand a specific file")
    
    file_path = __file__
    result = await simulate_mcp_tool_call("analyze_file", {
        "file_path": file_path
    })
    
    print(f"\n✓ Response:")
    print(f"   Language: {result['language']}")
    print(f"   Functions: {result['functions_count']}")
    print(f"   Classes: {result['classes_count']}")
    print(f"   Teaching Value: {result['teaching_value']:.2f}")
    print(f"   Patterns: {', '.join(result['patterns'][:3])}")
    print(f"   Avg Complexity: {result['complexity']['average']:.2f}")
    print(f"   Documentation: {result['documentation_coverage']:.1%}")
    
    # Example 2: score_teaching_value tool
    print("\n" + "-" * 70)
    print("Example 2: score_teaching_value Tool")
    print("-" * 70)
    print("\nUse case: AI wants to find the best code to teach from")
    
    result = await simulate_mcp_tool_call("score_teaching_value", {
        "file_path": file_path
    })
    
    print(f"\n✓ Response:")
    print(f"   Total Score: {result['total_score']:.2f}/1.0")
    print(f"   Breakdown:")
    print(f"     Documentation: {result['documentation_score']:.2f}")
    print(f"     Complexity: {result['complexity_score']:.2f}")
    print(f"     Patterns: {result['pattern_score']:.2f}")
    print(f"     Structure: {result['structure_score']:.2f}")
    print(f"   Explanation: {result['explanation']}")
    
    # Example 3: detect_patterns tool
    print("\n" + "-" * 70)
    print("Example 3: detect_patterns Tool")
    print("-" * 70)
    print("\nUse case: AI wants to understand architectural patterns")
    
    codebase_path = str(Path(__file__).parent.parent / "src")
    result = await simulate_mcp_tool_call("detect_patterns", {
        "codebase_path": codebase_path
    })
    
    print(f"\n✓ Response:")
    print(f"   Total Patterns: {result['total_patterns']}")
    print(f"   Pattern Types: {result['pattern_types']}")
    print(f"\n   Top Patterns:")
    for pattern_type, data in list(result['patterns'].items())[:5]:
        print(f"     - {pattern_type}:")
        print(f"       Count: {data['count']}")
        print(f"       Avg Confidence: {data['avg_confidence']:.2f}")
        print(f"       Files: {len(data['files'])}")
    
    # Example 4: analyze_dependencies tool
    print("\n" + "-" * 70)
    print("Example 4: analyze_dependencies Tool")
    print("-" * 70)
    print("\nUse case: AI wants to understand code relationships")
    
    result = await simulate_mcp_tool_call("analyze_dependencies", {
        "codebase_path": codebase_path
    })
    
    print(f"\n✓ Response:")
    print(f"   Total Files: {result['total_files']}")
    print(f"   Dependencies: {result['total_dependencies']}")
    print(f"   Circular Dependencies: {result['circular_dependencies']}")
    
    print(f"\n   Top External Dependencies:")
    for dep, count in list(result['external_dependencies'].items())[:5]:
        print(f"     - {dep}: {count} imports")
    
    print(f"\n   Most Imported Files:")
    for file_path, import_count in result['most_imported_files']:
        print(f"     - {Path(file_path).name}: imported by {import_count} files")
    
    # Example 5: Typical AI workflow
    print("\n" + "-" * 70)
    print("Example 5: Typical AI Workflow")
    print("-" * 70)
    print("\nHow an AI assistant might use these tools:")
    
    print("\n  Step 1: Scan codebase to understand structure")
    print("  Step 2: Detect patterns to identify architecture")
    print("  Step 3: Analyze dependencies to understand relationships")
    print("  Step 4: Score teaching value to find best examples")
    print("  Step 5: Analyze specific files for detailed understanding")
    print("  Step 6: Generate course content based on findings")
    
    print("\n  Benefits:")
    print("    ✓ Fast: Cached results for repeated queries")
    print("    ✓ Accurate: AST-based analysis, not regex")
    print("    ✓ Comprehensive: Multi-language support")
    print("    ✓ Intelligent: Teaching value scoring")
    print("    ✓ Scalable: Parallel processing for large codebases")
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)
    print("\nTo use these tools with Claude Desktop:")
    print("  1. Configure MCP server in Claude Desktop settings")
    print("  2. Start the server: python -m src.server")
    print("  3. Ask Claude to analyze your codebase")
    print("  4. Claude will use these tools automatically")
    print("\nTo test with MCP Inspector:")
    print("  npx @modelcontextprotocol/inspector python -m src.server")


if __name__ == "__main__":
    asyncio.run(main())
