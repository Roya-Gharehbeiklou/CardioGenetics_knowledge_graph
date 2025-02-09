import networkx as nx
from typing import Dict, List, Optional

class GraphAnalyzer:
    def __init__(self, graph: nx.Graph):
        self.graph = graph
    
    def get_graph_statistics(self) -> Dict:
        """Get basic statistics about the graph"""
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges()
        }