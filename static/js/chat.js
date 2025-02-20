// Model selection functionality
let modelSelector;

async function initializeModelSelector() {
    try {
        console.log('Fetching models...');  // Debug log
        const response = await fetch('/models');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Models response:', data);  // Debug log
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Group models by provider
        const modelsByProvider = new Map();
        data.models.forEach(model => {
            const [provider] = model.split('/');
            if (!modelsByProvider.has(provider)) {
                modelsByProvider.set(provider, []);
            }
            modelsByProvider.get(provider).push({
                id: model,
                description: data.descriptions?.[model] || 'No description available',
                capabilities: data.capabilities?.[model] || []
            });
        });
        
        console.log('Models grouped by provider:', modelsByProvider);  // Debug log

        // Initialize model selector
        const selectorElement = document.getElementById('model-selector');
        if (!selectorElement) {
            throw new Error('Model selector element not found');
        }
        
        modelSelector = new ModelSelector(selectorElement, {
            onModelSelect: async (model) => {
                try {
                    console.log('Model selected:', model);  // Debug log
                    await switchModel(model.id);
                } catch (error) {
                    console.error('Error switching model:', error);
                    appendMessage(`Failed to switch model: ${error.message}`, false);
                }
            }
        });

        modelSelector.providers = modelsByProvider;
        
        // Set current model if available
        if (data.current_model) {
            const currentProvider = data.current_model.split('/')[0];
            const providerModels = modelsByProvider.get(currentProvider);
            const currentModelData = providerModels?.find(m => m.id === data.current_model);
            if (currentModelData) {
                modelSelector.selectedModel = currentModelData;
            }
        }
        
        modelSelector.render();
        console.log('Model selector initialized');  // Debug log
    } catch (error) {
        console.error('Error initializing model selector:', error);
        appendMessage('Error loading models. Please try refreshing the page.', false);
    }
}

async function switchModel(model) {
    try {
        const response = await fetch('/switch_model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ model }),
        });
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to switch model');
        }
        
        appendMessage(`Switched to model: ${model}`, false);
        
    } catch (error) {
        console.error('Error switching model:', error);
        appendMessage(`Failed to switch model: ${error.message}`, false);
        throw error;
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeModelSelector();
});

let currentImageData = null;
let currentMediaType = null;

// Auto-resize textarea
const textarea = document.getElementById('message-input');
textarea.addEventListener('input', function() {
    this.style.height = '28px';
    this.style.height = (this.scrollHeight) + 'px';
});

function appendMessage(content, isUser = false) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-4 space-y-1';
    
    // Avatar
    const avatarDiv = document.createElement('div');
    if (isUser) {
        avatarDiv.className = 'w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-bold text-xs';
        avatarDiv.textContent = 'You';
    } else {
        avatarDiv.className = 'w-8 h-8 rounded-full ai-avatar flex items-center justify-center text-white font-bold text-xs';
        avatarDiv.textContent = 'CE';
    }
    
    // Message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'flex-1';
    
    const innerDiv = document.createElement('div');
    innerDiv.className = 'prose prose-slate max-w-none';
    
    if (!isUser && content) {
        try {
            innerDiv.innerHTML = marked.parse(content);
        } catch (e) {
            console.error('Error parsing markdown:', e);
            innerDiv.textContent = content;
        }
    } else {
        innerDiv.textContent = content || '';
    }
    
    contentDiv.appendChild(innerDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    messageWrapper.appendChild(messageDiv);
    messagesDiv.appendChild(messageWrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Event Listeners
document.getElementById('upload-btn').addEventListener('click', () => {
    document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.success) {
                currentImageData = data.image_data;
                currentMediaType = data.media_type;
                document.getElementById('preview-img').src = `data:${data.media_type};base64,${data.image_data}`;
                document.getElementById('image-preview').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        }
    }
});

document.getElementById('remove-image').addEventListener('click', () => {
    currentImageData = null;
    document.getElementById('image-preview').classList.add('hidden');
    document.getElementById('file-input').value = '';
});

function appendThinkingIndicator() {
    const messagesDiv = document.getElementById('chat-messages');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper thinking-message';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-4';
    
    // AI Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'w-8 h-8 rounded-full ai-avatar flex items-center justify-center text-white font-bold text-sm';
    avatarDiv.textContent = 'CE';
    
    // Thinking content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'flex-1';
    
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'thinking';
    thinkingDiv.innerHTML = '<div style="margin-top: 6px; margin-bottom: 4px;">Thinking<span class="thinking-dots"><span>.</span><span>.</span><span>.</span></span></div>';
    
    contentDiv.appendChild(thinkingDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    messageWrapper.appendChild(messageDiv);
    messagesDiv.appendChild(messageWrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return messageWrapper;
}

// Add command+enter handler
document.getElementById('message-input').addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    }
});

