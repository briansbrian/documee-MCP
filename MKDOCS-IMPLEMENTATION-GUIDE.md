# MkDocs Interactive Course: Practical Implementation Guide

## Quick Start (30 Minutes to Working Course)

### Step 1: Install and Setup (5 min)

```bash
# Install MkDocs and Material theme
pip install mkdocs mkdocs-material pymdown-extensions

# Create project
mkdocs new my-course
cd my-course

# Create directory structure
mkdir -p docs/javascripts
mkdir -p docs/stylesheets
mkdir -p docs/course/module1
mkdir -p docs/course/module2
```

### Step 2: Configure mkdocs.yml (5 min)

```yaml
site_name: My Interactive Course
site_description: Learn by doing
site_author: Your Name

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - search.suggest
    - content.code.copy
    - content.tabs.link
  palette:
    - scheme: default
      primary: indigo
      toggle:
        icon: material/brightness-7
        name: Dark mode
    - scheme: slate
      primary: indigo
      toggle:
        icon: material/brightness-4
        name: Light mode

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.tabbed
  - admonition
  - pymdownx.details

extra_javascript:
  - https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js
  - javascripts/interactive.js

extra_css:
  - stylesheets/custom.css

nav:
  - Home: index.md
  - Course:
    - Module 1:
      - Lesson 1: course/module1/lesson1.md
    - Module 2:
      - Lesson 2: course/module2/lesson1.md
```

### Step 3: Create Interactive JavaScript (10 min)

