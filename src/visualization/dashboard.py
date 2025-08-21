"""
Streamlit dashboard for GreenPulse sustainability data
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add the project root to the path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_fetch.sources.ssb import SSBDataProcessor
from src.data_fetch.sources.elhub import ElhubDataProcessor


def load_data():
    """Load all available data"""
    data_dir = project_root / "data"
    
    # Load SSB emissions data
    ssb_emissions = None
    ssb_path = data_dir / "processed" / "ssb_emissions_clean.csv"
    if ssb_path.exists():
        ssb_emissions = pd.read_csv(ssb_path)
    
    # Load Elhub energy data
    elhub_data = None
    elhub_path = data_dir / "raw" / "elhub_energy_formatted.json"
    if elhub_path.exists():
        with open(elhub_path, 'r') as f:
            elhub_raw = json.load(f)
        elhub_data = ElhubDataProcessor.to_consumption_summary(elhub_raw)
    
    # Load Enova efficiency data
    enova_companies = None
    enova_projects = None
    
    companies_path = data_dir / "processed" / "company_efficiency_summary.csv"
    if companies_path.exists():
        enova_companies = pd.read_csv(companies_path)
    
    projects_path = data_dir / "processed" / "efficiency_projects.csv"
    if projects_path.exists():
        enova_projects = pd.read_csv(projects_path)
    
    return ssb_emissions, elhub_data, enova_companies, enova_projects


def plot_emissions_trend(df):
    """Create emissions trend plot"""
    fig = px.line(
        df, 
        x='year', 
        y='emissions_MtCO2e',
        title='🌍 Norway Greenhouse Gas Emissions Trend (1990-2024)',
        labels={
            'emissions_MtCO2e': 'Emissions (Million tonnes CO2 eq)',
            'year': 'Year'
        }
    )
    
    # Add annotations for key points
    peak_year = df.loc[df['emissions_MtCO2e'].idxmax()]
    latest_year = df.iloc[-1]
    
    fig.add_annotation(
        x=peak_year['year'], y=peak_year['emissions_MtCO2e'],
        text=f"Peak: {peak_year['emissions_MtCO2e']:.1f} Mt<br>({peak_year['year']})",
        showarrow=True, arrowhead=2, arrowcolor="red"
    )
    
    fig.add_annotation(
        x=latest_year['year'], y=latest_year['emissions_MtCO2e'],
        text=f"Latest: {latest_year['emissions_MtCO2e']:.1f} Mt<br>({latest_year['year']})",
        showarrow=True, arrowhead=2, arrowcolor="green"
    )
    
    fig.update_layout(hovermode='x unified')
    return fig


def plot_energy_consumption(df):
    """Create energy consumption visualizations"""
    if df.empty:
        return None
    
    # Daily summary
    daily_df = ElhubDataProcessor.get_daily_summary(df)
    
    if daily_df.empty:
        return None
    
    # Group by price area and consumption group
    fig = px.bar(
        daily_df.groupby(['price_area', 'consumption_group'])['quantity_kwh'].sum().reset_index(),
        x='price_area',
        y='quantity_kwh', 
        color='consumption_group',
        title='⚡ Energy Consumption by Price Area and Group',
        labels={
            'quantity_kwh': 'Energy Consumption (kWh)',
            'price_area': 'Price Area'
        }
    )
    
    return fig


def plot_hourly_consumption(df):
    """Create hourly consumption pattern"""
    if df.empty:
        return None
    
    # Average consumption by hour
    hourly_avg = df.groupby('hour')['quantity_kwh'].mean().reset_index()
    
    fig = px.line(
        hourly_avg,
        x='hour',
        y='quantity_kwh',
        title='🕐 Average Hourly Energy Consumption Pattern',
        labels={
            'quantity_kwh': 'Average Consumption (kWh)',
            'hour': 'Hour of Day'
        }
    )
    
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))
    return fig


def plot_company_efficiency(companies_df):
    """Create company efficiency visualization"""
    if companies_df is None or companies_df.empty:
        return None
    
    fig = px.scatter(
        companies_df,
        x='efficiency_improvement_percent',
        y='energy_savings_mwh',
        size='total_investment_nok',
        color='sector',
        hover_data=['company_name', 'employees', 'renewable_share_percent'],
        title='🏭 Company Energy Efficiency Performance',
        labels={
            'efficiency_improvement_percent': 'Efficiency Improvement (%)',
            'energy_savings_mwh': 'Energy Savings (MWh)',
            'total_investment_nok': 'Investment (NOK)'
        }
    )
    
    fig.update_layout(
        xaxis_title="Efficiency Improvement (%)",
        yaxis_title="Energy Savings (MWh)",
        showlegend=True
    )
    
    return fig


def plot_efficiency_projects(projects_df):
    """Create efficiency projects timeline"""
    if projects_df is None or projects_df.empty:
        return None
    
    # Aggregate by year and project type
    yearly_projects = projects_df.groupby(['year', 'project_type']).agg({
        'investment_nok': 'sum',
        'annual_savings_mwh': 'sum',
        'co2_reduction_tonnes': 'sum'
    }).reset_index()
    
    fig = px.bar(
        yearly_projects,
        x='year',
        y='investment_nok',
        color='project_type',
        title='💰 Energy Efficiency Investments by Year and Type',
        labels={
            'investment_nok': 'Investment (NOK)',
            'year': 'Year',
            'project_type': 'Project Type'
        }
    )
    
    return fig


def plot_renewable_energy_share(companies_df):
    """Create renewable energy share visualization"""
    if companies_df is None or companies_df.empty:
        return None
    
    fig = px.box(
        companies_df,
        x='sector',
        y='renewable_share_percent',
        title='♻️ Renewable Energy Share by Sector',
        labels={
            'renewable_share_percent': 'Renewable Energy Share (%)',
            'sector': 'Industry Sector'
        }
    )
    
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def show_summary_stats(ssb_df, elhub_df, enova_companies, enova_projects):
    """Show summary statistics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if ssb_df is not None:
            latest_emissions = ssb_df.iloc[-1]['emissions_MtCO2e']
            st.metric(
                "Latest Emissions",
                f"{latest_emissions:.1f} Mt CO2eq",
                f"{ssb_df.iloc[-1]['year']}"
            )
    
    with col2:
        if ssb_df is not None:
            change = ((ssb_df.iloc[-1]['emissions_MtCO2e'] - ssb_df.iloc[0]['emissions_MtCO2e']) 
                     / ssb_df.iloc[0]['emissions_MtCO2e'] * 100)
            st.metric(
                "Change Since 1990",
                f"{change:.1f}%",
                "Reduction" if change < 0 else "Increase"
            )
    
    with col3:
        if enova_companies is not None and not enova_companies.empty:
            total_savings = enova_companies['energy_savings_mwh'].sum()
            st.metric(
                "Total Energy Savings",
                f"{total_savings:,.0f} MWh",
                f"{len(enova_companies)} companies"
            )
    
    with col4:
        if enova_companies is not None and not enova_companies.empty:
            avg_renewable = enova_companies['renewable_share_percent'].mean()
            st.metric(
                "Avg Renewable Share",
                f"{avg_renewable:.1f}%",
                "Bergen region"
            )


