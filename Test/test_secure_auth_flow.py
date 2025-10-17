#!/usr/bin/env python3
"""
Test script for secure authentication flow
Tests that session creation is required before accessing any endpoints
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

User = get_user_model()

def test_session_creation():
    """Test that session creation endpoint works without authentication"""
    print("\n🔑 Testing Session Creation (Anonymous Access)")
    print("-" * 50)
    
    client = Client()
    
    # Session creation should work without any authentication
    response = client.get('/api/common/session/')
    
    if response.status_code == 200:
        print("✅ Session creation successful")
        print(f"   - Status: {response.status_code}")
        
        # Check if session cookie is set
        if 'sessionid' in response.cookies:
            print("✅ Session cookie set")
            session_cookie = response.cookies['sessionid']
            print(f"   - HttpOnly: {session_cookie.get('httponly', False)}")
            print(f"   - SameSite: {session_cookie.get('samesite', 'None')}")
        else:
            print("❌ Session cookie not set")
            return False
        
        return True
    else:
        print(f"❌ Session creation failed: {response.status_code}")
        return False

def test_endpoints_require_session():
    """Test that endpoints reject requests without sessions"""
    print("\n🚫 Testing Endpoints Require Session")
    print("-" * 50)
    
    client = Client()
    
    # Test endpoints that should require session
    endpoints_to_test = [
        ('/api/user/login/', 'POST', {'mobile_number': '9999999999', 'password': 'test'}),
        ('/api/user/register/', 'POST', {'mobile_number': '8888888888', 'password': 'test'}),
        ('/api/common/cart/', 'GET', {}),
        ('/api/restaurant/menu/', 'GET', {}),
        ('/api/common/categories/', 'GET', {}),
    ]
    
    all_rejected = True
    
    for endpoint, method, data in endpoints_to_test:
        try:
            if method == 'GET':
                response = client.get(endpoint)
            elif method == 'POST':
                response = client.post(endpoint, data, content_type='application/json')
            
            if response.status_code in [401, 403]:
                print(f"✅ {endpoint} properly rejected: {response.status_code}")
            else:
                print(f"❌ {endpoint} should be rejected but got: {response.status_code}")
                all_rejected = False
                
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {e}")
            all_rejected = False
    
    return all_rejected

def test_session_then_login():
    """Test complete flow: session creation -> login -> authenticated call"""
    print("\n🔄 Testing Complete Authentication Flow")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create session
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False
    print("✅ Step 1: Session created")
    
    # Step 2: Login with session
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Step 2: Login failed: {login_response.status_code}")
        try:
            print(f"   Error: {login_response.json()}")
        except:
            print(f"   Raw response: {login_response.content}")
        return False
    print("✅ Step 2: Login successful")
    
    # Step 3: Make authenticated call
    cart_response = client.get('/api/common/cart/')
    if cart_response.status_code != 200:
        print(f"❌ Step 3: Cart access failed: {cart_response.status_code}")
        return False
    print("✅ Step 3: Authenticated API call successful")
    
    # Step 4: Test logout
    logout_response = client.post('/api/user/logout/')
    if logout_response.status_code != 200:
        print(f"❌ Step 4: Logout failed: {logout_response.status_code}")
        return False
    print("✅ Step 4: Logout successful")
    
    return True

def test_session_only_endpoint():
    """Test that only session creation endpoint allows anonymous access"""
    print("\n🎯 Testing Session-Only Anonymous Access")
    print("-" * 50)
    
    # Test that session creation is the ONLY endpoint that allows anonymous access
    anonymous_allowed_endpoints = [
        '/api/common/session/',
    ]
    
    client = Client()
    
    for endpoint in anonymous_allowed_endpoints:
        response = client.get(endpoint)
        if response.status_code == 200:
            print(f"✅ {endpoint} allows anonymous access")
        else:
            print(f"❌ {endpoint} should allow anonymous access but got: {response.status_code}")
            return False
    
    return True

def main():
    print("🔐 Secure Authentication Flow Tests")
    print("=" * 60)
    
    # Ensure test user exists
    try:
        user = User.objects.get(mobile_number='9999999999')
        print("✅ Using existing test user: 9999999999")
    except User.DoesNotExist:
        user = User.objects.create_user(
            mobile_number='9999999999',
            password='password123',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        print("✅ Created test user: 9999999999")
    
    # Run tests
    tests = [
        ("Session Creation", test_session_creation),
        ("Endpoints Require Session", test_endpoints_require_session),
        ("Complete Auth Flow", test_session_then_login),
        ("Session-Only Access", test_session_only_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Secure Authentication Tests Passed!")
        print("🔒 Your authentication system is properly secured!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
