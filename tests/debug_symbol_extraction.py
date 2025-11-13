"""Debug script to test symbol extraction."""

import asyncio
from src.analysis.ast_parser import ASTParserManager
from src.analysis.symbol_extractor import SymbolExtractor
from src.analysis.config import AnalysisConfig

async def test_symbol_extraction():
    """Test symbol extraction on a simple Python file."""
    
    # Initialize components
    config = AnalysisConfig()
    parser = ASTParserManager(config)
    extractor = SymbolExtractor()
    
    # Test file
    test_file = "src/server.py"
    
    print(f"Testing symbol extraction on: {test_file}")
    print("=" * 80)
    
    # Parse file
    print("\n1. Parsing file...")
    parse_result = parser.parse_file(test_file)
    print(f"   Language: {parse_result.language}")
    print(f"   Has errors: {parse_result.has_errors}")
    print(f"   Root node type: {parse_result.root_node.type}")
    print(f"   Root node children: {len(parse_result.root_node.children)}")
    
    # Show first few children
    print(f"\n   First 10 child node types:")
    for i, child in enumerate(parse_result.root_node.children[:10]):
        print(f"     {i}: {child.type}")
    
    # Extract symbols
    print("\n2. Extracting symbols...")
    symbol_info = extractor.extract_symbols(parse_result)
    
    print(f"   Functions found: {len(symbol_info.functions)}")
    print(f"   Classes found: {len(symbol_info.classes)}")
    print(f"   Imports found: {len(symbol_info.imports)}")
    
    # Show details
    if symbol_info.functions:
        print(f"\n   First 5 functions:")
        for func in symbol_info.functions[:5]:
            print(f"     - {func.name} (line {func.start_line}-{func.end_line}, complexity: {func.complexity})")
    else:
        print(f"\n   ⚠️  NO FUNCTIONS FOUND!")
        print(f"   Debugging: Let's check what nodes we're looking for...")
        
        # Count function_definition nodes
        def count_nodes_by_type(node, node_type):
            count = 0
            if node.type == node_type:
                count = 1
            for child in node.children:
                count += count_nodes_by_type(child, node_type)
            return count
        
        func_defs = count_nodes_by_type(parse_result.root_node, 'function_definition')
        print(f"   Total 'function_definition' nodes in AST: {func_defs}")
        
        # Show all unique node types
        def collect_node_types(node, types_set):
            types_set.add(node.type)
            for child in node.children:
                collect_node_types(child, types_set)
        
        all_types = set()
        collect_node_types(parse_result.root_node, all_types)
        print(f"\n   All node types in AST ({len(all_types)} unique):")
        for node_type in sorted(all_types):
            print(f"     - {node_type}")
    
    if symbol_info.classes:
        print(f"\n   First 5 classes:")
        for cls in symbol_info.classes[:5]:
            print(f"     - {cls.name} (line {cls.start_line}-{cls.end_line}, {len(cls.methods)} methods)")
    else:
        print(f"\n   ⚠️  NO CLASSES FOUND!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_symbol_extraction())
