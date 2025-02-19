import pytest
import os
from unittest.mock import patch, AsyncMock
import copy

# Mock environment variables before importing engine
with patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):
    from omni_core.engine import main, PROVIDER_CONFIG

# Store original config for reset
ORIGINAL_CONFIG = copy.deepcopy(PROVIDER_CONFIG)

@pytest.fixture(autouse=True)
def reset_config():
    """Reset PROVIDER_CONFIG before each test"""
    global PROVIDER_CONFIG
    PROVIDER_CONFIG.clear()
    PROVIDER_CONFIG.update(copy.deepcopy(ORIGINAL_CONFIG))

@pytest.mark.asyncio
async def test_default_parameters():
    """Test that default parameters are set correctly"""
    with patch('sys.argv', ['engine.py']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input:
        
        mock_input.side_effect = ['exit']
        
        # Run main
        await main()
        
        # Check default parameters
        assert PROVIDER_CONFIG['ollama']['parameters']['temperature'] == 0.7
        assert PROVIDER_CONFIG['ollama']['parameters']['top_p'] == 0.9
        assert PROVIDER_CONFIG['ollama']['parameters']['seed'] is None

@pytest.mark.asyncio
async def test_temperature_parameter():
    """Test that temperature parameter can be set"""
    with patch('sys.argv', ['engine.py', '--temperature', '0.5']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input:
        
        mock_input.side_effect = ['exit']
        
        # Run main
        await main()
        
        # Check temperature was set
        assert PROVIDER_CONFIG['ollama']['parameters']['temperature'] == 0.5

@pytest.mark.asyncio
async def test_invalid_temperature():
    """Test that invalid temperature is handled gracefully"""
    with patch('sys.argv', ['engine.py', '--temperature', '1.5']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input:
        
        mock_input.side_effect = ['exit']
        
        # Run main
        await main()
        
        # Check temperature remains at default
        assert PROVIDER_CONFIG['ollama']['parameters']['temperature'] == 0.7

@pytest.mark.asyncio
async def test_top_p_parameter():
    """Test that top-p parameter can be set"""
    with patch('sys.argv', ['engine.py', '--top-p', '0.8']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input:
        
        mock_input.side_effect = ['exit']
        
        # Run main
        await main()
        
        # Check top-p was set
        assert PROVIDER_CONFIG['ollama']['parameters']['top_p'] == 0.8

@pytest.mark.asyncio
async def test_seed_parameter():
    """Test that seed parameter can be set"""
    with patch('sys.argv', ['engine.py', '--seed', '42']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input:
        
        mock_input.side_effect = ['exit']
        
        # Run main
        await main()
        
        # Check seed was set
        assert PROVIDER_CONFIG['ollama']['parameters']['seed'] == 42

@pytest.mark.asyncio
async def test_parameters_with_cborg():
    """Test that parameters work with CBORG provider"""
    with patch('sys.argv', ['engine.py', '--api', 'cborg', '--temperature', '0.3', '--top-p', '0.95', '--seed', '123']), \
         patch('omni_core.engine.get_user_input', new_callable=AsyncMock) as mock_input, \
         patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key', 'CBORG_API_KEY': 'test_key'}):
        
        mock_input.side_effect = ['exit']
        
        # Run main
        await main()
        
        # Check parameters were set for CBORG
        assert PROVIDER_CONFIG['cborg']['parameters']['temperature'] == 0.3
        assert PROVIDER_CONFIG['cborg']['parameters']['top_p'] == 0.95
        assert PROVIDER_CONFIG['cborg']['parameters']['seed'] == 123
