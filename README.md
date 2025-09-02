# 🌱 GreenPulse

**A comprehensive sustainability and ESG platform with data analytics and web application**

GreenPulse is a full-stack## 📊 Current Data & Platform Status

### Analytics Platform Insights
Based on the latest analysis of Norwegian emissions (updated August 2025):

- **📉 12.3% reduction** in emissions since 1990 (51.4 → 45.0 Mt CO2eq)
- **🎯 Peak emissions** were 56.5 Mt CO2eq in 2007
- **📊 Recent trend** shows consistent decline over the last 10 years (-16.5%)
- **🔮 Forecast** suggests continued decline to ~41.7 Mt CO2eq by 2029
- **⚡ Energy patterns** show peak consumption during winter months
- **🌍 Regional variations** in energy consumption across Norwegian price areas

### Web Application Status
- **🏢 Demo Companies**: 3 sample companies (Bergen Maritime AS, Oslo Tech Solutions AS, Stavanger Energy AS)
- **👥 Demo Users**: 4 test users across different roles (admin, company admin, users)
- **🔐 Authentication**: Fully functional login system with role-based access
- **💾 Database**: PostgreSQL integration with automatic table creation
- **🌐 API**: All CRUD endpoints working and testedility platform that combines ESG data analysis with a modern web application. The project explores how informatics and open data can support sustainability reporting by collecting data from Norwegian sources like SSB, Elhub, and Enova. It features both an analytical dashboard for data insights and a web application for ESG company management.

## 🎯 Features

### ✅ Web Application (Phase 1 MVP)
- **🏢 Company Management**: Create and manage sustainability-focused companies
- **👥 User Management**: Role-based access with admin, company admin, user, and viewer roles
- **🔐 Authentication**: Secure login system with password hashing
- **📊 Database Integration**: PostgreSQL backend with SQLAlchemy ORM
- **🌐 REST API**: Full CRUD operations via JSON API endpoints
- **💾 Demo Data**: Pre-populated sample companies and users for testing

### ✅ Data Analytics Platform
- **📊 Emissions Data**: Norwegian greenhouse gas emissions (1990-2024) from Statistics Norway (SSB)
- **⚡ Energy Data**: Real-time energy consumption data from Elhub API
- **📈 Analytics**: Trend analysis, forecasting, and pattern recognition
- **🌐 Dashboard**: Interactive Streamlit dashboard with visualizations
- **🔄 Data Pipeline**: Automated data fetching and processing

### 🚧 In Development
- **🔋 Enova Integration**: Energy efficiency data (API endpoints need research)
- **🎨 Enhanced Visualizations**: More chart types and insights
- **📊 ESG Reporting**: Standardized sustainability metrics for companies
- **🌍 Regional Analysis**: Price area and municipality-level insights
- **🔗 Integration**: Connect analytics platform with web application

## 🚀 Quick Start

### 1. Setup
```bash
# Clone the repository
git clone <repository-url>
cd greenpulse

# Install dependencies (creates virtual environment automatically)
pip install -r requirements.txt

# Set up PostgreSQL database (required for web app)
createdb greenpulse_dev

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your database URL and API keys if available
```

### 2. Web Application
```bash
# Start the Flask web application
python3 run.py
# Visit http://127.0.0.1:5002 to access the API

# Test the API
python3 tests/test_api.py

# Add demo data (companies and users)
python3 scripts/add_demo_data.py

# Run Phase 1 MVP demo
python3 scripts/phase1_demo.py
```

