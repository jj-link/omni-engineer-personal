# Implementation Plan: Adding CBORG Support to engine.py

## Overview
Add CBORG support to the existing engine.py while maintaining all current functionality. We'll start with the web interface to make testing and debugging easier.

## Phase 1: Web Interface Enhancement
- [x] Add provider selection to web UI:
  - [x] Provider dropdown (Ollama/CBORG)
  - [x] Model selection per provider
  - [x] Parameter configuration UI
  - [x] Add /providers endpoint for listing providers
  - [x] Add /select_provider endpoint for switching
  - [x] Add /models endpoint for model selection
  - [x] Add /params endpoint for configuration
  - [x] Add comprehensive test coverage
  - [x] Implement session management for state
  - [x] Add parameter validation (temperature, top-p)
- [x] Update chat interface:
  - [x] Code highlighting improvements
  - [x] Chat history display
  - [x] Error message handling
- [x] Add file management:
  - [x] Upload/download support
  - [x] Project context management
- [x] Add in-chat model switching:
  - [x] Add model selector dropdown in chat UI
  - [x] Update model selection endpoint for active sessions
  - [x] Add model switch confirmation dialog
  - [x] Handle conversation context during model switch
  - [x] Add tests for model switching functionality
- [ ] Implement real-time updates:
  - [ ] Streaming responses
  - [ ] Progress indicators
  - [ ] Status messages

## Phase 2: CBORG Configuration
- [x] Add CBORG configuration to engine.py:
  - [x] PROVIDER_CONFIG dictionary
  - [x] 'cborg' key with base_url, default_model, requires_key, and parameters
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
      }
  }
  ```
- [x] Add environment variable support for CBORG API key
- [x] Add dynamic model list from CBORG API

## Phase 3: CBORG Integration
- [ ] Add provider selection via CLI arguments
- [ ] Ensure all existing features work with CBORG:
  - [ ] Rich console output
  - [ ] Code editing
  - [ ] Project context
  - [ ] File operations
  - [ ] Conversation history

## Phase 4: Error Handling
- [ ] Add CBORG-specific error handling:
  - [ ] Connection errors
  - [ ] API authentication
  - [ ] Model availability
  - [ ] Response validation
  - [ ] Automatic retries
- [ ] Ensure errors are properly displayed in web UI

## Phase 5: Testing
- [x] Test web interface components:
  - [x] Basic chat functionality
  - [x] Image upload and analysis
  - [x] Error handling
  - [x] Provider selection
  - [x] Model selection
  - [x] Parameter configuration
- [ ] Test CBORG integration
- [ ] Verify all existing features work with both providers
- [ ] Test error handling scenarios
- [ ] Document any CBORG-specific behavior

## Success Criteria
1. [ ] Can switch between Ollama and CBORG using web interface
2. [ ] Can switch between Ollama and CBORG using CLI arguments
3. [ ] All existing functionality works with both providers
4. [ ] Proper error handling for CBORG-specific issues
5. [ ] No regression in current features
6. [ ] Web interface provides full feature parity with CLI

## Secondary Goals
- [ ] Add CBORG chat completion function
- [ ] Major refactoring of existing code
- [ ] Adding new features beyond CBORG support
- [ ] Changing the current architecture
- [ ] Supporting additional providers beyond Ollama and CBORG
