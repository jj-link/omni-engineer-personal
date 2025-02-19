"""Tests for main entry point."""
from unittest.mock import patch
import pytest

from omni_engineer.__main__ import main

def test_main_basic_usage(capsys):
    """Test basic usage of main entry point."""
    with patch('omni_engineer.client.ClientFactory.create_client'):
        exit_code = main(['--api', 'cborg'])
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert "Using cborg API" in captured.out
        assert "Temperature: 0.7" in captured.out
        assert "Top-p: 1.0" in captured.out

def test_main_all_parameters(capsys):
    """Test main with all parameters specified."""
    with patch('omni_engineer.client.ClientFactory.create_client'):
        exit_code = main([
            '--api', 'ollama',
            '--temperature', '0.5',
            '--top-p', '0.9',
            '--seed', '42',
            '--model', 'codellama:latest',
            '--ollama-url', 'http://localhost:11434'
        ])
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert "Using ollama API" in captured.out
        assert "Temperature: 0.5" in captured.out
        assert "Top-p: 0.9" in captured.out
        assert "Seed: 42" in captured.out
        assert "Model: codellama:latest" in captured.out
        assert "Ollama URL: http://localhost:11434" in captured.out

def test_main_invalid_url(capsys):
    """Test main with invalid Ollama URL."""
    exit_code = main(['--api', 'ollama', '--ollama-url', 'not-a-url'])
    assert exit_code == 2
    
    captured = capsys.readouterr()
    assert "invalid validate_url value" in captured.err

def test_main_missing_api_key(capsys, monkeypatch):
    """Test main with missing CBORG API key."""
    monkeypatch.delenv('CBORG_API_KEY', raising=False)
    exit_code = main(['--api', 'cborg'])
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert "Missing CBORG_API_KEY" in captured.err

def test_main_unexpected_error(capsys):
    """Test main with unexpected error."""
    with patch('omni_engineer.client.ClientFactory.create_client', side_effect=Exception("Test error")):
        exit_code = main(['--api', 'cborg'])
        assert exit_code == 2
        
        captured = capsys.readouterr()
        assert "Unexpected error: Test error" in captured.err
