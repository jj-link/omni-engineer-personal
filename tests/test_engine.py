"""Tests for the engine module."""

import os
import unittest
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

class TestEngine(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test environment."""
        # Mock clients
        self.mock_ollama = AsyncMock()
        self.mock_tavily = Mock()
        
        # Store patches
        self.patches = [
            patch('omni_core.engine.client', self.mock_ollama),
            patch('tavily.TavilyClient', return_value=self.mock_tavily)
        ]
        
        # Start patches
        for p in self.patches:
            p.start()
        
        # Set up default mock response
        self.mock_ollama.chat.return_value = {
            'message': {
                'content': 'Test response',
                'tool_calls': []
            }
        }

    async def asyncTearDown(self):
        """Clean up test environment."""
        for p in self.patches:
            p.stop()

    async def test_chat_with_ollama_basic(self):
        """Test basic chat functionality without tools"""
        response = await chat_with_ollama("Test message")
        self.assertIsNotNone(response)
        self.assertIsInstance(response, tuple)
        self.assertIn("Test response", response[0])

    async def test_chat_with_ollama_tool_calls(self):
        """Test chat functionality with tool calls"""
        self.mock_ollama.chat.return_value = {
            'message': {
                'content': 'Using read_file tool',
                'tool_calls': [{
                    'type': 'function',
                    'function': {
                        'name': 'read_file',
                        'arguments': {'path': 'test.txt'}
                    }
                }]
            }
        }
        
        response = await chat_with_ollama("Read a file")
        self.assertIn("Using read_file tool", response[0])
        self.assertEqual(len(response[1]), 1)
        self.assertEqual(response[1][0]['function']['name'], 'read_file')

    async def test_chat_with_ollama_error(self):
        """Test chat error handling"""
        self.mock_ollama.chat.side_effect = Exception("Test error")
        
        with self.assertRaises(Exception) as cm:
            await chat_with_ollama("Test message")
        self.assertEqual(str(cm.exception), "Test error")

    async def test_execute_tool(self):
        """Test tool execution"""
        # Mock tool
        mock_tool = AsyncMock()
        mock_tool.return_value = "Tool result"
        
        # Test successful execution
        result = await execute_tool({
            'name': 'test_tool',
            'arguments': {'arg1': 'value1'}
        }, {'test_tool': mock_tool})
        
        self.assertEqual(result, "Tool result")
        mock_tool.assert_called_once_with(arg1='value1')

    async def test_execute_tool_error(self):
        """Test tool execution error handling"""
        # Mock tool that raises an error
        mock_tool = AsyncMock()
        mock_tool.side_effect = Exception("Tool error")
        
        with self.assertRaises(Exception) as cm:
            await execute_tool({
                'name': 'test_tool',
                'arguments': {'arg1': 'value1'}
            }, {'test_tool': mock_tool})
        self.assertEqual(str(cm.exception), "Tool error")

    def test_parse_goals(self):
        """Test goal parsing"""
        response = "Goals:\n1. Goal 1\n2. Goal 2\n3. Goal 3"
        goals = parse_goals(response)
        
        self.assertEqual(len(goals), 3)
        self.assertEqual(goals[0], "Goal 1")
        self.assertEqual(goals[1], "Goal 2")
        self.assertEqual(goals[2], "Goal 3")

    async def test_execute_goals(self):
        """Test goal execution"""
        goals = ["Goal 1", "Goal 2"]
        mock_execute = AsyncMock()
        
        await execute_goals(goals, mock_execute)
        self.assertEqual(mock_execute.call_count, len(goals))

    def test_reset_functions(self):
        """Test reset functions"""
        # Test conversation reset
        reset_conversation()
        # No assertions needed as this just clears a global variable
        
        # Test code editor memory reset
        with patch('builtins.open', mock_open()) as mock_file:
            reset_code_editor_memory()
            mock_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()
