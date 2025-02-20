# Implementation Plan: Adding CBORG Support to engine.py

## Overview
Add CBORG support to the existing engine.py while maintaining all current functionality. We'll start with the web interface to make testing and debugging easier.

## Phase 1: Web Interface Enhancement
- [ ] Add provider selection to web UI:
  - [ ] Provider dropdown (Ollama/CBORG)
  - [ ] Model selection per provider
  - [ ] Parameter configuration UI
- [ ] Update chat interface:
  - [ ] Code highlighting improvements
  - [ ] Chat history display
  - [ ] Error message handling
- [ ] Add file management:
  - [ ] Upload/download support
  - [ ] Project context management
- [ ] Implement real-time updates:
  - [ ] Streaming responses
  - [ ] Progress indicators
  - [ ] Status messages

## Phase 2: CBORG Configuration
- [ ] Add CBORG configuration to engine.py:
  ```python
  PROVIDER_CONFIG = {
      'cborg': {
          'base_url': 'https://api.cborg.lbl.gov',
          'default_model': 'lbl/cborg-coder:latest',
          'requires_key': True
      }
  }
  ```
- [ ] Add environment variable support for CBORG API key

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
- [ ] Test web interface components
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
