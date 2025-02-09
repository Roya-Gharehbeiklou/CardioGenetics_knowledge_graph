import pandas as pd
import requests
from pathlib import Path
from typing import List, Dict, Optional
from .base_loader import BaseLoader, logger

class GWASLoader(BaseLoader):
    def __init__(self, data_dir: Path):
        super().__init__(data_dir)
        self.gwas_file = self.raw_dir / "gwas-catalog-associations.tsv"
        self.processed_file = self.processed_dir / "gwas_cardiovascular.parquet"
    
    def download_data(self):
        """Download GWAS Catalog associations"""
        url = "https://www.ebi.ac.uk/gwas/api/search/downloads/alternative"
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(self.gwas_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Successfully downloaded GWAS data to {self.gwas_file}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading GWAS data: {e}")
            raise
    
    def process_data(self, disease_terms: Optional[List[str]] = None) -> pd.DataFrame:
        """Process GWAS data with optional disease term filtering"""
        if disease_terms is None:
            disease_terms = ['heart', 'cardiac', 'cardiovascular', 'coronary']
        
        try:
            df = pd.read_csv(self.gwas_file, sep='\t', low_memory=False)
            
            # Filter for specified disease terms
            pattern = '|'.join(disease_terms)
            filtered_df = df[df['DISEASE/TRAIT'].str.lower().str.contains(pattern, na=False)]
            
            # Extract and clean relevant columns
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
            self.save_processed_data(processed_df, "gwas_cardiovascular.parquet")
            
            return processed_df
            
        except Exception as e:
            logger.error(f"Error processing GWAS data: {e}")
            raise