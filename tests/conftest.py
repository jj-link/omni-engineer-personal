"""
Test configuration and fixtures for the omni-engineer test suite.
"""
import pytest
from unittest.mock import Mock, patch
import os
import logging

def pytest_configure():
    """Configure test environment."""
    # Disable all logging during tests
    logging.getLogger().setLevel(logging.ERROR)
    
    # Disable asyncio warnings
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)

@pytest.fixture
def mock_cborg_response():
    """Mock successful CBORG API response"""
    return {
        "id": "mock-completion-id",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "lbl/cborg-coder:latest",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Mock response content"
            },
            "finish_reason": "stop"
        }]
    }

@pytest.fixture
def mock_ollama_response():
    """Mock successful Ollama API response"""
    return {
        "model": "codellama",
        "created_at": "2024-02-19T12:00:00.000Z",
        "message": {
            "role": "assistant",
            "content": "Mock response content"
        },
        "done": True
    }

@pytest.fixture
def mock_environment(monkeypatch):
    """Setup mock environment variables"""
    mock_env = {
        "CBORG_API_KEY": "mock-cborg-key",
    }
    for key, value in mock_env.items():
        monkeypatch.setenv(key, value)
    return mock_env

@pytest.fixture
def mock_args():
    """Mock command line arguments"""
    return Mock(
        api="cborg",
        model="lbl/cborg-coder:latest",
        temperature=0.7,
        top_p=1.0,
        seed=None,
        ollama_url="http://localhost:11434"
    )

@pytest.fixture
def mock_stream_response():
    """Mock streaming response for both CBORG and Ollama"""
    class MockStreamResponse:
        def __init__(self, provider="cborg"):
            self.provider = provider
            self.chunks = [
                {"choices": [{"delta": {"content": "Hello"}}]},
                {"choices": [{"delta": {"content": " world"}}]},
                {"choices": [{"delta": {"content": "!"}}]}
            ] if provider == "cborg" else [
                {"message": {"content": "Hello"}},
                {"message": {"content": " world"}},
                {"message": {"content": "!"}}
            ]
            
        def __iter__(self):
            return iter(self.chunks)
    
    return MockStreamResponse
