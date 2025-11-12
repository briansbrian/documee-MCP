# Advanced Codebase Discovery Script - Identifies ANY code structure
# Usage: .\discover-codebase-advanced.ps1 [path-to-codebase]

param(
    [string]$Path = ".",
    [switch]$Detailed,
    [switch]$ExportJson
)

$ErrorActionPreference = "SilentlyContinue"
$FullPath = Resolve-Path $Path

# Initialize results object
$results = @{
    Path = $FullPath
    Timestamp = Get-Date
    Languages = @{}
    Frameworks = @()
    BuildTools = @()
    PackageManagers = @()
    Architecture = @{}
    EntryPoints = @()
    ConfigFiles = @()
    DatabaseSystems = @()
    TestingFrameworks = @()
    CITools = @()
    Containerization = @()
    CloudProviders = @()
    Documentation = @()
    CodeMetrics = @{}
    Recommendations = @()
}

Write-Host "=== ADVANCED CODEBASE DISCOVERY ===" -ForegroundColor Cyan
Write-Host "Analyzing: $FullPath" -ForegroundColor Yellow
Write-Host ""

# PHASE 1: DEEP FILE ANALYSIS
Write-Host "[1/10] Analyzing file structure..." -ForegroundColor Green

# Get all files excluding common ignore patterns
$allFiles = Get-ChildItem -Path $Path -Recurse -File | Where-Object {
    $_.DirectoryName -notmatch "(node_modules|\.git|\.venv|venv|__pycache__|dist|build|target|vendor|\.next|\.nuxt|out|coverage)"
}

# Language detection by extension
$extensionMap = @{
    '.js' = 'JavaScript'; '.jsx' = 'JavaScript'; '.mjs' = 'JavaScript'; '.cjs' = 'JavaScript'
    '.ts' = 'TypeScript'; '.tsx' = 'TypeScript'
    '.py' = 'Python'; '.pyw' = 'Python'; '.pyx' = 'Python'
    '.java' = 'Java'; '.class' = 'Java'; '.jar' = 'Java'
    '.rb' = 'Ruby'; '.rake' = 'Ruby'; '.gemspec' = 'Ruby'
    '.php' = 'PHP'; '.phtml' = 'PHP'
    '.go' = 'Go'
    '.rs' = 'Rust'
    '.c' = 'C'; '.h' = 'C'
    '.cpp' = 'C++'; '.cc' = 'C++'; '.cxx' = 'C++'; '.hpp' = 'C++'
    '.cs' = 'C#'; '.csx' = 'C#'
    '.swift' = 'Swift'
    '.kt' = 'Kotlin'; '.kts' = 'Kotlin'
    '.scala' = 'Scala'
    '.clj' = 'Clojure'; '.cljs' = 'Clojure'
    '.ex' = 'Elixir'; '.exs' = 'Elixir'
    '.erl' = 'Erlang'; '.hrl' = 'Erlang'
    '.hs' = 'Haskell'
    '.ml' = 'OCaml'; '.mli' = 'OCaml'
    '.lua' = 'Lua'
    '.r' = 'R'; '.R' = 'R'
    '.dart' = 'Dart'
    '.vue' = 'Vue'; '.svelte' = 'Svelte'
    '.sol' = 'Solidity'
    '.zig' = 'Zig'
    '.nim' = 'Nim'
    '.cr' = 'Crystal'
    '.jl' = 'Julia'
    '.v' = 'V'
    '.elm' = 'Elm'
    '.purs' = 'PureScript'
    '.fs' = 'F#'; '.fsx' = 'F#'
    '.vb' = 'Visual Basic'
    '.pl' = 'Perl'; '.pm' = 'Perl'
    '.sh' = 'Shell'; '.bash' = 'Shell'; '.zsh' = 'Shell'
    '.ps1' = 'PowerShell'; '.psm1' = 'PowerShell'
    '.sql' = 'SQL'
    '.graphql' = 'GraphQL'; '.gql' = 'GraphQL'
    '.proto' = 'Protocol Buffers'
    '.tf' = 'Terraform'; '.tfvars' = 'Terraform'
    '.yaml' = 'YAML'; '.yml' = 'YAML'
    '.json' = 'JSON'; '.jsonc' = 'JSON'
    '.xml' = 'XML'
    '.html' = 'HTML'; '.htm' = 'HTML'
    '.css' = 'CSS'; '.scss' = 'SCSS'; '.sass' = 'Sass'; '.less' = 'Less'
    '.md' = 'Markdown'; '.mdx' = 'MDX'
}

