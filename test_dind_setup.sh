#!/bin/bash
# Comprehensive Docker-in-Docker test for OpenHands

set -e  # Exit on error

echo "=== Starting Docker-in-Docker Test ==="

# Function to print messages with timestamp
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Step 1: Verify Docker daemon is accessible
log "Step 1: Verifying Docker daemon accessibility..."
docker info > /dev/null 2>&1 || { log "ERROR: Docker daemon not accessible"; exit 1; }
docker version > /dev/null 2>&1 || { log "ERROR: Docker CLI not working"; exit 1; }
log "✓ Docker daemon is accessible"

# Step 2: Verify Python and pip are available
log "Step 2: Verifying Python environment..."
python3 --version > /dev/null 2>&1 || { log "ERROR: Python not found"; exit 1; }
pip3 --version > /dev/null 2>&1 || { log "ERROR: Pip not found"; exit 1; }
log "✓ Python and pip are available"

# Step 3: Install Poetry
log "Step 3: Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 - || { log "ERROR: Failed to install Poetry"; exit 1; }
export PATH="$HOME/.local/bin:$PATH"
poetry --version > /dev/null 2>&1 || { log "ERROR: Poetry installation failed"; exit 1; }
log "✓ Poetry installed successfully"

# Step 4: Install OpenHands dependencies
log "Step 4: Installing OpenHands dependencies..."
cd /workspace/OpenHands || { log "ERROR: Could not find OpenHands directory"; exit 1; }
poetry install --only main,dev > /tmp/openhands_install.log 2>&1 || {
    log "ERROR: Failed to install OpenHands dependencies"
    cat /tmp/openhands_install.log
    exit 1;
}
log "✓ OpenHands dependencies installed"

# Step 5: Verify basic OpenHands functionality
log "Step 5: Verifying OpenHands functionality..."
python -c "
import sys
sys.path.insert(0, '/workspace/OpenHands')
try:
    from openhands.core.config import OpenHandsConfig
    config = OpenHandsConfig()
    print('OpenHands core module imported successfully')
except Exception as e:
    print(f'ERROR: Failed to import OpenHands modules: {e}')
    sys.exit(1)
" || { log "ERROR: OpenHands functionality test failed"; exit 1; }
log "✓ OpenHands functionality verified"

# Step 6: Run a simple runtime test
log "Step 6: Running basic runtime test..."
python -c "
import sys
sys.path.insert(0, '/workspace/OpenHands')
try:
    from openhands.runtime.impl.local import LocalRuntime
    from openhands.core.config import OpenHandsConfig
    config = OpenHandsConfig()
    runtime = LocalRuntime(config)
    # Test a simple command
    result = runtime.run_command('echo Hello OpenHands')
    print(f'Command result: {result}')
except Exception as e:
    print(f'ERROR: Runtime test failed: {e}')
    sys.exit(1)
" || { log "ERROR: Runtime test failed"; exit 1; }
log "✓ Basic runtime test completed"

# Step 7: Cleanup
log "Step 7: Cleaning up..."
docker system prune -f > /dev/null 2>&1 || true  # Force cleanup, ignore errors if no containers
log "✓ Cleanup completed"

echo "=== Docker-in-Docker Test Completed Successfully ==="
