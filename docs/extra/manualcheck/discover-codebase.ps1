# Codebase Discovery Script for Windows PowerShell
# Usage: .\discover-codebase.ps1 [path-to-codebase]

param(
    [string]$Path = "."
)

Write-Host "=== CODEBASE DISCOVERY REPORT ===" -ForegroundColor Cyan
Write-Host ""

$FullPath = Resolve-Path $Path
Write-Host "Analyzing: $FullPath" -ForegroundColor Yellow
Write-Host ""

# 1. LANGUAGE DETECTION
Write-Host "1. LANGUAGE DETECTION" -ForegroundColor Green
Write-Host "   Analyzing file extensions..." -ForegroundColor Gray

$extensions = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -ne "" } |
    Group-Object Extension |
    Sort-Object Count -Descending |
    Select-Object -First 10

Write-Host ""
foreach ($ext in $extensions) {
    Write-Host "   $($ext.Name): $($ext.Count) files" -ForegroundColor White
}

# 2. FRAMEWORK DETECTION
Write-Host ""
Write-Host "2. FRAMEWORK DETECTION" -ForegroundColor Green

$frameworks = @()

# JavaScript/Node.js
if (Test-Path "$Path/package.json") {
    Write-Host "   ✓ Node.js project detected" -ForegroundColor Yellow
    $packageJson = Get-Content "$Path/package.json" | ConvertFrom-Json
    
    if ($packageJson.dependencies) {
        Write-Host "   Dependencies:" -ForegroundColor Gray
        $packageJson.dependencies.PSObject.Properties | Select-Object -First 5 | ForEach-Object {
            Write-Host "     - $($_.Name): $($_.Value)" -ForegroundColor White
        }
        
        # Detect specific frameworks
        if ($packageJson.dependencies.react) { $frameworks += "React" }
        if ($packageJson.dependencies.next) { $frameworks += "Next.js" }
        if ($packageJson.dependencies.vue) { $frameworks += "Vue.js" }
        if ($packageJson.dependencies.angular) { $frameworks += "Angular" }
        if ($packageJson.dependencies.express) { $frameworks += "Express" }
        if ($packageJson.dependencies.nestjs) { $frameworks += "NestJS" }
    }
}

# Python
if (Test-Path "$Path/requirements.txt") {
    Write-Host "   ✓ Python project detected" -ForegroundColor Yellow
    $requirements = Get-Content "$Path/requirements.txt" -First 5
    Write-Host "   Requirements:" -ForegroundColor Gray
    foreach ($req in $requirements) {
        Write-Host "     - $req" -ForegroundColor White
    }
    
    # Detect frameworks
    $reqContent = Get-Content "$Path/requirements.txt" -Raw
    if ($reqContent -match "django") { $frameworks += "Django" }
    if ($reqContent -match "flask") { $frameworks += "Flask" }
    if ($reqContent -match "fastapi") { $frameworks += "FastAPI" }
}

# Ruby
if (Test-Path "$Path/Gemfile") {
    Write-Host "   ✓ Ruby project detected" -ForegroundColor Yellow
    $gemfile = Get-Content "$Path/Gemfile" | Select-String "^gem" | Select-Object -First 5
    Write-Host "   Gems:" -ForegroundColor Gray
    foreach ($gem in $gemfile) {
        Write-Host "     - $gem" -ForegroundColor White
    }
    
    $gemContent = Get-Content "$Path/Gemfile" -Raw
    if ($gemContent -match "rails") { $frameworks += "Ruby on Rails" }
}

# Java
if (Test-Path "$Path/pom.xml") {
    Write-Host "   ✓ Java/Maven project detected" -ForegroundColor Yellow
    $frameworks += "Maven"
}

if (Test-Path "$Path/build.gradle") {
    Write-Host "   ✓ Java/Gradle project detected" -ForegroundColor Yellow
    $frameworks += "Gradle"
}

# Go
if (Test-Path "$Path/go.mod") {
    Write-Host "   ✓ Go project detected" -ForegroundColor Yellow
    $goMod = Get-Content "$Path/go.mod" -First 5
    Write-Host "   Modules:" -ForegroundColor Gray
    foreach ($mod in $goMod) {
        Write-Host "     - $mod" -ForegroundColor White
    }
}

