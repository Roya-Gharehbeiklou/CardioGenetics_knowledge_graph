from abc import ABC, abstractmethod
from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseLoader(ABC):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw"
        self.processed_dir = data_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def download_data(self):
        """Download data from source"""
        pass
    
    @abstractmethod
    def process_data(self):
        """Process raw data into standardized format"""
        pass
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to parquet format"""
        output_path = self.processed_dir / filename
        df.to_parquet(output_path)
        logger.info(f"Saved processed data to {output_path}")
