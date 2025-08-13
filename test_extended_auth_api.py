#!/usr/bin/env python
"""
Comprehensive test script for all authentication API endpoints
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

class AuthAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_data = None
    
    def log(self, message, status="INFO"):
        status_colors = {
            "INFO": "\033[94m",      # Blue
            "SUCCESS": "\033[92m",   # Green
            "ERROR": "\033[91m",     # Red
            "WARNING": "\033[93m"    # Yellow
        }
        reset_color = "\033[0m"
        color = status_colors.get(status, "")
        print(f"{color}{status}{reset_color}: {message}")
    
    def test_register(self):
        """Test user registration"""
        self.log("🧪 Testing User Registration...", "INFO")
        
        data = {
            "name": "Test User Extended",
            "email": "testextended@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/register/", json=data)
            self.log(f"Status Code: {response.status_code}", "INFO")
            
            if response.status_code == 201:
                self.user_data = response.json()
                self.log("✅ Registration successful!", "SUCCESS")
                return True
            else:
                self.log(f"❌ Registration failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def test_login(self):
        """Test user login"""
        self.log("🧪 Testing User Login...", "INFO")
        
        data = {
            "email": "testextended@example.com",
            "password": "testpass123"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login/", json=data)
            self.log(f"Status Code: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('data', {}).get('access')
                if self.access_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                    self.log("✅ Login successful!", "SUCCESS")
                    return True
                else:
                    self.log("❌ No access token received", "ERROR")
                    return False
            else:
                self.log(f"❌ Login failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def test_profile(self):
        """Test profile endpoint"""
        self.log("🧪 Testing Profile Endpoint...", "INFO")
        
        try:
            response = self.session.get(f"{BASE_URL}/api/auth/profile/")
            self.log(f"Status Code: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                self.log("✅ Profile retrieval successful!", "SUCCESS")
                return True
            else:
                self.log(f"❌ Profile retrieval failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def test_password_change(self):
        """Test password change"""
        self.log("🧪 Testing Password Change...", "INFO")
        
        data = {
            "old_password": "testpass123",
            "new_password": "newpass456",
            "new_password_confirm": "newpass456"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/password/change/", json=data)
            self.log(f"Status Code: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                self.log("✅ Password change successful!", "SUCCESS")
                return True
            else:
                self.log(f"❌ Password change failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def test_password_reset_request(self):
        """Test password reset request"""
        self.log("🧪 Testing Password Reset Request...", "INFO")
        
        data = {
            "email": "testextended@example.com"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/password/reset/", json=data)
            self.log(f"Status Code: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                self.log("✅ Password reset request successful!", "SUCCESS")
                return True
            else:
                self.log(f"❌ Password reset request failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        self.log("🧪 Testing Password Reset Confirmation...", "INFO")
        
        data = {
            "token": "dummy_token_123",
            "new_password": "resetpass789",
            "new_password_confirm": "resetpass789"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/password/reset/confirm/", json=data)
            self.log(f"Status Code: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                self.log("✅ Password reset confirmation successful!", "SUCCESS")
                return True
            else:
                self.log(f"❌ Password reset confirmation failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def test_logout(self):
        """Test logout"""
        self.log("🧪 Testing Logout...", "INFO")
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/logout/")
            self.log(f"Status Code: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                self.log("✅ Logout successful!", "SUCCESS")
                # Clear the token
                self.access_token = None
                self.session.headers.pop('Authorization', None)
                return True
            else:
                self.log(f"❌ Logout failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def test_account_deletion(self):
        """Test account deletion"""
        self.log("🧪 Testing Account Deletion...", "INFO")
        
        # First login again to get a fresh token
        if not self.test_login():
            self.log("❌ Cannot test account deletion without login", "ERROR")
            return False
        
        data = {
            "password": "newpass456"  # Use the changed password
        }
        
        try:
            response = self.session.delete(f"{BASE_URL}/api/auth/account/delete/", json=data)
            self.log(f"Status Code: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                self.log("✅ Account deletion successful!", "SUCCESS")
                return True
            else:
                self.log(f"❌ Account deletion failed: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        self.log("🚀 Starting Comprehensive Authentication API Testing", "INFO")
        print("=" * 60)
        
        tests = [
            ("Registration", self.test_register),
            ("Login", self.test_login),
            ("Profile", self.test_profile),
            ("Password Change", self.test_password_change),
            ("Password Reset Request", self.test_password_reset_request),
            ("Password Reset Confirm", self.test_password_reset_confirm),
            ("Logout", self.test_logout),
            ("Account Deletion", self.test_account_deletion),
        ]
        
        results = []
        for test_name, test_func in tests:
            self.log(f"Running {test_name} test...", "INFO")
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                self.log(f"❌ {test_name} test crashed: {str(e)}", "ERROR")
                results.append((test_name, False))
        
        # Print summary
        print("\n" + "=" * 60)
        self.log("📊 TEST RESULTS SUMMARY", "INFO")
        print("=" * 60)
        
        passed = 0
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            color = "\033[92m" if success else "\033[91m"
            reset = "\033[0m"
            print(f"{color}{status}{reset}: {test_name}")
            if success:
                passed += 1
        
        print(f"\nTotal: {len(results)} tests")
        print(f"Passed: {passed}")
        print(f"Failed: {len(results) - passed}")
        
        if passed == len(results):
            self.log("🎉 All tests passed!", "SUCCESS")
        else:
            self.log("⚠️  Some tests failed", "WARNING")
        
        print("=" * 60)

def main():
    tester = AuthAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

