#!/usr/bin/env python3
"""
GreenPulse Web Application Entry Point
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app, db


def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")


if __name__ == '__main__':
    app = create_app()
    
    # Create tables if they don't exist
    create_tables()
    
    # Run the application
    print("🚀 Starting GreenPulse web application...")
    print("📊 API available at: http://127.0.0.1:5003")
    print("💾 Database: PostgreSQL")
    print("🔧 Environment: Development")
    
    app.run(
        host='127.0.0.1',
        port=5003,
        debug=True
    )
