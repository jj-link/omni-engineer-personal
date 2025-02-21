"""Tests for CBORG provider."""

import os
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
from omni_core.providers.cborg import list_models, chat_completion
from omni_core.config import Configuration
from omni_core.response import ResponseError

class TestCBORGProvider(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Set up test configuration."""
        # Mock environment variables
        self.patcher = patch.dict(os.environ, {"CBORG_API_KEY": "test-api-key"})
        self.patcher.start()
        
        self.config = Configuration()
        self.config.update_provider("cborg")
        self.config.update_model("lbl/cborg-coder:chat")

    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()

    @patch('aiohttp.ClientSession')
    async def test_list_models(self, mock_session):
        """Test listing CBORG models."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "models": [
                {
                    "id": "lbl/cborg-coder:chat",
                    "name": "CBORG Coder",
                    "version": "chat"
                }
            ]
        })
        
        mock_session.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        # Test model listing
        models = await list_models(self.config)
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]["id"], "lbl/cborg-coder:chat")
        self.assertEqual(models[0]["name"], "CBORG Coder")

    @patch('aiohttp.ClientSession')
    async def test_chat_completion_basic(self, mock_session):
        """Test basic chat completion."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
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
        })
        
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Test chat completion
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        response = await chat_completion(messages, self.config)
        
        self.assertEqual(response["choices"][0]["message"]["content"], "Hello! How can I help you?")

    @patch('aiohttp.ClientSession')
    async def test_chat_completion_with_parameters(self, mock_session):
        """Test chat completion with parameters."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
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
        })
        
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Test chat completion with parameters
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        parameters = {
            "temperature": 0.8,
            "top_p": 0.9,
            "max_tokens": 100,
            "seed": 42
        }
        await chat_completion(
            messages,
            self.config,
            temperature=parameters["temperature"],
            top_p=parameters["top_p"],
            max_tokens=parameters["max_tokens"],
            seed=parameters["seed"]
        )
        
        # Verify parameters were passed correctly
        call_kwargs = mock_session.return_value.__aenter__.return_value.post.call_args.kwargs
        self.assertEqual(call_kwargs["json"]["temperature"], parameters["temperature"])
        self.assertEqual(call_kwargs["json"]["top_p"], parameters["top_p"])
        self.assertEqual(call_kwargs["json"]["max_tokens"], parameters["max_tokens"])
        self.assertEqual(call_kwargs["json"]["seed"], parameters["seed"])

    @patch('aiohttp.ClientSession')
    async def test_chat_completion_error_handling(self, mock_session):
        """Test error handling in chat completion."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={
            "error": "Test error"
        })
        
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Test error handling
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        with self.assertRaises(ResponseError):
            await chat_completion(messages, self.config)

    def test_cborg_model_update(self):
        """Test updating CBORG model."""
        self.config.update_model("new-model")
        self.assertEqual(self.config.model, "new-model")

    @patch('aiohttp.ClientSession')
    async def test_cborg_model_list(self, mock_session):
        """Test listing available CBORG models."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "models": [
                {"id": "model1"},
                {"id": "model2"}
            ]
        })
        
        mock_session.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        # Test model listing
        models = await list_models(self.config)
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]["id"], "model1")
        self.assertEqual(models[1]["id"], "model2")

if __name__ == '__main__':
    unittest.main()
