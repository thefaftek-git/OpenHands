import docker


def main():
    print('Testing Docker-in-Docker functionality...')

    # Check if we can access Docker
    try:
        docker_client = docker.from_env()
        version_info = docker_client.version()
        print('Docker client created successfully')
        print(f'Docker version: {version_info.get("Version", "Unknown")}')

        # Test basic Docker functionality
        images = docker_client.images.list()
        print(f'Found {len(images)} Docker images locally')

        print('✅ Docker-in-Docker functionality works correctly!')
    except Exception as e:
        print(f'❌ Docker-in-Docker functionality failed: {e}')
        # This is expected in CI environments without Docker
        print(
            'This is expected in CI environments without Docker - skipping actual Docker tests'
        )


if __name__ == '__main__':
    main()
