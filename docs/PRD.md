# Product Requirements Document: Multi-Model Support for Omni Engineer

## Overview
Enhance the existing Ollama-based engineer by adding CBORG support while preserving and improving current functionality through incremental refactoring.

## Current State vs Target State

### Current State (engine.py)
- Fully functional Ollama integration
- Rich console output with syntax highlighting
- Code editing and diffing capabilities
- Project context management
- File system operations
- Conversation history
- Asynchronous operation

### Target State
- Support for both CBORG and Ollama models
- Modular, well-tested codebase
- Preserved existing functionality:
  - Rich console interface
  - Code editing capabilities
  - Project management
  - File operations
- Enhanced features:
  - Flexible model selection
  - Configurable parameters
  - Comprehensive test coverage
  - Improved error handling

## Technical Requirements

### 1. Model Provider Support
```python
PROVIDERS = {
    'cborg': {
        'env_key': 'CBORG_API_KEY',
        'base_url': 'https://api.cborg.lbl.gov',
        'default_model': 'lbl/cborg-coder:latest',
        'requires_key': True
    },
    'ollama': {
        'env_key': None,
        'base_url': 'http://localhost:11434',
        'default_model': 'codellama',
        'requires_key': False
    }
}
```

### 2. Preserved Core Features
- Asynchronous operation
- Rich console output
- Code editing and diffing
- Project context management
- File system operations
- Conversation history
- Progress tracking

### 3. Enhanced Features
- Model provider selection
- Parameter configuration:
  - Temperature
  - Top-p sampling
  - Random seed
- Improved error handling
- Comprehensive testing
- Provider-specific optimizations

### 4. Command Line Interface
```python
parser.add_argument('--api', choices=['cborg', 'ollama'], default='ollama')
parser.add_argument('--model', help='Model name')
parser.add_argument('--temperature', type=float, default=0.7)
parser.add_argument('--top-p', type=float, default=1.0)
parser.add_argument('--seed', type=int)
parser.add_argument('--ollama-url', default='http://localhost:11434')
```

## Implementation Strategy

### Phase 1: Test Coverage (Week 1)
1. Create comprehensive tests for existing functionality
2. Document current behavior
3. Establish baseline performance metrics

### Phase 2: Modular Refactoring (Week 1-2)
1. Extract core components into modules
2. Maintain existing functionality
3. Add unit tests for each module

### Phase 3: CBORG Integration (Week 2)
1. Add CBORG client implementation
2. Create provider selection logic
3. Test multi-provider support

### Phase 4: Enhancement (Week 2-3)
1. Improve error handling
2. Add parameter controls
3. Optimize performance

### Phase 5: Testing and Documentation (Week 3)
1. Complete test coverage
2. Update documentation
3. Create usage examples

## Success Criteria
1. All existing functionality preserved
2. Seamless provider switching
3. Comprehensive test coverage (>90%)
4. No regression in performance
5. Clear error messages
6. Updated documentation

## Usage Examples

### Basic Usage
```bash
# Use existing Ollama functionality (default)
python -m omni_core

# Use CBORG
python -m omni_core --api cborg

# Custom model and parameters
python -m omni_core --api cborg --model lbl/cborg-coder:latest --temperature 0.8
```

### Advanced Usage
```bash
# Code editing with specific provider
python -m omni_core --api cborg edit "Add error handling to main()"

# Project-wide changes
python -m omni_core refactor "Update docstrings"
