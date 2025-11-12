"""
Universal Language Pattern Detectors for all major programming languages.

Provides pattern detectors for Java, Go, Rust, C++, C#, Ruby, and PHP.
"""

import logging
import re
from typing import List, Optional

from .pattern_detector import BasePatternDetector, DetectedPattern
from .symbol_extractor import SymbolInfo

logger = logging.getLogger(__name__)


class JavaPatternDetector(BasePatternDetector):
    """Detects Java patterns: annotations, streams, generics, exceptions."""
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        if not file_path.endswith('.java'):
            return []
        
        patterns = []
        lines = file_content.split('\n')
        
        # Annotations
        annotation_count = sum(1 for line in lines if line.strip().startswith('@') and '//' not in line)
        if annotation_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="java_annotations",
                file_path=file_path,
                confidence=min(1.0, annotation_count * 0.15),
                evidence=[f"Annotations: {annotation_count}"],
                line_numbers=[],
                metadata={"count": annotation_count}
            ))
        
        # Streams
        stream_count = file_content.count('.stream(') + file_content.count('.parallelStream(')
        if stream_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="java_streams",
                file_path=file_path,
                confidence=min(1.0, stream_count * 0.2),
                evidence=[f"Stream operations: {stream_count}"],
                line_numbers=[],
                metadata={"count": stream_count}
            ))
        
        # Generics
        generic_count = file_content.count('<') - file_content.count('<!--')
        if generic_count > 5:
            patterns.append(DetectedPattern(
                pattern_type="java_generics",
                file_path=file_path,
                confidence=min(1.0, generic_count * 0.05),
                evidence=[f"Generic types usage"],
                line_numbers=[],
                metadata={"count": generic_count}
            ))
        
        return patterns


class GoPatternDetector(BasePatternDetector):
    """Detects Go patterns: goroutines, channels, defer, interfaces."""
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        if not file_path.endswith('.go'):
            return []
        
        patterns = []
        
        # Goroutines
        goroutine_count = file_content.count('go ')
        if goroutine_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="go_goroutines",
                file_path=file_path,
                confidence=min(1.0, goroutine_count * 0.25),
                evidence=[f"Goroutines: {goroutine_count}"],
                line_numbers=[],
                metadata={"count": goroutine_count}
            ))
        
        # Channels
        channel_count = file_content.count('chan ') + file_content.count('<-')
        if channel_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="go_channels",
                file_path=file_path,
                confidence=min(1.0, channel_count * 0.2),
                evidence=[f"Channel operations: {channel_count}"],
                line_numbers=[],
                metadata={"count": channel_count}
            ))
        
        # Defer
        defer_count = file_content.count('defer ')
        if defer_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="go_defer",
                file_path=file_path,
                confidence=min(1.0, defer_count * 0.2),
                evidence=[f"Defer statements: {defer_count}"],
                line_numbers=[],
                metadata={"count": defer_count}
            ))
        
        return patterns


class RustPatternDetector(BasePatternDetector):
    """Detects Rust patterns: ownership, lifetimes, traits, macros."""
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        if not file_path.endswith('.rs'):
            return []
        
        patterns = []
        
        # Lifetimes
        lifetime_count = len(re.findall(r"'[a-z]+", file_content))
        if lifetime_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="rust_lifetimes",
                file_path=file_path,
                confidence=min(1.0, lifetime_count * 0.2),
                evidence=[f"Lifetime annotations: {lifetime_count}"],
                line_numbers=[],
                metadata={"count": lifetime_count}
            ))
        
        # Traits
        trait_count = file_content.count('impl ') + file_content.count('trait ')
        if trait_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="rust_traits",
                file_path=file_path,
                confidence=min(1.0, trait_count * 0.2),
                evidence=[f"Trait implementations: {trait_count}"],
                line_numbers=[],
                metadata={"count": trait_count}
            ))
        
        # Macros
        macro_count = file_content.count('!') - file_content.count('!=')
        if macro_count > 5:
            patterns.append(DetectedPattern(
                pattern_type="rust_macros",
                file_path=file_path,
                confidence=min(1.0, macro_count * 0.1),
                evidence=[f"Macro usage"],
                line_numbers=[],
                metadata={"count": macro_count}
            ))
        
        return patterns



