#!/usr/bin/env python3
"""
Test script for admin add menu item API
Tests the new admin-only endpoint for adding menu items to restaurants
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
import json

# Add the project root to Python path
sys.path.append('/home/kulriya68/Elysian/elysianBackend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from common.models import Product, RestaurentEntity, Variant, Category
from restaurent.models import RestaurentMenu
from user.models import CustomUser

def create_test_data():
    """Create test data for the admin API test"""
    print("🔧 Creating test data...")
    
    # Create a category
    category, created = Category.objects.get_or_create(
        name="Test Category",
        defaults={
            'description': 'Test category for admin API',
            'type': 'food',
            'is_available': True
        }
    )
    
    # Create a restaurant
    restaurant, created = RestaurentEntity.objects.get_or_create(
        name="Test Restaurant",
        defaults={
            'description': 'Test restaurant for admin API',
            'address': 'Test Address',
            'is_available': True
        }
    )
    
    # Create a product
    product, created = Product.objects.get_or_create(
        name="Test Product for Admin",
        defaults={
            'description': 'Test product for admin API',
            'category': category,
            'image_urls': ['test.jpg'],
            'discount': 10.00,
            'is_available': True,
            'sub_category': ['test']
        }
    )
    
    # Create a variant for the product
    variant, created = Variant.objects.get_or_create(
        product=product,
        size="Medium",
        defaults={
            'price': 299.99,
            'description': 'Medium size test product',
            'is_available': True,
            'type': 'size'
        }
    )
    
    print(f"✅ Test data created:")
    print(f"   - Category: {category.name} (ID: {category.id})")
    print(f"   - Restaurant: {restaurant.name} (ID: {restaurant.id})")
    print(f"   - Product: {product.name} (ID: {product.id})")
    print(f"   - Variant: {variant.size} (ID: {variant.id})")
    
    return {
        'category': category,
        'restaurant': restaurant,
        'product': product,
        'variant': variant
    }

def create_admin_user():
    """Create an admin user for testing"""
    User = get_user_model()
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        mobile_number='9876543210',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@test.com',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Admin user created: {admin_user.mobile_number}")
    else:
        print(f"✅ Admin user exists: {admin_user.mobile_number}")
    
    return admin_user

def create_regular_user():
    """Create a regular user for testing"""
    User = get_user_model()
    
    # Create regular user
    regular_user, created = User.objects.get_or_create(
        mobile_number='9876543211',
        defaults={
            'first_name': 'Regular',
            'last_name': 'User',
            'email': 'user@test.com',
            'is_staff': False,
            'is_superuser': False,
            'is_active': True
        }
    )
    
    if created:
        regular_user.set_password('user123')
        regular_user.save()
        print(f"✅ Regular user created: {regular_user.mobile_number}")
    else:
        print(f"✅ Regular user exists: {regular_user.mobile_number}")
    
    return regular_user

def get_jwt_token(user):
    """Get JWT token for a user"""
    client = Client()
    
    # First create a session
    session_resp = client.get('/api/common/session/')
    if session_resp.status_code != 200:
        print(f"❌ Failed to create session: {session_resp.status_code}")
        return None
    
    # Login to get JWT token
    login_data = {
        'mobile_number': user.mobile_number,
        'password': 'admin123' if user.is_staff else 'user123'
    }
    
    login_resp = client.post('/api/user/login/', data=login_data)
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.status_code}")
        print(f"Response: {login_resp.content.decode()}")
        return None
    
    # Extract access token from cookies
    access_token = None
    if 'access_token' in login_resp.cookies:
        access_token = login_resp.cookies['access_token'].value

    # If not found in cookies, try to get from response data
    if not access_token:
        try:
            response_data = login_resp.json()
            access_token = response_data.get('access_token')
        except:
            pass
    
    if not access_token:
        print("❌ No access token found in login response")
        return None
    
    print(f"✅ JWT token obtained for {user.mobile_number}")
    return access_token

def test_admin_add_menu_item():
    """Test the admin add menu item API"""
    print("\n🧪 Testing Admin Add Menu Item API")
    print("=" * 50)

    # Clean up any existing menu items for our test data
    print("🧹 Cleaning up existing test data...")
    RestaurentMenu.objects.filter(
        product__name__contains="Test Product"
    ).delete()

    # Create test data
    test_data = create_test_data()
    admin_user = create_admin_user()
    regular_user = create_regular_user()
    
    # Get JWT tokens
    admin_token = get_jwt_token(admin_user)
    regular_token = get_jwt_token(regular_user)
    
    if not admin_token or not regular_token:
        print("❌ Failed to get JWT tokens")
        return False
    
    client = Client()
    
    # Test 1: Admin user can add menu item
    print("\n📝 Test 1: Admin user adding menu item")
    menu_data = {
        'product_id': test_data['product'].id,
        'restaurent_id': test_data['restaurant'].id,
        'is_available': True,
        'is_veg': True,
        'default_variant_id': test_data['variant'].id
    }
    
    response = client.post(
        '/api/restaurant/admin/menu/add/',
        data=json.dumps(menu_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response.status_code == 201:
        print("✅ Admin successfully added menu item")
        response_data = response.json()
        print(f"   Menu item: {response_data['menu_item']['name']}")
    else:
        print(f"❌ Admin failed to add menu item: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        return False
    
    # Test 2: Regular user cannot add menu item
    print("\n📝 Test 2: Regular user trying to add menu item")
    
    # Create another product for this test
    category = test_data['category']
    product2, created = Product.objects.get_or_create(
        name="Test Product 2 for Admin",
        defaults={
            'description': 'Second test product for admin API',
            'category': category,
            'image_urls': ['test2.jpg'],
            'discount': 5.00,
            'is_available': True,
            'sub_category': ['test2']
        }
    )
    
    menu_data2 = {
        'product_id': product2.id,
        'restaurent_id': test_data['restaurant'].id,
        'is_available': True,
        'is_veg': False
    }
    
    response = client.post(
        '/api/restaurant/admin/menu/add/',
        data=json.dumps(menu_data2),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {regular_token}'
    )
    
    if response.status_code == 403:
        print("✅ Regular user correctly denied access")
    else:
        print(f"❌ Regular user should be denied but got: {response.status_code}")
        return False
    
    # Test 3: Unauthenticated user cannot add menu item
    print("\n📝 Test 3: Unauthenticated user trying to add menu item")
    
    response = client.post(
        '/api/restaurant/admin/menu/add/',
        data=json.dumps(menu_data2),
        content_type='application/json'
    )
    
    if response.status_code == 401:
        print("✅ Unauthenticated user correctly denied access")
    else:
        print(f"❌ Unauthenticated user should be denied but got: {response.status_code}")
        return False
    
    # Test 4: Try to add duplicate menu item
    print("\n📝 Test 4: Testing duplicate menu item prevention")

    # Try to add the same menu item again
    duplicate_data = {
        'product_id': test_data['product'].id,
        'restaurent_id': test_data['restaurant'].id,
        'is_available': False,  # Different values to ensure it's not just a cache issue
        'is_veg': False,
        'default_variant_id': test_data['variant'].id
    }

    response = client.post(
        '/api/restaurant/admin/menu/add/',
        data=json.dumps(duplicate_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )

    if response.status_code == 400:
        response_data = response.json()
        if "already in the restaurant's menu" in str(response_data):
            print("✅ Duplicate menu item correctly prevented")
        else:
            print(f"❌ Wrong error message for duplicate: {response_data}")
            return False
    else:
        print(f"❌ Duplicate should be prevented but got: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        return False

    # Test 5: Verify menu item appears in menu list
    print("\n📝 Test 5: Verifying menu item appears in menu list")

    # Create a new client with session for menu access
    menu_client = Client()
    session_resp = menu_client.get('/api/common/session/')
    if session_resp.status_code != 200:
        print(f"❌ Failed to create session for menu check: {session_resp.status_code}")
        return False

    menu_response = menu_client.get('/api/restaurant/menu/')
    if menu_response.status_code == 200:
        menu_items = menu_response.json()
        added_item = None
        for item in menu_items:
            if item['product_id'] == test_data['product'].id:
                added_item = item
                break
        
        if added_item:
            print("✅ Menu item appears in menu list")
            print(f"   Item: {added_item['name']} (Veg: {added_item['veg']})")
        else:
            print("❌ Menu item not found in menu list")
            return False
    else:
        print(f"❌ Failed to get menu list: {menu_response.status_code}")
        return False
    
    print("\n🎉 All admin add menu item tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_admin_add_menu_item()
        if success:
            print("\n✅ Admin Add Menu Item API test completed successfully!")
        else:
            print("\n❌ Admin Add Menu Item API test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
