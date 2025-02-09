import sys
import os
import logging
from pathlib import Path
import requests
import pandas as pd
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataDownloader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def download_gwas_catalog(self):
        """Download GWAS Catalog associations"""
        url = "https://www.ebi.ac.uk/gwas/api/search/downloads/alternative"
        output_file = self.raw_dir / "gwas-catalog-associations.tsv"
        
        try:
            logger.info("Downloading GWAS Catalog data...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded GWAS Catalog data to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading GWAS Catalog data: {e}")
            return False

    def download_wikipathways(self, organism="Homo sapiens"):
        """Download WikiPathways data"""
        base_url = "https://webservice.wikipathways.org"
        output_file = self.raw_dir / f"wikipathways_{organism.replace(' ', '_')}.json"
        
        try:
            logger.info(f"Downloading WikiPathways data for {organism}...")
            
            # First get list of pathways
            params = {
                'organism': organism,
                'format': 'json'
            }
            response = requests.get(f"{base_url}/listPathways", params=params)
            response.raise_for_status()
            pathways = response.json()
            
            # Download each pathway
            pathway_data = []
            for pathway in pathways['pathways']:
                pathway_id = pathway['id']
                logger.info(f"Downloading pathway {pathway_id}")
                
                pathway_response = requests.get(
                    f"{base_url}/getPathway",
                    params={'pwId': pathway_id, 'format': 'json'}
                )
                pathway_response.raise_for_status()
                pathway_data.append(pathway_response.json())
            
            # Save all pathway data
            with open(output_file, 'w') as f:
                json.dump(pathway_data, f)
            
            logger.info(f"Successfully downloaded {len(pathway_data)} pathways to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading WikiPathways data: {e}")
            return False

    def download_opentargets(self, disease_ids):
        """Download Open Targets Platform data"""
        url = "https://api.platform.opentargets.org/api/v4/graphql"
        output_file = self.raw_dir / "opentargets_data.json"
        
        query = """
        query DiseaseAssociations($diseaseId: String!) {
            disease(efoId: $diseaseId) {
                id
                name
                therapeuticAreas {
                    id
                    name
                }
                associatedTargets {
                    rows {
                        target {
                            id
                            approvedSymbol
                            approvedName
                        }
                        score
                        datatypeScores {
                            id
                            score
                        }
                    }
                }
            }
        }
        """
        
        try:
            logger.info("Downloading Open Targets data...")
            results = []
            
            for disease_id in disease_ids:
                response = requests.post(
                    url,
                    json={'query': query, 'variables': {'diseaseId': disease_id}}
                )
                response.raise_for_status()
                results.append(response.json())
            
            # Save results
            with open(output_file, 'w') as f:
                json.dump(results, f)
            
            logger.info(f"Successfully downloaded Open Targets data for {len(disease_ids)} diseases to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading Open Targets data: {e}")
            return False

def main():
    downloader = DataDownloader()
    
    # Download GWAS Catalog
    success = downloader.download_gwas_catalog()
    if not success:
        logger.error("Failed to download GWAS Catalog data")
    
    # Download WikiPathways
    success = downloader.download_wikipathways()
    if not success:
        logger.error("Failed to download WikiPathways data")
    
    # Download Open Targets data for cardiovascular diseases
    # Add relevant disease IDs here
    cardiovascular_disease_ids = [
        'EFO_0000318',  # cardiovascular disease
        'EFO_0000319',  # heart disease
        # Add more disease IDs as needed
    ]
    success = downloader.download_opentargets(cardiovascular_disease_ids)
    if not success:
        logger.error("Failed to download Open Targets data")

if __name__ == "__main__":
    main()
