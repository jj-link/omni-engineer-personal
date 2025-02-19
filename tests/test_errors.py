"""Tests for error handling module."""

import pytest
import aiohttp
from unittest.mock import patch, AsyncMock, MagicMock
from omni_core.errors import (
    OmniError,
    ConnectionError,
    AuthenticationError,
    ModelError,
    ConfigurationError,
    ResponseError,
    format_error,
    check_connection,
    validate_api_key,
    check_model_availability
)

def test_error_formatting():
    """Test error message formatting."""
    # Test basic error
    error = OmniError("Test error")
    formatted = format_error(error)
    assert "Test error" in formatted
    assert "Details" not in formatted
    
    # Test error with details
    error = OmniError("Test error", {"key": "value"})
    formatted = format_error(error)
    assert "Test error" in formatted
    assert "Details" in formatted
    assert "key: value" in formatted

@pytest.mark.asyncio
async def test_connection_check():
    """Test connection checking."""
    url = "http://test.url"
    
    # Test successful connection
    mock_response = AsyncMock()
    mock_response.status = 200
    
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await check_connection(url)  # Should not raise
    
    # Test failed connection
    mock_response.status = 404
    mock_response.reason = "Not Found"
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(ConnectionError) as exc:
            await check_connection(url)
        assert "Failed to connect" in str(exc.value)
        assert exc.value.details["status"] == 404
    
    # Test network error
    mock_session.get.side_effect = aiohttp.ClientError("Network error")
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(ConnectionError) as exc:
            await check_connection(url)
        assert "Failed to connect" in str(exc.value)
        assert "Network error" in exc.value.details["error"]

def test_api_key_validation():
    """Test API key validation."""
    # Test missing key
    with pytest.raises(AuthenticationError) as exc:
        validate_api_key(None, "cborg")
    assert "Missing API key" in str(exc.value)
    assert exc.value.details["provider"] == "cborg"
    
    # Test invalid CBORG key format
    with pytest.raises(AuthenticationError) as exc:
        validate_api_key("invalid_key", "cborg")
    assert "Invalid API key format" in str(exc.value)
    assert exc.value.details["expected_prefix"] == "cborg_"
    
    # Test valid CBORG key
    validate_api_key("cborg_test_key", "cborg")  # Should not raise

@pytest.mark.asyncio
async def test_model_availability():
    """Test model availability checking."""
    base_url = "http://localhost:11434"
    
    # Test successful Ollama model check
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "models": [{"name": "codellama"}, {"name": "mistral"}]
    }
    
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await check_model_availability("ollama", "codellama", base_url)  # Should not raise
    
    # Test unavailable model
    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(ModelError) as exc:
            await check_model_availability("ollama", "nonexistent", base_url)
        assert "Model nonexistent not available" in str(exc.value)
        assert "codellama" in exc.value.details["available_models"]
    
    # Test failed API response
    mock_response.status = 500
    mock_response.reason = "Internal Server Error"
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(ModelError) as exc:
            await check_model_availability("ollama", "codellama", base_url)
        assert "Failed to get model list" in str(exc.value)
        assert exc.value.details["status"] == 500
    
    # Test network error
    mock_session.get.side_effect = aiohttp.ClientError("Network error")
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(ConnectionError) as exc:
            await check_model_availability("ollama", "codellama", base_url)
        assert "Failed to connect" in str(exc.value)
        assert "Network error" in exc.value.details["error"]
    
    # Test unknown provider
    with pytest.raises(ConfigurationError) as exc:
        await check_model_availability("unknown", "model", base_url)
    assert "Unknown provider" in str(exc.value)
    assert "ollama" in exc.value.details["available_providers"]