foreach ($file in $allFiles) {
    $ext = $file.Extension.ToLower()
    if ($extensionMap.ContainsKey($ext)) {
        $lang = $extensionMap[$ext]
        if (-not $results.Languages.ContainsKey($lang)) {
            $results.Languages[$lang] = @{ Count = 0; Size = 0 }
        }
        $results.Languages[$lang].Count++
        $results.Languages[$lang].Size += $file.Length
    }
}

Write-Host "   Found $($results.Languages.Count) languages" -ForegroundColor White
$results.Languages.GetEnumerator() | Sort-Object { $_.Value.Count } -Descending | Select-Object -First 5 | ForEach-Object {
    Write-Host "   - $($_.Key): $($_.Value.Count) files" -ForegroundColor Gray
}


# PHASE 2: FRAMEWORK & LIBRARY DETECTION
Write-Host ""
Write-Host "[2/10] Detecting frameworks and libraries..." -ForegroundColor Green

# Framework detection patterns
$frameworkPatterns = @{
    # JavaScript/TypeScript
    'React' = @('package.json:react', 'import.*from.*[''"]react[''"]')
    'Next.js' = @('package.json:next', 'next.config')
    'Vue.js' = @('package.json:vue', '*.vue')
    'Nuxt' = @('package.json:nuxt', 'nuxt.config')
    'Angular' = @('package.json:@angular', 'angular.json')
    'Svelte' = @('package.json:svelte', '*.svelte')
    'Express' = @('package.json:express')
    'NestJS' = @('package.json:@nestjs')
    'Fastify' = @('package.json:fastify')
    'Koa' = @('package.json:koa')
    'Gatsby' = @('package.json:gatsby', 'gatsby-config')
    'Remix' = @('package.json:@remix-run')
    'Astro' = @('package.json:astro', 'astro.config')
    'Solid.js' = @('package.json:solid-js')
    'Qwik' = @('package.json:@builder.io/qwik')
    
    # Python
    'Django' = @('requirements.txt:django', 'manage.py', 'settings.py')
    'Flask' = @('requirements.txt:flask', 'app.py')
    'FastAPI' = @('requirements.txt:fastapi')
    'Pyramid' = @('requirements.txt:pyramid')
    'Tornado' = @('requirements.txt:tornado')
    'Sanic' = @('requirements.txt:sanic')
    'Bottle' = @('requirements.txt:bottle')
    'CherryPy' = @('requirements.txt:cherrypy')
    
    # Ruby
    'Ruby on Rails' = @('Gemfile:rails', 'config/routes.rb')
    'Sinatra' = @('Gemfile:sinatra')
    'Hanami' = @('Gemfile:hanami')
    
    # Java
    'Spring Boot' = @('pom.xml:spring-boot', 'build.gradle:spring-boot')
    'Quarkus' = @('pom.xml:quarkus', 'build.gradle:quarkus')
    'Micronaut' = @('pom.xml:micronaut', 'build.gradle:micronaut')
    'Jakarta EE' = @('pom.xml:jakarta')
    'Play Framework' = @('build.sbt:play')
    
    # PHP
    'Laravel' = @('composer.json:laravel', 'artisan')
    'Symfony' = @('composer.json:symfony')
    'CodeIgniter' = @('composer.json:codeigniter')
    'Yii' = @('composer.json:yiisoft')
    'CakePHP' = @('composer.json:cakephp')
    
    # Go
    'Gin' = @('go.mod:gin-gonic/gin')
    'Echo' = @('go.mod:labstack/echo')
    'Fiber' = @('go.mod:gofiber/fiber')
    'Chi' = @('go.mod:go-chi/chi')
    'Beego' = @('go.mod:beego')
    
    # .NET
    'ASP.NET Core' = @('*.csproj:Microsoft.AspNetCore')
    'Blazor' = @('*.csproj:Microsoft.AspNetCore.Components')
    
    # Rust
    'Actix' = @('Cargo.toml:actix-web')
    'Rocket' = @('Cargo.toml:rocket')
    'Axum' = @('Cargo.toml:axum')
}

