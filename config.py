from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    CBORG_API_KEY = os.getenv('CBORG_API_KEY')

    # Provider Settings
    DEFAULT_PROVIDER = 'cborg'
    PROVIDER = os.getenv('PROVIDER', DEFAULT_PROVIDER)
    
    # Model Settings by Provider
    PROVIDER_MODELS = {
        'cborg': 'lbl/cborg-coder:latest',
        'anthropic': 'claude-3-sonnet-20240229',
        'ollama': 'codellama'
    }
    DEFAULT_MODEL = PROVIDER_MODELS.get(PROVIDER, PROVIDER_MODELS['cborg'])

    # Token Limits
    MAX_TOKENS = 8000
    MAX_CONVERSATION_TOKENS = 200000  # Maximum tokens per conversation

    # Paths
    BASE_DIR = Path(__file__).parent
    TOOLS_DIR = BASE_DIR / "tools"
    PROMPTS_DIR = BASE_DIR / "prompts"

    # Assistant Configuration
    ENABLE_THINKING = True
    SHOW_TOOL_USAGE = True
    DEFAULT_TEMPERATURE = 0.7

    # CBORG Configuration
    CBORG_CONFIG = {
        'enable_auto_tool_choice': True,
        'tool_call_parser': True
    }
