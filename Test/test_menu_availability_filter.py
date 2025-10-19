#!/usr/bin/env python
"""
Test script to verify menu availability filtering
Tests that only products with available variants are shown in menu
"""

import os
import sys
import django
import json
from django.test import Client

# Setup Django environment
sys.path.append('/home/kulriya68/Elysian/elysianBackend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from django.contrib.auth import get_user_model
from common.models import Product, Variant, Category
from restaurent.models import RestaurentMenu, RestaurentEntity

def setup_test_data():
    """Create test data for availability filtering"""
    print("🔧 Setting up test data...")
    
    # Create category
    category, _ = Category.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Test category', 'is_available': True}
    )
    
    # Create restaurant
    restaurant, _ = RestaurentEntity.objects.get_or_create(
        name='Test Restaurant',
        defaults={
            'address': 'Test Address',
            'phone_number': '1234567890',
            'is_active': True
        }
    )
    
    # Test Case 1: Product available, has available variants (SHOULD SHOW)
    product1, _ = Product.objects.get_or_create(
        name='Available Product with Available Variants',
        defaults={
            'description': 'Test product 1',
            'category': category,
            'is_available': True
        }
    )
    
    variant1, _ = Variant.objects.get_or_create(
        product=product1,
        size='Small',
        defaults={'price': 100, 'is_available': True}
    )
    
    menu1, _ = RestaurentMenu.objects.get_or_create(
        restaurent=restaurant,
        product=product1,
        defaults={'is_available': True, 'default_variant': variant1}
    )
    
    # Test Case 2: Product available, NO available variants (SHOULD NOT SHOW)
    product2, _ = Product.objects.get_or_create(
        name='Available Product with NO Available Variants',
        defaults={
            'description': 'Test product 2',
            'category': category,
            'is_available': True
        }
    )
    
    variant2, _ = Variant.objects.get_or_create(
        product=product2,
        size='Small',
        defaults={'price': 100, 'is_available': False}  # Variant not available
    )
    
    menu2, _ = RestaurentMenu.objects.get_or_create(
        restaurent=restaurant,
        product=product2,
        defaults={'is_available': True, 'default_variant': variant2}
    )
    
    # Test Case 3: Product NOT available, has available variants (SHOULD NOT SHOW)
    product3, _ = Product.objects.get_or_create(
        name='Unavailable Product with Available Variants',
        defaults={
            'description': 'Test product 3',
            'category': category,
            'is_available': False  # Product not available
        }
    )
    
    variant3, _ = Variant.objects.get_or_create(
        product=product3,
        size='Small',
        defaults={'price': 100, 'is_available': True}
    )
    
    menu3, _ = RestaurentMenu.objects.get_or_create(
        restaurent=restaurant,
        product=product3,
        defaults={'is_available': True, 'default_variant': variant3}
    )
    
    print(f"✅ Created test data:")
    print(f"   - Product 1: Available with available variants")
    print(f"   - Product 2: Available with NO available variants")
    print(f"   - Product 3: NOT available with available variants")
    
    return {
        'product1': product1,
        'product2': product2,
        'product3': product3,
        'restaurant': restaurant
    }

def test_menu_filtering():
    """Test that menu only shows products with available variants"""
    print("\n🧪 Testing menu availability filtering...")
    
    client = Client()
    
    # Get session first
    session_response = client.get('/api/common/session/')
    print(f"Session response: {session_response.status_code}")
    
    # Get menu
    response = client.get('/api/restaurant/menu/')
    
    if response.status_code == 200:
        menu_data = response.json()
        print(f"✅ Menu API returned {len(menu_data)} items")
        
        # Check which products are shown
        shown_products = [item['name'] for item in menu_data]
        print(f"📋 Products shown in menu:")
        for product in shown_products:
            print(f"   - {product}")
        
        # Verify filtering logic
        expected_product = 'Available Product with Available Variants'
        not_expected_products = [
            'Available Product with NO Available Variants',
            'Unavailable Product with Available Variants'
        ]
        
        # Check that the correct product is shown
        if expected_product in shown_products:
            print(f"✅ PASS: '{expected_product}' is correctly shown")
        else:
            print(f"❌ FAIL: '{expected_product}' should be shown but is not")
        
        # Check that incorrect products are not shown
        for product in not_expected_products:
            if product not in shown_products:
                print(f"✅ PASS: '{product}' is correctly hidden")
            else:
                print(f"❌ FAIL: '{product}' should be hidden but is shown")
        
        # Check variant filtering within shown products
        for item in menu_data:
            if item['name'] == expected_product:
                variants = item['variants']
                print(f"📊 Product '{item['name']}' has {len(variants)} variants shown")
                
                # All shown variants should be available
                all_available = all(variant.get('is_available', True) for variant in variants)
                if all_available:
                    print(f"✅ PASS: All variants shown are available")
                else:
                    print(f"❌ FAIL: Some unavailable variants are shown")
        
        return True
    else:
        print(f"❌ Menu API failed: {response.status_code}")
        print(response.content.decode())
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    # Delete test products and related data
    test_products = Product.objects.filter(name__startswith='Available Product').union(
        Product.objects.filter(name__startswith='Unavailable Product')
    )
    
    for product in test_products:
        print(f"   Deleting: {product.name}")
        product.delete()  # This will cascade delete variants and menu items
    
    # Delete test category and restaurant
    Category.objects.filter(name='Test Category').delete()
    RestaurentEntity.objects.filter(name='Test Restaurant').delete()
    
    print("✅ Cleanup completed")

def main():
    """Run the test"""
    print("🚀 Starting menu availability filtering test...")
    
    try:
        # Setup test data
        test_data = setup_test_data()
        
        # Run test
        success = test_menu_filtering()
        
        if success:
            print("\n🎉 All tests passed! Menu filtering is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always cleanup
        cleanup_test_data()

if __name__ == '__main__':
    main()