# Check for frameworks
foreach ($framework in $frameworkPatterns.Keys) {
    $patterns = $frameworkPatterns[$framework]
    $found = $false
    
    foreach ($pattern in $patterns) {
        if ($pattern -match '(.+):(.+)') {
            $file = $matches[1]
            $search = $matches[2]
            
            $targetFiles = Get-ChildItem -Path $Path -Filter $file -Recurse -File
            foreach ($targetFile in $targetFiles) {
                $content = Get-Content $targetFile.FullName -Raw
                if ($content -match $search) {
                    $found = $true
                    break
                }
            }
        } else {
            # File pattern check
            $exists = Get-ChildItem -Path $Path -Filter $pattern -Recurse -File
            if ($exists) {
                $found = $true
            }
        }
        
        if ($found) { break }
    }
    
    if ($found) {
        $results.Frameworks += $framework
    }
}

Write-Host "   Detected frameworks:" -ForegroundColor White
if ($results.Frameworks.Count -gt 0) {
    $results.Frameworks | ForEach-Object {
        Write-Host "   ★ $_" -ForegroundColor Magenta
    }
} else {
    Write-Host "   No major frameworks detected" -ForegroundColor Gray
}


# PHASE 3: BUILD TOOLS & PACKAGE MANAGERS
Write-Host ""
Write-Host "[3/10] Identifying build tools..." -ForegroundColor Green

$buildToolChecks = @{
    'npm' = 'package.json'
    'yarn' = 'yarn.lock'
    'pnpm' = 'pnpm-lock.yaml'
    'bun' = 'bun.lockb'
    'pip' = 'requirements.txt'
    'poetry' = 'pyproject.toml'
    'pipenv' = 'Pipfile'
    'conda' = 'environment.yml'
    'bundler' = 'Gemfile'
    'composer' = 'composer.json'
    'maven' = 'pom.xml'
    'gradle' = 'build.gradle'
    'sbt' = 'build.sbt'
    'cargo' = 'Cargo.toml'
    'go modules' = 'go.mod'
    'nuget' = '*.csproj'
    'mix' = 'mix.exs'
    'rebar3' = 'rebar.config'
    'leiningen' = 'project.clj'
    'stack' = 'stack.yaml'
    'cabal' = '*.cabal'
    'pub' = 'pubspec.yaml'
    'cocoapods' = 'Podfile'
    'carthage' = 'Cartfile'
    'swift package manager' = 'Package.swift'
}

foreach ($tool in $buildToolChecks.Keys) {
    $pattern = $buildToolChecks[$tool]
    $exists = Get-ChildItem -Path $Path -Filter $pattern -Recurse -File | Select-Object -First 1
    if ($exists) {
        $results.PackageManagers += $tool
    }
}

Write-Host "   Package managers:" -ForegroundColor White
$results.PackageManagers | ForEach-Object {
    Write-Host "   - $_" -ForegroundColor Gray
}

# Build system detection
$buildSystems = @{
    'Webpack' = 'webpack.config.*'
    'Vite' = 'vite.config.*'
    'Rollup' = 'rollup.config.*'
    'Parcel' = '.parcelrc'
    'esbuild' = 'esbuild.config.*'
    'Turbopack' = 'turbo.json'
    'Gulp' = 'gulpfile.*'
    'Grunt' = 'Gruntfile.*'
    'Make' = 'Makefile'
    'CMake' = 'CMakeLists.txt'
    'Bazel' = 'BUILD'
    'Ninja' = 'build.ninja'
}

foreach ($system in $buildSystems.Keys) {
    $pattern = $buildSystems[$system]
    $exists = Get-ChildItem -Path $Path -Filter $pattern -Recurse -File | Select-Object -First 1
    if ($exists) {
        $results.BuildTools += $system
    }
}

if ($results.BuildTools.Count -gt 0) {
    Write-Host "   Build tools:" -ForegroundColor White
    $results.BuildTools | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Gray
    }
}


# PHASE 4: ARCHITECTURE PATTERN DETECTION
Write-Host ""
Write-Host "[4/10] Analyzing architecture patterns..." -ForegroundColor Green

# Detect monorepo
$workspaceFiles = Get-ChildItem -Path $Path -Filter "package.json" -File | Select-Object -First 1
if ($workspaceFiles) {
    $packageContent = Get-Content $workspaceFiles.FullName -Raw | ConvertFrom-Json
    if ($packageContent.workspaces) {
        $results.Architecture['Type'] = 'Monorepo'
        $results.Architecture['Tool'] = 'npm/yarn workspaces'
    }
}

if (Test-Path "$Path/lerna.json") {
    $results.Architecture['Type'] = 'Monorepo'
    $results.Architecture['Tool'] = 'Lerna'
}

