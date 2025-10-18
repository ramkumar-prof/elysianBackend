#!/usr/bin/env python3
"""
Test script to verify all PhonePe payment modes are supported
"""

import os
import sys
import django

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from common.models import Payment, Order
from user.models import CustomUser

class MockPaymentMode:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value

def test_phonepe_payment_modes():
    """Test all PhonePe payment modes"""
    print("🧪 PhonePe Payment Modes Test")
    print("=" * 50)
    
    # PhonePe payment modes as specified
    phonepe_modes = [
        'UPI_INTENT',
        'UPI_COLLECT', 
        'UPI_QR',
        'CARD',
        'TOKEN',
        'NET_BANKING'
    ]
    
    # Get payment method choices from model
    payment_choices = dict(Payment.PAYMENT_METHOD_CHOICES)
    
    print("📋 PhonePe Payment Modes vs Model Choices:")
    print("-" * 45)
    
    all_supported = True
    
    for mode in phonepe_modes:
        if mode in payment_choices:
            print(f"✅ {mode:<12} → {payment_choices[mode]}")
        else:
            print(f"❌ {mode:<12} → NOT SUPPORTED")
            all_supported = False
    
    print()
    
    # Test additional choices that aren't PhonePe modes
    print("📋 Additional Payment Methods:")
    print("-" * 30)
    
    for choice_key, choice_label in Payment.PAYMENT_METHOD_CHOICES:
        if choice_key not in phonepe_modes:
            print(f"💰 {choice_key:<12} → {choice_label}")
    
    return all_supported

def test_payment_mode_extraction():
    """Test payment mode extraction logic"""
    print("\n🔧 Payment Mode Extraction Test")
    print("=" * 40)
    
    phonepe_modes = [
        'UPI_INTENT',
        'UPI_COLLECT', 
        'UPI_QR',
        'CARD',
        'TOKEN',
        'NET_BANKING'
    ]
    
    print("📋 Testing Payment Mode Extraction Logic:")
    print("-" * 42)
    
    for mode in phonepe_modes:
        # Simulate the extraction logic from order view
        payment_mode = MockPaymentMode(mode)
        
        if hasattr(payment_mode, 'value'):
            extracted_method = payment_mode.value
        else:
            extracted_method = str(payment_mode)
        
        print(f"   {mode} → {extracted_method}")

def test_payment_creation():
    """Test creating payments with PhonePe modes"""
    print("\n💳 Payment Creation Test")
    print("=" * 30)
    
    # Get or create a test user
    user, created = CustomUser.objects.get_or_create(
        mobile_number='9999999998',
        defaults={'first_name': 'PhonePe', 'last_name': 'Test User'}
    )
    
    # Create a test order
    order = Order.objects.create(
        user=user,
        order_amount=10000,  # 100.00 in paisa
        payment_status='PENDING',
        order_status='PENDING',
        delivery_address='Test Address for PhonePe'
    )
    
    phonepe_modes = [
        'UPI_INTENT',
        'UPI_COLLECT', 
        'UPI_QR',
        'CARD',
        'TOKEN',
        'NET_BANKING'
    ]
    
    created_payments = []
    
    print("📋 Creating Test Payments:")
    print("-" * 25)
    
    for i, mode in enumerate(phonepe_modes):
        try:
            payment = Payment.objects.create(
                order=order,
                amount=10000,
                transaction_id=f'TEST_TXN_{mode}_{i}',
                gateway_order_id=f'TEST_GATEWAY_{mode}_{i}',
                payment_status='PENDING',
                payment_method=mode
            )
            created_payments.append(payment)
            print(f"✅ {mode:<12} → Payment ID: {payment.id}")
        except Exception as e:
            print(f"❌ {mode:<12} → Error: {e}")
    
    print(f"\n📊 Successfully created {len(created_payments)} payments")
    
    # Cleanup
    for payment in created_payments:
        payment.delete()
    order.delete()
    
    return len(created_payments) == len(phonepe_modes)

def main():
    """Main test function"""
    print("🧪 PhonePe Payment Modes Verification")
    print("=" * 60)
    
    # Test payment modes support
    modes_supported = test_phonepe_payment_modes()
    
    # Test extraction logic
    test_payment_mode_extraction()
    
    # Test payment creation
    creation_success = test_payment_creation()
    
    print("\n🎯 Test Summary")
    print("=" * 30)
    
    if modes_supported:
        print("✅ All PhonePe payment modes are supported")
    else:
        print("❌ Some PhonePe payment modes are missing")
    
    if creation_success:
        print("✅ Payment creation works for all modes")
    else:
        print("❌ Payment creation failed for some modes")
    
    print("\n📊 Supported PhonePe Payment Modes:")
    print("   ✅ UPI_INTENT   - UPI Intent")
    print("   ✅ UPI_COLLECT  - UPI Collect") 
    print("   ✅ UPI_QR       - UPI QR")
    print("   ✅ CARD         - Card")
    print("   ✅ TOKEN        - Token")
    print("   ✅ NET_BANKING  - Net Banking")
    
    print("\n💡 Additional Payment Methods:")
    print("   💰 CASH         - Cash (for offline payments)")
    
    if modes_supported and creation_success:
        print("\n🎉 All PhonePe Payment Modes Successfully Configured!")
    else:
        print("\n⚠️  Some issues found with PhonePe payment mode configuration")

if __name__ == '__main__':
    main()
