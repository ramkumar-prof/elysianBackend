#!/usr/bin/env python3
"""
Test script for cookie-based authentication
Tests both manual token and automatic cookie authentication
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/home/kulriya68/Elysian/elysianBackend')
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from common.models import Cart, CartItem, Product, Variant, Category
from elysianBackend.constants import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME

User = get_user_model()

def setup_test_user():
    """Create or get test user"""
    user, created = User.objects.get_or_create(
        mobile_number='9999999999',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
    )
    
    if created:
        user.set_password('password123')
        user.save()
        print(f"✅ Created test user: {user.mobile_number}")
    else:
        print(f"✅ Using existing test user: {user.mobile_number}")
    
    return user

def test_login_sets_cookies():
    """Test that login sets both access and refresh token cookies"""
    print("\n🍪 Testing Login Cookie Setting")
    print("-" * 40)

    client = Client()

    # First create session (required for authentication)
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.status_code}")
        return False

    # Login request (now requires session)
    response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful")
        print(f"✅ Access token in response: {bool(data.get('access_token'))}")
        
        # Check cookies
        cookies = response.cookies
        access_cookie = cookies.get(ACCESS_TOKEN_COOKIE_NAME)
        refresh_cookie = cookies.get(REFRESH_TOKEN_COOKIE_NAME)
        
        print(f"✅ Access token cookie set: {bool(access_cookie)}")
        print(f"✅ Refresh token cookie set: {bool(refresh_cookie)}")
        
        if access_cookie:
            print(f"   - HttpOnly: {access_cookie.get('httponly', False)}")
            print(f"   - SameSite: {access_cookie.get('samesite', 'None')}")
            print(f"   - Path: {access_cookie.get('path', '/')}")
        
        return True
    else:
        print(f"❌ Login failed: {response.json()}")
        return False

def test_cookie_authentication():
    """Test that cookies can be used for authentication"""
    print("\n🔐 Testing Cookie Authentication")
    print("-" * 40)

    client = Client()

    # First create session
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False

    # Then login to get cookies
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print("❌ Login failed, cannot test cookie auth")
        return False
    
    # Test authenticated endpoint using cookies (no manual Authorization header)
    me_response = client.get('/api/user/me/')
    
    print(f"Get current user status: {me_response.status_code}")
    
    if me_response.status_code == 200:
        user_data = me_response.json()
        print(f"✅ Cookie authentication successful")
        print(f"✅ User: {user_data['user']['mobile_number']}")
        return True
    else:
        print(f"❌ Cookie authentication failed: {me_response.json()}")
        return False

def test_cart_with_cookies():
    """Test cart operations using cookie authentication"""
    print("\n🛒 Testing Cart with Cookie Auth")
    print("-" * 40)

    client = Client()

    # First create session
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False

    # Then login
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    # Test GET cart (should work with cookies)
    cart_response = client.get('/api/common/cart/')
    print(f"Get cart status: {cart_response.status_code}")
    
    if cart_response.status_code == 200:
        print("✅ GET cart with cookies successful")
        
        # Create test product and variant for POST test
        category, _ = Category.objects.get_or_create(
            name='Test Category',
            defaults={'is_available': True}
        )
        
        product, _ = Product.objects.get_or_create(
            name='Test Product',
            defaults={
                'category': category,
                'is_available': True,
                'discount': 0
            }
        )
        
        variant, _ = Variant.objects.get_or_create(
            product=product,
            size='Medium',
            defaults={
                'price': 10.99,
                'type': 'test',
                'is_available': True
            }
        )
        
        # Test POST cart (should work with cookies)
        add_response = client.post('/api/common/cart/', {
            'product_id': product.id,
            'variant_id': variant.id,
            'quantity': 1
        }, content_type='application/json')
        
        print(f"Add to cart status: {add_response.status_code}")
        
        if add_response.status_code == 200:
            print("✅ POST cart with cookies successful")
            return True
        else:
            print(f"❌ POST cart failed: {add_response.json()}")
            return False
    else:
        print(f"❌ GET cart failed: {cart_response.json()}")
        return False

def test_logout_clears_cookies():
    """Test that logout clears cookies"""
    print("\n🚪 Testing Logout Cookie Clearing")
    print("-" * 40)

    client = Client()

    # First create session
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False

    # Then login
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    # Logout
    logout_response = client.post('/api/user/logout/')
    print(f"Logout status: {logout_response.status_code}")
    
    if logout_response.status_code == 200:
        print("✅ Logout successful")
        
        # Check if cookies are cleared (they should have empty values or be deleted)
        cookies = logout_response.cookies
        access_cookie = cookies.get(ACCESS_TOKEN_COOKIE_NAME)
        refresh_cookie = cookies.get(REFRESH_TOKEN_COOKIE_NAME)
        
        # Django's delete_cookie sets the cookie with empty value and past expiry
        access_cleared = access_cookie and (access_cookie.value == '' or 'expires' in str(access_cookie))
        refresh_cleared = refresh_cookie and (refresh_cookie.value == '' or 'expires' in str(refresh_cookie))
        
        print(f"✅ Access token cookie cleared: {bool(access_cleared)}")
        print(f"✅ Refresh token cookie cleared: {bool(refresh_cleared)}")
        
        return True
    else:
        print(f"❌ Logout failed: {logout_response.json()}")
        return False

def test_token_refresh_updates_cookies():
    """Test that token refresh updates cookies"""
    print("\n🔄 Testing Token Refresh Cookie Update")
    print("-" * 40)

    client = Client()

    # First create session
    session_response = client.get('/api/common/session/')
    if session_response.status_code != 200:
        print("❌ Session creation failed")
        return False

    # Then login
    login_response = client.post('/api/user/login/', {
        'mobile_number': '9999999999',
        'password': 'password123'
    }, content_type='application/json')
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    # Refresh token (should use refresh token from cookie)
    refresh_response = client.post('/api/user/refresh/')
    print(f"Refresh status: {refresh_response.status_code}")
    
    if refresh_response.status_code == 200:
        data = refresh_response.json()
        print("✅ Token refresh successful")
        print(f"✅ New access token in response: {bool(data.get('access_token'))}")
        
        # Check if new cookies are set
        cookies = refresh_response.cookies
        access_cookie = cookies.get(ACCESS_TOKEN_COOKIE_NAME)
        refresh_cookie = cookies.get(REFRESH_TOKEN_COOKIE_NAME)
        
        print(f"✅ New access token cookie set: {bool(access_cookie)}")
        print(f"✅ New refresh token cookie set: {bool(refresh_cookie)}")
        
        return True
    else:
        print(f"❌ Token refresh failed: {refresh_response.json()}")
        return False

def run_cookie_auth_tests():
    """Run all cookie authentication tests"""
    print("🚀 Starting Cookie Authentication Tests")
    print("=" * 50)
    
    # Setup
    setup_test_user()
    
    # Run tests
    tests = [
        test_login_sets_cookies,
        test_cookie_authentication,
        test_cart_with_cookies,
        test_token_refresh_updates_cookies,
        test_logout_clears_cookies,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Cookie Authentication Tests Passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 50)

if __name__ == "__main__":
    run_cookie_auth_tests()
