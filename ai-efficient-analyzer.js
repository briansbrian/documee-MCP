#!/usr/bin/env node

/**
 * AI-Optimized Codebase Analyzer
 * 
 * This tool is designed to make AI analysis MORE efficient by:
 * 1. Providing structured JSON output (not human-readable text)
 * 2. Prioritizing files intelligently
 * 3. Extracting actionable insights
 * 4. Minimizing redundant analysis
 * 
 * Usage: node ai-efficient-analyzer.js /path/to/codebase
 */

const fs = require('fs');
const path = require('path');

// Configuration
const MAX_FILE_SIZE = 1024 * 1024; // 1MB
const IGNORE_PATTERNS = [
  'node_modules', '.git', 'dist', 'build', '.next', '.nuxt',
  'coverage', '__pycache__', 'vendor', 'target', 'out'
];

/**
 * Main analysis function
 */
async function analyzeCodebase(rootPath) {
  console.error('Starting analysis...'); // stderr for progress, stdout for JSON
  
  const startTime = Date.now();
  
  // Step 1: Scan directory structure
  const structure = scanDirectory(rootPath);
  console.error(`Found ${structure.files.length} files`);
  
  // Step 2: Prioritize files
  const prioritized = prioritizeFiles(structure.files);
  console.error(`Prioritized: ${prioritized.critical.length} critical, ${prioritized.high.length} high priority`);
  
  // Step 3: Read and analyze critical files
  const criticalContent = readFiles(prioritized.critical);
  const highContent = readFiles(prioritized.high.slice(0, 20)); // Limit to 20
  
  // Step 4: Detect patterns
  const patterns = detectPatterns(structure, criticalContent, highContent);
  console.error(`Detected: ${patterns.frameworks.join(', ')}`);
  
  // Step 5: Build dependency graph
  const dependencies = buildDependencyGraph(criticalContent);
  
  // Step 6: Extract teachable code
  const teachable = extractTeachableCode(highContent, patterns);
  console.error(`Found ${teachable.length} teachable snippets`);
  
  // Step 7: Generate recommendations
  const recommendations = generateRecommendations(patterns, teachable, dependencies);
  
  const endTime = Date.now();
  console.error(`Analysis complete in ${(endTime - startTime) / 1000}s`);
  
  // Output structured JSON to stdout
  return {
    metadata: {
      path: rootPath,
      analyzedAt: new Date().toISOString(),
      duration: endTime - startTime,
      filesAnalyzed: criticalContent.length + highContent.length
    },
    structure: {
      totalFiles: structure.files.length,
      totalDirectories: structure.directories.length,
      languages: structure.languages
    },
    patterns,
    dependencies,
    teachable,
    recommendations
  };
}

/**
 * Scan directory structure
 */
function scanDirectory(dir, depth = 0) {
  const result = {
    files: [],
    directories: [],
    languages: {}
  };
  
  if (depth > 10) return result; // Prevent infinite recursion
  
  try {
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
      // Skip ignored patterns
      if (IGNORE_PATTERNS.some(pattern => item.includes(pattern))) {
        continue;
      }
      
      const fullPath = path.join(dir, item);
      const stats = fs.statSync(fullPath);
      
      if (stats.isDirectory()) {
        result.directories.push(fullPath);
        const subResult = scanDirectory(fullPath, depth + 1);
        result.files.push(...subResult.files);
        result.directories.push(...subResult.directories);
        
        // Merge languages
        for (const [lang, count] of Object.entries(subResult.languages)) {
          result.languages[lang] = (result.languages[lang] || 0) + count;
        }
      } else if (stats.isFile() && stats.size < MAX_FILE_SIZE) {
        result.files.push(fullPath);
        
        // Count by extension
        const ext = path.extname(item);
        const lang = extensionToLanguage(ext);
        if (lang) {
          result.languages[lang] = (result.languages[lang] || 0) + 1;
        }
      }
    }
  } catch (err) {
    // Skip inaccessible directories
  }
  
  return result;
}

/**
 * Prioritize files for analysis
 */
