"""
GreenPulse - ESG data analysis and reporting platform

A sustainability and ESG reporting prototype that collects and analyzes data
from Norwegian sources to support climate and energy transition reporting.
"""

__version__ = "0.1.0"
__author__ = "GreenPulse Team"

from pathlib import Path
import sys

# Project root path
PROJECT_ROOT = Path(__file__).resolve().parent

def setup_project_path():
    """Add project root to Python path if not already present"""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

# Auto-setup path when importing
setup_project_path()
