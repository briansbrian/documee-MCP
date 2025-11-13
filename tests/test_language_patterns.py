"""
Quick test for language-specific pattern detectors.
"""

# Mock the dependencies
class MockSymbolInfo:
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []

class MockFunction:
    def __init__(self, name, decorators=None, is_async=False, start_line=1):
        self.name = name
        self.decorators = decorators or []
        self.is_async = is_async
        self.start_line = start_line

class MockClass:
    def __init__(self, name, methods=None):
        self.name = name
        self.methods = methods or []

class MockImport:
    def __init__(self, module, line_number=1):
        self.module = module
        self.line_number = line_number

# Test Python patterns
print("=" * 80)
print("Testing Python Pattern Detector")
print("=" * 80)

# Create test file content
python_code = """
import asyncio
from typing import List

@property
def get_value(self):
    return self._value

@staticmethod
def helper():
    pass

async def fetch_data():
    result = await some_api_call()
    return result

def generator_func():
    for i in range(10):
        yield i

def process_data():
    with open('file.txt') as f:
        data = f.read()
    
    # List comprehension
    numbers = [x * 2 for x in range(10)]
    
    # Dict comprehension
    squares = {x: x**2 for x in range(5)}
    
    return numbers, squares
"""

# Create mock symbol info
symbol_info = MockSymbolInfo()
symbol_info.functions = [
    MockFunction("get_value", decorators=["property"], start_line=5),
    MockFunction("helper", decorators=["staticmethod"], start_line=9),
    MockFunction("fetch_data", is_async=True, start_line=13),
    MockFunction("generator_func", start_line=17),
    MockFunction("process_data", start_line=21),
]
symbol_info.impor