#!/usr/bin/env python3
"""
Comprehensive test suite for Admin Product and Variant Management APIs

This test suite covers:
1. Product CRUD operations (Create, Read, Update, Delete)
2. Variant CRUD operations (Create, Read, Update, Delete)
3. Authentication and authorization testing
4. Input validation testing
5. Error handling testing
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/kulriya68/Elysian/elysianBackend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from common.models import Product, Variant, Category

User = get_user_model()

# Test configuration
BASE_URL = 'http://127.0.0.1:8000'
API_BASE = f'{BASE_URL}/api/common'

def cleanup_test_data():
    """Clean up any existing test data"""
    print("🧹 Cleaning up existing test data...")
    
    # Delete test products and variants
    Product.objects.filter(name__icontains='Test Product').delete()
    Category.objects.filter(name__icontains='Test Category').delete()

def create_test_data():
    """Create test data for the tests"""
    print("🔧 Creating test data...")
    
    # Create test category
    category, created = Category.objects.get_or_create(
        name='Test Category for Admin',
        defaults={
            'description': 'Test category for admin API testing',
            'is_available': True,
            'type': ['food']
        }
    )
    
    print(f"✅ Test category created: {category.name} (ID: {category.id})")
    return category

def get_test_users():
    """Get or create test users"""
    print("👥 Setting up test users...")
    
    # Get admin user
    admin_user = User.objects.filter(mobile_number='9876543210').first()
    if not admin_user:
        print("❌ Admin user not found. Please create admin user first.")
        return None, None
    
    # Get regular user
    regular_user = User.objects.filter(mobile_number='9876543211').first()
    if not regular_user:
        print("❌ Regular user not found. Please create regular user first.")
        return admin_user, None
    
    print(f"✅ Admin user exists: {admin_user.mobile_number}")
    print(f"✅ Regular user exists: {regular_user.mobile_number}")
    
    return admin_user, regular_user

def get_jwt_token(user):
    """Generate JWT token for user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def test_admin_product_apis():
    """Test all admin product APIs"""
    print("\n🧪 Testing Admin Product APIs")
    print("=" * 50)
    
    # Setup
    cleanup_test_data()
    category = create_test_data()
    admin_user, regular_user = get_test_users()
    
    if not admin_user or not regular_user:
        print("❌ Required test users not found")
        return False
    
    admin_token = get_jwt_token(admin_user)
    regular_token = get_jwt_token(regular_user)
    
    # Test data
    product_data = {
        'name': 'Test Product for Admin API',
        'description': 'Test product description',
        'image_urls': ['http://example.com/image1.jpg'],
        'discount': 10.50,
        'is_available': True,
        'category': category.id,
        'sub_category': ['tag1', 'tag2']
    }
    
    created_product_id = None
    
    # Test 1: Admin creating product
    print("\n📝 Test 1: Admin creating product")
    try:
        response = requests.post(
            f'{API_BASE}/admin/products/add/',
            json=product_data,
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 201:
            result = response.json()
            created_product_id = result['product']['id']
            print(f"✅ Admin successfully created product: {result['product']['name']} (ID: {created_product_id})")
        else:
            print(f"❌ Failed to create product: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating product: {e}")
        return False
    
    # Test 2: Regular user trying to create product
    print("\n📝 Test 2: Regular user trying to create product")
    try:
        response = requests.post(
            f'{API_BASE}/admin/products/add/',
            json=product_data,
            headers={'Authorization': f'Bearer {regular_token}'}
        )
        
        if response.status_code == 403:
            print("✅ Regular user correctly denied access")
        else:
            print(f"❌ Regular user should be denied: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing regular user access: {e}")
        return False
    
    # Test 3: Unauthenticated user trying to create product
    print("\n📝 Test 3: Unauthenticated user trying to create product")
    try:
        response = requests.post(
            f'{API_BASE}/admin/products/add/',
            json=product_data
        )
        
        if response.status_code == 401:
            print("✅ Unauthenticated user correctly denied access")
        else:
            print(f"❌ Unauthenticated user should be denied: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing unauthenticated access: {e}")
        return False
    
    # Test 4: Admin getting product details
    print("\n📝 Test 4: Admin getting product details")
    try:
        response = requests.get(
            f'{API_BASE}/admin/products/{created_product_id}/',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Admin successfully retrieved product: {product['name']}")
        else:
            print(f"❌ Failed to get product: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting product: {e}")
        return False
    
    # Test 5: Admin updating product
    print("\n📝 Test 5: Admin updating product")
    try:
        update_data = {
            'name': 'Updated Test Product',
            'discount': 15.00
        }
        
        response = requests.patch(
            f'{API_BASE}/admin/products/{created_product_id}/update/',
            json=update_data,
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin successfully updated product: {result['product']['name']}")
        else:
            print(f"❌ Failed to update product: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error updating product: {e}")
        return False
    
    # Test 6: Admin listing products
    print("\n📝 Test 6: Admin listing products")
    try:
        response = requests.get(
            f'{API_BASE}/admin/products/',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin successfully listed products: {result['count']} products found")
        else:
            print(f"❌ Failed to list products: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing products: {e}")
        return False
    
    # Test 7: Input validation testing
    print("\n📝 Test 7: Input validation testing")
    try:
        invalid_data = {
            'name': '',  # Empty name
            'category': 99999,  # Non-existent category
            'discount': 150  # Invalid discount
        }
        
        response = requests.post(
            f'{API_BASE}/admin/products/add/',
            json=invalid_data,
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 400:
            print("✅ Input validation correctly rejected invalid data")
        else:
            print(f"❌ Should reject invalid data: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        return False
    
    # Test 8: Admin deleting product
    print("\n📝 Test 8: Admin deleting product")
    try:
        response = requests.delete(
            f'{API_BASE}/admin/products/{created_product_id}/delete/',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin successfully deleted product: {result['message']}")
        else:
            print(f"❌ Failed to delete product: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error deleting product: {e}")
        return False
    
    return True

def test_admin_variant_apis():
    """Test all admin variant APIs"""
    print("\n🧪 Testing Admin Variant APIs")
    print("=" * 50)
    
    # Setup - create a product first
    category = Category.objects.filter(name='Test Category for Admin').first()
    admin_user, _ = get_test_users()
    admin_token = get_jwt_token(admin_user)
    
    # Create a test product for variants
    product_data = {
        'name': 'Test Product for Variants',
        'description': 'Test product for variant testing',
        'category': category.id,
        'is_available': True
    }
    
    response = requests.post(
        f'{API_BASE}/admin/products/add/',
        json=product_data,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    if response.status_code != 201:
        print("❌ Failed to create test product for variants")
        return False
    
    product_id = response.json()['product']['id']
    print(f"✅ Created test product for variants (ID: {product_id})")
    
    # Test variant creation
    variant_data = {
        'product': product_id,
        'size': 'Large',
        'price': 25.99,
        'description': 'Large size variant',
        'is_available': True,
        'type': 'size'
    }
    
    created_variant_id = None
    
    # Test 1: Admin creating variant
    print("\n📝 Test 1: Admin creating variant")
    try:
        response = requests.post(
            f'{API_BASE}/admin/variants/add/',
            json=variant_data,
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 201:
            result = response.json()
            created_variant_id = result['variant']['id']
            print(f"✅ Admin successfully created variant: {result['variant']['size']} (ID: {created_variant_id})")
        else:
            print(f"❌ Failed to create variant: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating variant: {e}")
        return False
    
    # Test 2: Admin updating variant
    print("\n📝 Test 2: Admin updating variant")
    try:
        update_data = {
            'price': 29.99,
            'description': 'Updated large size variant'
        }
        
        response = requests.patch(
            f'{API_BASE}/admin/variants/{created_variant_id}/update/',
            json=update_data,
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin successfully updated variant: ${result['variant']['price']}")
        else:
            print(f"❌ Failed to update variant: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error updating variant: {e}")
        return False
    
    # Test 3: Admin listing variants
    print("\n📝 Test 3: Admin listing variants")
    try:
        response = requests.get(
            f'{API_BASE}/admin/variants/?product={product_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin successfully listed variants: {result['count']} variants found")
        else:
            print(f"❌ Failed to list variants: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing variants: {e}")
        return False
    
    # Test 4: Duplicate variant prevention
    print("\n📝 Test 4: Testing duplicate variant prevention")
    try:
        response = requests.post(
            f'{API_BASE}/admin/variants/add/',
            json=variant_data,  # Same data as before
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 400:
            print("✅ Duplicate variant correctly prevented")
        else:
            print(f"❌ Should prevent duplicate variants: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing duplicate prevention: {e}")
        return False
    
    # Test 5: Admin deleting variant
    print("\n📝 Test 5: Admin deleting variant")
    try:
        response = requests.delete(
            f'{API_BASE}/admin/variants/{created_variant_id}/delete/',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin successfully deleted variant: {result['message']}")
        else:
            print(f"❌ Failed to delete variant: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error deleting variant: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Admin Product and Variant Management APIs")
    print("=" * 60)
    
    try:
        # Test product APIs
        product_tests_passed = test_admin_product_apis()
        
        # Test variant APIs
        variant_tests_passed = test_admin_variant_apis()
        
        # Final cleanup
        cleanup_test_data()
        
        if product_tests_passed and variant_tests_passed:
            print("\n🎉 All admin API tests passed!")
            print("\n✅ Admin Product and Variant Management APIs test completed successfully!")
            return True
        else:
            print("\n❌ Some tests failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