if (Test-Path "$Path/pnpm-workspace.yaml") {
    $results.Architecture['Type'] = 'Monorepo'
    $results.Architecture['Tool'] = 'pnpm'
}

if (Test-Path "$Path/turbo.json") {
    $results.Architecture['Type'] = 'Monorepo'
    $results.Architecture['Tool'] = 'Turborepo'
}

# Detect microservices
$dockerComposeFiles = Get-ChildItem -Path $Path -Filter "docker-compose*.yml" -Recurse -File
if ($dockerComposeFiles.Count -gt 0) {
    $composeContent = Get-Content $dockerComposeFiles[0].FullName -Raw
    $serviceCount = ([regex]::Matches($composeContent, "^\s+\w+:", [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count
    if ($serviceCount -gt 3) {
        $results.Architecture['Type'] = 'Microservices'
        $results.Architecture['Services'] = $serviceCount
    }
}

# Detect serverless
$serverlessFiles = @('serverless.yml', 'serverless.yaml', 'sam.yaml', 'template.yaml')
foreach ($file in $serverlessFiles) {
    if (Test-Path "$Path/$file") {
        $results.Architecture['Type'] = 'Serverless'
        break
    }
}

# Detect MVC pattern
$mvcIndicators = @{
    'models' = $false
    'views' = $false
    'controllers' = $false
}

foreach ($key in $mvcIndicators.Keys) {
    $dirs = Get-ChildItem -Path $Path -Directory -Recurse | Where-Object { $_.Name -match $key }
    if ($dirs) {
        $mvcIndicators[$key] = $true
    }
}

if ($mvcIndicators.Values -contains $true) {
    $mvcCount = ($mvcIndicators.Values | Where-Object { $_ -eq $true }).Count
    if ($mvcCount -ge 2) {
        $results.Architecture['Pattern'] = 'MVC'
    }
}

# Detect layered architecture
$layerIndicators = @('domain', 'application', 'infrastructure', 'presentation')
$foundLayers = @()
foreach ($layer in $layerIndicators) {
    $dirs = Get-ChildItem -Path $Path -Directory -Recurse | Where-Object { $_.Name -match $layer }
    if ($dirs) {
        $foundLayers += $layer
    }
}

if ($foundLayers.Count -ge 3) {
    $results.Architecture['Pattern'] = 'Layered/Clean Architecture'
}

Write-Host "   Architecture:" -ForegroundColor White
if ($results.Architecture.Count -gt 0) {
    $results.Architecture.GetEnumerator() | ForEach-Object {
        Write-Host "   - $($_.Key): $($_.Value)" -ForegroundColor Gray
    }
} else {
    Write-Host "   - Standard/Monolithic" -ForegroundColor Gray
}


# PHASE 5: DATABASE DETECTION
Write-Host ""
Write-Host "[5/10] Detecting databases..." -ForegroundColor Green

$databasePatterns = @{
    'PostgreSQL' = @('pg', 'postgres', 'psycopg', 'node-postgres')
    'MySQL' = @('mysql', 'mysql2', 'pymysql')
    'MongoDB' = @('mongodb', 'mongoose', 'pymongo')
    'Redis' = @('redis', 'ioredis')
    'SQLite' = @('sqlite', 'sqlite3', 'better-sqlite3')
    'MariaDB' = @('mariadb')
    'Oracle' = @('oracledb', 'cx_Oracle')
    'SQL Server' = @('mssql', 'tedious', 'pyodbc')
    'Cassandra' = @('cassandra-driver')
    'DynamoDB' = @('aws-sdk.*dynamodb', '@aws-sdk/client-dynamodb')
    'Elasticsearch' = @('elasticsearch', '@elastic/elasticsearch')
    'Neo4j' = @('neo4j-driver')
    'CouchDB' = @('nano', 'couchdb')
    'Firebase' = @('firebase', '@firebase')
    'Supabase' = @('supabase', '@supabase')
}

# Check package files
$packageFiles = Get-ChildItem -Path $Path -Filter "package.json" -Recurse -File
foreach ($pkgFile in $packageFiles) {
    $content = Get-Content $pkgFile.FullName -Raw
    foreach ($db in $databasePatterns.Keys) {
        foreach ($pattern in $databasePatterns[$db]) {
            if ($content -match $pattern) {
                if ($results.DatabaseSystems -notcontains $db) {
                    $results.DatabaseSystems += $db
                }
            }
        }
    }
}

# Check Python requirements
$reqFiles = Get-ChildItem -Path $Path -Filter "requirements.txt" -Recurse -File
foreach ($reqFile in $reqFiles) {
    $content = Get-Content $reqFile.FullName -Raw
    foreach ($db in $databasePatterns.Keys) {
        foreach ($pattern in $databasePatterns[$db]) {
            if ($content -match $pattern) {
                if ($results.DatabaseSystems -notcontains $db) {
                    $results.DatabaseSystems += $db
                }
            }
        }
    }
}

# Check for ORM/Query builders
$ormPatterns = @{
    'Prisma' = 'schema.prisma'
    'TypeORM' = 'ormconfig.json'
    'Sequelize' = 'package.json:sequelize'
    'Drizzle' = 'drizzle.config.*'
    'SQLAlchemy' = 'requirements.txt:sqlalchemy'
    'Django ORM' = 'models.py'
    'ActiveRecord' = 'Gemfile:activerecord'
    'Hibernate' = 'pom.xml:hibernate'
    'Entity Framework' = '*.csproj:EntityFramework'
}

$foundORMs = @()
foreach ($orm in $ormPatterns.Keys) {
    $pattern = $ormPatterns[$orm]
    if ($pattern -match '(.+):(.+)') {
        $file = $matches[1]
        $search = $matches[2]
        $targetFiles = Get-ChildItem -Path $Path -Filter $file -Recurse -File
        foreach ($targetFile in $targetFiles) {
            $content = Get-Content $targetFile.FullName -Raw
            if ($content -match $search) {
                $foundORMs += $orm
                break
            }
        }
    } else {
        $exists = Get-ChildItem -Path $Path -Filter $pattern -Recurse -File
        if ($exists) {
            $foundORMs += $orm
        }
    }
}

Write-Host "   Databases:" -ForegroundColor White
if ($results.DatabaseSystems.Count -gt 0) {
    $results.DatabaseSystems | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Gray
    }
} else {
    Write-Host "   - None detected" -ForegroundColor Gray
}

if ($foundORMs.Count -gt 0) {
    Write-Host "   ORMs/Query Builders:" -ForegroundColor White
    $foundORMs | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Gray
    }
}


# PHASE 6: TESTING FRAMEWORKS
Write-Host ""
Write-Host "[6/10] Detecting testing frameworks..." -ForegroundColor Green

$testingFrameworks = @{
    'Jest' = @('jest', 'jest.config')
    'Vitest' = @('vitest', 'vitest.config')
    'Mocha' = @('mocha', '.mocharc')
    'Jasmine' = @('jasmine')
    'Cypress' = @('cypress', 'cypress.config')
    'Playwright' = @('playwright', 'playwright.config')
    'Puppeteer' = @('puppeteer')
    'Testing Library' = @('@testing-library')
    'pytest' = @('pytest', 'pytest.ini')
    'unittest' = @('unittest')
    'RSpec' = @('rspec', '.rspec')
    'Minitest' = @('minitest')
    'JUnit' = @('junit', 'pom.xml:junit')
    'TestNG' = @('testng')
    'NUnit' = @('nunit')
    'xUnit' = @('xunit')
    'Go testing' = @('_test.go')
    'Rust tests' = @('#[test]')
}

foreach ($framework in $testingFrameworks.Keys) {
    $patterns = $testingFrameworks[$framework]
    $found = $false
    
    foreach ($pattern in $patterns) {
        # Check in package.json
        $packageFiles = Get-ChildItem -Path $Path -Filter "package.json" -Recurse -File
        foreach ($pkgFile in $packageFiles) {
            $content = Get-Content $pkgFile.FullName -Raw
            if ($content -match $pattern) {
                $found = $true
                break
            }
        }
        
        # Check for config files
        $configFiles = Get-ChildItem -Path $Path -Filter "*$pattern*" -Recurse -File
        if ($configFiles) {
            $found = $true
        }
        
        if ($found) { break }
    }
    
    if ($found) {
        $results.TestingFrameworks += $framework
    }
}

# Count test files
$testFilePatterns = @('*test*', '*spec*', '*Test*', '*Spec*')
$testFiles = @()
foreach ($pattern in $testFilePatterns) {
    $testFiles += Get-ChildItem -Path $Path -Filter $pattern -Recurse -File
}
$testFileCount = ($testFiles | Select-Object -Unique).Count

Write-Host "   Testing frameworks:" -ForegroundColor White
if ($results.TestingFrameworks.Count -gt 0) {
    $results.TestingFrameworks | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Gray
    }
} else {
    Write-Host "   - None detected" -ForegroundColor Gray
}
Write-Host "   Test files: $testFileCount" -ForegroundColor Gray

