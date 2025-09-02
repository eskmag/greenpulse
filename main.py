#!/usr/bin/env python3
"""
GreenPulse - Unified CLI for ESG data analysis and reporting
"""
import argparse
import sys
import subprocess
from pathlib import Path
import pandas as pd
import os

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.analysis.emissions_analysis import analyze_emissions_data


def fetch_data():
    """Fetch all data from available sources"""
    print("🔄 Fetching data from all sources...")
    fetch_script = project_root / "src" / "data_fetch" / "fetch_all.py"
    
    try:
        result = subprocess.run([
            sys.executable, str(fetch_script)
        ], cwd=project_root, check=True)
        print("✅ Data fetch completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Data fetch failed: {e}")
        return 1


def run_analysis():
    """Run emissions analysis only"""
    print("📊 Running emissions analysis...")
    
    data_path = project_root / "data" / "processed" / "ssb_emissions_clean.csv"
    
    if not data_path.exists():
        print(f"❌ Emissions data not found at {data_path}")
        print("🔄 Run 'python main.py fetch' first")
        return 1
    
    try:
        results = analyze_emissions_data(data_path)
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


def analyze_company_efficiency(companies_path, projects_path):
    """Analyze company efficiency data"""
    if not companies_path.exists() or not projects_path.exists():
        return None
    
    companies_df = pd.read_csv(companies_path)
    projects_df = pd.read_csv(projects_path)
    
    # Company efficiency summary
    total_companies = len(companies_df)
    total_investment = companies_df['total_investment_nok'].sum()
    total_savings = companies_df['energy_savings_mwh'].sum()
    avg_efficiency = companies_df['efficiency_improvement_percent'].mean()
    avg_renewable = companies_df['renewable_share_percent'].mean()
    
    # Projects summary
    total_projects = len(projects_df)
    total_co2_reduction = projects_df['co2_reduction_tonnes'].sum()
    
    # Top performers
    top_efficiency = companies_df.nlargest(3, 'efficiency_improvement_percent')
    top_renewable = companies_df.nlargest(3, 'renewable_share_percent')
    
    return {
        'summary': {
            'total_companies': total_companies,
            'total_investment_nok': total_investment,
            'total_energy_savings_mwh': total_savings,
            'avg_efficiency_improvement': avg_efficiency,
            'avg_renewable_share': avg_renewable,
            'total_projects': total_projects,
            'total_co2_reduction_tonnes': total_co2_reduction
        },
        'top_efficiency': top_efficiency,
        'top_renewable': top_renewable,
        'companies_df': companies_df,
        'projects_df': projects_df
    }


def generate_esg_report(emissions_results, efficiency_results):
    """Generate comprehensive ESG report"""
    report = []
    
    report.append("# 🌱 GreenPulse ESG Analysis Report")
    report.append("=" * 50)
    report.append("")
    
    # Environmental Metrics
    report.append("## 🌍 Environmental Performance")
    
    if emissions_results:
        emissions_data = emissions_results['metrics']
        report.append(f"### National Emissions Context (Norway)")
        report.append(f"- Latest emissions: {emissions_data['latest']['emissions_mt']:.1f} Mt CO2eq")
        report.append(f"- Change since 1990: {emissions_data['total_change']['percentage']:.1f}%")
        report.append(f"- Recent trend (10yr): {emissions_data['recent_trend']['percentage']:.1f}%")
        report.append("")
    
    if efficiency_results:
        eff_data = efficiency_results['summary']
        report.append(f"### Bergen Region Company Performance")
        report.append(f"- Companies analyzed: {eff_data['total_companies']}")
        report.append(f"- Total energy savings: {eff_data['total_energy_savings_mwh']:,.0f} MWh")
        report.append(f"- Average efficiency improvement: {eff_data['avg_efficiency_improvement']:.1f}%")
        report.append(f"- Average renewable energy share: {eff_data['avg_renewable_share']:.1f}%")
        report.append(f"- Total CO2 reduction: {eff_data['total_co2_reduction_tonnes']:,.0f} tonnes")
        report.append("")
    
    # Social & Governance
    report.append("## 👥 Social & Governance Metrics")
    if efficiency_results:
        companies_df = efficiency_results['companies_df']
        total_employees = companies_df['employees'].sum()
        sectors = companies_df['sector'].nunique()
        
        report.append(f"- Total employees covered: {total_employees:,}")
        report.append(f"- Industry sectors represented: {sectors}")
        report.append(f"- Investment in efficiency: {eff_data['total_investment_nok']:,.0f} NOK")
        report.append("")
    
    # Top Performers
    if efficiency_results:
        report.append("## 🏆 Top Performing Companies")
        
        report.append("### Energy Efficiency Leaders:")
        for _, company in efficiency_results['top_efficiency'].head(3).iterrows():
            report.append(f"- **{company['company_name']}** ({company['sector']}): {company['efficiency_improvement_percent']:.1f}% improvement")
        
        report.append("")
        report.append("### Renewable Energy Leaders:")
        for _, company in efficiency_results['top_renewable'].head(3).iterrows():
            report.append(f"- **{company['company_name']}** ({company['sector']}): {company['renewable_share_percent']:.1f}% renewable")
        
        report.append("")
    
    # ESG Framework Alignment
    report.append("## 📋 ESG Framework Alignment")
    report.append("This analysis provides metrics aligned with:")
    report.append("- **GRI Standards**: Energy consumption, emissions, efficiency")
    report.append("- **EU Taxonomy**: Climate change mitigation activities")
    report.append("- **TCFD**: Climate-related risks and opportunities")
    report.append("- **SASB**: Industry-specific sustainability metrics")
    report.append("")
    
    # Recommendations
    report.append("## 🎯 Key Recommendations")
    if efficiency_results:
        avg_eff = efficiency_results['summary']['avg_efficiency_improvement']
        avg_renewable = efficiency_results['summary']['avg_renewable_share']
        
        if avg_eff < 25:
            report.append("- Consider accelerating energy efficiency programs")
        if avg_renewable < 70:
            report.append("- Increase renewable energy adoption across sectors")
        
        report.append("- Continue investment in proven technologies (heat pumps, LED, solar)")
        report.append("- Expand efficiency programs to more companies")
        report.append("- Develop sector-specific efficiency benchmarks")
    
    return "\n".join(report)


