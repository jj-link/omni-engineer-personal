from flask import Flask, render_template, request, jsonify, url_for, session
from ce3 import Assistant
import os
from werkzeug.utils import secure_filename
import base64
from config import Config

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.urandom(24)  # For session management

# Provider configuration
PROVIDER_CONFIG = {
    'cborg': {
        'base_url': 'https://api.cborg.lbl.gov',
        'default_model': 'lbl/cborg-coder:latest',
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
        'requires_key': False,
        'parameters': {
            'temperature': 0.7,
            'top_p': 0.9,
            'seed': None
        }
    }
}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the assistant with default provider (ollama)
assistant = Assistant()
current_provider = 'ollama'
current_parameters = PROVIDER_CONFIG['ollama']['parameters'].copy()

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
    
    # Store provider in session
    session['current_provider'] = provider
    
    # Reset parameters to provider defaults
    session['current_parameters'] = PROVIDER_CONFIG[provider]['parameters'].copy()
    
    return jsonify({
        'success': True,
        'provider': provider,
        'default_model': PROVIDER_CONFIG[provider]['default_model']
    })

@app.route('/models', methods=['GET'])
def get_models():
    """Get available models for current provider"""
    provider = session.get('current_provider', 'ollama')
    
    if provider == 'ollama':
        models = ['codellama']  # For now, just return default model
    else:  # cborg
        models = ['lbl/cborg-coder:latest']  # For now, just return default model
    
    return jsonify({
        'models': models,
        'current_model': PROVIDER_CONFIG[provider]['default_model']
    })

@app.route('/params', methods=['GET'])
def get_parameters():
    """Get current parameter configuration"""
    provider = session.get('current_provider', 'ollama')
    params = session.get('current_parameters', PROVIDER_CONFIG[provider]['parameters'])
    return jsonify(params)

@app.route('/update_params', methods=['POST'])
def update_parameters():
    """Update parameter configuration"""
    data = request.json
    
    # Validate parameters
    if 'temperature' in data:
        temp = float(data['temperature'])
        if temp < 0 or temp > 1:
            return jsonify({
                'success': False,
                'error': 'Temperature must be between 0 and 1'
            }), 400
    
    if 'top_p' in data:
        top_p = float(data['top_p'])
        if top_p < 0 or top_p > 1:
            return jsonify({
                'success': False,
                'error': 'Top-p must be between 0 and 1'
            }), 400
    
    # Update parameters in session
    current_params = session.get('current_parameters', 
                               PROVIDER_CONFIG[session.get('current_provider', 'ollama')]['parameters'])
    current_params.update(data)
    session['current_parameters'] = current_params
    
    return jsonify({
        'success': True,
        'parameters': current_params
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    image_data = data.get('image')  # Get the base64 image data
    
    # Prepare the message content
    if image_data:
        # Create a message with both text and image in correct order
        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",  # We should detect this from the image
                    "data": image_data.split(',')[1] if ',' in image_data else image_data  # Remove data URL prefix if present
                }
            }
        ]
        
        # Only add text message if there is actual text
        if message.strip():
            message_content.append({
                "type": "text",
                "text": message
            })
    else:
        # Text-only message
        message_content = message
    
    try:
        # Handle the chat message with the appropriate content
        response = assistant.chat(message_content)
        
        # Get token usage from assistant
        token_usage = {
            'total_tokens': assistant.total_tokens_used,
            'max_tokens': Config.MAX_CONVERSATION_TOKENS
        }
        
        # Get the last used tool from the conversation history
        tool_name = None
        if assistant.conversation_history:
            for msg in reversed(assistant.conversation_history):
                if msg.get('role') == 'assistant' and msg.get('content'):
                    content = msg['content']
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'tool_use':
                                tool_name = block.get('name')
                                break
                    if tool_name:
                        break
        
        return jsonify({
            'response': response,
            'thinking': False,
            'tool_name': tool_name,
            'token_usage': token_usage
        })
        
    except Exception as e:
        return jsonify({
            'response': f"Error: {str(e)}",
            'thinking': False,
            'tool_name': None,
            'token_usage': None
        }), 200  # Return 200 even for errors to handle them gracefully in frontend

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