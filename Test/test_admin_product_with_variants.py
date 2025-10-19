#!/usr/bin/env python
"""
Test script for admin product creation and update with variant management
"""

import os
import sys
import django
import json

# Setup Django
sys.path.append('/home/kulriya68/Elysian/elysianBackend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from common.models import Product, Variant, Category
from rest_framework_simplejwt.tokens import AccessToken

def get_admin_token():
    """Get JWT token for admin user"""
    User = get_user_model()
    admin_user, created = User.objects.get_or_create(
        mobile_number='9999999999',
        defaults={
            'name': 'Admin User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    if not admin_user.is_staff:
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
    
    token = AccessToken.for_user(admin_user)
    return str(token)

def test_add_product_with_variants():
    """Test adding a new product with variants"""
    print("🧪 Testing: Add Product with Variants")
    
    client = Client()
    token = get_admin_token()
    
    # Ensure category exists
    category, created = Category.objects.get_or_create(
        id=4,
        defaults={
            'name': 'Beverages',
            'description': 'Hot and cold beverages',
            'is_available': True,
            'type': 'beverage'
        }
    )
    
    # Test data matching the user's example
    test_data = {
        "name": "chai",
        "description": "chai masala with milk",
        "discount": "0",
        "is_available": True,
        "category": 4,
        "sub_category": ["beverages"],
        "variants": [
            {
                "size": "regular",
                "price": "30",
                "description": "approx 150 ml",
                "is_available": True,
                "type": ""
            }
        ]
    }
    
    response = client.post(
        '/api/common/admin/products/add/',
        data=json.dumps(test_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        product_data = response.json()['product']
        product_id = product_data['id']
        
        # Verify product was created correctly
        product = Product.objects.get(id=product_id)
        print(f"✅ Product created: {product.name}")
        print(f"   Description: {product.description}")
        print(f"   Category: {product.category.name}")
        print(f"   Sub-categories: {product.sub_category}")
        print(f"   Discount: {product.discount}")
        print(f"   Available: {product.is_available}")
        
        # Verify variants were created
        variants = product.variants.all()
        print(f"   Variants count: {variants.count()}")
        for variant in variants:
            print(f"     - {variant.size}: ₹{variant.price} ({variant.description})")
        
        return product_id
    else:
        print(f"❌ Failed to create product")
        return None

def test_update_product_with_variants(product_id):
    """Test updating a product with new variants"""
    print(f"\n🧪 Testing: Update Product {product_id} with Variants")
    
    client = Client()
    token = get_admin_token()
    
    # Test data with multiple variants
    update_data = {
        "name": "Masala Chai",
        "description": "Premium masala chai with special spices",
        "discount": "5",
        "is_available": True,
        "category": 4,
        "sub_category": ["beverages", "hot"],
        "variants": [
            {
                "size": "small",
                "price": "25",
                "description": "approx 100 ml",
                "is_available": True,
                "type": "volume"
            },
            {
                "size": "regular",
                "price": "35",
                "description": "approx 150 ml",
                "is_available": True,
                "type": "volume"
            },
            {
                "size": "large",
                "price": "45",
                "description": "approx 200 ml",
                "is_available": True,
                "type": "volume"
            }
        ]
    }
    
    response = client.put(
        f'/api/common/admin/products/{product_id}/update/',
        data=json.dumps(update_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        # Verify product was updated correctly
        product = Product.objects.get(id=product_id)
        print(f"✅ Product updated: {product.name}")
        print(f"   Description: {product.description}")
        print(f"   Discount: {product.discount}")
        
        # Verify variants were replaced
        variants = product.variants.all()
        print(f"   Variants count: {variants.count()}")
        for variant in variants:
            print(f"     - {variant.size}: ₹{variant.price} ({variant.description}) [{variant.type}]")
        
        return True
    else:
        print(f"❌ Failed to update product")
        return False

def test_validation_errors():
    """Test validation errors"""
    print(f"\n🧪 Testing: Validation Errors")
    
    client = Client()
    token = get_admin_token()
    
    # Test 1: No variants
    test_data = {
        "name": "Invalid Product",
        "category": 4,
        "variants": []
    }
    
    response = client.post(
        '/api/common/admin/products/add/',
        data=json.dumps(test_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"Test 1 - No variants:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 2: Invalid price
    test_data = {
        "name": "Invalid Product 2",
        "category": 4,
        "variants": [
            {
                "size": "regular",
                "price": "-10",
                "is_available": True
            }
        ]
    }
    
    response = client.post(
        '/api/common/admin/products/add/',
        data=json.dumps(test_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"\nTest 2 - Invalid price:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("🚀 Starting Admin Product with Variants Tests")
    print("=" * 50)
    
    try:
        # Test 1: Add product with variants
        product_id = test_add_product_with_variants()
        
        if product_id:
            # Test 2: Update product with variants
            test_update_product_with_variants(product_id)
        
        # Test 3: Validation errors
        test_validation_errors()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
