import unittest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch

from tools.base import BaseTool, ProviderContext
from omni_core.engine import execute_tool, tools_registry

# Test data
VALID_OLLAMA_CONTEXT = {
    "provider_type": "ollama",
    "model": "codellama",
    "parameters": {
        "temperature": 0.7,
        "top_p": 0.9,
        "seed": None
    }
}

VALID_CBORG_CONTEXT = {
    "provider_type": "cborg",
    "model": "lbl/cborg-coder:chat",
    "parameters": {
        "temperature": 0.0,
        "top_p": 0.9,
        "seed": None
    }
}

class MockTool(BaseTool):
    """Mock tool for testing"""
    name = "mock_tool"
    description = "Mock tool for testing"
    input_schema = {
        "type": "object",
        "properties": {
            "test_input": {
                "type": "string",
                "description": "Test input"
            }
        }
    }

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        return {"result": f"mock_result: {kwargs.get('test_input', '')}"}

class TestToolExecution(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.ollama_context = ProviderContext(**VALID_OLLAMA_CONTEXT)
        self.cborg_context = ProviderContext(**VALID_CBORG_CONTEXT)

    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()

    def test_tools_registry_structure(self):
        """Test that tools registry has correct structure"""
        self.assertIn("file_editor", tools_registry)
        tool_info = tools_registry["file_editor"]
        self.assertIn("class", tool_info)
        self.assertIn("supported_providers", tool_info)
        self.assertIsInstance(tool_info["supported_providers"], list)

    def test_tool_provider_support(self):
        """Test tool provider support validation"""
        file_editor = tools_registry["file_editor"]["class"]()
        self.assertIn("ollama", tools_registry["file_editor"]["supported_providers"])
        self.assertIn("cborg", tools_registry["file_editor"]["supported_providers"])

    def test_execute_tool_ollama_format(self):
        """Test executing tool with Ollama function call format"""
        async def run_test():
            tool_call = {
                "function": {
                    "name": "mock_tool",
                    "arguments": {
                        "test_input": "ollama_test"
                    }
                }
            }
            result = await execute_tool(tool_call, self.ollama_context)
            self.assertEqual(result["content"], "mock_result: ollama_test")
            self.assertFalse(result["is_error"])

        self.loop.run_until_complete(run_test())

    def test_execute_tool_cborg_format(self):
        """Test executing tool with CBORG function call format"""
        async def run_test():
            tool_call = {
                "name": "mock_tool",
                "arguments": {
                    "test_input": "cborg_test"
                }
            }
            result = await execute_tool(tool_call, self.cborg_context)
            self.assertEqual(result["content"], "mock_result: cborg_test")
            self.assertFalse(result["is_error"])

        self.loop.run_until_complete(run_test())

    def test_execute_tool_invalid_format(self):
        """Test executing tool with invalid function call format"""
        async def run_test():
            tool_call = {
                "invalid": "format"
            }
            result = await execute_tool(tool_call, self.ollama_context)
            self.assertTrue(result["is_error"])
            self.assertIn("Invalid tool call format", result["content"])

        self.loop.run_until_complete(run_test())

    def test_execute_tool_unknown_tool(self):
        """Test executing unknown tool"""
        async def run_test():
            tool_call = {
                "function": {
                    "name": "unknown_tool",
                    "arguments": {}
                }
            }
            result = await execute_tool(tool_call, self.ollama_context)
            self.assertTrue(result["is_error"])
            self.assertIn("Unknown tool", result["content"])

        self.loop.run_until_complete(run_test())

    def test_execute_tool_missing_arguments(self):
        """Test executing tool with missing required arguments"""
        async def run_test():
            tool_call = {
                "function": {
                    "name": "mock_tool",
                    "arguments": {}
                }
            }
            result = await execute_tool(tool_call, self.ollama_context)
            self.assertFalse(result["is_error"])  # Our mock tool handles missing arguments
            self.assertEqual(result["content"], "mock_result: ")

        self.loop.run_until_complete(run_test())

    def test_execute_tool_provider_specific_response(self):
        """Test that tool responses are formatted according to provider"""
        async def run_test():
            # Test Ollama format
            ollama_call = {
                "function": {
                    "name": "mock_tool",
                    "arguments": {"test_input": "test"}
                }
            }
            ollama_result = await execute_tool(ollama_call, self.ollama_context)
            self.assertIn("content", ollama_result)
            self.assertIn("is_error", ollama_result)

            # Test CBORG format
            cborg_call = {
                "name": "mock_tool",
                "arguments": {"test_input": "test"}
            }
            cborg_result = await execute_tool(cborg_call, self.cborg_context)
            self.assertIn("content", cborg_result)
            self.assertIn("is_error", cborg_result)

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
