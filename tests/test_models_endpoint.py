import pytest
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_ollama_list():
    """Mock Ollama list command output"""
    return """\
NAME              ID    SIZE   MODIFIED
codellama:latest  abc   5.0GB  2 weeks ago
llama2:latest     def   4.2GB  3 weeks ago
mistral:latest    ghi   4.8GB  1 week ago
"""

def test_get_models_ollama(client, mock_ollama_list):
    """Test getting models when Ollama is the current provider"""
    with client.session_transaction() as sess:
        sess['current_provider'] = 'ollama'
    
    with patch('subprocess.run') as mock_run:
        # Mock successful Ollama list command
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = mock_ollama_list
        mock_run.return_value = mock_process
        
        response = client.get('/models')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['provider'] == 'ollama'
        assert data['format'] == 'flat'
        assert len(data['models']) == 3
        
        # Verify model data
        model = data['models'][0]
        assert model['name'] == 'codellama:latest'
        assert model['size'] == '5.0GB'
        assert model['modified'] == '2 weeks ago'

def test_get_models_cborg(client):
    """Test getting models when CBORG is the current provider"""
    with client.session_transaction() as sess:
        sess['current_provider'] = 'cborg'
    
    response = client.get('/models')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['provider'] == 'cborg'
    assert data['format'] == 'grouped'
    
    # Verify model groups
    assert 'model_groups' in data
    assert 'lbl' in data['model_groups']
    assert 'openai' in data['model_groups']
    assert 'anthropic' in data['model_groups']
    
    # Verify model metadata
    assert 'capabilities' in data
    assert 'descriptions' in data
    assert len(data['capabilities']) > 0
    assert len(data['descriptions']) > 0
