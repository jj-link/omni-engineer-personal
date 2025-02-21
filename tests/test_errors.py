"""Tests for error handling module."""

import unittest
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

class TestErrors(unittest.IsolatedAsyncioTestCase):
    def test_error_formatting(self):
        """Test error message formatting."""
        # Test basic error
        error = OmniError("Test error")
        formatted = format_error(error)
        self.assertIn("Test error", formatted)
        self.assertNotIn("Details", formatted)
        
        # Test error with details
        error = OmniError("Test error", {"key": "value"})
        formatted = format_error(error)
        self.assertIn("Test error", formatted)
        self.assertIn("Details", formatted)
        self.assertIn("key: value", formatted)

    async def test_connection_check(self):
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
            with self.assertRaises(ConnectionError) as cm:
                await check_connection(url)
            self.assertIn("Failed to connect", str(cm.exception))
            self.assertIn("404", str(cm.exception))
            self.assertIn("Not Found", str(cm.exception))
        
        # Test network error
        mock_session.get.side_effect = aiohttp.ClientError("Network error")
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            with self.assertRaises(ConnectionError) as cm:
                await check_connection(url)
            self.assertIn("Failed to connect", str(cm.exception))
            self.assertIn("Network error", str(cm.exception))

    def test_api_key_validation(self):
        """Test API key validation."""
        # Test missing key
        with self.assertRaises(AuthenticationError) as cm:
            validate_api_key(None, "cborg")
        self.assertIn("Missing API key", str(cm.exception))
        self.assertIn("cborg", str(cm.exception))
        
        # Test invalid CBORG key format
        with self.assertRaises(AuthenticationError) as cm:
            validate_api_key("invalid_key", "cborg")
        self.assertIn("Invalid API key format", str(cm.exception))
        self.assertIn("cborg_", str(cm.exception))
        
        # Test valid CBORG key
        validate_api_key("cborg_test_key", "cborg")  # Should not raise

    async def test_model_availability(self):
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
            with self.assertRaises(ModelError) as cm:
                await check_model_availability("ollama", "nonexistent", base_url)
            self.assertIn("Model nonexistent not available", str(cm.exception))
            self.assertIn("codellama", str(cm.exception))
        
        # Test failed API response
        mock_response.status = 500
        mock_response.reason = "Internal Server Error"
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            with self.assertRaises(ModelError) as cm:
                await check_model_availability("ollama", "codellama", base_url)
            self.assertIn("Failed to get model list", str(cm.exception))
            self.assertIn("500", str(cm.exception))
            self.assertIn("Internal Server Error", str(cm.exception))
        
        # Test network error
        mock_session.get.side_effect = aiohttp.ClientError("Network error")
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            with self.assertRaises(ConnectionError) as cm:
                await check_model_availability("ollama", "codellama", base_url)
            self.assertIn("Failed to connect", str(cm.exception))
            self.assertIn("Network error", str(cm.exception))
        
        # Test unknown provider
        with self.assertRaises(ConfigurationError) as cm:
            await check_model_availability("unknown", "model", base_url)
        self.assertIn("Unknown provider", str(cm.exception))
        self.assertIn("ollama", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
