// Model selection functionality
async function initializeModelSelector() {
    try {
        console.log('Fetching models...');
        const response = await fetch('/models', {
            credentials: 'same-origin',  // Include cookies
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Models response:', data);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        const element = document.getElementById('model-selector');
        if (!element) {
            throw new Error('Model selector element not found');
        }

        // Clear existing content
        element.innerHTML = '';

        // Add current model display
        const currentModelDiv = document.createElement('div');
        currentModelDiv.className = 'current-model';
        currentModelDiv.innerHTML = `
            <div class="label">Current Model</div>
            <div class="value">${data.current_model || 'None selected'}</div>
        `;
        element.appendChild(currentModelDiv);

        // Add provider sections
        const groups = data.model_groups || {};
        Object.entries(groups).forEach(([provider, models]) => {
            const section = document.createElement('div');
            section.className = 'provider-section';
            
            const header = document.createElement('div');
            header.className = 'provider-header';
            header.innerHTML = `
                <img src="/static/img/provider-icon.png" alt="${provider}" class="provider-icon">
                <span>${provider}</span>
                <span class="expand-icon">+</span>
            `;
            
            const modelList = document.createElement('div');
            modelList.className = 'model-list';
            modelList.style.display = 'none';
            
            models.forEach(model => {
                const modelItem = document.createElement('div');
                modelItem.className = 'model-item';
                modelItem.innerHTML = `
                    <img src="/static/img/model-icon.png" alt="${model}" class="model-icon">
                    <span class="model-name">${model}</span>
                `;
                modelItem.title = data.descriptions?.[model] || '';
                modelItem.addEventListener('click', () => selectModel(model));
                modelList.appendChild(modelItem);
            });
            
            header.addEventListener('click', () => {
                const isExpanded = modelList.style.display !== 'none';
                modelList.style.display = isExpanded ? 'none' : 'block';
                header.querySelector('.expand-icon').textContent = isExpanded ? '+' : '-';
            });
            
            section.appendChild(header);
            section.appendChild(modelList);
            element.appendChild(section);
        });
        
    } catch (error) {
        console.error('Error initializing model selector:', error);
    }
}

async function selectModel(model) {
    try {
        console.log('Switching to model:', model);
        const response = await fetch('/switch_model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',  // Include cookies
            body: JSON.stringify({ model })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to switch model');
        }
        
        // Update current model display
        const currentModelValue = document.querySelector('.current-model .value');
        if (currentModelValue) {
            currentModelValue.textContent = model;
        }
        
        console.log('Successfully switched to model:', model);
        
    } catch (error) {
        console.error('Error switching model:', error);
        alert('Failed to switch model: ' + error.message);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializeModelSelector);

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
                credentials: 'same-origin',  // Include cookies
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
    const tokenDisplay = document.getElementById('token-display');
    const tokenBar = document.getElementById('token-progress');
    
    if (!tokenDisplay || !tokenBar) return;  // Skip if elements don't exist
    
    tokenDisplay.textContent = `${usedTokens.toLocaleString()} / ${maxTokens.toLocaleString()}`;
    
    const percentage = (usedTokens / maxTokens) * 100;
    tokenBar.style.width = `${percentage}%`;
    
    // Update color based on usage
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
            credentials: 'same-origin',  // Include cookies
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
            },
            credentials: 'same-origin',  // Include cookies
        });
        
        if (!response.ok) {
            throw new Error('Failed to reset conversation');
        }
        
        // Clear any existing messages except the first one
        const messagesDiv = document.getElementById('chat-messages');
        if (messagesDiv) {
            const messages = messagesDiv.getElementsByClassName('message-wrapper');
            while (messages.length > 1) {
                messages[1].remove();
            }
        }
        
        // Reset any other state
        currentImageData = null;
        const imagePreview = document.getElementById('image-preview');
        const fileInput = document.getElementById('file-input');
        const messageInput = document.getElementById('message-input');
        
        if (imagePreview) imagePreview.classList.add('hidden');
        if (fileInput) fileInput.value = '';
        if (messageInput) messageInput.value = '';
        
        resetTextarea();
        
        // Reset token usage display if the elements exist
        updateTokenUsage(0, 200000);
        
    } catch (error) {
        console.error('Error resetting conversation:', error);
    }
}); 

let currentImageData = null;
let currentMediaType = null;