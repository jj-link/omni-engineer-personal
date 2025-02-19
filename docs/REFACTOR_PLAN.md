# Detailed Refactor Plan: Multi-Model Support Implementation

## General Guidelines
- Follow Test-Driven Development (TDD) approach
- Preserve existing functionality while refactoring
- Add tests before making changes
- Use meaningful commit messages
- Make incremental, reversible changes

## Phase 1: Test Infrastructure

### 1.1 Test Current Functionality
- [x] Set up pytest framework
- [x] Create test fixtures for:
  - Ollama API responses
  - File system operations
  - Console output
  - Code editing
```python
def test_ollama_generation():
    """Test existing Ollama generation"""

def test_code_editing():
    """Test code editing functionality"""

def test_console_output():
    """Test rich console output"""
```

### 1.2 Document Behavior
- [x] Map out existing functions
- [x] Document current workflows
- [x] Create behavior specifications
```python
# Example behavior specification
def test_edit_workflow():
    """
    Given: A file with content
    When: User requests an edit
    Then: System should:
    1. Generate edit instructions
    2. Apply changes
    3. Show diff
    4. Save changes
    """
```

## Phase 2: Module Extraction

### 2.1 Core Components
- [ ] Extract from engine.py:
  - Model client interface
  - Console manager
  - File operations
  - Project context
```python
# Example module structure
class ModelClient:
    """Base class for model interactions"""

class ConsoleManager:
    """Handle rich console output"""

class FileOps:
    """File system operations"""
```

### 2.2 Supporting Features
- [ ] Extract from engine.py:
  - Conversation management
  - Code editing
  - Diff generation
  - Command parsing
```python
class ConversationManager:
    """Manage chat history"""

class CodeEditor:
    """Handle code modifications"""
```

## Phase 3: CBORG Integration

### 3.1 Provider Interface
- [ ] Create common interface
- [ ] Implement CBORG client
- [ ] Add provider selection
```python
class ProviderInterface:
    """Common interface for all providers"""

class CBORGClient(ProviderInterface):
    """CBORG-specific implementation"""
```

### 3.2 Configuration
- [ ] Add provider settings
- [ ] Implement environment handling
- [ ] Create validation logic
```python
class ProviderConfig:
    """Handle provider configuration"""
```

## Phase 4: Enhancement

### 4.1 Error Handling
- [ ] Improve error messages
- [ ] Add recovery strategies
- [ ] Create logging system
```python
class ErrorHandler:
    """Centralized error handling"""
```

### 4.2 Parameter Management
- [ ] Add parameter validation
- [ ] Implement provider-specific formatting
- [ ] Create parameter presets
```python
class ParameterManager:
    """Handle model parameters"""
```

## Phase 5: Testing and Documentation

### 5.1 Test Coverage
- [ ] Integration tests
- [ ] Performance tests
- [ ] Edge cases
- [ ] Provider-specific tests

### 5.2 Documentation
- [ ] Update README
- [ ] Create API documentation
- [ ] Add usage examples
- [ ] Document architecture

## Module Structure
```
omni_core/
├── __init__.py
├── __main__.py
├── engine.py
├── client/
│   ├── __init__.py
│   ├── base.py
│   ├── ollama.py
│   └── cborg.py
├── console/
│   ├── __init__.py
│   └── manager.py
├── editor/
│   ├── __init__.py
│   └── code_editor.py
└── utils/
    ├── __init__.py
    ├── files.py
    └── config.py
```

## Success Metrics
- All tests passing
- No regression in functionality
- >90% test coverage
- Clear error messages
- Comprehensive documentation

## Migration Plan
1. Create tests for current functionality
2. Extract modules one at a time
3. Add CBORG support
4. Enhance and optimize
5. Document and test thoroughly

## Existing Files Assessment
- omni_core/config.py: Can be adapted for provider configuration
- omni_core/client.py: Can be basis for provider interface
- omni_core/cli.py: Need to merge with existing CLI
- Other files: Need to be evaluated against existing functionality
