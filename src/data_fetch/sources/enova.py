"""
Enova data source for energy efficiency and renewable energy data
"""
import requests
import pandas as pd
import json
from typing import Dict, Any, Optional
import os
from datetime import datetime
from pathlib import Path


class EnovaApiClient:
    """Client for fetching data from Enova and alternative energy efficiency sources"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ENOVA_API_KEY')
        # Enova's actual endpoints and alternatives
        self.base_urls = {
            'enova_public': 'https://www.enova.no/api/v1',
            # Alternative: NVE energy efficiency data
            'nve_efficiency': 'https://api.nve.no/web/EnergyEfficiency',
            # Alternative: SSB energy efficiency statistics
            'ssb_efficiency': 'https://data.ssb.no/api/v0/no/table'
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
            # Some APIs use different auth headers
            headers['X-API-Key'] = self.api_key
            
        return headers
    
    def fetch_energy_efficiency_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch energy efficiency data from Enova or alternative sources
        """
        # Try Enova endpoints first
        enova_endpoints = [
            f"{self.base_urls['enova_public']}/projects/statistics",
            f"{self.base_urls['enova_public']}/efficiency/data",
            "https://www.enova.no/bedrift/transport/statistikk/api/data"
        ]
        
        for endpoint in enova_endpoints:
            try:
                print(f"Trying Enova endpoint: {endpoint}")
                response = requests.get(
                    endpoint,
                    headers=self.get_headers(),
                    params={
                        'year': '2023,2024',
                        'category': 'all'
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print(f"Authentication required for {endpoint}")
                    continue
                elif response.status_code == 404:
                    print(f"Endpoint not found: {endpoint}")
                    continue
                else:
                    print(f"Error {response.status_code} for {endpoint}: {response.text}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed for {endpoint}: {e}")
                continue
        
        # If Enova fails, try alternative sources
        return self._fetch_alternative_efficiency_data()
    
    def _fetch_alternative_efficiency_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch energy efficiency data from SSB as an alternative to Enova
        """
        try:
            # SSB table for energy efficiency/renewable energy
            ssb_endpoint = "https://data.ssb.no/api/v0/no/table/12733"  # Renewable energy table
            
            query = {
                "query": [
                    {
                        "code": "Energikilde",
                        "selection": {
                            "filter": "item",
                            "values": ["00"]  # Total renewable
                        }
                    },
                    {
                        "code": "ContentsCode", 
                        "selection": {
                            "filter": "item",
                            "values": ["Produksjon"]  # Production
                        }
                    }
                ],
                "response": {
                    "format": "json-stat2"
                }
            }
            
            response = requests.post(ssb_endpoint, json=query, timeout=30)
            
            if response.status_code == 200:
                print("Successfully fetched alternative energy efficiency data from SSB")
                return response.json()
            else:
                print(f"Alternative efficiency data fetch failed: {response.status_code}")
                # Try another SSB table for energy use in households
                return self._fetch_household_energy_data()
                
        except Exception as e:
            print(f"Failed to fetch alternative efficiency data: {e}")
            return self._fetch_household_energy_data()
    
    def _fetch_household_energy_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch household energy consumption as proxy for efficiency data
        """
        try:
            # SSB table for household energy consumption
            ssb_endpoint = "https://data.ssb.no/api/v0/no/table/10482"
            
            query = {
                "query": [
                    {
                        "code": "Energikilde",
                        "selection": {
                            "filter": "item",
                            "values": ["0"]  # All energy sources
                        }
                    }
                ],
                "response": {
                    "format": "json-stat2"
                }
            }
            
            response = requests.post(ssb_endpoint, json=query, timeout=30)
            
            if response.status_code == 200:
                print("Successfully fetched household energy data from SSB")
                return response.json()
            else:
                print(f"Household energy data fetch failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Failed to fetch household energy data: {e}")
            return None


def fetch_enova_data() -> bool:
    """
    Main function to fetch Enova data
    Returns True if successful, False otherwise
    """
    try:
        client = EnovaApiClient()
        data = client.fetch_energy_efficiency_data()
        
        if data:
            # Save raw data
            raw_dir = Path(__file__).resolve().parents[3] / "data/raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            with open(raw_dir / 'enova_efficiency.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            # Process and save formatted data
            formatted_data = {
                'metadata': {
                    'source': 'Enova/SSB Energy Efficiency Data',
                    'fetched_at': datetime.now().isoformat(),
                    'description': 'Norwegian energy efficiency and renewable energy data'
                },
                'data': data
            }
            
            with open(raw_dir / 'enova_efficiency_formatted.json', 'w') as f:
                json.dump(formatted_data, f, indent=2)
            
            print("✅ Enova/Energy efficiency data fetched successfully")
            return True
        else:
            print("❌ Failed to fetch Enova/Energy efficiency data from all sources")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching Enova data: {e}")
        return False


def fetch_all_enova_data(years=None):
    """Legacy function for backward compatibility"""
    return fetch_enova_data()
