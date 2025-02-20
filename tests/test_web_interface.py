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
    # Create mock instance with our desired behavior
    mock_instance = MagicMock()
    mock_instance.chat.return_value = "Test response"
    mock_instance.total_tokens_used = 100
    mock_instance.conversation_history = [{
        'role': 'assistant',
        'content': [
            {
                'type': 'tool_use',
                'name': 'test_tool'
            },
            {
                'type': 'text',
                'text': 'Test response'
            }
        ]
    }]
    
    # Patch the global assistant instance
    patcher = patch('app.assistant', new=mock_instance)
    patcher.start()
    yield mock_instance
    patcher.stop()

@pytest.fixture
def client(mock_assistant):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully"""
    response = client.get('/')
    try:
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    except AssertionError as e:
        print(f"\nAssertion failed in test_home_page: {str(e)}")
        raise

def test_chat_basic(client, mock_assistant):
    """Test basic chat functionality"""
    print("\n=== Testing basic chat functionality ===")
    
    test_message = {'message': 'Hello'}
    print(f"Sending message: {test_message}")
    response = client.post('/chat', json=test_message)
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    data = json.loads(response.data)
    print(f"Parsed data: {data}")
    
    # Test each assertion separately
    if response.status_code != 200:
        pytest.fail(f"Expected status 200, got {response.status_code}")
    
    if data.get('response') != "Test response":
        pytest.fail(f"Expected response 'Test response', got {data.get('response')}")
    
    if data.get('thinking') is not False:
        pytest.fail(f"Expected thinking False, got {data.get('thinking')}")
    
    if 'token_usage' not in data:
        pytest.fail("Missing token_usage in response")
        
    if not isinstance(data.get('token_usage'), dict):
        pytest.fail(f"Expected token_usage to be dict, got {type(data.get('token_usage'))}")
        
    if 'total_tokens' not in data['token_usage']:
        pytest.fail("Missing total_tokens in token_usage")
        
    if 'max_tokens' not in data['token_usage']:
        pytest.fail("Missing max_tokens in token_usage")
        
    if 'tool_name' not in data:
        pytest.fail("Missing tool_name in response")

def test_chat_with_image(client):
    """Test chat with image upload"""
    print("\n=== Testing chat with image ===")
    
    # Create a mock instance
    mock_instance = MagicMock()
    mock_instance.chat.return_value = "Image analysis response"
    mock_instance.conversation_history = [{
        'role': 'assistant',
        'content': [
            {
                'type': 'tool_use',
                'name': 'test_tool'
            },
            {
                'type': 'text',
                'text': 'Image analysis response'
            }
        ]
    }]
    mock_instance.total_tokens_used = 100
    
    # Patch the global assistant instance
    patcher = patch('app.assistant', new=mock_instance)
    patcher.start()
    
    try:
        test_message = {
            'message': 'Analyze this image',
            'image': 'data:image/jpeg;base64,/9j/4AAQSkZJRg=='
        }
        print(f"Sending message with image: {test_message}")
        response = client.post('/chat', json=test_message)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        data = json.loads(response.data)
        print(f"Parsed data: {data}")
        
        # Test each assertion separately
        if response.status_code != 200:
            pytest.fail(f"Expected status 200, got {response.status_code}")
        
        if data.get('response') != "Image analysis response":
            pytest.fail(f"Expected 'Image analysis response', got {data.get('response')}")
        
        if data.get('thinking') is not False:
            pytest.fail(f"Expected thinking False, got {data.get('thinking')}")
        
        if 'token_usage' not in data:
            pytest.fail("Missing token_usage in response")
            
        if not isinstance(data.get('token_usage'), dict):
            pytest.fail(f"Expected token_usage to be dict, got {type(data.get('token_usage'))}")
            
        if 'total_tokens' not in data['token_usage']:
            pytest.fail("Missing total_tokens in token_usage")
            
        if 'max_tokens' not in data['token_usage']:
            pytest.fail("Missing max_tokens in token_usage")
            
        if 'tool_name' not in data:
            pytest.fail("Missing tool_name in response")
    finally:
        patcher.stop()

def test_chat_error_handling(client):
    """Test error handling in chat"""
    print("\n=== Testing chat error handling ===")
    
    # Create a mock instance that will raise an error
    mock_instance = MagicMock()
    mock_instance.chat.side_effect = Exception("Test error")
    mock_instance.conversation_history = []
    mock_instance.total_tokens_used = 0
    
    # Patch the global assistant instance
    patcher = patch('app.assistant', new=mock_instance)
    patcher.start()
    
    try:
        test_message = {'message': 'Hello'}
        print(f"Sending message: {test_message}")
        response = client.post('/chat', json=test_message)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        data = json.loads(response.data)
        print(f"Parsed data: {data}")
        
        # Test each assertion separately
        if response.status_code != 200:
            pytest.fail(f"Expected status 200, got {response.status_code}")
        
        if data.get('response') != "Error: Test error":
            pytest.fail(f"Expected 'Error: Test error', got {data.get('response')}")
        
        if data.get('thinking') is not False:
            pytest.fail(f"Expected thinking False, got {data.get('thinking')}")
        
        if data.get('tool_name') is not None:
            pytest.fail(f"Expected tool_name None, got {data.get('tool_name')}")
        
        if data.get('token_usage') is not None:
            pytest.fail(f"Expected token_usage None, got {data.get('token_usage')}")
    finally:
        patcher.stop()

def test_file_upload(client):
    """Test file upload functionality"""
    from io import BytesIO
    file_content = b'fake image content'
    data = {
        'file': (BytesIO(file_content), 'test.jpg')
    }
    response = client.post('/upload', data=data)
    try:
        assert response.status_code in [200, 400], f"Expected status 200 or 400, got {response.status_code}"  # Either success or validation error
    except AssertionError as e:
        print(f"\nAssertion failed in test_file_upload: {str(e)}")
        raise

def test_reset(client):
    """Test conversation reset functionality"""
    response = client.post('/reset')
    try:
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['status'] == 'success', f"Expected status 'success', got {data.get('status')}"
    except AssertionError as e:
        print(f"\nAssertion failed in test_reset: {str(e)}")
        raise

def test_provider_selection(client):
    """Test provider selection endpoint"""
    # Test getting available providers
    response = client.get('/providers')
    try:
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        data = json.loads(response.data)
        assert 'providers' in data, "Missing providers in response"
        assert isinstance(data['providers'], list), f"Expected providers to be list, got {type(data.get('providers'))}"
        assert 'cborg' in data['providers'], "Missing cborg in providers"
    except AssertionError as e:
        print(f"\nAssertion failed in test_provider_selection: {str(e)}")
        raise

    # Test selecting a provider
    response = client.post('/select_provider', json={'provider': 'cborg'})
    try:
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['success'] is True, f"Expected success True, got {data.get('success')}"
        assert data['provider'] == 'cborg', f"Expected provider 'cborg', got {data.get('provider')}"
        assert 'parameters' in data, "Missing parameters in response"
    except AssertionError as e:
        print(f"\nAssertion failed in test_provider_selection: {str(e)}")
        raise

    # Test selecting an invalid provider
    response = client.post('/select_provider', json={'provider': 'invalid'})
    try:
        assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
        data = json.loads(response.data)
        assert data['success'] is False, f"Expected success False, got {data.get('success')}"
        assert 'error' in data, "Missing error in response"
    except AssertionError as e:
        print(f"\nAssertion failed in test_provider_selection: {str(e)}")
        raise

def test_model_selection(client):
    """Test model selection functionality"""
    print("\n=== Testing model selection ===")
    
    # Test getting models for CBORG provider
    with client.session_transaction() as session:
        session['current_provider'] = 'cborg'
    
    response = client.get('/models')
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    data = json.loads(response.data)
    print(f"Parsed data: {data}")
    
    # Test each assertion separately
    if response.status_code != 200:
        pytest.fail(f"Expected status 200, got {response.status_code}")
    
    if 'models' not in data:
        pytest.fail("Missing models in response")
        
    if not isinstance(data['models'], list):
        pytest.fail(f"Expected models to be list, got {type(data.get('models'))}")
        
    if 'default_model' not in data:
        pytest.fail("Missing default_model in response")
        
    if data['default_model'] not in data['models']:
        pytest.fail(f"Default model {data['default_model']} not in available models")
    
    # Test getting models for Ollama provider
    with client.session_transaction() as session:
        session['current_provider'] = 'ollama'
    
    response = client.get('/models')
    data = json.loads(response.data)
    
    if response.status_code != 200:
        pytest.fail(f"Expected status 200, got {response.status_code}")
    
    if 'models' not in data:
        pytest.fail("Missing models in response")
        
    if not isinstance(data['models'], list):
        pytest.fail(f"Expected models to be list, got {type(data.get('models'))}")
        
    if 'default_model' not in data:
        pytest.fail("Missing default_model in response")
        
    if data['default_model'] not in data['models']:
        pytest.fail(f"Default model {data['default_model']} not in available models")

def test_model_switching(client):
    """Test model switching functionality"""
    print("\n=== Testing model switching ===")
    
    # Test switching model for CBORG provider
    with client.session_transaction() as session:
        session['current_provider'] = 'cborg'
        session['current_model'] = 'lbl/cborg-coder:chat'
    
    response = client.post('/switch_model', json={'model': 'lbl/cborg-coder:chat'})
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    data = json.loads(response.data)
    print(f"Parsed data: {data}")
    
    # Test each assertion separately
    if response.status_code != 200:
        pytest.fail(f"Expected status 200, got {response.status_code}")
    
    if 'success' not in data:
        pytest.fail("Missing success in response")
        
    if data['success'] is not True:
        pytest.fail(f"Expected success True, got {data.get('success')}")
        
    if 'model' not in data:
        pytest.fail("Missing model in response")
        
    if data['model'] != 'lbl/cborg-coder:chat':
        pytest.fail(f"Expected model 'lbl/cborg-coder:chat', got {data.get('model')}")
    
    # Test switching model for Ollama provider
    with client.session_transaction() as session:
        session['current_provider'] = 'ollama'
        session['current_model'] = 'codellama'
    
    response = client.post('/switch_model', json={'model': 'codellama'})
    data = json.loads(response.data)
    
    if response.status_code != 200:
        pytest.fail(f"Expected status 200, got {response.status_code}")
    
    if 'success' not in data:
        pytest.fail("Missing success in response")
        
    if data['success'] is not True:
        pytest.fail(f"Expected success True, got {data.get('success')}")
        
    if 'model' not in data:
        pytest.fail("Missing model in response")
        
    if data['model'] != 'codellama':
        pytest.fail(f"Expected model 'codellama', got {data.get('model')}")
    
    # Test switching to invalid model
    response = client.post('/switch_model', json={'model': 'invalid'})
    data = json.loads(response.data)
    
    if response.status_code != 400:
        pytest.fail(f"Expected status 400, got {response.status_code}")
    
    if 'success' not in data:
        pytest.fail("Missing success in response")
        
    if data['success'] is not False:
        pytest.fail(f"Expected success False, got {data.get('success')}")
        
    if 'error' not in data:
        pytest.fail("Missing error in response")

def test_parameter_configuration(client):
    """Test parameter configuration endpoints"""
    # Set up session with CBORG provider
    with client.session_transaction() as sess:
        sess['current_provider'] = 'cborg'
        sess['current_parameters'] = {
            'temperature': 0.7,
            'top_p': 0.9,
            'seed': None
        }
    
    # Test getting current parameters
    response = client.get('/params')
    try:
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        data = json.loads(response.data)
        assert 'temperature' in data, "Missing temperature in response"
        assert 'top_p' in data, "Missing top_p in response"
        assert 'seed' in data, "Missing seed in response"
        assert data['temperature'] == 0.7, f"Expected temperature 0.7, got {data.get('temperature')}"
        assert data['top_p'] == 0.9, f"Expected top_p 0.9, got {data.get('top_p')}"
        assert data['seed'] is None, f"Expected seed None, got {data.get('seed')}"
    except AssertionError as e:
        print(f"\nAssertion failed in test_parameter_configuration: {str(e)}")
        raise

    # Test updating parameters
    new_params = {
        'temperature': 0.8,
        'top_p': 0.95,
        'seed': 42
    }
    response = client.post('/update_params', json=new_params)
    try:
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['success'] is True, f"Expected success True, got {data.get('success')}"
        assert data['parameters']['temperature'] == 0.8, f"Expected temperature 0.8, got {data.get('parameters', {}).get('temperature')}"
        assert data['parameters']['top_p'] == 0.95, f"Expected top_p 0.95, got {data.get('parameters', {}).get('top_p')}"
        assert data['parameters']['seed'] == 42, f"Expected seed 42, got {data.get('parameters', {}).get('seed')}"
    except AssertionError as e:
        print(f"\nAssertion failed in test_parameter_configuration: {str(e)}")
        raise

    # Test invalid parameter values
    invalid_params = {
        'temperature': 1.5,  # Should be between 0 and 1
        'top_p': -0.1,      # Should be between 0 and 1
        'seed': 'invalid'   # Should be integer or None
    }
    response = client.post('/update_params', json=invalid_params)
    try:
        assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
        data = json.loads(response.data)
        assert data['success'] is False, f"Expected success False, got {data.get('success')}"
        assert 'error' in data, "Missing error in response"
    except AssertionError as e:
        print(f"\nAssertion failed in test_parameter_configuration: {str(e)}")
        raise
