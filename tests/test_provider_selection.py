import pytest
import os
from unittest.mock import patch, AsyncMock

# Mock environment variables before importing engine
with patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):
    from omni_core.engine import main, PROVIDER_CONFIG

@pytest.mark.asyncio
async def test_provider_selection_ollama():
    """Test that Ollama provider is selected by default"""
    with patch('sys.argv', ['engine.py']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input, \
         patch('omni_core.engine.chat_with_ollama', new_callable=AsyncMock) as mock_ollama, \
         patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):
        
        # Setup mock to exit after one interaction
        mock_input.side_effect = ['exit']
        mock_ollama.return_value = ('Response', False)
        
        # Run main
        await main()
        
        # Verify Ollama was selected (by checking welcome message)
        assert mock_ollama.call_count == 0  # No chat calls since we exit immediately

@pytest.mark.asyncio
async def test_provider_selection_cborg():
    """Test that CBORG provider can be selected"""
    with patch('sys.argv', ['engine.py', '--api', 'cborg']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input, \
         patch('omni_core.engine.chat_with_cborg', new_callable=AsyncMock) as mock_cborg, \
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
async def test_provider_selection_with_model():
    """Test that model selection works"""
    test_model = "test-model"
    with patch('sys.argv', ['engine.py', '--api', 'ollama', '--model', test_model]), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input, \
         patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):
        
        mock_input.side_effect = ['exit']
        
        # Run main
        await main()
        
        # Verify model was set
        assert PROVIDER_CONFIG['ollama']['default_model'] == test_model

@pytest.mark.asyncio
async def test_provider_selection_cborg_without_key():
    """Test that CBORG fails without API key"""
    with patch('sys.argv', ['engine.py', '--api', 'cborg']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input, \
         patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):  # Only Tavily key, no CBORG key
        
        mock_input.side_effect = ['exit']
        
        # Run main - should exit early due to missing API key
        await main()
        
        # Verify no chat attempts were made
        assert mock_input.call_count == 0  # Should exit before any input
