from flask import Flask, render_template, request, jsonify, url_for, session, json
from ce3 import Assistant
import os
import subprocess
from werkzeug.utils import secure_filename
import base64
from config import Config
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Print environment variable status
print("Environment variables:")
print(f"CBORG_API_KEY set: {bool(os.getenv('CBORG_API_KEY'))}")
print(f"Current provider: {Config.PROVIDER}")

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'dev'  # Fixed key for development

# Provider configuration
default_provider = Config.DEFAULT_PROVIDER  # Define default provider

PROVIDER_CONFIG = {
    'cborg': {
        'base_url': 'https://api.cborg.lbl.gov',
        'default_model': 'lbl/cborg-coder:latest',
        'available_models': [
            # LBL Models
            'lbl/cborg-coder:latest',
            'lbl/cborg-chat:latest',
            'lbl/cborg-vision:latest',
            'lbl/cborg-deepthought:latest',
            'lbl/cborg-pdfbot',
            'lbl/llama-3',
            'lbl/qwen-coder',
            'lbl/qwen-vision',
            
            # OpenAI Models
            'openai/gpt-4o',
            'openai/gpt-4o-mini',
            'openai/o1',
            'openai/o1-mini',
            'openai/o3-mini',
            
            # Anthropic Models
            'anthropic/claude-haiku',
            'anthropic/claude-sonnet',
            'anthropic/claude-opus',
        ],
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 2048,
            'stop': None
        },
        'requires_key': True,
        'api_key_env': 'CBORG_API_KEY'
    },
    'ollama': {
        'base_url': 'http://localhost:11434',
        'default_model': 'codellama',
        'available_models': [],  # Will be populated dynamically
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 2048,
            'stop': None
        },
        'requires_key': False
    },
    'anthropic': {
        'base_url': 'https://api.anthropic.com/v1',
        'default_model': 'anthropic/claude-sonnet',
        'available_models': [
            'anthropic/claude-haiku',
            'anthropic/claude-sonnet',
            'anthropic/claude-opus'
        ],
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.95,
            'max_tokens': 4000
        },
        'requires_key': True,
        'api_key_env': 'ANTHROPIC_API_KEY'
    },
    'openai': {
        'base_url': 'https://api.openai.com/v1',
        'default_model': 'openai/gpt-4',
        'available_models': [
            'openai/gpt-4',
            'openai/gpt-4-turbo',
            'openai/gpt-3.5-turbo'
        ],
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 4096,
            'stop': None
        },
        'requires_key': True,
        'api_key_env': 'OPENAI_API_KEY'
    },
    'google': {
        'base_url': 'https://generativelanguage.googleapis.com',
        'default_model': 'google/gemini-pro',
        'available_models': [
            'google/gemini-pro',
            'google/gemini-pro-vision',
            'google/gemini-ultra',
            'google/gemini-ultra-vision'
        ],
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 2048,
            'stop': None
        },
        'requires_key': True,
        'api_key_env': 'GOOGLE_API_KEY'
    }
}

# Initialize default provider
default_provider = Config.DEFAULT_PROVIDER  # or 'ollama' based on your preference

@app.before_request
def initialize_session():
    if 'current_provider' not in session:
        session['current_provider'] = default_provider
        print(f"[DEBUG] Initialized session with provider: {default_provider}")
    if 'current_model' not in session:
        session['current_model'] = PROVIDER_CONFIG[session['current_provider']]['default_model']
        print(f"[DEBUG] Initialized session with model: {session['current_model']}")

# Initialize assistant with default settings
assistant = Assistant(provider=default_provider)
assistant.model = PROVIDER_CONFIG[default_provider]['default_model']
current_provider = default_provider
current_parameters = PROVIDER_CONFIG[default_provider]['parameters'].copy()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/providers', methods=['GET'])
def get_providers():
    """Get available providers"""
    providers = list(PROVIDER_CONFIG.keys())
    current = session.get('current_provider', default_provider)
    print(f"[DEBUG] Available providers: {providers}")
    print(f"[DEBUG] Current provider: {current}")
    return jsonify({
        'providers': providers,
        'current_provider': current
    })

