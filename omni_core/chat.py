"""Chat module for Omni Engineer."""

from typing import Dict, Any, List, Optional
import logging
from .config import Configuration
from .providers.ollama import OllamaProvider

# Configure logging
logger = logging.getLogger(__name__)

class ChatManager:
    """Manages chat interactions with different providers."""
    
    def __init__(self):
        """Initialize chat manager."""
        self.config = Configuration()
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Initialize provider
        if self.config.provider == "ollama":
            self.provider = OllamaProvider()
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    async def list_models(self) -> List[str]:
        """List available models for the current provider."""
        try:
            return await self.provider.list_models()
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send a chat request to the current provider."""
        try:
            # Use config values if not provided
            model = model or self.config.model
            temperature = temperature or self.config.temperature
            top_p = top_p or self.config.top_p
            max_tokens = max_tokens or self.config.max_tokens
            
            return await self.provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                top_p=top_p,
                seed=seed,
                max_tokens=max_tokens,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise
