"""
Main script for fetching and processing SSB emissions data
"""
import json
from pathlib import Path

from ssb_api import SSBApiClient
from data_processors import SSBDataProcessor
from file_manager import DataFileManager


def main():
    """Main function to fetch and process SSB emissions data"""
    
    # Setup
    project_root = Path(__file__).resolve().parents[2]
    api_client = SSBApiClient()
    processor = SSBDataProcessor()
    file_manager = DataFileManager(project_root)
    
    try:
        print("Fetching data from SSB API...")
        
        # Fetch raw data
        raw_data = api_client.fetch_emissions_data()
        
        # Save raw JSON
        raw_json_path = file_manager.save_raw_json(
            json.dumps(raw_data).encode('utf-8')
        )
        print(f"Raw JSON saved to {raw_json_path}")
        
        # Process and save formatted JSON
        formatted_data = processor.to_formatted_json(raw_data)
        formatted_json_path = file_manager.save_formatted_json(formatted_data)
        print(f"Formatted JSON saved to {formatted_json_path}")
        
        # Process and save raw CSV
        raw_df = processor.to_raw_csv(raw_data)
        raw_csv_path = file_manager.save_raw_csv(raw_df)
        print(f"Raw CSV saved to {raw_csv_path}")
        
        # Process and save clean CSV
        clean_df = processor.to_clean_csv(raw_data)
        clean_csv_path = file_manager.save_processed_csv(clean_df)
        print(f"Processed CSV saved to {clean_csv_path}")
        
        # Display summary
        stats = processor.get_summary_stats(clean_df)
        print(f"\nData Summary:")
        print(f"  Time period: {stats['time_period']}")
        print(f"  Data points: {stats['data_points']}")
        print(f"  Latest emissions ({stats['latest_emissions']['year']}): {stats['latest_emissions']['value_ktCO2e']:,} kt CO2-eq")
        print(f"  Peak emissions: {stats['peak_emissions']['value_ktCO2e']:,} kt CO2-eq in {stats['peak_emissions']['year']}")
        print(f"  Total change since 1990: {stats['total_change_pct']:+.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
