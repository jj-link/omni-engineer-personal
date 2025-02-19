"""Tests for command line interface."""

import pytest
from argparse import ArgumentParser, Namespace, ArgumentTypeError
from omni_core.cli import (
    parse_args,
    validate_temperature,
    validate_top_p,
    validate_provider,
    get_cli_config,
    CliConfig
)

def test_validate_temperature():
    """Test temperature validation."""
    # Valid temperatures
    assert validate_temperature("0.0") == 0.0
    assert validate_temperature("0.5") == 0.5
    assert validate_temperature("1.0") == 1.0
    
    # Invalid temperatures
    with pytest.raises(ArgumentTypeError):
        validate_temperature("-0.1")
    with pytest.raises(ArgumentTypeError):
        validate_temperature("1.1")
    with pytest.raises(ArgumentTypeError):
        validate_temperature("invalid")

def test_validate_top_p():
    """Test top-p validation."""
    # Valid top-p values
    assert validate_top_p("0.0") == 0.0
    assert validate_top_p("0.5") == 0.5
    assert validate_top_p("1.0") == 1.0
    
    # Invalid top-p values
    with pytest.raises(ArgumentTypeError):
        validate_top_p("-0.1")
    with pytest.raises(ArgumentTypeError):
        validate_top_p("1.1")
    with pytest.raises(ArgumentTypeError):
        validate_top_p("invalid")

def test_validate_provider():
    """Test provider validation."""
    # Valid provider
    assert validate_provider("ollama") == "ollama"
    assert validate_provider("cborg") == "cborg"
    
    # Invalid provider
    with pytest.raises(ArgumentTypeError):
        validate_provider("invalid")

def test_cli_config_defaults(monkeypatch):
    """Test CLI configuration with default values."""
    test_args = ["--provider", "ollama", "--model", "codellama"]
    monkeypatch.setattr("sys.argv", ["omni-engineer"] + test_args)
    
    config = parse_args()
    assert isinstance(config, CliConfig)
    assert config.provider == "ollama"
    assert config.model == "codellama"
    assert config.temperature == 0.7  # Default
    assert config.top_p == 0.9  # Default
    assert config.seed is None  # Default
    assert config.max_tokens is None  # Default
    assert config.system_prompt is None  # Default
    assert config.auto_mode is None  # Default

def test_cli_config_all_args(monkeypatch):
    """Test CLI configuration with all arguments specified."""
    test_args = [
        "--provider", "cborg",
        "--model", "lbl/cborg-coder:latest",
        "--temperature", "0.8",
        "--top-p", "0.95",
        "--seed", "42",
        "--max-tokens", "1000",
        "--system-prompt", "Custom prompt",
        "--auto-mode", "5"
    ]
    monkeypatch.setattr("sys.argv", ["omni-engineer"] + test_args)
    
    config = parse_args()
    assert isinstance(config, CliConfig)
    assert config.provider == "cborg"
    assert config.model == "lbl/cborg-coder:latest"
    assert config.temperature == 0.8
    assert config.top_p == 0.95
    assert config.seed == 42
    assert config.max_tokens == 1000
    assert config.system_prompt == "Custom prompt"
    assert config.auto_mode == 5

def test_get_cli_config(monkeypatch):
    """Test get_cli_config returns correct dictionary format."""
    test_args = [
        "--provider", "ollama",
        "--model", "codellama",
        "--temperature", "0.8",
        "--seed", "42"
    ]
    monkeypatch.setattr("sys.argv", ["omni-engineer"] + test_args)
    
    config = get_cli_config()
    assert isinstance(config, dict)
    assert config["provider"] == "ollama"
    assert config["model"] == "codellama"
    assert config["parameters"]["temperature"] == 0.8
    assert config["parameters"]["seed"] == 42
    assert config["system_prompt"] is None
    assert config["auto_mode"] is None

def test_missing_required_args(monkeypatch):
    """Test error handling for missing required arguments."""
    # Missing model
    test_args = ["--provider", "ollama"]
    monkeypatch.setattr("sys.argv", ["omni-engineer"] + test_args)
    with pytest.raises(SystemExit):
        parse_args()
    
    # Missing provider
    test_args = ["--model", "codellama"]
    monkeypatch.setattr("sys.argv", ["omni-engineer"] + test_args)
    with pytest.raises(SystemExit):
        parse_args()

def test_invalid_args(monkeypatch):
    """Test error handling for invalid argument values."""
    base_args = ["--model", "codellama"]
    
    # Invalid provider
    test_args = ["--provider", "invalid"] + base_args
    monkeypatch.setattr("sys.argv", ["omni-engineer"] + test_args)
    with pytest.raises(SystemExit):
        parse_args()
    
    # Invalid temperature
    test_args = ["--provider", "ollama", "--temperature", "2.0"] + base_args
    monkeypatch.setattr("sys.argv", ["omni-engineer"] + test_args)
    with pytest.raises(SystemExit):
        parse_args()
    
    # Invalid top-p
    test_args = ["--provider", "ollama", "--top-p", "-1.0"] + base_args
    monkeypatch.setattr("sys.argv", ["omni-engineer"] + test_args)
    with pytest.raises(SystemExit):
        parse_args()
