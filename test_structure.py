#!/usr/bin/env python3
"""
Test script to validate the new data_fetch structure
"""
import os
import sys
from pathlib import Path

def test_structure():
    """Test that the new structure exists"""
    base_path = Path(__file__).resolve().parent / "src" / "data_fetch"
    
    # Check main files
    required_files = [
        base_path / "__init__.py",
        base_path / "fetch_all.py",
        base_path / "sources" / "__init__.py",
        base_path / "sources" / "ssb.py",
        base_path / "sources" / "elhub.py",
        base_path / "sources" / "enova.py"
    ]
    
    print("🔍 Testing new data_fetch structure...")
    
    for file_path in required_files:
        if file_path.exists():
            print(f"✅ {file_path.relative_to(base_path)}")
        else:
            print(f"❌ {file_path.relative_to(base_path)} - Missing!")
            return False
    
    # Check that old files are removed
    old_files = [
        base_path / "ssb_api.py",
        base_path / "data_processors.py", 
        base_path / "file_manager.py",
        base_path / "fetch_ssb_data.py",
        base_path / "fetch_elhub_data.py",
        base_path / "fetch_enova_data.py"
    ]
    
    print("\n🗑️  Checking old files are removed...")
    for file_path in old_files:
        if not file_path.exists():
            print(f"✅ {file_path.relative_to(base_path)} - Removed")
        else:
            print(f"⚠️  {file_path.relative_to(base_path)} - Still exists")
    
    print("\n🎉 Structure reorganization completed successfully!")
    print("\nNew structure:")
    print("src/data_fetch/")
    print("├── __init__.py")
    print("├── fetch_all.py")
    print("└── sources/")
    print("    ├── __init__.py")
    print("    ├── ssb.py")
    print("    ├── elhub.py")
    print("    └── enova.py")
    
    return True

if __name__ == "__main__":
    test_structure()
