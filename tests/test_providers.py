import unittest
import json
from unittest.mock import patch, MagicMock
from app import app

@patch('app.Assistant')
@patch('app.assistant')
class TestProviders(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_key'
        self.client = app.test_client()
        # Reset session for each test
        with self.client.session_transaction() as session:
            session.clear()

    def test_ollama_models(self, mock_global_assistant, mock_assistant_class):
        """Test Ollama models endpoint"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = (
                "NAME                ID              SIZE      MODIFIED\n"
                "codellama:latest    abc123         5.0GB     2 days ago\n"
                "llama2:latest       def456         4.2GB     3 days ago"
            )
            
            response = self.client.get('/models')
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertIn('model_groups', data)
            self.assertIn('ollama', data['model_groups'])
            self.assertIn('codellama:latest', data['model_groups']['ollama'])

    def test_cborg_chat(self, mock_global_assistant, mock_assistant_class):
        """Test CBORG chat endpoint"""
        # Set up session
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'
            session['current_model'] = 'lbl/cborg-coder:latest'

        # Mock both the global assistant and the Assistant class
        mock_instance = MagicMock()
        mock_instance.chat.return_value = "Hello from CBORG!"
        mock_global_assistant.chat.return_value = "Hello from CBORG!"
        mock_assistant_class.return_value = mock_instance
        
        response = self.client.post('/chat', json={'message': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['response'], "Hello from CBORG!")

    def test_ollama_chat(self, mock_global_assistant, mock_assistant_class):
        """Test Ollama chat endpoint"""
        # Set up session
        with self.client.session_transaction() as session:
            session['current_provider'] = 'ollama'
            session['current_model'] = 'codellama:latest'

        # Mock both subprocess.run (for version check) and subprocess.Popen (for chat)
        with patch('subprocess.run') as mock_run, \
             patch('subprocess.Popen') as mock_popen:
            
            # Mock version check
            mock_run.return_value = MagicMock(returncode=0)
            
            # Mock chat process
            mock_process = MagicMock()
            
            # Create response object that matches Ollama's JSON format
            response_obj = {"response": "Hello from Ollama!"}
            done_obj = {"done": True}
            
            mock_process.stdout.readline.side_effect = [
                json.dumps(response_obj) + '\n',
                json.dumps(done_obj) + '\n',
                ''
            ]
            mock_process.stderr.readline.return_value = ''
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            response = self.client.post('/chat', json={'message': 'test'})
            self.assertEqual(response.status_code, 200)
            
            # Parse the response and extract just the text
            response_json = response.get_json()
            response_data = json.loads(response_json['response'].split('\n')[0])
            self.assertEqual(response_data['response'], "Hello from Ollama!")

    def test_invalid_provider(self, mock_global_assistant, mock_assistant_class):
        """Test invalid provider handling"""
        response = self.client.post('/select_provider', json={'provider': 'invalid'})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
