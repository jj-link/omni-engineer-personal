"""Main module for Omni Engineer CLI."""

import os
import sys
import asyncio
import logging
import msvcrt
from typing import Optional, Dict, Any
from .cli import get_cli_config
from .config import Configuration
from .chat import ChatManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_input() -> str:
    """Get input from user."""
    line = []
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwche()
            if char == '\r':  # Enter key
                sys.stdout.write('\n')
                return ''.join(line)
            elif char == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif char == '\b':  # Backspace
                if line:
                    line.pop()
                    sys.stdout.write(' \b')  # Clear the character
            else:
                line.append(char)

async def chat_loop(chat_manager: ChatManager, config: Configuration):
    """Run the chat loop."""
    while True:
        try:
            # Get user input
            sys.stdout.write("You: ")
            sys.stdout.flush()
            user_input = get_input()
            
            if not user_input:
                continue
            
            user_input = user_input.strip()
            if user_input.lower() in ['exit', 'quit']:
                sys.stdout.write("\nGoodbye!\n")
                sys.stdout.flush()
                break
                
            try:
                # Send chat request and display assistant response
                sys.stdout.write("\nAssistant: ")
                sys.stdout.flush()
                
                await chat_manager.chat_completion(
                    messages=[{"role": "user", "content": user_input}],
                    model=config.model,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    seed=config.seed,
                    max_tokens=config.max_tokens
                )
                
                # Add newline after response
                sys.stdout.write("\n")
                sys.stdout.flush()
                
            except Exception as e:
                logger.error(f"Error during chat completion: {str(e)}")
                continue
            
        except EOFError:
            sys.stdout.write("\nGoodbye!\n")
            sys.stdout.flush()
            break
        except KeyboardInterrupt:
            sys.stdout.write("\nGoodbye!\n")
            sys.stdout.flush()
            break
        except Exception as e:
            logger.error(f"Error during input: {str(e)}")
            continue

async def main():
    """Main entry point for the CLI."""
    try:
        config = get_cli_config()
        
        # Initialize configuration
        configuration = Configuration()
        configuration.update_provider(config.provider)
        configuration.update_model(config.model)
        configuration.update_parameters({
            "temperature": config.temperature,
            "top_p": config.top_p,
            "seed": config.seed,
            "max_tokens": config.max_tokens
        })
        
        # Create chat manager
        chat_manager = ChatManager()
        
        # Handle list-models command
        if config.list_models:
            try:
                models = await chat_manager.list_models()
                sys.stdout.write("\nAvailable models:\n")
                for model in models:
                    sys.stdout.write(f"- {model}\n")
                sys.stdout.flush()
                return 0
            except Exception as e:
                logger.error(f"Error listing models: {str(e)}")
                return 1
        
        # Start interactive chat session
        sys.stdout.write("\nWelcome to Omni Engineer! Type 'exit' or 'quit' to end the session.\n")
        sys.stdout.write(f"Using {config.provider} provider with {config.model} model\n\n")
        sys.stdout.flush()
        
        await chat_loop(chat_manager, configuration)
        
    except KeyboardInterrupt:
        sys.stdout.write("\nExiting...\n")
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        return 1
    
    return 0

def run():
    """Run the main function."""
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.stdout.write("\nExiting...\n")
        sys.stdout.flush()
        sys.exit(0)

if __name__ == "__main__":
    run()
