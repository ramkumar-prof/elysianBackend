#!/usr/bin/env python3
"""
Test script to verify enhanced session creation API with refresh token handling
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

def test_session_creation_without_tokens():
    """Test session creation when no tokens are present"""
    print("\n📝 Testing Session Creation Without Tokens")
    print("-" * 50)
    
    client = Client()
    
    # Call session creation without any tokens
    session_response = client.get('/api/common/session/')
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.status_code}")
        return False
    
    # Check response
    session_data = session_response.json()
    if session_data.get('message') != 'Session created':
        print(f"❌ Unexpected response message: {session_data.get('message')}")
        return False
    
    if 'session_id' not in session_data:
        print("❌ Session ID not in response")
        return False
    
    print(f"✅ Session created: {session_data['session_id'][:8]}...")
    
    # Check session cookie is set
    session_cookie = session_response.cookies.get(SESSION_COOKIE_NAME)
    if not session_cookie:
        print("❌ Session cookie not set")
        return False
    
    if session_cookie.value != session_data['session_id']:
        print("❌ Session cookie value doesn't match response")
        return False
    
    print("✅ Session cookie set correctly")
    
    # Check that JWT cookies are cleared
    access_token = session_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token = session_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    access_cleared = not access_token or access_token.value == ''
    refresh_cleared = not refresh_token or refresh_token.value == ''
    
    if access_cleared and refresh_cleared:
        print("✅ JWT tokens cleared")
    else:
        print("⚠️  JWT token clearing not verified")
    
    return True

def test_session_creation_with_valid_refresh_token():
    """Test session creation when valid refresh token is present"""
    print("\n🔄 Testing Session Creation With Valid Refresh Token")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Login to get refresh token
    initial_session = client.get('/api/common/session/')
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
    
    print("✅ Initial tokens obtained")
    
    # Step 2: Call session creation with valid refresh token
    session_response = client.get('/api/common/session/')
    
    if session_response.status_code != 200:
        print(f"❌ Session creation with refresh token failed: {session_response.status_code}")
        return False
    
    # Check response
    session_data = session_response.json()
    if session_data.get('message') != 'Access token refreshed':
        print(f"❌ Unexpected response message: {session_data.get('message')}")
        return False
    
    if 'access_token' not in session_data:
        print("❌ Access token not in response")
        return False
    
    print("✅ Access token refreshed via session creation")
    
    # Check that new tokens are set
    new_access_token = session_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    new_refresh_token = session_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not new_access_token or not new_refresh_token:
        print("❌ New tokens not set")
        return False
    
    print("✅ New JWT tokens set")
    
    # Verify tokens are different (new tokens generated)
    if new_access_token.value != initial_access_token.value:
        print("✅ New access token generated")
    else:
        print("⚠️  Access token unchanged (may be expected)")
    
    # Check that no session cookie is set (should remain JWT authenticated)
    session_cookie = session_response.cookies.get(SESSION_COOKIE_NAME)
    if session_cookie and session_cookie.value:
        print("⚠️  Session cookie set when using refresh token")
    else:
        print("✅ No session cookie set (JWT mode maintained)")
    
    return True

def test_session_creation_with_invalid_refresh_token():
    """Test session creation when invalid refresh token is present"""
    print("\n❌ Testing Session Creation With Invalid Refresh Token")
    print("-" * 50)
    
    client = Client()
    
    # Set an invalid refresh token manually
    client.cookies[REFRESH_TOKEN_COOKIE_NAME] = 'invalid_token_value'
    
    # Call session creation
    session_response = client.get('/api/common/session/')
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.status_code}")
        return False
    
    # Should fall back to session creation
    session_data = session_response.json()
    if session_data.get('message') != 'Session created':
        print(f"❌ Should fall back to session creation: {session_data.get('message')}")
        return False
    
    if 'session_id' not in session_data:
        print("❌ Session ID not in response")
        return False
    
    print("✅ Fell back to session creation with invalid refresh token")
    
    # Check session cookie is set
    session_cookie = session_response.cookies.get(SESSION_COOKIE_NAME)
    if not session_cookie:
        print("❌ Session cookie not set")
        return False
    
    print("✅ Session cookie set correctly")
    
    # Check that JWT cookies are cleared
    access_token = session_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token = session_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    access_cleared = not access_token or access_token.value == ''
    refresh_cleared = not refresh_token or refresh_token.value == ''
    
    if access_cleared and refresh_cleared:
        print("✅ Invalid JWT tokens cleared")
    else:
        print("⚠️  JWT token clearing not verified")
    
    return True

def test_session_creation_flow_integration():
    """Test integration with existing authentication flow"""
    print("\n🔗 Testing Session Creation Flow Integration")
    print("-" * 50)
    
    client = Client()
    
    # Step 1: Create initial session
    session_response1 = client.get('/api/common/session/')
    if session_response1.status_code != 200:
        print("❌ Initial session creation failed")
        return False
    
    session_id1 = session_response1.json().get('session_id')
    print(f"✅ Initial session: {session_id1[:8]}...")
    
    # Step 2: Use session to access public endpoint
    menu_response = client.get('/api/restaurant/menu/')
    if menu_response.status_code != 200:
        print(f"❌ Menu access with session failed: {menu_response.status_code}")
        return False
    
    print("✅ Public endpoint accessible with session")
    
    # Step 3: Login (should clear session, set JWT)
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    print("✅ Login successful")
    
    # Step 4: Call session creation (should refresh tokens)
    session_response2 = client.get('/api/common/session/')
    if session_response2.status_code != 200:
        print(f"❌ Session creation after login failed: {session_response2.status_code}")
        return False
    
    session_data2 = session_response2.json()
    if session_data2.get('message') != 'Access token refreshed':
        print(f"❌ Should refresh token: {session_data2.get('message')}")
        return False
    
    print("✅ Token refreshed via session creation")
    
    # Step 5: Logout (should create new session)
    logout_response = client.post('/api/user/logout/')
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    session_id3 = logout_response.json().get('session_id')
    print(f"✅ Logout created session: {session_id3[:8]}...")
    
    # Step 6: Call session creation again (should maintain session)
    session_response3 = client.get('/api/common/session/')
    if session_response3.status_code != 200:
        print(f"❌ Session creation after logout failed: {session_response3.status_code}")
        return False
    
    session_data3 = session_response3.json()
    if session_data3.get('message') != 'Session created':
        print(f"❌ Should maintain session mode: {session_data3.get('message')}")
        return False
    
    print("✅ Session mode maintained after logout")
    
    return True

def main():
    print("🔄 Enhanced Session Creation Tests")
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
        ("Session Creation Without Tokens", test_session_creation_without_tokens),
        ("Session Creation With Valid Refresh Token", test_session_creation_with_valid_refresh_token),
        ("Session Creation With Invalid Refresh Token", test_session_creation_with_invalid_refresh_token),
        ("Session Creation Flow Integration", test_session_creation_flow_integration),
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
        print("🎉 All Enhanced Session Creation Tests Passed!")
        print("🔒 Your smart session creation is working perfectly!")
        print("✨ Automatic token refresh and session fallback implemented!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
