"""Tests for response handling module."""

import json
import pytest
import aiohttp
from unittest.mock import patch, AsyncMock, MagicMock
from omni_core.response import (
    RetryConfig,
    with_retries,
    validate_json_response,
    validate_ollama_response,
    make_request,
    ResponseError
)

@pytest.mark.asyncio
async def test_json_response_validation():
    """Test JSON response validation."""
    # Test valid JSON response
    mock_response = AsyncMock()
    mock_response.json.return_value = {"key": "value"}
    
    result = await validate_json_response(mock_response)
    assert result == {"key": "value"}
    
    # Test invalid JSON
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "{invalid}", 0)
    mock_response.text.return_value = "{invalid}"
    mock_response.status = 200
    mock_response.content_type = "application/json"
    
    with pytest.raises(ResponseError) as exc:
        await validate_json_response(mock_response)
    assert "Invalid JSON response" in str(exc.value)
    assert exc.value.details["status"] == 200
    assert exc.value.details["content_type"] == "application/json"

def test_ollama_response_validation():
    """Test Ollama response format validation."""
    # Test valid models response
    data = {
        "models": [
            {"name": "codellama"},
            {"name": "mistral"}
        ]
    }
    validate_ollama_response(data)  # Should not raise
    
    # Test valid chat response
    data = {
        "response": "Hello, how can I help you?"
    }
    validate_ollama_response(data)  # Should not raise
    
    # Test invalid models response
    data = {
        "models": "not a list"
    }
    with pytest.raises(ResponseError) as exc:
        validate_ollama_response(data)
    assert "Invalid Ollama models response" in str(exc.value)
    
    # Test invalid model format
    data = {
        "models": [
            "not a dict"
        ]
    }
    with pytest.raises(ResponseError) as exc:
        validate_ollama_response(data)
    assert "Invalid Ollama model format" in str(exc.value)
    
    # Test invalid chat response
    data = {
        "response": {"not": "a string"}
    }
    with pytest.raises(ResponseError) as exc:
        validate_ollama_response(data)
    assert "Invalid Ollama chat response" in str(exc.value)
    
    # Test unknown response format
    data = {
        "unknown": "field"
    }
    with pytest.raises(ResponseError) as exc:
        validate_ollama_response(data)
    assert "Unknown Ollama response format" in str(exc.value)

@pytest.mark.asyncio
async def test_request_retries():
    """Test request retry behavior."""
    retry_config = RetryConfig(
        max_retries=3,
        initial_delay=0.1,  # Short delay for tests
        max_delay=0.2,
        backoff_factor=2.0,
        retry_on_status=(500, 503)
    )
    
    # Test successful request after retry
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"key": "value"}
    mock_response.__aenter__.return_value = mock_response
    
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    
    # First call fails, second succeeds
    mock_session.get.side_effect = [
        aiohttp.ClientError("First attempt failed"),
        mock_response
    ]
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        @with_retries(retry_config)
        async def test_func():
            async with aiohttp.ClientSession() as session:
                async with await session.get("http://test.url") as response:
                    return await response.json()
        
        result = await test_func()
        assert result == {"key": "value"}
    
    # Test max retries exceeded
    mock_session.get.side_effect = [
        aiohttp.ClientError("Failed attempt")
        for _ in range(retry_config.max_retries)
    ]
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(aiohttp.ClientError) as exc:
            await test_func()
        assert "Failed attempt" in str(exc.value)

@pytest.mark.asyncio
async def test_make_request():
    """Test make_request function."""
    # Test successful request
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "models": [
            {"name": "codellama"}
        ]
    }
    mock_response.__aenter__.return_value = mock_response
    
    mock_session = AsyncMock()
    mock_session.get.return_value = mock_response
    mock_session.__aenter__.return_value = mock_session
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await make_request(
            "GET",
            "http://test.url",
            "ollama"
        )
        assert result["models"][0]["name"] == "codellama"
    
    # Test failed request
    mock_response.status = 500
    mock_response.reason = "Internal Server Error"
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(ResponseError) as exc:
            await make_request(
                "GET",
                "http://test.url",
                "ollama"
            )
        assert "Request failed with status 500" in str(exc.value)
        assert exc.value.details["reason"] == "Internal Server Error"
    
    # Test invalid provider
    mock_response.status = 200
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(ValueError) as exc:
            await make_request(
                "GET",
                "http://test.url",
                "invalid"
            )
        assert "Unknown provider" in str(exc.value)
