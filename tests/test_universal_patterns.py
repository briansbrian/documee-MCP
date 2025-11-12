"""
Unit tests for universal language pattern detectors.

Tests Java, Go, Rust, C++, C#, Ruby, and PHP pattern detectors.
Verifies pattern detection and confidence scoring across all languages.

Requirements: 3.5, 14.3
"""

import pytest
from dataclasses import dataclass, field
from typing import List, Optional

from src.analysis.universal_language_detectors import (
    JavaPatternDetector,
    GoPatternDetector,
    RustPatternDetector,
    CppPatternDetector,
    CSharpPatternDetector,
    RubyPatternDetector,
    PHPPatternDetector
)


# Mock SymbolInfo and related classes for testing
@dataclass
class ImportInfo:
    module: str
    imported_symbols: List[str] = field(default_factory=list)
    is_relative: bool = False
    import_type: str = "import"
    line_number: int = 1


@dataclass
class FunctionInfo:
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    start_line: int = 1
    end_line: int = 10
    complexity: int = 1
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    start_line: int = 1
    end_line: int = 20
    decorators: List[str] = field(default_factory=list)


@dataclass
class SymbolInfo:
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


# ============================================================================
# Java Pattern Detection Tests
# ============================================================================

class TestJavaPatternDetector:
    """Test Java-specific pattern detection."""
    
    def test_detect_annotations(self):
        """Test detection of Java annotations."""
        detector = JavaPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    @Override
    public String toString() {
        return name;
    }
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "User.java")
        
        annotation_patterns = [p for p in patterns if p.pattern_type == "java_annotations"]
        assert len(annotation_patterns) == 1
        
        pattern = annotation_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 5
    
    def test_detect_streams(self):
        """Test detection of Java Stream API usage."""
        detector = JavaPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """List<String> names = users.stream()
    .filter(user -> user.isActive())
    .map(User::getName)
    .collect(Collectors.toList());

int sum = numbers.parallelStream()
    .reduce(0, Integer::sum);
"""
        
        patterns = detector.detect(symbol_info, file_content, "Service.java")
        
        stream_patterns = [p for p in patterns if p.pattern_type == "java_streams"]
        assert len(stream_patterns) == 1
        
        pattern = stream_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] == 2
    
    def test_detect_generics(self):
        """Test detection of Java generics."""
        detector = JavaPatternDetector()
        
        symbol_info = SymbolInfo()
        
        # Need more than 5 generic uses to trigger detection
        file_content = """public class Box<T> {
    private T value;
    
    public void set(T value) {
        this.value = value;
    }
    
    public T get() {
        return value;
    }
}

List<String> strings = new ArrayList<>();
Map<String, Integer> map = new HashMap<>();
Set<Double> values = new HashSet<>();
Optional<User> user = Optional.empty();
"""
        
        patterns = detector.detect(symbol_info, file_content, "Box.java")
        
        generic_patterns = [p for p in patterns if p.pattern_type == "java_generics"]
        assert len(generic_patterns) == 1
        
        pattern = generic_patterns[0]
        assert pattern.confidence > 0.0
    
    def test_no_patterns_in_simple_java(self):
        """Test that simple Java code doesn't trigger false positives."""
        detector = JavaPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """public class Simple {
    public int add(int a, int b) {
        return a + b;
    }
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "Simple.java")
        
        # Should not detect significant patterns
        assert len(patterns) == 0 or all(p.confidence < 0.3 for p in patterns)


# ============================================================================
# Go Pattern Detection Tests
# ============================================================================

class TestGoPatternDetector:
    """Test Go-specific pattern detection."""
    
    def test_detect_goroutines(self):
        """Test detection of goroutines."""
        detector = GoPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """func main() {
    go processData()
    go func() {
        fmt.Println("Anonymous goroutine")
    }()
    
    for i := 0; i < 10; i++ {
        go worker(i)
    }
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "main.go")
        
        goroutine_patterns = [p for p in patterns if p.pattern_type == "go_goroutines"]
        assert len(goroutine_patterns) == 1
        
        pattern = goroutine_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 3
    
    def test_detect_channels(self):
        """Test detection of Go channels."""
        detector = GoPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """func worker(jobs <-chan int, results chan<- int) {
    for job := range jobs {
        results <- job * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)
    
    value := <-results
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "worker.go")
        
        channel_patterns = [p for p in patterns if p.pattern_type == "go_channels"]
        assert len(channel_patterns) == 1
        
        pattern = channel_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 3
    
    def test_detect_defer(self):
        """Test detection of defer statements."""
        detector = GoPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """func readFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close()
    
    defer fmt.Println("Done")
    
    // Read file
    return nil
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "file.go")
        
        defer_patterns = [p for p in patterns if p.pattern_type == "go_defer"]
        assert len(defer_patterns) == 1
        
        pattern = defer_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] == 2
    
    def test_no_patterns_in_simple_go(self):
        """Test that simple Go code doesn't trigger false positives."""
        detector = GoPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """func add(a, b int) int {
    return a + b
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "simple.go")
        
        # Should not detect any patterns
        assert len(patterns) == 0


# ============================================================================
# Rust Pattern Detection Tests
# ============================================================================

class TestRustPatternDetector:
    """Test Rust-specific pattern detection."""
    
    def test_detect_lifetimes(self):
        """Test detection of Rust lifetime annotations."""
        detector = RustPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

struct ImportantExcerpt<'a> {
    part: &'a str,
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "lifetime.rs")
        
        lifetime_patterns = [p for p in patterns if p.pattern_type == "rust_lifetimes"]
        assert len(lifetime_patterns) == 1
        
        pattern = lifetime_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 4
    
    def test_detect_traits(self):
        """Test detection of Rust traits."""
        detector = RustPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """trait Summary {
    fn summarize(&self) -> String;
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}", self.headline)
    }
}

