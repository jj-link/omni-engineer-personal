import unittest
from unittest.mock import patch, MagicMock
import subprocess
import json
import os
import logging
from app import app, PROVIDER_CONFIG

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestOllamaIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        logger.debug("Setting up test environment")
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test_key'
        self.client = self.app.test_client()
        
        # Set up test context
        logger.debug("Pushing app context")
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Mock successful Ollama list response
        self.mock_ollama_list = """\
NAME              ID    SIZE   MODIFIED
codellama:latest  abc   5.0GB  2 weeks ago
llama2:latest     def   4.2GB  3 weeks ago
mistral:latest    ghi   4.8GB  1 week ago
"""
        logger.debug("Test setup complete")
    
    def tearDown(self):
        """Clean up after each test"""
        logger.debug("Cleaning up test environment")
        self.ctx.pop()
        logger.debug("Test cleanup complete")

    def test_get_ollama_models(self):
        """Test that we can get a list of Ollama models"""
        logger.debug("Starting test_get_ollama_models")
        
        with self.client.session_transaction() as sess:
            logger.debug("Setting current provider to ollama")
            sess['current_provider'] = 'ollama'
            
        with patch('subprocess.run') as mock_run:
            logger.debug("Setting up subprocess.run mock")
            # Configure mock
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = self.mock_ollama_list
            mock_run.return_value.stderr = ""
            
            # Make request
            logger.debug("Making GET request to /models")
            response = self.client.get('/models')
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response data: {response.data}")
            
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            # Models should be in a list under 'models' key
            models = data.get('models', [])
            logger.debug(f"Retrieved models: {models}")
            
            # Verify model list
            expected_models = ['codellama:latest', 'llama2:latest', 'mistral:latest']
            for model in expected_models:
                self.assertIn(model, models)

    def test_ollama_chat(self):
        """Test chat functionality with Ollama"""
        logger.debug("Starting test_ollama_chat")
        test_message = "Write a hello world program"
        expected_response = "Here's a simple hello world program:\n\nprint('Hello, World!')"
        
        with self.client.session_transaction() as sess:
            logger.debug("Setting up chat session")
            sess['current_provider'] = 'ollama'
            sess['current_model'] = 'codellama:latest'
            
        with patch('subprocess.Popen') as mock_popen:
            logger.debug("Setting up subprocess.Popen mock")
            # Configure mock process
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = [expected_response, ""]
            mock_process.stderr.read.return_value = ""
            mock_popen.return_value = mock_process
            
            # Make request
            logger.debug("Making POST request to /chat")
            response = self.client.post('/chat', 
                json={
                    'message': test_message,
                    'settings': {
                        'temperature': 0.7,
                        'top_p': 0.9
                    }
                })
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response data: {response.data}")
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('response', data)
            self.assertEqual(data['response'], expected_response)

    def test_ollama_not_installed(self):
        """Test graceful handling when Ollama is not installed"""
        logger.debug("Starting test_ollama_not_installed")
        
        with self.client.session_transaction() as sess:
            logger.debug("Setting current provider to ollama")
            sess['current_provider'] = 'ollama'
            
        with patch('subprocess.run') as mock_run:
            logger.debug("Setting up subprocess.run mock to raise FileNotFoundError")
            # Simulate Ollama not found
            mock_run.side_effect = FileNotFoundError("No such file or directory: 'ollama'")
            
            logger.debug("Making GET request to /models")
            response = self.client.get('/models')
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response data: {response.data}")
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            # Should return empty model list when Ollama not found
            self.assertEqual(data.get('models', []), [])

    def test_switch_to_ollama_model(self):
        """Test switching to an Ollama model"""
        logger.debug("Starting test_switch_to_ollama_model")
        
        with self.client.session_transaction() as sess:
            logger.debug("Setting current provider to ollama")
            sess['current_provider'] = 'ollama'
            
        with patch('subprocess.run') as mock_run:
            logger.debug("Setting up subprocess.run mock for model list")
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = self.mock_ollama_list
            mock_run.return_value.stderr = ""
            
            logger.debug("Making POST request to /switch_model")
            response = self.client.post('/switch_model',
                json={'model': 'codellama:latest'})
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response data: {response.data}")
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data.get('model'), 'codellama:latest')

if __name__ == '__main__':
    unittest.main()
