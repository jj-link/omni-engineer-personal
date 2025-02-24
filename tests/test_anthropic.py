"""Tests for the Anthropic provider."""

import unittest
import os
from unittest.mock import patch, MagicMock
import json
from omni_core.providers.anthropic import AnthropicProvider

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

    def get(self, url, **kwargs):
        return self.get_response

    def post(self, url, **kwargs):
        return self.post_response

    async def close(self):
        pass

class TestAnthropicProvider(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Mock ANTHROPIC_API_KEY
        self.api_key = "test_key_123"
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': self.api_key}):
            self.provider = AnthropicProvider()

    async def test_list_models(self):
        """Test listing available models."""
        models = await self.provider.list_models()
        
        self.assertEqual(len(models), 3)
        self.assertEqual(models[0]["name"], "anthropic/claude-haiku")
        self.assertEqual(models[1]["name"], "anthropic/claude-sonnet")
        self.assertEqual(models[2]["name"], "anthropic/claude-opus")

    async def test_chat_completion(self):
        """Test chat completion generation."""
        mock_response_data = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Hello! How can I help you today?"}],
            "model": "claude-haiku",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20
            }
        }
        mock_response = MockResponse(mock_response_data)
        mock_session = MockClientSession(post_response=mock_response)

        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello!"}
        ]

        with patch('aiohttp.ClientSession', return_value=mock_session):
            response = await self.provider.chat_completion(
                messages=messages,
                model="anthropic/claude-haiku"
            )

            self.assertEqual(
                response["choices"][0]["message"]["content"],
                "Hello! How can I help you today?"
            )
            self.assertEqual(response["model"], "claude-haiku")

    async def test_chat_completion_with_params(self):
        """Test chat completion with optional parameters."""
        mock_response_data = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Hello! How can I help you today?"}],
            "model": "claude-haiku",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20
            }
        }
        mock_response = MockResponse(mock_response_data)
        mock_session = MockClientSession(post_response=mock_response)

        messages = [{"role": "user", "content": "Hello!"}]

        with patch('aiohttp.ClientSession', return_value=mock_session):
            response = await self.provider.chat_completion(
                messages=messages,
                model="anthropic/claude-haiku",
                temperature=0.5,
                top_p=0.8,
                seed=42,
                max_tokens=1000
            )

            self.assertEqual(
                response["choices"][0]["message"]["content"],
                "Hello! How can I help you today?"
            )

    async def test_chat_completion_error(self):
        """Test error handling in chat completion."""
        mock_response_data = {
            "error": {
                "type": "invalid_request_error",
                "message": "Invalid API key"
            }
        }
        mock_response = MockResponse(mock_response_data, status=401)
        mock_session = MockClientSession(post_response=mock_response)

        messages = [{"role": "user", "content": "Hello!"}]

        with patch('aiohttp.ClientSession', return_value=mock_session):
            with self.assertRaises(Exception) as context:
                await self.provider.chat_completion(messages)
            self.assertIn("Anthropic API error", str(context.exception))

    def test_missing_api_key(self):
        """Test initialization with missing API key."""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}, clear=True):
            with self.assertRaises(ValueError) as context:
                AnthropicProvider()
            self.assertIn("ANTHROPIC_API_KEY", str(context.exception))

if __name__ == '__main__':
    unittest.main()
