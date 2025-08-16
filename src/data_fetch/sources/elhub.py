"""
Elhub data source for energy consumption data
"""
import requests
import pandas as pd
import json
from typing import Dict, Any, Optional
import os
from datetime import datetime
from pathlib import Path


class ElhubApiClient:
    """Client for fetching data from Elhub APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ELHUB_API_KEY')
        # Elhub's correct API v0 endpoints
        self.base_url = 'https://api.elhub.no/energy-data/v0'
        self.entities = ['Price Areas', 'Grid Areas', 'Metering Points', 'Municipalities']
        self.datasets = {
            'consumption': 'CONSUMPTION_PER_GROUP_MBA_HOUR',
            'production': 'PRODUCTION_PER_GROUP_MBA_HOUR'
        }
        
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
    
    def list_available_options(self):
        """List available entities and datasets for debugging"""
        print("🔍 Elhub API v0 Configuration:")
        print(f"Base URL: {self.base_url}")
        print(f"Available entities: {', '.join(self.entities)}")
        print(f"Available datasets: {', '.join(self.datasets.values())}")
        print(f"API Key configured: {'✅ Yes' if self.api_key else '❌ No'}")
    
    def fetch_energy_consumption_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch energy consumption data from Elhub using correct API v0 structure
        """
        # Try different entities for consumption data
        entities_to_try = [
            ('Price Areas', 'price-areas'),
            ('Grid Areas', 'grid-areas'), 
            ('Municipalities', 'municipalities'),
            ('Metering Points', 'metering-points')
        ]
        
        for entity_name, entity_param in entities_to_try:
            try:
                # Construct the correct API URL
                url = f"{self.base_url}/{entity_param}"
                
                print(f"Trying Elhub endpoint: {url}")
                
                # Parameters for the request
                params = {
                    'dataset': self.datasets['consumption']
                }
                
                response = requests.get(
                    url,
                    headers=self.get_headers(),
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ Successfully fetched consumption data for {entity_name}")
                    return {
                        'metadata': {
                            'source': 'Elhub Energy Data API v0',
                            'entity': entity_name,
                            'dataset': self.datasets['consumption'],
                            'endpoint': url
                        },
                        'data': response.json()
                    }
                elif response.status_code == 401:
                    print(f"🔑 Authentication required for {entity_name}")
                    continue
                elif response.status_code == 404:
                    print(f"❌ Endpoint not found for {entity_name}: {url}")
                    continue
                elif response.status_code == 403:
                    print(f"🚫 Access forbidden for {entity_name} - may need API key")
                    continue
                else:
                    print(f"⚠️ Error {response.status_code} for {entity_name}: {response.text[:200]}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed for {entity_name}: {e}")
                continue
        
        # If all Elhub endpoints fail, try production data as fallback
        print("\n🔄 Trying production data as fallback...")
        return self._fetch_production_data()
    
    def _fetch_production_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch energy production data as fallback
        """
        entities_to_try = [
            ('Price Areas', 'price-areas'),
            ('Grid Areas', 'grid-areas'), 
            ('Municipalities', 'municipalities')
        ]
        
        for entity_name, entity_param in entities_to_try:
            try:
                url = f"{self.base_url}/{entity_param}"
                
                print(f"Trying production endpoint: {url}")
                
                params = {
                    'dataset': self.datasets['production']
                }
                
                response = requests.get(
                    url,
                    headers=self.get_headers(),
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ Successfully fetched production data for {entity_name}")
                    return {
                        'metadata': {
                            'source': 'Elhub Energy Data API v0',
                            'entity': entity_name,
                            'dataset': self.datasets['production'],
                            'endpoint': url
                        },
                        'data': response.json()
                    }
                elif response.status_code == 401:
                    print(f"🔑 Authentication required for production data - {entity_name}")
                    continue
                else:
                    print(f"⚠️ Error {response.status_code} for production {entity_name}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed for production {entity_name}: {e}")
                continue
        
        # If all fails, try alternative sources
        return self._fetch_alternative_energy_data()
    
    def _fetch_alternative_energy_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch energy data from SSB as an alternative to Elhub
        """
        try:
            # SSB table for energy consumption
            ssb_endpoint = "https://data.ssb.no/api/v0/no/table/08303"
            
            query = {
                "query": [
                    {
                        "code": "Energibærer",
                        "selection": {
                            "filter": "item",
                            "values": ["00"]  # Total energy
                        }
                    },
                    {
                        "code": "ContentsCode",
                        "selection": {
                            "filter": "item", 
                            "values": ["Forbruk"]  # Consumption
                        }
                    }
                ],
                "response": {
                    "format": "json-stat2"
                }
            }
            
            response = requests.post(ssb_endpoint, json=query, timeout=30)
            
            if response.status_code == 200:
                print("Successfully fetched alternative energy data from SSB")
                return response.json()
            else:
                print(f"Alternative energy data fetch failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Failed to fetch household energy data: {e}")
            return None


class ElhubDataProcessor:
    """Process Elhub energy data into analysis-ready formats"""
    
    @staticmethod
    def to_consumption_summary(elhub_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert Elhub consumption data to summary DataFrame
        
        Args:
            elhub_data: Raw Elhub API response
            
        Returns:
            DataFrame with aggregated consumption data
        """
        records = []
        
        if 'raw_data' in elhub_data and 'data' in elhub_data['raw_data']:
            for area_data in elhub_data['raw_data']['data']:
                if 'attributes' in area_data and 'consumptionPerGroupMbaHour' in area_data['attributes']:
                    for consumption_record in area_data['attributes']['consumptionPerGroupMbaHour']:
                        records.append({
                            'timestamp': consumption_record.get('startTime'),
                            'price_area': consumption_record.get('priceArea'),
                            'consumption_group': consumption_record.get('consumptionGroup'),
                            'quantity_kwh': consumption_record.get('quantityKwh'),
                            'metering_points': consumption_record.get('meteringPointCount'),
                            'area_id': area_data.get('id'),
                            'country': area_data.get('attributes', {}).get('country')
                        })
        
        df = pd.DataFrame(records)
        
        if not df.empty:
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            
        return df
    
    @staticmethod
    def get_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        Get daily consumption summary by price area
        
        Args:
            df: Processed consumption DataFrame
            
        Returns:
            DataFrame with daily aggregated data
        """
        if df.empty:
            return pd.DataFrame()
            
        daily_summary = df.groupby(['date', 'price_area', 'consumption_group']).agg({
            'quantity_kwh': 'sum',
            'metering_points': 'mean'  # Average metering points per day
        }).reset_index()
        
        return daily_summary
def fetch_elhub_data() -> bool:
    """
    Main function to fetch Elhub data using the correct API v0 structure
    Returns True if successful, False otherwise
    """
    try:
        client = ElhubApiClient()
        
        # Show available options for debugging
        client.list_available_options()
        
        data = client.fetch_energy_consumption_data()
        
        if data:
            # Save raw data
            raw_dir = Path(__file__).resolve().parents[3] / "data/raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            with open(raw_dir / 'elhub_energy.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            # Process and save formatted data
            formatted_data = {
                'metadata': {
                    'source': 'Elhub Energy Data API v0',
                    'fetched_at': datetime.now().isoformat(),
                    'description': 'Norwegian energy consumption/production data',
                    'api_info': data.get('metadata', {})
                },
                'raw_data': data.get('data', {}),
                'summary': {
                    'entity': data.get('metadata', {}).get('entity', 'Unknown'),
                    'dataset': data.get('metadata', {}).get('dataset', 'Unknown'),
                    'endpoint': data.get('metadata', {}).get('endpoint', 'Unknown')
                }
            }
            
            with open(raw_dir / 'elhub_energy_formatted.json', 'w') as f:
                json.dump(formatted_data, f, indent=2)
            
            print("✅ Elhub energy data fetched and saved successfully")
            return True
        else:
            print("❌ Failed to fetch Elhub energy data from all sources")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching Elhub data: {e}")
        return False