### 3. Data Analytics Platform
```bash
# Fetch all available data
python3 main.py fetch

# Run emissions analysis only
python3 main.py analyze

# Run comprehensive ESG analysis
python3 main.py comprehensive

# Launch interactive dashboard
python3 main.py dashboard

# Complete workflow
python3 main.py fetch && python3 main.py comprehensive && python3 main.py dashboard
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
├── webapp.py                # 🌐 Flask web application (main entry point)
├── main.py                  # 📊 Unified CLI for data analytics
├── add_demo_data.py         # 💾 Script to populate demo companies/users
├── test_api.py              # 🧪 API testing suite
├── phase1_demo.py           # 🚀 Phase 1 MVP demo script
├── requirements.txt         # 📦 Python dependencies
├── __init__.py             # 📋 Package initialization
├── src/
│   ├── data_fetch/          # 🔄 Data collection modules
│   │   ├── sources/         # 🏪 API clients for each data source
│   │   │   ├── ssb.py      # 📈 Statistics Norway API
│   │   │   ├── elhub.py    # ⚡ Elhub energy data API  
│   │   │   └── enova.py    # 🔋 Enova efficiency API
│   │   ├── fetch_all.py    # 🎯 Main data orchestrator
│   │   └── config.py       # ⚙️ API configuration
│   ├── analysis/           # 🔬 Data analysis modules
│   │   └── emissions_analysis.py  # 📉 Trend analysis & forecasting
│   └── visualization/      # 📊 Dashboard and charts
│       └── dashboard.py    # 🎨 Streamlit dashboard
├── data/
│   ├── raw/               # 📥 Raw API responses
│   └── processed/         # 🔧 Clean, analysis-ready data
└── README.md              # 📖 This file
```

## 🏗️ Architecture

### Web Application (Flask)
- **Backend**: Flask 2.3+ with SQLAlchemy ORM
- **Database**: PostgreSQL with automatic table creation
- **Models**: Company and User entities with role-based access
- **API**: RESTful endpoints for all CRUD operations
- **Security**: Password hashing with Werkzeug

### Analytics Platform (CLI + Streamlit)
- **Data Sources**: Multiple Norwegian sustainability APIs
- **Processing**: Pandas-based data transformation pipeline
- **Analysis**: Statistical analysis with trend forecasting
- **Visualization**: Interactive Streamlit dashboard
- **Export**: Multiple formats (JSON, CSV, analysis reports)

## � Current Data Insights

Based on the latest analysis of Norwegian emissions (updated August 2025):

- **📉 12.3% reduction** in emissions since 1990 (51.4 → 45.0 Mt CO2eq)
- **🎯 Peak emissions** were 56.5 Mt CO2eq in 2007
- **📊 Recent trend** shows consistent decline over the last 10 years (-16.5%)
- **🔮 Forecast** suggests continued decline to ~41.7 Mt CO2eq by 2029
- **⚡ Energy patterns** show peak consumption during winter months
- **🌍 Regional variations** in energy consumption across Norwegian price areas

## 🛠️ Technical Details

### Web Application APIs
- **Companies**: `GET/POST /api/companies` - Manage sustainability companies
- **Users**: `GET/POST /api/users` - User management with role-based access
- **Authentication**: `POST /api/auth/login` - Secure login system
- **Health**: `GET /health` - Application and database status
- **Demo Data**: `POST /api/demo/reset` - Reset sample data for testing

### Data Source APIs
- **SSB API**: `https://data.ssb.no/api/v0/en/table/{table_id}`
- **Elhub API**: `https://api.elhub.no/energy-data/v0/{entity}?dataset={dataset}`

