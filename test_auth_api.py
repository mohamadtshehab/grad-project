#!/usr/bin/env python
"""
Test script for authentication API endpoints
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_register():
    """Test user registration endpoint"""
    print("🧪 Testing User Registration...")
    
    data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register/", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return response.json()
        else:
            print("❌ Registration failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_login():
    """Test user login endpoint"""
    print("\n🧪 Testing User Login...")
    
    data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_profile():
    """Test profile endpoint (requires authentication)"""
    print("\n🧪 Testing Profile Endpoint...")
    
    # First login to get token
    login_data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            # The access token is nested in the 'data' field
            access_token = token_data.get('data', {}).get('access')
            
            if access_token:
                headers = {'Authorization': f'Bearer {access_token}'}
                response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    print("✅ Profile retrieval successful!")
                else:
                    print("❌ Profile retrieval failed!")
            else:
                print("❌ No access token received")
        else:
            print("❌ Login failed, cannot test profile")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Testing Authentication API Endpoints")
    print("=" * 50)
    
    # Test registration
    user_data = test_register()
    
    # Test login
    login_data = test_login()
    
    # Test profile (requires authentication)
    test_profile()
    
    print("\n" + "=" * 50)
    print("🎉 Authentication API testing completed!")

if __name__ == "__main__":
    main()
