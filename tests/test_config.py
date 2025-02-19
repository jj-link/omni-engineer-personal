"""Tests for configuration module."""

import os
import pytest
from omni_core.config import Configuration, ConfigurationError, ProviderConfig

def test_provider_config_validation():
    """Test provider configuration validation."""
    config = Configuration()
    
    # Test valid provider
    provider = config.get_provider('ollama')
    assert isinstance(provider, ProviderConfig)
    assert provider.base_url == 'http://localhost:11434'
    assert provider.default_model == 'codellama'
    assert not provider.requires_key
    
    # Test invalid provider
    with pytest.raises(ConfigurationError, match="Unknown provider"):
        config.get_provider('invalid')

def test_environment_validation():
    """Test environment variable validation."""
    config = Configuration()
    
    # Clear environment variables
    if 'TAVILY_API_KEY' in os.environ:
        del os.environ['TAVILY_API_KEY']
    if 'CBORG_API_KEY' in os.environ:
        del os.environ['CBORG_API_KEY']
    
    # Test missing Tavily key
    with pytest.raises(ConfigurationError, match="TAVILY_API_KEY not found"):
        config.validate_environment()
    
    # Set Tavily key but missing CBORG key
    os.environ['TAVILY_API_KEY'] = 'test_key'
    with pytest.raises(ConfigurationError, match="CBORG_API_KEY not found"):
        config.validate_environment()
    
    # Set all required keys
    os.environ['CBORG_API_KEY'] = 'test_key'
    config.validate_environment()  # Should not raise

def test_model_update():
    """Test model update functionality."""
    config = Configuration()
    
    # Test valid model update
    config.update_provider_model('ollama', 'mistral')
    assert config.get_provider('ollama').default_model == 'mistral'
    
    # Test invalid provider
    with pytest.raises(ConfigurationError, match="Unknown provider"):
        config.update_provider_model('invalid', 'model')

def test_parameter_update():
    """Test parameter update functionality."""
    config = Configuration()
    
    # Test valid parameter updates
    config.update_provider_parameters('ollama', temperature=0.5, top_p=0.8, seed=42)
    provider = config.get_provider('ollama')
    assert provider.parameters.temperature == 0.5
    assert provider.parameters.top_p == 0.8
    assert provider.parameters.seed == 42
    
    # Test invalid temperature
    with pytest.raises(ConfigurationError, match="Temperature must be between"):
        config.update_provider_parameters('ollama', temperature=1.5)
    
    # Test invalid top_p
    with pytest.raises(ConfigurationError, match="Top-p must be between"):
        config.update_provider_parameters('ollama', top_p=-0.1)
    
    # Test invalid provider
    with pytest.raises(ConfigurationError, match="Unknown provider"):
        config.update_provider_parameters('invalid', temperature=0.5)

def test_api_key_retrieval():
    """Test API key retrieval."""
    config = Configuration()
    
    # Set required keys
    os.environ['CBORG_API_KEY'] = 'test_key'
    
    # Test key retrieval for provider requiring key
    assert config.get_api_key('cborg') == 'test_key'
    
    # Test key retrieval for provider not requiring key
    assert config.get_api_key('ollama') is None
    
    # Test invalid provider
    with pytest.raises(ConfigurationError, match="Unknown provider"):
        config.get_api_key('invalid')
    
    # Test missing required key
    del os.environ['CBORG_API_KEY']
    with pytest.raises(ConfigurationError, match="CBORG_API_KEY not found"):
        config.get_api_key('cborg')
