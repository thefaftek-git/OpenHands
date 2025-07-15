# OpenHands Docker-in-Docker (dinD) Development Mode

## Overview

OpenHands supports **docker-in-docker (dinD)** mode for development, allowing you to run the application without requiring a local Docker installation. This is particularly useful when:

- You're developing on a system where Docker cannot be installed
- You want isolated development environments
- You need consistent runtime behavior across different machines

## How It Works

dinD mode leverages Docker containers to provide all necessary runtime capabilities, including:
- Containerized execution environment
- Isolated file systems and dependencies
- Built-in Docker daemon for sandbox operations

## Configuration Options

### 1. Enable dinD Mode

To enable dinD mode, set the following configuration:

```toml
[sandbox]
enable_dind = true
```

Alternatively, use the environment variable:
```bash
export ENABLE_DIND=1
```

### 2. Customize Base Image (Optional)

Specify a custom Docker image for the dinD containers:
```toml
[sandbox]
dind_base_image = "your-custom-image:latest"
```

Or via environment variable:
```bash
export DIND_BASE_IMAGE="your-custom-image:latest"
```

### 3. Add Volume Mounts (Optional)

Mount additional directories into the dinD container:
```toml
[sandbox]
dind_volumes = "/host/path:/container/path:rw,/another/path:/container/another:ro"
```

Or via environment variable:
```bash
export DIND_VOLUMES="/host/path:/container/path:rw,/another/path:/container/another:ro"
```

## Usage Instructions

### Method 1: Using Makefile Target (Recommended)

The easiest way to run OpenHands in dinD mode is using the dedicated Makefile target:

```bash
make run-dind
```

This command:
- Sets up the appropriate environment variables
- Starts the backend in a privileged Docker container with dinD capabilities
- Launches the frontend interface

### Method 2: Manual Setup

For advanced users who want more control, you can manually configure dinD mode:

1. Set the required environment variables:
```bash
export RUNTIME=dind
export ENABLE_DIND=1
```

2. Start the backend:
```bash
cd containers/dev && ./dev.sh
```

3. Start the frontend (in a separate terminal):
```bash
cd frontend && npm run dev -- --port 3001 --host 0.0.0.0
```

## Environment Variables

The following environment variables control dinD behavior:

- `RUNTIME=dind`: Selects the docker-in-docker runtime mode
- `ENABLE_DIND=1`: Enables dinD mode (alternative to config.toml)
- `DIND_BASE_IMAGE`: Custom base image for dinD containers
- `DIND_VOLUMES`: Additional volume mounts for dinD containers

## Benefits of Using dinD Mode

1. **No Local Docker Requirement**: Develop without installing Docker on your host system
2. **Isolated Environment**: Consistent development experience across different machines
3. **Built-in Dependencies**: All required tools and libraries are pre-installed in the container
4. **Easy Setup**: Simple one-command setup with `make run-dind`

## Known Limitations

1. **Performance**: dinD mode may have slightly slower performance due to container nesting
2. **Resource Usage**: Requires more system resources (CPU, memory)
3. **Network Configuration**: Some network-intensive operations may behave differently
4. **Not Suitable for Production**: dinD is intended for development only

## Troubleshooting

### Common Issues and Solutions

1. **Permission Denied Errors**:
   - Ensure you're running with sufficient privileges: `sudo make run-dind`
   - Verify Docker daemon is accessible on your host system

2. **Port Conflicts**:
   - The default port for dinD mode is 3000; change it if needed:
     ```bash
     export BACKEND_PORT=4000
     ```

3. **Volume Mount Issues**:
   - Verify paths exist and are accessible
   - Check Docker permissions on mounted directories

### Viewing Logs

To debug issues, check the log files:

```bash
# View backend logs in dinD container
docker logs openhands-dev

# View frontend logs (separate terminal)
cd frontend && npm run dev
```

## Best Practices

1. **Use `make run-dind`**: The recommended way to start OpenHands in dinD mode
2. **Keep Configuration Simple**: Start with default settings, then customize as needed
3. **Monitor Resource Usage**: dinD containers can be resource-intensive
4. **Test Locally First**: Verify your development works locally before using dinD

## Examples

### Basic Usage

```bash
# Start OpenHands in dinD mode with all defaults
make run-dind
```

### Custom Configuration

```bash
# Use a custom base image and add volume mounts
export DIND_BASE_IMAGE="ubuntu:22.04"
export DIND_VOLUMES="/my/code:/workspace:rw,/my/data:/data:ro"
make run-dind
```

## Related Documentation

- [Main OpenHands Configuration](config.template.toml)
- [Docker Development Guide](dev.md)
- [Troubleshooting Common Issues](troubleshooting.md)

---

This documentation provides comprehensive guidance for using OpenHands in docker-in-docker mode. For support or additional features, please open an issue in the repository.
