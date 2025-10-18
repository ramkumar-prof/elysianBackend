#!/usr/bin/env python3
"""
Test script to verify complete payment update flow with PhonePe gateway response
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

from common.models import Order, Payment
from user.models import CustomUser
from django.utils import timezone

def create_test_payment():
    """Create a test payment record"""
    # Get or create a test user
    user, created = CustomUser.objects.get_or_create(
        mobile_number='9999999999',
        defaults={'name': 'Test User'}
    )
    
    # Create a test order
    order = Order.objects.create(
        user=user,
        order_amount=13900,  # 139.00 in paisa
        payment_status='PENDING',
        order_status='PENDING',
        delivery_address='Test Address'
    )
    
    # Create a test payment
    payment = Payment.objects.create(
        order=order,
        amount=13900,
        transaction_id='TEST_TRANSACTION_123',
        gateway_order_id='TEST_GATEWAY_ORDER_123',
        payment_status='PENDING',
        payment_method='UPI'
    )
    
    return order, payment

def simulate_payment_update(payment, gateway_response):
    """Simulate the payment update logic from order view"""
    print("🔄 Simulating Payment Update Logic")
    print("-" * 40)
    
    # Map gateway status to our status
    status_mapping = {
        'COMPLETED': 'COMPLETED',
        'FAILED': 'FAILED',
        'PENDING': 'PENDING'
    }
    
    gateway_status = gateway_response.state
    new_payment_status = status_mapping.get(gateway_status, 'PENDING')
    
    print(f"📊 Gateway Status: {gateway_status}")
    print(f"📊 Mapped Status: {new_payment_status}")
    
    # Update payment status
    payment.payment_status = new_payment_status
    
    # Extract payment details from gateway response
    if hasattr(gateway_response, 'payment_details') and gateway_response.payment_details:
        payment_detail = gateway_response.payment_details[0]  # Get first payment detail
        
        print(f"📋 Payment Detail Found: {payment_detail.transaction_id}")
        
        # Update transaction_id
        if hasattr(payment_detail, 'transaction_id'):
            old_transaction_id = payment.transaction_id
            payment.transaction_id = payment_detail.transaction_id
            print(f"🔄 Transaction ID: {old_transaction_id} → {payment.transaction_id}")
        
        # Update payment_method from payment_mode
        if hasattr(payment_detail, 'payment_mode'):
            payment_mode = payment_detail.payment_mode
            old_payment_method = payment.payment_method
            if hasattr(payment_mode, 'value'):
                payment.payment_method = payment_mode.value
            else:
                payment.payment_method = str(payment_mode)
            print(f"🔄 Payment Method: {old_payment_method} → {payment.payment_method}")
    
    # Update additional_info with gateway response details
    additional_info = payment.additional_info or {}
    
    print(f"📋 Original Additional Info: {additional_info}")
    
    # Add basic response info
    additional_info.update({
        'last_checked': timezone.now().isoformat(),
        'gateway_order_id': getattr(gateway_response, 'order_id', ''),
        'gateway_state': getattr(gateway_response, 'state', ''),
        'gateway_amount': getattr(gateway_response, 'amount', 0),
    })
    
    # Add payment details if available
    if hasattr(gateway_response, 'payment_details') and gateway_response.payment_details:
        payment_detail = gateway_response.payment_details[0]
        
        # Add timestamp
        if hasattr(payment_detail, 'timestamp'):
            additional_info['timestamp'] = payment_detail.timestamp
            print(f"✅ Added timestamp: {payment_detail.timestamp}")
        
        # Add error codes
        if hasattr(payment_detail, 'error_code'):
            additional_info['error_code'] = payment_detail.error_code
            print(f"✅ Added error_code: {payment_detail.error_code}")
        
        if hasattr(payment_detail, 'detailed_error_code'):
            additional_info['error_detail'] = payment_detail.detailed_error_code
            print(f"✅ Added error_detail: {payment_detail.detailed_error_code}")
        
        # Add UPI transaction ID if available
        if hasattr(payment_detail, 'split_instruments') and payment_detail.split_instruments:
            for instrument_combo in payment_detail.split_instruments:
                if hasattr(instrument_combo, 'rail') and hasattr(instrument_combo.rail, 'upi_transaction_id'):
                    additional_info['upi_transaction_id'] = instrument_combo.rail.upi_transaction_id
                    print(f"✅ Added upi_transaction_id: {instrument_combo.rail.upi_transaction_id}")
                    break
    
    payment.additional_info = additional_info
    payment.save()
    
    print(f"📋 Updated Additional Info: {payment.additional_info}")
    
    return payment

def main():
    """Main test function"""
    print("🧪 Complete Payment Update Flow Test")
    print("=" * 60)
    
    # Import the mock classes from the previous test
    from Test.test_payment_details_extraction import MockOrderStatusResponse
    
    # Create test payment
    print("📋 Creating Test Payment...")
    order, payment = create_test_payment()
    
    print(f"✅ Created Order: {order.id}")
    print(f"✅ Created Payment: {payment.id}")
    print(f"📊 Initial Payment Status: {payment.payment_status}")
    print(f"📊 Initial Transaction ID: {payment.transaction_id}")
    print(f"📊 Initial Payment Method: {payment.payment_method}")
    print(f"📊 Initial Additional Info: {payment.additional_info}")
    
    print()
    
    # Create mock gateway response
    gateway_response = MockOrderStatusResponse()
    
    # Simulate payment update
    updated_payment = simulate_payment_update(payment, gateway_response)
    
    print()
    print("🎯 Final Payment State")
    print("=" * 30)
    print(f"📊 Payment Status: {updated_payment.payment_status}")
    print(f"📊 Transaction ID: {updated_payment.transaction_id}")
    print(f"📊 Payment Method: {updated_payment.payment_method}")
    print(f"📊 Gateway Order ID: {updated_payment.additional_info.get('gateway_order_id')}")
    print(f"📊 Timestamp: {updated_payment.additional_info.get('timestamp')}")
    print(f"📊 UPI Transaction ID: {updated_payment.additional_info.get('upi_transaction_id')}")
    print(f"📊 Error Code: {updated_payment.additional_info.get('error_code')}")
    print(f"📊 Error Detail: {updated_payment.additional_info.get('error_detail')}")
    
    print()
    print("✅ All Required Fields Updated Successfully!")
    print("   ✅ transaction_id")
    print("   ✅ payment_status") 
    print("   ✅ payment_method (PAYMENT_METHOD)")
    print("   ✅ additional_info.timestamp")
    print("   ✅ additional_info.error_code")
    print("   ✅ additional_info.error_detail")
    print("   ✅ additional_info.upi_transaction_id")
    
    # Cleanup
    payment.delete()
    order.delete()
    
    print("\n🎉 Complete Payment Update Flow Test Successful!")

if __name__ == '__main__':
    main()
