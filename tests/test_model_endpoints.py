"""Tests for model endpoints."""

import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestModelEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Mock Ollama list command output
        self.mock_ollama_list = """\
NAME              ID    SIZE   MODIFIED
codellama:latest  abc   5.0GB  2 weeks ago
llama2:latest     def   4.2GB  3 weeks ago
mistral:latest    ghi   4.8GB  1 week ago
"""

    def test_provider_switching(self):
        """Test that switching providers works correctly"""
        # Start with CBORG
        with self.client.session_transaction() as sess:
            sess['current_provider'] = 'cborg'
        
        # Get initial models (CBORG)
        response = self.client.get('/models')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['provider'], 'cborg')
        self.assertEqual(data['format'], 'grouped')
        self.assertIn('model_groups', data)
        
        # Switch to Ollama
        with patch('subprocess.run') as mock_run:
            # Mock successful Ollama list command
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.stdout = self.mock_ollama_list
            mock_run.return_value = mock_process
            
            # Switch provider
            response = self.client.post('/select_provider', json={'provider': 'ollama'})
            self.assertEqual(response.status_code, 200)
            
            # Get models (should be Ollama now)
            response = self.client.get('/models')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['provider'], 'ollama')
            self.assertEqual(data['format'], 'flat')
            self.assertEqual(len(data['models']), 3)
            self.assertEqual(data['models'][0]['name'], 'codellama:latest')

    def test_provider_list(self):
        """Test that provider list includes both providers"""
        response = self.client.get('/providers')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('providers', data)
        self.assertIn('ollama', data['providers'])
        self.assertIn('cborg', data['providers'])

if __name__ == '__main__':
    unittest.main()