```javascript
// docs/javascripts/interactive.js

// Initialize Monaco Editor
require.config({ 
  paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' }
});

require(['vs/editor/editor.main'], function() {
  initializeEditors();
  initializeProgress();
  initializeGamification();
});

// Initialize all code editors
function initializeEditors() {
  document.querySelectorAll('.code-editor').forEach((element, index) => {
    const code = element.dataset.starterCode || '';
    const language = element.dataset.language || 'javascript';
    const editorId = `editor-${index}`;
    
    element.innerHTML = `
      <div id="${editorId}" style="height: 400px; border: 1px solid #ddd;"></div>
      <div class="editor-controls">
        <button onclick="runCode('${editorId}')" class="btn-run">▶ Run</button>
        <button onclick="resetCode('${editorId}')" class="btn-reset">↻ Reset</button>
      </div>
      <div id="${editorId}-output" class="output"></div>
    `;
    
    const editor = monaco.editor.create(document.getElementById(editorId), {
      value: code.trim(),
      language: language,
      theme: 'vs-dark',
      minimap: { enabled: false },
      fontSize: 14,
      lineNumbers: 'on',
      roundedSelection: false,
      scrollBeyondLastLine: false,
      automaticLayout: true
    });
    
    // Store editor instance
    window[`editor_${editorId}`] = editor;
    window[`starter_${editorId}`] = code.trim();
  });
}

// Run code in editor
function runCode(editorId) {
  const editor = window[`editor_${editorId}`];
  const code = editor.getValue();
  const outputDiv = document.getElementById(`${editorId}-output`);
  
  // Clear previous output
  outputDiv.innerHTML = '';
  
  // Capture console.log
  const logs = [];
  const originalLog = console.log;
  console.log = function(...args) {
    logs.push(args.join(' '));
    originalLog.apply(console, args);
  };
  
  try {
    // Execute code
    eval(code);
    
    // Display output
    outputDiv.innerHTML = `
      <div class="output-success">
        <strong>Output:</strong>
        <pre>${logs.join('\n') || 'No output'}</pre>
      </div>
    `;
    
    // Award points
    awardPoints(10, 'Ran code');
    
  } catch (error) {
    outputDiv.innerHTML = `
      <div class="output-error">
        <strong>Error:</strong>
        <pre>${error.message}</pre>
      </div>
    `;
  } finally {
    console.log = originalLog;
  }
}

// Reset code to starter
function resetCode(editorId) {
  const editor = window[`editor_${editorId}`];
  const starter = window[`starter_${editorId}`];
  editor.setValue(starter);
}

// Progress tracking
function initializeProgress() {
  const progress = JSON.parse(localStorage.getItem('course_progress') || '{}');
  
  // Mark completed lessons
  document.querySelectorAll('[data-lesson-id]').forEach(lesson => {
    const id = lesson.dataset.lessonId;
    if (progress[id]) {
      lesson.classList.add('completed');
    }
  });
  
  updateProgressBar();
}

function markComplete(lessonId) {
  const progress = JSON.parse(localStorage.getItem('course_progress') || '{}');
  progress[lessonId] = {
    completed: true,
    completedAt: new Date().toISOString()
  };
  localStorage.setItem('course_progress', JSON.stringify(progress));
  
  // Update UI
  document.querySelector(`[data-lesson-id="${lessonId}"]`)?.classList.add('completed');
  updateProgressBar();
  
  // Award points
  awardPoints(100, 'Completed lesson');
  checkBadges();
  
  showNotification('✓ Lesson completed!');
}

function updateProgressBar() {
  const progress = JSON.parse(localStorage.getItem('course_progress') || '{}');
  const total = document.querySelectorAll('[data-lesson-id]').length;
  const completed = Object.keys(progress).length;
  const percentage = total > 0 ? (completed / total) * 100 : 0;
  
  const progressBar = document.getElementById('progress-bar');
  if (progressBar) {
    progressBar.style.width = `${percentage}%`;
    progressBar.textContent = `${Math.round(percentage)}%`;
  }
}

// Gamification
function initializeGamification() {
  updatePoints();
  updateStreak();
  displayBadges();
}

function awardPoints(amount, reason) {
  const points = parseInt(localStorage.getItem('points') || '0');
  const newPoints = points + amount;
  localStorage.setItem('points', newPoints);
  updatePoints();
  showNotification(`+${amount} XP: ${reason}`);
}

function updatePoints() {
  const points = localStorage.getItem('points') || '0';
  const pointsDisplay = document.getElementById('points-display');
  if (pointsDisplay) {
    pointsDisplay.textContent = `${points} XP`;
  }
}

function updateStreak() {
  const lastVisit = localStorage.getItem('last_visit');
  const today = new Date().toDateString();
  
  if (lastVisit !== today) {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    let streak = parseInt(localStorage.getItem('streak') || '0');
    
    if (lastVisit === yesterday.toDateString()) {
      streak++;
    } else if (lastVisit !== today) {
      streak = 1;
    }
    
    localStorage.setItem('streak', streak);
    localStorage.setItem('last_visit', today);
  }
  
  const streakDisplay = document.getElementById('streak-display');
  if (streakDisplay) {
    const streak = localStorage.getItem('streak') || '0';
    streakDisplay.textContent = `🔥 ${streak} day streak`;
  }
}

function checkBadges() {
  const progress = JSON.parse(localStorage.getItem('course_progress') || '{}');
  const completed = Object.keys(progress).length;
  const badges = JSON.parse(localStorage.getItem('badges') || '[]');
  
  const badgeDefinitions = [
    { id: 'first_lesson', name: 'Getting Started', requirement: 1, icon: '🎯' },
    { id: 'five_lessons', name: 'On a Roll', requirement: 5, icon: '🚀' },
    { id: 'ten_lessons', name: 'Dedicated', requirement: 10, icon: '⭐' },
    { id: 'twenty_lessons', name: 'Expert', requirement: 20, icon: '👑' }
  ];
  
  badgeDefinitions.forEach(badge => {
    if (completed >= badge.requirement && !badges.includes(badge.id)) {
      badges.push(badge.id);
      localStorage.setItem('badges', JSON.stringify(badges));
      showBadgeNotification(badge);
    }
  });
  
  displayBadges();
}

function displayBadges() {
  const badges = JSON.parse(localStorage.getItem('badges') || '[]');
  const badgesDisplay = document.getElementById('badges-display');
  
  if (badgesDisplay) {
    const badgeDefinitions = [
      { id: 'first_lesson', name: 'Getting Started', icon: '🎯' },
      { id: 'five_lessons', name: 'On a Roll', icon: '🚀' },
      { id: 'ten_lessons', name: 'Dedicated', icon: '⭐' },
      { id: 'twenty_lessons', name: 'Expert', icon: '👑' }
    ];
    
    badgesDisplay.innerHTML = badgeDefinitions
      .filter(b => badges.includes(b.id))
      .map(b => `<span class="badge" title="${b.name}">${b.icon}</span>`)
      .join('');
  }
}

function showNotification(message) {
  const notification = document.createElement('div');
  notification.className = 'notification';
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.classList.add('show');
  }, 100);
  
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

function showBadgeNotification(badge) {
  const notification = document.createElement('div');
  notification.className = 'notification badge-notification';
  notification.innerHTML = `
    <div class="badge-earned">
      <div class="badge-icon">${badge.icon}</div>
      <div class="badge-text">
        <strong>Badge Earned!</strong>
        <p>${badge.name}</p>
      </div>
    </div>
  `;
  document.body.appendChild(notification);
  
  setTimeout(() => notification.classList.add('show'), 100);
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}
```

