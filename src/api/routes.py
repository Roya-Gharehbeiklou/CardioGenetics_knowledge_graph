from flask import Blueprint, jsonify, request, send_file, abort
from pathlib import Path
import networkx as nx
import logging
from typing import Dict, List, Optional
import json

from src.data.gwas_loader import GWASLoader
from src.data.wikipathways_loader import WikiPathwaysLoader
from src.data.opentargets_loader import OpenTargetsLoader
from src.graph.builder import KnowledgeGraphBuilder
from src.graph.analysis import GraphAnalyzer
from src.visualization.network_viz import NetworkVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_api_blueprint():
    bp = Blueprint('api', __name__)
    
    # Initialize components
    data_dir = Path("data")
    graph_builder = KnowledgeGraphBuilder()

    # Create temporary directory for visualizations
    viz_dir = Path("static/visualizations")
    viz_dir.mkdir(parents=True, exist_ok=True)

    @bp.before_app_first_request
    def initialize_graph():
        """Initialize the knowledge graph with data from all sources"""
        try:
            # Initialize data loaders
            gwas_loader = GWASLoader(data_dir)
            wikipathways_loader = WikiPathwaysLoader(data_dir)
            opentargets_loader = OpenTargetsLoader(data_dir)
            
            # Load and process GWAS data
            gwas_associations = gwas_loader.process_data()
            graph_builder.add_gwas_associations(gwas_associations)
            
            logger.info("Successfully initialized knowledge graph")
            
        except Exception as e:
            logger.error(f"Error initializing graph: {e}")
            raise

    @bp.route('/statistics', methods=['GET'])
    def get_graph_statistics():
        """Get basic statistics about the knowledge graph"""
        try:
            stats = graph_builder.get_graph_statistics()
            return jsonify(stats)
        except Exception as e:
            logger.error(f"Error getting graph statistics: {e}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/visualization', methods=['GET'])
    def get_visualization():
        """Generate and return an interactive visualization of the graph"""
        try:
            output_path = viz_dir / 'network.html'
            visualizer = NetworkVisualizer(graph_builder.get_graph())
            visualizer.create_interactive_visualization(str(output_path))
            return send_file(str(output_path))
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/nodes/<node_id>/neighborhood', methods=['GET'])
    def get_node_neighborhood(node_id: str):
        """Get the neighborhood of a specific node"""
        try:
            distance = request.args.get('distance', default=1, type=int)
            neighborhood = graph_builder.get_node_neighborhood(node_id, distance)
            return jsonify(neighborhood)
        except Exception as e:
            logger.error(f"Error getting node neighborhood: {e}")
            return jsonify({'error': str(e)}), 500

    return bp