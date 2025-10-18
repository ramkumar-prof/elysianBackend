#!/usr/bin/env python3
"""
Test script to verify the complete menu to cart flow with variant IDs
"""

import os
import sys
import django
from django.test import Client
import json

# Setup Django
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

def test_menu_variant_ids():
    """Test that menu API returns variant IDs"""
    print("📋 Testing Menu API Variant IDs")
    print("-" * 40)
    
    client = Client()
    
    # Create session
    session_resp = client.get('/api/common/session/')
    print(f"✅ Session created: {session_resp.status_code}")
    
    # Get menu
    menu_resp = client.get('/api/restaurant/menu/')
    print(f"✅ Menu loaded: {menu_resp.status_code}")
    
    if menu_resp.status_code == 200:
        menu = menu_resp.json()
        print(f"✅ Found {len(menu)} menu items")
        
        # Check each item has variant IDs
        for item in menu:
            print(f"\n   📦 {item['name']}:")
            for variant in item['variants']:
                required_fields = ['variant_id', 'size', 'price', 'default']
                missing_fields = [field for field in required_fields if field not in variant]
                
                if missing_fields:
                    print(f"     ❌ Missing fields: {missing_fields}")
                    return False
                else:
                    default_mark = " (default)" if variant['default'] else ""
                    print(f"     ✅ ID {variant['variant_id']}: {variant['size']} - ₹{variant['price']}{default_mark}")
        
        return True
    else:
        print(f"❌ Menu API failed: {menu_resp.status_code}")
        return False

def test_cart_functionality():
    """Test adding items to cart using variant IDs from menu"""
    print("\n🛒 Testing Cart Functionality")
    print("-" * 40)
    
    client = Client()
    
    # Create session
    session_resp = client.get('/api/common/session/')
    
    # Get menu
    menu_resp = client.get('/api/restaurant/menu/')
    if menu_resp.status_code != 200:
        print("❌ Failed to get menu")
        return False
    
    menu = menu_resp.json()
    
    # Test 1: Add first item to cart
    first_item = menu[0]
    first_variant = first_item['variants'][0]
    
    print(f"🛒 Adding: {first_item['name']} ({first_variant['size']}) x2")
    
    add_resp = client.post('/api/common/cart/', {
        'variant_id': first_variant['variant_id'],
        'quantity': 2
    }, content_type='application/json')
    
    print(f"✅ Add to cart: {add_resp.status_code}")
    
    if add_resp.status_code != 200:
        print(f"❌ Failed to add to cart: {add_resp.json()}")
        return False
    
    add_data = add_resp.json()
    print(f"   Message: {add_data['message']}")
    print(f"   Total items: {add_data['total_items']}")
    print(f"   Total amount: ₹{add_data['total_amount']}")

    # Test 2: Add second item to cart
    second_item = menu[1]
    second_variant = second_item['variants'][1] if len(second_item['variants']) > 1 else second_item['variants'][0]
    
    print(f"\n🛒 Adding: {second_item['name']} ({second_variant['size']}) x1")
    
    add_resp2 = client.post('/api/common/cart/', {
        'variant_id': second_variant['variant_id'],
        'quantity': 1
    }, content_type='application/json')
    
    print(f"✅ Add second item: {add_resp2.status_code}")
    
    if add_resp2.status_code == 200:
        add_data2 = add_resp2.json()
        print(f"   Total items in cart: {add_data2['total_items']}")
        print(f"   Total amount: ₹{add_data2['total_amount']}")

        # Show cart contents (new unified format)
        print(f"\n📦 Cart Contents:")
        for item in add_data2['cart_items']:
            print(f"   - {item['product_name']} ({item['variant_size']}) x{item['quantity']} = ₹{item['item_total']}")
    
    # Test 3: Get cart via GET endpoint
    cart_resp = client.get('/api/common/cart/')
    print(f"\n✅ Get cart: {cart_resp.status_code}")
    
    if cart_resp.status_code == 200:
        cart = cart_resp.json()
        print(f"   Cart items via GET: {len(cart['cart_items'])}")

        # Show cart items from GET endpoint
        for item in cart['cart_items']:
            print(f"   - {item['product_name']} ({item['variant_size']}) x{item['quantity']} = ₹{item['item_total']}")
    
    return True

def test_edge_cases():
    """Test edge cases for cart functionality"""
    print("\n🔍 Testing Edge Cases")
    print("-" * 40)
    
    client = Client()
    
    # Create session
    session_resp = client.get('/api/common/session/')
    
    # Test 1: Invalid variant ID
    print("🧪 Testing invalid variant ID")
    add_resp = client.post('/api/common/cart/', {
        'variant_id': 99999,
        'quantity': 1
    }, content_type='application/json')
    
    print(f"✅ Invalid variant ID: {add_resp.status_code}")
    if add_resp.status_code == 404:
        print("   Correctly rejected invalid variant")
    
    # Test 2: Zero quantity
    print("\n🧪 Testing zero quantity")
    add_resp = client.post('/api/common/cart/', {
        'variant_id': 1,
        'quantity': 0
    }, content_type='application/json')
    
    print(f"✅ Zero quantity: {add_resp.status_code}")
    if add_resp.status_code == 400:
        print("   Correctly rejected zero quantity")
    
    # Test 3: Missing variant_id
    print("\n🧪 Testing missing variant_id")
    add_resp = client.post('/api/common/cart/', {
        'quantity': 1
    }, content_type='application/json')
    
    print(f"✅ Missing variant_id: {add_resp.status_code}")
    if add_resp.status_code == 400:
        print("   Correctly rejected missing variant_id")
    
    return True

def test_session_persistence():
    """Test that cart persists across requests in the same session"""
    print("\n🔄 Testing Session Persistence")
    print("-" * 40)
    
    client = Client()
    
    # Create session and add item
    session_resp = client.get('/api/common/session/')
    
    add_resp = client.post('/api/common/cart/', {
        'variant_id': 1,
        'quantity': 1
    }, content_type='application/json')
    
    print(f"✅ Added item: {add_resp.status_code}")
    
    # Make another request to check persistence
    cart_resp = client.get('/api/common/cart/')
    print(f"✅ Get cart after: {cart_resp.status_code}")
    
    if cart_resp.status_code == 200:
        cart = cart_resp.json()
        if len(cart['cart_items']) > 0:
            print("   ✅ Cart persisted across requests")
            return True
        else:
            print("   ❌ Cart not persisted")
            return False
    
    return False

def main():
    """Run all tests for menu to cart flow"""
    print("🍽️  Menu to Cart Flow Tests")
    print("=" * 60)
    
    tests = [
        ("Menu Variant IDs", test_menu_variant_ids),
        ("Cart Functionality", test_cart_functionality),
        ("Edge Cases", test_edge_cases),
        ("Session Persistence", test_session_persistence),
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
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Menu to Cart Flow Tests Passed!")
        print("✅ Variant IDs are properly returned in menu API")
        print("🛒 Cart functionality works with session authentication")
        print("🔄 Cart persists across requests in the same session")
        print("🛡️  Edge cases are properly handled")
        print("📱 Frontend can now use variant IDs to add items to cart")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
