# Data Models and Schemas

## Overview

The MCP server uses Python dataclasses for all tool responses and internal data structures. All models support JSON serialization via the `to_dict()` method, enabling seamless communication between the MCP server and AI clients.

**Location:** `src/models/schemas.py`

## Core Data Models

### ScanResult

Result from scanning a codebase structure using the `scan_codebase` tool.

**Attributes:**
- `codebase_id` (str): Unique SHA-256 hash identifier (16 chars) for the codebase
- `structure` (Dict[str, Any]): Contains `total_files`, `total_directories`, `total_size_mb`, `languages` dict, and `file_types` dict
- `summary` (Dict[str, Any]): Contains `primary_language`, `project_type`, `has_tests`, and `size_category`
- `scan_time_ms` (float): Actual execution time in milliseconds
- `from_cache` (bool): Whether the result was retrieved from cache (default: False)

**Usage:**
```python
scan_result = ScanResult(
    codebase_id="a1b2c3d4e5f6g7h8",
    structure={
        "total_files": 150,
        "total_directories": 25,
        "total_size_mb": 2.5,
        "languages": {"JavaScript": 80, "TypeScript": 50, "CSS": 20},
        "file_types": {".js": 80, ".ts": 50, ".css": 20}
    },
    summary={
        "primary_language": "JavaScript",
        "project_type": "web-application",
        "has_tests": True,
        "size_category": "small"
    },
    scan_time_ms=1250.5,
    from_cache=False
)
```

---

### Framework

Detected framework or library in a codebase.

**Attributes:**
- `name` (str): Framework name (e.g., "React", "Django", "Express")
- `version` (str): Version string from dependency file or "detected"
- `confidence` (float): Confidence score from 0.0 to 1.0 (0.99 for package.json deps)
- `evidence` (List[str]): List of evidence strings (e.g., "package.json dependency")

**Usage:**
```python
framework = Framework(
    name="React",
    version="18.2.0",
    confidence=0.99,
    evidence=["package.json dependency"]
)
```

---

### FrameworkDetectionResult

Result from detecting frameworks using the `detect_frameworks` tool.

**Attributes:**
- `frameworks` (List[Framework]): List of detected Framework objects
- `total_detected` (int): Total number of frameworks detected
- `confidence_threshold` (float): Minimum confidence score used for filtering
- `from_cache` (bool): Whether the result was retrieved from cache (default: False)

**Usage:**
```python
detection_result = FrameworkDetectionResult(
    frameworks=[
        Framework("React", "18.2.0", 0.99, ["package.json dependency"]),
        Framework("Next.js", "14.0.0", 0.99, ["package.json dependency"])
    ],
    total_detected=2,
    confidence_threshold=0.7,
    from_cache=False
)
```

---

### Feature

Discovered feature in a codebase (routes, components, API endpoints, etc.).

**Attributes:**
- `id` (str): Unique SHA-256 hash identifier (16 chars) for the feature
- `name` (str): Feature name (directory name without trailing slash)
- `category` (str): Feature category (routes, components, api, utils, hooks)
- `path` (str): Absolute path to the feature directory
- `priority` (str): Priority level ("high" for routes/api, "medium" for others)

**Usage:**
```python
feature = Feature(
    id="f1e2d3c4b5a69788",
    name="components",
    category="components",
    path="/path/to/project/src/components",
    priority="medium"
)
```

---

### FeatureDiscoveryResult

Result from discovering features using the `discover_features` tool.

**Attributes:**
- `features` (List[Feature]): List of discovered Feature objects
- `total_features` (int): Total number of features discovered
- `categories` (List[str]): List of unique categories found
- `from_cache` (bool): Whether the result was retrieved from cache (default: False)

**Usage:**
```python
discovery_result = FeatureDiscoveryResult(
    features=[
        Feature("abc123", "routes", "routes", "/path/routes", "high"),
        Feature("def456", "components", "components", "/path/components", "medium"),
        Feature("ghi789", "api", "api", "/path/api", "high")
    ],
    total_features=3,
    categories=["routes", "components", "api"],
    from_cache=False
)
```

## JSON Serialization

All dataclasses implement a `to_dict()` method for JSON serialization:

```python
# Convert to dictionary
result_dict = scan_result.to_dict()

# Serialize to JSON
import json
json_string = json.dumps(result_dict)
```

The `to_dict()` method uses Python's `dataclasses.asdict()` function and handles nested objects properly:
- `FrameworkDetectionResult.to_dict()` ensures all Framework objects are serialized
- `FeatureDiscoveryResult.to_dict()` ensures all Feature objects are serialized

## Design Principles

1. **Immutability**: Dataclasses are designed to be immutable after creation
2. **Type Safety**: All fields have explicit type hints for IDE support and validation
3. **JSON-First**: All models serialize cleanly to JSON for MCP protocol
4. **Evidence-Based**: Framework detection includes evidence arrays to prevent hallucination
5. **Performance Tracking**: Results include timing and cache status for monitoring

## Integration with MCP Tools

These models are used by the three core discovery tools:

- **scan_codebase** → Returns `ScanResult`
- **detect_frameworks** → Returns `FrameworkDetectionResult`
- **discover_features** → Returns `FeatureDiscoveryResult`

The MCP server automatically serializes these models to JSON when returning tool results to AI clients.

## Future Extensions

Additional models planned for future specs:

- `FileContent` - For parallel file reading (Spec 2)
- `CodeAnalysis` - For code quality analysis (Spec 2)
- `TeachingScore` - For teaching value assessment (Spec 2)
- `CourseOutline` - For course generation (Spec 3)
- `LessonPlan` - For lesson planning (Spec 3)

---

**Last Updated:** November 12, 2025
