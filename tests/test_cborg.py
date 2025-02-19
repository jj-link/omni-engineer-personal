"""Tests for CBORG provider."""

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
from omni_core.providers.cborg import list_models, chat_completion
from omni_core.config import Configuration
from omni_core.response import ResponseError

@pytest.fixture
def mock_config(monkeypatch):
    """Mock configuration for tests."""
    # Mock environment variables
    monkeypatch.setenv("CBORG_API_KEY", "test-api-key")
    
    config = Configuration()
    config.update_provider("cborg")
    config.update_model("lbl/cborg-coder:latest")
    return config

@pytest.mark.asyncio
async def test_list_models(mock_config):
    """Test listing CBORG models."""
    mock_response = {
        "models": [
            {
                "id": "lbl/cborg-coder:latest",
                "name": "CBORG Coder",
                "version": "latest"
            }
        ]
    }
    
    with patch("omni_core.providers.cborg.make_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        models = await list_models()
        
        assert len(models) == 1
        assert models[0]["id"] == "lbl/cborg-coder:latest"
        assert models[0]["name"] == "CBORG Coder"
        
        mock_request.assert_called_once_with(
            "GET",
            "https://api.cborg.lbl.gov/models",
            provider="cborg",
            headers={"Authorization": "Bearer test-api-key"}
        )

@pytest.mark.asyncio
async def test_chat_completion_basic(mock_config):
    """Test basic chat completion."""
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    
    mock_response = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you?"
            },
            "finish_reason": "stop"
        }]
    }
    
    with patch("omni_core.providers.cborg.make_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        response = await chat_completion(messages)
        
        assert response["choices"][0]["message"]["content"] == "Hello! How can I help you?"
        mock_request.assert_called_once()

@pytest.mark.asyncio
async def test_chat_completion_with_parameters(mock_config):
    """Test chat completion with parameters."""
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    parameters = {
        "temperature": 0.8,
        "top_p": 0.9,
        "max_tokens": 100,
        "seed": 42
    }
    
    with patch("omni_core.providers.cborg.make_request", new_callable=AsyncMock) as mock_request:
        await chat_completion(
            messages,
            temperature=parameters["temperature"],
            top_p=parameters["top_p"],
            max_tokens=parameters["max_tokens"],
            seed=parameters["seed"]
        )
        
        # Verify parameters were passed correctly
        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["json"]["temperature"] == parameters["temperature"]
        assert call_kwargs["json"]["top_p"] == parameters["top_p"]
        assert call_kwargs["json"]["max_tokens"] == parameters["max_tokens"]
        assert call_kwargs["json"]["seed"] == parameters["seed"]

@pytest.mark.asyncio
async def test_chat_completion_error_handling(mock_config):
    """Test error handling in chat completion."""
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    
    with patch("omni_core.providers.cborg.make_request", new_callable=AsyncMock) as mock_request:
        # Simulate API error
        mock_request.side_effect = ResponseError(
            "API request failed",
            {"status": 500, "reason": "Internal Server Error"}
        )
        
        with pytest.raises(ResponseError) as exc:
            await chat_completion(messages)
        
        assert "API request failed" in str(exc.value)
        assert exc.value.details["status"] == 500
