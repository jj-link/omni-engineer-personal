"""
Tests for the client factory system.
"""
import os
from dataclasses import dataclass
import unittest
from unittest.mock import patch

from omni_engineer.client import ClientFactory, CBORGClient, OllamaClient

@dataclass
class MockArgs:
    """Mock command line arguments."""
    ollama_url: str = "http://localhost:11434"

class TestClientFactory(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.args = MockArgs()
        # Store original environment
        self.original_env = dict(os.environ)

    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_cborg_client_creation(self):
        """Test creation of CBORG client"""
        os.environ['CBORG_API_KEY'] = 'test_key'
        
        client = ClientFactory.create_client('cborg', self.args)
        self.assertIsInstance(client, CBORGClient)
        self.assertEqual(client.base_url, 'https://api.cborg.lbl.gov')
        self.assertEqual(client.api_key, 'test_key')
        self.assertEqual(client.headers['Authorization'], 'Bearer test_key')

    def test_ollama_client_creation(self):
        """Test creation of Ollama client"""
        client = ClientFactory.create_client('ollama', self.args)
        
        self.assertIsInstance(client, OllamaClient)
        self.assertEqual(client.base_url, self.args.ollama_url)
        self.assertIsNone(client.api_key)

    def test_missing_cborg_key(self):
        """Test error handling when CBORG key is missing"""
        if 'CBORG_API_KEY' in os.environ:
            del os.environ['CBORG_API_KEY']
        
        with self.assertRaises(ValueError) as cm:
            ClientFactory.create_client('cborg', self.args)
        self.assertIn('Missing CBORG_API_KEY environment variable', str(cm.exception))

    def test_invalid_ollama_url(self):
        """Test error handling with invalid Ollama URL"""
        args = MockArgs(ollama_url="invalid-url")
        
        with self.assertRaises(ValueError) as cm:
            ClientFactory.create_client('ollama', args)
        self.assertIn('Invalid URL', str(cm.exception))

    def test_invalid_provider(self):
        """Test error handling with invalid provider"""
        with self.assertRaises(ValueError) as cm:
            ClientFactory.create_client('invalid', self.args)
        self.assertIn('Invalid provider', str(cm.exception))

if __name__ == '__main__':
    unittest.main()
