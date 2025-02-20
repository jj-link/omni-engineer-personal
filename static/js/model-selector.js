class ModelSelector {
    constructor(element, options = {}) {
        this.element = element;
        this.providers = new Map();
        this.selectedModel = null;
        this.onModelSelect = options.onModelSelect || (() => {});
        this.expandedProviders = new Set(); // Track which providers are expanded
    }

    render() {
        const html = [];
        html.push('<div class="model-selector">');
        
        // Show selected model at the top if one exists
        if (this.selectedModel) {
            const [provider, modelName] = this.selectedModel.id.split('/');
            html.push(`
                <div class="current-model">
                    <div class="text-sm text-gray-500 mb-1">Current Model</div>
                    <div class="selected-model-display">
                        <span class="provider-icon">🤖</span>
                        <div class="selected-model-info">
                            <div class="font-medium">${modelName}</div>
                            <div class="text-sm text-gray-500">${provider}</div>
                        </div>
                    </div>
                </div>
            `);
        }
        
        html.push('<div class="providers-list">');
        for (const [provider, models] of this.providers.entries()) {
            const isExpanded = this.expandedProviders.has(provider);
            html.push(`
                <div class="provider-group">
                    <div class="provider-header" data-provider="${provider}">
                        <div class="provider-header-content">
                            <span class="provider-icon">🤖</span>
                            <span class="provider-name">${provider}</span>
                        </div>
                        <span class="expand-icon">${isExpanded ? '−' : '+'}</span>
                    </div>
                    <div class="models-list ${isExpanded ? 'expanded' : ''}">
            `);
            
            for (const model of models) {
                const [, modelName] = model.id.split('/');
                html.push(`
                    <div class="model-item ${this.selectedModel?.id === model.id ? 'selected' : ''}"
                         data-model-id="${model.id}">
                        <div class="model-name">${modelName}</div>
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
        html.push('</div></div>');
        
        this.element.innerHTML = html.join('');

        // Add click handlers for provider headers
        this.element.querySelectorAll('.provider-header').forEach(header => {
            header.addEventListener('click', () => {
                const provider = header.dataset.provider;
                if (this.expandedProviders.has(provider)) {
                    this.expandedProviders.delete(provider);
                } else {
                    this.expandedProviders.add(provider);
                }
                this.render();
            });
        });

        // Add click handlers for model items
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
