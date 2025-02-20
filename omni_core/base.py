"""Base provider class for all AI providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models.
        
        Returns:
            List of model names
        """
        pass
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        top_p: float = 0.95,
        seed: Optional[int] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send chat completion request.
        
        Args:
            messages: List of message dictionaries
            model: Model name to use
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            seed: Random seed
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response
        """
        pass
