"""
Verification script for Analysis Engine setup.

This script verifies that all dependencies are installed correctly
and the basic configuration is working.
"""

import sys
from pathlib import Path

def verify_tree_sitter():
    """Verify tree-sitter installation."""
    try:
        from tree_sitter import Language, Parser
        from tree_sitter_languages import get_parser, get_language
        
        # Test loading Python parser
        parser = get_parser('python')
        language = get_language('python')
        
        print("✓ tree-sitter installed correctly")
        print(f"  - Parser type: {type(parser)}")
        print(f"  - Language type: {type(language)}")
        
        # Test parsing a simple Python code
        code = b"def hello():\n    print('Hello, world!')"
        tree = parser.parse(code)
        root = tree.root_node
        
        print(f"  - Successfully parsed sample code")
        print(f"  - Root node type: {root.type}")
        
        return True
    except Exception as e:
        print(f"✗ tree-sitter verification failed: {e}")
        return False

def verify_nbformat():
    """Verify nbformat installation."""
    try:
        import nbformat
        print("✓ nbformat installed correctly")
        print(f"  - Version: {nbformat.__version__}")
        return True
    except Exception as e:
        print(f"✗ nbformat verification failed: {e}")
        return False

def verify_config():
    """Verify configuration module."""
    try:
        from .config import AnalysisConfig
        
        # Test creating default config
        config = AnalysisConfig()
        print("✓ AnalysisConfig loaded correctly")
        print(f"  - Supported languages: {len(config.supported_languages)}")
        print(f"  - Max complexity threshold: {config.max_complexity_threshold}")
        
        # Test loading from dict
        config_dict = {
            'analysis': {
                'max_file_size_mb': 20,
                'max_complexity_threshold': 15
            }
        }
        config2 = AnalysisConfig.from_dict(config_dict)
        print(f"  - Config from dict: max_file_size_mb={config2.max_file_size_mb}")
        
        return True
    except Exception as e:
        print(f"✗ AnalysisConfig verification failed: {e}")
        return False

def verify_engine():
    """Verify engine module."""
    try:
        from .engine import AnalysisEngine
        
        print("✓ AnalysisEngine loaded correctly")
        print(f"  - Module: {AnalysisEngine.__module__}")
        
        return True
    except Exception as e:
        print(f"✗ AnalysisEngine verification failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Analysis Engine Setup Verification")
    print("=" * 60)
    print()
    
    results = []
    
    print("1. Verifying tree-sitter installation...")
    results.append(verify_tree_sitter())
    print()
    
    print("2. Verifying nbformat installation...")
    results.append(verify_nbformat())
    print()
    
    print("3. Verifying AnalysisConfig...")
    results.append(verify_config())
    print()
    
    print("4. Verifying AnalysisEngine...")
    results.append(verify_engine())
    print()
    
    print("=" * 60)
    if all(results):
        print("✓ All verification checks passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some verification checks failed")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
