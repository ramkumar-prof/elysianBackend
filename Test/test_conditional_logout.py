#!/usr/bin/env python3
"""
Test script to verify conditional logout behavior:
- Valid refresh token -> create new access token
- Invalid/no refresh token -> create new session
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

def test_logout_with_valid_refresh_token():
    """Test logout with valid refresh token creates new access token"""
    print("\n🔄 Testing Logout with Valid Refresh Token")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Login to get valid tokens
    session_response = client.get('/api/common/session/')
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Get initial tokens
    initial_access_token = login_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    initial_refresh_token = login_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not initial_access_token or not initial_refresh_token:
        print("❌ Initial tokens not set")
        return False
    
    print("✅ Login successful, tokens obtained")
    
    # Step 2: Logout with valid refresh token
    logout_response = client.post('/api/user/logout/')
    
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    # Check response
    logout_data = logout_response.json()
    if 'access_token' not in logout_data:
        print("❌ Logout response missing access_token")
        return False
    
    if 'session_id' in logout_data:
        print("❌ Logout response should not contain session_id when refresh token is valid")
        return False
    
    if 'new access token created' not in logout_data.get('message', ''):
        print("❌ Logout message doesn't indicate access token creation")
        return False
    
    print("✅ Logout response indicates new access token created")
    
    # Check that new tokens are set
    new_access_token = logout_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    new_refresh_token = logout_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    session_cookie = logout_response.cookies.get(SESSION_COOKIE_NAME)
    
    if not new_access_token or not new_refresh_token:
        print("❌ New tokens not set after logout")
        return False
    
    if session_cookie and session_cookie.value:
        print("❌ Session cookie should not be set when refresh token is valid")
        return False
    
    print("✅ New JWT tokens set, no session cookie")
    
    # Verify tokens are different (new tokens generated)
    if new_access_token.value != initial_access_token.value:
        print("✅ New access token generated")
    else:
        print("⚠️  Access token appears unchanged")
    
    # Step 3: Verify user can still access authenticated endpoints
    user_response = client.get('/api/user/me/')
    if user_response.status_code == 200:
        print("✅ Can access authenticated endpoints with new tokens")
    else:
        print(f"❌ Cannot access authenticated endpoints: {user_response.status_code}")
        return False
    
    return True

def test_logout_with_invalid_refresh_token():
    """Test logout with invalid refresh token creates new session"""
    print("\n🚪 Testing Logout with Invalid Refresh Token")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create session and manually set invalid refresh token
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False
    
    # Manually set invalid refresh token cookie
    client.cookies[REFRESH_TOKEN_COOKIE_NAME] = 'invalid_token_value'
    
    print("✅ Invalid refresh token set")
    
    # Step 2: Logout with invalid refresh token
    logout_response = client.post('/api/user/logout/')
    
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    # Check response
    logout_data = logout_response.json()
    if 'session_id' not in logout_data:
        print("❌ Logout response missing session_id")
        return False
    
    if 'access_token' in logout_data:
        print("❌ Logout response should not contain access_token when refresh token is invalid")
        return False
    
    if 'new session created' not in logout_data.get('message', ''):
        print("❌ Logout message doesn't indicate session creation")
        return False
    
    print("✅ Logout response indicates new session created")
    
    # Check that session cookie is set and JWT cookies are cleared
    new_session_cookie = logout_response.cookies.get(SESSION_COOKIE_NAME)
    access_token_after = logout_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token_after = logout_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not new_session_cookie or not new_session_cookie.value:
        print("❌ New session cookie not set")
        return False
    
    access_cleared = not access_token_after or access_token_after.value == ''
    refresh_cleared = not refresh_token_after or refresh_token_after.value == ''
    
    if not access_cleared or not refresh_cleared:
        print("❌ JWT tokens not properly cleared")
        return False
    
    print("✅ New session cookie set, JWT tokens cleared")
    
    # Step 3: Verify can access public endpoints but not authenticated ones
    menu_response = client.get('/api/restaurant/menu/')
    if menu_response.status_code == 200:
        print("✅ Can access public endpoints with new session")
    else:
        print(f"❌ Cannot access public endpoints: {menu_response.status_code}")
        return False
    
    user_response = client.get('/api/user/me/')
    if user_response.status_code in [401, 403]:
        print("✅ Cannot access authenticated endpoints (as expected)")
    else:
        print(f"❌ Should not be able to access authenticated endpoints: {user_response.status_code}")
        return False
    
    return True

def test_logout_with_no_refresh_token():
    """Test logout with no refresh token creates new session"""
    print("\n🆕 Testing Logout with No Refresh Token")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create session only (no login)
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False
    
    print("✅ Session created, no refresh token")
    
    # Step 2: Logout without any refresh token
    logout_response = client.post('/api/user/logout/')
    
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    # Check response
    logout_data = logout_response.json()
    if 'session_id' not in logout_data:
        print("❌ Logout response missing session_id")
        return False
    
    if 'access_token' in logout_data:
        print("❌ Logout response should not contain access_token when no refresh token")
        return False
    
    if 'new session created' not in logout_data.get('message', ''):
        print("❌ Logout message doesn't indicate session creation")
        return False
    
    print("✅ Logout response indicates new session created")
    
    # Check that new session cookie is set
    new_session_cookie = logout_response.cookies.get(SESSION_COOKIE_NAME)
    if not new_session_cookie or not new_session_cookie.value:
        print("❌ New session cookie not set")
        return False
    
    print("✅ New session cookie set")
    
    # Step 3: Verify can access public endpoints
    menu_response = client.get('/api/restaurant/menu/')
    if menu_response.status_code == 200:
        print("✅ Can access public endpoints with new session")
    else:
        print(f"❌ Cannot access public endpoints: {menu_response.status_code}")
        return False
    
    return True

def test_logout_behavior_consistency():
    """Test that logout behavior is consistent across multiple calls"""
    print("\n🔄 Testing Logout Behavior Consistency")
    print("-" * 50)
    
    client = Client()
    
    # Test 1: Valid token -> Access token
    session_response = client.get('/api/common/session/')
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    logout_response1 = client.post('/api/user/logout/')
    logout_data1 = logout_response1.json()
    
    if 'access_token' not in logout_data1:
        print("❌ First logout should create access token")
        return False
    
    print("✅ First logout with valid token creates access token")
    
    # Test 2: Still valid token -> Access token again
    logout_response2 = client.post('/api/user/logout/')
    logout_data2 = logout_response2.json()
    
    if 'access_token' not in logout_data2:
        print("❌ Second logout should also create access token")
        return False
    
    print("✅ Second logout with valid token creates access token")
    
    # Test 3: Clear tokens manually and logout -> Session
    client.cookies.clear()
    logout_response3 = client.post('/api/user/logout/')
    logout_data3 = logout_response3.json()
    
    if 'session_id' not in logout_data3:
        print("❌ Third logout should create session")
        return False
    
    print("✅ Third logout without token creates session")
    
    return True

def main():
    print("🔄 Conditional Logout Behavior Tests")
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
        ("Logout with Valid Refresh Token", test_logout_with_valid_refresh_token),
        ("Logout with Invalid Refresh Token", test_logout_with_invalid_refresh_token),
        ("Logout with No Refresh Token", test_logout_with_no_refresh_token),
        ("Logout Behavior Consistency", test_logout_behavior_consistency),
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
        print("🎉 All Conditional Logout Tests Passed!")
        print("🔒 Your conditional logout logic is working perfectly!")
        print("✨ Valid tokens -> New access token | Invalid/No tokens -> New session")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
