import tempfile
from pathlib import Path

import docker

from openhands.runtime.builder import DockerRuntimeBuilder
from openhands.runtime.utils.runtime_build import build_runtime_image


def main():
    print('Testing Docker-in-Docker functionality...')

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

        print(f'Built image: {image_name}')

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

        if 'Docker version' in logs:
            print('✅ Docker-in-Docker functionality works correctly!')
        else:
            print('❌ Docker-in-Docker functionality failed')


if __name__ == '__main__':
    main()
