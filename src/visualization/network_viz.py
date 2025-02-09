import networkx as nx
from pyvis.network import Network
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class NetworkVisualizer:
    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.node_colors = {
            'gene': '#2ecc71',      # Green
            'disease': '#e74c3c',    # Red
            'pathway': '#3498db',    # Blue
            'drug': '#9b59b6'        # Purple
        }
    
    def create_interactive_visualization(self, output_path: str,
                                      height: str = "750px",
                                      width: str = "100%",
                                      bgcolor: str = "#ffffff"):
        """Create an interactive HTML visualization of the graph"""
        try:
            # Initialize PyVis network
            net = Network(height=height, 
                         width=width, 
                         bgcolor=bgcolor, 
                         font_color="black")
            
            # Configure physics
            net.force_atlas_2based()
            net.show_buttons(filter_=['physics'])
            
            # Add nodes
            for node, attr in self.graph.nodes(data=True):
                node_type = attr.get('type', 'unknown')
                net.add_node(
                    node,
                    label=attr.get('name', node),
                    color=self.node_colors.get(node_type, '#95a5a6'),
                    title=self._create_node_tooltip(node, attr)
                )
            
            # Add edges
            for source, target, attr in self.graph.edges(data=True):
                net.add_edge(
                    source,
                    target,
                    title=self._create_edge_tooltip(attr),
                    color={'color': '#666666', 'opacity': 0.8}
                )
            
            # Set options
            net.set_options(self._get_network_options())
            
            # Save visualization
            net.show(output_path)
            logger.info(f"Created interactive visualization at {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating interactive visualization: {e}")
            raise
    
    def create_subgraph_visualization(self, 
                                    central_node: str, 
                                    max_distance: int = 2,
                                    output_path: str = None):
        """Create a visualization of a subgraph centered around a specific node"""
        try:
            # Extract subgraph
            subgraph = nx.ego_graph(self.graph, central_node, radius=max_distance)
            
            # Create new visualizer for subgraph
            subgraph_viz = NetworkVisualizer(subgraph)
            
            if output_path:
                subgraph_viz.create_interactive_visualization(output_path)
            
            return subgraph_viz
            
        except Exception as e:
            logger.error(f"Error creating subgraph visualization: {e}")
            raise
    
    def create_cluster_visualization(self, 
                                   clusters: Dict[str, int],
                                   output_path: str):
        """Create a visualization with nodes colored by cluster"""
        try:
            # Initialize PyVis network
            net = Network(height="750px", 
                         width="100%", 
                         bgcolor="#ffffff", 
                         font_color="black")
            
            # Generate colors for clusters
            unique_clusters = len(set(clusters.values()))
            cluster_colors = self._generate_cluster_colors(unique_clusters)
            
            # Add nodes with cluster colors
            for node, attr in self.graph.nodes(data=True):
                cluster_id = clusters.get(node, 0)
                net.add_node(
                    node,
                    label=attr.get('name', node),
                    color=cluster_colors[cluster_id],
                    title=f"Cluster: {cluster_id}\n{self._create_node_tooltip(node, attr)}"
                )
            
            # Add edges
            for source, target, attr in self.graph.edges(data=True):
                net.add_edge(source, target)
            
            # Set options
            net.set_options(self._get_network_options())
            
            # Save visualization
            net.show(output_path)
            logger.info(f"Created cluster visualization at {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating cluster visualization: {e}")
            raise
    
    def create_centrality_visualization(self, 
                                      centrality_scores: Dict[str, float],
                                      output_path: str):
        """Create a visualization with node sizes based on centrality scores"""
        try:
            # Initialize PyVis network
            net = Network(height="750px", 
                         width="100%", 
                         bgcolor="#ffffff", 
                         font_color="black")
            
            # Normalize centrality scores for node sizing
            max_score = max(centrality_scores.values())
            min_size = 10
            max_size = 50
            
            # Add nodes with varying sizes
            for node, attr in self.graph.nodes(data=True):
                node_type = attr.get('type', 'unknown')
                size = min_size + (centrality_scores.get(node, 0) / max_score) * (max_size - min_size)
                
                net.add_node(
                    node,
                    label=attr.get('name', node),
                    color=self.node_colors.get(node_type, '#95a5a6'),
                    size=size,
                    title=f"Centrality: {centrality_scores.get(node, 0):.3f}\n{self._create_node_tooltip(node, attr)}"
                )
            
            # Add edges
            for source, target, attr in self.graph.edges(data=True):
                net.add_edge(source, target)
            
            # Set options
            net.set_options(self._get_network_options())
            
            # Save visualization
            net.show(output_path)
            logger.info(f"Created centrality visualization at {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating centrality visualization: {e}")
            raise
    
    def _create_node_tooltip(self, node: str, attr: Dict) -> str:
        """Create HTML tooltip for node"""
        tooltip = f"<strong>ID:</strong> {node}<br>"
        tooltip += f"<strong>Type:</strong> {attr.get('type', 'unknown')}<br>"
        
        if 'name' in attr:
            tooltip += f"<strong>Name:</strong> {attr['name']}<br>"
            
        for key, value in attr.items():
            if key not in ['id', 'type', 'name', 'color']:
                tooltip += f"<strong>{key}:</strong> {value}<br>"
                
        return tooltip
    
    def _create_edge_tooltip(self, attr: Dict) -> str:
        """Create HTML tooltip for edge"""
        tooltip = f"<strong>Type:</strong> {attr.get('type', 'unknown')}<br>"
        
        for key, value in attr.items():
            if key != 'type':
                tooltip += f"<strong>{key}:</strong> {value}<br>"
                
        return tooltip
    
    def _get_network_options(self) -> str:
        """Get network visualization options"""
        options = {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08
                },
                "maxVelocity": 50,
                "solver": "forceAtlas2Based",
                "timestep": 0.35,
                "stabilization": {"iterations": 150}
            },
            "edges": {
                "smooth": {"type": "continuous"},
                "color": {"inherit": False}
            },
            "interaction": {
                "hover": True,
                "tooltipDelay": 200
            }
        }
        
        return json.dumps(options)
    
    def _generate_cluster_colors(self, num_clusters: int) -> List[str]:
        """Generate distinct colors for clusters"""
        import colorsys
        
        colors = []
        for i in range(num_clusters):
            hue = i / num_clusters
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.8)
            colors.append('#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            ))
        
        return colors