@app.route('/select_provider', methods=['POST'])
def select_provider():
    """Select a provider"""
    data = request.json
    provider = data.get('provider')
    print(f"[DEBUG] select_provider called with provider: {provider}")
    print(f"[DEBUG] Current session before update: {dict(session)}")
    print(f"[DEBUG] Current request: {request}")
    print(f"[DEBUG] Current request headers: {dict(request.headers)}")
    
    if provider not in PROVIDER_CONFIG:
        return jsonify({
            'success': False,
            'error': f'Invalid provider. Must be one of: {", ".join(PROVIDER_CONFIG.keys())}'
        }), 400
    
    # Check if provider requires API key
    if PROVIDER_CONFIG[provider].get('requires_key', False):
        api_key = os.getenv(PROVIDER_CONFIG[provider]['api_key_env'])
        if not api_key:
            return jsonify({
                'success': False,
                'error': f'Missing API key for {provider}. Please set {PROVIDER_CONFIG[provider]["api_key_env"]} environment variable.'
            }), 400
    
    # Store provider in session
    session['current_provider'] = provider
    print(f"[DEBUG] Session after update: {dict(session)}")
    
    # Reset parameters to provider defaults
    session['current_parameters'] = PROVIDER_CONFIG[provider]['parameters'].copy()
    
    return jsonify({
        'success': True,
        'provider': provider,
        'parameters': session['current_parameters']
    })

