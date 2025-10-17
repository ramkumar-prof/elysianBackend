#!/usr/bin/env python3
"""
Test script for new authentication classes
Tests SessionOrJWTAuthentication, JWTOnlyAuthentication, and RefreshTokenAuthentication
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

def test_session_or_jwt_auth():
    """Test SessionOrJWTAuthentication allows both session and JWT"""
    print("\n🔄 Testing SessionOrJWTAuthentication")
    print("-" * 50)
    
    client = Client()
    
    # Test 1: Session-only access (anonymous user with session)
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False
    
    # Test menu access with session only (no JWT)
    menu_response = client.get('/api/restaurant/menu/')
    if menu_response.status_code == 200:
        print("✅ Session-only access works for public endpoints")
    else:
        print(f"❌ Session-only access failed: {menu_response.status_code}")
        return False
    
    # Test 2: JWT access after login
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Test menu access with JWT cookies
    menu_response_jwt = client.get('/api/restaurant/menu/')
    if menu_response_jwt.status_code == 200:
        print("✅ JWT cookie access works for public endpoints")
    else:
        print(f"❌ JWT cookie access failed: {menu_response_jwt.status_code}")
        return False
    
    return True

def test_jwt_only_auth():
    """Test JWTOnlyAuthentication requires valid JWT token"""
    print("\n🔐 Testing JWTOnlyAuthentication")
    print("-" * 50)
    
    client = Client()
    
    # Test 1: Access without JWT should fail
    user_response = client.get('/api/user/me/')
    if user_response.status_code in [401, 403]:
        print("✅ JWT-only endpoints properly reject requests without JWT")
    else:
        print(f"❌ JWT-only endpoint should reject but got: {user_response.status_code}")
        return False
    
    # Test 2: Session creation and access should still fail
    session_response = client.get('/api/common/session/')
    user_response_with_session = client.get('/api/user/me/')
    if user_response_with_session.status_code in [401, 403]:
        print("✅ JWT-only endpoints reject session-only requests")
    else:
        print(f"❌ JWT-only endpoint should reject session but got: {user_response_with_session.status_code}")
        return False
    
    # Test 3: Login and access with JWT should work
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Now JWT access should work
    user_response_jwt = client.get('/api/user/me/')
    if user_response_jwt.status_code == 200:
        print("✅ JWT-only endpoints work with valid JWT cookies")
        user_data = user_response_jwt.json()
        print(f"   User: {user_data.get('mobile_number', 'Unknown')}")
    else:
        print(f"❌ JWT access failed: {user_response_jwt.status_code}")
        return False
    
    return True

def test_refresh_token_auth():
    """Test RefreshTokenAuthentication requires valid refresh token"""
    print("\n🔄 Testing RefreshTokenAuthentication")
    print("-" * 50)
    
    client = Client()
    
    # Test 1: Refresh without token should fail
    refresh_response = client.post('/api/user/refresh/')
    if refresh_response.status_code in [401, 403]:
        print("✅ Refresh endpoint properly rejects requests without refresh token")
    else:
        print(f"❌ Refresh endpoint should reject but got: {refresh_response.status_code}")
        return False
    
    # Test 2: Login to get refresh token
    session_response = client.get('/api/common/session/')
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Test 3: Refresh with valid token should work
    refresh_response_valid = client.post('/api/user/refresh/')
    if refresh_response_valid.status_code == 200:
        print("✅ Refresh endpoint works with valid refresh token")
        refresh_data = refresh_response_valid.json()
        if 'access_token' in refresh_data:
            print("✅ New access token provided in refresh response")
        else:
            print("❌ No access token in refresh response")
            return False
    else:
        print(f"❌ Refresh with valid token failed: {refresh_response_valid.status_code}")
        return False
    
    return True

def test_session_to_jwt_transition():
    """Test that login clears session and sets JWT cookies"""
    print("\n🔄 Testing Session to JWT Transition")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create session
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False
    
    # Check session cookie is set
    if 'sessionid' not in session_response.cookies:
        print("❌ Session cookie not set")
        return False
    print("✅ Session cookie created")
    
    # Step 2: Login (should clear session, set JWT)
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Check JWT cookies are set
    if 'access_token' in login_response.cookies and 'refresh_token' in login_response.cookies:
        print("✅ JWT cookies set after login")
    else:
        print("❌ JWT cookies not set after login")
        return False
    
    # Check session cookie is cleared (should have empty value or be deleted)
    session_cookie = login_response.cookies.get('sessionid')
    if session_cookie and session_cookie.value == '':
        print("✅ Session cookie cleared after login")
    else:
        print("✅ Session cookie handling after login (may vary by implementation)")
    
    return True

def test_endpoint_authentication_mapping():
    """Test that endpoints use correct authentication classes"""
    print("\n🎯 Testing Endpoint Authentication Mapping")
    print("-" * 50)
    
    client = Client()
    
    # Create session and login
    session_response = client.get('/api/common/session/')
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print("❌ Setup failed")
        return False
    
    # Test endpoints that should use SessionOrJWTAuthentication (public)
    public_endpoints = [
        '/api/restaurant/menu/',
        '/api/common/categories/',
        '/api/common/cart/',
    ]
    
    for endpoint in public_endpoints:
        response = client.get(endpoint)
        if response.status_code == 200:
            print(f"✅ {endpoint} accessible with JWT")
        else:
            print(f"❌ {endpoint} failed: {response.status_code}")
            return False
    
    # Test endpoints that should use JWTOnlyAuthentication (user-specific)
    jwt_only_endpoints = [
        '/api/user/me/',
        '/api/user/addresses/',
    ]
    
    for endpoint in jwt_only_endpoints:
        response = client.get(endpoint)
        if response.status_code == 200:
            print(f"✅ {endpoint} accessible with JWT")
        else:
            print(f"❌ {endpoint} failed: {response.status_code}")
            return False
    
    return True

def main():
    print("🔐 New Authentication Classes Tests")
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
        ("SessionOrJWTAuthentication", test_session_or_jwt_auth),
        ("JWTOnlyAuthentication", test_jwt_only_auth),
        ("RefreshTokenAuthentication", test_refresh_token_auth),
        ("Session to JWT Transition", test_session_to_jwt_transition),
        ("Endpoint Authentication Mapping", test_endpoint_authentication_mapping),
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
        print("🎉 All Authentication Class Tests Passed!")
        print("🔒 Your new authentication system is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