# PHP
if (Test-Path "$Path/composer.json") {
    Write-Host "   ✓ PHP project detected" -ForegroundColor Yellow
    $composerJson = Get-Content "$Path/composer.json" | ConvertFrom-Json
    if ($composerJson.require) {
        Write-Host "   Dependencies:" -ForegroundColor Gray
        $composerJson.require.PSObject.Properties | Select-Object -First 5 | ForEach-Object {
            Write-Host "     - $($_.Name): $($_.Value)" -ForegroundColor White
        }
    }
    
    $composerContent = Get-Content "$Path/composer.json" -Raw
    if ($composerContent -match "laravel") { $frameworks += "Laravel" }
    if ($composerContent -match "symfony") { $frameworks += "Symfony" }
}

# .NET
if (Test-Path "$Path/*.csproj") {
    Write-Host "   ✓ .NET project detected" -ForegroundColor Yellow
    $frameworks += ".NET"
}

Write-Host ""
if ($frameworks.Count -gt 0) {
    Write-Host "   Detected Frameworks:" -ForegroundColor Cyan
    foreach ($fw in $frameworks) {
        Write-Host "     ★ $fw" -ForegroundColor Magenta
    }
}

# 3. PROJECT STRUCTURE
Write-Host ""
Write-Host "3. PROJECT STRUCTURE" -ForegroundColor Green

$directories = Get-ChildItem -Path $Path -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notmatch "^(node_modules|\.git|\.venv|venv|__pycache__|dist|build|target)$" } |
    Select-Object -First 15

Write-Host "   Top-level directories:" -ForegroundColor Gray
foreach ($dir in $directories) {
    $fileCount = (Get-ChildItem -Path $dir.FullName -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "   📁 $($dir.Name) ($fileCount files)" -ForegroundColor White
}

# 4. ENTRY POINTS
Write-Host ""
Write-Host "4. ENTRY POINTS" -ForegroundColor Green

$entryPoints = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^(main|index|app|server)\.(js|ts|py|java|go|rb|php)$" } |
    Select-Object -First 10

if ($entryPoints) {
    Write-Host "   Found entry points:" -ForegroundColor Gray
    foreach ($entry in $entryPoints) {
        $relativePath = $entry.FullName.Replace($FullPath, "").TrimStart("\")
        Write-Host "   🚀 $relativePath" -ForegroundColor White
    }
} else {
    Write-Host "   No obvious entry points found" -ForegroundColor Gray
}

# 5. TESTS
Write-Host ""
Write-Host "5. TESTS" -ForegroundColor Green

$testFiles = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "(test|spec)" }

$testCount = ($testFiles | Measure-Object).Count
Write-Host "   Found $testCount test files" -ForegroundColor White

if ($testCount -gt 0) {
    Write-Host "   Test frameworks detected:" -ForegroundColor Gray
    $testContent = $testFiles | Select-Object -First 5 | ForEach-Object { Get-Content $_.FullName -Raw }
    $allTestContent = $testContent -join " "
    
    if ($allTestContent -match "jest") { Write-Host "     - Jest" -ForegroundColor White }
    if ($allTestContent -match "mocha") { Write-Host "     - Mocha" -ForegroundColor White }
    if ($allTestContent -match "pytest") { Write-Host "     - Pytest" -ForegroundColor White }
    if ($allTestContent -match "rspec") { Write-Host "     - RSpec" -ForegroundColor White }
    if ($allTestContent -match "junit") { Write-Host "     - JUnit" -ForegroundColor White }
}

# 6. DOCUMENTATION
Write-Host ""
Write-Host "6. DOCUMENTATION" -ForegroundColor Green

$docFiles = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -eq ".md" -or $_.Name -match "README" } |
    Select-Object -First 10

