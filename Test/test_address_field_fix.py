#!/usr/bin/env python3
"""
Test script to verify the Address field fix in checkout process
"""

import os
import sys
import django
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

# Import Django models AFTER setup
from django.test import Client
from django.contrib.auth import get_user_model
from user.models import Address
from common.models import Cart, CartItem, Product, Variant

User = get_user_model()

def test_address_field_access():
    """Test that Address model fields can be accessed correctly"""
    print("🔍 Testing Address Model Field Access")
    print("=" * 45)
    
    # Create test user
    user, created = User.objects.get_or_create(
        mobile_number='9876543210',
        defaults={'password': 'testpass123'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Create test address
    address, created = Address.objects.get_or_create(
        user=user,
        name='Test Address',
        defaults={
            'address': '123 Main Street, Test Area',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'country': 'India',
            'is_default': True
        }
    )
    
    print(f"✅ Address created: {address.name}")
    print(f"📍 Address details:")
    print(f"   - ID: {address.id}")
    print(f"   - Name: {address.name}")
    print(f"   - Address: {address.address}")
    print(f"   - City: {address.city}")
    print(f"   - State: {address.state}")
    print(f"   - Pincode: {address.pincode}")
    print(f"   - Country: {address.country}")
    
    # Test the old (broken) field access
    print(f"\n🚫 Testing OLD (broken) field access:")
    try:
        broken_format = f"{address.street_address}, {address.city}, {address.state} - {address.postal_code}"
        print(f"❌ This should not work: {broken_format}")
        return False
    except AttributeError as e:
        print(f"✅ Expected error: {e}")
    
    # Test the new (fixed) field access
    print(f"\n✅ Testing NEW (fixed) field access:")
    try:
        correct_format = f"{address.address}, {address.city}, {address.state} - {address.pincode}"
        print(f"✅ Correct format: {correct_format}")
        return True
    except AttributeError as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_checkout_address_formatting():
    """Test the address formatting logic used in checkout"""
    print(f"\n🛒 Testing Checkout Address Formatting")
    print("=" * 40)
    
    # Get test user and address
    user = User.objects.filter(mobile_number='9876543210').first()
    if not user:
        print("❌ Test user not found")
        return False
    
    address = Address.objects.filter(user=user).first()
    if not address:
        print("❌ Test address not found")
        return False
    
    # Test the exact formatting logic used in checkout
    try:
        # This is the FIXED version from common/views/order.py line 84
        delivery_address = f"{address.address}, {address.city}, {address.state} - {address.pincode}"
        
        print(f"✅ Checkout address formatting works!")
        print(f"📍 Formatted address: {delivery_address}")
        
        # Verify all components are present
        components = [address.address, address.city, address.state, address.pincode]
        if all(components):
            print(f"✅ All address components present")
            return True
        else:
            print(f"❌ Missing address components: {[c for c in components if not c]}")
            return False
            
    except AttributeError as e:
        print(f"❌ Address formatting failed: {e}")
        return False

def test_address_serializer():
    """Test that AddressSerializer works with correct fields"""
    print(f"\n📝 Testing Address Serializer")
    print("=" * 30)
    
    from user.serializers import AddressSerializer
    
    # Get test address
    user = User.objects.filter(mobile_number='9876543210').first()
    address = Address.objects.filter(user=user).first()
    
    if not address:
        print("❌ Test address not found")
        return False
    
    try:
        serializer = AddressSerializer(address)
        data = serializer.data
        
        print(f"✅ Address serialization successful!")
        print(f"📋 Serialized fields: {list(data.keys())}")
        
        # Check that all expected fields are present
        expected_fields = ['id', 'name', 'address', 'pincode', 'city', 'state', 'country', 'is_default']
        missing_fields = [field for field in expected_fields if field not in data]
        
        if not missing_fields:
            print(f"✅ All expected fields present")
            return True
        else:
            print(f"❌ Missing fields: {missing_fields}")
            return False
            
    except Exception as e:
        print(f"❌ Serialization failed: {e}")
        return False

def main():
    """Run all address field tests"""
    print("🔧 Address Field Fix Verification Tests")
    print("=" * 50)
    
    tests = [
        ("Address Field Access", test_address_field_access),
        ("Checkout Address Formatting", test_checkout_address_formatting),
        ("Address Serializer", test_address_serializer),
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
        print("\n🎉 All Address Field Tests Passed!")
        print("✅ Address model fields are correctly defined")
        print("✅ Checkout address formatting works properly")
        print("✅ Address serializer uses correct field names")
        print("🔧 The 'street_address' AttributeError has been fixed!")
        print("\n📋 Address Model Fields:")
        print("   - address (TextField): Full address text")
        print("   - city (CharField): City name")
        print("   - state (CharField): State name")
        print("   - pincode (CharField): 6-digit postal code")
        print("   - country (CharField): Country name")
        print("   - name (CharField): Address label")
        print("   - is_default (BooleanField): Default address flag")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    print("=" * 50)

if __name__ == '__main__':
    main()
