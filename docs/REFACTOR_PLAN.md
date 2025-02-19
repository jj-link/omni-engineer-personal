# Refactor Plan: Adding Multi-Model Support

> ⚠️ **IMPORTANT**: This plan must be updated to mark completed items BEFORE committing any code changes. This ensures we maintain an accurate record of progress.

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
- [x] Add provider config structure:
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
- [x] Add environment variable handling
- [x] Add config validation

## Phase 2: Error Handling (HIGH PRIORITY)
Goal: Ensure robust error handling before adding CBORG

### 2.1 Critical Error Handling 
- [x] Add connection error handling
- [x] Add API key validation
- [x] Add model availability checks
- [x] Add tests for error scenarios

### 2.2 Response Error Handling 
- [x] Add response validation
- [x] Add response format checking
- [x] Add automatic retries for transient errors
- [x] Add error logging

### 2.3 CLI Argument Handling
- [x] Add argparse configuration
- [x] Implement provider selection via CLI
- [x] Implement model selection via CLI
- [x] Add parameter configuration (temperature, top-p, etc.)
- [x] Add tests for CLI argument handling
- [ ] Update documentation with CLI usage

## Phase 3: CBORG Integration
Goal: Add CBORG support now that foundation is ready

### 3.1 Add CBORG Chat Function
- [x] Create chat_with_cborg parallel to chat_with_ollama
- [x] Ensure consistent response format with Ollama
- [x] Add streaming support
- [x] Add tests for CBORG chat

### 3.2 Provider-Specific Features
- [x] Add Ollama-specific options:
  - [x] Context window
  - [x] Model file path
- [ ] Add CBORG-specific options:
  - [ ] API version
  - [ ] Response format

## Success Criteria
- [x] Switch between providers with single argument
- [x] Clear error messages and recovery
- [x] Common parameters work across providers
- [x] Provider-specific features accessible
- [x] No loss of existing features
- [x] >90% test coverage

## Dependencies
- [x] aiohttp for CBORG API calls (Phase 3)
- [x] python-dotenv for API keys (Phase 1)
- [x] pytest for testing (All Phases)
- [x] rich for console output (existing)
- [x] ollama for Ollama support (existing)
