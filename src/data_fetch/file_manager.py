"""
File management utilities for saving data in various formats
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any


class DataFileManager:
    """Manage saving data files in different formats"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.raw_dir = project_root / "data" / "raw"
        self.processed_dir = project_root / "data" / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def save_raw_json(self, data: bytes, filename: str = "ssb_emissions.json") -> Path:
        """Save raw JSON response from API"""
        filepath = self.raw_dir / filename
        filepath.write_bytes(data)
        return filepath
    
    def save_formatted_json(self, data: Dict[str, Any], filename: str = "ssb_emissions_formatted.json") -> Path:
        """Save formatted JSON data"""
        filepath = self.raw_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath
    
    def save_raw_csv(self, df: pd.DataFrame, filename: str = "ssb_emissions_raw.csv") -> Path:
        """Save raw CSV data"""
        filepath = self.raw_dir / filename
        df.to_csv(filepath, index=False)
        return filepath
    
    def save_processed_csv(self, df: pd.DataFrame, filename: str = "ssb_emissions_clean.csv") -> Path:
        """Save processed CSV data"""
        filepath = self.processed_dir / filename
        df.to_csv(filepath, index=False)
        return filepath