### Step 4: Add Custom Styles (5 min)

```css
/* docs/stylesheets/custom.css */

/* Code editor controls */
.editor-controls {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.btn-run, .btn-reset {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-run {
  background: #4CAF50;
  color: white;
}

.btn-run:hover {
  background: #45a049;
}

.btn-reset {
  background: #f44336;
  color: white;
}

.btn-reset:hover {
  background: #da190b;
}

/* Output display */
.output {
  margin-top: 15px;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.output-success {
  background: #e8f5e9;
  border-left: 4px solid #4CAF50;
}

.output-error {
  background: #ffebee;
  border-left: 4px solid #f44336;
}

.output pre {
  margin: 5px 0 0 0;
  white-space: pre-wrap;
}

/* Progress bar */
#progress-bar {
  height: 30px;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  color: white;
  text-align: center;
  line-height: 30px;
  border-radius: 4px;
  transition: width 0.3s;
}

/* Gamification */
#points-display, #streak-display {
  display: inline-block;
  padding: 5px 15px;
  background: #3f51b5;
  color: white;
  border-radius: 20px;
  margin: 0 10px;
  font-weight: 500;
}

#badges-display {
  display: flex;
  gap: 10px;
  margin: 10px 0;
}

.badge {
  font-size: 32px;
  cursor: pointer;
  transition: transform 0.2s;
}

.badge:hover {
  transform: scale(1.2);
}

/* Notifications */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  opacity: 0;
  transform: translateY(-20px);
  transition: all 0.3s;
  z-index: 1000;
}

.notification.show {
  opacity: 1;
  transform: translateY(0);
}

.badge-notification {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.badge-earned {
  display: flex;
  align-items: center;
  gap: 15px;
}

.badge-icon {
  font-size: 48px;
}

.badge-text strong {
  display: block;
  font-size: 16px;
  margin-bottom: 5px;
}

.badge-text p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

/* Completed lessons */
[data-lesson-id].completed::before {
  content: '✓ ';
  color: #4CAF50;
  font-weight: bold;
}
```

### Step 5: Create Your First Lesson (5 min)

