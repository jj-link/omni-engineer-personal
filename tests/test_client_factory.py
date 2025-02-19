"""
Tests for the client factory system.
"""
import pytest
from unittest.mock import patch, Mock

# Import will be uncommented once we create the actual module
# from omni_engineer.client import ClientFactory

def test_cborg_client_creation(mock_environment, mock_args):
    """Test creation of CBORG client"""
    pytest.skip("Implementation pending")
    # factory = ClientFactory()
    # client = factory.create_client('cborg', mock_args)
    # assert client.base_url == 'https://api.cborg.lbl.gov'
    # assert client.api_key == mock_environment['CBORG_API_KEY']

def test_ollama_client_creation(mock_args):
    """Test creation of Ollama client"""
    pytest.skip("Implementation pending")
    # factory = ClientFactory()
    # client = factory.create_client('ollama', mock_args)
    # assert client.base_url == mock_args.ollama_url

def test_missing_cborg_key(monkeypatch, mock_args):
    """Test error handling when CBORG key is missing"""
    pytest.skip("Implementation pending")
    # monkeypatch.delenv('CBORG_API_KEY', raising=False)
    # factory = ClientFactory()
    # with pytest.raises(ValueError, match="Missing CBORG_API_KEY"):
    #     factory.create_client('cborg', mock_args)

def test_invalid_ollama_url(mock_args):
    """Test error handling with invalid Ollama URL"""
    pytest.skip("Implementation pending")
    # mock_args.ollama_url = "invalid-url"
    # factory = ClientFactory()
    # with pytest.raises(ValueError, match="Invalid Ollama URL"):
    #     factory.create_client('ollama', mock_args)
