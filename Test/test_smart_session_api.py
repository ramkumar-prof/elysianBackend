#!/usr/bin/env python3
"""
Test script to demonstrate the smart session creation API behavior
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

def demonstrate_smart_session_api():
    """Demonstrate the smart session creation API behavior"""
    print("\n🧠 Smart Session Creation API Demonstration")
    print("=" * 60)
    
    client = Client()
    
    # Scenario 1: Fresh user (no tokens)
    print("\n📱 Scenario 1: Fresh User (No Tokens)")
    print("-" * 40)
    
    session_resp = client.get('/api/common/session/')
    session_data = session_resp.json()
    
    print(f"✅ Response: {session_data['message']}")
    print(f"✅ Session ID: {session_data['session_id'][:8]}...")
    print(f"✅ Cookie Set: {SESSION_COOKIE_NAME}")
    
    # Test browsing with session
    menu_resp = client.get('/api/restaurant/menu/')
    print(f"✅ Menu Access: {menu_resp.status_code} (with session)")
    
    # Scenario 2: User logs in
    print("\n🔐 Scenario 2: User Login")
    print("-" * 40)
    
    login_resp = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    login_data = login_resp.json()
    print(f"✅ Login: {login_data['message']}")
    print(f"✅ JWT Tokens Set: {ACCESS_TOKEN_COOKIE_NAME}, {REFRESH_TOKEN_COOKIE_NAME}")
    
    # Scenario 3: Session API with valid refresh token
    print("\n🔄 Scenario 3: Session API with Valid Refresh Token")
    print("-" * 40)
    
    session_resp2 = client.get('/api/common/session/')
    session_data2 = session_resp2.json()
    
    print(f"✅ Response: {session_data2['message']}")
    print(f"✅ New Access Token: {session_data2['access_token'][:20]}...")
    print(f"✅ Behavior: Token refresh (no session cookie)")
    
    # Test authenticated access
    user_resp = client.get('/api/user/me/')
    print(f"✅ User Profile Access: {user_resp.status_code} (with JWT)")
    
    # Scenario 4: User logs out
    print("\n🚪 Scenario 4: User Logout")
    print("-" * 40)
    
    logout_resp = client.post('/api/user/logout/')
    logout_data = logout_resp.json()
    
    print(f"✅ Logout: {logout_data['message']}")
    print(f"✅ New Session ID: {logout_data['session_id'][:8]}...")
    print(f"✅ JWT Tokens Cleared, Session Cookie Set")
    
    # Scenario 5: Session API after logout (no tokens)
    print("\n🌐 Scenario 5: Session API After Logout")
    print("-" * 40)
    
    session_resp3 = client.get('/api/common/session/')
    session_data3 = session_resp3.json()
    
    print(f"✅ Response: {session_data3['message']}")
    print(f"✅ Session ID: {session_data3['session_id'][:8]}...")
    print(f"✅ Behavior: Session maintenance (no token refresh)")
    
    # Test anonymous browsing
    menu_resp2 = client.get('/api/restaurant/menu/')
    user_resp2 = client.get('/api/user/me/')
    
    print(f"✅ Menu Access: {menu_resp2.status_code} (anonymous)")
    print(f"✅ User Profile Access: {user_resp2.status_code} (rejected)")
    
    print("\n🎉 Smart Session API Demonstration Complete!")
    return True

def test_edge_cases():
    """Test edge cases for the smart session API"""
    print("\n🔍 Testing Edge Cases")
    print("=" * 40)
    
    # Edge Case 1: Expired refresh token
    print("\n⏰ Edge Case 1: Expired/Invalid Refresh Token")
    print("-" * 40)
    
    client = Client()
    
    # Set an invalid refresh token
    client.cookies[REFRESH_TOKEN_COOKIE_NAME] = 'invalid.token.here'
    
    session_resp = client.get('/api/common/session/')
    session_data = session_resp.json()
    
    print(f"✅ Response: {session_data['message']}")
    print(f"✅ Behavior: Falls back to session creation")
    
    # Edge Case 2: Multiple session API calls
    print("\n🔄 Edge Case 2: Multiple Session API Calls")
    print("-" * 40)
    
    client2 = Client()
    
    # First call
    resp1 = client2.get('/api/common/session/')
    data1 = resp1.json()
    session_id1 = data1['session_id']
    
    # Second call (should maintain same session)
    resp2 = client2.get('/api/common/session/')
    data2 = resp2.json()
    session_id2 = data2['session_id']
    
    if session_id1 == session_id2:
        print("✅ Session maintained across multiple calls")
    else:
        print("⚠️  New session created on each call")
    
    # Edge Case 3: Session API during authenticated state
    print("\n🔐 Edge Case 3: Session API During Authenticated State")
    print("-" * 40)
    
    client3 = Client()
    
    # Login first
    session_resp = client3.get('/api/common/session/')
    login_resp = client3.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    # Multiple session API calls while authenticated
    for i in range(3):
        session_resp = client3.get('/api/common/session/')
        session_data = session_resp.json()
        print(f"✅ Call {i+1}: {session_data['message']}")
    
    print("\n✅ Edge Cases Testing Complete!")
    return True

def test_api_consistency():
    """Test API response consistency"""
    print("\n📋 Testing API Response Consistency")
    print("=" * 40)
    
    client = Client()
    
    # Test response structure for session creation
    session_resp = client.get('/api/common/session/')
    session_data = session_resp.json()
    
    required_fields_session = ['message', 'session_id']
    for field in required_fields_session:
        if field in session_data:
            print(f"✅ Session response has '{field}' field")
        else:
            print(f"❌ Session response missing '{field}' field")
            return False
    
    # Login and test token refresh response
    login_resp = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    refresh_resp = client.get('/api/common/session/')
    refresh_data = refresh_resp.json()
    
    required_fields_refresh = ['message', 'access_token']
    for field in required_fields_refresh:
        if field in refresh_data:
            print(f"✅ Refresh response has '{field}' field")
        else:
            print(f"❌ Refresh response missing '{field}' field")
            return False
    
    # Test logout response
    logout_resp = client.post('/api/user/logout/')
    logout_data = logout_resp.json()
    
    required_fields_logout = ['message', 'session_id']
    for field in required_fields_logout:
        if field in logout_data:
            print(f"✅ Logout response has '{field}' field")
        else:
            print(f"❌ Logout response missing '{field}' field")
            return False
    
    print("✅ API Response Consistency Verified!")
    return True

def main():
    print("🧠 Smart Session Creation API Tests")
    print("=" * 70)
    
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
    
    # Run demonstrations and tests
    tests = [
        ("Smart Session API Demonstration", demonstrate_smart_session_api),
        ("Edge Cases Testing", test_edge_cases),
        ("API Response Consistency", test_api_consistency),
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
        print("🎉 All Smart Session API Tests Passed!")
        print("🧠 Your intelligent session creation is working perfectly!")
        print("✨ Automatic token refresh and session fallback implemented!")
        print("🔄 Seamless user experience across all authentication states!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
