"""Tests for the Ollama provider implementation."""
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from omni_core.providers.ollama import OllamaProvider
from omni_core.config import ProviderConfig
import json


class MockResponse:
    def __init__(self, json_data, status=200):
        self._json_data = json_data
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def json(self):
        return self._json_data

    async def text(self):
        return json.dumps(self._json_data)


class MockClientSession:
    def __init__(self, get_response=None, post_response=None):
        self.get_response = get_response
        self.post_response = post_response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def get(self, url):
        return self.get_response

    def post(self, url, json=None):
        return self.post_response

    async def close(self):
        pass


class TestOllamaProvider(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Create a test instance of OllamaProvider."""
        self.config = ProviderConfig(
            name="ollama",
            model="codellama",
            base_url="http://localhost:11434"
        )
        self.provider = OllamaProvider(self.config)

    @patch('aiohttp.ClientSession')
    async def test_list_models(self, mock_session):
        """Test listing available models."""
        # Mock response
        mock_response_data = {
            "models": [
                {
                    "name": "codellama",
                    "modified_at": "2024-02-20T12:00:00Z",
                    "size": 4563402752
                },
                {
                    "name": "llama2",
                    "modified_at": "2024-02-20T12:00:00Z",
                    "size": 4563402752
                }
            ]
        }
        mock_response = MockResponse(mock_response_data)
        mock_session.return_value = MockClientSession(get_response=mock_response)

        # Test model listing
        models = await self.provider.list_models()
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]["name"], "codellama")
        self.assertEqual(models[1]["name"], "llama2")

    @patch('aiohttp.ClientSession')
    async def test_chat_completion(self, mock_session):
        """Test chat completion generation."""
        # Mock response
        mock_response_data = {
            "model": "codellama",
            "created_at": "2024-02-20T12:00:00Z",
            "response": "Hello! I am CodeLlama.",
            "done": True
        }
        mock_response = MockResponse(mock_response_data)
        mock_session.return_value = MockClientSession(post_response=mock_response)

        # Test chat completion
        messages = [
            {"role": "user", "content": "Hello, who are you?"}
        ]
        response = await self.provider.chat_completion(
            messages,
            temperature=0.7,
            top_p=0.9
        )

        self.assertEqual(response["choices"][0]["message"]["content"], "Hello! I am CodeLlama.")

    @patch('aiohttp.ClientSession')
    async def test_chat_completion_with_optional_params(self, mock_session):
        """Test chat completion with optional parameters."""
        # Mock response
        mock_response_data = {
            "model": "codellama",
            "created_at": "2024-02-20T12:00:00Z",
            "response": "Hello! I am CodeLlama.",
            "done": True
        }
        mock_response = MockResponse(mock_response_data)
        mock_session.return_value = MockClientSession(post_response=mock_response)

        # Test chat completion with parameters
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Hello, who are you?"}
        ]
        response = await self.provider.chat_completion(
            messages,
            temperature=0.5,
            top_p=0.8,
            max_tokens=100
        )

        self.assertEqual(response["choices"][0]["message"]["content"], "Hello! I am CodeLlama.")

    async def test_chat_completion_error(self):
        """Test error handling in chat completion."""
        messages = [{"role": "user", "content": "Hello"}]
        mock_response_data = {
            "error": "Model not found"
        }
        mock_response = MockResponse(mock_response_data, status=404)
        mock_session = MockClientSession(post_response=mock_response)

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with self.assertRaises(Exception) as context:
                await self.provider.chat_completion(messages)
            self.assertTrue(
                "Model not found" in str(context.exception) or 
                mock_response.status == 404
            )


if __name__ == '__main__':
    unittest.main()
