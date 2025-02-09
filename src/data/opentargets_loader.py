import pandas as pd
import requests
from pathlib import Path
from typing import List, Dict
from .base_loader import BaseLoader, logger

class OpenTargetsLoader(BaseLoader):
    def __init__(self, data_dir: Path):
        super().__init__(data_dir)
        self.data_file = self.raw_dir / "opentargets_data.json"
        self.processed_file = self.processed_dir / "opentargets_cardiovascular.parquet"
        self.api_url = "https://api.platform.opentargets.org/api/v4/graphql"
    
    def download_data(self, disease_ids: List[str]):
        """Download data from Open Targets Platform"""
        try:
            # GraphQL query for disease associations
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
            
            results = []
            for disease_id in disease_ids:
                response = requests.post(
                    self.api_url,
                    json={'query': query, 'variables': {'diseaseId': disease_id}}
                )
                response.raise_for_status()
                results.append(response.json())
            
            # Save raw data
            pd.DataFrame(results).to_json(self.data_file)
            logger.info(f"Downloaded data for {len(disease_ids)} diseases")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading Open Targets data: {e}")
            raise
    
    def process_data(self) -> pd.DataFrame:
        """Process Open Targets data"""
        try:
            # Read raw data
            data_df = pd.read_json(self.data_file)
            
            # Extract and flatten relevant information
            processed_data = []
            for _, row in data_df.iterrows():
                disease_data = row['data']['disease']
                
                for target in disease_data['associatedTargets']['rows']:
                    processed_data.append({
                        'disease_id': disease_data['id'],
                        'disease_name': disease_data['name'],
                        'target_id': target['target']['id'],
                        'target_symbol': target['target']['approvedSymbol'],
                        'target_name': target['target']['approvedName'],
                        'association_score': target['score']
                    })
            
            # Convert to DataFrame
            processed_df = pd.DataFrame(processed_data)
            
            # Save processed data
            self.save_processed_data(processed_df, "opentargets_cardiovascular.parquet")
            
            return processed_df
            
        except Exception as e:
            logger.error(f"Error processing Open Targets data: {e}")
            raise