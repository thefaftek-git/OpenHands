# Task 4: Documentation for dinD Support

## Goal
Create comprehensive documentation for the docker-in-docker (dinD) development environment.

## Target Audiences
1. OpenHands developers who want to use dinD for local development
2. Contributors working on CI/CD pipelines that use dinD
3. Users who want to understand how dinD works in OpenHands

## Documentation Plan

### 1. User Guide: Getting Started with dinD

**File**: `docs/development/dind_guide.md`

#### Sections:
- **Introduction**: What is dinD and why use it?
- **Prerequisites**: Requirements (Docker, WSL for Windows users)
- **Quick Start**: Basic usage instructions
- **Environment Variables**: Configuration options
- **Troubleshooting**: Common issues and solutions

### 2. Developer Guide: Advanced Usage

**File**: `docs/development/dind_advanced.md`

#### Sections:
- **Customization**: How to customize dinD containers
- **Performance Tuning**: Optimizing resource usage
- **Security Considerations**: Best practices for secure dinD usage
- **Integration**: Using dinD with other tools

### 3. Reference Guide: Configuration Options

**File**: `docs/reference/dind_config.md`

#### Sections:
- **Environment Variables**: Complete list with descriptions
- **Default Values**: What settings are used by default
- **Examples**: Common configuration scenarios

## Documentation Content Examples

### Quick Start Section

```markdown
## Getting Started with dinD

dinD (docker-in-docker) allows you to run OpenHands development without requiring Docker on your local machine.

### Prerequisites

- Docker installed on your host system
- Basic OpenHands setup completed (`make build`)

### Quick Start

1. **Start dinD mode**:
   ```bash
   cd /home/nathan/Repos/OpenHands/workspace/OpenHands
   make run-dind
   ```

2. **Access the application**:
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API: [http://localhost:8000](http://localhost:8000)

### Common Environment Variables

- `ENABLE_DIND=1`: Enable dinD mode
- `DIND_BASE_IMAGE="ubuntu:20.04"`: Custom base image
- `DIND_VOLUMES="/host/path:/container/path"`: Mount host volumes
```

### Troubleshooting Section

```markdown
## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Backend not starting | Check uvicorn logs for errors. Ensure port 8000 is available. |
| Frontend fails to load | Check `/tmp/openhands-frontend.log` for errors. Verify node modules are installed. |
| Docker daemon issues | Make sure Docker is running on the host and has proper permissions. |
| Windows compatibility | Use WSL2 with Ubuntu distribution for best results. |

### Advanced Debugging

For detailed debugging, you can access container logs:

```bash
# Get list of running containers
docker ps

# View logs for a specific container
docker logs <container_id>
```
```

## Implementation Plan

1. **Create documentation files** in the appropriate directories
2. **Link to existing documentation**: Update `README.md` and other main docs to reference dinD guide
3. **Add examples**: Include real-world usage scenarios and code snippets
4. **Review with team**: Get feedback from other developers on clarity and completeness

## Next Steps

1. Implement actual health checks (Task 3)
2. Test the documentation with new users
3. Consider adding video tutorials or interactive guides
