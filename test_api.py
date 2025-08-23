#!/usr/bin/env python3
"""
Test the Flask API endpoints
"""
import requests
import json
import time

def test_api():
    base_url = "http://127.0.0.1:5002"
    
    print("🧪 Testing GreenPulse API...")
    
    try:
        # Test main endpoint
        print("\n1️⃣ Testing main endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test companies endpoint
        print("\n2️⃣ Testing companies endpoint...")
        response = requests.get(f"{base_url}/api/companies")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total']} companies")
            for company in data['companies']:
                print(f"  • {company['name']} ({company['industry_sector']})")
        
        # Test users endpoint
        print("\n3️⃣ Testing users endpoint...")
        response = requests.get(f"{base_url}/api/users")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total']} users")
            for user in data['users']:
                print(f"  • {user['first_name']} {user['last_name']} ({user['email']}) - {user['role']} at {user['company_name']}")
        
        # Test login
        print("\n4️⃣ Testing login...")
        login_data = {
            "email": "admin@bergen-maritime.no",
            "password": "secure_password_123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Login successful for: {data['user']['first_name']} {data['user']['last_name']}")
            print(f"Company: {data['user']['company_name']}")
            print(f"Role: {data['user']['role']}")
        
        # Test creating a new company
        print("\n5️⃣ Testing company creation...")
        new_company = {
            "name": "Trondheim Innovation AS",
            "org_number": "888999000",
            "industry_sector": "Technology",
            "employee_count": 45,
            "headquarters_location": "Trondheim, Norway"
        }
        response = requests.post(f"{base_url}/api/companies", json=new_company)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"Created company: {data['company']['name']}")
            company_id = data['company']['id']
            
            # Test creating a user for the new company
            print("\n6️⃣ Testing user creation...")
            new_user = {
                "email": "ceo@trondheim-innovation.no",
                "password": "innovation_2024",
                "first_name": "Kari",
                "last_name": "Olsen",
                "company_id": company_id,
                "role": "company_admin"
            }
            response = requests.post(f"{base_url}/api/users", json=new_user)
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                data = response.json()
                print(f"Created user: {data['user']['first_name']} {data['user']['last_name']}")
        
        print("\n✅ API testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure Flask app is running on port 5002")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_api()
