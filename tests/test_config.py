"""Tests for configuration module."""

import os
import unittest
from omni_core.config import Configuration, ConfigurationError, ProviderConfig

class TestConfiguration(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.config = Configuration()
        # Store original environment
        self.original_env = dict(os.environ)

    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_provider_config_validation(self):
        """Test provider configuration validation."""
        # Test valid provider
        provider = self.config.get_provider('ollama')
        self.assertIsInstance(provider, ProviderConfig)
        self.assertEqual(provider.base_url, 'http://localhost:11434')
        self.assertEqual(provider.default_model, 'codellama')
        self.assertFalse(provider.requires_key)
        
        # Test invalid provider
        with self.assertRaises(ConfigurationError) as cm:
            self.config.get_provider('invalid')
        self.assertIn("Unknown provider", str(cm.exception))

    def test_environment_validation(self):
        """Test environment variable validation."""
        # Clear environment variables
        if 'TAVILY_API_KEY' in os.environ:
            del os.environ['TAVILY_API_KEY']
        if 'CBORG_API_KEY' in os.environ:
            del os.environ['CBORG_API_KEY']
        
        # Test missing Tavily key
        with self.assertRaises(ConfigurationError) as cm:
            self.config.validate_environment()
        self.assertIn("TAVILY_API_KEY not found", str(cm.exception))
        
        # Set Tavily key but missing CBORG key
        os.environ['TAVILY_API_KEY'] = 'test_key'
        with self.assertRaises(ConfigurationError) as cm:
            self.config.validate_environment()
        self.assertIn("CBORG_API_KEY not found", str(cm.exception))
        
        # Set all required keys
        os.environ['CBORG_API_KEY'] = 'test_key'
        self.config.validate_environment()  # Should not raise

    def test_model_update(self):
        """Test model update functionality."""
        # Test valid model update
        self.config.update_provider_model('ollama', 'mistral')
        self.assertEqual(self.config.get_provider('ollama').default_model, 'mistral')
        
        # Test invalid model update
        with self.assertRaises(ConfigurationError) as cm:
            self.config.update_provider_model('invalid', 'model')
        self.assertIn("Unknown provider", str(cm.exception))

    def test_parameter_update(self):
        """Test parameter update functionality."""
        # Test valid parameter update
        params = {
            'temperature': 0.8,
            'top_p': 0.95,
            'seed': 42
        }
        self.config.update_provider_parameters('ollama', params)
        provider = self.config.get_provider('ollama')
        self.assertEqual(provider.parameters['temperature'], 0.8)
        self.assertEqual(provider.parameters['top_p'], 0.95)
        self.assertEqual(provider.parameters['seed'], 42)
        
        # Test invalid parameter values
        with self.assertRaises(ConfigurationError) as cm:
            self.config.update_provider_parameters('ollama', {'temperature': 1.5})
        self.assertIn("Invalid temperature", str(cm.exception))
        
        with self.assertRaises(ConfigurationError) as cm:
            self.config.update_provider_parameters('ollama', {'top_p': -0.1})
        self.assertIn("Invalid top_p", str(cm.exception))

    def test_api_key_retrieval(self):
        """Test API key retrieval."""
        # Test CBORG key retrieval
        os.environ['CBORG_API_KEY'] = 'test_cborg_key'
        self.assertEqual(self.config.get_api_key('cborg'), 'test_cborg_key')
        
        # Test Tavily key retrieval
        os.environ['TAVILY_API_KEY'] = 'test_tavily_key'
        self.assertEqual(self.config.get_api_key('tavily'), 'test_tavily_key')
        
        # Test missing key
        with self.assertRaises(ConfigurationError) as cm:
            self.config.get_api_key('invalid')
        self.assertIn("Unknown provider", str(cm.exception))
        
        # Test provider without key
        self.assertIsNone(self.config.get_api_key('ollama'))

if __name__ == '__main__':
    unittest.main()
