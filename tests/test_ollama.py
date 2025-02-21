"""Tests for the Ollama provider implementation."""
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from omni_core.providers.ollama import OllamaProvider
from omni_core.config import ProviderConfig

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
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
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
        })
        
        mock_session.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        # Test model listing
        models = await self.provider.list_models()
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]["name"], "codellama")
        self.assertEqual(models[1]["name"], "llama2")

    @patch('aiohttp.ClientSession')
    async def test_chat_completion(self, mock_session):
        """Test chat completion generation."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "model": "codellama",
            "created_at": "2024-02-20T12:00:00Z",
            "response": "Hello! I am CodeLlama.",
            "done": True
        })
        
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Test chat completion
        response = await self.provider.chat_completion(
            "Hello, who are you?",
            temperature=0.7,
            top_p=0.9
        )

        self.assertEqual(response.content, "Hello! I am CodeLlama.")
        self.assertTrue(response.done)

    @patch('aiohttp.ClientSession')
    async def test_chat_completion_with_optional_params(self, mock_session):
        """Test chat completion with optional parameters."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "model": "codellama",
            "created_at": "2024-02-20T12:00:00Z",
            "response": "Hello! I am CodeLlama.",
            "done": True
        })
        
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Test chat completion with parameters
        response = await self.provider.chat_completion(
            "Hello, who are you?",
            temperature=0.5,
            top_p=0.8,
            max_tokens=100,
            stop=["stop"],
            stream=True
        )

        self.assertEqual(response.content, "Hello! I am CodeLlama.")
        self.assertTrue(response.done)

        # Verify parameters were passed correctly
        call_kwargs = mock_session.return_value.__aenter__.return_value.post.call_args.kwargs
        self.assertEqual(call_kwargs["json"]["temperature"], 0.5)
        self.assertEqual(call_kwargs["json"]["top_p"], 0.8)
        self.assertEqual(call_kwargs["json"]["max_tokens"], 100)
        self.assertEqual(call_kwargs["json"]["stop"], ["stop"])
        self.assertTrue(call_kwargs["json"]["stream"])

    @patch('aiohttp.ClientSession')
    async def test_chat_completion_error(self, mock_session):
        """Test error handling in chat completion."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.json = AsyncMock(return_value={
            "error": "Internal server error"
        })
        
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Test error handling
        with self.assertRaises(Exception):
            await self.provider.chat_completion("Hello")

if __name__ == '__main__':
    unittest.main()
