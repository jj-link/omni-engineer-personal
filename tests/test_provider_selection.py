import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Mock environment variables before importing engine
with patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):
    from omni_core.engine import main, PROVIDER_CONFIG

@pytest.fixture
def mock_input():
    """Mock user input"""
    with patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input:
        yield mock_input

@pytest.fixture
def mock_ollama():
    """Mock Ollama chat"""
    with patch('omni_core.engine.chat_with_ollama', new_callable=AsyncMock) as mock_ollama:
        yield mock_ollama

@pytest.fixture
def mock_cborg():
    """Mock CBORG chat"""
    with patch('omni_core.engine.chat_with_cborg', new_callable=AsyncMock) as mock_cborg:
        yield mock_cborg

@pytest.fixture
def mock_ollama_list():
    """Mock Ollama list command output"""
    return """\
NAME              ID    SIZE   MODIFIED
codellama:latest  abc   5.0GB  2 weeks ago
llama2:latest     def   4.2GB  3 weeks ago
mistral:latest    ghi   4.8GB  1 week ago
"""

@pytest.mark.asyncio
async def test_provider_selection_ollama(mock_input, mock_ollama):
    """Test that Ollama provider is selected by default"""
    with patch('sys.argv', ['engine.py']):
        
        # Setup mock to exit after one interaction
        mock_input.side_effect = ['exit']
        mock_ollama.return_value = ('Response', False)
        
        # Run main
        await main()
        
        # Verify Ollama was selected (by checking welcome message)
        assert mock_ollama.call_count == 0  # No chat calls since we exit immediately

@pytest.mark.asyncio
async def test_provider_selection_cborg(mock_input, mock_cborg):
    """Test that CBORG provider can be selected"""
    with patch('sys.argv', ['engine.py', '--api', 'cborg']), \
         patch.dict(os.environ, {
             'TAVILY_API_KEY': 'test_key',
             'CBORG_API_KEY': 'test_key'
         }):
        
        # Setup mock to send one message then exit
        mock_input.side_effect = ['Hello', 'exit']
        mock_cborg.return_value = ('Response', False)
        
        # Run main
        await main()
        
        # Verify CBORG was called
        mock_cborg.assert_called_once_with('Hello')

@pytest.mark.asyncio
async def test_provider_selection_with_model(mock_input):
    """Test that model selection works"""
    test_model = "test-model"
    with patch('sys.argv', ['engine.py', '--api', 'ollama', '--model', test_model]), \
         patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):
        
        mock_input.side_effect = ['exit']
        
        # Run main
        await main()
        
        # Verify model was set
        assert PROVIDER_CONFIG['ollama']['default_model'] == test_model

@pytest.mark.asyncio
async def test_provider_selection_cborg_without_key(mock_input):
    """Test that CBORG fails without API key"""
    with patch('sys.argv', ['engine.py', '--api', 'cborg']), \
         patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):  # Only Tavily key, no CBORG key
        
        mock_input.side_effect = ['exit']
        
        # Run main - should exit early due to missing API key
        await main()
        
        # Verify no chat attempts were made
        assert mock_input.call_count == 0  # Should exit before any input

@pytest.mark.asyncio
async def test_get_models_ollama(mock_ollama_list):
    """Test getting models when Ollama is the current provider"""
    with patch('subprocess.run') as mock_run:
        # Mock successful Ollama list command
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = mock_ollama_list
        mock_run.return_value = mock_process
        
        # Run main
        await main()
        
        # Verify Ollama was called
        mock_run.assert_called_once()

@pytest.mark.asyncio
async def test_get_models_cborg():
    """Test getting models when CBORG is the current provider"""
    with patch('requests.get') as mock_get:
        # Mock successful CBORG list response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'model_groups': {
                'lbl': ['model1', 'model2'],
                'openai': ['model3', 'model4'],
                'anthropic': ['model5', 'model6']
            },
            'capabilities': ['capability1', 'capability2'],
            'descriptions': ['description1', 'description2']
        }
        mock_get.return_value = mock_response
        
        # Run main
        await main()
        
        # Verify CBORG was called
        mock_get.assert_called_once()