def run_comprehensive_analysis():
    """Run comprehensive ESG analysis"""
    print("🚀 Starting comprehensive ESG analysis...")
    
    data_dir = project_root / "data" / "processed"
    
    # Analyze emissions data
    emissions_results = None
    emissions_path = data_dir / "ssb_emissions_clean.csv"
    if emissions_path.exists():
        print("📊 Analyzing national emissions data...")
        emissions_results = analyze_emissions_data(emissions_path)
    else:
        print("⚠️ No emissions data found")
    
    # Analyze company efficiency data
    efficiency_results = None
    companies_path = data_dir / "company_efficiency_summary.csv"
    projects_path = data_dir / "efficiency_projects.csv"
    
    if companies_path.exists() and projects_path.exists():
        print("🏭 Analyzing company efficiency data...")
        efficiency_results = analyze_company_efficiency(companies_path, projects_path)
    else:
        print("⚠️ No company efficiency data found")
    
    # Generate comprehensive report
    if emissions_results or efficiency_results:
        print("📝 Generating ESG report...")
        esg_report = generate_esg_report(emissions_results, efficiency_results)
        print("\n" + esg_report)
        
        # Save report to file
        report_path = project_root / "reports" / "esg_analysis_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(esg_report)
        
        print(f"\n💾 Report saved to: {report_path}")
    else:
        print("❌ No data available for analysis. Run data fetch first:")
        print("   python main.py fetch")
        return 1
    
    print("\n✅ Comprehensive ESG analysis complete!")
    return 0


def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching GreenPulse Dashboard...")
    
    dashboard_path = project_root / "src" / "visualization" / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard not found at {dashboard_path}")
        return 1
    
    try:
        print("🌐 Dashboard will open in your browser at http://localhost:8501")
        print("📝 To stop the dashboard, press Ctrl+C")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GreenPulse - ESG data analysis and reporting platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py fetch                    # Fetch all data sources
  python main.py analyze                  # Run emissions analysis only
  python main.py comprehensive            # Run full ESG analysis
  python main.py dashboard                # Launch interactive dashboard
  
  # Complete workflow:
  python main.py fetch && python main.py comprehensive && python main.py dashboard
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fetch command
    subparsers.add_parser('fetch', help='Fetch data from all available sources')
    
    # Analysis commands
    subparsers.add_parser('analyze', help='Run emissions trend analysis')
    subparsers.add_parser('comprehensive', help='Run comprehensive ESG analysis')
    
    # Dashboard command
    subparsers.add_parser('dashboard', help='Launch interactive dashboard')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute the requested command
    if args.command == 'fetch':
        return fetch_data()
    elif args.command == 'analyze':
        return run_analysis()
    elif args.command == 'comprehensive':
        return run_comprehensive_analysis()
    elif args.command == 'dashboard':
        return launch_dashboard()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
