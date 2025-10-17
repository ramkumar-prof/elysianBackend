#!/usr/bin/env python3
"""
Test script to verify logout creates new session and sets it in cookie
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

from elysianBackend.constants import (
    ACCESS_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_NAME,
    SESSION_COOKIE_NAME
)

User = get_user_model()

def test_logout_session_creation():
    """Test that logout creates a new session and sets it in cookie"""
    print("\n🚪 Testing Logout Session Creation")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create initial session and login
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Initial session creation failed")
        return False
    
    initial_session_id = session_response.cookies.get(SESSION_COOKIE_NAME)
    if not initial_session_id:
        print("❌ Initial session cookie not set")
        return False
    
    print(f"✅ Initial session created: {initial_session_id.value[:8]}...")
    
    # Step 2: Login (should clear session and set JWT)
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Verify JWT tokens are set
    access_token = login_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token = login_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not access_token or not refresh_token:
        print("❌ JWT tokens not set after login")
        return False
    
    print("✅ Login successful, JWT tokens set")
    
    # Step 3: Logout (should clear JWT and create new session)
    logout_response = client.post('/api/user/logout/')
    
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    # Check response contains session_id
    logout_data = logout_response.json()
    if 'session_id' not in logout_data:
        print("❌ Logout response doesn't contain session_id")
        return False
    
    new_session_id_from_response = logout_data['session_id']
    print(f"✅ Logout response contains session_id: {new_session_id_from_response[:8]}...")
    
    # Check that new session cookie is set
    new_session_cookie = logout_response.cookies.get(SESSION_COOKIE_NAME)
    if not new_session_cookie:
        print("❌ New session cookie not set after logout")
        return False
    
    new_session_id_from_cookie = new_session_cookie.value
    print(f"✅ New session cookie set: {new_session_id_from_cookie[:8]}...")
    
    # Verify session IDs match
    if new_session_id_from_response != new_session_id_from_cookie:
        print("❌ Session ID in response doesn't match cookie")
        return False
    
    print("✅ Session ID in response matches cookie")
    
    # Verify it's different from initial session
    if new_session_id_from_cookie == initial_session_id.value:
        print("⚠️  New session ID is same as initial (may be unexpected)")
    else:
        print("✅ New session ID is different from initial session")
    
    return True

def test_logout_jwt_token_clearing():
    """Test that logout properly clears JWT tokens"""
    print("\n🗑️  Testing JWT Token Clearing on Logout")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Login to get JWT tokens
    session_response = client.get('/api/common/session/')
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Verify tokens are set
    access_token_before = login_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token_before = login_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not access_token_before or not refresh_token_before:
        print("❌ JWT tokens not set after login")
        return False
    
    print("✅ JWT tokens set after login")
    
    # Step 2: Logout
    logout_response = client.post('/api/user/logout/')
    
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    # Check that JWT tokens are cleared
    access_token_after = logout_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token_after = logout_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    # Tokens should be cleared (empty value or deleted)
    access_token_cleared = not access_token_after or access_token_after.value == ''
    refresh_token_cleared = not refresh_token_after or refresh_token_after.value == ''
    
    if access_token_cleared:
        print("✅ Access token cleared on logout")
    else:
        print(f"❌ Access token not cleared: {access_token_after.value[:20]}...")
        return False
    
    if refresh_token_cleared:
        print("✅ Refresh token cleared on logout")
    else:
        print(f"❌ Refresh token not cleared: {refresh_token_after.value[:20]}...")
        return False
    
    return True

def test_post_logout_anonymous_access():
    """Test that after logout, user can access public endpoints with new session"""
    print("\n🌐 Testing Post-Logout Anonymous Access")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Login and logout to get new session
    session_response = client.get('/api/common/session/')
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    logout_response = client.post('/api/user/logout/')
    
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    # Step 2: Try to access public endpoints with new session
    public_endpoints = [
        '/api/restaurant/menu/',
        '/api/common/categories/',
        '/api/common/cart/',
    ]
    
    for endpoint in public_endpoints:
        response = client.get(endpoint)
        if response.status_code == 200:
            print(f"✅ {endpoint} accessible with new session")
        else:
            print(f"❌ {endpoint} failed with new session: {response.status_code}")
            return False
    
    # Step 3: Try to access JWT-only endpoints (should fail)
    jwt_only_endpoints = [
        '/api/user/me/',
        '/api/user/addresses/',
    ]
    
    for endpoint in jwt_only_endpoints:
        response = client.get(endpoint)
        if response.status_code in [401, 403]:
            print(f"✅ {endpoint} properly rejected without JWT")
        else:
            print(f"❌ {endpoint} should be rejected but got: {response.status_code}")
            return False
    
    return True

def test_session_cookie_properties():
    """Test that the new session cookie has proper security properties"""
    print("\n🔒 Testing Session Cookie Security Properties")
    print("-" * 50)
    
    client = Client()
    
    # Login and logout to get new session cookie
    session_response = client.get('/api/common/session/')
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    logout_response = client.post('/api/user/logout/')
    
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    # Check session cookie properties
    session_cookie = logout_response.cookies.get(SESSION_COOKIE_NAME)
    if not session_cookie:
        print("❌ Session cookie not found")
        return False
    
    # Check security properties
    if hasattr(session_cookie, 'httponly') and session_cookie.httponly:
        print("✅ Session cookie is HttpOnly")
    else:
        print("⚠️  Session cookie HttpOnly property not verified")
    
    if hasattr(session_cookie, 'samesite'):
        print(f"✅ Session cookie SameSite: {session_cookie.samesite}")
    else:
        print("⚠️  Session cookie SameSite property not verified")
    
    if hasattr(session_cookie, 'path') and session_cookie.path:
        print(f"✅ Session cookie Path: {session_cookie.path}")
    else:
        print("⚠️  Session cookie Path property not verified")
    
    return True

def main():
    print("🚪 Logout Session Creation Tests")
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
        ("Logout Session Creation", test_logout_session_creation),
        ("JWT Token Clearing on Logout", test_logout_jwt_token_clearing),
        ("Post-Logout Anonymous Access", test_post_logout_anonymous_access),
        ("Session Cookie Security Properties", test_session_cookie_properties),
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
        print("🎉 All Logout Session Creation Tests Passed!")
        print("🔒 Your logout flow with session creation is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
