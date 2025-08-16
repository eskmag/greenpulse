"""
SSB (Statistics Norway) data source for greenhouse gas emissions
"""
import requests
import json
import pandas as pd
import os
from pathlib import Path
from typing import Dict, Any, Optional


class SSBApiClient:
    """Client for Statistics Norway (SSB) API"""
    
    def __init__(self, base_url: str = "https://data.ssb.no/api/v0/en/table", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key or os.getenv('SSB_API_KEY')
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication if available"""
        headers = {
            'User-Agent': 'GreenPulse-DataFetch/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        return headers
    
    def fetch_emissions_data(self, table_id: str = "13931") -> Dict[str, Any]:
        """
        Fetch greenhouse gas emissions data from SSB
        
        Args:
            table_id: SSB table identifier
            
        Returns:
            Raw JSON data from the API
            
        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.base_url}/{table_id}"
        
        query = {
            "query": [
                {
                    "code": "UtslpTilLuft",
                    "selection": {"filter": "item", "values": ["0"]}  # All sources
                },
                {
                    "code": "UtslpKomp", 
                    "selection": {"filter": "item", "values": ["A10"]}  # Greenhouse gases total
                },
                {
                    "code": "ContentsCode",
                    "selection": {"filter": "item", "values": ["UtslippCO2ekvival"]}
                }
            ],
            "response": {"format": "json-stat2"}
        }
        
        response = requests.post(url, json=query, headers=self.get_headers())
        
        if response.status_code == 200:
            return json.loads(response.content.decode("utf-8"))
        else:
            raise requests.RequestException(
                f"Failed to fetch data: {response.status_code} - {response.text}"
            )


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


def fetch_ssb_data():
    """Legacy function for simple SSB data fetching"""
    # Filstier
    RAW_PATH = Path(__file__).resolve().parents[3] / "data/raw/ssb_emissions.json"
    CSV_PATH = Path(__file__).resolve().parents[3] / "data/processed/ssb_emissions.csv"

    # API-endepunkt
    url = "https://data.ssb.no/api/v0/no/table/13931/"

    # Spørring (Paris-avtale total klimagassutslipp, CO2-ekv)
    query = {
        "query": [
            {
                "code": "Klimagass",
                "selection": {"filter": "item", "values": ["A10"]}  # Alle klimagasser
            },
            {
                "code": "ContentsCode",
                "selection": {"filter": "item", "values": ["UtslippCO2ekvivalenter"]}
            }
        ],
        "response": {"format": "json-stat2"}
    }

    # Get headers with potential authentication
    headers = {
        'User-Agent': 'GreenPulse-DataFetch/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    api_key = os.getenv('SSB_API_KEY')
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    response = requests.post(url, json=query, headers=headers)
    if response.status_code == 200:
        # Lagre rådata
        RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
        RAW_PATH.write_bytes(response.content)
        print(f"✅ Rådata lagret til {RAW_PATH}")

        # Parse JSON til DataFrame
        data = json.loads(response.content.decode("utf-8"))
        years = list(data["dimension"]["Tid"]["category"]["label"].keys())
        values = data["value"]

        df = pd.DataFrame({"year": years, "emissions_CO2eq": values})
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CSV_PATH, index=False)
        print(f"✅ Prosessert CSV lagret til {CSV_PATH}")
    else:
        print(f"❌ Feil ved henting av SSB-data: {response.status_code} - {response.text}")
