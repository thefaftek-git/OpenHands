# OpenHands Local Development and Running Guide

This document provides a comprehensive guide for building and running OpenHands locally in your development environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Build Process](#build-process)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Environment Variables](#environment-variables)
10. [Port Configuration](#port-configuration)

## Prerequisites

Before setting up OpenHands, ensure you have the following dependencies installed:

### Required Software

- **Operating System**: Linux, macOS, or Windows Subsystem for Linux (WSL) [Ubuntu >= 22.04]
- **Python**: Version 3.12 (exactly)
- **Node.js**: Version 22.x or later
- **Docker**: Latest stable version with daemon running
- **Poetry**: Version 1.8 or later for Python dependency management
- **npm**: Comes with Node.js installation
- **Git**: For version control

### System-Specific Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install build-essential python3.12-dev netcat-openbsd docker.io
sudo service docker start
```

#### WSL (Windows Subsystem for Linux)
```bash
sudo apt-get install netcat-openbsd
```

#### macOS
Ensure Docker Desktop is installed and running. Make sure to allow the default Docker socket to be used from advanced settings.

## System Requirements

### Hardware Requirements
- **RAM**: Minimum 8GB, recommended 16GB or more
- **CPU**: Multi-core processor recommended
- **Storage**: At least 5GB free space for dependencies and build artifacts
- **Network**: Stable internet connection for downloading dependencies

### Development Environment
- Terminal/Command line access
- Text editor or IDE (VS Code, PyCharm, etc.)
- Web browser for testing the frontend

## Build Process

### 1. Install Pre-commit Hooks

**Important**: Always run this first to ensure code quality standards:

```bash
make install-pre-commit-hooks
```

### 2. Full Build

The complete build process includes environment setup, dependency installation, and frontend compilation:

```bash
make build
```

This command performs the following steps:
- Checks system dependencies (Python, Node.js, Docker, Poetry, tmux)
- Creates Python virtual environment using Poetry
- Installs Python dependencies (443+ packages including ML/AI libraries)
- Installs Node.js dependencies (1268+ packages)
- Installs Playwright browser automation tools
- Builds the React frontend for production
- Sets up pre-commit hooks

### 3. Build Components

You can also build individual components:

```bash
# Install Python dependencies only
make install-python-dependencies

# Install frontend dependencies only
make install-frontend-dependencies

# Build frontend only
make build-frontend
```

### Build Time Expectations

- **Full build**: 10-15 minutes (depending on internet speed and system performance)
- **Python dependencies**: 8-12 minutes (includes large ML libraries like PyTorch)
- **Frontend dependencies**: 1-2 minutes
- **Frontend build**: 1-2 minutes

## Configuration

### Basic Configuration

Create a basic configuration file:

```bash
make setup-config-basic
```

This creates a `config.toml` file with minimal settings:
```toml
[core]
workspace_base="./workspace"
```

### Advanced Configuration

For interactive configuration with LLM settings:

```bash
make setup-config
```

This will prompt you for:
- Workspace directory path
- LLM model name (e.g., gpt-4o, claude-sonnet-4)
- LLM API key
- LLM base URL (for local models)

### Configuration Priority

Settings are applied in this order (highest to lowest priority):
1. Environment variables
2. config.toml file values
3. Default application values

## Running the Application

### Option 1: Run Complete Application

Start both backend and frontend servers:

```bash
make run
```

This will:
- Start the backend server on http://127.0.0.1:3000
- Start the frontend development server on http://127.0.0.1:3001
- Open the application in your default browser

### Option 2: Run Servers Individually

#### Backend Only
```bash
make start-backend
```
- Runs on http://127.0.0.1:3000
- FastAPI/Uvicorn server with auto-reload
- API endpoints available at http://127.0.0.1:3000/docs

#### Frontend Only
```bash
make start-frontend
```
- Runs on http://127.0.0.1:3001
- Vite development server with hot reload
- Automatically connects to backend on port 3000

### Option 3: Docker-based Development

#### Run in Docker
```bash
make docker-run
```

#### Develop in Docker Container
```bash
make docker-dev
```

## Development Workflow

### Making Code Changes

#### Backend Changes (Python)
1. Make changes to files in the `openhands/` directory
2. Backend server automatically reloads (if started with `make start-backend`)
3. Run linting: `make lint-backend`
4. Run tests: `poetry run pytest tests/unit/test_*.py`

#### Frontend Changes (React/TypeScript)
1. Make changes to files in the `frontend/src/` directory
2. Frontend server automatically reloads with hot module replacement
3. Run linting: `make lint-frontend`
4. Run tests: `make test-frontend`

### Pre-commit Checks

Before committing code, ensure all checks pass:

```bash
# Run all linters
make lint

# Run specific linters
make lint-backend
make lint-frontend
```

## Testing

### Frontend Tests
```bash
make test-frontend
```

### Unit Tests
```bash
poetry run pytest tests/unit/test_*.py
```

### End-to-End Tests
```bash
cd frontend && npm run test:e2e
```

## Troubleshooting

### Common Issues and Solutions

#### Docker Not Running
**Error**: "Docker is not installed" or connection errors
**Solution**: 
```bash
sudo service docker start
# or on macOS/Windows: Start Docker Desktop
```

#### Python Version Issues
**Error**: "Python 3.12 is not installed"
**Solution**: Install Python 3.12 exactly:
```bash
# Ubuntu/Debian
sudo apt install python3.12 python3.12-dev

# Using conda/mamba
mamba install python=3.12
```

#### Node.js Version Issues
**Error**: "Node.js 22.x or later is required"
**Solution**: Install Node.js 22+:
```bash
# Using NodeJS official installer
# or via package manager
# or using conda/mamba
mamba install conda-forge::nodejs
```

#### Poetry Not Found
**Error**: "Poetry is not installed"
**Solution**:
```bash
curl -sSL https://install.python-poetry.org | python3.12 -
# Add Poetry to PATH as instructed
```

#### Frontend Build Failures
**Error**: npm install or build failures
**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Port Already in Use
**Error**: "Address already in use"
**Solution**:
```bash
# Find and kill processes using ports 3000/3001
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:3001 | xargs kill -9
```

#### WSL-specific Issues
**Error**: File watching not working
**Solution**: The build process automatically detects WSL and uses polling for file watching.

### Debug Mode

Enable debug logging for LLM interactions:
```bash
export DEBUG=1
make start-backend
```

Logs will be stored in `logs/llm/CURRENT_DATE/` directory.

## Environment Variables

### Key Environment Variables

```bash
# Backend Configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=3000

# Frontend Configuration
FRONTEND_HOST=127.0.0.1
FRONTEND_PORT=3001
VITE_BACKEND_HOST=127.0.0.1:3000

# Development
DEBUG=1                    # Enable debug logging
LOG_ALL_EVENTS=true       # Log all events

# Runtime Configuration
WORKSPACE_BASE=./workspace        # Deprecated, use RUNTIME_MOUNT
RUNTIME_MOUNT=/host/path:/workspace:rw  # Mount host directory

# Docker Configuration
SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik

# Build Configuration
INSTALL_PLAYWRIGHT=true   # Install Playwright (default: true)
POETRY_GROUP=main         # Install specific Poetry group
```

### Frontend-specific Variables

```bash
VITE_BACKEND_HOST=127.0.0.1:3000
VITE_USE_TLS=false
VITE_INSECURE_SKIP_VERIFY=false
VITE_FRONTEND_PORT=3001
VITE_MOCK_API=false
VITE_MOCK_SAAS=false
VITE_WATCH_USE_POLLING=true  # For WSL environments
```

## Port Configuration

### Default Ports

- **Backend**: 3000 (FastAPI/Uvicorn)
- **Frontend**: 3001 (Vite dev server)
- **Production**: 3000 (serves both backend API and frontend static files)

### Custom Port Configuration

```bash
# Run with custom ports
make run BACKEND_HOST="0.0.0.0" BACKEND_PORT="8000" FRONTEND_PORT="8001"

# For cloud/remote development
make openhands-cloud-run  # Uses ports 12000 and 12001
```

### Accessing the Application

Once running:
- **Main Application**: http://localhost:3001 (development) or http://localhost:3000 (production)
- **Backend API Documentation**: http://localhost:3000/docs
- **Health Check**: http://localhost:3000/health

## Advanced Topics

### Using Existing Docker Images

To speed up development, use pre-built runtime images:

```bash
export SANDBOX_RUNTIME_CONTAINER_IMAGE=ghcr.io/all-hands-ai/runtime:0.39-nikolaik
```

### Microagents

OpenHands supports microagents for specialized tasks. See the `microagents/` directory for available microagents and documentation on creating custom ones.

### Multiple Model Support

Configure different LLM providers in the UI or via environment variables:
- OpenAI GPT models
- Anthropic Claude models  
- Google Gemini models
- Local models via Ollama or similar

## Getting Help

### Available Commands

```bash
make help  # Show all available make targets
```

### Documentation Resources

- **Main README**: `/README.md` - Project overview and quick start
- **Development Guide**: `/Development.md` - Detailed development instructions
- **Contributing Guide**: `/CONTRIBUTING.md` - Contribution guidelines
- **Frontend README**: `/frontend/README.md` - Frontend-specific documentation
- **Backend README**: `/openhands/README.md` - Backend implementation details

### Community Support

- **Slack**: [Join OpenHands Slack](https://join.slack.com/t/openhands-ai/shared_invite/zt-34zm4j0gj-Qz5kRHoca8DFCbqXPS~f_A)
- **Discord**: [Join Discord Server](https://discord.gg/ESHStjSjD4)
- **GitHub Issues**: [Report bugs or request features](https://github.com/All-Hands-AI/OpenHands/issues)

---

## Sources and References

This documentation was created by analyzing the following components of the OpenHands repository:

1. **Makefile** (`/workspace/OpenHands/Makefile`) - Build and development commands
2. **Development.md** (`/workspace/OpenHands/Development.md`) - Official development guide
3. **README.md** (`/workspace/OpenHands/README.md`) - Main project documentation
4. **pyproject.toml** (`/workspace/OpenHands/pyproject.toml`) - Python dependencies and project configuration
5. **package.json** (`/workspace/OpenHands/frontend/package.json`) - Frontend dependencies and scripts
6. **Build Process Execution** - Direct experience running `make build` and `make run` commands
7. **Server Startup Logs** - Analysis of actual backend and frontend startup processes

The guide reflects the actual build and runtime behavior observed during testing on a Linux environment with all dependencies properly installed.