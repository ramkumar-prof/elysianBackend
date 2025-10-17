#!/usr/bin/env python3
"""
Test script for the new Cart API endpoints
Run this after applying migrations to test the cart functionality
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
from rest_framework.authtoken.models import Token

User = get_user_model()

def setup_test_data():
    """Create test data for cart API testing"""
    print("🔧 Setting up test data...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        mobile_number='9999999999',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
    )
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    
    # Create test category
    category, created = Category.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Test category for API testing', 'is_available': True}
    )
    
    # Create test products
    product1, created = Product.objects.get_or_create(
        name='Test Pizza',
        defaults={
            'description': 'Test pizza for API testing',
            'category': category,
            'discount': 10.00,
            'is_available': True
        }
    )
    
    product2, created = Product.objects.get_or_create(
        name='Test Burger',
        defaults={
            'description': 'Test burger for API testing',
            'category': category,
            'discount': 5.00,
            'is_available': True
        }
    )
    
    # Create test variants
    variant1, created = Variant.objects.get_or_create(
        product=product1,
        size='Large',
        defaults={
            'price': 15.99,
            'type': 'pizza',
            'is_available': True
        }
    )
    
    variant2, created = Variant.objects.get_or_create(
        product=product1,
        size='Medium',
        defaults={
            'price': 12.99,
            'type': 'pizza',
            'is_available': True
        }
    )
    
    variant3, created = Variant.objects.get_or_create(
        product=product2,
        size='Regular',
        defaults={
            'price': 8.99,
            'type': 'burger',
            'is_available': True
        }
    )
    
    print(f"✅ Test data created:")
    print(f"   User: {user.mobile_number}")
    print(f"   Token: {token.key}")
    print(f"   Products: {product1.name}, {product2.name}")
    print(f"   Variants: {variant1.size}, {variant2.size}, {variant3.size}")
    
    return user, token, product1, product2, variant1, variant2, variant3

def test_get_empty_cart(client, token):
    """Test GET /api/common/cart/ with empty cart"""
    print("\n📋 Testing GET empty cart...")
    
    response = client.get('/api/common/cart/', HTTP_AUTHORIZATION=f'Bearer {token.key}')
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['cart_items'] == []
    assert data['total_items'] == 0
    assert data['total_amount'] == 0
    
    print("✅ Empty cart test passed")

def test_add_to_cart(client, token, product1, variant1):
    """Test POST /api/common/cart/ to add item"""
    print("\n📦 Testing POST add to cart...")
    
    payload = {
        'product_id': product1.id,
        'variant_id': variant1.id,
        'quantity': 2
    }
    
    response = client.post(
        '/api/common/cart/',
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token.key}'
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == 'Item added to cart successfully'
    assert len(data['cart_items']) == 1
    
    cart_item = data['cart_items'][0]
    assert cart_item['productId'] == product1.id
    assert cart_item['productName'] == product1.name
    assert len(cart_item['selectedVariant']) == 1
    assert cart_item['selectedVariant'][0]['quantity'] == 2
    
    print("✅ Add to cart test passed")

def test_add_existing_item(client, token, product1, variant1):
    """Test adding same item again (should update quantity)"""
    print("\n🔄 Testing POST add existing item...")
    
    payload = {
        'product_id': product1.id,
        'variant_id': variant1.id,
        'quantity': 1
    }
    
    response = client.post(
        '/api/common/cart/',
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token.key}'
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    
    cart_item = data['cart_items'][0]
    assert cart_item['selectedVariant'][0]['quantity'] == 3  # 2 + 1
    
    print("✅ Add existing item test passed")

def test_add_multiple_variants(client, token, product1, variant2):
    """Test adding different variant of same product"""
    print("\n🍕 Testing POST add different variant...")
    
    payload = {
        'product_id': product1.id,
        'variant_id': variant2.id,
        'quantity': 1
    }
    
    response = client.post(
        '/api/common/cart/',
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token.key}'
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    
    cart_item = data['cart_items'][0]
    assert len(cart_item['selectedVariant']) == 2  # Large + Medium
    
    print("✅ Multiple variants test passed")

def test_add_different_product(client, token, product2, variant3):
    """Test adding different product"""
    print("\n🍔 Testing POST add different product...")
    
    payload = {
        'product_id': product2.id,
        'variant_id': variant3.id,
        'quantity': 1
    }
    
    response = client.post(
        '/api/common/cart/',
        data=json.dumps(payload),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token.key}'
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data['cart_items']) == 2  # Pizza + Burger
    
    print("✅ Different product test passed")

def test_get_populated_cart(client, token):
    """Test GET /api/common/cart/ with items"""
    print("\n📋 Testing GET populated cart...")
    
    response = client.get('/api/common/cart/', HTTP_AUTHORIZATION=f'Bearer {token.key}')
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data['cart_items']) > 0
    assert data['total_items'] > 0
    assert data['total_amount'] > 0
    
    print("✅ Populated cart test passed")

def test_error_cases(client, token):
    """Test error cases"""
    print("\n❌ Testing error cases...")
    
    # Test missing product_id
    response = client.post(
        '/api/common/cart/',
        data=json.dumps({'variant_id': 1, 'quantity': 1}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token.key}'
    )
    assert response.status_code == 400
    print("✅ Missing product_id error test passed")
    
    # Test invalid product_id
    response = client.post(
        '/api/common/cart/',
        data=json.dumps({'product_id': 99999, 'variant_id': 1, 'quantity': 1}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token.key}'
    )
    assert response.status_code == 404
    print("✅ Invalid product_id error test passed")
    
    # Test no authentication
    response = client.post(
        '/api/common/cart/',
        data=json.dumps({'product_id': 1, 'variant_id': 1, 'quantity': 1}),
        content_type='application/json'
    )
    assert response.status_code == 401
    print("✅ No authentication error test passed")

def run_tests():
    """Run all cart API tests"""
    print("🚀 Starting Cart API Tests")
    print("=" * 50)
    
    # Setup
    user, token, product1, product2, variant1, variant2, variant3 = setup_test_data()
    client = Client()
    
    # Clear any existing cart items for clean test
    Cart.objects.filter(user=user).delete()
    
    try:
        # Run tests in sequence
        test_get_empty_cart(client, token)
        test_add_to_cart(client, token, product1, variant1)
        test_add_existing_item(client, token, product1, variant1)
        test_add_multiple_variants(client, token, product1, variant2)
        test_add_different_product(client, token, product2, variant3)
        test_get_populated_cart(client, token)
        test_error_cases(client, token)
        
        print("\n🎉 All Cart API Tests Passed!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        print("=" * 50)
    except Exception as e:
        print(f"\n💥 Unexpected Error: {e}")
        print("=" * 50)

if __name__ == "__main__":
    run_tests()