# PHASE 7: CI/CD & DEVOPS
Write-Host ""
Write-Host "[7/10] Detecting CI/CD tools..." -ForegroundColor Green

$ciTools = @{
    'GitHub Actions' = '.github/workflows'
    'GitLab CI' = '.gitlab-ci.yml'
    'CircleCI' = '.circleci/config.yml'
    'Travis CI' = '.travis.yml'
    'Jenkins' = 'Jenkinsfile'
    'Azure Pipelines' = 'azure-pipelines.yml'
    'Bitbucket Pipelines' = 'bitbucket-pipelines.yml'
    'Drone' = '.drone.yml'
    'TeamCity' = '.teamcity'
    'Bamboo' = 'bamboo.yml'
}

foreach ($tool in $ciTools.Keys) {
    $path = $ciTools[$tool]
    if (Test-Path "$Path/$path") {
        $results.CITools += $tool
    }
}

# Containerization
$containerTools = @{
    'Docker' = 'Dockerfile'
    'Docker Compose' = 'docker-compose.yml'
    'Kubernetes' = '*.yaml:kind: Deployment'
    'Helm' = 'Chart.yaml'
    'Podman' = 'Containerfile'
}

foreach ($tool in $containerTools.Keys) {
    $pattern = $containerTools[$tool]
    if ($pattern -match ':') {
        $file, $content = $pattern -split ':'
        $files = Get-ChildItem -Path $Path -Filter $file -Recurse -File
        foreach ($f in $files) {
            $fileContent = Get-Content $f.FullName -Raw
            if ($fileContent -match $content) {
                $results.Containerization += $tool
                break
            }
        }
    } else {
        if (Get-ChildItem -Path $Path -Filter $pattern -Recurse -File) {
            $results.Containerization += $tool
        }
    }
}