impl Display for Point {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "traits.rs")
        
        trait_patterns = [p for p in patterns if p.pattern_type == "rust_traits"]
        assert len(trait_patterns) == 1
        
        pattern = trait_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 3
    
    def test_detect_macros(self):
        """Test detection of Rust macros."""
        detector = RustPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """fn main() {
    println!("Hello, world!");
    vec![1, 2, 3];
    assert_eq!(result, expected);
    format!("Value: {}", value);
    panic!("Something went wrong");
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "main.rs")
        
        macro_patterns = [p for p in patterns if p.pattern_type == "rust_macros"]
        assert len(macro_patterns) == 1
        
        pattern = macro_patterns[0]
        assert pattern.confidence > 0.0
    
    def test_no_patterns_in_simple_rust(self):
        """Test that simple Rust code doesn't trigger false positives."""
        detector = RustPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """fn add(a: i32, b: i32) -> i32 {
    a + b
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "simple.rs")
        
        # Should not detect significant patterns
        assert len(patterns) == 0 or all(p.confidence < 0.3 for p in patterns)


# ============================================================================
# C++ Pattern Detection Tests
# ============================================================================

class TestCppPatternDetector:
    """Test C++-specific pattern detection."""
    
    def test_detect_templates(self):
        """Test detection of C++ templates."""
        detector = CppPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """template<typename T>
class Stack {
    T* data;
public:
    void push(T value);
    T pop();
};

template<typename T, typename U>
auto add(T a, U b) -> decltype(a + b) {
    return a + b;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "stack.cpp")
        
        template_patterns = [p for p in patterns if p.pattern_type == "cpp_templates"]
        assert len(template_patterns) == 1
        
        pattern = template_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] == 2
    
    def test_detect_smart_pointers(self):
        """Test detection of C++ smart pointers."""
        detector = CppPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """#include <memory>

void example() {
    std::unique_ptr<int> ptr1 = std::make_unique<int>(42);
    std::shared_ptr<std::string> ptr2 = std::make_shared<std::string>("hello");
    std::weak_ptr<int> ptr3 = ptr2;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "pointers.cpp")
        
        smart_ptr_patterns = [p for p in patterns if p.pattern_type == "cpp_smart_pointers"]
        assert len(smart_ptr_patterns) == 1
        
        pattern = smart_ptr_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 3
    
    def test_detect_stl_containers(self):
        """Test detection of STL containers."""
        detector = CppPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """#include <vector>
#include <map>
#include <set>

