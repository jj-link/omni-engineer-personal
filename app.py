from flask import Flask, render_template, request, jsonify, url_for, session
from ce3 import Assistant
import os
from werkzeug.utils import secure_filename
import base64
from config import Config
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Debug: Print environment variables
print("Environment variables:")
print(f"CBORG_API_KEY set: {'CBORG_API_KEY' in os.environ}")
print(f"Current provider: {os.getenv('CBORG_API_KEY', 'not set')}")

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.urandom(24)  # For session management

# Provider configuration
PROVIDER_CONFIG = {
    'cborg': {
        'base_url': 'https://api.cborg.lbl.gov',
        'default_model': 'lbl/cborg-coder:latest',
        'available_models': [
            # OpenAI Models
            'openai/gpt-35-turbo',
            'openai/gpt-4o',
            'openai/gpt-4o-mini',
            'openai/o1',
            'openai/o1-mini',
            'openai/o3-mini',
            'openai/chatgpt:latest',
            
            # LBL Models
            'lbl/cborg-coder:latest',
            'lbl/cborg-coder:chat',
            'lbl/cborg-coder-base:latest',
            'lbl/cborg-chat:latest',
            'lbl/cborg-chat:chat',
            'lbl/cborg-vision:latest',
            'lbl/cborg-deepthought:latest',
            'lbl/cborg-pdfbot',
            'lbl/llama',
            'lbl/llama-3',
            'lbl/llama-vision',
            'lbl/qwen-coder',
            'lbl/qwen-vision',
            'lbl/labgpt',
            'lbl/failbot',
            'lbl/nomic-embed-text',
            'lbl/deepseek-r1:llama-70b',
            
            # Anthropic Models
            'anthropic/claude-haiku:latest',
            'anthropic/claude-haiku',
            'anthropic/claude:latest',
            'anthropic/claude-sonnet',
            'anthropic/claude-sonnet:v1',
            'anthropic/claude-opus',
            
            # Google Models
            'google/gemini-pro',
            'google/gemini-flash',
            'google/gemini:latest',
            
            # AWS Models
            'aws/mistral-large',
            'aws/llama-3.1-405b',
            'aws/llama-3.1-8b',
            'aws/llama-3.1-70b',
            'aws/command-r-v1',
            'aws/command-r-plus-v1',
            
            # Azure Models
            'azure/phi-3-medium-4k',
            'azure/phi-3.5-moe',
            'azure/deepseek-r1',
            
            # Other Models
            'wolfram/alpha'
        ],
        'requires_key': True,
        'api_key_env': 'CBORG_API_KEY',
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'seed': None
        }
    },
    'ollama': {
        'base_url': 'http://localhost:11434',
        'default_model': 'codellama',
        'available_models': ['codellama', 'llama2', 'mistral'],
        'requires_key': False,
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'seed': None
        }
    }
}

# Initialize with CBORG if API key exists, otherwise fallback to ollama
default_provider = 'cborg' if os.getenv('CBORG_API_KEY') else 'ollama'
assistant = Assistant(provider=default_provider)
current_provider = default_provider
current_parameters = PROVIDER_CONFIG[default_provider]['parameters'].copy()

@app.route('/')
def home():
    # Set initial provider in session
    if 'current_provider' not in session:
        session['current_provider'] = default_provider
    return render_template('index.html')

@app.route('/providers', methods=['GET'])
def get_providers():
    """Get available providers"""
    return jsonify({
        'providers': list(PROVIDER_CONFIG.keys()),
        'current_provider': session.get('current_provider', 'ollama')
    })

@app.route('/select_provider', methods=['POST'])
def select_provider():
    """Select a provider"""
    data = request.json
    provider = data.get('provider')
    
    if provider not in PROVIDER_CONFIG:
        return jsonify({
            'success': False,
            'error': f'Invalid provider. Must be one of: {", ".join(PROVIDER_CONFIG.keys())}'
        }), 400
    
    # Check if provider requires API key
    if PROVIDER_CONFIG[provider]['requires_key']:
        api_key = os.getenv(PROVIDER_CONFIG[provider]['api_key_env'])
        if not api_key:
            return jsonify({
                'success': False,
                'error': f'Missing API key for {provider}. Please set {PROVIDER_CONFIG[provider]["api_key_env"]} environment variable.'
            }), 400
    
    # Store provider in session
    session['current_provider'] = provider
    
    # Reset parameters to provider defaults
    session['current_parameters'] = PROVIDER_CONFIG[provider]['parameters'].copy()
    
    return jsonify({
        'success': True,
        'provider': provider,
        'parameters': session['current_parameters']
    })

