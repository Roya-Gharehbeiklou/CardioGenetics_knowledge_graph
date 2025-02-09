import networkx as nx
import pandas as pd
from typing import Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    def __init__(self):
        self.graph = nx.Graph()
        self.node_types = {
            'gene': '#2ecc71',      # Green
            'disease': '#e74c3c',    # Red
            'pathway': '#3498db',    # Blue
            'drug': '#9b59b6'        # Purple
        }
    
    def add_node(self, node_id: str, node_type: str, **attributes):
        """Add a node with its type and additional attributes"""
        if node_id not in self.graph:
            self.graph.add_node(
                node_id,
                type=node_type,
                color=self.node_types.get(node_type, '#95a5a6'),
                **attributes
            )
    
    def add_edge(self, source: str, target: str, edge_type: str, **attributes):
        """Add an edge with its type and additional attributes"""
        self.graph.add_edge(
            source,
            target,
            type=edge_type,
            **attributes
        )
    
    def add_gwas_associations(self, gwas_df: pd.DataFrame):
        """Add GWAS disease-gene associations to the graph"""
        try:
            for _, row in gwas_df.iterrows():
                disease = row['DISEASE/TRAIT']
                self.add_node(disease, 'disease')
                
                # Add gene nodes and edges
                for gene in row['MAPPED_GENE']:
                    if gene:  # Skip empty genes
                        self.add_node(gene, 'gene')
                        self.add_edge(
                            disease,
                            gene,
                            'gwas_association',
                            p_value=row['P-VALUE'],
                            effect=row['OR or BETA'],
                            study=row['STUDY ACCESSION']
                        )
            
            logger.info(f"Added GWAS associations: {len(gwas_df)} studies processed")
            
        except Exception as e:
            logger.error(f"Error adding GWAS associations: {e}")
            raise
    
    def add_pathway_associations(self, pathways_df: pd.DataFrame):
        """Add pathway associations to the graph"""
        try:
            for _, row in pathways_df.iterrows():
                pathway_id = row['pathway_id']
                self.add_node(
                    pathway_id,
                    'pathway',
                    name=row['pathway_name']
                )
                
                # Add genes in pathway
                for gene in row['genes']:
                    self.add_node(gene, 'gene')
                    self.add_edge(
                        pathway_id,
                        gene,
                        'pathway_member'
                    )
                
                # Add interactions
                for interaction in row['interactions']:
                    self.add_edge(
                        interaction['source'],
                        interaction['target'],
                        'pathway_interaction'
                    )
            
            logger.info(f"Added pathway associations: {len(pathways_df)} pathways processed")
            
        except Exception as e:
            logger.error(f"Error adding pathway associations: {e}")
            raise
    
    def add_opentargets_associations(self, opentargets_df: pd.DataFrame):
        """Add Open Targets disease-target associations to the graph"""
        try:
            for _, row in opentargets_df.iterrows():
                disease_id = row['disease_id']
                self.add_node(
                    disease_id,
                    'disease',
                    name=row['disease_name']
                )
                
                target_id = row['target_id']
                self.add_node(
                    target_id,
                    'gene',
                    symbol=row['target_symbol'],
                    name=row['target_name']
                )
                
                self.add_edge(
                    disease_id,
                    target_id,
                    'target_association',
                    score=row['association_score']
                )
            
            logger.info(f"Added Open Targets associations: {len(opentargets_df)} associations processed")
            
        except Exception as e:
            logger.error(f"Error adding Open Targets associations: {e}")
            raise
    
    def get_graph_statistics(self) -> Dict:
        """Get basic statistics about the knowledge graph"""
        try:
            stats = {
                'total_nodes': self.graph.number_of_nodes(),
                'total_edges': self.graph.number_of_edges(),
                'node_types': {},
                'edge_types': {}
            }
            
            # Count node types
            for node, attrs in self.graph.nodes(data=True):
                node_type = attrs.get('type', 'unknown')
                stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1
            
            # Count edge types
            for _, _, attrs in self.graph.edges(data=True):
                edge_type = attrs.get('type', 'unknown')
                stats['edge_types'][edge_type] = stats['edge_types'].get(edge_type, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating graph statistics: {e}")
            raise
    
    def find_paths_between_nodes(self, source: str, target: str, max_length: int = 3) -> List[List[str]]:
        """Find all paths between two nodes up to a maximum length"""
        try:
            all_paths = []
            for path in nx.all_simple_paths(self.graph, source, target, cutoff=max_length):
                all_paths.append(path)
            return all_paths
            
        except Exception as e:
            logger.error(f"Error finding paths between nodes: {e}")
            raise
    
    def get_node_neighborhood(self, node_id: str, distance: int = 1) -> nx.Graph:
        """Get the subgraph containing the specified node and its neighbors up to given distance"""
        try:
            if node_id not in self.graph:
                raise ValueError(f"Node {node_id} not found in graph")
                
            return nx.ego_graph(self.graph, node_id, radius=distance)
            
        except Exception as e:
            logger.error(f"Error getting node neighborhood: {e}")
            raise
    
    def calculate_node_centrality(self, centrality_type: str = 'degree') -> Dict[str, float]:
        """Calculate node centrality using specified method"""
        try:
            centrality_functions = {
                'degree': nx.degree_centrality,
                'betweenness': nx.betweenness_centrality,
                'eigenvector': nx.eigenvector_centrality,
                'pagerank': nx.pagerank
            }
            
            if centrality_type not in centrality_functions:
                raise ValueError(f"Unsupported centrality type: {centrality_type}")
            
            return centrality_functions[centrality_type](self.graph)
            
        except Exception as e:
            logger.error(f"Error calculating node centrality: {e}")
            raise
    
    def save_graph(self, output_path: Path):
        """Save the graph to a file"""
        try:
            nx.write_gexf(self.graph, output_path)
            logger.info(f"Saved graph to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving graph: {e}")
            raise
    
    def load_graph(self, input_path: Path):
        """Load a graph from a file"""
        try:
            self.graph = nx.read_gexf(input_path)
            logger.info(f"Loaded graph from {input_path}")
            
        except Exception as e:
            logger.error(f"Error loading graph: {e}")
            raise

    def get_common_neighbors(self, node1: str, node2: str) -> List[str]:
        """Get common neighbors between two nodes"""
        try:
            return list(nx.common_neighbors(self.graph, node1, node2))
        except Exception as e:
            logger.error(f"Error getting common neighbors: {e}")
            raise

    def get_graph(self) -> nx.Graph:
        """Return the constructed graph"""
        return self.graph
