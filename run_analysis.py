#!/usr/bin/env python3
"""
Run emissions analysis and generate report
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.analysis.emissions_analysis import analyze_emissions_data


def main():
    """Run the emissions analysis"""
    # Path to the processed emissions data
    data_path = project_root / "data" / "processed" / "ssb_emissions_clean.csv"
    
    if not data_path.exists():
        print(f"❌ Emissions data not found at {data_path}")
        print("🔄 Run the data fetch script first: python src/data_fetch/fetch_all.py")
        return 1
    
    print("📊 Analyzing Norwegian emissions data...")
    
    try:
        # Run the analysis
        results = analyze_emissions_data(data_path)
        
        # Print the summary report
        print(results['summary_report'])
        
        # Show forecast
        forecast_df = results['forecast']
        future_data = forecast_df[forecast_df['type'] == 'forecast']
        
        if not future_data.empty:
            print("\n## 🔮 5-Year Forecast")
            for _, row in future_data.iterrows():
                print(f"- **{int(row['year'])}**: {row['emissions_MtCO2e']:.1f} Mt CO2eq")
        
        print(f"\n✅ Analysis complete! Data spans {len(forecast_df[forecast_df['type'] == 'historical'])} years")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
