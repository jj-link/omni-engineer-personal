"""
Tests for API configuration management.
"""
import os
import unittest
from unittest.mock import patch
from omni_core.config import APIConfig

class TestAPIConfig(unittest.TestCase):
    def test_api_config_initialization(self):
        """Test that APIConfig can be initialized and contains expected providers."""
        self.assertIn('cborg', APIConfig.PROVIDERS)
        self.assertIn('ollama', APIConfig.PROVIDERS)
        
        # Test CBORG config
        cborg_config = APIConfig.get_config('cborg')
        self.assertEqual(cborg_config['env_key'], 'CBORG_API_KEY')
        self.assertEqual(cborg_config['base_url'], 'https://api.cborg.lbl.gov')
        self.assertEqual(cborg_config['default_model'], 'lbl/cborg-coder:latest')
        self.assertTrue(cborg_config['requires_key'])
        
        # Test Ollama config
        ollama_config = APIConfig.get_config('ollama')
        self.assertIsNone(ollama_config['env_key'])
        self.assertEqual(ollama_config['base_url'], 'http://localhost:11434')
        self.assertEqual(ollama_config['default_model'], 'codellama')
        self.assertFalse(ollama_config['requires_key'])

    def test_api_config_cborg_validation(self):
        """Test CBORG API key validation."""
        # Test with valid API key
        with patch.dict(os.environ, {'CBORG_API_KEY': 'test_key'}):
            api_key = APIConfig.get_api_key('cborg')
            self.assertEqual(api_key, 'test_key')
        
        # Test with missing API key
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                APIConfig.get_api_key('cborg')

    def test_api_config_ollama_validation(self):
        """Test Ollama config validation (no API key required)."""
        api_key = APIConfig.get_api_key('ollama')
        self.assertIsNone(api_key)

    def test_invalid_provider(self):
        """Test error handling for invalid provider."""
        with self.assertRaises(ValueError):
            APIConfig.get_config('invalid_provider')

if __name__ == '__main__':
    unittest.main()