function prioritizeFiles(files) {
  const priority = {
    critical: [],
    high: [],
    medium: [],
    low: []
  };
  
  for (const file of files) {
    const basename = path.basename(file);
    const dirname = path.dirname(file);
    
    // Critical: Entry points and package managers
    if (basename.match(/^(package\.json|requirements\.txt|Gemfile|pom\.xml|go\.mod|Cargo\.toml|composer\.json)$/)) {
      priority.critical.push(file);
    }
    else if (basename.match(/^(index|main|app|server)\.(js|ts|jsx|tsx|py|java|go|rs)$/)) {
      priority.critical.push(file);
    }
    else if (basename.match(/^README/i)) {
      priority.critical.push(file);
    }
    // High: Config and core source
    else if (basename.match(/config|\.env|settings|tsconfig|webpack|vite|rollup/)) {
      priority.high.push(file);
    }
    else if (dirname.match(/\/(src|lib|app|core|domain)\//)) {
      priority.high.push(file);
    }
    // Medium: Other source files
    else if (file.match(/\.(js|ts|jsx|tsx|py|java|go|rs|rb|php)$/)) {
      priority.medium.push(file);
    }
    // Low: Tests and docs
    else {
      priority.low.push(file);
    }
  }
  
  return priority;
}

/**
 * Read multiple files
 */
function readFiles(filePaths) {
  const contents = [];
  
  for (const filePath of filePaths) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      contents.push({
        path: filePath,
        name: path.basename(filePath),
        content: content,
        lines: content.split('\n').length,
        size: content.length
      });
    } catch (err) {
      // Skip unreadable files
    }
  }
  
  return contents;
}

/**
 * Detect patterns and frameworks
 */
