#!/usr/bin/env python3
"""
Launch script for the GreenPulse dashboard
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit dashboard"""
    # Get the path to the dashboard
    dashboard_path = Path(__file__).parent / "src" / "visualization" / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard not found at {dashboard_path}")
        return 1
    
    # Launch Streamlit
    try:
        print("🚀 Launching GreenPulse Dashboard...")
        print("🌐 Dashboard will open in your browser at http://localhost:8501")
        print("📝 To stop the dashboard, press Ctrl+C")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
