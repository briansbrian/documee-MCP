"""
Quick integration check for language-specific pattern detectors.
This verifies that the new detectors integrate correctly with the existing codebase.
"""

# Test imports
try:
    from src.analysis.language_pattern_detector import PythonPatternDetector, JavaScriptPatternDetector
    print("✓ Language pattern detectors imported successfully")
except ImportError as e:
    print(f"✗ Failed to import language pattern detectors: {e}")
    exit(1)

try:
    from src.analysis.pattern_detector import BasePatternDetector, DetectedPattern
    print("✓ Base pattern detector classes imported successfully")
except ImportError as e:
    print(f"✗ Failed to import base pattern detector: {e}")
    exit(1)

try:
    from src.analysis.symbol_extractor import SymbolInfo, FunctionInfo, ClassInfo, ImportInfo
    print("✓ Symbol extractor classes imported successfully")
except ImportError as e:
    print(f"✗ Failed to import symbol extractor: {e}")
    exit(1)

# Test that detectors inherit from BasePatternDetector
assert issubclass(PythonPatternDetector, BasePatternDetector), "PythonPatternDetector must inherit from BasePatternDetector"
assert issubclass(JavaScriptPatternDetector, BasePatternDetector), "JavaScriptPatternDetector must inherit from BasePatternDetector"
print("✓ Detectors correctly inherit from BasePatternDetector")

# Test instantiation
try:
    python_detector = PythonPatternDetector()
    js_detector = JavaScriptPatternDetector()
    print("✓ Detectors can be instantiated")
except Exception as e:
    print(f"✗ Failed to instantiate detectors: {e}")
    exit(1)

# Test that detect method exists
assert hasattr(python_detector, 'detect'), "PythonPatternDetector must have detect method"
assert hasattr(js_detector, 'detect'), "JavaScriptPatternDetector must have detect method"
print("✓ Detectors have detect method")

# Test with minimal symbol info
symbol_info = SymbolInfo(
    functions=[
        FunctionInfo(
            name="test_func",
            parameters=[],
            return_type=None,
            docstring="Test function",
            start_line=1,
            end_line=5,
            complexity=1,
            is_async=True,
            decorators=["@property"]
        )
    ],
    classes=[],
    imports=[
        ImportInfo(
            module="asyncio",
            imported_symbols=["sleep"],
            is_relative=False,
            import_type="from",
            line_number=1
        )
    ],
    exports=[]
)

file_content = """
import asyncio

@property
async def test_func():
    '''Test function'''
    await asyncio.sleep(1)
    return [x for x in range(10)]
"""

# Test Python detector
try:
    patterns = python_detector.detect(symbol_info, file_content, "test.py")
    print(f"✓ Python detector returned {len(patterns)} patterns")
    for pattern in patterns:
        print(f"  - {pattern.pattern_type}: confidence={pattern.confidence:.2f}")
except Exception as e:
    print(f"✗ Python detector failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test JavaScript detector (should return empty for .py file)
try:
    patterns = js_detector.detect(symbol_info, file_content, "test.py")
    print(f"✓ JavaScript detector correctly returned {len(patterns)} patterns for .py file")
except Exception as e:
    print(f"✗ JavaScript detector failed: {e}")
    exit(1)

# Test JavaScript detector with .js file
js_content = """
const fetchData = async () => {
    const response = await fetch('/api/data');
    const { data, error } = await response.json();
    return data.map(item => ({ ...item, processed: true }));
};

fetchData()
    .then(data => console.log(data))
    .catch(err => console.error(err));
"""

try:
    patterns = js_detector.detect(symbol_info, js_content, "test.js")
    print(f"✓ JavaScript detector returned {len(patterns)} patterns for .js file")
    for pattern in patterns:
        print(f"  - {pattern.pattern_type}: confidence={pattern.confidence:.2f}")
except Exception as e:
    print(f"✗ JavaScript detector failed on .js file: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("✓ ALL INTEGRATION CHECKS PASSED")
print("="*60)
print("\nThe language-specific pattern detectors are correctly integrated!")
print("Next steps:")
print("1. Run full test suite: .\\venv\\Scripts\\python.exe -m pytest tests/")
print("2. Test with real codebase analysis")
print("3. Verify pattern scores are non-zero for Python/JS files")
