import unittest
from unittest.mock import patch, MagicMock
from ce3 import Assistant
from tools.base import BaseTool, ProviderContext
import types
import os
from ce3 import Config

class TestChatEngine(unittest.TestCase):
    def setUp(self):
        self.engine = Assistant(provider='cborg')
        self.engine.provider_context = ProviderContext(provider_type='cborg')

    def test_cborg_tool_formatting(self):
        """Test that tools are formatted correctly for CBORG"""
        # Create a mock tool
        class MockTool(BaseTool):
            name = "mock_tool"
            description = "A mock tool for testing"
            input_schema = {
                "type": "object",
                "properties": {
                    "test": {
                        "type": "string",
                        "description": "Test parameter"
                    }
                }
            }
            def _execute(self, **kwargs):
                return {"response": "mock response"}

        # Create a mock module containing the tool
        mock_module = types.ModuleType('mock_module')
        mock_module.MockTool = MockTool
        mock_module.__name__ = 'mock_module'

        # Create empty tools list
        tools = []
        
        # Extract the mock tool
        self.engine._extract_tools_from_module(mock_module, tools)

        # Verify tool formatting
        self.assertEqual(len(tools), 1)
        tool = tools[0]
        
        # Check tool has both toolSpec and function fields
        self.assertIn('toolSpec', tool)
        self.assertIn('function', tool)
        toolSpec = tool['toolSpec']
        function = tool['function']
        
        # Both fields should have same content
        self.assertEqual(toolSpec, function)
        
        # Check content is correct
        self.assertEqual(toolSpec['name'], "mock_tool")
        self.assertEqual(toolSpec['description'], "A mock tool for testing")
        self.assertEqual(toolSpec['parameters'], {
            "type": "object",
            "properties": {
                "test": {
                    "type": "string",
                    "description": "Test parameter"
                }
            }
        })

    def test_cborg_tool_validation(self):
        """Test that tools are properly validated for CBORG"""
        def create_mock_module(tool_class):
            mock_module = types.ModuleType('mock_module')
            mock_module.MockTool = tool_class
            mock_module.__name__ = 'mock_module'
            return mock_module

        # Test empty name
        class EmptyNameTool(BaseTool):
            name = ""
            description = "A mock tool for testing"
            input_schema = {"type": "object", "properties": {}}
            def _execute(self, **kwargs): return {}

        tools = []
        self.engine._extract_tools_from_module(create_mock_module(EmptyNameTool), tools)
        self.assertEqual(len(tools), 0, "Tool with empty name should be skipped")

        # Test invalid name characters
        class InvalidNameTool(BaseTool):
            name = "invalid@name!"
            description = "A mock tool for testing"
            input_schema = {"type": "object", "properties": {}}
            def _execute(self, **kwargs): return {}

        tools = []
        self.engine._extract_tools_from_module(create_mock_module(InvalidNameTool), tools)
        self.assertEqual(len(tools), 0, "Tool with invalid name characters should be skipped")

        # Test empty description
        class EmptyDescriptionTool(BaseTool):
            name = "valid_name"
            description = ""
            input_schema = {"type": "object", "properties": {}}
            def _execute(self, **kwargs): return {}

        tools = []
        self.engine._extract_tools_from_module(create_mock_module(EmptyDescriptionTool), tools)
        self.assertEqual(len(tools), 0, "Tool with empty description should be skipped")

        # Test valid tool
        class ValidTool(BaseTool):
            name = "valid-name_123"
            description = "A valid description"
            input_schema = {"type": "object", "properties": {}}
            def _execute(self, **kwargs): return {}

        tools = []
        self.engine._extract_tools_from_module(create_mock_module(ValidTool), tools)
        self.assertEqual(len(tools), 1, "Valid tool should be added")
        self.assertEqual(tools[0]['toolSpec']['name'], "valid-name_123")

    def test_anthropic_provider_initialization(self):
        """Test initializing the assistant with Anthropic provider"""
        # Set up environment
        os.environ['ANTHROPIC_API_KEY'] = 'test_key'
        assistant = Assistant(provider='anthropic')
        
        self.assertEqual(assistant.provider, 'anthropic')
        self.assertEqual(assistant.model, Config.PROVIDER_MODELS['anthropic'])
        self.assertEqual(assistant.base_url, 'https://api.anthropic.com')
        self.assertEqual(assistant.api_key, 'test_key')

    def test_anthropic_provider_missing_key(self):
        """Test error when Anthropic API key is missing"""
        # Remove API key from environment
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
        
        with self.assertRaises(ValueError) as context:
            Assistant(provider='anthropic')
        
        self.assertIn('No ANTHROPIC_API_KEY found', str(context.exception))

    def test_anthropic_provider_completion(self):
        """Test getting completion from Anthropic provider"""
        # Set up environment
        os.environ['ANTHROPIC_API_KEY'] = 'test_key'
        assistant = Assistant(provider='anthropic')
        
        # Mock the requests.post call
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'content': [{'type': 'text', 'text': 'Test response'}]
            }
            mock_post.return_value = mock_response
            
            # Add a test message
            assistant.conversation_history.append({
                'role': 'user',
                'content': 'Test message'
            })
            
            # Get completion
            response = assistant._get_completion()
            
            # Verify the request
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            
            # Check URL
            self.assertEqual(args[0], 'https://api.anthropic.com/v1/messages')
            
            # Check headers
            self.assertEqual(kwargs['headers']['anthropic-version'], '2023-06-01')
            self.assertEqual(kwargs['headers']['x-api-key'], 'test_key')
            
            # Check request body
            self.assertEqual(kwargs['json']['model'], Config.PROVIDER_MODELS['anthropic'])
            self.assertEqual(kwargs['json']['temperature'], assistant.temperature)
            self.assertEqual(kwargs['json']['tool_choice'], 'auto')
            self.assertTrue('tools' in kwargs['json'])
            self.assertTrue('messages' in kwargs['json'])

if __name__ == '__main__':
    unittest.main()
