"""
Data processors for converting SSB JSON-stat2 data to different formats
"""
import json
import pandas as pd
from typing import Dict, Any, List


class SSBDataProcessor:
    """Process SSB JSON-stat2 data into various formats"""
    
    @staticmethod
    def to_formatted_json(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert JSON-stat2 format to readable JSON structure
        
        Args:
            raw_data: Raw JSON-stat2 data from SSB API
            
        Returns:
            Formatted JSON with metadata and clean data structure
        """
        formatted_data = {
            "metadata": {
                "table_id": raw_data.get("extension", {}).get("px", {}).get("tableid", "08940"),
                "title": raw_data.get("label", ""),
                "source": raw_data.get("source", ""),
                "updated": raw_data.get("updated", ""),
                "notes": raw_data.get("note", []),
                "unit": "1,000 tonnes CO2-equivalents (AR4)",
                "contact": raw_data.get("extension", {}).get("contact", [])
            },
            "dimensions": {
                "source": raw_data["dimension"]["UtslpTilLuft"]["category"]["label"],
                "pollutant": raw_data["dimension"]["UtslpKomp"]["category"]["label"],
                "contents": raw_data["dimension"]["ContentsCode"]["category"]["label"]
            },
            "data": []
        }
        
        # Extract emissions data
        years = list(raw_data["dimension"]["Tid"]["category"]["label"].values())
        values = raw_data["value"]
        
        for year, value in zip(years, values):
            formatted_data["data"].append({
                "year": int(year),
                "emissions_ktCO2e": value
            })
        
        return formatted_data
    
    @staticmethod
    def to_raw_csv(raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert to raw CSV format preserving original structure
        
        Args:
            raw_data: Raw JSON-stat2 data from SSB API
            
        Returns:
            DataFrame with original API structure and codes
        """
        years = list(raw_data["dimension"]["Tid"]["category"]["label"].values())
        values = raw_data["value"]
        
        return pd.DataFrame({
            "Tid": years,  # Original dimension name
            "UtslippCO2ekvival": values,  # Original value name
            "UtslpTilLuft": ["0"] * len(years),  # Source code
            "UtslpKomp": ["A10"] * len(years),  # Pollutant code
            "table_id": ["08940"] * len(years),  # Table identifier
            "unit": ["1000_tonnes_CO2_eq"] * len(years)  # Unit info
        })
    
    @staticmethod
    def to_clean_csv(raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert to analysis-ready CSV format
        
        Args:
            raw_data: Raw JSON-stat2 data from SSB API
            
        Returns:
            DataFrame with clean, analysis-ready data
        """
        years = list(raw_data["dimension"]["Tid"]["category"]["label"].values())
        values = raw_data["value"]
        
        return pd.DataFrame({
            "year": [int(year) for year in years],
            "emissions_ktCO2e": values,
            "emissions_MtCO2e": [round(val / 1000, 2) for val in values],  # Convert to million tonnes
            "source": ["All sources"] * len(years),
            "pollutant": ["Greenhouse gases total"] * len(years),
            "country": ["Norway"] * len(years)
        })
    
    @staticmethod
    def get_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for emissions data
        
        Args:
            df: Clean DataFrame with emissions data
            
        Returns:
            Dictionary with summary statistics
        """
        return {
            "time_period": f"{df['year'].min()} - {df['year'].max()}",
            "data_points": len(df),
            "latest_emissions": {
                "year": int(df.iloc[-1]['year']),
                "value_ktCO2e": int(df.iloc[-1]['emissions_ktCO2e'])
            },
            "peak_emissions": {
                "value_ktCO2e": int(df['emissions_ktCO2e'].max()),
                "year": int(df.loc[df['emissions_ktCO2e'].idxmax(), 'year'])
            },
            "total_change_pct": round(
                ((df.iloc[-1]['emissions_ktCO2e'] - df.iloc[0]['emissions_ktCO2e']) 
                 / df.iloc[0]['emissions_ktCO2e']) * 100, 1
            )
        }
