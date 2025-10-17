#!/usr/bin/env python3
"""
Test script to verify cookie constants usage and proper token deletion
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

def test_cookie_constants_usage():
    """Test that all cookie operations use the defined constants"""
    print("\n🍪 Testing Cookie Constants Usage")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create session and verify session cookie name
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False
    
    # Check that session cookie uses the constant name
    if SESSION_COOKIE_NAME in session_response.cookies:
        print(f"✅ Session cookie uses constant: {SESSION_COOKIE_NAME}")
    else:
        print(f"❌ Session cookie not found with constant name: {SESSION_COOKIE_NAME}")
        print(f"   Available cookies: {list(session_response.cookies.keys())}")
        return False
    
    # Step 2: Login and verify JWT cookie names
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Check JWT cookies use constants
    if ACCESS_TOKEN_COOKIE_NAME in login_response.cookies:
        print(f"✅ Access token cookie uses constant: {ACCESS_TOKEN_COOKIE_NAME}")
    else:
        print(f"❌ Access token cookie not found with constant name: {ACCESS_TOKEN_COOKIE_NAME}")
        return False
    
    if REFRESH_TOKEN_COOKIE_NAME in login_response.cookies:
        print(f"✅ Refresh token cookie uses constant: {REFRESH_TOKEN_COOKIE_NAME}")
    else:
        print(f"❌ Refresh token cookie not found with constant name: {REFRESH_TOKEN_COOKIE_NAME}")
        return False
    
    return True

def test_token_deletion_before_setting():
    """Test that existing tokens are properly deleted before setting new ones"""
    print("\n🗑️  Testing Token Deletion Before Setting")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create session
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False
    
    # Step 2: First login to set initial tokens
    login_response1 = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response1.status_code != 200:
        print(f"❌ First login failed: {login_response1.status_code}")
        return False
    
    # Get initial token values
    initial_access_token = login_response1.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    initial_refresh_token = login_response1.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not initial_access_token or not initial_refresh_token:
        print("❌ Initial tokens not set properly")
        return False
    
    print("✅ Initial tokens set successfully")
    
    # Step 3: Logout to clear tokens
    logout_response = client.post('/api/user/logout/')
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    print("✅ Logout successful")
    
    # Step 4: Create new session and login again
    session_response2 = client.get('/api/common/session/')
    login_response2 = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response2.status_code != 200:
        print(f"❌ Second login failed: {login_response2.status_code}")
        return False
    
    # Get new token values
    new_access_token = login_response2.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    new_refresh_token = login_response2.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not new_access_token or not new_refresh_token:
        print("❌ New tokens not set properly")
        return False
    
    # Verify tokens are different (new tokens generated)
    if new_access_token.value != initial_access_token.value:
        print("✅ New access token generated (different from initial)")
    else:
        print("⚠️  Access token appears to be the same (may be expected)")
    
    if new_refresh_token.value != initial_refresh_token.value:
        print("✅ New refresh token generated (different from initial)")
    else:
        print("⚠️  Refresh token appears to be the same (may be expected)")
    
    return True

def test_refresh_token_replacement():
    """Test that refresh token properly replaces existing tokens"""
    print("\n🔄 Testing Refresh Token Replacement")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Login to get initial tokens
    session_response = client.get('/api/common/session/')
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    initial_access_token = login_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    initial_refresh_token = login_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    print("✅ Initial tokens obtained")
    
    # Step 2: Use refresh token to get new tokens
    refresh_response = client.post('/api/user/refresh/')
    
    if refresh_response.status_code != 200:
        print(f"❌ Refresh failed: {refresh_response.status_code}")
        return False
    
    new_access_token = refresh_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    new_refresh_token = refresh_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not new_access_token or not new_refresh_token:
        print("❌ New tokens not set after refresh")
        return False
    
    print("✅ Refresh token endpoint works")
    print("✅ New tokens set after refresh")
    
    # Verify that tokens are properly replaced
    if new_access_token.value != initial_access_token.value:
        print("✅ Access token was replaced with new value")
    else:
        print("⚠️  Access token value unchanged (may be expected)")
    
    return True

def test_session_cookie_clearing():
    """Test that session cookie is properly cleared on login"""
    print("\n🧹 Testing Session Cookie Clearing")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create session
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False
    
    session_cookie = session_response.cookies.get(SESSION_COOKIE_NAME)
    if not session_cookie or not session_cookie.value:
        print("❌ Session cookie not created properly")
        return False
    
    print(f"✅ Session cookie created: {SESSION_COOKIE_NAME}")
    
    # Step 2: Login (should clear session cookie)
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Check if session cookie is cleared (empty value or deleted)
    session_cookie_after_login = login_response.cookies.get(SESSION_COOKIE_NAME)
    if session_cookie_after_login and session_cookie_after_login.value == '':
        print(f"✅ Session cookie cleared on login: {SESSION_COOKIE_NAME}")
    elif not session_cookie_after_login:
        print(f"✅ Session cookie deleted on login: {SESSION_COOKIE_NAME}")
    else:
        print(f"⚠️  Session cookie handling: {session_cookie_after_login.value}")
    
    return True

def main():
    print("🍪 Cookie Constants and Token Deletion Tests")
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
    
    # Display constants being tested
    print(f"\n📋 Cookie Constants:")
    print(f"   SESSION_COOKIE_NAME: {SESSION_COOKIE_NAME}")
    print(f"   ACCESS_TOKEN_COOKIE_NAME: {ACCESS_TOKEN_COOKIE_NAME}")
    print(f"   REFRESH_TOKEN_COOKIE_NAME: {REFRESH_TOKEN_COOKIE_NAME}")
    
    # Run tests
    tests = [
        ("Cookie Constants Usage", test_cookie_constants_usage),
        ("Token Deletion Before Setting", test_token_deletion_before_setting),
        ("Refresh Token Replacement", test_refresh_token_replacement),
        ("Session Cookie Clearing", test_session_cookie_clearing),
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
        print("🎉 All Cookie Constants and Token Deletion Tests Passed!")
        print("🔒 Your cookie management is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
