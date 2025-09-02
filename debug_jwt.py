#!/usr/bin/env python3
"""
Debug JWT Token Issues
"""
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
import jwt as pyjwt

def debug_jwt():
    """Debug JWT token generation and validation"""
    print("🔍 Debugging JWT Configuration")
    print("=" * 40)
    
    # Create the app
    app = create_app()
    
    with app.app_context():
        print(f"SECRET_KEY: {app.config.get('SECRET_KEY')[:20]}...")
        print(f"JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')[:20]}...")
        print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
    
    with app.test_client() as client:
        # Test login and examine token
        print("\n🔐 Testing login and examining token...")
        login_data = {
            'email': 'admin@bergen-maritime.no',
            'password': 'secure_password_123'
        }
        
        response = client.post('/api/auth/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            access_token = data.get('access_token')
            
            print(f"✅ Login successful, token length: {len(access_token)}")
            
            # Decode the token to see what's inside
            try:
                # Decode without verification first to see contents
                decoded = pyjwt.decode(access_token, options={"verify_signature": False})
                print(f"📄 Token contents: {json.dumps(decoded, indent=2, default=str)}")
                
                # Try to decode with verification using the secret
                with app.app_context():
                    secret = app.config.get('JWT_SECRET_KEY')
                    verified = pyjwt.decode(access_token, secret, algorithms=['HS256'])
                    print(f"✅ Token verification successful with secret")
                    
            except Exception as e:
                print(f"❌ Token decode error: {e}")
            
            # Test the token with a manual request
            print(f"\n🧪 Testing manual authenticated request...")
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = client.get('/api/auth/profile', headers=headers)
            print(f"Profile response status: {profile_response.status_code}")
            if profile_response.status_code != 200:
                print(f"Response data: {profile_response.get_json()}")
                
        else:
            print(f"❌ Login failed: {response.get_json()}")

if __name__ == "__main__":
    debug_jwt()
