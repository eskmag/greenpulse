#!/usr/bin/env python3
"""
Database viewer for GreenPulse
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from webapp import app, db, Company, User, UserRole

def view_database():
    """View all data in the GreenPulse database"""
    print("🗄️  GreenPulse Database Viewer")
    print("="*50)
    
    with app.app_context():
        try:
            # Show table info
            print(f"\n📊 Database Statistics:")
            print(f"   • Companies: {Company.query.count()}")
            print(f"   • Users: {User.query.count()}")
            
            # Show all companies
            print(f"\n🏢 Companies:")
            print("-" * 30)
            companies = Company.query.all()
            for company in companies:
                print(f"   ID: {company.id}")
                print(f"   Name: {company.name}")
                print(f"   Org Number: {company.org_number}")
                print(f"   Industry: {company.industry_sector}")
                print(f"   Employees: {company.employee_count}")
                print(f"   Location: {company.headquarters_location}")
                print(f"   Created: {company.created_at}")
                print()
            
            # Show all users
            print(f"👥 Users:")
            print("-" * 30)
            users = User.query.all()
            for user in users:
                print(f"   ID: {user.id}")
                print(f"   Name: {user.first_name} {user.last_name}")
                print(f"   Email: {user.email}")
                print(f"   Role: {user.role.value}")
                print(f"   Company: {user.company.name}")
                print(f"   Active: {user.is_active}")
                print(f"   Created: {user.created_at}")
                print(f"   Last Login: {user.last_login}")
                print()
                
            # Show relationships
            print(f"🔗 Company-User Relationships:")
            print("-" * 30)
            for company in companies:
                company_users = User.query.filter_by(company_id=company.id).all()
                print(f"   {company.name} ({len(company_users)} users):")
                for user in company_users:
                    print(f"      • {user.first_name} {user.last_name} ({user.role.value})")
                print()
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    view_database()