void example() {
    std::vector<int> numbers;
    std::map<std::string, int> ages;
    std::set<double> values;
    std::unordered_map<int, std::string> lookup;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "containers.cpp")
        
        stl_patterns = [p for p in patterns if p.pattern_type == "cpp_stl_containers"]
        assert len(stl_patterns) == 1
        
        pattern = stl_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 4
    
    def test_no_patterns_in_simple_cpp(self):
        """Test that simple C++ code doesn't trigger false positives."""
        detector = CppPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """int add(int a, int b) {
    return a + b;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "simple.cpp")
        
        # Should not detect any patterns
        assert len(patterns) == 0


# ============================================================================
# C# Pattern Detection Tests
# ============================================================================

class TestCSharpPatternDetector:
    """Test C#-specific pattern detection."""
    
    def test_detect_linq(self):
        """Test detection of LINQ operations."""
        detector = CSharpPatternDetector()
        
        symbol_info = SymbolInfo()
        
        # Need more than 5 LINQ operations to trigger detection
        file_content = """var adults = people
    .Where(p => p.Age >= 18)
    .Select(p => p.Name)
    .OrderBy(name => name)
    .ToList();

var query = from user in users
            where user.IsActive
            select user.Name;

var filtered = items.Where(x => x.Active).Select(x => x.Name);
"""
        
        patterns = detector.detect(symbol_info, file_content, "Query.cs")
        
        linq_patterns = [p for p in patterns if p.pattern_type == "csharp_linq"]
        assert len(linq_patterns) == 1
        
        pattern = linq_patterns[0]
        assert pattern.confidence > 0.0
    
    def test_detect_async_await(self):
        """Test detection of C# async/await."""
        detector = CSharpPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """public async Task<string> FetchDataAsync() {
    var response = await httpClient.GetAsync(url);
    return await response.Content.ReadAsStringAsync();
}

public async void ProcessAsync() {
    await Task.Delay(1000);
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "Service.cs")
        
        async_patterns = [p for p in patterns if p.pattern_type == "csharp_async_await"]
        assert len(async_patterns) == 1
        
        pattern = async_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 4
    
    def test_detect_properties(self):
        """Test detection of C# auto-properties."""
        detector = CSharpPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """public class Person {
    public string Name { get; set; }
    public int Age { get; set; }
    public string Email { get; }
    public DateTime CreatedAt { get; private set; }
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "Person.cs")
        
        property_patterns = [p for p in patterns if p.pattern_type == "csharp_properties"]
        assert len(property_patterns) == 1
        
        pattern = property_patterns[0]
        assert pattern.confidence > 0.0
        # Detector counts { get; set; } and { get; } separately
        assert pattern.metadata["count"] >= 3
    
    def test_no_patterns_in_simple_csharp(self):
        """Test that simple C# code doesn't trigger false positives."""
        detector = CSharpPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """public int Add(int a, int b) {
    return a + b;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "Simple.cs")
        
        # Should not detect significant patterns
        assert len(patterns) == 0 or all(p.confidence < 0.3 for p in patterns)


# ============================================================================
# Ruby Pattern Detection Tests
# ============================================================================

class TestRubyPatternDetector:
    """Test Ruby-specific pattern detection."""
    
    def test_detect_blocks(self):
        """Test detection of Ruby blocks."""
        detector = RubyPatternDetector()
        
        symbol_info = SymbolInfo()
        
        # Need more than 5 blocks to trigger detection
        file_content = """numbers = [1, 2, 3, 4, 5]

numbers.each do |n|
  puts n * 2
end

result = numbers.map { |n| n ** 2 }

File.open('file.txt') do |file|
  content = file.read
end

items.select { |i| i.active }
data.reduce { |sum, n| sum + n }
collection.reject { |x| x.nil? }
"""
        
        patterns = detector.detect(symbol_info, file_content, "example.rb")
        
        block_patterns = [p for p in patterns if p.pattern_type == "ruby_blocks"]
        assert len(block_patterns) == 1
        
        pattern = block_patterns[0]
        assert pattern.confidence > 0.0
    
    def test_detect_symbols(self):
        """Test detection of Ruby symbols."""
        detector = RubyPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """options = {
  name: 'John',
  age: 30,
  city: 'New York'
}

user.update(status: :active)
redirect_to root_path, notice: :success
config[:database] = :postgresql
"""
        
        patterns = detector.detect(symbol_info, file_content, "config.rb")
        
        symbol_patterns = [p for p in patterns if p.pattern_type == "ruby_symbols"]
        assert len(symbol_patterns) == 1
        
        pattern = symbol_patterns[0]
        assert pattern.confidence > 0.0
        # Detector uses regex to find symbols
        assert pattern.metadata["count"] >= 2
    
    def test_detect_metaprogramming(self):
        """Test detection of Ruby metaprogramming."""
        detector = RubyPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """class MyClass
  define_method :dynamic_method do |arg|
    puts arg
  end
  
  def method_missing(method_name, *args)
    puts "Called #{method_name}"
  end
  
  class_eval do
    attr_accessor :value
  end
