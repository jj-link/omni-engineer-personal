# Implementation Plan: Adding CBORG Support to engine.py

## Overview
Add CBORG support to the existing engine.py while maintaining all current functionality. This is NOT a refactor - we are simply adding CBORG as an additional model provider.

## Phase 1: Preparation
- [ ] Revert recent refactoring changes
- [ ] Commit reversion as clean starting point
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

## Phase 2: CBORG Integration
- [ ] Add CBORG chat completion function
- [ ] Add provider selection via CLI arguments
- [ ] Add environment variable support for CBORG API key
- [ ] Ensure all existing features work with CBORG:
  - [ ] Rich console output
  - [ ] Code editing
  - [ ] Project context
  - [ ] File operations
  - [ ] Conversation history

## Phase 3: Error Handling
- [ ] Add CBORG-specific error handling:
  - [ ] Connection errors
  - [ ] API authentication
  - [ ] Model availability
  - [ ] Response validation
  - [ ] Automatic retries

## Phase 4: Testing
- [ ] Test CBORG integration
- [ ] Verify all existing features work with both providers
- [ ] Test error handling scenarios
- [ ] Document any CBORG-specific behavior

## Success Criteria
1. Can switch between Ollama and CBORG using CLI arguments
2. All existing functionality works with both providers
3. Proper error handling for CBORG-specific issues
4. No regression in current features

## Non-Goals
- Major refactoring of existing code
- Adding new features beyond CBORG support
- Changing the current architecture
- Supporting additional providers beyond Ollama and CBORG
