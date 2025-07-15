#!/usr/bin/env python3

from pydantic import BaseModel, Field
import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sandbox_config():
    """Test that the new dinD configuration options work correctly."""
    print("Testing SandboxConfig...")

    try:
        from openhands.core.config.sandbox_config import SandboxConfig

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

        print("SandboxConfig test passed!")
        return True

    except Exception as e:
        print(f"Error testing SandboxConfig: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sandbox_config()
    sys.exit(0 if success else 1)