end
"""
        
        patterns = detector.detect(symbol_info, file_content, "meta.rb")
        
        meta_patterns = [p for p in patterns if p.pattern_type == "ruby_metaprogramming"]
        assert len(meta_patterns) == 1
        
        pattern = meta_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] == 3
    
    def test_no_patterns_in_simple_ruby(self):
        """Test that simple Ruby code doesn't trigger false positives."""
        detector = RubyPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """def add(a, b)
  a + b
end
"""
        
        patterns = detector.detect(symbol_info, file_content, "simple.rb")
        
        # Should not detect significant patterns
        assert len(patterns) == 0 or all(p.confidence < 0.3 for p in patterns)


# ============================================================================
# PHP Pattern Detection Tests
# ============================================================================

class TestPHPPatternDetector:
    """Test PHP-specific pattern detection."""
    
    def test_detect_namespaces(self):
        """Test detection of PHP namespaces."""
        detector = PHPPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """<?php
namespace App\\Controllers;

use App\\Models\\User;
use Illuminate\\Http\\Request;
use Illuminate\\Support\\Facades\\DB;

class UserController {
    // Controller code
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "UserController.php")
        
        namespace_patterns = [p for p in patterns if p.pattern_type == "php_namespaces"]
        assert len(namespace_patterns) == 1
        
        pattern = namespace_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 4
    
    def test_detect_traits(self):
        """Test detection of PHP traits."""
        detector = PHPPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """<?php
trait Timestampable {
    public function setCreatedAt() {
        $this->created_at = time();
    }
}

class User {
    use Timestampable;
    use SoftDeletes;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "User.php")
        
        trait_patterns = [p for p in patterns if p.pattern_type == "php_traits"]
        assert len(trait_patterns) == 1
        
        pattern = trait_patterns[0]
        assert pattern.confidence > 0.0
    
    def test_detect_closures(self):
        """Test detection of PHP closures."""
        detector = PHPPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """<?php
$greet = function($name) {
    return "Hello, $name";
};

$numbers = array_map(function($n) {
    return $n * 2;
}, [1, 2, 3]);

$add = fn($a, $b) => $a + $b;
"""
        
        patterns = detector.detect(symbol_info, file_content, "closures.php")
        
        closure_patterns = [p for p in patterns if p.pattern_type == "php_closures"]
        assert len(closure_patterns) == 1
        
        pattern = closure_patterns[0]
        assert pattern.confidence > 0.0
        assert pattern.metadata["count"] >= 3
    
    def test_no_patterns_in_simple_php(self):
        """Test that simple PHP code doesn't trigger false positives."""
        detector = PHPPatternDetector()
        
        symbol_info = SymbolInfo()
        
        file_content = """<?php
function add($a, $b) {
    return $a + $b;
}
"""
        
        patterns = detector.detect(symbol_info, file_content, "simple.php")
        
        # Should not detect significant patterns
        assert len(patterns) == 0 or all(p.confidence < 0.3 for p in patterns)


# ============================================================================
# Cross-Language Pattern Tests
# ============================================================================

class TestCrossLanguagePatterns:
    """Test pattern detection consistency across languages."""
    
    def test_all_detectors_return_non_zero_confidence(self):
        """Verify all detectors return non-zero confidence for matching patterns."""
        detectors_and_files = [
            (JavaPatternDetector(), "@Override\npublic void test() {}", "Test.java"),
            (GoPatternDetector(), "go func() { fmt.Println() }()", "main.go"),
            (RustPatternDetector(), "fn test<'a>(x: &'a str) {}", "test.rs"),
            (CppPatternDetector(), "template<typename T>\nclass Box {};", "box.cpp"),
            (CSharpPatternDetector(), "public string Name { get; set; }", "Model.cs"),
            (RubyPatternDetector(), "items.each do |item|\nend", "script.rb"),
            (PHPPatternDetector(), "namespace App;\nuse Model;", "Controller.php")
        ]
        
        symbol_info = SymbolInfo()
        
        for detector, content, filename in detectors_and_files:
            patterns = detector.detect(symbol_info, content, filename)
            if len(patterns) > 0:
                for pattern in patterns:
                    assert pattern.confidence > 0.0, \
                        f"{detector.__class__.__name__} returned zero confidence for {filename}"
    
    def test_pattern_confidence_scoring_consistency(self):
        """Test that confidence scoring is consistent across multiple runs."""
        detector = JavaPatternDetector()
        symbol_info = SymbolInfo()
        
        file_content = """@Entity
@Table(name = "users")
public class User {
    @Id
    private Long id;
}
"""
        
        # Run detection multiple times
        confidences = []
        for _ in range(5):
            patterns = detector.detect(symbol_info, file_content, "User.java")
            if patterns:
                confidences.append(patterns[0].confidence)
        
        # All confidence scores should be identical
        assert len(set(confidences)) == 1, "Confidence scores should be consistent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
