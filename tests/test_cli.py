"""Tests for command line interface."""

import unittest
from unittest.mock import patch
from argparse import ArgumentParser, Namespace, ArgumentTypeError
from omni_core.cli import (
    parse_args,
    validate_temperature,
    validate_top_p,
    validate_provider,
    get_cli_config,
    CliConfig
)

class TestCLI(unittest.TestCase):
    def test_validate_temperature(self):
        """Test temperature validation."""
        # Valid temperatures
        self.assertEqual(validate_temperature("0.0"), 0.0)
        self.assertEqual(validate_temperature("0.5"), 0.5)
        self.assertEqual(validate_temperature("1.0"), 1.0)
        
        # Invalid temperatures
        with self.assertRaises(ArgumentTypeError):
            validate_temperature("-0.1")
        with self.assertRaises(ArgumentTypeError):
            validate_temperature("1.1")
        with self.assertRaises(ArgumentTypeError):
            validate_temperature("invalid")

    def test_validate_top_p(self):
        """Test top-p validation."""
        # Valid top-p values
        self.assertEqual(validate_top_p("0.0"), 0.0)
        self.assertEqual(validate_top_p("0.5"), 0.5)
        self.assertEqual(validate_top_p("1.0"), 1.0)
        
        # Invalid top-p values
        with self.assertRaises(ArgumentTypeError):
            validate_top_p("-0.1")
        with self.assertRaises(ArgumentTypeError):
            validate_top_p("1.1")
        with self.assertRaises(ArgumentTypeError):
            validate_top_p("invalid")

    def test_validate_provider(self):
        """Test provider validation."""
        # Valid providers
        self.assertEqual(validate_provider("cborg"), "cborg")
        self.assertEqual(validate_provider("ollama"), "ollama")
        
        # Invalid provider
        with self.assertRaises(ArgumentTypeError):
            validate_provider("invalid")

    def test_cli_config_defaults(self):
        """Test CLI configuration with default values."""
        with patch('sys.argv', ['script.py', 'prompt']):
            args = parse_args()
            config = CliConfig.from_args(args)
            
            # Check default values
            self.assertEqual(config.prompt, "prompt")
            self.assertEqual(config.provider, "ollama")
            self.assertEqual(config.model, "codellama:latest")
            self.assertEqual(config.temperature, 0.7)
            self.assertEqual(config.top_p, 1.0)
            self.assertFalse(config.stream)

    def test_cli_config_all_args(self):
        """Test CLI configuration with all arguments specified."""
        test_args = [
            'script.py',
            'test prompt',
            '--provider', 'cborg',
            '--model', 'lbl/cborg-coder:custom',
            '--temperature', '0.5',
            '--top-p', '0.9',
            '--stream'
        ]
        
        with patch('sys.argv', test_args):
            args = parse_args()
            config = CliConfig.from_args(args)
            
            # Check all values
            self.assertEqual(config.prompt, "test prompt")
            self.assertEqual(config.provider, "cborg")
            self.assertEqual(config.model, "lbl/cborg-coder:custom")
            self.assertEqual(config.temperature, 0.5)
            self.assertEqual(config.top_p, 0.9)
            self.assertTrue(config.stream)

    def test_get_cli_config(self):
        """Test get_cli_config returns correct dictionary format."""
        test_args = [
            'script.py',
            'test prompt',
            '--provider', 'cborg',
            '--model', 'lbl/cborg-coder:custom',
            '--temperature', '0.5',
            '--top-p', '0.9',
            '--stream'
        ]
        
        with patch('sys.argv', test_args):
            config_dict = get_cli_config()
            
            # Check dictionary structure
            self.assertIn('prompt', config_dict)
            self.assertIn('provider', config_dict)
            self.assertIn('model', config_dict)
            self.assertIn('parameters', config_dict)
            
            # Check values
            self.assertEqual(config_dict['prompt'], "test prompt")
            self.assertEqual(config_dict['provider'], "cborg")
            self.assertEqual(config_dict['model'], "lbl/cborg-coder:custom")
            self.assertEqual(config_dict['parameters']['temperature'], 0.5)
            self.assertEqual(config_dict['parameters']['top_p'], 0.9)
            self.assertTrue(config_dict['parameters']['stream'])

    def test_missing_required_args(self):
        """Test error handling for missing required arguments."""
        test_cases = [
            ['script.py'],  # Missing prompt
            ['script.py', '--provider', 'cborg'],  # Missing prompt with provider
            ['script.py', '--model', 'test-model']  # Missing prompt with model
        ]
        
        for args in test_cases:
            with patch('sys.argv', args), self.assertRaises(SystemExit):
                parse_args()

    def test_invalid_args(self):
        """Test error handling for invalid argument values."""
        test_cases = [
            # Invalid temperature
            ['script.py', 'prompt', '--temperature', '2.0'],
            
            # Invalid top-p
            ['script.py', 'prompt', '--top-p', '-0.1'],
            
            # Invalid provider
            ['script.py', 'prompt', '--provider', 'invalid'],
            
            # Invalid combinations
            ['script.py', 'prompt', '--provider', 'cborg', '--temperature', 'invalid'],
            ['script.py', 'prompt', '--top-p', 'not-a-number']
        ]
        
        for args in test_cases:
            with patch('sys.argv', args), self.assertRaises((SystemExit, ArgumentTypeError)):
                parse_args()

if __name__ == '__main__':
    unittest.main()