function detectPatterns(structure, criticalFiles, highFiles) {
  const patterns = {
    languages: Object.keys(structure.languages).sort((a, b) => 
      structure.languages[b] - structure.languages[a]
    ),
    frameworks: [],
    architecture: 'monolithic',
    databases: [],
    testing: [],
    buildTools: []
  };
  
  const allContent = [...criticalFiles, ...highFiles]
    .map(f => f.content)
    .join('\n');
  
  // Detect frameworks
  const frameworkPatterns = {
    'React': /import.*from ['"]react['"]/,
    'Next.js': /"next"|next\.config/,
    'Vue': /import.*from ['"]vue['"]/,
    'Angular': /@angular/,
    'Django': /django\.|from django/,
    'Flask': /from flask import/,
    'FastAPI': /from fastapi import/,
    'Express': /require\(['"]express['"]\)|from ['"]express['"]/,
    'Spring Boot': /@SpringBootApplication|spring-boot/,
    'Laravel': /Illuminate\\|laravel/,
    'Ruby on Rails': /Rails\.|ActiveRecord/
  };
  
  for (const [framework, pattern] of Object.entries(frameworkPatterns)) {
    if (pattern.test(allContent)) {
      patterns.frameworks.push(framework);
    }
  }
  
  // Detect databases
  const dbPatterns = {
    'PostgreSQL': /pg|postgres|psycopg/,
    'MySQL': /mysql/,
    'MongoDB': /mongodb|mongoose/,
    'Redis': /redis|ioredis/,
    'SQLite': /sqlite/
  };
  
  for (const [db, pattern] of Object.entries(dbPatterns)) {
    if (pattern.test(allContent)) {
      patterns.databases.push(db);
    }
  }
  
  // Detect architecture
  if (allContent.includes('workspaces') || allContent.includes('lerna')) {
    patterns.architecture = 'monorepo';
  }
  
  // Detect testing
  if (allContent.match(/jest|vitest|mocha|pytest|junit/)) {
    patterns.testing.push('automated-tests');
  }
  
  return patterns;
}

/**
 * Build dependency graph
 */
function buildDependencyGraph(files) {
  const graph = {
    nodes: [],
    edges: [],
    entryPoints: []
  };
  
  for (const file of files) {
    const imports = extractImports(file.content);
    
    graph.nodes.push({
      file: file.path,
      imports: imports.length,
      complexity: estimateComplexity(file.content)
    });
    
    if (imports.length === 0 || file.name.match(/^(index|main|app)/)) {
      graph.entryPoints.push(file.path);
    }
  }
  
  return graph;
}

/**
 * Extract imports from code
 */
function extractImports(content) {
  const imports = [];
  
  // ES6 imports
  const es6Pattern = /import .* from ['"](.+)['"]/g;
  let match;
  while ((match = es6Pattern.exec(content)) !== null) {
    imports.push(match[1]);
  }
  
  // CommonJS requires
  const cjsPattern = /require\(['"](.+)['"]\)/g;
  while ((match = cjsPattern.exec(content)) !== null) {
    imports.push(match[1]);
  }
  
  // Python imports
  const pyPattern = /from (\S+) import|import (\S+)/g;
  while ((match = pyPattern.exec(content)) !== null) {
    imports.push(match[1] || match[2]);
  }
  
  return imports;
}

/**
 * Estimate code complexity
 */
function estimateComplexity(content) {
  const lines = content.split('\n').length;
  const functions = (content.match(/function |def |func /g) || []).length;
  const conditionals = (content.match(/if |switch |case /g) || []).length;
  const loops = (content.match(/for |while |forEach/g) || []).length;
  
  return {
    lines,
    functions,
    conditionals,
    loops,
    score: functions + conditionals * 2 + loops * 2
  };
}

/**
 * Extract teachable code snippets
 */
function extractTeachableCode(files, patterns) {
  const teachable = [];
  
  for (const file of files) {
    // Extract functions
    const functionPattern = /(?:function|const|let|var)\s+(\w+)\s*[=\(][\s\S]{20,500}?[}\)]/g;
    let match;
    
    while ((match = functionPattern.exec(file.content)) !== null) {
      const snippet = match[0];
      const complexity = estimateComplexity(snippet);
      
      // Good teaching material: not too simple, not too complex
      if (complexity.lines >= 5 && complexity.lines <= 50 && complexity.score < 20) {
        teachable.push({
          name: match[1],
          file: file.path,
          code: snippet,
          complexity: complexity.score,
          lines: complexity.lines,
          teachingValue: calculateTeachingValue(snippet, complexity)
        });
      }
    }
  }
  
  // Sort by teaching value
  return teachable.sort((a, b) => b.teachingValue - a.teachingValue).slice(0, 20);
}

/**
 * Calculate teaching value
 */
function calculateTeachingValue(code, complexity) {
  let value = 0;
  
  // Has comments
  if (code.match(/\/\/|\/\*|\#|"""/)) value += 3;
  
  // Moderate complexity (sweet spot)
  if (complexity.score >= 5 && complexity.score <= 15) value += 5;
  
  // Uses common patterns
  if (code.match(/async|await|promise|callback/)) value += 2;
  if (code.match(/map|filter|reduce/)) value += 2;
  if (code.match(/class|extends/)) value += 2;
  
  // Clear naming
  if (code.match(/[a-z][A-Z]/)) value += 1; // camelCase
  
  return value;
}

/**
 * Generate recommendations
 */
function generateRecommendations(patterns, teachable, dependencies) {
  const recommendations = {
    pattern: 'A',
    patternName: 'Documentation Overlay',
    effort: 'Low (1-2 weeks)',
    reasons: [],
    techStack: [],
    lessons: []
  };
  
  // Determine best pattern
  if (patterns.frameworks.includes('React') || patterns.frameworks.includes('Vue')) {
    if (patterns.architecture === 'monorepo') {
      recommendations.pattern = 'B';
      recommendations.patternName = 'Monorepo with Shared Packages';
      recommendations.effort = 'Medium (4-6 weeks)';
      recommendations.reasons.push('Monorepo structure detected');
    } else {
      recommendations.pattern = 'D';
      recommendations.patternName = 'Component Showcase';
      recommendations.effort = 'Low (1-2 weeks)';
      recommendations.reasons.push('Component-based framework detected');
    }
  }
  
  if (patterns.frameworks.some(f => f.match(/Django|Flask|FastAPI|Express|Spring/))) {
    recommendations.pattern = 'C';
    recommendations.patternName = 'API-First Approach';
    recommendations.effort = 'Low-Medium (2-3 weeks)';
    recommendations.reasons.push('Backend framework detected');
  }
  
  // Tech stack recommendations
  recommendations.techStack = [
    'Next.js 15 for course platform',
    'Monaco Editor for code editing',
    'Supabase for user data and progress'
  ];
  
  if (patterns.databases.length > 0) {
    recommendations.techStack.push(`Use existing ${patterns.databases[0]} for course content`);
  }
  
  // Generate lesson ideas from teachable code
  recommendations.lessons = teachable.slice(0, 5).map((snippet, i) => ({
    order: i + 1,
    title: `Understanding ${snippet.name}`,
    file: snippet.file,
    complexity: snippet.complexity,
    estimatedTime: '30-45 minutes'
  }));
  
  return recommendations;
}

/**
 * Map file extension to language
 */
function extensionToLanguage(ext) {
  const map = {
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.py': 'Python',
    '.java': 'Java',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.cpp': 'C++',
    '.c': 'C',
    '.swift': 'Swift',
    '.kt': 'Kotlin'
  };
  
  return map[ext] || null;
}

// Main execution
if (require.main === module) {
  const targetPath = process.argv[2] || '.';
  
  analyzeCodebase(targetPath)
    .then(result => {
      // Output JSON to stdout
      console.log(JSON.stringify(result, null, 2));
    })
    .catch(err => {
      console.error('Error:', err.message);
      process.exit(1);
    });
}

module.exports = { analyzeCodebase };
