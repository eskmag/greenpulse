# 📁 GreenPulse Project Organization

## 🚀 Quick Start Commands

```bash
# Web Application
.venv/bin/python run.py                    # Start the Flask web application
# OR using the helper script:
scripts/run_with_venv.sh run.py           # Start with virtual environment

# Data Analytics
.venv/bin/python main.py fetch             # Fetch data from all sources
.venv/bin/python main.py analyze           # Run emissions analysis
.venv/bin/python main.py comprehensive     # Run full ESG analysis
.venv/bin/python main.py dashboard         # Launch interactive dashboard

# Utilities & Scripts
.venv/bin/python scripts/add_demo_data.py  # Add demo companies and users
.venv/bin/python scripts/phase1_demo.py   # Run Phase 1 MVP demonstration
.venv/bin/python scripts/view_database.py # Browse database interactively

# Testing
.venv/bin/python tests/test_api.py         # Test API endpoints
```

## 📂 Project Structure

```
greenpulse/
├── 📱 Web Application
│   ├── run.py                   # Main application entry point
│   ├── config.py                # Configuration settings
│   └── app/                     # Flask application package
│       ├── __init__.py          # Application factory
│       ├── models.py            # Database models
│       ├── routes.py            # Main routes
│       ├── extensions.py        # Flask extensions
│       └── api/                 # API endpoints
│           ├── auth.py          # Authentication
│           ├── companies.py     # Company management
│           ├── users.py         # User management
│           └── reports.py       # ESG reporting
│
├── 📊 Data Analytics Platform
│   ├── main.py                  # Main CLI interface
│   └── src/                     # Source code
│       ├── analysis/            # Data analysis modules
│       │   └── emissions_analysis.py
│       ├── data_fetch/          # Data collection
│       │   ├── fetch_all.py
│       │   ├── config.py
│       │   └── sources/         # Data source APIs
│       │       ├── ssb.py       # Statistics Norway
│       │       ├── elhub.py     # Energy Hub
│       │       └── enova.py     # Enova (efficiency)
│       └── visualization/       # Dashboards & charts
│           └── dashboard.py     # Streamlit dashboard
│
├── 🛠 Scripts & Utilities
│   ├── scripts/
│   │   ├── add_demo_data.py     # Database demo data
│   │   ├── phase1_demo.py       # MVP demonstration
│   │   └── view_database.py     # Database browser
│   └── tests/
│       └── test_api.py          # API tests
│
├── 📊 Data & Reports
│   ├── data/                    # Data storage
│   │   ├── raw/                 # Original data files
│   │   ├── processed/           # Cleaned data
│   │   └── examples/            # Sample data
│   ├── reports/                 # Generated reports
│   │   └── esg_analysis_report.txt
│   └── docs/                    # Documentation
│       └── README_PHASE1.md     # Phase 1 documentation
│
└── 📋 Configuration
    ├── requirements.txt         # Python dependencies
    ├── .env.template           # Environment variables template
    ├── .gitignore              # Git ignore rules
    └── LICENSE                 # License file
```

## 🔧 Development Workflow

### 1. Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your settings

# Setup database
createdb greenpulse_dev
```

### 2. Web Application Development
```bash
# Start development server
python run.py

# Add demo data
python scripts/add_demo_data.py

# Test API endpoints
python tests/test_api.py
```

### 3. Data Analytics Development
```bash
# Fetch latest data
python main.py fetch

# Run analysis
python main.py comprehensive

# Launch dashboard
python main.py dashboard
```

## 🏗 Architecture Benefits

### 🎯 Separation of Concerns
- **Web Application**: Clean Flask app with modular blueprints
- **Data Analytics**: Independent analysis pipeline
- **Scripts**: Utility functions separated from core logic
- **Configuration**: Centralized settings management

### 📦 Modular Design
- **API Blueprints**: Separate endpoints for different functionalities
- **Database Models**: Clean ORM with relationship management
- **Data Sources**: Individual modules for each data provider
- **Analysis**: Focused modules for specific analysis types

### 🔧 Maintainability
- **Clear Entry Points**: Specific scripts for different purposes
- **Organized Dependencies**: Requirements clearly defined
- **Documentation**: Inline and separate documentation files
- **Testing**: Dedicated test directory structure

### 🚀 Scalability
- **Application Factory**: Flask app can be configured for different environments
- **Blueprint Architecture**: Easy to add new API endpoints
- **Modular Data Pipeline**: New data sources can be added easily
- **Configuration Management**: Environment-specific settings

## 📈 Development Roadmap

### Phase 2: Enhanced Integration
- [ ] Connect web app with analytics platform
- [ ] Real-time data updates in web interface
- [ ] Company-specific analytics dashboards
- [ ] Enhanced API endpoints for analytics

### Phase 3: Production Deployment
- [ ] Docker containerization
- [ ] Cloud deployment configuration
- [ ] Production database setup
- [ ] CI/CD pipeline implementation

## 🤝 Contributing

1. Follow the established directory structure
2. Add new API endpoints as blueprints in `app/api/`
3. Create new data sources in `src/data_fetch/sources/`
4. Add utility scripts to `scripts/` directory
5. Place tests in appropriate `tests/` subdirectories
6. Update documentation when adding new features
