class ModelSelector {
    constructor(element, options = {}) {
        this.element = element;
        this.providers = new Map();
        this.selectedModel = null;
        this.onModelSelect = options.onModelSelect || (() => {});
    }

    render() {
        const html = [];
        html.push('<div class="model-selector">');
        
        for (const [provider, models] of this.providers.entries()) {
            html.push(`
                <div class="provider-group">
                    <div class="provider-header">
                        <span class="provider-icon">🤖</span>
                        <span class="provider-name">${provider}</span>
                    </div>
                    <div class="models-list">
            `);
            
            for (const model of models) {
                html.push(`
                    <div class="model-item ${this.selectedModel?.id === model.id ? 'selected' : ''}"
                         data-model-id="${model.id}">
                        <div class="model-name">${model.id.split('/')[1]}</div>
                        <div class="model-description">${model.description || 'No description available'}</div>
                        <div class="model-capabilities">
                            ${(model.capabilities || []).map(cap => 
                                `<span class="capability-badge">${cap}</span>`
                            ).join('')}
                        </div>
                    </div>
                `);
            }
            
            html.push('</div></div>');
        }
        
        html.push('</div>');
        this.element.innerHTML = html.join('');

        // Add click handlers
        this.element.querySelectorAll('.model-item').forEach(item => {
            item.addEventListener('click', () => {
                const modelId = item.dataset.modelId;
                const [provider] = modelId.split('/');
                const model = this.providers.get(provider)?.find(m => m.id === modelId);
                if (model) {
                    this.selectedModel = model;
                    this.onModelSelect(model);
                    this.render();
                }
            });
        });
    }
}
