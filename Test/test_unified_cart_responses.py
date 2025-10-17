#!/usr/bin/env python3
"""
Test script to verify unified cart response format between GET and POST endpoints
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

def test_response_format_consistency():
    """Test that POST and GET cart endpoints have consistent response formats"""
    print("🔄 Testing Cart Response Format Consistency")
    print("=" * 50)
    
    client = Client()
    
    # Create session
    session_resp = client.get('/api/common/session/')
    print(f"✅ Session created: {session_resp.status_code}")
    
    # Test 1: Add item to cart (POST)
    print(f"\n📤 POST /api/common/cart/ - Add Item")
    add_resp = client.post('/api/common/cart/', {
        'variant_id': 1,
        'quantity': 2
    }, content_type='application/json')
    
    print(f"Status: {add_resp.status_code}")
    add_data = add_resp.json()
    
    # Test 2: Get cart (GET)
    print(f"\n📥 GET /api/common/cart/ - Get Cart")
    get_resp = client.get('/api/common/cart/')
    
    print(f"Status: {get_resp.status_code}")
    get_data = get_resp.json()
    
    # Test 3: Error response (POST)
    print(f"\n❌ POST /api/common/cart/ - Error Case")
    error_resp = client.post('/api/common/cart/', {
        'variant_id': 99999,
        'quantity': 1
    }, content_type='application/json')
    
    print(f"Status: {error_resp.status_code}")
    error_data = error_resp.json()
    
    # Analysis
    print(f"\n🔍 Response Structure Analysis")
    print("-" * 30)
    
    success_keys = set(add_data.keys())
    get_keys = set(get_data.keys())
    error_keys = set(error_data.keys())
    
    print(f"POST Success: {sorted(success_keys)}")
    print(f"GET Response: {sorted(get_keys)}")
    print(f"POST Error:   {sorted(error_keys)}")
    
    # Check consistency
    common_keys = success_keys & get_keys & error_keys
    post_only = success_keys - get_keys
    
    print(f"\n✅ Common keys across all responses: {sorted(common_keys)}")
    if post_only:
        print(f"📤 POST-only keys: {sorted(post_only)}")
    
    # Verify cart_items structure
    if add_data['cart_items'] and get_data['cart_items']:
        add_item_keys = set(add_data['cart_items'][0].keys())
        get_item_keys = set(get_data['cart_items'][0].keys())
        
        if add_item_keys == get_item_keys:
            print(f"✅ Cart item structures are identical")
            print(f"   Item keys: {sorted(add_item_keys)}")
        else:
            print(f"❌ Cart item structures differ")
            print(f"   POST item: {sorted(add_item_keys)}")
            print(f"   GET item:  {sorted(get_item_keys)}")
    
    # Show sample responses
    print(f"\n📋 Sample Responses")
    print("-" * 20)
    
    print(f"\n✅ Success Response (POST):")
    print(json.dumps({
        'message': add_data['message'],
        'cart_items': f"[{len(add_data['cart_items'])} items]",
        'total_items': add_data['total_items'],
        'total_amount': add_data['total_amount']
    }, indent=2))
    
    print(f"\n📥 Get Response (GET):")
    print(json.dumps({
        'cart_items': f"[{len(get_data['cart_items'])} items]",
        'total_items': get_data['total_items'],
        'total_amount': get_data['total_amount']
    }, indent=2))
    
    print(f"\n❌ Error Response (POST):")
    print(json.dumps({
        'message': error_data['message'],
        'cart_items': f"[{len(error_data['cart_items'])} items]",
        'total_items': error_data['total_items'],
        'total_amount': error_data['total_amount']
    }, indent=2))
    
    # Verify consistency requirements
    consistency_checks = [
        (success_keys == error_keys, "POST success and error responses have same structure"),
        (common_keys == {'cart_items', 'total_items', 'total_amount'}, "All responses share core cart data"),
        (post_only == {'message'}, "POST responses only add message field"),
        (add_data['total_items'] == get_data['total_items'], "Total items count matches"),
        (add_data['total_amount'] == get_data['total_amount'], "Total amount matches"),
        (len(add_data['cart_items']) == len(get_data['cart_items']), "Cart items count matches")
    ]
    
    print(f"\n🧪 Consistency Checks")
    print("-" * 20)
    
    all_passed = True
    for check, description in consistency_checks:
        status = "✅" if check else "❌"
        print(f"{status} {description}")
        if not check:
            all_passed = False
    
    return all_passed

def test_cart_item_structure():
    """Test the detailed structure of cart items"""
    print(f"\n📦 Testing Cart Item Structure")
    print("=" * 35)
    
    client = Client()
    
    # Create session and add item
    session_resp = client.get('/api/common/session/')
    add_resp = client.post('/api/common/cart/', {
        'variant_id': 1,
        'quantity': 2
    }, content_type='application/json')
    
    if add_resp.status_code == 200:
        add_data = add_resp.json()
        
        if add_data['cart_items']:
            item = add_data['cart_items'][0]
            
            print("Cart Item Fields:")
            for key, value in item.items():
                print(f"  {key}: {value} ({type(value).__name__})")
            
            # Verify required fields
            required_fields = [
                'cart_item_id', 'cart_id', 'product_id', 'product_name',
                'variant_id', 'variant_size', 'quantity', 'price',
                'discount', 'discounted_price', 'item_total'
            ]
            
            missing_fields = [field for field in required_fields if field not in item]
            extra_fields = [field for field in item.keys() if field not in required_fields]
            
            print(f"\n🔍 Field Analysis:")
            if not missing_fields:
                print(f"✅ All required fields present")
            else:
                print(f"❌ Missing fields: {missing_fields}")
            
            if not extra_fields:
                print(f"✅ No unexpected fields")
            else:
                print(f"ℹ️  Extra fields: {extra_fields}")
            
            return len(missing_fields) == 0
    
    return False

def main():
    """Run all unified response format tests"""
    print("🔄 Unified Cart Response Format Tests")
    print("=" * 60)
    
    tests = [
        ("Response Format Consistency", test_response_format_consistency),
        ("Cart Item Structure", test_cart_item_structure),
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
        print("\n🎉 All Unified Response Format Tests Passed!")
        print("✅ POST and GET cart endpoints have consistent response formats")
        print("📤 POST responses include 'message' field for success/error feedback")
        print("📥 GET responses use the same cart_items, total_items, total_amount structure")
        print("🔄 Both success and error POST responses follow the same format")
        print("📱 Frontend can handle all cart responses with a single interface")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