```markdown
<!-- docs/course/module1/lesson1.md -->
# Lesson 1: JavaScript Variables

<div class="lesson-header">
  <div id="points-display">0 XP</div>
  <div id="streak-display">🔥 0 day streak</div>
  <div id="badges-display"></div>
</div>

## Learning Objectives
- Understand variable declarations
- Learn the difference between let, const, and var
- Practice declaring variables

## Theory (20%)

In JavaScript, you can declare variables using three keywords:

- `let` - for variables that can change
- `const` - for variables that won't change
- `var` - old way (avoid using)

```javascript
let name = "Alice";  // Can be changed
const age = 25;      // Cannot be changed
var city = "NYC";    // Old way
```

## Interactive Example (10%)

Try editing this code and click Run:

<div class="code-editor" data-language="javascript" data-starter-code="
// Declare variables
let greeting = 'Hello';
const name = 'World';

// Combine them
let message = greeting + ', ' + name + '!';

// Output
console.log(message);
"></div>

## Exercise (60%)

<div class="exercise" data-lesson-id="lesson-1-1">

### Your Task
Create variables for a person's information and display them.

<div class="code-editor" data-language="javascript" data-starter-code="
// TODO: Create variables for:
// - firstName (use let)
// - lastName (use let)
// - age (use const)
// - city (use const)

// TODO: Create a message that says:
// 'My name is [firstName] [lastName], I am [age] years old and live in [city]'

// TODO: Log the message
"></div>

### Requirements
- Use `let` for firstName and lastName
- Use `const` for age and city
- Combine all variables into one message
- Log the message to console

<button onclick="markComplete('lesson-1-1')" class="btn-complete">✓ Mark as Complete</button>

</div>

## Progress

<div style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 20px;">
  <strong>Course Progress:</strong>
  <div id="progress-bar" style="width: 0%; margin-top: 10px;">0%</div>
</div>

## Next Lesson
[Lesson 2: Functions →](lesson2.md)
```

### Step 6: Run and Test (5 min)

```bash
# Start development server
mkdocs serve

# Open browser to http://127.0.0.1:8000
# Test the interactive features!
```

---

## Advanced Features

### Add Code Execution API (Judge0)

```javascript
// Add to docs/javascripts/interactive.js

async function runCodeWithAPI(editorId, language) {
  const editor = window[`editor_${editorId}`];
  const code = editor.getValue();
  const outputDiv = document.getElementById(`${editorId}-output`);
  
  outputDiv.innerHTML = '<div class="loading">Running code...</div>';
  
  try {
    const response = await fetch('https://judge0-ce.p.rapidapi.com/submissions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-RapidAPI-Key': 'YOUR_API_KEY',
        'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
      },
      body: JSON.stringify({
        source_code: btoa(code),
        language_id: getLanguageId(language)
      })
    });
    
    const { token } = await response.json();
    const result = await pollSubmission(token);
    
    outputDiv.innerHTML = `
      <div class="output-success">
        <strong>Output:</strong>
        <pre>${atob(result.stdout || '')}</pre>
      </div>
    `;
  } catch (error) {
    outputDiv.innerHTML = `
      <div class="output-error">
        <strong>Error:</strong>
        <pre>${error.message}</pre>
      </div>
    `;
  }
}

function getLanguageId(language) {
  const ids = {
    'javascript': 63,
    'python': 71,
    'java': 62,
    'cpp': 54,
    'c': 50
  };
  return ids[language] || 63;
}

async function pollSubmission(token) {
  const maxAttempts = 10;
  for (let i = 0; i < maxAttempts; i++) {
    const response = await fetch(
      `https://judge0-ce.p.rapidapi.com/submissions/${token}`,
      {
        headers: {
          'X-RapidAPI-Key': 'YOUR_API_KEY',
          'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
        }
      }
    );
    
    const result = await response.json();
    
    if (result.status.id > 2) {
      return result;
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error('Execution timeout');
}
```

---

## Deployment

### Option 1: GitHub Pages (Free)

```bash
# Build site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Option 2: Netlify (Free)

```bash
# Create netlify.toml
cat > netlify.toml << EOF
[build]
  command = "mkdocs build"
  publish = "site"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
EOF

# Push to GitHub and connect to Netlify
```

### Option 3: Vercel (Free)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

---

## Summary

You now have a fully interactive MkDocs course platform with:

✅ Monaco code editor
✅ Code execution (client-side JavaScript)
✅ Progress tracking
✅ Gamification (points, badges, streaks)
✅ Beautiful Material Design theme
✅ Free hosting options

**Total setup time: 30 minutes**
**Total cost: $0**

**Next steps:**
1. Add more lessons
2. Integrate Judge0 for multi-language support
3. Add Supabase for cloud sync
4. Customize theme and branding
5. Add analytics

**Your course is ready to launch!** 🚀