// Add function to show tool usage
function appendToolUsage(toolName) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-4';
    
    // AI Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'w-8 h-8 rounded-full ai-avatar flex items-center justify-center text-white font-bold text-sm';
    avatarDiv.textContent = 'CE';
    
    // Tool usage content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'flex-1';
    
    const toolDiv = document.createElement('div');
    toolDiv.className = 'tool-usage';
    toolDiv.textContent = `Using tool: ${toolName}`;
    
    contentDiv.appendChild(toolDiv);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    messageWrapper.appendChild(messageDiv);
    messagesDiv.appendChild(messageWrapper);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Add this function near the top of your file
function updateTokenUsage(usedTokens, maxTokens) {
    const percentage = (usedTokens / maxTokens) * 100;
    const tokenBar = document.getElementById('token-bar');
    const tokensUsed = document.getElementById('tokens-used');
    const tokenPercentage = document.getElementById('token-percentage');
    
    // Update the numbers
    tokensUsed.textContent = usedTokens.toLocaleString();
    tokenPercentage.textContent = `${percentage.toFixed(1)}%`;
    
    // Update the bar
    tokenBar.style.width = `${percentage}%`;
    
    // Update colors based on usage
    tokenBar.classList.remove('warning', 'danger');
    if (percentage > 90) {
        tokenBar.classList.add('danger');
    } else if (percentage > 75) {
        tokenBar.classList.add('warning');
    }
}

// Update the chat form submit handler
document.getElementById('chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (!message && !currentImageData) return;
    
    // Append user message (and image if present)
    appendMessage(message, true);
    if (currentImageData) {
        // Optionally show the image in the chat
        const imagePreview = document.createElement('img');
        imagePreview.src = `data:image/jpeg;base64,${currentImageData}`;
        imagePreview.className = 'max-h-48 rounded-lg mt-2';
        document.querySelector('.message-wrapper:last-child .prose').appendChild(imagePreview);
    }
    
    // Clear input and reset height
    messageInput.value = '';
    resetTextarea();
    
    try {
        // Add thinking indicator
        const thinkingMessage = appendThinkingIndicator();
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                image: currentImageData  // This will be null if no image is selected
            })
        });
        
        const data = await response.json();
        
        // Update token usage if provided in response
        if (data.token_usage) {
            updateTokenUsage(data.token_usage.total_tokens, data.token_usage.max_tokens);
        }
        
        // Remove thinking indicator
        if (thinkingMessage) {
            thinkingMessage.remove();
        }
        
        // Show tool usage if present
        if (data.tool_name) {
            appendToolUsage(data.tool_name);
        }
        
        // Show response if we have one
        if (data && data.response) {
            appendMessage(data.response);
        } else {
            appendMessage('Error: No response received');
        }
        
        // Clear image after sending
        currentImageData = null;
        document.getElementById('image-preview').classList.add('hidden');
        document.getElementById('file-input').value = '';
        
    } catch (error) {
        console.error('Error sending message:', error);
        document.querySelector('.thinking-message')?.remove();
        appendMessage('Error: Failed to send message');
    }
});

function resetTextarea() {
    const textarea = document.getElementById('message-input');
    textarea.style.height = '28px';
}

document.getElementById('chat-form').addEventListener('reset', () => {
    resetTextarea();
});

// Add at the top of the file
window.addEventListener('load', async () => {
    try {
        // Reset the conversation when page loads
        const response = await fetch('/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error('Failed to reset conversation');
        }
        
        // Clear any existing messages except the first one
        const messagesDiv = document.getElementById('chat-messages');
        const messages = messagesDiv.getElementsByClassName('message-wrapper');
        while (messages.length > 1) {
            messages[1].remove();
        }
        
        // Reset any other state
        currentImageData = null;
        document.getElementById('image-preview')?.classList.add('hidden');
        document.getElementById('file-input').value = '';
        document.getElementById('message-input').value = '';
        resetTextarea();
        
        // Reset token usage display
        updateTokenUsage(0, 200000);
    } catch (error) {
        console.error('Error resetting conversation:', error);
    }
}); 