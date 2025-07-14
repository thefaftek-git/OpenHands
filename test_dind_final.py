import tempfile

import docker


def main():
    print('Testing Docker-in-Docker functionality...')

    # Create a temporary directory for the build
    with tempfile.TemporaryDirectory():
        # Build the runtime image with dind support enabled
        docker_client = docker.from_env()
        docker.client.DockerClient(base_url='unix://var/run/docker.sock')

        base_image = 'ubuntu:24.04'
        print(f'Using base image: {base_image}')

        # Start a container from the built image and test Docker access
        container = docker_client.containers.run(
            base_image,
            command=[
                'bash',
                '-c',
                'apt-get update && apt-get install -y docker.io && docker --version',
            ],
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
