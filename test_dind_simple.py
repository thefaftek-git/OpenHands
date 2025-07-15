#!/usr/bin/env python3
"""
Simple test to verify Docker-in-Docker functionality.
This script tests basic Docker operations in a container environment.
"""

import subprocess
import sys


def run_command(cmd):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"Command '{cmd}' succeeded:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed with exit code {e.returncode}:")
        print('STDOUT:', e.stdout)
        print('STDERR:', e.stderr)
        return False


def main():
    """Test Docker-in-Docker functionality."""
    print('Testing Docker-in-Docker setup...')

    # Test 1: Check if docker command is available
    if not run_command('which docker'):
        print('ERROR: Docker command not found')
        sys.exit(1)

    # Test 2: Verify Docker daemon is accessible
    if not run_command('docker info'):
        print('ERROR: Docker daemon not accessible')
        sys.exit(1)

    # Test 3: Check Docker version
    if not run_command("docker version --format '{{.Server.Version}}'"):
        print('ERROR: Could not get Docker version')
        sys.exit(1)

    # Test 4: List running containers (should be empty or show docker service)
    if not run_command('docker ps'):
        print('WARNING: Could not list running containers')

    print('All Docker-in-Docker tests passed successfully!')
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
