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
  - [ ] Implement three-level model selection hierarchy:
    - [ ] Level 1: Provider type (CBORG/Ollama)
    - [ ] Level 2: Model provider (OpenAI, Anthropic, etc. for CBORG)
    - [ ] Level 3: Individual models
  - [ ] Add Ollama model detection:
    - [ ] Create endpoint to list local Ollama models using 'ollama list'
    - [ ] Parse and format Ollama model metadata
    - [ ] Show model file sizes where available
  - [ ] Update model metadata handling:
    - [ ] Create unified model metadata schema
    - [ ] Add provider-specific metadata parsers
    - [ ] Implement model capability detection
  - [ ] Enhance model organization:
    - [ ] Group CBORG models by provider
    - [ ] Group Ollama models by type/purpose
    - [ ] Add model tags and filtering
    - [ ] Implement model search across all levels
    - [ ] Implement model sorting by file size
  - [ ] Add model management features:
    - [ ] Show Ollama model status (pulled/not pulled)
    - [ ] Display model file sizes
    - [ ] Add model info tooltips
    - [ ] Implement model removal option (for Ollama)
    - [ ] Implement context window tracking:
      - [ ] Add model context limits to metadata
      - [ ] Track current context usage in session
      - [ ] Create visual context usage indicator:
        - [ ] Show total context window size
        - [ ] Display current usage / total available
        - [ ] Add warning when nearing limit (80%+)
        - [ ] Update in real-time as conversation grows
        - [ ] Show estimated tokens per message
      - [ ] Add context management options:
        - [ ] Trim older messages when nearing limit
        - [ ] When context reaches limit, create a condensed version of the conversation history, that can function well as the context for a new conversation

## Backend Changes Required
- [ ] Enhance Ollama integration:
  - [ ] Add endpoint to list all local Ollama models
  - [ ] Parse Ollama model metadata and status
  - [ ] Add model pull command support
  - [ ] Add model removal support
- [ ] Update provider configuration:
  - [ ] Refactor PROVIDER_CONFIG for nested structure
  - [ ] Add provider type categorization
  - [ ] Add context window limits per model
  - [ ] Implement token counting for messages
- [ ] Enhance model selection logic:
  - [ ] Update model switching endpoint
  - [ ] Add model availability checks
  - [ ] Reset context tracking on model switch
  - [ ] Handle context overflow scenarios

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
              'temperature': 0.0,
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

## Phase 4: Tools Implementation

### Context
The project currently has two key components that need to be integrated:
1. Original claude-engineer tools system:
   - Located in /tools directory
   - Each tool inherits from BaseTool class
   - Tools designed for Claude/Anthropic API originally
   - Tools use a function-calling schema similar to OpenAI
   
2. New CBORG integration:
   - Added PROVIDER_CONFIG in engine.py for provider management
   - Supports both Ollama and CBORG models
   - Each provider has different response formats and capabilities
   - Need to maintain all existing tool functionality while supporting both providers

### Implementation Tasks

#### 1. Provider-Agnostic BaseTool Class (/tools/base.py)
- [x] Create ProviderContext class to encapsulate provider-specific logic:
  ```python
  class ProviderContext:
      def __init__(self, provider_type, model, parameters):
          self.provider_type = provider_type  # 'ollama' or 'cborg'
          self.model = model
          self.parameters = parameters
  ```
- [x] Update BaseTool constructor to accept ProviderContext:
  ```python
  def __init__(self, provider_context: Optional[ProviderContext] = None):
      self.provider_context = provider_context
  ```
- [x] Add provider-specific response parsing methods:
  ```python
  def parse_response(self, response: dict) -> Any:
      if self.provider_context.provider_type == 'cborg':
          return self._parse_cborg_response(response)
      return self._parse_ollama_response(response)
  ```
- [x] Add tests in /tests/test_base_tool.py:
  - Test provider context initialization
  - Test response parsing for each provider
  - Test error handling scenarios

#### 2. Tool Execution System (engine.py)
- [ ] Update execute_tool function (line 687):
  ```python
  async def execute_tool(tool_call: Dict[str, Any], provider_context: ProviderContext):
      tool_name = tool_call["function"]["name"]
      tool_instance = tools_registry[tool_name](provider_context)
      return await tool_instance.execute(**tool_call["function"]["arguments"])
  ```
- [ ] Add provider-specific function call formatting:
  - CBORG format: {"name": "tool_name", "arguments": {...}}
  - Ollama format: {"function": {"name": "tool_name", "arguments": {...}}}
- [ ] Update tools registry to support provider capabilities:
  ```python
  tools_registry = {
      "file_editor": {
          "class": FileEditorTool,
          "supported_providers": ["ollama", "cborg"]
      }
  }
  ```

#### 3. Individual Tool Updates
Each tool in /tools needs the following updates:

##### 3.1 CreateFolderTool (/tools/create_folder_tool.py)
- [x] Create abstract base class with provider-agnostic interface
- [x] Implement concrete class in create_folder_tool_impl.py
- [x] Add comprehensive unit tests:
  - [x] Test folder creation
  - [x] Test error handling
  - [x] Test provider-specific responses
- [x] Fix response formatting issues:
  - [x] Ensure consistent response structure
  - [x] Handle provider-specific formatting in base class
  - [x] Add integration tests with both providers
- [x] Add manual testing script:
  - [x] Test with Ollama provider
  - [x] Test with CBORG provider
  - [x] Test error scenarios

##### 3.2 FileEditorTool (/tools/fileedittool.py)
- [ ] Update execute method for provider-specific handling
- [ ] Add provider-specific response formatting
- [ ] Update tests in /tests/test_file_editor_tool.py

##### 3.3 CodeSearchTool (/tools/codesearchtool.py)
- [ ] Update execute method for provider-specific handling
- [ ] Add provider-specific response formatting
- [ ] Update tests in /tests/test_code_search_tool.py

##### 3.4 CommandRunnerTool (/tools/commandrunnertool.py)
- [ ] Update execute method for provider-specific handling
- [ ] Add provider-specific response formatting
- [ ] Update tests in /tests/test_command_runner_tool.py

##### 3.5 WebSearchTool (/tools/websearchtool.py)
- [ ] Update execute method for provider-specific handling
- [ ] Add provider-specific response formatting
- [ ] Update tests in /tests/test_web_search_tool.py

#### 4. Testing Strategy
- [ ] Unit Tests:
  - [ ] Test each tool with both providers
  - [ ] Test error handling for each provider
  - [ ] Test response formatting
- [ ] Integration Tests:
  - [ ] Test tool chaining
  - [ ] Test provider switching mid-conversation
  - [ ] Test error recovery
- [ ] Manual Testing:
  - [ ] Create test scripts for each tool
  - [ ] Test real-world scenarios
  - [ ] Document edge cases and limitations

#### 5. Documentation
- [ ] Update tool documentation with provider-specific details
- [ ] Add examples for both providers
- [ ] Document response formats and error handling
- [ ] Add troubleshooting guide

## Phase 5: Error Handling
- [ ] Add CBORG-specific error handling:
  - [ ] Connection errors
  - [ ] API authentication
  - [ ] Model availability
  - [ ] Response validation
  - [ ] Automatic retries
- [ ] Ensure errors are properly displayed in web UI

## Phase 6: Testing
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

## Phase 7: UI/UX Implementation
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
