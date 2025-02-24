from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ProviderContext:
    """Context for provider-specific settings"""
    provider_type: str
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate provider context after initialization"""
        if self.provider_type not in ["ollama", "cborg", "anthropic"]:
            raise ValueError(f"Invalid provider type: {self.provider_type}")
        
        # Initialize parameters if None
        if self.parameters is None:
            self.parameters = {}

        # Validate temperature if present
        if "temperature" in self.parameters:
            temp = self.parameters["temperature"]
            if not 0 <= temp <= 1:
                raise ValueError("Temperature must be between 0 and 1")

class BaseTool(ABC):
    """Base class for all tools"""
    name: str = None
    description: str = None
    input_schema: Dict[str, Any] = None
    provider_context: Optional[ProviderContext] = None

    def __init__(self, provider_context: ProviderContext = None):
        """Initialize the tool with optional provider context"""
        self.provider_context = provider_context

    def validate_input(self, **kwargs) -> bool:
        """Validate input against schema"""
        if not self.input_schema:
            return True
        
        required = self.input_schema.get("required", [])
        properties = self.input_schema.get("properties", {})
        
        # Check required fields
        for field in required:
            if field not in kwargs:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate types
        for field, value in kwargs.items():
            if field in properties:
                field_type = properties[field].get("type")
                if field_type == "string" and not isinstance(value, str):
                    raise ValueError(f"Field {field} must be a string")
                elif field_type == "integer" and not isinstance(value, int):
                    raise ValueError(f"Field {field} must be an integer")
                elif field_type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Field {field} must be a boolean")
                
        return True

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with the given arguments"""
        import logging
        logging.debug(f"[{self.name}] Executing with parameters: {kwargs}")
        try:
            self.validate_input(**kwargs)
            logging.debug(f"[{self.name}] Input validation passed")
            result = self._execute(**kwargs)
            logging.debug(f"[{self.name}] Execution result: {result}")
            
            # Handle string responses
            if isinstance(result, str):
                result = {"response": result}
            
            # Ensure result has a response key
            if "response" not in result:
                raise ValueError("Tool response must contain a 'response' key")
            
            # Format response based on provider
            if self.provider_context and self.provider_context.provider_type == "cborg":
                formatted_result = {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": result["response"],
                            "tool_call_result": True
                        }
                    }]
                }
            else:  # Ollama format
                formatted_result = {
                    "response": result["response"],
                    "tool_call_id": kwargs.get("tool_call_id", ""),
                    "name": self.name
                }
            logging.debug(f"[{self.name}] Formatted result: {formatted_result}")
            return formatted_result
                
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logging.error(f"[{self.name}] {error_msg}")
            if self.provider_context and self.provider_context.provider_type == "cborg":
                error_result = {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": error_msg,
                            "tool_call_result": True,
                            "error": True
                        }
                    }]
                }
            else:  # Ollama format
                error_result = {
                    "response": error_msg,
                    "tool_call_id": kwargs.get("tool_call_id", ""),
                    "name": self.name,
                    "error": True
                }
            logging.debug(f"[{self.name}] Error result: {error_result}")
            return error_result

    @abstractmethod
    def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool-specific logic"""
        pass
