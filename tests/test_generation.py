"""Tests for model text generation."""
import json
from unittest.mock import patch
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
        self._content = content
        
    def json(self):
        """Return JSON content."""
        return json.loads(self._content)
    
    def raise_for_status(self):
        """Raise exception if status code is not 200."""
        if self.status_code != 200:
            raise requests.HTTPError(f"HTTP error occurred: {self.status_code}")

def test_cborg_generation(monkeypatch):
    """Test CBORG text generation."""
    monkeypatch.setenv('CBORG_API_KEY', 'test_key')
    
    mock_response = MockResponse(json.dumps({
        "choices": [{
            "message": {
                "content": "Generated text"
            }
        }]
    }))
    
    with patch('requests.post', return_value=mock_response):
        client = CBORGClient('https://api.cborg.lbl.gov', 'test_key')
        params = ModelParameters(temperature=0.7)
        
        response = client.generate("Test prompt", params)
        assert response == "Generated text"

def test_ollama_generation():
    """Test Ollama text generation."""
    mock_response = MockResponse(json.dumps({
        "response": "Generated text"
    }))
    
    with patch('requests.post', return_value=mock_response):
        client = OllamaClient('http://localhost:11434')
        params = ModelParameters(temperature=0.7)
        
        response = client.generate("Test prompt", params)
        assert response == "Generated text"

def test_generation_error_handling():
    """Test error handling during generation."""
    mock_response = MockResponse("", status_code=500)
    
    with patch('requests.post', return_value=mock_response):
        client = CBORGClient('https://api.cborg.lbl.gov', 'test_key')
        params = ModelParameters()
        
        with pytest.raises(requests.HTTPError):
            client.generate("Test prompt", params)

def test_generation_with_all_parameters():
    """Test generation with all available parameters."""
    mock_response = MockResponse(json.dumps({
        "response": "Generated text"
    }))
    
    with patch('requests.post', return_value=mock_response) as mock_post:
        client = OllamaClient('http://localhost:11434')
        params = ModelParameters(
            temperature=0.5,
            top_p=0.9,
            seed=42,
            model="codellama:latest"
        )
        
        response = client.generate("Test prompt", params)
        assert response == "Generated text"
        
        # Verify all parameters were passed correctly
        call_args = mock_post.call_args
        request_json = call_args.kwargs['json']
        assert request_json['options']['temperature'] == 0.5
        assert request_json['options']['top_p'] == 0.9
        assert request_json['options']['seed'] == 42
        assert request_json['model'] == "codellama:latest"

def test_cborg_generation_parameter_passing():
    """Test that parameters are correctly passed to CBORG API."""
    mock_response = MockResponse(json.dumps({
        "choices": [{
            "message": {
                "content": "Generated text"
            }
        }]
    }))
    
    with patch('requests.post', return_value=mock_response) as mock_post:
        client = CBORGClient('https://api.cborg.lbl.gov', 'test_key')
        params = ModelParameters(
            temperature=0.5,
            top_p=0.9,
            seed=42,
            model="lbl/cborg-coder:custom"
        )
        
        response = client.generate("Test prompt", params)
        assert response == "Generated text"
        
        # Verify all parameters were passed correctly
        call_args = mock_post.call_args
        request_json = call_args.kwargs['json']
        assert request_json['temperature'] == 0.5
        assert request_json['top_p'] == 0.9
        assert request_json['seed'] == 42
        assert request_json['model'] == "lbl/cborg-coder:custom"
        
        # Verify headers
        headers = call_args.kwargs['headers']
        assert headers['Authorization'] == 'Bearer test_key'
        assert headers['Content-Type'] == 'application/json'

def test_invalid_base_url():
    """Test initialization with invalid base URL."""
    with pytest.raises(ValueError, match="Invalid URL format"):
        CBORGClient("not-a-url", "test_key")
    
    with pytest.raises(ValueError, match="Invalid URL format"):
        OllamaClient("also-not-a-url")

def test_malformed_response():
    """Test handling of malformed API responses."""
    # Test CBORG malformed response
    mock_response = MockResponse(json.dumps({
        "choices": []  # Missing expected data
    }))
    
    with patch('requests.post', return_value=mock_response):
        client = CBORGClient('https://api.cborg.lbl.gov', 'test_key')
        with pytest.raises(KeyError):
            client.generate("Test prompt", ModelParameters())
    
    # Test Ollama malformed response
    mock_response = MockResponse(json.dumps({
        "not_response": "data"  # Wrong key
    }))
    
    with patch('requests.post', return_value=mock_response):
        client = OllamaClient('http://localhost:11434')
        with pytest.raises(KeyError):
            client.generate("Test prompt", ModelParameters())
