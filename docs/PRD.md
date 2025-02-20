# Product Requirements Document: Multi-Model Support for Omni Engineer

## Overview
Add CBORG support to the existing Ollama-based engineer while preserving all current functionality. This is a focused enhancement to enable the use of both local Ollama models and CBORG's cloud models.

## Current State vs Target State

### Current State (engine.py)
- Fully functional Ollama integration with features:
  - Rich console output with syntax highlighting
  - Code editing and diffing capabilities
  - Project context management
  - File system operations
  - Conversation history
  - Asynchronous operation

### Target State
Same as current state, plus:
- Support for CBORG models alongside Ollama
- Ability to switch between providers via CLI arguments
- Proper error handling for both providers
- Environment variable support for API keys

## Technical Requirements

### 1. Model Provider Support
```python
PROVIDER_CONFIG = {
    'cborg': {
        'base_url': 'https://api.cborg.lbl.gov',
        'default_model': 'lbl/cborg-coder:latest',
        'requires_key': True,
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'seed': None
        }
    },
    'ollama': {
        'base_url': 'http://localhost:11434',
        'default_model': 'codellama',
        'requires_key': False,
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'seed': None
        }
    }
}
```

### 2. CLI Arguments
- `--provider`: Choose between 'ollama' and 'cborg'
- `--model`: Specify model name
- `--temperature`: Set temperature (0-1)
- `--top-p`: Set top-p sampling (0-1)
- `--seed`: Set random seed for reproducibility

### 3. Error Handling
- Connection errors
- API authentication
- Model availability
- Response validation
- Automatic retries for transient errors

### 4. Testing Requirements
- Unit tests for provider selection
- Integration tests for both providers
- Error handling test cases

## Success Criteria
1. Can switch between Ollama and CBORG models using CLI arguments
2. All existing functionality works with both providers
3. Proper error handling and recovery
4. No regression in current features
