"""Tests for parameter handling."""

import os
import unittest
from unittest.mock import patch, AsyncMock
import copy

# Mock environment variables before importing engine
with patch.dict(os.environ, {'TAVILY_API_KEY': 'test_key'}):
    from omni_core.engine import main, PROVIDER_CONFIG

# Store original config for reset
ORIGINAL_CONFIG = copy.deepcopy(PROVIDER_CONFIG)

class TestParameters(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test environment."""
        # Reset config before each test
        global PROVIDER_CONFIG
        PROVIDER_CONFIG.clear()
        PROVIDER_CONFIG.update(copy.deepcopy(ORIGINAL_CONFIG))
        
        # Mock user input
        self.mock_input = AsyncMock()
        self.input_patcher = patch('omni_core.engine.get_user_input', new=self.mock_input)
        self.input_patcher.start()

    async def asyncTearDown(self):
        """Clean up test environment."""
        self.input_patcher.stop()

    async def test_default_parameters(self):
        """Test that default parameters are set correctly"""
        with patch('sys.argv', ['engine.py']):
            self.mock_input.side_effect = ['exit']
            
            # Run main
            await main()
            
            # Check default parameters
            self.assertEqual(PROVIDER_CONFIG['ollama']['parameters']['temperature'], 0.7)
            self.assertEqual(PROVIDER_CONFIG['ollama']['parameters']['top_p'], 0.9)
            self.assertIsNone(PROVIDER_CONFIG['ollama']['parameters']['seed'])

    async def test_temperature_parameter(self):
        """Test that temperature parameter can be set"""
        with patch('sys.argv', ['engine.py', '--temperature', '0.5']):
            self.mock_input.side_effect = ['exit']
            
            # Run main
            await main()
            
            # Check temperature was set
            self.assertEqual(PROVIDER_CONFIG['ollama']['parameters']['temperature'], 0.5)

    async def test_invalid_temperature(self):
        """Test that invalid temperature values are rejected"""
        test_cases = [
            ['engine.py', '--temperature', '-0.1'],
            ['engine.py', '--temperature', '1.1'],
            ['engine.py', '--temperature', 'invalid']
        ]
        
        for args in test_cases:
            with self.subTest(args=args):
                with patch('sys.argv', args), \
                     self.assertRaises(ValueError):
                    await main()

    async def test_top_p_parameter(self):
        """Test that top-p parameter can be set"""
        with patch('sys.argv', ['engine.py', '--top-p', '0.5']):
            self.mock_input.side_effect = ['exit']
            
            # Run main
            await main()
            
            # Check top-p was set
            self.assertEqual(PROVIDER_CONFIG['ollama']['parameters']['top_p'], 0.5)

    async def test_invalid_top_p(self):
        """Test that invalid top-p values are rejected"""
        test_cases = [
            ['engine.py', '--top-p', '-0.1'],
            ['engine.py', '--top-p', '1.1'],
            ['engine.py', '--top-p', 'invalid']
        ]
        
        for args in test_cases:
            with self.subTest(args=args):
                with patch('sys.argv', args), \
                     self.assertRaises(ValueError):
                    await main()

    async def test_seed_parameter(self):
        """Test that seed parameter can be set"""
        with patch('sys.argv', ['engine.py', '--seed', '42']):
            self.mock_input.side_effect = ['exit']
            
            # Run main
            await main()
            
            # Check seed was set
            self.assertEqual(PROVIDER_CONFIG['ollama']['parameters']['seed'], 42)

    async def test_invalid_seed(self):
        """Test that invalid seed values are rejected"""
        test_cases = [
            ['engine.py', '--seed', '-1'],
            ['engine.py', '--seed', 'invalid']
        ]
        
        for args in test_cases:
            with self.subTest(args=args):
                with patch('sys.argv', args), \
                     self.assertRaises(ValueError):
                    await main()

    async def test_parameters_with_cborg(self):
        """Test that parameters work with CBORG provider"""
        with patch('sys.argv', ['engine.py', '--provider', 'cborg', 
                              '--temperature', '0.5', '--top-p', '0.8']):
            self.mock_input.side_effect = ['exit']
            
            # Set required environment variable
            os.environ['CBORG_API_KEY'] = 'test_key'
            
            # Run main
            await main()
            
            # Check parameters were set for CBORG
            self.assertEqual(PROVIDER_CONFIG['cborg']['parameters']['temperature'], 0.5)
            self.assertEqual(PROVIDER_CONFIG['cborg']['parameters']['top_p'], 0.8)

if __name__ == '__main__':
    unittest.main()
