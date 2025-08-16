"""
Emissions analysis and forecasting for the GreenPulse project
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


class EmissionsAnalyzer:
    """Analyze greenhouse gas emissions trends and patterns"""
    
    def __init__(self, emissions_df: pd.DataFrame):
        """
        Initialize with emissions DataFrame
        
        Args:
            emissions_df: DataFrame with emissions data (from SSB)
        """
        self.df = emissions_df.copy()
        self.df['year'] = pd.to_numeric(self.df['year'])
        
    def calculate_trend_metrics(self) -> Dict[str, Any]:
        """
        Calculate key trend metrics
        
        Returns:
            Dictionary with trend analysis metrics
        """
        df = self.df.sort_values('year')
        
        # Basic metrics
        baseline_year = df.iloc[0]
        latest_year = df.iloc[-1]
        peak_emissions = df.loc[df['emissions_MtCO2e'].idxmax()]
        
        # Calculate changes
        total_change = latest_year['emissions_MtCO2e'] - baseline_year['emissions_MtCO2e']
        total_change_pct = (total_change / baseline_year['emissions_MtCO2e']) * 100
        
        # Recent trend (last 10 years)
        recent_df = df[df['year'] >= (latest_year['year'] - 10)]
        recent_change = recent_df.iloc[-1]['emissions_MtCO2e'] - recent_df.iloc[0]['emissions_MtCO2e']
        recent_change_pct = (recent_change / recent_df.iloc[0]['emissions_MtCO2e']) * 100
        
        # Average annual change
        years_span = latest_year['year'] - baseline_year['year']
        avg_annual_change = total_change / years_span
        avg_annual_change_pct = total_change_pct / years_span
        
        return {
            'baseline': {
                'year': int(baseline_year['year']),
                'emissions_mt': float(baseline_year['emissions_MtCO2e'])
            },
            'latest': {
                'year': int(latest_year['year']),
                'emissions_mt': float(latest_year['emissions_MtCO2e'])
            },
            'peak': {
                'year': int(peak_emissions['year']),
                'emissions_mt': float(peak_emissions['emissions_MtCO2e'])
            },
            'total_change': {
                'absolute_mt': float(total_change),
                'percentage': float(total_change_pct),
                'years_span': int(years_span)
            },
            'recent_trend': {
                'absolute_mt': float(recent_change),
                'percentage': float(recent_change_pct),
                'years': 10
            },
            'average_annual': {
                'absolute_mt': float(avg_annual_change),
                'percentage': float(avg_annual_change_pct)
            }
        }
    
    def simple_forecast(self, years_ahead: int = 5) -> pd.DataFrame:
        """
        Simple linear forecast based on recent trend
        
        Args:
            years_ahead: Number of years to forecast
            
        Returns:
            DataFrame with forecasted emissions
        """
        df = self.df.sort_values('year')
        
        # Use recent 10 years for trend calculation
        recent_df = df[df['year'] >= (df['year'].max() - 10)]
        
        # Linear regression on recent data
        x = recent_df['year'].values
        y = recent_df['emissions_MtCO2e'].values
        
        # Simple linear fit
        slope = np.polyfit(x, y, 1)[0]
        intercept = np.polyfit(x, y, 1)[1]
        
        # Generate forecast years
        last_year = df['year'].max()
        forecast_years = range(last_year + 1, last_year + years_ahead + 1)
        
        # Calculate forecasted emissions
        forecast_data = []
        for year in forecast_years:
            emissions = slope * year + intercept
            # Ensure emissions don't go negative
            emissions = max(0, emissions)
            
            forecast_data.append({
                'year': year,
                'emissions_MtCO2e': emissions,
                'type': 'forecast'
            })
        
        forecast_df = pd.DataFrame(forecast_data)
        
        # Add historical data for context
        historical_df = df[['year', 'emissions_MtCO2e']].copy()
        historical_df['type'] = 'historical'
        
        # Combine historical and forecast
        combined_df = pd.concat([historical_df, forecast_df], ignore_index=True)
        
        return combined_df
    
    def identify_patterns(self) -> Dict[str, Any]:
        """
        Identify patterns in emissions data
        
        Returns:
            Dictionary with pattern analysis
        """
        df = self.df.sort_values('year')
        
        # Year-over-year changes
        df['yoy_change'] = df['emissions_MtCO2e'].pct_change() * 100
        df['yoy_absolute'] = df['emissions_MtCO2e'].diff()
        
        # Volatility metrics
        volatility = df['yoy_change'].std()
        max_increase = df['yoy_change'].max()
        max_decrease = df['yoy_change'].min()
        
        # Find periods of consistent decline/increase
        consecutive_declines = 0
        consecutive_increases = 0
        current_decline_streak = 0
        current_increase_streak = 0
        
        for change in df['yoy_change'].dropna():
            if change < 0:
                current_decline_streak += 1
                current_increase_streak = 0
                consecutive_declines = max(consecutive_declines, current_decline_streak)
            elif change > 0:
                current_increase_streak += 1
                current_decline_streak = 0
                consecutive_increases = max(consecutive_increases, current_increase_streak)
        
        return {
            'volatility': {
                'std_deviation_pct': float(volatility),
                'max_annual_increase_pct': float(max_increase),
                'max_annual_decrease_pct': float(max_decrease)
            },
            'streaks': {
                'longest_decline_years': int(consecutive_declines),
                'longest_increase_years': int(consecutive_increases)
            },
            'recent_trend': {
                'last_5_years_avg_change': float(df['yoy_change'].tail(5).mean()),
                'is_declining': bool(df['yoy_change'].tail(3).mean() < 0)
            }
        }
    
    def generate_summary_report(self) -> str:
        """
        Generate a text summary of the emissions analysis
        
        Returns:
            Formatted string with analysis summary
        """
        metrics = self.calculate_trend_metrics()
        patterns = self.identify_patterns()
        
        report = f"""
