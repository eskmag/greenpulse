#!/usr/bin/env python3
"""
Add demo data to the GreenPulse database
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def add_demo_companies():
    """Add demo companies and users to the database"""
    from app import create_app, db
    from app.models import Company, User, UserRole
    
    app = create_app()
    with app.app_context():
        print("🏢 Adding demo companies to GreenPulse database...")
        
        # Company 1: Bergen Maritime AS
        company1 = Company(
            name="Bergen Maritime AS",
            org_number="123456789",
            industry_sector="Maritime",
            employee_count=150,
            headquarters_location="Bergen, Norway"
        )
        db.session.add(company1)
        db.session.flush()  # Get ID without committing
        
        # Users for Bergen Maritime
        user1 = User(
            email="admin@bergen-maritime.no",
            first_name="Lars",
            last_name="Hansen",
            role=UserRole.COMPANY_ADMIN,
            company_id=company1.id
        )
        user1.set_password("secure_password_123")
        db.session.add(user1)
        
        # Company 2: Oslo Tech Solutions
        company2 = Company(
            name="Oslo Tech Solutions",
            org_number="987654321", 
            industry_sector="Technology",
            employee_count=85,
            headquarters_location="Oslo, Norway"
        )
        db.session.add(company2)
        db.session.flush()
        
        # Users for Oslo Tech
        user2 = User(
            email="ceo@oslo-tech.no",
            first_name="Maria",
            last_name="Andersen",
            role=UserRole.COMPANY_ADMIN,
            company_id=company2.id
        )
        user2.set_password("tech_secure_456")
        db.session.add(user2)
        
        user3 = User(
            email="analyst@oslo-tech.no", 
            first_name="Erik",
            last_name="Olsen",
            role=UserRole.USER,
            company_id=company2.id
        )
        user3.set_password("analyst_pass_789")
        db.session.add(user3)
        
        # Company 3: Stavanger Manufacturing  
        company3 = Company(
            name="Stavanger Manufacturing",
            org_number="555666777",
            industry_sector="Manufacturing",
            employee_count=320,
            headquarters_location="Stavanger, Norway"
        )
        db.session.add(company3)
        db.session.flush()
        
        # Users for Stavanger Manufacturing
        user4 = User(
            email="director@stavanger-mfg.no",
            first_name="Ingrid",
            last_name="Nordahl", 
            role=UserRole.COMPANY_ADMIN,
            company_id=company3.id
        )
        user4.set_password("manufacturing_pass_101")
        db.session.add(user4)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Demo data added successfully!")
        print(f"   • {Company.query.count()} companies created")
        print(f"   • {User.query.count()} users created")
        
        # Show created data
        print("\n📊 Created companies:")
        for company in Company.query.all():
            print(f"   • {company.name} ({company.org_number}) - {company.employee_count} employees")
            
        print("\n👥 Created users:")
        for user in User.query.all():
            print(f"   • {user.first_name} {user.last_name} ({user.email}) - {user.role.value} at {user.company.name}")

if __name__ == '__main__':
    add_demo_companies()