if ($docFiles) {
    Write-Host "   Found documentation:" -ForegroundColor Gray
    foreach ($doc in $docFiles) {
        $relativePath = $doc.FullName.Replace($FullPath, "").TrimStart("\")
        Write-Host "   📄 $relativePath" -ForegroundColor White
    }
} else {
    Write-Host "   No documentation found" -ForegroundColor Gray
}

# 7. CONFIGURATION FILES
Write-Host ""
Write-Host "7. CONFIGURATION FILES" -ForegroundColor Green

$configFiles = Get-ChildItem -Path $Path -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -match "\.(json|yaml|yml|toml|ini|env|config)$" -or $_.Name -match "config" } |
    Select-Object -First 10

if ($configFiles) {
    Write-Host "   Found configuration files:" -ForegroundColor Gray
    foreach ($config in $configFiles) {
        Write-Host "   ⚙️  $($config.Name)" -ForegroundColor White
    }
}

# 8. CODE STATISTICS
Write-Host ""
Write-Host "8. CODE STATISTICS" -ForegroundColor Green

$allFiles = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Directory.Name -notmatch "^(node_modules|\.git|\.venv|venv|__pycache__|dist|build|target)$" }

$totalFiles = ($allFiles | Measure-Object).Count
$totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "   Total files: $totalFiles" -ForegroundColor White
Write-Host "   Total size: $([math]::Round($totalSize, 2)) MB" -ForegroundColor White

# 9. RECOMMENDATIONS
Write-Host ""
Write-Host "9. COURSE PLATFORM RECOMMENDATIONS" -ForegroundColor Green
Write-Host ""

Write-Host "   Based on analysis, recommended approach:" -ForegroundColor Cyan
Write-Host ""

if ($frameworks -contains "React" -or $frameworks -contains "Next.js") {
    Write-Host "   ✓ PATTERN B: Monorepo with Shared Packages" -ForegroundColor Yellow
    Write-Host "     - Modern React/Next.js detected" -ForegroundColor Gray
    Write-Host "     - Can extract components into packages" -ForegroundColor Gray
    Write-Host "     - Course platform can import real components" -ForegroundColor Gray
}
elseif ($frameworks -contains "Django" -or $frameworks -contains "Flask" -or $frameworks -contains "FastAPI") {
    Write-Host "   ✓ PATTERN C: API-First Approach" -ForegroundColor Yellow
    Write-Host "     - Backend framework detected" -ForegroundColor Gray
    Write-Host "     - Expose API endpoints for course platform" -ForegroundColor Gray
    Write-Host "     - Students interact with real API" -ForegroundColor Gray
}
elseif ($testCount -gt 20) {
    Write-Host "   ✓ PATTERN A: Documentation Overlay" -ForegroundColor Yellow
    Write-Host "     - Well-tested codebase" -ForegroundColor Gray
    Write-Host "     - Create separate course site" -ForegroundColor Gray
    Write-Host "     - Import code snippets and examples" -ForegroundColor Gray
}
else {
    Write-Host "   ✓ PATTERN A: Documentation Overlay (Default)" -ForegroundColor Yellow
    Write-Host "     - Safest approach for any codebase" -ForegroundColor Gray
    Write-Host "     - Zero impact on existing code" -ForegroundColor Gray
    Write-Host "     - Quick to implement" -ForegroundColor Gray
}

Write-Host ""
Write-Host "   Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Review the full framework: codebase-to-course-discovery-framework.md" -ForegroundColor White
Write-Host "   2. Set up Next.js course platform" -ForegroundColor White
Write-Host "   3. Extract 5-10 key concepts to teach" -ForegroundColor White
Write-Host "   4. Create interactive exercises" -ForegroundColor White
Write-Host "   5. Deploy and iterate" -ForegroundColor White

Write-Host ""
Write-Host "=== END OF REPORT ===" -ForegroundColor Cyan
Write-Host ""

# Export report to file
$reportPath = Join-Path $Path "codebase-discovery-report.txt"
$report = @"
CODEBASE DISCOVERY REPORT
Generated: $(Get-Date)
Path: $FullPath

FRAMEWORKS DETECTED:
$($frameworks -join ", ")

TOTAL FILES: $totalFiles
TOTAL SIZE: $([math]::Round($totalSize, 2)) MB
TEST FILES: $testCount

See full analysis above.
"@

$report | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "Report saved to: $reportPath" -ForegroundColor Green
