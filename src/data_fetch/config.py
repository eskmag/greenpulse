"""
Configuration management for data fetching APIs
"""
import os
from typing import Optional


class DataFetchConfig:
    """Configuration for data fetching APIs"""
    
    def __init__(self):
        self.ssb_api_key = os.getenv('SSB_API_KEY')
        self.elhub_api_key = os.getenv('ELHUB_API_KEY')
        self.enova_api_key = os.getenv('ENOVA_API_KEY')
        
    @property
    def has_ssb_auth(self) -> bool:
        return self.ssb_api_key is not None
        
    @property
    def has_elhub_auth(self) -> bool:
        return self.elhub_api_key is not None
        
    @property 
    def has_enova_auth(self) -> bool:
        return self.enova_api_key is not None
        
    def get_api_endpoints(self) -> dict:
        """Get available API endpoints based on authentication"""
        return {
            'ssb': {
                'base_url': 'https://data.ssb.no/api/v0/no/table',
                'requires_auth': False,
                'available': True,
                'description': f'Statistics Norway - Always available{" (with API key)" if self.has_ssb_auth else ""}'
            },
            'elhub': {
                'base_url': 'https://api.elhub.no',
                'requires_auth': True,
                'available': self.has_elhub_auth,
                'description': 'Elhub Energy Data - Requires API key'
            },
            'enova': {
                'base_url': 'https://www.enova.no/api/v1',
                'requires_auth': True,
                'available': self.has_enova_auth,
                'description': 'Enova Energy Efficiency - Requires API key'
            }
        }
    
    def print_status(self):
        """Print the status of all API endpoints"""
        print("🔧 API Configuration Status:")
        endpoints = self.get_api_endpoints()
        
        for name, config in endpoints.items():
            status = "✅ Available" if config['available'] else "❌ Not available"
            auth_info = "(Auth required)" if config['requires_auth'] else "(No auth)"
            print(f"  {name.upper()}: {status} {auth_info} - {config['description']}")


# Global config instance
config = DataFetchConfig()
