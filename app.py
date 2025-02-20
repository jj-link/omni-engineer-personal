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
            
            # Google Models
            'google/gemini-pro',
            'google/gemini-flash',
            
            # Other Models
            'wolfram/alpha'
        ],
        'requires_key': True,
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

# Initialize default provider
default_provider = 'cborg'  # or 'ollama' based on your preference

@app.before_request
def initialize_session():
    if 'current_provider' not in session:
        session['current_provider'] = default_provider
    if 'current_model' not in session:
        session['current_model'] = PROVIDER_CONFIG[session['current_provider']]['default_model']

assistant = Assistant(provider=default_provider)
current_provider = default_provider
current_parameters = PROVIDER_CONFIG[default_provider]['parameters'].copy()

@app.route('/')
def home():
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
    """Get available models for the current provider."""
    try:
        provider = session.get('current_provider', default_provider)
        print(f"Current provider: {provider}")  # Debug log
        
        if provider not in PROVIDER_CONFIG:
            raise ValueError(f"Invalid provider: {provider}")
        
        models = PROVIDER_CONFIG[provider]['available_models']
        print(f"Available models: {len(models)}")  # Debug log
        
        current_model = session.get('current_model', PROVIDER_CONFIG[provider]['default_model'])
        print(f"Current model: {current_model}")  # Debug log
        
        # Model metadata mapping
        model_metadata = {
            'lbl/cborg-chat:latest': {
                'description': 'Berkeley Lab-hosted chat model based on Llama 3.3 70B + Vision',
                'capabilities': ['chat', 'vision']
            },
            'lbl/cborg-coder:latest': {
                'description': 'Berkeley Lab-hosted chat model for code assistance based on Qwen Coder 2.5',
                'capabilities': ['code', 'chat']
            },
            'lbl/cborg-vision:latest': {
                'description': 'Lab-hosted multi-modal model for image analysis Qwen 72B Vision',
                'capabilities': ['vision', 'chat']
            },
            'lbl/cborg-deepthought:latest': {
                'description': 'Lab-hosted deep reasoning model based on DeepSeekR1-Distill Llama 70B (experimental)',
                'capabilities': ['chat']
            },
            'lbl/cborg-pdfbot': {
                'description': 'Specialized model for PDF document analysis and Q&A',
                'capabilities': ['chat', 'document']
            },
            'lbl/llama-3': {
                'description': 'Base Llama 3 model with general chat capabilities',
                'capabilities': ['chat']
            },
            'lbl/qwen-coder': {
                'description': 'Specialized code assistance model based on Qwen',
                'capabilities': ['code', 'chat']
            },
            'lbl/qwen-vision': {
                'description': 'Vision-capable model based on Qwen architecture',
                'capabilities': ['vision', 'chat']
            },
            'openai/gpt-4o': {
                'description': 'The latest high-quality multi-modal model from OpenAI for chat, coding and more',
                'capabilities': ['code', 'chat', 'vision']
            },
            'openai/gpt-4o-mini': {
                'description': 'Lightweight, low-cost multi-modal model from OpenAI for chat and vision',
                'capabilities': ['chat', 'vision']
            },
            'openai/o1': {
                'description': 'Latest release of deep reasoning model from OpenAI for chat, coding and analysis',
                'capabilities': ['code', 'chat']
            },
            'openai/o1-mini': {
                'description': 'Lightweight reasoning model from OpenAI for chat, coding and analysis',
                'capabilities': ['code', 'chat']
            },
            'openai/o3-mini': {
                'description': 'Latest lightweight reasoning model from OpenAI for chat, coding and analysis',
                'capabilities': ['code', 'chat']
            },
            'google/gemini-flash': {
                'description': 'Lightweight model with vision, optimized for speed and efficiency',
                'capabilities': ['chat', 'vision', 'fast']
            },
            'google/gemini-pro': {
                'description': 'Advanced model for general performance across a wide range of tasks',
                'capabilities': ['chat', 'code']
            },
            'anthropic/claude-haiku': {
                'description': 'Fast and affordable model, including vision capabilities',
                'capabilities': ['chat', 'vision', 'fast']
            },
            'anthropic/claude-sonnet': {
                'description': 'Latest version of cost-optimized model with excellent reasoning and coding',
                'capabilities': ['chat', 'code']
            },
            'anthropic/claude-opus': {
                'description': 'Advanced model for nuanced reasoning, math, coding and more',
                'capabilities': ['chat', 'code', 'math']
            },
            'wolfram/alpha': {
                'description': 'Knowledge base query source',
                'capabilities': ['query']
            }
        }
        
        # Default metadata for models without specific entries
        def get_default_metadata(model_id):
            return {
                'description': 'N/A',
                'capabilities': ['chat']
            }
        
        # Build response data
        response_data = {
            'models': models,
            'current_model': current_model,
            'default_model': PROVIDER_CONFIG[provider]['default_model'],
            'descriptions': {},
            'capabilities': {}
        }
        
        # Add metadata for each model
        for model in models:
            metadata = model_metadata.get(model, get_default_metadata(model))
            response_data['descriptions'][model] = metadata['description']
            response_data['capabilities'][model] = metadata['capabilities']
        
        print(f"Response data ready: {len(response_data['models'])} models")  # Debug log
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in get_models: {str(e)}")  # Debug log
        return jsonify({
            'error': f'Failed to fetch models: {str(e)}',
            'models': [],
            'current_model': None,
            'default_model': None,
            'descriptions': {},
            'capabilities': {}
        }), 500

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
        provider = session.get('current_provider', default_provider)
        
        # Validate provider
        if provider not in PROVIDER_CONFIG:
            return jsonify({
                'error': f'Invalid provider: {provider}'
            }), 400
        
        # Validate model availability
        if model not in PROVIDER_CONFIG[provider]['available_models']:
            return jsonify({
                'error': f'Model {model} is not available for provider {provider}'
            }), 400
        
        # Update session
        session['current_model'] = model
        
        # Update assistant's model
        assistant.model = model
        
        return jsonify({
            'success': True,
            'model': model
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
    try:
        # Reset the assistant's conversation history
        assistant.reset()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in reset: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)