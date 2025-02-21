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
- [ ] Enhance model selector UI:
  - [x] Implement hierarchical dropdown with provider groups
  - [x] Add model descriptions and capabilities as tooltips
  - [x] Implement search/filter functionality
  - [x] Add visual indicators for model status
  - [x] Improve mobile responsiveness
  - [x] Add keyboard navigation support
  - [ ] Add provider icons/logos for each group
  - [ ] Add "Recently Used" or "Favorites" section
  - [ ] Persist user preferences (last used model, favorites)

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

## Phase 6: UI/UX Implementation
- [ ] Implement new layout structure:
  - [ ] Create left sidebar component (250px width)
  - [ ] Add collapsible toggle button for sidebar
  - [ ] Create main chat area with max-width 1200px
  - [ ] Add proper padding (24px) and margins
  - [ ] Implement CSS Grid for responsive layout

- [ ] Update typography and colors:
  - [ ] Set system font stack (system-ui, -apple-system, etc.)
  - [ ] Define font sizes (14px body, 16px headers)
  - [ ] Implement CBORG color palette:
    - Primary: #2563eb (blue)
    - Background: #ffffff
    - Text: #1e293b
    - Border: #e2e8f0
    - Hover: #f1f5f9

- [ ] Revamp message display:
  - [ ] Create distinct message bubbles:
    - User: Right-aligned, blue background
    - Assistant: Left-aligned, white with border
  - [ ] Add 16px gap between messages
  - [ ] Style code blocks:
    - Padding: 12px
    - Border radius: 6px
    - Background: #f8fafc
    - Font: Menlo, Monaco, monospace
    - Add copy button in top-right
  - [ ] Configure highlight.js with:
    - Theme: github-light
    - Languages: python, javascript, html, css, bash
  - [ ] Add markdown parsing with marked.js options:
    - gfm: true
    - breaks: true
    - highlight: use highlight.js

- [ ] Create new model selector:
  - [ ] Build dropdown component:
    - Width: 300px
    - Max height: 400px
    - Shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1)
  - [ ] Add provider sections:
    - Header with 20x20px icon
    - Group models by provider
    - Sticky headers on scroll
  - [ ] Design model list items:
    - Model name in larger font (16px)
    - Description text below in gray (14px)
    - Two-line description with ellipsis
    - Proper padding (16px)
    - Hover state background
  - [ ] Implement search:
    - Sticky search bar at top
    - Filter by model name and description
    - Highlight matching text
  - [ ] Add capability badges:
    - Code: Blue pill
    - Vision: Teal pill
    - Chat: Indigo pill
    - Fast: Amber pill
  - [ ] Add keyboard navigation:
    - Arrow keys to move
    - Enter to select
    - Escape to close
  - [ ] Store in localStorage:
    - Last 3 used models
    - Favorite models

- [ ] Enhance input area:
  - [ ] Create auto-expanding textarea:
    - Min height: 56px
    - Max height: 200px
    - Padding: 16px
  - [ ] Add file upload:
    - Drag and drop zone
    - Preview thumbnails
    - Progress indicator
    - Size limit warning
  - [ ] Implement command palette:
    - Trigger with "/"
    - Commands list popup
    - Keyboard navigation
  - [ ] Add shortcuts:
    - Ctrl+Enter: Send
    - Ctrl+B: Bold
    - Ctrl+I: Italic
    - Ctrl+K: Code
  - [ ] Show character count:
    - Update in real-time
    - Warning at 90% limit
    - Error at limit
  - [ ] Add speech-to-text input:
    - Microphone button in input area
    - Use Web Speech API
    - Show audio input level indicator
    - Add visual feedback during recording
    - Support common voice commands:
      - "new line"
      - "period"
      - "question mark"
      - "exclamation mark"
    - Handle browser permission requests
    - Fallback for unsupported browsers

- [ ] Implement responsive design:
  - [ ] Define breakpoints in Tailwind:
    - sm: 640px
    - md: 768px
    - lg: 1024px
    - xl: 1280px
  - [ ] Create mobile navigation:
    - Hamburger menu
    - Slide-in sidebar
    - Bottom navigation bar
  - [ ] Adjust message layout:
    - Full width on mobile
    - Readable line length on desktop
    - Proper image scaling
  - [ ] Optimize for touch:
    - Min tap target: 44px
    - Touch-friendly dropdowns
    - Swipe gestures for sidebar

- [ ] Add loading states:
  - [ ] Create typing indicator:
    - Three dots animation
    - 600ms duration
    - Subtle fade in/out
  - [ ] Implement loading skeletons:
    - Message bubble shape
    - Code block shape
    - Image placeholder
  - [ ] Add transitions:
    - Menu slides: 200ms
    - Fade in/out: 150ms
    - Height animations: 250ms
  - [ ] Show upload progress:
    - Linear progress bar
    - Percentage indicator
    - Cancel button

## Extra Features (Low Priority)
- [ ] Add model parameter controls to web UI:
  - [ ] Add temperature slider (0.0 - 1.0)
  - [ ] Add top_p slider (0.0 - 1.0)
  - [ ] Add parameter presets (Code, Creative, Balanced)
  - [ ] Save parameter preferences per model
  - [ ] Add parameter info tooltips
  - [ ] Update /params endpoint to handle parameter changes
  - [ ] Add visual feedback for parameter changes

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
