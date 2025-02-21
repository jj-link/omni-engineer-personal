// @jest-environment jsdom
const fs = require('fs');
const path = require('path');

describe('ModelSelector', () => {
    let modelSelector;
    let mockFetch;

    beforeEach(() => {
        // Set up document body
        document.body.innerHTML = '<div id="model-selector"></div>';
        
        // Mock fetch responses
        mockFetch = jest.fn();
        global.fetch = mockFetch;
        
        // Import ModelSelector class
        const modelSelectorJs = fs.readFileSync(
            path.resolve(__dirname, '../static/js/model_selector.js'),
            'utf8'
        );
        eval(modelSelectorJs);
    });

    it('should load models for both providers on initialization', async () => {
        // Mock provider list response
        mockFetch
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    providers: ['ollama', 'cborg'],
                    current_provider: 'cborg'
                })
            })
            // Mock CBORG models response
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    provider: 'cborg',
                    format: 'grouped',
                    model_groups: {
                        'lbl': ['model1', 'model2'],
                        'openai': ['model3']
                    },
                    capabilities: {},
                    descriptions: {}
                })
            })
            // Mock switch to Ollama response
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ success: true })
            })
            // Mock Ollama models response
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    provider: 'ollama',
                    format: 'flat',
                    models: [
                        { name: 'codellama:latest', size: '5GB', modified: '2 weeks ago' },
                        { name: 'llama2:latest', size: '4GB', modified: '3 weeks ago' }
                    ]
                })
            })
            // Mock switch back to CBORG response
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ success: true })
            })
            // Mock final CBORG models response
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    provider: 'cborg',
                    format: 'grouped',
                    model_groups: {
                        'lbl': ['model1', 'model2'],
                        'openai': ['model3']
                    }
                })
            });

        // Initialize model selector
        document.dispatchEvent(new Event('DOMContentLoaded'));

        // Wait for all promises to resolve
        await new Promise(resolve => setTimeout(resolve, 0));

        // Verify fetch calls
        expect(mockFetch.mock.calls).toEqual([
            ['/providers'],
            ['/models'],
            ['/select_provider', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider: 'ollama' })
            }],
            ['/models'],
            ['/select_provider', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider: 'cborg' })
            }],
            ['/models']
        ]);

        // Verify providers are stored
        const modelSelector = document.querySelector('#model-selector').__modelSelector;
        expect(modelSelector.providers.has('ollama')).toBe(true);
        expect(modelSelector.providers.has('cborg')).toBe(true);

        // Verify Ollama models
        const ollamaData = modelSelector.providers.get('ollama');
        expect(ollamaData.format).toBe('flat');
        expect(ollamaData.models).toHaveLength(2);
        expect(ollamaData.models[0].name).toBe('codellama:latest');

        // Verify CBORG models
        const cborgData = modelSelector.providers.get('cborg');
        expect(cborgData.format).toBe('grouped');
        expect(Object.keys(cborgData.model_groups)).toContain('lbl');
        expect(Object.keys(cborgData.model_groups)).toContain('openai');
    });
});

describe('Model Selection', () => {
    beforeEach(() => {
        // Reset DOM
        document.body.innerHTML = `
            <div id="modelSelector"></div>
            <div id="currentModel"></div>
        `;
    });

    test('should display Ollama models when Ollama provider is selected', async () => {
        // Mock fetch for provider switch
        global.fetch = jest.fn().mockImplementation((url) => {
            if (url.endsWith('/select_provider')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ success: true, provider: 'ollama' })
                });
            }
            if (url.endsWith('/models')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        provider: 'ollama',
                        format: 'flat',
                        models: [
                            { name: 'codellama:latest', size: '5.0GB', modified: '2 days ago' },
                            { name: 'llama2:latest', size: '4.2GB', modified: '3 days ago' }
                        ]
                    })
                });
            }
        });

        // Initialize model selector
        await initializeModelSelector();

        // Switch to Ollama provider
        await switchProvider('ollama');

        // Verify Ollama models are displayed
        const modelSelector = document.getElementById('modelSelector');
        expect(modelSelector.innerHTML).toContain('codellama:latest');
        expect(modelSelector.innerHTML).toContain('llama2:latest');
        
        // Verify model details are shown
        expect(modelSelector.innerHTML).toContain('5.0GB');
        expect(modelSelector.innerHTML).toContain('2 days ago');
    });
});
