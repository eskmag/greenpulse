#!/usr/bin/env python3
"""
Verify the project structure reorganization
"""
from pathlib import Path
import sys

def verify_structure():
    """Check that all expected files are in their correct locations"""
    project_root = Path(__file__).resolve().parent.parent
    
    print("🔍 Verifying GreenPulse project structure...")
    print(f"📁 Project root: {project_root}")
    print()
    
    # Check main directories
    directories = {
        'app': 'Flask web application',
        'src': 'Data analytics platform', 
        'scripts': 'Utility scripts',
        'tests': 'Test files',
        'data': 'Data storage',
        'reports': 'Generated reports',
        'docs': 'Documentation'
    }
    
    print("📂 Directory Structure:")
    for dir_name, description in directories.items():
        dir_path = project_root / dir_name
        status = "✅" if dir_path.exists() else "❌"
        print(f"  {status} {dir_name:<12} - {description}")
    
    print()
    
    # Check key files
    files = {
        'run.py': 'Web application entry point',
        'main.py': 'Analytics CLI interface',
        'config.py': 'Configuration settings',
        'requirements.txt': 'Python dependencies',
        'app/__init__.py': 'Flask application factory',
        'scripts/add_demo_data.py': 'Demo data script',
        'tests/test_api.py': 'API tests',
        'docs/PROJECT_STRUCTURE.md': 'Structure documentation'
    }
    
    print("📄 Key Files:")
    for file_path, description in files.items():
        full_path = project_root / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"  {status} {file_path:<25} - {description}")
    
    print()
    
    # Check for old files that should be removed/moved
    old_files = [
        'webapp.py',
        'phase1_demo.py', 
        'add_demo_data.py',
        'test_api.py',
        'esg_analysis_report.txt',
        'README_PHASE1.md'
    ]
    
    cleanup_needed = []
    for old_file in old_files:
        if (project_root / old_file).exists():
            cleanup_needed.append(old_file)
    
    if cleanup_needed:
        print("🧹 Files that should be cleaned up:")
        for file in cleanup_needed:
            print(f"  ⚠️  {file} (should be moved/removed)")
    else:
        print("🧹 Cleanup: All old files properly moved/removed")
    
    print()
    print("✅ Project structure verification complete!")
    print("📖 See docs/PROJECT_STRUCTURE.md for detailed information")

if __name__ == '__main__':
    verify_structure()
