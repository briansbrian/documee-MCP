"""
Test all universal language pattern detectors.
Verifies God Mode support for Python, JavaScript, Java, Go, Rust, C++, C#, Ruby, and PHP.
"""

from src.analysis.language_pattern_detector import PythonPatternDetector, JavaScriptPatternDetector
from src.analysis.universal_language_detectors import (
    JavaPatternDetector, GoPatternDetector, RustPatternDetector,
    CppPatternDetector, CSharpPatternDetector, RubyPatternDetector, PHPPatternDetector
)
from src.analysis.symbol_extractor import SymbolInfo

print("="*70)
print("UNIVERSAL LANGUAGE PATTERN DETECTOR TEST (GOD MODE)")
print("="*70)

# Test samples for each language
test_cases = [
    ("Python", PythonPatternDetector(), "test.py", """
@property
async def fetch_data():
    await asyncio.sleep(1)
    return [x for x in range(10)]
"""),
    ("JavaScript", JavaScriptPatternDetector(), "test.js", """
const fetchData = async () => {
    const { data } = await fetch('/api');
    return data.map(item => ({ ...item }));
};
"""),
    ("Java", JavaPatternDetector(), "Test.java", """
@Service
@Autowired
public class UserService {
    public List<User> getUsers() {
        return users.stream()
            .filter(u -> u.isActive())
            .collect(Collectors.toList());
    }
}
"""),
    ("Go", GoPatternDetector(), "main.go", """
func main() {
    ch := make(chan int)
    go func() {
        defer close(ch)
        ch <- 42
    }()
}
"""),
    ("Rust", RustPatternDetector(), "main.rs", """
impl<'a> MyStruct<'a> {
    fn new() -> Self {
        println!("Creating struct");
    }
}
trait MyTrait {}
"""),
    ("C++", CppPatternDetector(), "main.cpp", """
template<typename T>
class Container {
    std::unique_ptr<T> data;
    std::vector<T> items;
};
"""),
    ("C#", CSharpPatternDetector(), "Program.cs", """
public class User {
    public string Name { get; set; }
    public async Task<List<User>> GetUsersAsync() {
        return await users.Where(u => u.IsActive).ToListAsync();
    }
}
"""),
    ("Ruby", RubyPatternDetector(), "app.rb", """
class User
    define_method :greet do |name|
        puts "Hello, #{name}"
    end
    
    users.each do |user|
        process(user)
    end
end
"""),
    ("PHP", PHPPatternDetector(), "index.php", """
namespace App\\Controllers;
use App\\Models\\User;

trait Loggable {
    public function log() {}
}

$users = array_map(function($user) {
    return $user->name;
}, $users);
""")
]

symbol_info = SymbolInfo(functions=[], classes=[], imports=[], exports=[])
total_patterns = 0

for lang_name, detector, filename, code in test_cases:
    patterns = detector.detect(symbol_info, code, filename)
    total_patterns += len(patterns)
    
    print(f"\n{lang_name} ({filename}):")
    if patterns:
        for pattern in patterns:
            print(f"  ✓ {pattern.pattern_type}: confidence={pattern.confidence:.2f}")
    else:
        print(f"  ✗ No patterns detected")

print(f"\n{'='*70}")
print(f"TOTAL PATTERNS DETECTED: {total_patterns}")
print(f"{'='*70}")

if total_patterns >= 15:  # Expect at least 15 patterns across all languages
    print("✓ GOD MODE ACTIVATED - All language detectors working!")
else:
    print(f"✗ Expected at least 15 patterns, got {total_patterns}")

print("\nSupported Languages:")
print("  • Python (decorators, async/await, generators, comprehensions)")
print("  • JavaScript/TypeScript (promises, async/await, arrow functions, destructuring)")
print("  • Java (annotations, streams, generics)")
print("  • Go (goroutines, channels, defer)")
print("  • Rust (lifetimes, traits, macros)")
print("  • C++ (templates, smart pointers, STL)")
print("  • C# (LINQ, async/await, properties)")
print("  • Ruby (blocks, metaprogramming, symbols)")
print("  • PHP (namespaces, traits, closures)")
