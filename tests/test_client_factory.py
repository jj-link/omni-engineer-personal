"""
Tests for the client factory system.
"""
import os
from dataclasses import dataclass
import pytest
from unittest.mock import patch

from omni_engineer.client import ClientFactory, CBORGClient, OllamaClient

@dataclass
class MockArgs:
    """Mock command line arguments."""
    ollama_url: str = "http://localhost:11434"

def test_cborg_client_creation(monkeypatch):
    """Test creation of CBORG client"""
    monkeypatch.setenv('CBORG_API_KEY', 'test_key')
    args = MockArgs()
    
    client = ClientFactory.create_client('cborg', args)
    assert isinstance(client, CBORGClient)
    assert client.base_url == 'https://api.cborg.lbl.gov'
    assert client.api_key == 'test_key'
    assert client.headers['Authorization'] == 'Bearer test_key'

def test_ollama_client_creation():
    """Test creation of Ollama client"""
    args = MockArgs()
    client = ClientFactory.create_client('ollama', args)
    
    assert isinstance(client, OllamaClient)
    assert client.base_url == args.ollama_url
    assert client.api_key is None

def test_missing_cborg_key(monkeypatch):
    """Test error handling when CBORG key is missing"""
    monkeypatch.delenv('CBORG_API_KEY', raising=False)
    args = MockArgs()
    
    with pytest.raises(ValueError, match='Missing CBORG_API_KEY environment variable'):
        ClientFactory.create_client('cborg', args)

def test_invalid_ollama_url():
    """Test error handling with invalid Ollama URL"""
    args = MockArgs(ollama_url="invalid-url")
    
    with pytest.raises(ValueError, match='Invalid URL'):
        ClientFactory.create_client('ollama', args)
