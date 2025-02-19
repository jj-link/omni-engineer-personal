# Product Requirements Document: Multi-Model Support for Omni Engineer

## Overview
Enhance `omni-engineer-personal` by adding support for both CBORG and local Ollama models while maintaining core functionality and adding flexible parameter controls.

## Current State vs Target State

### Current State
- Limited to Anthropic's API
- Single model configuration
- Fixed parameters
- Single API key configuration

### Target State
- Support for CBORG and Ollama models
- Flexible model selection
- Configurable parameters (temperature, top-p, seed)
- Support for both cloud (CBORG) and local (Ollama) models

## Technical Requirements

### 1. API and Model Support
```python
class APIConfig:
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

### 2. Command Line Interface
```python
parser.add_argument('--api', choices=['cborg', 'ollama'], default='cborg')
parser.add_argument('--model', help='Specify model name')
parser.add_argument('--temperature', type=float, default=0.7)
parser.add_argument('--top-p', type=float, default=1.0)
parser.add_argument('--seed', type=int)
parser.add_argument('--ollama-url', default='http://localhost:11434')
```

### 3. Core Features
- Model switching via command line arguments
- Parameter control (temperature, top-p, seed)
- Streaming output with `/stop` support
- Environment variable management
- Error handling for missing API keys
- Local model status checking (Ollama)

## Implementation Phases

### Phase 1: Core Architecture (Week 1)
1. Create API configuration system
2. Implement client factory
3. Add command line argument parsing
4. Set up environment variable handling

### Phase 2: Model Integration (Week 1-2)
1. Implement CBORG client integration
2. Add Ollama client integration
3. Create model switching logic
4. Test basic functionality

### Phase 3: Parameter Controls (Week 2)
1. Implement temperature control
2. Add top-p sampling
3. Include seed support
4. Test parameter effects

### Phase 4: Streaming and Controls (Week 2-3)
1. Implement streaming output
2. Add `/stop` functionality
3. Create error handling
4. Test interruption capabilities

### Phase 5: Testing and Documentation (Week 3)
1. Comprehensive testing
2. Update documentation
3. Create usage examples
4. Final bug fixes

## Success Criteria
1. Seamless switching between CBORG and Ollama models
2. Parameter controls working correctly
3. Streaming output with working interruption
4. Proper error handling for missing configurations
5. Clear documentation and examples

## Usage Examples

### Basic Usage
```bash
# Use CBORG (default)
python main.py

# Use local Ollama
python main.py --api ollama
```

### Advanced Usage
```bash
# CBORG with parameters
python main.py --model lbl/cborg-coder:latest --temperature 0.8 --top-p 0.9

# Ollama with custom setup
python main.py --api ollama --model codellama --temperature 0.8 --ollama-url http://192.168.1.100:11434
```

## Environment Setup
```bash
# .env file
CBORG_API_KEY=your_cborg_key
```

## Technical Dependencies
- Python 3.8+
- OpenAI API client (for CBORG)
- Requests library (for Ollama)
- Required packages in `requirements.txt`

## Migration Plan
1. Backup existing configuration
2. Update environment variables
3. Install new dependencies
4. Test both APIs
5. Update documentation

## Maintenance Considerations
1. Regular testing of both APIs
2. Monitoring for API changes
3. Version compatibility checks
4. Error logging and handling
