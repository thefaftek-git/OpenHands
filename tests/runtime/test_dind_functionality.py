import tempfile
from pathlib import Path

import docker

from openhands.runtime.builder import DockerRuntimeBuilder
from openhands.runtime.utils.runtime_build import build_runtime_image


def test_docker_in_docker_functionality():
    """Test that Docker-in-Docker is properly configured and functional."""

    # Create a temporary directory for the build
    with tempfile.TemporaryDirectory() as temp_dir:
        # Build the runtime image with dind support enabled
        docker_client = docker.from_env()
        builder = DockerRuntimeBuilder(docker_client)

        base_image = 'ubuntu:24.04'
        image_name = build_runtime_image(
            base_image,
            builder,
            build_folder=Path(temp_dir),
            dry_run=False,
            force_rebuild=True,
        )

        # Start a container from the built image and test Docker access
        container = docker_client.containers.run(
            image_name,
            command=['bash', '-c', 'docker --version && docker ps'],
            detach=True,
            tty=True,
            remove=True,
            privileged=True,  # Required for dind
            volumes={
                '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}
            },
        )

        # Get logs to verify Docker is accessible
        logs = container.logs().decode('utf-8')
        print(f'Container logs: {logs}')

        assert 'Docker version' in logs, (
            f"Expected 'Docker version' in logs, got: {logs}"
        )
        assert 'Cannot connect to the Docker daemon' not in logs, (
            'Docker daemon connection failed'
        )

        # Test that we can run a simple Docker command inside the container
        test_container = docker_client.containers.run(
            image_name,
            command=['bash', '-c', 'docker run --rm hello-world'],
            detach=True,
            tty=True,
            remove=True,
            privileged=True,
            volumes={
                '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}
            },
        )

        test_logs = test_container.logs().decode('utf-8')
        print(f'Test container logs: {test_logs}')
        assert 'Hello from Docker!' in test_logs, (
            f"Expected 'Hello from Docker!' in logs, got: {test_logs}"
        )


if __name__ == '__main__':
    test_docker_in_docker_functionality()
