# Task 3: Implement dinD Health Checks

## Goal
Implement health monitoring for docker-in-docker (dinD) mode to ensure the development environment is running properly.

## Why This Matters
Health checks are crucial for:
- Early detection of container issues
- Better developer experience
- Automated monitoring in CI/CD pipelines
- Ensuring isolation and security of dinD containers

## Implementation Plan

### Phase 1: Basic Health Endpoint

1. **Add health endpoint to backend**:
   - Create a simple `/health` endpoint that returns status information
   - Include basic system metrics (CPU, memory usage)
   - Add container-specific checks if possible

2. **Modify dinD startup script**:
   - Ensure the health endpoint is accessible during development
   - Document how to access the health endpoint

### Phase 2: Container-Specific Health Checks

1. **Docker daemon health**:
   - Check if Docker daemon is running inside the container
   - Verify Docker API responsiveness

2. **Network connectivity**:
   - Test network connectivity between host and container
   - Verify that required ports are accessible

3. **Volume mounting**:
   - Check that all specified volumes are properly mounted
   - Verify write permissions to mounted volumes

### Phase 3: Advanced Monitoring (Optional)

1. **Resource usage monitoring**:
   - Track CPU, memory, disk usage of dinD containers
   - Implement alerts for resource thresholds

2. **Security checks**:
   - Verify container isolation
   - Check for potential security vulnerabilities

## Technical Implementation

### Backend Health Endpoint Example

```python
# In openhands/server/health.py (new file)
from fastapi import APIRouter
import psutil

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }
```

### Register the endpoint

```python
# In openhands/server/__init__.py
from .health import router as health_router

app.include_router(health_router, prefix="/api", tags=["health"])
```

## Testing Plan

1. **Start dinD mode**:
   ```bash
   make run-dind
   ```

2. **Access health endpoint**:
   ```
   curl http://localhost:8000/api/health
   ```

3. **Verify expected response**:
   - Status should be "healthy"
   - Resource metrics should be reasonable values

## Documentation

Add a section to the development documentation explaining:
- How to access the health endpoint
- What each status means
- Common troubleshooting steps for health issues

## Next Steps

1. Implement actual dinD container health checks if needed
2. Consider adding health check integration with frontend UI
3. Explore automated monitoring solutions for CI/CD pipelines
