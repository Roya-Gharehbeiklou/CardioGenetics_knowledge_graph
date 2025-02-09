import sys
import os
import logging
from pathlib import Path
import pandas as pd
import json
from typing import List, Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def process_gwas_data(self, disease_terms: List[str] = None):
        """Process GWAS catalog data"""
        if disease_terms is None:
            disease_terms = ['heart', 'cardiac', 'cardiovascular', 'coronary']
        
        input_file = self.raw_dir / "gwas-catalog-associations.tsv"
        output_file = self.processed_dir / "gwas_cardiovascular.parquet"
        
        try:
            logger.info("Processing GWAS Catalog data...")
            
            # Read data
            df = pd.read_csv(input_file, sep='\t', low_memory=False)
            
            # Filter for cardiovascular traits
            pattern = '|'.join(disease_terms)
            filtered_df = df[df['DISEASE/TRAIT'].str.lower().str.contains(pattern, na=False)]
            
            # Extract relevant columns
            processed_df = filtered_df[[
                'STUDY ACCESSION',
                'DISEASE/TRAIT',
                'REPORTED GENE(S)',
                'MAPPED_GENE',
                'P-VALUE',
                'OR or BETA',
                'LINK'
            ]].copy()
            
            # Clean gene names
            processed_df['MAPPED_GENE'] = processed_df['MAPPED_GENE'].fillna('')
            processed_df['MAPPED_GENE'] = processed_df['MAPPED_GENE'].str.split(',').apply(
                lambda x: [gene.strip() for gene in x if gene.strip()]
            )
            
            # Save processed data
            processed_df.to_parquet(output_file)
            logger.info(f"Successfully processed GWAS data: {len(processed_df)} associations saved")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing GWAS data: {e}")
            return False

    def process_wikipathways_data(self):
        """Process WikiPathways data"""
        input_file = self.raw_dir / "wikipathways_Homo_sapiens.json"
        output_file = self.processed_dir / "wikipathways_processed.parquet"
        
        try:
            logger.info("Processing WikiPathways data...")
            
            # Read data
            with open(input_file, 'r') as f:
                pathway_data = json.load(f)
            
            # Process pathways
            processed_data = []
            for pathway in pathway_data:
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
            
            # Convert to DataFrame and save
            processed_df = pd.DataFrame(processed_data)
            processed_df.to_parquet(output_file)
            
            logger.info(f"Successfully processed WikiPathways data: {len(processed_df)} pathways saved")
            return True
            
        except Exception as e:
            logger.error(f"Error processing WikiPathways data: {e}")
            return False

    def process_opentargets_data(self):
        """Process Open Targets data"""
        input_file = self.raw_dir / "opentargets_data.json"
        output_file = self.processed_dir / "opentargets_processed.parquet"
        
        try:
            logger.info("Processing Open Targets data...")
            
            # Read data
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Process and flatten data
            processed_data = []
            for response in data:
                disease_data = response['data']['disease']
                
                for target in disease_data['associatedTargets']['rows']:
                    processed_data.append({
                        'disease_id': disease_data['id'],
                        'disease_name': disease_data['name'],
                        'target_id': target['target']['id'],
                        'target_symbol': target['target']['approvedSymbol'],
                        'target_name': target['target']['approvedName'],
                        'association_score': target['score']
                    })
            
            # Convert to DataFrame and save
            processed_df = pd.DataFrame(processed_data)
            processed_df.to_parquet(output_file)
            
            logger.info(f"Successfully processed Open Targets data: {len(processed_df)} associations saved")
            return True
            
        except Exception as e:
            logger.error(f"Error processing Open Targets data: {e}")
            return False

def main():
    processor = DataProcessor()
    
    # Process GWAS data
    success = processor.process_gwas_data()
    if not success:
        logger.error("Failed to process GWAS data")
    
    # Process WikiPathways data
    success = processor.process_wikipathways_data()
    if not success:
        logger.error("Failed to process WikiPathways data")
    
    # Process Open Targets data
    success = processor.process_opentargets_data()
    if not success:
        logger.error("Failed to process Open Targets data")

if __name__ == "__main__":
    main()