# 🌍 Norway Emissions Analysis Report

## Key Metrics
- **Time Period**: {metrics['baseline']['year']} - {metrics['latest']['year']}
- **Baseline Emissions ({metrics['baseline']['year']})**: {metrics['baseline']['emissions_mt']:.1f} Mt CO2eq
- **Latest Emissions ({metrics['latest']['year']})**: {metrics['latest']['emissions_mt']:.1f} Mt CO2eq
- **Peak Emissions**: {metrics['peak']['emissions_mt']:.1f} Mt CO2eq in {metrics['peak']['year']}

## Overall Trend
- **Total Change**: {metrics['total_change']['percentage']:.1f}% ({metrics['total_change']['absolute_mt']:.1f} Mt CO2eq)
- **Average Annual Change**: {metrics['average_annual']['percentage']:.2f}% per year
- **Recent 10-Year Trend**: {metrics['recent_trend']['percentage']:.1f}%

## Pattern Analysis
- **Volatility**: {patterns['volatility']['std_deviation_pct']:.1f}% standard deviation
- **Longest Decline Period**: {patterns['streaks']['longest_decline_years']} consecutive years
- **Recent Trend**: {'Declining' if patterns['recent_trend']['is_declining'] else 'Stable/Increasing'}

## Assessment
"""
        
        # Add assessment based on trends
        if metrics['total_change']['percentage'] < -10:
            report += "✅ **Strong Progress**: Significant emissions reduction achieved.\n"
        elif metrics['total_change']['percentage'] < 0:
            report += "🟡 **Moderate Progress**: Some emissions reduction achieved.\n"
        else:
            report += "❌ **Limited Progress**: Emissions have increased overall.\n"
        
        if patterns['recent_trend']['is_declining']:
            report += "📉 **Recent Trend**: Positive - emissions are declining in recent years.\n"
        else:
            report += "📈 **Recent Trend**: Concerning - emissions stable or increasing recently.\n"
        
        return report


def analyze_emissions_data(csv_path: Path) -> Dict[str, Any]:
    """
    Convenience function to analyze emissions data from CSV
    
    Args:
        csv_path: Path to the emissions CSV file
        
    Returns:
        Complete analysis results
    """
    df = pd.read_csv(csv_path)
    analyzer = EmissionsAnalyzer(df)
    
    return {
        'metrics': analyzer.calculate_trend_metrics(),
        'patterns': analyzer.identify_patterns(),
        'forecast': analyzer.simple_forecast(),
        'summary_report': analyzer.generate_summary_report()
    }
