"""Tests for the Ollama provider implementation."""
import pytest
from unittest.mock import AsyncMock, patch
from omni_core.providers.ollama import OllamaProvider
from omni_core.config import ProviderConfig

@pytest.fixture
def ollama_provider():
    """Create a test instance of OllamaProvider."""
    config = ProviderConfig(
        name="ollama",
        model="codellama",
        base_url="http://localhost:11434"
    )
    return OllamaProvider(config)

@pytest.mark.asyncio
async def test_list_models(ollama_provider):
    """Test listing available models."""
    mock_response = {
        "models": [
            {"name": "llama2"},
            {"name": "codellama"},
            {"name": "mistral"}
        ]
    }
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value.status = 200
        mock_context.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value = mock_context
        
        models = await ollama_provider.list_models()
        
        assert models == ["llama2", "codellama", "mistral"]
        mock_get.assert_called_once_with("http://localhost:11434/api/tags")

@pytest.mark.asyncio
async def test_chat_completion(ollama_provider):
    """Test chat completion generation."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello!"}
    ]
    
    mock_response = {
        "message": {
            "role": "assistant",
            "content": "Hello! How can I help you today?"
        },
        "prompt_eval_count": 10,
        "eval_count": 15
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value.status = 200
        mock_context.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_post.return_value = mock_context
        
        response = await ollama_provider.chat_completion(
            messages=messages,
            model="llama2",
            temperature=0.7,
            top_p=1.0
        )
        
        assert response["choices"][0]["message"]["content"] == "Hello! How can I help you today?"
        assert response["usage"]["prompt_tokens"] == 10
        assert response["usage"]["completion_tokens"] == 15
        assert response["usage"]["total_tokens"] == 25
        
        # Verify correct payload was sent
        expected_payload = {
            "model": "llama2",
            "messages": messages,
            "options": {
                "temperature": 0.7,
                "top_p": 1.0
            }
        }
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/chat",
            json=expected_payload
        )

@pytest.mark.asyncio
async def test_chat_completion_with_optional_params(ollama_provider):
    """Test chat completion with optional parameters."""
    messages = [{"role": "user", "content": "Hello!"}]
    mock_response = {
        "message": {"role": "assistant", "content": "Hi!"},
        "prompt_eval_count": 5,
        "eval_count": 5
    }
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value.status = 200
        mock_context.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_post.return_value = mock_context
        
        response = await ollama_provider.chat_completion(
            messages=messages,
            model="llama2",
            temperature=0.5,
            top_p=0.9,
            max_tokens=100,
            stop=["END"]
        )
        
        # Verify all optional parameters were included
        expected_payload = {
            "model": "llama2",
            "messages": messages,
            "options": {
                "temperature": 0.5,
                "top_p": 0.9,
                "num_predict": 100,
                "stop": ["END"]
            }
        }
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/chat",
            json=expected_payload
        )

@pytest.mark.asyncio
async def test_chat_completion_error(ollama_provider):
    """Test error handling in chat completion."""
    messages = [{"role": "user", "content": "Hello!"}]
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value.status = 400
        mock_context.__aenter__.return_value.text = AsyncMock(return_value="Invalid model")
        mock_post.return_value = mock_context
        
        with pytest.raises(Exception) as exc_info:
            await ollama_provider.chat_completion(
                messages=messages,
                model="invalid_model"
            )
        
        assert "Chat completion failed: Invalid model" in str(exc_info.value)