Write-Host "   CI/CD:" -ForegroundColor White
if ($results.CITools.Count -gt 0) {
    $results.CITools | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Gray
    }
} else {
    Write-Host "   - None detected" -ForegroundColor Gray
}

if ($results.Containerization.Count -gt 0) {
    Write-Host "   Containerization:" -ForegroundColor White
    $results.Containerization | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Gray
    }
}


# PHASE 8: CLOUD PROVIDERS & SERVICES
Write-Host ""
Write-Host "[8/10] Detecting cloud providers..." -ForegroundColor Green

$cloudPatterns = @{
    'AWS' = @('aws-sdk', '@aws-sdk', 'boto3', 'aws-cdk', 'serverless.yml:provider: aws')
    'Google Cloud' = @('google-cloud', '@google-cloud', 'gcloud')
    'Azure' = @('azure', '@azure', 'az ')
    'Vercel' = @('vercel.json', 'package.json:vercel')
    'Netlify' = @('netlify.toml', '_redirects')
    'Heroku' = @('Procfile', 'app.json')
    'Railway' = @('railway.json')
    'Render' = @('render.yaml')
    'DigitalOcean' = @('.do/app.yaml')
    'Cloudflare' = @('wrangler.toml', 'cloudflare')
}

foreach ($provider in $cloudPatterns.Keys) {
    $patterns = $cloudPatterns[$provider]
    $found = $false
    
    foreach ($pattern in $patterns) {
        if ($pattern -match '(.+):(.+)') {
            $file = $matches[1]
            $search = $matches[2]
            $targetFiles = Get-ChildItem -Path $Path -Filter $file -Recurse -File
            foreach ($targetFile in $targetFiles) {
                $content = Get-Content $targetFile.FullName -Raw
                if ($content -match $search) {
                    $found = $true
                    break
                }
            }
        } else {
            # Check in files
            $allContent = ""
            Get-ChildItem -Path $Path -Include "package.json","requirements.txt","go.mod" -Recurse -File | ForEach-Object {
                $allContent += Get-Content $_.FullName -Raw
            }
            if ($allContent -match $pattern) {
                $found = $true
            }
            
            # Check for config files
            if (Get-ChildItem -Path $Path -Filter $pattern -Recurse -File) {
                $found = $true
            }
        }
        
        if ($found) { break }
    }
    
    if ($found) {
        $results.CloudProviders += $provider
    }
}

