#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/nathan/Repos/OpenHands/workspace/OpenHands')

try:
    from openhands.core.config.sandbox_config import SandboxConfig

    # Check if the fields exist
    print("Fields in SandboxConfig:")
    for field_name in dir(SandboxConfig):
        if not field_name.startswith('_'):
            print(f"  - {field_name}")

    # Try to create an instance and check the fields
    config = SandboxConfig()
    print("\nField values:")
    print(f"enable_dind: {getattr(config, 'enable_dind', 'NOT FOUND')}")
    print(f"dind_base_image: {getattr(config, 'dind_base_image', 'NOT FOUND')}")
    print(f"dind_volumes: {getattr(config, 'dind_volumes', 'NOT FOUND')}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


from openhands.core.config.sandbox_config import SandboxConfig, OpenHandsConfig

def test_sandbox_config():
    """Test that the new dinD configuration options work correctly."""
    print("Testing SandboxConfig...")

    # Test default values
    config = SandboxConfig()
    print(f"Default enable_dind: {config.enable_dind}")
    print(f"Default dind_base_image: {config.dind_base_image}")
    print(f"Default dind_volumes: {config.dind_volumes}")

    # Test custom values
    custom_config = SandboxConfig(
        enable_dind=True,
        dind_base_image="ubuntu:20.04",
        dind_volumes="/host/path:/container/path:rw"
    )
    print(f"Custom enable_dind: {custom_config.enable_dind}")
    print(f"Custom dind_base_image: {custom_config.dind_base_image}")
    print(f"Custom dind_volumes: {custom_config.dind_volumes}")

    # Test that it's included in OpenHandsConfig
    openhands_config = OpenHandsConfig()
    print(f"OpenHandsConfig sandbox.enable_dind: {openhands_config.sandbox.enable_dind}")
    print("SandboxConfig test passed!")

if __name__ == "__main__":
    test_sandbox_config()

