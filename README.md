# 🌱 GreenPulse

**A sustainability and ESG reporting prototype dashboard**

This project explores how informatics and open data can support sustainability and ESG reporting. By collecting and analyzing data from sources like SSB, Elhub, and Enova, it builds a prototype dashboard that visualizes emissions, energy use, and climate measures. The goal is to learn the industry, connect technology with green transition challenges, and demonstrate how data can be transformed into actionable insights.

## 🎯 Features

### ✅ Currently Working
- **📊 Emissions Data**: Norwegian greenhouse gas emissions (1990-2024) from Statistics Norway (SSB)
- **⚡ Energy Data**: Real-time energy consumption data from Elhub API
- **📈 Analytics**: Trend analysis, forecasting, and pattern recognition
- **🌐 Dashboard**: Interactive Streamlit dashboard with visualizations
- **🔄 Data Pipeline**: Automated data fetching and processing

### 🚧 In Development
- **🔋 Enova Integration**: Energy efficiency data (API endpoints need research)
- **🎨 Enhanced Visualizations**: More chart types and insights
- **📊 ESG Reporting**: Standardized sustainability metrics
- **🌍 Regional Analysis**: Price area and municipality-level insights

## 🚀 Quick Start

### 1. Setup
```bash
# Clone the repository
git clone <repository-url>
cd greenpulse

# Install dependencies (creates virtual environment automatically)
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your API keys if available
```

### 2. Fetch Data
```bash
# Fetch all available data
python src/data_fetch/fetch_all.py
```

### 3. Run Analysis
```bash
# Generate emissions analysis report
python run_analysis.py
```

### 4. Launch Dashboard
```bash
# Start the interactive dashboard
python run_dashboard.py
# Or directly: streamlit run src/visualization/dashboard.py
```

## 📊 Data Sources

| Source | Status | Description | API Key Required |
|--------|--------|-------------|------------------|
| **SSB (Statistics Norway)** | ✅ Working | Greenhouse gas emissions data | No (optional) |
| **Elhub** | ✅ Working | Energy consumption by price areas | No (public endpoints) |
| **Enova** | ❌ Needs Fix | Energy efficiency data | Yes (endpoints TBD) |

## 📁 Project Structure

```
greenpulse/
├── src/
│   ├── data_fetch/          # Data collection modules
│   │   ├── sources/         # API clients for each data source
│   │   │   ├── ssb.py      # Statistics Norway API
│   │   │   ├── elhub.py    # Elhub energy data API  
│   │   │   └── enova.py    # Enova efficiency API
│   │   ├── fetch_all.py    # Main data orchestrator
│   │   └── config.py       # API configuration
│   ├── analysis/           # Data analysis modules
│   │   └── emissions_analysis.py  # Trend analysis & forecasting
│   └── visualization/      # Dashboard and charts
│       └── dashboard.py    # Streamlit dashboard
├── data/
│   ├── raw/               # Raw API responses
│   └── processed/         # Clean, analysis-ready data
├── notebooks/            # Jupyter notebooks (planned)
├── run_analysis.py       # Analysis runner script
├── run_dashboard.py      # Dashboard launcher
└── requirements.txt      # Dependencies
```

## 📈 Current Data Insights

Based on the latest analysis of Norwegian emissions:

- **📉 12.3% reduction** in emissions since 1990 (51.4 → 45.0 Mt CO2eq)
- **🎯 Peak emissions** were 56.5 Mt CO2eq in 2007
- **📊 Recent trend** shows consistent decline over the last 10 years (-16.5%)
- **🔮 Forecast** suggests continued decline to ~41.7 Mt CO2eq by 2029

## 🛠️ Technical Details

### APIs Used
- **SSB API**: `https://data.ssb.no/api/v0/en/table/{table_id}`
- **Elhub API**: `https://api.elhub.no/energy-data/v0/{entity}?dataset={dataset}`

### Data Processing
- **Raw JSON** → **Formatted JSON** → **Analysis-ready CSV**
- Automatic data validation and error handling
- Multiple export formats for different use cases

### Dependencies
- **Data**: `pandas`, `requests`, `numpy`
- **Visualization**: `streamlit`, `plotly`, `matplotlib`, `seaborn`
- **Environment**: `python-dotenv`

## 🎨 Dashboard Features

The interactive dashboard includes:

- **📊 Emissions Trends**: Historical emissions with peak/latest annotations
- **⚡ Energy Consumption**: Real-time energy data by price areas and consumption groups
- **🕐 Hourly Patterns**: Average consumption patterns throughout the day
- **📈 Forecasting**: Simple linear projections based on recent trends
- **📋 Data Tables**: Raw data exploration with filtering

## 🔧 Development Roadmap

### Phase 1: Foundation ✅
- [x] SSB emissions data integration
- [x] Elhub energy data integration  
- [x] Basic data processing pipeline
- [x] Interactive dashboard

### Phase 2: Analysis 🚧
- [x] Emissions trend analysis
- [x] Simple forecasting
- [ ] Energy efficiency metrics
- [ ] Regional analysis by price areas
- [ ] Correlation analysis between emissions and energy

### Phase 3: Enhanced Features 📋
- [ ] Fix Enova API integration
- [ ] Advanced forecasting models
- [ ] ESG reporting templates
- [ ] Export capabilities (PDF reports)
- [ ] Automated data updates
- [ ] Web deployment

## 🤝 Contributing

1. **Data Sources**: Help identify and integrate additional Norwegian sustainability data sources
2. **Visualizations**: Enhance the dashboard with new chart types and insights
3. **Analysis**: Implement advanced analytics and machine learning models
4. **Documentation**: Improve setup guides and usage examples

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Last Updated**: August 2025 | **Status**: Active Development | **Next**: Fix Enova API integration