@app.route('/models', methods=['GET'])
def get_models():
    """Get available models for the current provider"""
    provider = session.get('current_provider', default_provider)
    
    if provider == 'ollama':
        try:
            # Try to get list of installed models from Ollama
            import requests
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                installed_models = [model['name'] for model in response.json()['models']]
            else:
                installed_models = ['codellama']  # Fallback to default
                
            models = [f"OLLAMA: {model}" for model in installed_models]
            default_model = f"OLLAMA: {PROVIDER_CONFIG['ollama']['default_model']}"
            
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
            models = ["OLLAMA: codellama"]  # Fallback to default
            default_model = "OLLAMA: codellama"
            
    elif provider == 'cborg':
        # For CBORG, use the configured models
        models = [f"CBORG: {model}" for model in PROVIDER_CONFIG['cborg']['available_models']]
        default_model = f"CBORG: {PROVIDER_CONFIG['cborg']['default_model']}"
    else:
        return jsonify({
            'success': False,
            'error': f'Unknown provider: {provider}'
        }), 400
    
    # Get current model with proper prefix
    current_model = session.get('current_model')
    if not current_model:
        current_model = default_model
    elif not (current_model.startswith('OLLAMA: ') or current_model.startswith('CBORG: ')):
        current_model = f"{provider.upper()}: {current_model}"
    
    return jsonify({
        'models': models,
        'default_model': default_model,
        'current_model': current_model,
        'current_provider': provider
    })

@app.route('/switch_model', methods=['POST'])
def switch_model():
    """Switch to a different model"""
    try:
        data = request.get_json()
        if not data or 'model' not in data:
            return jsonify({
                'success': False,
                'error': 'No model specified'
            }), 400
        
        model = data['model']
        provider = session.get('current_provider', default_provider)
        
        # Remove provider prefix for validation
        if model.startswith('OLLAMA: '):
            if provider != 'ollama':
                return jsonify({
                    'success': False,
                    'error': 'Cannot use Ollama model with CBORG provider'
                }), 400
            actual_model = model.replace('OLLAMA: ', '')
            # Update the assistant's model
            assistant.model = actual_model
        elif model.startswith('CBORG: '):
            if provider != 'cborg':
                return jsonify({
                    'success': False,
                    'error': 'Cannot use CBORG model with Ollama provider'
                }), 400
            actual_model = model.replace('CBORG: ', '')
            # Don't add :chat here - it will be added in the chat endpoint
            assistant.model = actual_model
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid model format. Must start with OLLAMA: or CBORG:'
            }), 400
        
        # Store the selected model in the session
        session['current_model'] = model
        
        return jsonify({
            'success': True,
            'model': model,
            'provider': provider
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    message = data['message']
    image_data = data.get('image_data')
    media_type = data.get('media_type')

    try:
        # Get current model and remove provider prefix
        current_model = session.get('current_model')
        if current_model:
            if current_model.startswith('CBORG: '):
                model_name = current_model.replace('CBORG: ', '')
                # Model name already includes :chat suffix
            elif current_model.startswith('OLLAMA: '):
                model_name = current_model.replace('OLLAMA: ', '')
            else:
                model_name = current_model
        else:
            # Use default model based on provider
            provider = session.get('current_provider', default_provider)
            if provider == 'cborg':
                model_name = PROVIDER_CONFIG['cborg']['default_model']  # Already includes :chat
            else:
                model_name = PROVIDER_CONFIG['ollama']['default_model']

        # Update the model in the Assistant
        assistant.model = model_name

        if image_data and media_type:
            response = assistant.chat_with_image(message, image_data, media_type)
        else:
            response = assistant.chat(message)

        return jsonify({'response': response})

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    # Reset the assistant's conversation history
    assistant.reset()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=False)