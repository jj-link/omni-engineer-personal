"""Tests for streaming response handling."""
import json
from unittest.mock import patch, Mock
import pytest
import requests

from omni_engineer.client import (
    ClientFactory,
    ModelParameters,
    CBORGClient,
    OllamaClient
)

class MockResponse:
    """Mock response object for requests."""
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code
        self._content_iter = iter(content)
    
    def iter_lines(self):
        """Iterate over content lines."""
        return self._content_iter
    
    def raise_for_status(self):
        """Raise exception if status code is not 200."""
        if self.status_code != 200:
            raise requests.HTTPError(f"HTTP error occurred: {self.status_code}")

def test_cborg_streaming(monkeypatch):
    """Test CBORG streaming response handling"""
    monkeypatch.setenv('CBORG_API_KEY', 'test_key')
    
    # Mock streaming response data
    mock_data = [
        json.dumps({"choices": [{"delta": {"content": "Hello "}}]}).encode(),
        json.dumps({"choices": [{"delta": {"content": "world!"}}]}).encode()
    ]
    
    mock_response = MockResponse(mock_data)
    
    with patch('requests.post', return_value=mock_response):
        client = CBORGClient('https://api.cborg.lbl.gov', 'test_key')
        params = ModelParameters(temperature=0.7)
        
        response = list(client.stream("Test prompt", params))
        assert len(response) == 2
        assert json.loads(response[0])["choices"][0]["delta"]["content"] == "Hello "
        assert json.loads(response[1])["choices"][0]["delta"]["content"] == "world!"

def test_ollama_streaming(monkeypatch):
    """Test Ollama streaming response handling"""
    # Mock streaming response data
    mock_data = [
        json.dumps({"response": "Hello "}).encode(),
        json.dumps({"response": "world!"}).encode()
    ]
    
    mock_response = MockResponse(mock_data)
    
    with patch('requests.post', return_value=mock_response):
        client = OllamaClient('http://localhost:11434')
        params = ModelParameters(temperature=0.7)
        
        response = list(client.stream("Test prompt", params))
        assert len(response) == 2
        assert json.loads(response[0])["response"] == "Hello "
        assert json.loads(response[1])["response"] == "world!"

def test_stream_error_handling():
    """Test error handling during streaming"""
    mock_response = MockResponse([], status_code=500)
    
    with patch('requests.post', return_value=mock_response):
        client = CBORGClient('https://api.cborg.lbl.gov', 'test_key')
        params = ModelParameters()
        
        with pytest.raises(requests.HTTPError):
            list(client.stream("Test prompt", params))

def test_stream_with_all_parameters():
    """Test streaming with all available parameters"""
    mock_data = [json.dumps({"response": "test"}).encode()]
    mock_response = MockResponse(mock_data)
    
    with patch('requests.post', return_value=mock_response):
        client = OllamaClient('http://localhost:11434')
        params = ModelParameters(
            temperature=0.5,
            top_p=0.9,
            seed=42,
            model="codellama:latest"
        )
        
        # Verify no errors when using all parameters
        response = list(client.stream("Test prompt", params))
        assert len(response) == 1
        assert json.loads(response[0])["response"] == "test"
