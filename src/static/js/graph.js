class KnowledgeGraphUI {
    constructor() {
        this.network = null;
        this.data = {
            nodes: new vis.DataSet([]),
            edges: new vis.DataSet([])
        };
        this.options = {
            nodes: {
                shape: 'dot',
                size: 16,
                font: {
                    size: 12,
                    color: '#333333'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 1,
                color: {
                    color: '#848484',
                    highlight: '#1e88e5',
                    hover: '#848484'
                },
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                forceAtlas2Based: {
                    gravitationalConstant: -26,
                    centralGravity: 0.005,
                    springLength: 230,
                    springConstant: 0.18
                },
                maxVelocity: 146,
                solver: 'forceAtlas2Based',
                timestep: 0.35,
                stabilization: { iterations: 150 }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                zoomView: true,
                dragView: true
            }
        };
        this.container = document.getElementById('graph-container');
        this.initializeNetwork();
        this.setupEventListeners();
    }

    initializeNetwork() {
        this.network = new vis.Network(this.container, this.data, this.options);
        this.loadInitialData();
    }

    async loadInitialData() {
        try {
            this.showLoading();
            const response = await fetch('/api/graph/statistics');
            const stats = await response.json();
            this.updateStatistics(stats);
            await this.loadGraphData();
            this.hideLoading();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.hideLoading();
            this.showError('Failed to load graph data');
        }
    }

    async loadGraphData() {
        try {
            const response = await fetch('/api/graph/nodes');
            const graphData = await response.json();
            this.updateGraph(graphData);
        } catch (error) {
            console.error('Error loading graph data:', error);
            this.showError('Failed to load graph data');
        }
    }

    updateGraph(graphData) {
        // Clear existing data
        this.data.nodes.clear();
        this.data.edges.clear();

        // Add new nodes and edges
        this.data.nodes.add(graphData.nodes);
        this.data.edges.add(graphData.edges);

        // Fit the network to view all nodes
        this.network.fit();
    }

    updateStatistics(stats) {
        document.getElementById('total-nodes').textContent = stats.total_nodes;
        document.getElementById('total-edges').textContent = stats.total_edges;
        document.getElementById('total-clusters').textContent = stats.clusters || 0;
    }

    setupEventListeners() {
        // Node click event
        this.network.on('click', async (params) => {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                await this.showNodeDetails(nodeId);
            }
        });

        // Search functionality
        const searchInput = document.querySelector('input[type="text"]');
        searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));

        // Filter checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', this.handleFilter.bind(this));
        });

        // Analysis tools buttons
        document.querySelectorAll('.analysis-tool').forEach(button => {
            button.addEventListener('click', this.handleAnalysis.bind(this));
        });
    }

    async showNodeDetails(nodeId) {
        try {
            const response = await fetch(`/api/graph/nodes/${nodeId}`);
            const nodeData = await response.json();
            
            const infoPanel = document.getElementById('info-panel');
            const nodeDetails = document.getElementById('node-details');
            
            // Populate node details
            nodeDetails.innerHTML = this.generateNodeDetailsHTML(nodeData);
            
            // Show the panel
            infoPanel.classList.remove('hidden');
        } catch (error) {
            console.error('Error loading node details:', error);
            this.showError('Failed to load node details');
        }
    }

    generateNodeDetailsHTML(nodeData) {
        return `
            <div class="space-y-4">
                <div>
                    <h3 class="font-semibold">ID</h3>
                    <p>${nodeData.id}</p>
                </div>
                <div>
                    <h3 class="font-semibold">Type</h3>
                    <p>${nodeData.type}</p>
                </div>
                <div>
                    <h3 class="font-semibold">Properties</h3>
                    <div class="bg-gray-50 p-2 rounded">
                        ${Object.entries(nodeData.properties || {})
                            .map(([key, value]) => `<div><span class="font-medium">${key}:</span> ${value}</div>`)
                            .join('')}
                    </div>
                </div>
                <div>
                    <h3 class="font-semibold">Connected Nodes</h3>
                    <div class="bg-gray-50 p-2 rounded max-h-40 overflow-y-auto">
                        ${nodeData.connections
                            .map(conn => `<div class="hover:bg-gray-100 p-1">${conn}</div>`)
                            .join('')}
                    </div>
                </div>
            </div>
        `;
    }

    async handleSearch(event) {
        const searchTerm = event.target.value;
        if (searchTerm.length < 2) return;

        try {
            const response = await fetch(`/api/graph/search?q=${encodeURIComponent(searchTerm)}`);
            const results = await response.json();
            this.showSearchResults(results);
        } catch (error) {
            console.error('Error searching:', error);
        }
    }

    handleFilter(event) {
        const filterType = event.target.nextElementSibling.textContent.toLowerCase();
        const isChecked = event.target.checked;

        // Update node visibility based on filter
        const nodeIds = this.data.nodes.getIds();
        const updates = nodeIds.map(id => {
            const node = this.data.nodes.get(id);
            if (node.type === filterType) {
                return { id, hidden: !isChecked };
            }
            return null;
        }).filter(update => update !== null);

        this.data.nodes.update(updates);
    }

    async handleAnalysis(event) {
        const analysisType = event.target.textContent.toLowerCase();
        this.showLoading();

        try {
            const response = await fetch(`/api/graph/analysis/${analysisType}`);
            const results = await response.json();
            this.showAnalysisResults(analysisType, results);
        } catch (error) {
            console.error('Error running analysis:', error);
            this.showError('Failed to run analysis');
        } finally {
            this.hideLoading();
        }
    }

    showSearchResults(results) {
        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'search-results absolute w-full bg-white shadow-lg rounded-b-lg';
        
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item hover:bg-gray-100 p-2';
            item.textContent = result.label;
            item.addEventListener('click', () => this.focusNode(result.id));
            resultsContainer.appendChild(item);
        });

        // Replace existing results if any
        const existingResults = document.querySelector('.search-results');
        if (existingResults) {
            existingResults.remove();
        }
        document.querySelector('.search-container').appendChild(resultsContainer);
    }

    focusNode(nodeId) {
        this.network.focus(nodeId, {
            scale: 1.5,
            animation: true
        });
        this.network.selectNodes([nodeId]);
    }

    showAnalysisResults(type, results) {
        const resultsPanel = document.getElementById('analysis-results');
        resultsPanel.innerHTML = `
            <h3 class="text-lg font-semibold mb-2">${type.charAt(0).toUpperCase() + type.slice(1)} Results</h3>
            <div class="analysis-result">
                <pre>${JSON.stringify(results, null, 2)}</pre>
            </div>
        `;
        resultsPanel.classList.remove('hidden');
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }

    showError(message) {
        // Implement error notification
        console.error(message);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize the UI when the document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.graphUI = new KnowledgeGraphUI();
});
