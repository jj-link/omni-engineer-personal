"""
Tests for API configuration management.
"""
import os
import pytest
from omni_engineer.config import APIConfig

def test_api_config_initialization():
    """Test that APIConfig can be initialized and contains expected providers."""
    assert 'cborg' in APIConfig.PROVIDERS
    assert 'ollama' in APIConfig.PROVIDERS
    
    # Test CBORG config
    cborg_config = APIConfig.get_config('cborg')
    assert cborg_config['env_key'] == 'CBORG_API_KEY'
    assert cborg_config['base_url'] == 'https://api.cborg.lbl.gov'
    assert cborg_config['default_model'] == 'lbl/cborg-coder:latest'
    assert cborg_config['requires_key'] is True
    
    # Test Ollama config
    ollama_config = APIConfig.get_config('ollama')
    assert ollama_config['env_key'] is None
    assert ollama_config['base_url'] == 'http://localhost:11434'
    assert ollama_config['default_model'] == 'codellama'
    assert ollama_config['requires_key'] is False

def test_api_config_cborg_validation(monkeypatch):
    """Test CBORG API key validation."""
    # Test with valid API key
    monkeypatch.setenv('CBORG_API_KEY', 'test_key')
    api_key = APIConfig.get_api_key('cborg')
    assert api_key == 'test_key'
    
    # Test with missing API key
    monkeypatch.delenv('CBORG_API_KEY', raising=False)
    with pytest.raises(ValueError, match='Missing CBORG_API_KEY environment variable'):
        APIConfig.get_api_key('cborg')

def test_api_config_ollama_validation():
    """Test Ollama config validation (no API key required)."""
    api_key = APIConfig.get_api_key('ollama')
    assert api_key is None

def test_invalid_provider():
    """Test error handling for invalid provider."""
    with pytest.raises(ValueError, match='Unsupported provider'):
        APIConfig.get_config('invalid_provider')