def main():
    """Main dashboard function"""
    st.set_page_config(
        page_title="GreenPulse Dashboard",
        page_icon="🌱",
        layout="wide"
    )
    
    st.title("🌱 GreenPulse Sustainability Dashboard")
    st.markdown("*Visualizing Norway's emissions, energy data, and company efficiency for ESG reporting*")
    
    # Load data
    with st.spinner("Loading data..."):
        ssb_emissions, elhub_data, enova_companies, enova_projects = load_data()
    
    # Show summary statistics
    st.subheader("📊 Key Metrics")
    show_summary_stats(ssb_emissions, elhub_data, enova_companies, enova_projects)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🌍 Emissions", "⚡ Energy Consumption", "🏭 Company Efficiency", "📊 ESG Reports"])
    
    with tab1:
        st.subheader("Greenhouse Gas Emissions")
        
        if ssb_emissions is not None:
            # Show the trend
            fig_emissions = plot_emissions_trend(ssb_emissions)
            st.plotly_chart(fig_emissions, use_container_width=True)
            
            # Show data table
            with st.expander("📋 View Emissions Data"):
                st.dataframe(ssb_emissions)
                
            # Summary insights
            st.markdown("### 🔍 Key Insights")
            peak_year = ssb_emissions.loc[ssb_emissions['emissions_MtCO2e'].idxmax()]
            latest_year = ssb_emissions.iloc[-1]
            change = ((latest_year['emissions_MtCO2e'] - ssb_emissions.iloc[0]['emissions_MtCO2e']) 
                     / ssb_emissions.iloc[0]['emissions_MtCO2e'] * 100)
            
            st.markdown(f"""
            - **Peak emissions**: {peak_year['emissions_MtCO2e']:.1f} Mt CO2eq in {peak_year['year']}
            - **Latest emissions**: {latest_year['emissions_MtCO2e']:.1f} Mt CO2eq in {latest_year['year']}
            - **Overall change**: {change:.1f}% since 1990
            - **Data source**: Statistics Norway (SSB)
            """)
        else:
            st.error("❌ No emissions data available. Run the data fetch script first.")
    
    with tab2:
        st.subheader("Energy Consumption")
        
        if elhub_data is not None and not elhub_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_consumption = plot_energy_consumption(elhub_data)
                if fig_consumption:
                    st.plotly_chart(fig_consumption, use_container_width=True)
            
            with col2:
                fig_hourly = plot_hourly_consumption(elhub_data)
                if fig_hourly:
                    st.plotly_chart(fig_hourly, use_container_width=True)
            
            # Show data summary
            with st.expander("📋 View Energy Data Summary"):
                daily_summary = ElhubDataProcessor.get_daily_summary(elhub_data)
                if not daily_summary.empty:
                    st.dataframe(daily_summary)
                else:
                    st.dataframe(elhub_data.head(20))
            
            # Energy insights
            st.markdown("### ⚡ Energy Insights")
            total_consumption = elhub_data['quantity_kwh'].sum()
            avg_hourly = elhub_data['quantity_kwh'].mean()
            peak_hour = elhub_data.groupby('hour')['quantity_kwh'].mean().idxmax()
            
            st.markdown(f"""
            - **Total consumption tracked**: {total_consumption:,.0f} kWh
            - **Average hourly consumption**: {avg_hourly:,.0f} kWh
            - **Peak consumption hour**: {peak_hour}:00
            - **Data source**: Elhub Energy Data API
            """)
        else:
            st.error("❌ No energy consumption data available. Run the data fetch script first.")
    
    with tab3:
        st.subheader("Company Energy Efficiency")
        
        if enova_companies is not None and not enova_companies.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_efficiency = plot_company_efficiency(enova_companies)
                if fig_efficiency:
                    st.plotly_chart(fig_efficiency, use_container_width=True)
            
            with col2:
                fig_renewable = plot_renewable_energy_share(enova_companies)
                if fig_renewable:
                    st.plotly_chart(fig_renewable, use_container_width=True)
            
            # Investment analysis
            if enova_projects is not None and not enova_projects.empty:
                fig_projects = plot_efficiency_projects(enova_projects)
                if fig_projects:
                    st.plotly_chart(fig_projects, use_container_width=True)
            
            # Company selector and details
            st.markdown("### 🏢 Company Details")
            selected_company = st.selectbox(
                "Select a company for detailed analysis:",
                enova_companies['company_name'].tolist()
            )
            
            if selected_company:
                company_data = enova_companies[enova_companies['company_name'] == selected_company].iloc[0]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Sector", company_data['sector'])
                with col2:
                    st.metric("Employees", f"{company_data['employees']}")
                with col3:
                    st.metric("Efficiency Improvement", f"{company_data['efficiency_improvement_percent']:.1f}%")
                with col4:
                    st.metric("Renewable Share", f"{company_data['renewable_share_percent']:.1f}%")
                
                # Show company projects
                if enova_projects is not None:
                    company_projects = enova_projects[enova_projects['company_name'] == selected_company]
                    if not company_projects.empty:
                        st.markdown("#### 🔧 Efficiency Projects")
                        st.dataframe(company_projects[['year', 'project_type', 'investment_nok', 'annual_savings_mwh', 'co2_reduction_tonnes']])
            
            # Efficiency insights
            st.markdown("### 🎯 Efficiency Insights")
            total_investment = enova_companies['total_investment_nok'].sum()
            total_savings = enova_companies['energy_savings_mwh'].sum()
            avg_efficiency = enova_companies['efficiency_improvement_percent'].mean()
            
            st.markdown(f"""
            - **Total efficiency investments**: {total_investment:,.0f} NOK
            - **Total energy savings**: {total_savings:,.0f} MWh
            - **Average efficiency improvement**: {avg_efficiency:.1f}%
            - **Companies tracked**: {len(enova_companies)} in Bergen region
            - **Data source**: Demo Energy Efficiency Data (Enova-style)
            """)
        else:
            st.error("❌ No company efficiency data available. Run the data fetch script first.")
    
    with tab4:
        st.subheader("ESG Reports & Export")
        
        # ESG Summary
        st.markdown("### 📈 ESG Summary Dashboard")
        
        if all(data is not None for data in [ssb_emissions, enova_companies]):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Environmental Metrics")
                latest_emissions = ssb_emissions.iloc[-1]['emissions_MtCO2e']
                total_co2_reduction = enova_companies['energy_savings_mwh'].sum() * 0.12  # Approx kg CO2/kWh
                
                st.metric("National Emissions", f"{latest_emissions:.1f} Mt CO2eq")
                st.metric("Company CO2 Reductions", f"{total_co2_reduction:,.0f} tonnes")
                st.metric("Avg Renewable Share", f"{enova_companies['renewable_share_percent'].mean():.1f}%")
            
            with col2:
                st.markdown("#### Social & Governance")
                total_employees = enova_companies['employees'].sum()
                companies_tracked = len(enova_companies)
                sectors = enova_companies['sector'].nunique()
                
                st.metric("Employees Covered", f"{total_employees:,}")
                st.metric("Companies Tracked", f"{companies_tracked}")
                st.metric("Sectors Covered", f"{sectors}")
        
        # Export functionality
        st.markdown("### 📄 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("� Download Company Data"):
                if enova_companies is not None:
                    csv = enova_companies.to_csv(index=False)
                    st.download_button(
                        "💾 company_efficiency_data.csv",
                        csv,
                        "company_efficiency_data.csv",
                        "text/csv"
                    )
        
        with col2:
            if st.button("🔧 Download Projects Data"):
                if enova_projects is not None:
                    csv = enova_projects.to_csv(index=False)
                    st.download_button(
                        "💾 efficiency_projects.csv",
                        csv,
                        "efficiency_projects.csv", 
                        "text/csv"
                    )
        
        with col3:
            if st.button("🌍 Download Emissions Data"):
                if ssb_emissions is not None:
                    csv = ssb_emissions.to_csv(index=False)
                    st.download_button(
                        "💾 norway_emissions.csv",
                        csv,
                        "norway_emissions.csv",
                        "text/csv"
                    )
        
        st.markdown("### 📋 ESG Reporting Standards")
        st.markdown("""
        This dashboard provides data aligned with major ESG frameworks:
        - **GRI Standards**: Environmental performance indicators
        - **EU Taxonomy**: Climate change mitigation metrics  
        - **TCFD**: Climate-related financial disclosures
        - **SASB**: Sustainability accounting standards
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Data Sources**: 
    - Statistics Norway (SSB) for national emissions data
    - Elhub for energy consumption data
    - Demo energy efficiency data for Bergen region companies
    
    **Last Updated**: {timestamp}
    """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")))


if __name__ == "__main__":
    main()
