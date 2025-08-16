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
    
    return ssb_emissions, elhub_data


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


def show_summary_stats(ssb_df, elhub_df):
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
        if elhub_df is not None and not elhub_df.empty:
            total_consumption = elhub_df['quantity_kwh'].sum()
            st.metric(
                "Total Energy Data",
                f"{total_consumption:,.0f} kWh",
                f"{len(elhub_df)} records"
            )
    
    with col4:
        if elhub_df is not None and not elhub_df.empty:
            unique_areas = elhub_df['price_area'].nunique()
            st.metric(
                "Price Areas",
                f"{unique_areas}",
                "Monitored"
            )


def main():
    """Main dashboard function"""
    st.set_page_config(
        page_title="GreenPulse Dashboard",
        page_icon="🌱",
        layout="wide"
    )
    
    st.title("🌱 GreenPulse Sustainability Dashboard")
    st.markdown("*Visualizing Norway's emissions and energy data for ESG reporting*")
    
    # Load data
    with st.spinner("Loading data..."):
        ssb_emissions, elhub_data = load_data()
    
    # Show summary statistics
    st.subheader("📊 Key Metrics")
    show_summary_stats(ssb_emissions, elhub_data)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🌍 Emissions", "⚡ Energy Consumption", "📈 Combined Analysis"])
    
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
        st.subheader("Combined Analysis")
        
        if ssb_emissions is not None and elhub_data is not None and not elhub_data.empty:
            st.markdown("### 🔄 Data Integration Opportunities")
            st.markdown("""
            This tab would show correlations between emissions and energy consumption:
            - Energy consumption vs emissions intensity
            - Regional analysis combining price areas with emissions
            - Time series analysis of efficiency improvements
            - ESG reporting metrics
            """)
            
            # Placeholder for future analysis
            st.info("🚧 Advanced analysis features coming soon!")
            
        else:
            st.warning("⚠️ Combined analysis requires both emissions and energy data.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Data Sources**: 
    - Statistics Norway (SSB) for emissions data
    - Elhub for energy consumption data
    
    **Last Updated**: {timestamp}
    """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")))


if __name__ == "__main__":
    main()