@app.route('/models', methods=['GET'])
def get_models():
    """Get available models from all providers."""
    try:
        # Initialize response data
        model_groups = {}
        capabilities = {}
        descriptions = {}
        
        # Get CBORG models
        cborg_models = PROVIDER_CONFIG['cborg']['available_models']
        for model in cborg_models:
            prefix = model.split('/')[0]
            if prefix not in model_groups:
                model_groups[prefix] = []
            model_groups[prefix].append(model)
            
            # Add metadata for CBORG models
            capabilities[model] = ['chat', 'code']  # Default capabilities for CBORG models
            descriptions[model] = {
                'lbl/cborg-coder:latest': 'Specialized coding model from CBORG',
                'lbl/cborg-chat:latest': 'General chat model from CBORG',
                'lbl/cborg-vision:latest': 'Vision-capable model from CBORG',
                'lbl/cborg-deepthought:latest': 'Advanced reasoning model from CBORG',
                'lbl/cborg-pdfbot': 'PDF analysis and interaction model',
                'lbl/llama-3': 'Open source large language model',
                'lbl/qwen-coder': 'Code-specialized Qwen model',
                'lbl/qwen-vision': 'Vision-capable Qwen model',
                'openai/gpt-4o': 'OpenAI GPT-4 compatible model',
                'openai/gpt-4o-mini': 'Lightweight GPT-4 compatible model',
                'openai/o1': 'OpenAI compatible model',
                'openai/o1-mini': 'Lightweight OpenAI compatible model',
                'openai/o3-mini': 'Lightweight OpenAI compatible model',
                'anthropic/claude-haiku': 'Fast and efficient Claude-compatible model',
                'anthropic/claude-sonnet': 'Balanced Claude-compatible model',
                'anthropic/claude-opus': 'Advanced Claude-compatible model'
            }.get(model, 'CBORG language model')
        
        # Get Anthropic models
        anthropic_models = PROVIDER_CONFIG.get('anthropic', {}).get('available_models', [
            'anthropic/claude-haiku',
            'anthropic/claude-sonnet',
            'anthropic/claude-opus'
        ])
        for model in anthropic_models:
            if 'anthropic' not in model_groups:
                model_groups['anthropic'] = []
            model_groups['anthropic'].append(model)
            
            # Add metadata
            capabilities[model] = ['chat', 'code']  # Default capabilities
            descriptions[model] = {
                'anthropic/claude-haiku': 'Fast and affordable model, including vision capabilities',
                'anthropic/claude-sonnet': 'Latest version of cost-optimized model with excellent reasoning and coding',
                'anthropic/claude-opus': 'Advanced model for nuanced reasoning, math, coding and more'
            }.get(model, 'Anthropic language model')
        
        # Get Ollama models
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                if 'ollama' not in model_groups:
                    model_groups['ollama'] = []
                
                for line in result.stdout.splitlines()[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            name = parts[0]
                            size = parts[2]
                            modified = ' '.join(parts[3:])
                            
                            # Add to model groups
                            model_groups['ollama'].append(name)
                            
                            # Add metadata
                            capabilities[name] = ['local', 'chat']  # Default capabilities
                            descriptions[name] = f"Local Ollama model ({size}, {modified})"
        except FileNotFoundError:
            print("[INFO] Ollama not installed")
        except Exception as e:
            print(f"[ERROR] Error listing Ollama models: {str(e)}")
        
        return jsonify({
            'format': 'grouped',
            'model_groups': model_groups,
            'capabilities': capabilities,
            'descriptions': descriptions,
            'current_model': session.get('current_model')
        })
            
    except Exception as e:
        print(f"[ERROR] Error in get_models: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/switch_model', methods=['POST'])
def switch_model():
    """Switch to a different model."""
    try:
        data = request.get_json()
        if not data or 'model' not in data:
            return jsonify({
                'error': 'No model specified'
            }), 400
        
        model = data['model']
        
        # Determine provider from model name
        if '/' in model:
            provider = model.split('/')[0]  # e.g. 'lbl/cborg-chat:latest' -> 'lbl'
            if provider == 'lbl':
                provider = 'cborg'  # Map LBL prefix to CBORG provider
        else:
            provider = 'ollama'  # Ollama models don't have a prefix
        
        # Validate provider
        valid_providers = {'cborg', 'ollama', 'anthropic', 'openai', 'google', 'wolfram'}
        if provider not in valid_providers:
            return jsonify({
                'error': f'Invalid provider: {provider}'
            }), 400
        
        # Validate model availability
        if provider == 'ollama':
            try:
                # Get list of Ollama models
                result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse model names from Ollama list output
                    models = []
                    for line in result.stdout.splitlines()[1:]:  # Skip header
                        if line.strip():
                            model_name = line.split()[0]  # First column is model name
                            models.append(model_name)
                else:
                    print(f"Ollama list error: {result.stderr}")
                    return jsonify({'error': 'Failed to list Ollama models'}), 500
            except FileNotFoundError:
                print("Ollama not installed")
                return jsonify({'error': 'Ollama not installed'}), 500
            except Exception as e:
                print(f"Error listing Ollama models: {str(e)}")
                return jsonify({'error': 'Failed to list Ollama models'}), 500
        else:
            # For other providers, check if model exists in their config
            provider_models = PROVIDER_CONFIG.get(provider, {}).get('available_models', [])
            if not provider_models:
                return jsonify({
                    'error': f'No models available for provider {provider}'
                }), 400
            models = provider_models
        
        if model not in models:
            return jsonify({
                'error': f'Model {model} is not available for provider {provider}'
            }), 400
        
        # Check if provider requires API key
        if PROVIDER_CONFIG.get(provider, {}).get('requires_key'):
            api_key_env = PROVIDER_CONFIG[provider]['api_key_env']
            if not os.getenv(api_key_env):
                return jsonify({
                    'error': f'API key required for {provider}. Please set {api_key_env} environment variable.'
                }), 400
        
        # Update session
        current_model = session.get('current_model')
        current_provider = session.get('current_provider')
        
        # If switching from an Ollama model, stop it first
        if current_provider == 'ollama' and current_model:
            try:
                # Stop the current model
                stop_result = subprocess.run(['ollama', 'stop', current_model], capture_output=True, text=True)
                if stop_result.returncode != 0:
                    print(f"Warning: Failed to stop previous Ollama model: {stop_result.stderr}")
            except Exception as e:
                print(f"Warning: Error stopping previous Ollama model: {str(e)}")
        
        session['current_model'] = model
        session['current_provider'] = provider
        
        # Update assistant's provider and model
        assistant.provider = provider
        assistant.model = model
        
        return jsonify({
            'success': True,
            'model': model,
            'provider': provider
        })
        
    except Exception as e:
        print(f"Error in switch_model: {str(e)}")
        return jsonify({
            'error': f'Failed to switch model: {str(e)}'
        }), 500

@app.route('/params', methods=['GET'])
def get_parameters():
    """Get current parameter configuration"""
    provider = session.get('current_provider', default_provider)
    params = session.get('current_parameters', PROVIDER_CONFIG[provider]['parameters'])
    return jsonify(params)

@app.route('/update_params', methods=['POST'])
def update_parameters():
    """Update parameter configuration"""
    data = request.json
    provider = session.get('current_provider', default_provider)
    
    try:
        # Validate parameters
        if 'temperature' in data:
            temp = float(data['temperature'])
            if temp < 0 or temp > 1:
                raise ValueError('Temperature must be between 0 and 1')
        
        if 'top_p' in data:
            top_p = float(data['top_p'])
            if top_p < 0 or top_p > 1:
                raise ValueError('Top-p must be between 0 and 1')
        
        if 'seed' in data and data['seed'] is not None:
            try:
                data['seed'] = int(data['seed'])
            except (ValueError, TypeError):
                raise ValueError('Seed must be an integer or None')
        
        # Update parameters in session
        current_params = session.get('current_parameters', 
                                 PROVIDER_CONFIG[provider]['parameters'])
        current_params.update(data)
        session['current_parameters'] = current_params
        
        return jsonify({
            'success': True,
            'parameters': current_params
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/debug/provider', methods=['GET'])
def debug_provider():
    """Debug endpoint to check provider status"""
    return jsonify({
        'current_provider': session.get('current_provider', 'not set'),
        'default_provider': default_provider,
        'available_providers': list(PROVIDER_CONFIG.keys())
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        message = data['message']
        settings = data.get('settings', {})
        
        try:
            current_model = session.get('current_model')
            if not current_model:
                current_model = PROVIDER_CONFIG['cborg']['default_model']
                session['current_model'] = current_model
            
            print(f"[DEBUG] Using model: {current_model}")
            
            # Determine provider from model name
            provider = 'cborg' if '/' in current_model else 'ollama'
            print(f"[DEBUG] Using provider: {provider}")
            
            try:
                # Update the assistant's provider and model
                if assistant.provider != provider:
                    assistant.provider = provider
                assistant.model = current_model

                # Update temperature if provided
                if settings.get('temperature'):
                    assistant.temperature = float(settings['temperature'])

                # Handle image data if present
                if 'image_data' in data and 'media_type' in data:
                    response = assistant.chat_with_image(message, data['image_data'], data['media_type'])
                else:
                    response = assistant.chat(message)

                print(f"[DEBUG] Response received from {provider}")
                return jsonify({'response': response})
                
            except Exception as e:
                print(f"[ERROR] {provider} error: {str(e)}")
                return jsonify({'error': f"{provider} error: {str(e)}"}), 500
                
        except Exception as e:
            print(f"[ERROR] Error in chat endpoint: {str(e)}")
            return jsonify({'error': f"Error in chat endpoint: {str(e)}"}), 500
            
    except Exception as e:
        print(f"[ERROR] Error parsing request: {str(e)}")
        return jsonify({'error': f"Error parsing request: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get the actual media type
        media_type = file.content_type or 'image/jpeg'  # Default to jpeg if not detected
        
        # Convert image to base64
        with open(filepath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Clean up the file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'image_data': encoded_string,
            'media_type': media_type
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/reset', methods=['POST'])
def reset():
    try:
        # Reset the assistant's conversation history
        assistant.reset()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in reset: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Enable debug mode and use port 5001