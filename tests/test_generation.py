"""Tests for model text generation."""
import json
import unittest
from unittest.mock import patch, MagicMock
import requests

from omni_engineer.client import (
    ClientFactory,
    ModelParameters,
    CBORGClient,
    OllamaClient
)

class MockResponse:
    """Mock response object for requests."""
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code
        self._content = content
        
    def json(self):
        """Return JSON content."""
        if isinstance(self._content, str):
            return json.loads(self._content)
        return self._content

    def raise_for_status(self):
        """Raise exception if status code is not 200."""
        if self.status_code != 200:
            raise requests.HTTPError(f"HTTP error occurred: {self.status_code}")

class TestGeneration(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.cborg_client = CBORGClient(
            api_key="test-key",
            base_url="https://api.cborg.dev"
        )
        self.ollama_client = OllamaClient(
            base_url="http://localhost:11434"
        )

    @patch('requests.post')
    def test_cborg_generation(self, mock_post):
        """Test CBORG text generation."""
        mock_response = MockResponse({
            "choices": [{
                "message": {
                    "content": "Generated text"
                }
            }]
        })
        mock_post.return_value = mock_response

        response = self.cborg_client.generate(
            "Test prompt",
            ModelParameters(temperature=0.7)
        )

        self.assertEqual(response, "Generated text")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_ollama_generation(self, mock_post):
        """Test Ollama text generation."""
        mock_response = MockResponse({
            "response": "Generated text"
        })
        mock_post.return_value = mock_response

        response = self.ollama_client.generate(
            "Test prompt",
            ModelParameters(temperature=0.7)
        )

        self.assertEqual(response, "Generated text")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_generation_error_handling(self, mock_post):
        """Test error handling during generation."""
        mock_response = MockResponse("", status_code=500)
        mock_post.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            self.cborg_client.generate(
                "Test prompt",
                ModelParameters()
            )

    def test_generation_with_all_parameters(self):
        """Test generation with all available parameters."""
        params = ModelParameters(
            temperature=0.8,
            top_p=0.9,
            seed=42,
            model="codellama:latest"
        )

        # Test parameter validation
        self.assertEqual(params.temperature, 0.8)
        self.assertEqual(params.top_p, 0.9)
        self.assertEqual(params.seed, 42)
        self.assertEqual(params.model, "codellama:latest")

        # Test invalid parameter values
        with self.assertRaises(ValueError):
            ModelParameters(temperature=2.0)
        with self.assertRaises(ValueError):
            ModelParameters(top_p=1.5)

    @patch('requests.post')
    def test_cborg_generation_parameter_passing(self, mock_post):
        """Test that parameters are correctly passed to CBORG API."""
        mock_response = MockResponse({
            "choices": [{
                "message": {
                    "content": "Generated text"
                }
            }]
        })
        mock_post.return_value = mock_response

        params = ModelParameters(
            temperature=0.8,
            top_p=0.9,
            seed=42,
            model="lbl/cborg-coder:custom"
        )

        self.cborg_client.generate("Test prompt", params)

        # Verify API call parameters
        call_args = mock_post.call_args
        self.assertIn("json", call_args.kwargs)
        request_body = call_args.kwargs["json"]
        self.assertEqual(request_body["temperature"], 0.8)
        self.assertEqual(request_body["top_p"], 0.9)
        self.assertEqual(request_body["seed"], 42)
        self.assertEqual(request_body["model"], "lbl/cborg-coder:custom")

    def test_invalid_base_url(self):
        """Test initialization with invalid base URL."""
        with self.assertRaises(ValueError):
            CBORGClient(
                api_key="test-key",
                base_url="invalid-url"
            )

    @patch('requests.post')
    def test_malformed_response(self, mock_post):
        """Test handling of malformed API responses."""
        # Test missing required fields
        mock_post.return_value = MockResponse({
            "invalid": "response"
        })

        with self.assertRaises(KeyError):
            self.cborg_client.generate(
                "Test prompt",
                ModelParameters()
            )

        # Test invalid JSON response
        mock_post.return_value = MockResponse(
            "Invalid JSON",
            status_code=200
        )

        with self.assertRaises(json.JSONDecodeError):
            self.cborg_client.generate(
                "Test prompt",
                ModelParameters()
            )

if __name__ == '__main__':
    unittest.main()
