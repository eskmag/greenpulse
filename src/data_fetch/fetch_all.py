"""
Main data fetching orchestrator for all data sources
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Handle both direct execution and module imports
if __name__ == "__main__":
    # Add the project root to the path for direct execution
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from src.data_fetch.sources.ssb import SSBApiClient, SSBDataProcessor, fetch_ssb_data
    from src.data_fetch.sources.elhub import fetch_elhub_data
    from src.data_fetch.sources.enova import fetch_enova_data
else:
    # Use relative imports when imported as a module
    from .sources.ssb import SSBApiClient, SSBDataProcessor, fetch_ssb_data
    from .sources.elhub import fetch_elhub_data
    from .sources.enova import fetch_enova_data


class DataFileManager:
    """Manage saving data files in different formats"""
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]
        
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
    
    def save_raw_csv(self, df, filename: str = "ssb_emissions_raw.csv") -> Path:
        """Save raw CSV data"""
        filepath = self.raw_dir / filename
        df.to_csv(filepath, index=False)
        return filepath
    
    def save_processed_csv(self, df, filename: str = "ssb_emissions_clean.csv") -> Path:
        """Save processed CSV data"""
        filepath = self.processed_dir / filename
        df.to_csv(filepath, index=False)
        return filepath


def fetch_all_data():
    """Fetch data from all sources"""
    print("🚀 Starting data fetch from all sources...")
    
    # Initialize file manager
    file_manager = DataFileManager()
    
    # Fetch SSB emissions data
    print("\n📊 Fetching SSB emissions data...")
    try:
        ssb_client = SSBApiClient()
        raw_data = ssb_client.fetch_emissions_data()
        
        # Save in multiple formats
        file_manager.save_raw_json(
            json.dumps(raw_data).encode('utf-8'),
            "ssb_emissions.json"
        )
        
        formatted_data = SSBDataProcessor.to_formatted_json(raw_data)
        file_manager.save_formatted_json(formatted_data)
        
        raw_df = SSBDataProcessor.to_raw_csv(raw_data)
        file_manager.save_raw_csv(raw_df)
        
        clean_df = SSBDataProcessor.to_clean_csv(raw_data)
        file_manager.save_processed_csv(clean_df)
        
        print("✅ SSB data fetched and saved successfully")
        
    except Exception as e:
        print(f"❌ Error fetching SSB data: {e}")
    
    # Fetch Elhub data
    print("\n⚡ Fetching Elhub energy data...")
    try:
        fetch_elhub_data()
    except Exception as e:
        print(f"❌ Error fetching Elhub data: {e}")
    
    # Fetch Enova data
    print("\n🔋 Fetching Enova energy efficiency data...")
    try:
        fetch_enova_data()
    except Exception as e:
        print(f"❌ Error fetching Enova data: {e}")
    
    print("\n🎉 Data fetch completed!")


def fetch_ssb_only():
    """Fetch only SSB data (legacy compatibility)"""
    print("📊 Fetching SSB data...")
    fetch_ssb_data()


if __name__ == "__main__":
    fetch_all_data()
