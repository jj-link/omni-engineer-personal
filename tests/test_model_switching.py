import unittest
from unittest.mock import patch, MagicMock
import json
import os
from app import app, PROVIDER_CONFIG

class TestModelSwitching(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_key'
        self.client = app.test_client()
        
        # Set up test context
        self.ctx = app.app_context()
        self.ctx.push()
        
        # Mock successful Ollama list response
        self.mock_ollama_list = """\
NAME              ID    SIZE   MODIFIED
codellama:latest  abc   5.0GB  2 weeks ago
llama2:latest     def   4.2GB  3 weeks ago
mistral:latest    ghi   4.8GB  1 week ago
"""

    def tearDown(self):
        """Clean up after each test"""
        self.ctx.pop()

    def test_switch_to_ollama_model(self):
        """Test switching to an Ollama model"""
        with patch('subprocess.run') as mock_run:
            # Mock Ollama list command
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=self.mock_ollama_list
            )
            
            # Try switching to llama2:latest
            response = self.client.post('/switch_model', 
                json={'model': 'llama2:latest'})
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['model'], 'llama2:latest')
            self.assertEqual(data['provider'], 'ollama')

    def test_switch_to_cborg_model(self):
        """Test switching to a CBORG model"""
        # Try switching to a CBORG model
        response = self.client.post('/switch_model', 
            json={'model': 'lbl/cborg-coder:latest'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['model'], 'lbl/cborg-coder:latest')
        self.assertEqual(data['provider'], 'cborg')

    def test_switch_to_anthropic_model(self):
        """Test switching to an Anthropic model"""
        # Mock ANTHROPIC_API_KEY
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'}):
            response = self.client.post('/switch_model', 
                json={'model': 'anthropic/claude-haiku'})
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['model'], 'anthropic/claude-haiku')
            self.assertEqual(data['provider'], 'anthropic')

    def test_switch_to_anthropic_without_api_key(self):
        """Test switching to Anthropic model without API key fails"""
        # Ensure ANTHROPIC_API_KEY is not set
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}, clear=True):
            response = self.client.post('/switch_model', 
                json={'model': 'anthropic/claude-haiku'})
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 400)
            self.assertIn('API key required', data['error'])

    def test_switch_to_invalid_model(self):
        """Test switching to a non-existent model fails"""
        response = self.client.post('/switch_model', 
            json={'model': 'invalid/model'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid provider', data['error'])

    def test_switch_to_unavailable_ollama_model(self):
        """Test switching to an unavailable Ollama model fails"""
        with patch('subprocess.run') as mock_run:
            # Mock Ollama list command
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=self.mock_ollama_list
            )
            
            # Try switching to non-existent model
            response = self.client.post('/switch_model', 
                json={'model': 'nonexistent:latest'})
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 400)
            self.assertIn('not available', data['error'])

if __name__ == '__main__':
    unittest.main()
