import pytest
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock environment variables
os.environ["TAVILY_API_KEY"] = "mock_tavily_key"

from omni_core.engine import (
    chat_with_ollama,
    execute_tool,
    parse_goals,
    execute_goals,
    reset_conversation,
    reset_code_editor_memory,
)

@pytest.fixture
def mock_ollama_client():
    with patch('omni_core.engine.client') as mock_client:
        mock_response = {
            'message': {
                'content': 'Test response',
                'tool_calls': []
            }
        }
        mock_client.chat = AsyncMock(return_value=mock_response)
        yield mock_client

@pytest.fixture
def mock_tavily():
    with patch('tavily.TavilyClient') as mock_tavily:
        yield mock_tavily

@pytest.mark.asyncio
async def test_chat_with_ollama_basic(mock_ollama_client):
    """Test basic chat functionality without tools"""
    response = await chat_with_ollama("Test message")
    assert response is not None
    assert isinstance(response, tuple)
    assert "Test response" in response[0]

@pytest.mark.asyncio
async def test_chat_with_ollama_tool_calls(mock_ollama_client):
    """Test chat functionality with tool calls"""
    mock_ollama_client.chat.return_value = {
        'message': {
            'content': 'Using read_file tool',
            'tool_calls': [{
                'function': {
                    'name': 'read_file',
                    'arguments': '{"path": "test.txt"}'
                }
            }]
        }
    }

    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data='test content')):
        response = await chat_with_ollama("Read test.txt")
        assert response is not None
        assert isinstance(response, tuple)
        assert "Using read_file tool" in response[0]

@pytest.mark.asyncio
async def test_chat_with_ollama_error(mock_ollama_client):
    """Test chat error handling"""
    mock_ollama_client.chat.side_effect = Exception("API error")
    response = await chat_with_ollama("Test message")
    assert response is not None
    assert isinstance(response, tuple)
    assert "error communicating with the AI" in response[0]
    assert response[1] is False

@pytest.mark.asyncio
async def test_execute_tool():
    """Test tool execution with a mock tool"""
    mock_tool = {
        "type": "function",
        "function": {
            "name": "read_file",
            "arguments": '{"path": "test.txt"}'
        }
    }
    
    with patch('builtins.open', mock_open(read_data="test content")):
        with patch('os.path.exists', return_value=True):
            result = await execute_tool(mock_tool)
            assert result is not None

@pytest.mark.asyncio
async def test_execute_tool_error():
    """Test tool execution error handling"""
    mock_tool = {
        "type": "function",
        "function": {
            "name": "read_file",
            "arguments": '{"path": "nonexistent.txt"}'
        }
    }
    
    with patch('os.path.exists', return_value=False):
        result = await execute_tool(mock_tool)
        assert result["is_error"] is True
        assert "File not found" in result["content"]

def test_parse_goals():
    """Test goal parsing from response"""
    test_response = """
    Goals:
    1. Create test file
    2. Add test cases
    3. Run tests
    """
    with patch('omni_core.engine.re.findall', return_value=["Create test file", "Add test cases", "Run tests"]):
        goals = parse_goals(test_response)
        assert len(goals) == 3
        assert "Create test file" in goals

@pytest.mark.asyncio
async def test_reset_functions():
    """Test reset functions"""
    reset_conversation()
    from omni_core.engine import conversation_history
    assert len(conversation_history) == 0
    
    reset_code_editor_memory()
    from omni_core.engine import code_editor_memory, code_editor_files
    assert len(code_editor_memory) == 0
    assert len(code_editor_files) == 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
