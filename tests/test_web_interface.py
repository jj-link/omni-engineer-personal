import pytest
from flask.testing import FlaskClient
import json
from unittest.mock import patch, MagicMock
import os
import sys

print("Starting test module")
print(f"Python path: {sys.path}")

# Mock environment variables
os.environ['ANTHROPIC_API_KEY'] = 'mock-key'

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
print(f"Project root: {project_root}")

try:
    # Import app after setting up environment
    from app import app
    print("Successfully imported app")
except Exception as e:
    print(f"Error importing app: {e}")

@pytest.fixture
def mock_assistant():
    with patch('app.Assistant') as mock:
        mock.return_value.chat.return_value = 'Test response'
        yield mock

@pytest.fixture
def client(mock_assistant):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200

def test_chat_basic(client, mock_assistant):
    """Test basic chat functionality"""
    test_message = {'message': 'Hello'}
    response = client.post('/chat', json=test_message)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert 'thinking' in data
    assert data['thinking'] is False

def test_chat_with_image(client, mock_assistant):
    """Test chat with image upload"""
    test_message = {
        'message': 'Analyze this image',
        'image': 'data:image/jpeg;base64,/9j/4AAQSkZJRg=='
    }
    response = client.post('/chat', json=test_message)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data

def test_chat_error_handling(client):
    """Test error handling in chat"""
    with patch('app.Assistant') as mock_assistant:
        mock_assistant.return_value.chat.side_effect = Exception("Test error")
        response = client.post('/chat', json={'message': 'trigger error'})
        assert response.status_code == 200  # We return 200 even for errors
        data = json.loads(response.data)
        assert 'Error:' in data['response']

def test_file_upload(client):
    """Test file upload functionality"""
    from io import BytesIO
    file_content = b'fake image content'
    data = {
        'file': (BytesIO(file_content), 'test.jpg')
    }
    response = client.post('/upload', data=data)
    assert response.status_code in [200, 400]  # Either success or validation error

def test_reset(client):
    """Test conversation reset functionality"""
    response = client.post('/reset')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'

def test_provider_selection(client):
    """Test provider selection endpoint"""
    # Test getting available providers
    response = client.get('/providers')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'providers' in data
    assert 'ollama' in data['providers']
    assert 'cborg' in data['providers']

    # Test selecting a provider
    response = client.post('/select_provider', json={'provider': 'ollama'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['provider'] == 'ollama'

    # Test invalid provider
    response = client.post('/select_provider', json={'provider': 'invalid'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data

def test_model_selection(client):
    """Test model selection for each provider"""
    # First select Ollama provider
    client.post('/select_provider', json={'provider': 'ollama'})
    
    # Test getting Ollama models
    response = client.get('/models')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'models' in data
    assert 'codellama' in data['models']  # Default Ollama model
    
    # Switch to CBORG provider
    client.post('/select_provider', json={'provider': 'cborg'})
    
    # Test getting CBORG models
    response = client.get('/models')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'models' in data
    assert 'lbl/cborg-coder:latest' in data['models']  # Default CBORG model

def test_parameter_configuration(client):
    """Test parameter configuration endpoints"""
    test_params = {
        'temperature': 0.7,
        'top_p': 0.9,
        'seed': 42
    }
    
    # Test setting parameters
    response = client.post('/update_params', json=test_params)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    
    # Test getting current parameters
    response = client.get('/params')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['temperature'] == test_params['temperature']
    assert data['top_p'] == test_params['top_p']
    assert data['seed'] == test_params['seed']
    
    # Test invalid parameters
    invalid_params = {'temperature': 2.0}  # Invalid temperature value
    response = client.post('/update_params', json=invalid_params)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'error' in data
