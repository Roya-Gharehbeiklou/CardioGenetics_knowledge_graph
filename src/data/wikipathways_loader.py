import pandas as pd
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict
from .base_loader import BaseLoader, logger

class WikiPathwaysLoader(BaseLoader):
    def __init__(self, data_dir: Path):
        super().__init__(data_dir)
        self.pathways_file = self.raw_dir / "wikipathways.xml"
        self.processed_file = self.processed_dir / "wikipathways_cardiovascular.parquet"
        self.api_url = "https://webservice.wikipathways.org"
    
    def download_data(self):
        """Download cardiovascular pathways from WikiPathways"""
        try:
            # Get list of cardiovascular pathways
            params = {
                'query': 'cardiovascular',
                'format': 'json'
            }
            response = requests.get(f"{self.api_url}/findPathwaysByText", params=params)
            response.raise_for_status()
            
            pathways_data = response.json()
            
            # Download each pathway
            pathway_list = []
            for pathway in pathways_data['result']:
                pathway_id = pathway['id']
                
                # Get pathway details
                pathway_response = requests.get(
                    f"{self.api_url}/getPathway",
                    params={'pwId': pathway_id, 'format': 'json'}
                )
                pathway_response.raise_for_status()
                pathway_list.append(pathway_response.json())
            
            # Save raw data
            pd.DataFrame(pathway_list).to_json(self.pathways_file)
            logger.info(f"Downloaded {len(pathway_list)} pathways")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading WikiPathways data: {e}")
            raise
    
    def process_data(self) -> pd.DataFrame:
        """Process WikiPathways data"""
        try:
            # Read raw data
            pathways_df = pd.read_json(self.pathways_file)
            
            # Extract relevant information
            processed_data = []
            for _, pathway in pathways_df.iterrows():
                pathway_info = {
                    'pathway_id': pathway['id'],
                    'pathway_name': pathway['name'],
                    'genes': [],
                    'interactions': []
                }
                
                # Extract genes and interactions
                for element in pathway.get('elements', []):
                    if element['type'] == 'gene':
                        pathway_info['genes'].append(element['name'])
                    elif element['type'] == 'interaction':
                        pathway_info['interactions'].append({
                            'source': element['source'],
                            'target': element['target']
                        })
                
                processed_data.append(pathway_info)
            
            # Convert to DataFrame
            processed_df = pd.DataFrame(processed_data)
            
            # Save processed data
            self.save_processed_data(processed_df, "wikipathways_cardiovascular.parquet")
            
            return processed_df
            
        except Exception as e:
            logger.error(f"Error processing WikiPathways data: {e}")
            raise