class CppPatternDetector(BasePatternDetector):
    """Detects C++ patterns: templates, RAII, smart pointers, STL."""
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        if not (file_path.endswith('.cpp') or file_path.endswith('.cc') or 
                file_path.endswith('.cxx') or file_path.endswith('.hpp') or file_path.endswith('.h')):
            return []
        
        patterns = []
        
        # Templates
        template_count = file_content.count('template<')
        if template_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="cpp_templates",
                file_path=file_path,
                confidence=min(1.0, template_count * 0.2),
                evidence=[f"Template definitions: {template_count}"],
                line_numbers=[],
                metadata={"count": template_count}
            ))
        
        # Smart pointers
        smart_ptr_count = (file_content.count('unique_ptr') + file_content.count('shared_ptr') + 
                          file_content.count('weak_ptr'))
        if smart_ptr_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="cpp_smart_pointers",
                file_path=file_path,
                confidence=min(1.0, smart_ptr_count * 0.2),
                evidence=[f"Smart pointer usage: {smart_ptr_count}"],
                line_numbers=[],
                metadata={"count": smart_ptr_count}
            ))
        
        # STL containers
        stl_count = (file_content.count('std::vector') + file_content.count('std::map') + 
                    file_content.count('std::set') + file_content.count('std::unordered'))
        if stl_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="cpp_stl_containers",
                file_path=file_path,
                confidence=min(1.0, stl_count * 0.15),
                evidence=[f"STL container usage: {stl_count}"],
                line_numbers=[],
                metadata={"count": stl_count}
            ))
        
        return patterns



class CSharpPatternDetector(BasePatternDetector):
    """Detects C# patterns: LINQ, async/await, properties, attributes."""
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        if not file_path.endswith('.cs'):
            return []
        
        patterns = []
        
        # LINQ
        linq_count = (file_content.count('.Select(') + file_content.count('.Where(') + 
                     file_content.count('.OrderBy(') + file_content.count('from ') + file_content.count(' in '))
        if linq_count > 5:
            patterns.append(DetectedPattern(
                pattern_type="csharp_linq",
                file_path=file_path,
                confidence=min(1.0, linq_count * 0.1),
                evidence=[f"LINQ operations"],
                line_numbers=[],
                metadata={"count": linq_count}
            ))
        
        # Async/await
        async_count = file_content.count('async ') + file_content.count('await ')
        if async_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="csharp_async_await",
                file_path=file_path,
                confidence=min(1.0, async_count * 0.15),
                evidence=[f"Async/await usage: {async_count}"],
                line_numbers=[],
                metadata={"count": async_count}
            ))
        
        # Properties
        property_count = file_content.count('{ get; set; }') + file_content.count('{ get; }')
        if property_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="csharp_properties",
                file_path=file_path,
                confidence=min(1.0, property_count * 0.1),
                evidence=[f"Auto-properties: {property_count}"],
                line_numbers=[],
                metadata={"count": property_count}
            ))
        
        return patterns



class RubyPatternDetector(BasePatternDetector):
    """Detects Ruby patterns: blocks, metaprogramming, symbols, mixins."""
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        if not file_path.endswith('.rb'):
            return []
        
        patterns = []
        
        # Blocks
        block_count = file_content.count(' do ') + file_content.count('{')
        if block_count > 5:
            patterns.append(DetectedPattern(
                pattern_type="ruby_blocks",
                file_path=file_path,
                confidence=min(1.0, block_count * 0.05),
                evidence=[f"Block usage"],
                line_numbers=[],
                metadata={"count": block_count}
            ))
        
        # Symbols
        symbol_count = len(re.findall(r':[a-zA-Z_]\w*', file_content))
        if symbol_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="ruby_symbols",
                file_path=file_path,
                confidence=min(1.0, symbol_count * 0.1),
                evidence=[f"Symbol usage: {symbol_count}"],
                line_numbers=[],
                metadata={"count": symbol_count}
            ))
        
        # Metaprogramming
        meta_count = (file_content.count('define_method') + file_content.count('method_missing') + 
                     file_content.count('class_eval') + file_content.count('instance_eval'))
        if meta_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="ruby_metaprogramming",
                file_path=file_path,
                confidence=min(1.0, meta_count * 0.3),
                evidence=[f"Metaprogramming: {meta_count}"],
                line_numbers=[],
                metadata={"count": meta_count}
            ))
        
        return patterns



class PHPPatternDetector(BasePatternDetector):
    """Detects PHP patterns: namespaces, traits, closures, type hints."""
    
    def detect(self, symbol_info: SymbolInfo, file_content: str, file_path: str) -> List[DetectedPattern]:
        if not file_path.endswith('.php'):
            return []
        
        patterns = []
        
        # Namespaces
        namespace_count = file_content.count('namespace ') + file_content.count('use ')
        if namespace_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="php_namespaces",
                file_path=file_path,
                confidence=min(1.0, namespace_count * 0.15),
                evidence=[f"Namespace usage: {namespace_count}"],
                line_numbers=[],
                metadata={"count": namespace_count}
            ))
        
        # Traits
        trait_count = file_content.count('trait ') + file_content.count('use ')
        if trait_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="php_traits",
                file_path=file_path,
                confidence=min(1.0, trait_count * 0.2),
                evidence=[f"Trait usage"],
                line_numbers=[],
                metadata={"count": trait_count}
            ))
        
        # Closures
        closure_count = file_content.count('function(') + file_content.count('fn(')
        if closure_count > 0:
            patterns.append(DetectedPattern(
                pattern_type="php_closures",
                file_path=file_path,
                confidence=min(1.0, closure_count * 0.15),
                evidence=[f"Closure usage: {closure_count}"],
                line_numbers=[],
                metadata={"count": closure_count}
            ))
        
        return patterns
