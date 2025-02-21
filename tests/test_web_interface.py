import unittest
from unittest.mock import patch, MagicMock
from flask import url_for
from app import app

class TestWebInterface(unittest.TestCase):
    def setUp(self):
        """Set up test client."""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_key'
        self.client = app.test_client()
        
        # Reset session for each test
        with self.client.session_transaction() as session:
            session.clear()

    def test_index_route(self):
        """Test index route returns correct template."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)

    def test_chat_route_cborg(self):
        """Test chat route with CBORG provider."""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'
            session['current_model'] = 'lbl/cborg-coder:latest'

        with patch('app.Assistant') as mock_assistant:
            mock_instance = MagicMock()
            mock_instance.chat.return_value = "Test response"
            mock_assistant.return_value = mock_instance

            response = self.client.post('/chat', json={
                'message': 'Test message',
                'temperature': 0.7,
                'top_p': 0.9
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['response'], "Test response")

    def test_chat_route_ollama(self):
        """Test chat route with Ollama provider."""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'ollama'
            session['current_model'] = 'codellama:latest'

        with patch('subprocess.run') as mock_run, \
             patch('subprocess.Popen') as mock_popen:
            
            mock_run.return_value = MagicMock(returncode=0)
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = [
                '{"response": "Test response"}\n',
                '{"done": true}\n',
                ''
            ]
            mock_process.stderr.readline.return_value = ''
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            response = self.client.post('/chat', json={
                'message': 'Test message',
                'temperature': 0.7,
                'top_p': 0.9
            })

            self.assertEqual(response.status_code, 200)
            self.assertIn('Test response', response.json['response'])

    def test_select_provider_route(self):
        """Test provider selection route."""
        response = self.client.post('/select_provider', json={
            'provider': 'cborg'
        })
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as session:
            self.assertEqual(session['current_provider'], 'cborg')

    def test_select_model_route(self):
        """Test model selection route."""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'

        response = self.client.post('/select_model', json={
            'model': 'lbl/cborg-coder:latest'
        })
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as session:
            self.assertEqual(session['current_model'], 'lbl/cborg-coder:latest')

    def test_invalid_provider(self):
        """Test error handling for invalid provider."""
        response = self.client.post('/select_provider', json={
            'provider': 'invalid'
        })
        self.assertEqual(response.status_code, 400)

    def test_invalid_model(self):
        """Test error handling for invalid model."""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'

        response = self.client.post('/select_model', json={
            'model': 'invalid:model'
        })
        self.assertEqual(response.status_code, 400)

    def test_missing_session(self):
        """Test error handling for missing session data."""
        response = self.client.post('/chat', json={
            'message': 'Test message'
        })
        self.assertEqual(response.status_code, 400)

    def test_home_page(self):
        """Test that the home page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_chat_basic(self):
        """Test basic chat functionality"""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'
            session['current_model'] = 'lbl/cborg-coder:latest'

        with patch('app.Assistant') as mock_assistant:
            mock_instance = MagicMock()
            mock_instance.chat.return_value = "Test response"
            mock_assistant.return_value = mock_instance

            test_message = {'message': 'Hello'}
            response = self.client.post('/chat', json=test_message)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['response'], "Test response")

    def test_chat_with_image(self):
        """Test chat with image upload"""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'
            session['current_model'] = 'lbl/cborg-coder:latest'

        with patch('app.Assistant') as mock_assistant:
            mock_instance = MagicMock()
            mock_instance.chat.return_value = "Image analysis response"
            mock_assistant.return_value = mock_instance

            test_message = {
                'message': 'Analyze this image',
                'image': 'data:image/jpeg;base64,/9j/4AAQSkZJRg=='
            }
            response = self.client.post('/chat', json=test_message)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['response'], "Image analysis response")

    def test_chat_error_handling(self):
        """Test error handling in chat"""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'
            session['current_model'] = 'lbl/cborg-coder:latest'

        with patch('app.Assistant') as mock_assistant:
            mock_instance = MagicMock()
            mock_instance.chat.side_effect = Exception("Test error")
            mock_assistant.return_value = mock_instance

            test_message = {'message': 'Hello'}
            response = self.client.post('/chat', json=test_message)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['response'], "Error: Test error")

    def test_file_upload(self):
        """Test file upload functionality"""
        from io import BytesIO
        file_content = b'fake image content'
        data = {
            'file': (BytesIO(file_content), 'test.jpg')
        }
        response = self.client.post('/upload', data=data)
        self.assertIn(response.status_code, [200, 400])

    def test_reset(self):
        """Test conversation reset functionality"""
        response = self.client.post('/reset')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')

    def test_provider_selection(self):
        """Test provider selection endpoint"""
        response = self.client.get('/providers')
        self.assertEqual(response.status_code, 200)
        self.assertIn('providers', response.json)
        self.assertIsInstance(response.json['providers'], list)
        self.assertIn('cborg', response.json['providers'])

        response = self.client.post('/select_provider', json={'provider': 'cborg'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(response.json['provider'], 'cborg')

        response = self.client.post('/select_provider', json={'provider': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)

    def test_model_selection(self):
        """Test model selection functionality"""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'

        response = self.client.get('/models')
        self.assertEqual(response.status_code, 200)
        self.assertIn('models', response.json)
        self.assertIsInstance(response.json['models'], list)
        self.assertIn('default_model', response.json)
        self.assertIn(response.json['default_model'], response.json['models'])

        with self.client.session_transaction() as session:
            session['current_provider'] = 'ollama'

        response = self.client.get('/models')
        self.assertEqual(response.status_code, 200)
        self.assertIn('models', response.json)
        self.assertIsInstance(response.json['models'], list)
        self.assertIn('default_model', response.json)
        self.assertIn(response.json['default_model'], response.json['models'])

    def test_model_switching(self):
        """Test model switching functionality"""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'
            session['current_model'] = 'lbl/cborg-coder:chat'

        response = self.client.post('/switch_model', json={'model': 'lbl/cborg-coder:chat'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(response.json['model'], 'lbl/cborg-coder:chat')

        with self.client.session_transaction() as session:
            session['current_provider'] = 'ollama'
            session['current_model'] = 'codellama'

        response = self.client.post('/switch_model', json={'model': 'codellama'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(response.json['model'], 'codellama')

        response = self.client.post('/switch_model', json={'model': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)

    def test_parameter_configuration(self):
        """Test parameter configuration endpoints"""
        with self.client.session_transaction() as session:
            session['current_provider'] = 'cborg'
            session['current_parameters'] = {
                'temperature': 0.7,
                'top_p': 0.9,
                'seed': None
            }

        response = self.client.get('/params')
        self.assertEqual(response.status_code, 200)
        self.assertIn('temperature', response.json)
        self.assertIn('top_p', response.json)
        self.assertIn('seed', response.json)
        self.assertEqual(response.json['temperature'], 0.7)
        self.assertEqual(response.json['top_p'], 0.9)
        self.assertIsNone(response.json['seed'])

        new_params = {
            'temperature': 0.8,
            'top_p': 0.95,
            'seed': 42
        }
        response = self.client.post('/update_params', json=new_params)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
        self.assertEqual(response.json['parameters']['temperature'], 0.8)
        self.assertEqual(response.json['parameters']['top_p'], 0.95)
        self.assertEqual(response.json['parameters']['seed'], 42)

        invalid_params = {
            'temperature': 1.5,  # Should be between 0 and 1
            'top_p': -0.1,      # Should be between 0 and 1
            'seed': 'invalid'   # Should be integer or None
        }
        response = self.client.post('/update_params', json=invalid_params)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)

if __name__ == '__main__':
    unittest.main()
