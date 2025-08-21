"""
Enova data source for energy efficiency and renewable energy data
"""
import requests
import pandas as pd
import json
from typing import Dict, Any, Optional
import os
from datetime import datetime, timedelta
from pathlib import Path
import random


class EnovaApiClient:
    """Client for fetching energy efficiency data with real SSB sources and demo data"""
    
    def __init__(self, api_key: Optional[str] = None, use_demo_data: bool = True):
        self.api_key = api_key or os.getenv('ENOVA_API_KEY')
        self.use_demo_data = use_demo_data
        
        # Real working endpoints for energy data
        self.base_urls = {
            # SSB energy efficiency and renewable energy tables
            'ssb_renewable': 'https://data.ssb.no/api/v0/no/table/12733',  # Renewable energy production
            'ssb_energy_use': 'https://data.ssb.no/api/v0/no/table/12351',  # Energy use by sector
            'ssb_energy_efficiency': 'https://data.ssb.no/api/v0/no/table/12717',  # Energy efficiency
        }
        
    def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            'User-Agent': 'GreenPulse-DataFetch/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def generate_demo_energy_efficiency_data(self) -> Dict[str, Any]:
        """
        Generate realistic demo data for energy efficiency metrics
        This simulates Enova-style energy efficiency and renewable energy data
        """
        current_year = datetime.now().year
        years = list(range(2020, current_year + 1))
        
        # Generate realistic energy efficiency data for Bergen region
        companies_data = []
        
        # Sample companies in Bergen region (various sectors)
        companies = [
            {"name": "Bergen Maritime Solutions AS", "sector": "Maritime", "employees": 150, "energy_baseline": 2500},
            {"name": "Havbruk Bergen AS", "sector": "Aquaculture", "employees": 80, "energy_baseline": 1800},
            {"name": "Vestland Industri AS", "sector": "Manufacturing", "employees": 200, "energy_baseline": 3200},
            {"name": "Bergen Logistikk AS", "sector": "Transport", "employees": 120, "energy_baseline": 2100},
            {"name": "Fjord Energy Solutions", "sector": "Energy", "employees": 90, "energy_baseline": 1600},
            {"name": "Bergen Fish Processing", "sector": "Food Processing", "employees": 160, "energy_baseline": 2800},
            {"name": "Kystservice Bergen AS", "sector": "Services", "employees": 75, "energy_baseline": 1200},
        ]
        
        for company in companies:
            company_data = {
                "company_info": company,
                "efficiency_projects": [],
                "annual_metrics": []
            }
            
            baseline_consumption = company["energy_baseline"]  # MWh/year
            cumulative_savings = 0
            
            for year in years:
                # Simulate energy efficiency improvements over time
                if year > 2020:
                    # Random efficiency project (some years have projects, some don't)
                    if random.random() < 0.6:  # 60% chance of efficiency project per year
                        project_savings = random.uniform(50, 300)  # MWh saved
                        cumulative_savings += project_savings
                        
                        project = {
                            "year": year,
                            "project_type": random.choice([
                                "LED lighting upgrade", 
                                "HVAC optimization", 
                                "Heat pump installation",
                                "Building insulation",
                                "Energy management system",
                                "Solar panel installation",
                                "Electric vehicle fleet"
                            ]),
                            "investment_nok": random.randint(200000, 2000000),
                            "annual_savings_mwh": round(project_savings, 1),
                            "co2_reduction_tonnes": round(project_savings * 0.12, 1),  # ~0.12 kg CO2/kWh
                            "enova_support_nok": random.randint(50000, 500000) if random.random() < 0.7 else 0
                        }
                        company_data["efficiency_projects"].append(project)
                
                # Annual energy metrics
                current_consumption = baseline_consumption - cumulative_savings + random.uniform(-50, 50)
                efficiency_improvement = (cumulative_savings / baseline_consumption) * 100
                
                annual_metric = {
                    "year": year,
                    "total_energy_consumption_mwh": round(max(current_consumption, baseline_consumption * 0.6), 1),
                    "efficiency_improvement_percent": round(efficiency_improvement, 2),
                    "cumulative_savings_mwh": round(cumulative_savings, 1),
                    "renewable_energy_share_percent": round(
                        min(random.uniform(20, 60) + (year - 2020) * 3, 85), 1
                    ),
                    "co2_emissions_tonnes": round(current_consumption * 0.12, 1)
                }
                company_data["annual_metrics"].append(annual_metric)
            
            companies_data.append(company_data)
        
        # Regional summary statistics
        regional_summary = {
            "region": "Bergen/Vestland",
            "total_companies": len(companies),
            "total_efficiency_projects": sum(len(c["efficiency_projects"]) for c in companies_data),
            "total_investment_nok": sum(
                sum(p["investment_nok"] for p in c["efficiency_projects"]) 
                for c in companies_data
            ),
            "total_energy_savings_mwh": sum(
                c["annual_metrics"][-1]["cumulative_savings_mwh"] 
                for c in companies_data if c["annual_metrics"]
            ),
            "total_co2_reduction_tonnes": sum(
                sum(p["co2_reduction_tonnes"] for p in c["efficiency_projects"]) 
                for c in companies_data
            ),
            "average_renewable_share": round(
                sum(c["annual_metrics"][-1]["renewable_energy_share_percent"] 
                    for c in companies_data if c["annual_metrics"]) / len(companies_data), 1
            )
        }
        
        return {
            "metadata": {
                "source": "Demo Energy Efficiency Data (Enova-style)",
                "region": "Bergen/Vestland, Norway",
                "generated_at": datetime.now().isoformat(),
                "data_type": "energy_efficiency_demo",
                "years_covered": years,
                "description": "Simulated energy efficiency and renewable energy data for Bergen region companies"
            },
            "regional_summary": regional_summary,
            "companies": companies_data
        }
    
    def fetch_energy_efficiency_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch energy efficiency data from real SSB sources or generate demo data
        """
        if self.use_demo_data:
            print("🎭 Using demo energy efficiency data (Enova-style)")
            return self.generate_demo_energy_efficiency_data()
        
        # Try to fetch real renewable energy data from SSB
        try:
            return self._fetch_ssb_renewable_energy_data()
        except Exception as e:
            print(f"Failed to fetch real data, falling back to demo: {e}")
            return self.generate_demo_energy_efficiency_data()
    
    def _fetch_ssb_renewable_energy_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch renewable energy production data from SSB
        """
        try:
            # SSB renewable energy production table
            query = {
                "query": [
                    {
                        "code": "Energikilde",
                        "selection": {
                            "filter": "item",
                            "values": ["0", "1", "2", "3", "4"]  # Different renewable sources
                        }
                    },
                    {
                        "code": "Tid",
                        "selection": {
                            "filter": "top",
                            "values": 5  # Last 5 years
                        }
                    }
                ],
                "response": {
                    "format": "json-stat2"
                }
            }
            
            response = requests.post(
                self.base_urls['ssb_renewable'],
                json=query,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Successfully fetched renewable energy data from SSB")
                data = response.json()
                
                # Add our metadata
                return {
                    "metadata": {
                        "source": "SSB Renewable Energy Production",
                        "fetched_at": datetime.now().isoformat(),
                        "table": "12733",
                        "description": "Norwegian renewable energy production statistics"
                    },
                    "data": data
                }
            else:
                print(f"SSB renewable energy fetch failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching SSB renewable energy data: {e}")
            return None


class EnovaDataProcessor:
    """Process and format Enova/energy efficiency data"""
    
    @staticmethod
    def to_efficiency_summary(data: Dict[str, Any]) -> pd.DataFrame:
        """Convert energy efficiency data to summary DataFrame"""
        if not data or "companies" not in data:
            return pd.DataFrame()
        
        summaries = []
        for company in data["companies"]:
            company_info = company["company_info"]
            latest_metrics = company["annual_metrics"][-1] if company["annual_metrics"] else {}
            
            summary = {
                "company_name": company_info["name"],
                "sector": company_info["sector"],
                "employees": company_info["employees"],
                "total_projects": len(company["efficiency_projects"]),
                "total_investment_nok": sum(p["investment_nok"] for p in company["efficiency_projects"]),
                "energy_savings_mwh": latest_metrics.get("cumulative_savings_mwh", 0),
                "efficiency_improvement_percent": latest_metrics.get("efficiency_improvement_percent", 0),
                "renewable_share_percent": latest_metrics.get("renewable_energy_share_percent", 0),
                "co2_emissions_tonnes": latest_metrics.get("co2_emissions_tonnes", 0),
                "year": latest_metrics.get("year", datetime.now().year)
            }
            summaries.append(summary)
        
        return pd.DataFrame(summaries)
    
    @staticmethod
    def to_projects_df(data: Dict[str, Any]) -> pd.DataFrame:
        """Convert efficiency projects to DataFrame"""
        if not data or "companies" not in data:
            return pd.DataFrame()
        
        projects = []
        for company in data["companies"]:
            company_name = company["company_info"]["name"]
            company_sector = company["company_info"]["sector"]
            
            for project in company["efficiency_projects"]:
                project_data = project.copy()
                project_data["company_name"] = company_name
                project_data["company_sector"] = company_sector
                projects.append(project_data)
        
        return pd.DataFrame(projects)


def fetch_enova_data() -> bool:
    """
    Main function to fetch Enova/energy efficiency data
    Returns True if successful, False otherwise
    """
    try:
        # Use demo data by default for reliable results
        client = EnovaApiClient(use_demo_data=True)
        data = client.fetch_energy_efficiency_data()
        
        if data:
            # Save raw data
            raw_dir = Path(__file__).resolve().parents[3] / "data/raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            with open(raw_dir / 'enova_efficiency.json', 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Process and save formatted data for easier access
            processed_dir = Path(__file__).resolve().parents[3] / "data/processed"
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Save company efficiency summary
            efficiency_df = EnovaDataProcessor.to_efficiency_summary(data)
            if not efficiency_df.empty:
                efficiency_df.to_csv(processed_dir / 'company_efficiency_summary.csv', index=False)
                print(f"📊 Saved efficiency data for {len(efficiency_df)} companies")
            
            # Save projects data
            projects_df = EnovaDataProcessor.to_projects_df(data)
            if not projects_df.empty:
                projects_df.to_csv(processed_dir / 'efficiency_projects.csv', index=False)
                print(f"🔧 Saved {len(projects_df)} efficiency projects")
            
            print("✅ Enova/Energy efficiency data fetched and processed successfully")
            return True
        else:
            print("❌ Failed to fetch Enova/Energy efficiency data")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching Enova data: {e}")
        return False


def fetch_all_enova_data(years=None):
    """Legacy function for backward compatibility"""
    return fetch_enova_data()


if __name__ == "__main__":
    # Test the module
    success = fetch_enova_data()
    if success:
        print("\n📈 Energy Efficiency Data Summary:")
        
        # Load and display summary
        processed_dir = Path(__file__).resolve().parents[3] / "data/processed"
        
        if (processed_dir / 'company_efficiency_summary.csv').exists():
            df = pd.read_csv(processed_dir / 'company_efficiency_summary.csv')
            print(f"Companies analyzed: {len(df)}")
            print(f"Total energy savings: {df['energy_savings_mwh'].sum():.1f} MWh")
            print(f"Average efficiency improvement: {df['efficiency_improvement_percent'].mean():.1f}%")
            print(f"Average renewable share: {df['renewable_share_percent'].mean():.1f}%")
            print("\nTop efficiency performers:")
            print(df.nlargest(3, 'efficiency_improvement_percent')[['company_name', 'sector', 'efficiency_improvement_percent']])
    else:
        print("Failed to fetch energy efficiency data")
