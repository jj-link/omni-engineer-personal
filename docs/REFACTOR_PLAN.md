# Refactor Plan: Adding Multi-Model Support

## Current Status
- [x] Basic test infrastructure is set up
- [x] Project structure renamed for multi-model support
- [x] Basic error handling tests implemented

## Phase 1: Provider Selection (HIGHEST PRIORITY)
Goal: Enable switching between Ollama and CBORG at runtime

### 1.1 Add Basic Provider Selection
- [ ] Add --api argument to CLI:
  ```python
  parser.add_argument('--api', choices=['cborg', 'ollama'], default='ollama')
  parser.add_argument('--model', help='Model name')
  ```
- [ ] Add model selection logic in main()
- [ ] Add tests for provider selection

### 1.2 Add Common Parameters
- [ ] Add temperature control
- [ ] Add top-p sampling
- [ ] Add seed setting
- [ ] Add tests for parameter handling

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
- [ ] Switch between providers with single argument
- [ ] Clear error messages and recovery
- [ ] Common parameters work across providers
- [ ] Provider-specific features accessible
- [ ] No loss of existing features
- [ ] >90% test coverage

## Dependencies
- [ ] aiohttp for CBORG API calls (Phase 3)
- [ ] python-dotenv for API keys (Phase 1)
- [ ] pytest for testing (All Phases)
- [ ] rich for console output (existing)
- [ ] ollama for Ollama support (existing)
