# Refactor Plan: Adding Multi-Model Support

## Current Status
- [x] Basic test infrastructure is set up
- [x] Project structure renamed for multi-model support
- [x] Basic error handling tests implemented
- [x] Provider selection implemented
- [x] Common parameters added

## Phase 1: Provider Selection (HIGHEST PRIORITY)
Goal: Enable switching between Ollama and CBORG at runtime

### 1.1 Add Basic Provider Selection 
- [x] Add --api argument to CLI:
  ```python
  parser.add_argument('--api', choices=['cborg', 'ollama'], default='ollama')
  parser.add_argument('--model', help='Model name')
  ```
- [x] Add model selection logic in main()
- [x] Add tests for provider selection

### 1.2 Add Common Parameters 
- [x] Add temperature control
- [x] Add top-p sampling
- [x] Add seed setting
- [x] Add tests for parameter handling

### 1.3 Add Provider Configuration
- [ ] Add provider config structure:
  ```python
  PROVIDER_CONFIG = {
      'cborg': {
          'base_url': 'https://api.cborg.lbl.gov',
          'default_model': 'lbl/cborg-coder:latest',
          'requires_key': True
      },
      'ollama': {
          'base_url': 'http://localhost:11434',
          'default_model': 'codellama',
          'requires_key': False
      }
  }
  ```
- [ ] Add environment variable handling
- [ ] Add config validation

## Phase 2: Error Handling (HIGH PRIORITY)
Goal: Ensure robust error handling before adding CBORG

### 2.1 Critical Error Handling
- [ ] Add connection error handling
- [ ] Add API key validation
- [ ] Add model availability checks
- [ ] Add tests for error scenarios

### 2.2 Response Error Handling
- [ ] Add response validation
- [ ] Add response format checking
- [ ] Add automatic retries for transient errors
- [ ] Add error logging

## Phase 3: CBORG Integration
Goal: Add CBORG support now that foundation is ready

### 3.1 Add CBORG Chat Function
- [ ] Create chat_with_cborg parallel to chat_with_ollama
- [ ] Ensure consistent response format with Ollama
- [ ] Add streaming support
- [ ] Add tests for CBORG chat

### 3.2 Provider-Specific Features
- [ ] Add Ollama-specific options:
  - [ ] Context window
  - [ ] Model file path
- [ ] Add CBORG-specific options:
  - [ ] API version
  - [ ] Response format

## Success Criteria
- [x] Switch between providers with single argument
- [ ] Clear error messages and recovery
- [x] Common parameters work across providers
- [ ] Provider-specific features accessible
- [ ] No loss of existing features
- [ ] >90% test coverage

## Dependencies
- [ ] aiohttp for CBORG API calls (Phase 3)
- [x] python-dotenv for API keys (Phase 1)
- [x] pytest for testing (All Phases)
- [x] rich for console output (existing)
- [x] ollama for Ollama support (existing)
