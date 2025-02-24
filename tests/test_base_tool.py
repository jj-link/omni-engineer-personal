import unittest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch

from tools.base import BaseTool, ProviderContext

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

# Sample tool responses
OLLAMA_RESPONSE = {
    "response": "Tool execution result",
    "done": True
}

CBORG_RESPONSE = {
    "choices": [{
        "message": {
            "content": "Tool execution result",
            "role": "assistant"
        }
    }]
}

class TestProviderContext(unittest.TestCase):
    def test_init_with_valid_ollama_context(self):
        """Test initialization with valid Ollama context"""
        context = ProviderContext(**VALID_OLLAMA_CONTEXT)
        self.assertEqual(context.provider_type, "ollama")
        self.assertEqual(context.model, "codellama")
        self.assertEqual(context.parameters["temperature"], 0.7)

    def test_init_with_valid_cborg_context(self):
        """Test initialization with valid CBORG context"""
        context = ProviderContext(**VALID_CBORG_CONTEXT)
        self.assertEqual(context.provider_type, "cborg")
        self.assertEqual(context.model, "lbl/cborg-coder:chat")
        self.assertEqual(context.parameters["temperature"], 0.0)

    def test_init_with_invalid_provider(self):
        """Test initialization with invalid provider type"""
        with self.assertRaises(ValueError) as cm:
            ProviderContext(provider_type="invalid", model="test", parameters={})
        self.assertIn("Invalid provider type", str(cm.exception))

    def test_validate_parameters(self):
        """Test parameter validation"""
        with self.assertRaises(ValueError) as cm:
            ProviderContext(
                provider_type="ollama",
                model="codellama",
                parameters={"temperature": 1.5}
            )
        self.assertIn("Temperature must be between 0 and 1", str(cm.exception))

class MockTool(BaseTool):
    """Mock tool class for testing BaseTool functionality"""
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
        return {"result": "test_success"}

class TestBaseTool(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.mock_tool = MockTool()
        self.mock_tool_with_ollama = MockTool(
            provider_context=ProviderContext(**VALID_OLLAMA_CONTEXT)
        )
        self.mock_tool_with_cborg = MockTool(
            provider_context=ProviderContext(**VALID_CBORG_CONTEXT)
        )
        # Create event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up after tests"""
        self.loop.close()

    def test_init_without_context(self):
        """Test tool initialization without provider context"""
        self.assertIsNone(self.mock_tool.provider_context)
        self.assertEqual(self.mock_tool.name, "mock_tool")

    def test_init_with_ollama_context(self):
        """Test tool initialization with Ollama context"""
        self.assertEqual(self.mock_tool_with_ollama.provider_context.provider_type, "ollama")
        self.assertEqual(self.mock_tool_with_ollama.provider_context.model, "codellama")

    def test_init_with_cborg_context(self):
        """Test tool initialization with CBORG context"""
        self.assertEqual(self.mock_tool_with_cborg.provider_context.provider_type, "cborg")
        self.assertEqual(self.mock_tool_with_cborg.provider_context.model, "lbl/cborg-coder:chat")

    def test_parse_ollama_response(self):
        """Test parsing Ollama response format"""
        result = self.loop.run_until_complete(
            self.mock_tool_with_ollama.parse_response(OLLAMA_RESPONSE)
        )
        self.assertEqual(result, "Tool execution result")

    def test_parse_cborg_response(self):
        """Test parsing CBORG response format"""
        result = self.loop.run_until_complete(
            self.mock_tool_with_cborg.parse_response(CBORG_RESPONSE)
        )
        self.assertEqual(result, "Tool execution result")

    def test_execute_with_invalid_input(self):
        """Test execution with invalid input schema"""
        async def run_test():
            with patch.object(MockTool, '_validate_input', return_value=False):
                with self.assertRaises(Exception) as cm:
                    await self.mock_tool.execute(invalid_param="test")
                self.assertIn("Tool execution failed: Invalid input", str(cm.exception))
        
        self.loop.run_until_complete(run_test())

    def test_execute_with_provider_error(self):
        """Test handling of provider-specific errors"""
        async def run_test():
            with patch.object(MockTool, '_execute', side_effect=Exception("Provider error")):
                with self.assertRaises(Exception) as cm:
                    await self.mock_tool_with_ollama.execute(test_input="test")
                self.assertIn("Provider error", str(cm.exception))
        
        self.loop.run_until_complete(run_test())

    def test_successful_execution(self):
        """Test successful tool execution"""
        result = self.loop.run_until_complete(
            self.mock_tool.execute(test_input="test")
        )
        self.assertEqual(result, {"result": "test_success"})

    def test_validate_provider_capabilities(self):
        """Test validation of provider capabilities"""
        self.assertTrue(self.mock_tool_with_ollama.validate_provider_capabilities())

if __name__ == '__main__':
    unittest.main()
