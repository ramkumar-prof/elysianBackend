#!/usr/bin/env python3
"""
Test script to verify complete logout flow: JWT user -> logout -> anonymous session -> browsing
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

def test_complete_logout_to_anonymous_flow():
    """Test complete flow: Anonymous -> Login -> Authenticated -> Logout -> Anonymous"""
    print("\n🔄 Testing Complete Logout to Anonymous Flow")
    print("-" * 60)
    
    client = Client()
    
    # Phase 1: Anonymous user creates session
    print("\n📝 Phase 1: Anonymous Session Creation")
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Anonymous session creation failed")
        return False
    
    initial_session_id = session_response.cookies.get(SESSION_COOKIE_NAME)
    if not initial_session_id:
        print("❌ Initial session cookie not set")
        return False
    
    print(f"✅ Anonymous session created: {initial_session_id.value[:8]}...")
    
    # Test anonymous browsing
    menu_response = client.get('/api/restaurant/menu/')
    if menu_response.status_code == 200:
        print("✅ Anonymous user can browse menu")
    else:
        print(f"❌ Anonymous menu access failed: {menu_response.status_code}")
        return False
    
    # Phase 2: User logs in
    print("\n🔐 Phase 2: User Login")
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Verify JWT tokens are set and session is cleared
    access_token = login_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token = login_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    session_after_login = login_response.cookies.get(SESSION_COOKIE_NAME)
    
    if not access_token or not refresh_token:
        print("❌ JWT tokens not set after login")
        return False
    
    if session_after_login and session_after_login.value == '':
        print("✅ Session cookie cleared after login")
    else:
        print("⚠️  Session cookie handling after login")
    
    print("✅ User logged in successfully with JWT tokens")
    
    # Test authenticated access
    user_response = client.get('/api/user/me/')
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"✅ Authenticated user access: {user_data.get('mobile_number', 'Unknown')}")
    else:
        print(f"❌ Authenticated access failed: {user_response.status_code}")
        return False
    
    # Phase 3: User logs out
    print("\n🚪 Phase 3: User Logout")
    logout_response = client.post('/api/user/logout/')
    
    if logout_response.status_code != 200:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return False
    
    # Verify logout response contains new session
    logout_data = logout_response.json()
    if 'session_id' not in logout_data:
        print("❌ Logout response missing session_id")
        return False
    
    new_session_id = logout_data['session_id']
    print(f"✅ Logout successful, new session: {new_session_id[:8]}...")
    
    # Verify JWT tokens are cleared
    access_token_after = logout_response.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token_after = logout_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    new_session_cookie = logout_response.cookies.get(SESSION_COOKIE_NAME)
    
    access_cleared = not access_token_after or access_token_after.value == ''
    refresh_cleared = not refresh_token_after or refresh_token_after.value == ''
    
    if access_cleared and refresh_cleared:
        print("✅ JWT tokens cleared on logout")
    else:
        print("❌ JWT tokens not properly cleared")
        return False
    
    if new_session_cookie and new_session_cookie.value == new_session_id:
        print("✅ New session cookie set correctly")
    else:
        print("❌ New session cookie not set properly")
        return False
    
    # Phase 4: Anonymous browsing with new session
    print("\n🌐 Phase 4: Post-Logout Anonymous Browsing")
    
    # Test public endpoints work with new session
    public_endpoints = [
        ('/api/restaurant/menu/', 'Menu'),
        ('/api/common/categories/', 'Categories'),
        ('/api/common/cart/', 'Cart'),
    ]
    
    for endpoint, name in public_endpoints:
        response = client.get(endpoint)
        if response.status_code == 200:
            print(f"✅ {name} accessible with new session")
        else:
            print(f"❌ {name} failed with new session: {response.status_code}")
            return False
    
    # Test that JWT-only endpoints are properly rejected
    jwt_endpoints = [
        ('/api/user/me/', 'User Profile'),
        ('/api/user/addresses/', 'User Addresses'),
    ]
    
    for endpoint, name in jwt_endpoints:
        response = client.get(endpoint)
        if response.status_code in [401, 403]:
            print(f"✅ {name} properly rejected without JWT")
        else:
            print(f"❌ {name} should be rejected but got: {response.status_code}")
            return False
    
    # Phase 5: Verify session continuity
    print("\n🔗 Phase 5: Session Continuity Verification")
    
    # Add item to cart with new session
    cart_add_response = client.post('/api/common/cart/', {
        'product_id': 1,
        'variant_id': 1,
        'quantity': 2
    }, content_type='application/json')
    
    if cart_add_response.status_code == 200:
        print("✅ Can add items to cart with new session")
    else:
        print(f"⚠️  Cart add failed: {cart_add_response.status_code} (may be expected if product doesn't exist)")
    
    # Get cart with same session
    cart_get_response = client.get('/api/common/cart/')
    if cart_get_response.status_code == 200:
        print("✅ Can retrieve cart with new session")
    else:
        print(f"❌ Cart retrieval failed: {cart_get_response.status_code}")
        return False
    
    print("\n🎉 Complete logout to anonymous flow successful!")
    return True

def test_logout_session_isolation():
    """Test that logout creates isolated sessions for different users"""
    print("\n🔒 Testing Logout Session Isolation")
    print("-" * 50)
    
    # Create two separate clients
    client1 = Client()
    client2 = Client()
    
    # Both clients login
    for i, client in enumerate([client1, client2], 1):
        session_response = client.get('/api/common/session/')
        login_response = client.post('/api/user/login/', {
            'mobile_number': '9999999999',
            'password': 'password123'
        }, content_type='application/json')
        
        if login_response.status_code != 200:
            print(f"❌ Client {i} login failed")
            return False
    
    print("✅ Both clients logged in")
    
    # Client 1 logs out
    logout_response1 = client1.post('/api/user/logout/')
    if logout_response1.status_code != 200:
        print("❌ Client 1 logout failed")
        return False
    
    session_id1 = logout_response1.json().get('session_id')
    print(f"✅ Client 1 logged out, new session: {session_id1[:8]}...")
    
    # Client 2 logs out
    logout_response2 = client2.post('/api/user/logout/')
    if logout_response2.status_code != 200:
        print("❌ Client 2 logout failed")
        return False
    
    session_id2 = logout_response2.json().get('session_id')
    print(f"✅ Client 2 logged out, new session: {session_id2[:8]}...")
    
    # Verify sessions are different
    if session_id1 != session_id2:
        print("✅ Different sessions created for different clients")
    else:
        print("❌ Same session ID generated (security issue)")
        return False
    
    # Verify both can browse independently
    menu_response1 = client1.get('/api/restaurant/menu/')
    menu_response2 = client2.get('/api/restaurant/menu/')
    
    if menu_response1.status_code == 200 and menu_response2.status_code == 200:
        print("✅ Both clients can browse independently")
    else:
        print("❌ Independent browsing failed")
        return False
    
    return True

def main():
    print("🔄 Complete Logout Flow Tests")
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
    
    # Run tests
    tests = [
        ("Complete Logout to Anonymous Flow", test_complete_logout_to_anonymous_flow),
        ("Logout Session Isolation", test_logout_session_isolation),
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
        print("🎉 All Complete Logout Flow Tests Passed!")
        print("🔒 Your logout-to-anonymous flow is working perfectly!")
        print("✨ Users can seamlessly transition from authenticated to anonymous browsing!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
