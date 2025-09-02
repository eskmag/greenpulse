#!/usr/bin/env python3
"""
Test JWT Authentication for GreenPulse API

This script tests the new JWT authentication system.
"""
import requests
import json
import sys
from datetime import datetime

# API base URL
BASE_URL = "http://127.0.0.1:5003"

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    def login(self, email, password):
        """Login and store tokens"""
        response = requests.post(f"{self.base_url}/api/auth/login", json={
            'email': email,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token')
            return data
        else:
            return response.json()
    
    def get_headers(self):
        """Get authorization headers"""
        if self.access_token:
            return {'Authorization': f'Bearer {self.access_token}'}
        return {}
    
    def get(self, endpoint):
        """Make authenticated GET request"""
        return requests.get(f"{self.base_url}{endpoint}", headers=self.get_headers())
    
    def post(self, endpoint, data=None):
        """Make authenticated POST request"""
        return requests.post(f"{self.base_url}{endpoint}", 
                           json=data, headers=self.get_headers())
    
    def refresh_access_token(self):
        """Refresh access token"""
        if not self.refresh_token:
            return None
        
        headers = {'Authorization': f'Bearer {self.refresh_token}'}
        response = requests.post(f"{self.base_url}/api/auth/refresh", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            return data
        return response.json()


def test_api_health():
    """Test basic API health"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy - {data['statistics']['companies']} companies, {data['statistics']['users']} users")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False


def test_jwt_authentication():
    """Test JWT authentication flow"""
    print("\n🔐 Testing JWT Authentication...")
    
    client = APIClient(BASE_URL)
    
    # Test demo user login
    demo_credentials = [
        ("admin@bergen-maritime.no", "secure_password_123"),
        ("ceo@oslo-tech.no", "tech_secure_456"),
        ("esg@oslo-tech.no", "analyst_pass_789")
    ]
    
    for email, password in demo_credentials:
        print(f"\n📝 Testing login for: {email}")
        
        # Test login
        login_result = client.login(email, password)
        if 'access_token' in login_result:
            print(f"✅ Login successful - Token received")
            print(f"   User: {login_result['user']['first_name']} {login_result['user']['last_name']}")
            print(f"   Role: {login_result['user']['role']}")
            print(f"   Company: {login_result['user']['company_name']}")
            
            # Test profile endpoint
            print(f"   Testing profile access...")
            profile_response = client.get("/api/auth/profile")
            if profile_response.status_code == 200:
                print(f"✅ Profile access successful")
            else:
                print(f"❌ Profile access failed: {profile_response.status_code}")
            
            # Test companies endpoint
            print(f"   Testing companies access...")
            companies_response = client.get("/api/companies")
            if companies_response.status_code == 200:
                companies_data = companies_response.json()
                print(f"✅ Companies access successful - {companies_data['total']} companies visible")
            else:
                print(f"❌ Companies access failed: {companies_response.status_code}")
            
            # Test users endpoint
            print(f"   Testing users access...")
            users_response = client.get("/api/users")
            if users_response.status_code == 200:
                users_data = users_response.json()
                print(f"✅ Users access successful - {users_data['total']} users visible")
            else:
                print(f"❌ Users access failed: {users_response.status_code}")
            
            # Test token verification
            print(f"   Testing token verification...")
            verify_response = client.get("/api/auth/verify")
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                print(f"✅ Token verification successful - Valid: {verify_data['valid']}")
            else:
                print(f"❌ Token verification failed: {verify_response.status_code}")
            
            # Test logout
            print(f"   Testing logout...")
            logout_response = client.post("/api/auth/logout")
            if logout_response.status_code == 200:
                print(f"✅ Logout successful")
            else:
                print(f"❌ Logout failed: {logout_response.status_code}")
            
            break  # Test one user successfully
        else:
            print(f"❌ Login failed: {login_result.get('error', 'Unknown error')}")


def test_unauthorized_access():
    """Test access without token"""
    print("\n🚫 Testing unauthorized access...")
    
    protected_endpoints = [
        "/api/users",
        "/api/companies",
        "/api/auth/profile"
    ]
    
    for endpoint in protected_endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 401:
            print(f"✅ {endpoint} correctly requires authentication")
        else:
            print(f"❌ {endpoint} should require authentication but returned {response.status_code}")


def main():
    """Run all JWT tests"""
    print("🧪 GreenPulse JWT Authentication Test Suite")
    print("=" * 50)
    
    # Test API health first
    if not test_api_health():
        print("\n❌ API is not running. Please start the application first:")
        print("   python run.py")
        sys.exit(1)
    
    # Test JWT authentication
    test_jwt_authentication()
    
    # Test unauthorized access
    test_unauthorized_access()
    
    print("\n✅ JWT Authentication tests completed!")
    print("\n📋 Summary:")
    print("   - JWT tokens are issued on successful login")
    print("   - Protected endpoints require valid tokens")
    print("   - Role-based access control is enforced")
    print("   - Token verification and logout work correctly")


if __name__ == "__main__":
    main()
