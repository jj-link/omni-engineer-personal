# Omni Engineer 🤖

A flexible command-line interface for AI engineering with multi-provider support. Currently supports CBORG and Ollama providers, with a modular architecture for easy addition of new providers.

## Features

### Multi-Provider Support
- 🔄 Dynamic provider switching
- 🤖 CBORG API integration
- 🦙 Local Ollama support
- 🔌 Extensible provider architecture

### Advanced Configuration
- 🎛️ Fine-grained model parameters
- 🌡️ Temperature control
- 📊 Top-p sampling
- 🔢 Token limit settings
- 🎯 Reproducible results with seed setting

### Robust Error Handling
- 🔒 API key validation
- 🔍 Model availability checks
- 🔄 Automatic retries for transient errors
- 📝 Detailed error logging

## Installation

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) (for local models)
- CBORG API key (for CBORG models)

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/omni-engineer.git
cd omni-engineer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Basic Commands
```bash
# Use CBORG provider
python -m omni_core --provider cborg --model lbl/cborg-coder:latest

# Use local Ollama
python -m omni_core --provider ollama --model codellama

# Set model parameters
python -m omni_core --provider cborg --temperature 0.7 --top-p 0.9 --max-tokens 1000
```

### Environment Configuration
Create a `.env` file with your API keys:
```env
CBORG_API_KEY=your_cborg_key_here
# Ollama runs locally, no API key needed
```

### Provider-Specific Features

#### CBORG
- Latest CBORG models
- API version selection
- Custom response formats

#### Ollama
- Local model execution
- Custom model loading
- Adjustable context window

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Providers
1. Create a new provider class in `omni_core/providers/`
2. Implement the required interface methods:
   - `list_models()`
   - `chat_completion()`
3. Add provider configuration to `omni_core/config.py`
4. Create corresponding tests

## Contributing
Contributions are welcome! Please read our contributing guidelines for details on our code of conduct and development process.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