Write-Host "   Cloud providers:" -ForegroundColor White
if ($results.CloudProviders.Count -gt 0) {
    $results.CloudProviders | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Gray
    }
} else {
    Write-Host "   - None detected" -ForegroundColor Gray
}

# PHASE 9: DOCUMENTATION & ENTRY POINTS
Write-Host ""
Write-Host "[9/10] Finding entry points and documentation..." -ForegroundColor Green

# Entry points
$entryPatterns = @(
    'main.*', 'index.*', 'app.*', 'server.*', 'start.*',
    'Program.cs', 'Application.java', '__init__.py', 'boot.rb'
)

foreach ($pattern in $entryPatterns) {
    $files = Get-ChildItem -Path $Path -Filter $pattern -Recurse -File | Select-Object -First 5
    foreach ($file in $files) {
        $relativePath = $file.FullName.Replace($FullPath, "").TrimStart("\")
        $results.EntryPoints += $relativePath
    }
}

Write-Host "   Entry points:" -ForegroundColor White
if ($results.EntryPoints.Count -gt 0) {
    $results.EntryPoints | Select-Object -First 5 | ForEach-Object {
        Write-Host "   - $_" -ForegroundColor Gray
    }
} else {
    Write-Host "   - None found" -ForegroundColor Gray
}

# Documentation
$docPatterns = @('README*', '*.md', 'docs/', 'documentation/', 'wiki/')
foreach ($pattern in $docPatterns) {
    $files = Get-ChildItem -Path $Path -Filter $pattern -Recurse | Select-Object -First 10
    foreach ($file in $files) {
        $relativePath = $file.FullName.Replace($FullPath, "").TrimStart("\")
        $results.Documentation += $relativePath
    }
}

Write-Host "   Documentation files: $($results.Documentation.Count)" -ForegroundColor Gray

# PHASE 10: CODE METRICS & COMPLEXITY
Write-Host ""
Write-Host "[10/10] Calculating code metrics..." -ForegroundColor Green

$codeFiles = $allFiles | Where-Object { 
    $_.Extension -match '\.(js|ts|jsx|tsx|py|java|rb|php|go|rs|cs|cpp|c|swift|kt)$' 
}

$totalLines = 0
$totalSize = 0
foreach ($file in $codeFiles) {
    $lines = (Get-Content $file.FullName).Count
    $totalLines += $lines
    $totalSize += $file.Length
}

$results.CodeMetrics = @{
    TotalFiles = $allFiles.Count
    CodeFiles = $codeFiles.Count
    TotalLines = $totalLines
    TotalSize = [math]::Round($totalSize / 1MB, 2)
    AvgLinesPerFile = if ($codeFiles.Count -gt 0) { [math]::Round($totalLines / $codeFiles.Count, 0) } else { 0 }
}

Write-Host "   Total files: $($results.CodeMetrics.TotalFiles)" -ForegroundColor White
Write-Host "   Code files: $($results.CodeMetrics.CodeFiles)" -ForegroundColor White
Write-Host "   Total lines: $($results.CodeMetrics.TotalLines)" -ForegroundColor White
Write-Host "   Total size: $($results.CodeMetrics.TotalSize) MB" -ForegroundColor White
Write-Host "   Avg lines/file: $($results.CodeMetrics.AvgLinesPerFile)" -ForegroundColor White


# GENERATE RECOMMENDATIONS
Write-Host ""
Write-Host "=== RECOMMENDATIONS ===" -ForegroundColor Cyan
Write-Host ""

# Determine primary language
$primaryLang = ($results.Languages.GetEnumerator() | Sort-Object { $_.Value.Count } -Descending | Select-Object -First 1).Key

# Determine complexity
$complexity = "Low"
if ($results.CodeMetrics.TotalFiles -gt 500) { $complexity = "High" }
elseif ($results.CodeMetrics.TotalFiles -gt 100) { $complexity = "Medium" }

# Generate recommendations
Write-Host "Primary Language: $primaryLang" -ForegroundColor Yellow
Write-Host "Complexity: $complexity" -ForegroundColor Yellow
Write-Host ""

# Pattern recommendation
$recommendedPattern = "A"
$patternName = "Documentation Overlay"
$effort = "Low (1-2 weeks)"

if ($results.Frameworks -contains "React" -or $results.Frameworks -contains "Next.js" -or $results.Frameworks -contains "Vue.js") {
    if ($results.Architecture.Type -eq "Monorepo") {
        $recommendedPattern = "B"
        $patternName = "Monorepo with Shared Packages"
        $effort = "Medium (4-6 weeks)"
    } else {
        $recommendedPattern = "D"
        $patternName = "Component Showcase"
        $effort = "Low (1-2 weeks)"
    }
}

if ($results.Frameworks -match "Django|Flask|FastAPI|Express|NestJS|Spring Boot") {
    $recommendedPattern = "C"
    $patternName = "API-First Approach"
    $effort = "Low-Medium (2-3 weeks)"
}

if ($results.CITools.Count -gt 0 -and $testFileCount -gt 20) {
    $recommendedPattern = "E"
    $patternName = "Git-Based Learning"
    $effort = "Very Low (1 week)"
}

Write-Host "✓ RECOMMENDED PATTERN: $recommendedPattern - $patternName" -ForegroundColor Green
Write-Host "  Estimated effort: $effort" -ForegroundColor Gray
Write-Host ""

$results.Recommendations += "Pattern $recommendedPattern - $patternName"
$results.Recommendations += "Estimated effort: $effort"

# Specific recommendations
Write-Host "Specific Recommendations:" -ForegroundColor Cyan

if ($primaryLang -match "JavaScript|TypeScript") {
    Write-Host "  1. Use Next.js 15 for course platform" -ForegroundColor White
    Write-Host "  2. Integrate Monaco Editor for code editing" -ForegroundColor White
    Write-Host "  3. Use Supabase for user data and progress" -ForegroundColor White
    $results.Recommendations += "Tech stack: Next.js + Monaco + Supabase"
}

if ($results.DatabaseSystems.Count -gt 0) {
    Write-Host "  4. Leverage existing database for course content" -ForegroundColor White
    $results.Recommendations += "Use existing database: $($results.DatabaseSystems -join ', ')"
}

if ($results.TestingFrameworks.Count -gt 0) {
    Write-Host "  5. Use existing tests for exercise validation" -ForegroundColor White
    $results.Recommendations += "Reuse test framework: $($results.TestingFrameworks -join ', ')"
}

if ($results.Containerization -contains "Docker") {
    Write-Host "  6. Use Docker for safe code execution" -ForegroundColor White
    $results.Recommendations += "Code execution: Docker containers"
}

if ($results.Documentation.Count -gt 5) {
    Write-Host "  7. Extract content from existing documentation" -ForegroundColor White
    $results.Recommendations += "Good documentation exists - can be repurposed"
}

if ($complexity -eq "High") {
    Write-Host "  8. Start with 5-10 core lessons, expand gradually" -ForegroundColor White
    $results.Recommendations += "Large codebase - focus on core concepts first"
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review full framework: codebase-to-course-discovery-framework.md" -ForegroundColor White
Write-Host "  2. Set up course platform using recommended pattern" -ForegroundColor White
Write-Host "  3. Extract 5-10 key concepts to teach" -ForegroundColor White
Write-Host "  4. Create interactive exercises" -ForegroundColor White
Write-Host "  5. Deploy and gather feedback" -ForegroundColor White

Write-Host ""
Write-Host "=== END OF ANALYSIS ===" -ForegroundColor Cyan
Write-Host ""

# Export results
if ($ExportJson) {
    $jsonPath = Join-Path $Path "codebase-analysis.json"
    $results | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8
    Write-Host "✓ Analysis exported to: $jsonPath" -ForegroundColor Green
}

# Create summary report
$reportPath = Join-Path $Path "codebase-discovery-report.txt"
$report = @"
CODEBASE DISCOVERY REPORT
Generated: $($results.Timestamp)
Path: $($results.Path)

PRIMARY LANGUAGE: $primaryLang
COMPLEXITY: $complexity

FRAMEWORKS: $($results.Frameworks -join ', ')
ARCHITECTURE: $($results.Architecture.Type)
DATABASES: $($results.DatabaseSystems -join ', ')
TESTING: $($results.TestingFrameworks -join ', ')

RECOMMENDED APPROACH:
Pattern $recommendedPattern - $patternName
Effort: $effort

CODE METRICS:
- Total Files: $($results.CodeMetrics.TotalFiles)
- Code Files: $($results.CodeMetrics.CodeFiles)
- Total Lines: $($results.CodeMetrics.TotalLines)
- Size: $($results.CodeMetrics.TotalSize) MB

RECOMMENDATIONS:
$($results.Recommendations -join "`n")

For detailed analysis, see codebase-analysis.json
"@

$report | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "✓ Summary report saved to: $reportPath" -ForegroundColor Green
Write-Host ""
