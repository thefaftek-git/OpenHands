import os
from openhands.core.config import OpenHandsConfig

def test_dind_config_loading():
    """Test that dinD configuration options are properly loaded."""
    # Test default values
    config = OpenHandsConfig()
    assert config.sandbox.enable_dind == False, "enable_dind should be False by default"
    assert config.sandbox.dind_base_image is None, "dind_base_image should be None by default"
    assert config.sandbox.dind_volumes is None, "dind_volumes should be None by default"

def test_dind_config_from_env():
    """Test that dinD configuration options can be set via environment variables."""
    # Set environment variables
    os.environ['ENABLE_DIND'] = '1'
    os.environ['DIND_BASE_IMAGE'] = 'test-image:latest'
    os.environ['DIND_VOLUMES'] = '/host/path:/container/path:rw'

    try:
        config = OpenHandsConfig()
        assert config.sandbox.enable_dind == True, "enable_dind should be True when set via env"
        assert config.sandbox.dind_base_image == 'test-image:latest', "dind_base_image should match env var"
        assert config.sandbox.dind_volumes == '/host/path:/container/path:rw', "dind_volumes should match env var"
    finally:
        # Clean up environment variables
        if 'ENABLE_DIND' in os.environ:
            del os.environ['ENABLE_DIND']
        if 'DIND_BASE_IMAGE' in os.environ:
            del os.environ['DIND_BASE_IMAGE']
        if 'DIND_VOLUMES' in os.environ:
            del os.environ['DIND_VOLUMES']

def test_dind_config_from_toml():
    """Test that dinD configuration options can be set via TOML config."""
    # Create a temporary config file
    import tempfile

    config_content = '''
[sandbox]
enable_dind = true
dind_base_image = "custom-image:latest"
dind_volumes = "/host/path:/container/path:ro"
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml') as f:
        f.write(config_content)
        f.flush()

        # Set the config file path
        original_config_path = OpenHandsConfig._CONFIG_PATH
        try:
            OpenHandsConfig._CONFIG_PATH = f.name

            config = OpenHandsConfig()
            assert config.sandbox.enable_dind == True, "enable_dind should be True from TOML"
            assert config.sandbox.dind_base_image == 'custom-image:latest', "dind_base_image should match TOML"
            assert config.sandbox.dind_volumes == '/host/path:/container/path:ro', "dind_volumes should match TOML"

        finally:
            # Restore original config path
            OpenHandsConfig._CONFIG_PATH = original_config_path
