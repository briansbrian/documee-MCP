# Setup Instructions

## Prerequisites

- Python 3.12 (required)
- pip (Python package manager)

## Setup Steps

### 1. Create Virtual Environment with Python 3.12

```bash
# Windows - Use py launcher to specify Python 3.12
py -3.12 -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -c "from src.config import Settings; s = Settings(); print('Configuration loaded successfully!')"
```

### 4. Run the Server

```bash
python -m src.server
```

## Environment Variables (Optional)

You can override configuration settings using environment variables:

- `CACHE_MAX_SIZE_MB` - Override cache memory size (default: 500)
- `REDIS_URL` - Redis connection URL (default: None)
- `MAX_FILE_SIZE_MB` - Maximum file size to process (default: 10)

Example:
```bash
# Windows
set CACHE_MAX_SIZE_MB=1000
set MAX_FILE_SIZE_MB=20
python -m src.server
```

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m src.server
```
