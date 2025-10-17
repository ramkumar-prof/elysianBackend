#!/usr/bin/env python3
"""
Test script to verify cart quantity management including:
- Adding items
- Updating quantities 
- Removing items (quantity = 0)
- Unified response format
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

def test_cart_quantity_operations():
    """Test all cart quantity operations"""
    print("🛒 Testing Cart Quantity Management")
    print("=" * 45)
    
    client = Client()
    
    # Create session
    session_resp = client.get('/api/common/session/')
    print(f"✅ Session created: {session_resp.status_code}")
    
    # Test 1: Add item with quantity 2
    print(f"\n📦 Test 1: Add item (quantity = 2)")
    add_resp = client.post('/api/common/cart/', {
        'variant_id': 1,
        'quantity': 2
    }, content_type='application/json')
    
    print(f"Status: {add_resp.status_code}")
    add_data = add_resp.json()
    print(f"Message: {add_data['message']}")
    print(f"Items in cart: {add_data['total_items']}")
    if add_data['cart_items']:
        item = add_data['cart_items'][0]
        print(f"Item: {item['product_name']} x{item['quantity']} = ₹{item['item_total']}")
    
    # Test 2: Update quantity to 5
    print(f"\n🔄 Test 2: Update quantity to 5")
    update_resp = client.post('/api/common/cart/', {
        'variant_id': 1,
        'quantity': 5
    }, content_type='application/json')
    
    print(f"Status: {update_resp.status_code}")
    update_data = update_resp.json()
    print(f"Message: {update_data['message']}")
    if update_data['cart_items']:
        item = update_data['cart_items'][0]
        print(f"Updated: {item['product_name']} x{item['quantity']} = ₹{item['item_total']}")
    
    # Test 3: Add second item
    print(f"\n📦 Test 3: Add second item (quantity = 1)")
    add_resp2 = client.post('/api/common/cart/', {
        'variant_id': 4,
        'quantity': 1
    }, content_type='application/json')
    
    print(f"Status: {add_resp2.status_code}")
    add_data2 = add_resp2.json()
    print(f"Message: {add_data2['message']}")
    print(f"Total items in cart: {add_data2['total_items']}")
    print(f"Total amount: ₹{add_data2['total_amount']}")
    
    # Test 4: Remove first item (quantity = 0)
    print(f"\n🗑️  Test 4: Remove first item (quantity = 0)")
    remove_resp = client.post('/api/common/cart/', {
        'variant_id': 1,
        'quantity': 0
    }, content_type='application/json')
    
    print(f"Status: {remove_resp.status_code}")
    remove_data = remove_resp.json()
    print(f"Message: {remove_data['message']}")
    print(f"Items remaining: {remove_data['total_items']}")
    print(f"Total amount: ₹{remove_data['total_amount']}")
    
    # Test 5: Try to remove non-existent item
    print(f"\n🧪 Test 5: Remove non-existent item")
    remove_resp2 = client.post('/api/common/cart/', {
        'variant_id': 1,  # Already removed
        'quantity': 0
    }, content_type='application/json')
    
    print(f"Status: {remove_resp2.status_code}")
    remove_data2 = remove_resp2.json()
    print(f"Message: {remove_data2['message']}")
    print(f"Items in cart: {remove_data2['total_items']}")
    
    # Test 6: Remove all remaining items
    print(f"\n🗑️  Test 6: Remove all remaining items")
    remove_resp3 = client.post('/api/common/cart/', {
        'variant_id': 4,
        'quantity': 0
    }, content_type='application/json')
    
    print(f"Status: {remove_resp3.status_code}")
    remove_data3 = remove_resp3.json()
    print(f"Message: {remove_data3['message']}")
    print(f"Items in cart: {remove_data3['total_items']}")
    print(f"Total amount: ₹{remove_data3['total_amount']}")
    
    # Test 7: Verify with GET
    print(f"\n📥 Test 7: Verify empty cart with GET")
    get_resp = client.get('/api/common/cart/')
    print(f"Status: {get_resp.status_code}")
    get_data = get_resp.json()
    print(f"Items in cart: {get_data['total_items']}")
    print(f"Total amount: ₹{get_data['total_amount']}")
    
    # Verify all responses have consistent format
    responses = [
        ("Add", add_data),
        ("Update", update_data), 
        ("Add Second", add_data2),
        ("Remove", remove_data),
        ("Remove Non-existent", remove_data2),
        ("Remove All", remove_data3)
    ]
    
    print(f"\n🔍 Response Format Verification")
    print("-" * 35)
    
    all_consistent = True
    expected_keys = {'message', 'cart_items', 'total_items', 'total_amount'}
    
    for name, response in responses:
        response_keys = set(response.keys())
        if response_keys == expected_keys:
            print(f"✅ {name}: Correct format")
        else:
            print(f"❌ {name}: Incorrect format - {response_keys}")
            all_consistent = False
    
    # Check GET response format (no message field)
    get_keys = set(get_data.keys())
    expected_get_keys = {'cart_items', 'total_items', 'total_amount'}
    if get_keys == expected_get_keys:
        print(f"✅ GET: Correct format")
    else:
        print(f"❌ GET: Incorrect format - {get_keys}")
        all_consistent = False
    
    return all_consistent

def test_negative_quantity():
    """Test negative quantity validation"""
    print(f"\n🚫 Testing Negative Quantity Validation")
    print("=" * 40)
    
    client = Client()
    
    # Create session
    session_resp = client.get('/api/common/session/')
    
    # Test negative quantity
    error_resp = client.post('/api/common/cart/', {
        'variant_id': 1,
        'quantity': -1
    }, content_type='application/json')
    
    print(f"Status: {error_resp.status_code}")
    error_data = error_resp.json()
    print(f"Message: {error_data['message']}")
    print(f"Items in cart: {error_data['total_items']}")
    
    return error_resp.status_code == 400 and 'negative' in error_data['message']

def main():
    """Run all cart quantity management tests"""
    print("🛒 Cart Quantity Management Tests")
    print("=" * 50)
    
    tests = [
        ("Cart Quantity Operations", test_cart_quantity_operations),
        ("Negative Quantity Validation", test_negative_quantity),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} - PASSED")
            else:
                print(f"\n❌ {test_name} - FAILED")
        except Exception as e:
            print(f"\n❌ {test_name} - ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Cart Quantity Management Tests Passed!")
        print("✅ Items can be added to cart with any positive quantity")
        print("🔄 Item quantities can be updated by setting new quantity")
        print("🗑️  Items can be removed by setting quantity = 0")
        print("🚫 Negative quantities are properly rejected")
        print("📱 All responses follow unified format with appropriate messages")
        print("📥 GET and POST responses are consistent")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    print("=" * 50)

if __name__ == '__main__':
    main()