### Database Schema
```sql
-- Companies table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    org_number VARCHAR(20) UNIQUE NOT NULL,
    industry_sector VARCHAR(100),
    employee_count INTEGER,
    headquarters_location VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users table with role-based access
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    company_id INTEGER REFERENCES companies(id),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Data Processing Pipeline
- **Raw JSON** → **Formatted JSON** → **Analysis-ready CSV**
- Automatic data validation and error handling
- Multiple export formats for different use cases

### Dependencies
- **Web**: `Flask`, `SQLAlchemy`, `Flask-Migrate`, `psycopg2`
- **Data**: `pandas`, `requests`, `numpy`
- **Visualization**: `streamlit`, `plotly`, `matplotlib`, `seaborn`
- **Analysis**: `scikit-learn`, `statsmodels`
- **Environment**: `python-dotenv`

## 🎨 Dashboard Features

The interactive Streamlit dashboard includes:

- **📊 Emissions Trends**: Historical emissions with peak/latest annotations and trend lines
- **⚡ Energy Consumption**: Real-time energy data by price areas and consumption groups
- **🕐 Hourly Patterns**: Average consumption patterns throughout the day
- **📈 Forecasting**: Linear projections and advanced time series models
- **📋 Data Tables**: Raw data exploration with filtering and export options
- **🔍 Comparative Analysis**: Year-over-year comparisons and seasonal adjustments

## 🔧 Development Roadmap

### Phase 1: Foundation ✅
- [x] SSB emissions data integration
- [x] Elhub energy data integration  
- [x] Basic data processing pipeline
- [x] Interactive dashboard
- [x] Flask web application with PostgreSQL
- [x] Company and user management
- [x] Role-based authentication system
- [x] REST API with full CRUD operations

### Phase 2: Integration & Analytics 🚧
- [x] Emissions trend analysis
- [x] Simple forecasting models
- [ ] Connect web app with analytics platform
- [ ] ESG reporting for companies
- [ ] Regional analysis by price areas
- [ ] Advanced user permissions and company data isolation
- [ ] Fix Enova API integration

### Phase 3: Enhanced Features 📋
- [ ] Advanced forecasting models (ARIMA, Prophet)
- [ ] Company-specific ESG dashboards
- [ ] Automated sustainability reporting
- [ ] Export capabilities (PDF reports)
- [ ] Email notifications and alerts
- [ ] Web deployment with cloud hosting
- [ ] Mobile-responsive frontend interface

## 🎨 Dashboard Features

### Analytics Dashboard (Streamlit)
- **📊 Emissions Trends**: Historical emissions with peak/latest annotations and trend lines
- **⚡ Energy Consumption**: Real-time energy data by price areas and consumption groups
- **🕐 Hourly Patterns**: Average consumption patterns throughout the day
- **📈 Forecasting**: Linear projections and advanced time series models
- **📋 Data Tables**: Raw data exploration with filtering and export options
- **🔍 Comparative Analysis**: Year-over-year comparisons and seasonal adjustments

### Web Application Features
- **🏢 Company Portal**: Manage company sustainability profiles
- **👥 User Management**: Role-based access control (Admin, Company Admin, User, Viewer)
- **📊 Health Monitoring**: Real-time application and database status
- **💾 Demo Environment**: Pre-populated test data for development
- **🔐 Secure Authentication**: Password hashing and session management

## 🤝 Contributing

### Web Application Development
1. **Backend Features**: Enhance Flask API with new endpoints and functionality
2. **Frontend Development**: Create a modern web interface (React/Vue.js recommended)
3. **Database Optimization**: Improve queries and add new data models
4. **Security**: Implement JWT tokens, enhanced authentication, and authorization

### Data Analytics Enhancement
1. **Data Sources**: Help identify and integrate additional Norwegian sustainability data sources
2. **Visualizations**: Enhance the dashboard with new chart types and insights
3. **Machine Learning**: Implement advanced analytics and predictive models
4. **Integration**: Connect analytics platform with web application data

### General Improvements
1. **Documentation**: Improve setup guides, API documentation, and usage examples
2. **Testing**: Add comprehensive unit tests and integration tests
3. **DevOps**: Set up CI/CD pipeline and deployment automation
4. **Performance**: Optimize database queries and application performance

## 🚦 Getting Started for Developers

1. **Fork the repository** and clone your fork
2. **Set up PostgreSQL** database locally
3. **Install dependencies** with `pip install -r requirements.txt`
4. **Run tests** with `python test_api.py` (after starting webapp)
5. **Add sample data** with `python add_demo_data.py`
6. **Start development** on your feature branch

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Last Updated**: August 23, 2025 | **Status**: Active Development | **Current Phase**: Web application MVP completed, integrating with analytics platform