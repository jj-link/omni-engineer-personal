"""Tests for command line interface."""
import pytest
from argparse import ArgumentParser, Namespace
from omni_engineer.cli import create_parser, validate_args

def test_cli_basic_arguments():
    """Test basic CLI argument parsing."""
    parser = create_parser()
    args = parser.parse_args(['--api', 'cborg'])
    
    assert args.api == 'cborg'
    assert args.temperature == 0.7  # Default value
    assert args.top_p == 1.0  # Default value
    assert args.seed is None  # Default value
    assert args.model is None  # Default value

def test_cli_all_arguments():
    """Test CLI with all arguments specified."""
    parser = create_parser()
    args = parser.parse_args([
        '--api', 'ollama',
        '--temperature', '0.5',
        '--top-p', '0.9',
        '--seed', '42',
        '--model', 'codellama:latest',
        '--ollama-url', 'http://localhost:11434'
    ])
    
    assert args.api == 'ollama'
    assert args.temperature == 0.5
    assert args.top_p == 0.9
    assert args.seed == 42
    assert args.model == 'codellama:latest'
    assert args.ollama_url == 'http://localhost:11434'

def test_cli_invalid_api():
    """Test error handling for invalid API selection."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(['--api', 'invalid'])

def test_cli_temperature_validation():
    """Test temperature parameter validation."""
    parser = create_parser()
    
    # Test valid temperature
    args = parser.parse_args(['--api', 'cborg', '--temperature', '0.5'])
    assert args.temperature == 0.5
    
    # Test invalid temperature (too high)
    with pytest.raises(SystemExit):
        parser.parse_args(['--api', 'cborg', '--temperature', '2.0'])
    
    # Test invalid temperature (too low)
    with pytest.raises(SystemExit):
        parser.parse_args(['--api', 'cborg', '--temperature', '-0.1'])

def test_cli_top_p_validation():
    """Test top-p parameter validation."""
    parser = create_parser()
    
    # Test valid top-p
    args = parser.parse_args(['--api', 'cborg', '--top-p', '0.9'])
    assert args.top_p == 0.9
    
    # Test invalid top-p (too high)
    with pytest.raises(SystemExit):
        parser.parse_args(['--api', 'cborg', '--top-p', '1.1'])
    
    # Test invalid top-p (too low)
    with pytest.raises(SystemExit):
        parser.parse_args(['--api', 'cborg', '--top-p', '-0.1'])

def test_cli_seed_validation():
    """Test seed parameter validation."""
    parser = create_parser()
    
    # Test valid seed
    args = parser.parse_args(['--api', 'cborg', '--seed', '42'])
    assert args.seed == 42
    
    # Test invalid seed (negative)
    with pytest.raises(SystemExit):
        parser.parse_args(['--api', 'cborg', '--seed', '-1'])

def test_cli_ollama_url_validation():
    """Test Ollama URL validation."""
    parser = create_parser()
    args = Namespace(
        api='ollama',
        ollama_url='not-a-url',
        temperature=0.7,
        top_p=1.0,
        seed=None,
        model=None
    )
    
    with pytest.raises(ValueError, match='Invalid URL format'):
        validate_args(args)

def test_cli_help_text():
    """Test help text contains all necessary information."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(['--help'])
    # Note: We can't easily test the output text directly,
    # but we ensure it doesn't error
