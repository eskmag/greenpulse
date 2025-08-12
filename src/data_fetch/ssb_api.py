"""
SSB API client for fetching emissions data
"""
import requests
import json
from typing import Dict, Any


class SSBApiClient:
    """Client for Statistics Norway (SSB) API"""
    
    def __init__(self, base_url: str = "https://data.ssb.no/api/v0/en/table"):
        self.base_url = base_url
    
    def fetch_emissions_data(self, table_id: str = "08940") -> Dict[str, Any]:
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
        
        response = requests.post(url, json=query)
        
        if response.status_code == 200:
            return json.loads(response.content.decode("utf-8"))
        else:
            raise requests.RequestException(
                f"Failed to fetch data: {response.status_code} - {response.text}"
            )
