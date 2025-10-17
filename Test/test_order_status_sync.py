#!/usr/bin/env python3
"""
Simple test script to verify order status synchronization functionality
Run this after creating some test orders to see the status sync in action
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/home/kulriya68/Elysian/elysianBackend')
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from common.models import Order, Payment
from common.utils.payment_utils import get_payment_status
from django.contrib.auth import get_user_model

User = get_user_model()

def test_order_status_sync():
    """Test the order status synchronization logic"""
    
    print("🔍 Testing Order Status Synchronization")
    print("=" * 50)
    
    # Get all pending orders
    pending_orders = Order.objects.filter(payment_status='PENDING')
    
    if not pending_orders.exists():
        print("❌ No pending orders found to test")
        print("💡 Create some test orders first using the checkout API")
        return
    
    print(f"📋 Found {pending_orders.count()} pending orders")
    print()
    
    for order in pending_orders:
        print(f"🔄 Testing Order #{order.id}")
        print(f"   Current Status: {order.payment_status}")
        print(f"   Order Status: {order.order_status}")
        
        try:
            # Simulate the same logic as in get_order_details
            gateway_response = get_payment_status(str(order.id))
            
            if gateway_response and hasattr(gateway_response, 'data'):
                gateway_data = gateway_response.data
                print(f"   Gateway Response: {gateway_data}")
                
                if hasattr(gateway_data, 'state'):
                    gateway_status = gateway_data.state
                    print(f"   Gateway Status: {gateway_status}")
                    
                    # Status mapping
                    status_mapping = {
                        'COMPLETED': 'COMPLETED',
                        'FAILED': 'FAILED',
                        'PENDING': 'PENDING'
                    }
                    
                    new_payment_status = status_mapping.get(gateway_status, 'PENDING')
                    
                    if order.payment_status != new_payment_status:
                        print(f"   ✅ Status Update Required: {order.payment_status} → {new_payment_status}")
                        
                        # Update order
                        order.payment_status = new_payment_status
                        
                        if new_payment_status == 'COMPLETED':
                            order.order_status = 'CONFIRMED'
                            print(f"   ✅ Order Status Updated: PENDING → CONFIRMED")
                        elif new_payment_status == 'FAILED':
                            order.order_status = 'CANCELLED'
                            print(f"   ✅ Order Status Updated: PENDING → CANCELLED")
                        
                        order.save()
                        
                        # Update payment record
                        payment = Payment.objects.filter(order=order).first()
                        if payment:
                            payment.payment_status = new_payment_status
                            
                            if hasattr(gateway_data, 'transaction_id'):
                                payment.transaction_id = gateway_data.transaction_id
                                print(f"   ✅ Transaction ID Updated: {gateway_data.transaction_id}")
                            
                            payment.save()
                            
                        print(f"   ✅ Database Updated Successfully")
                    else:
                        print(f"   ℹ️  No Status Change Required")
                else:
                    print(f"   ⚠️  No state field in gateway response")
            else:
                print(f"   ⚠️  No data in gateway response")
                
        except Exception as e:
            print(f"   ❌ Error checking payment status: {str(e)}")
        
        print()
    
    print("✅ Test completed!")

def show_order_summary():
    """Show summary of all orders and their statuses"""
    
    print("\n📊 Order Status Summary")
    print("=" * 30)
    
    orders = Order.objects.all().order_by('-created_at')
    
    if not orders.exists():
        print("❌ No orders found")
        return
    
    for order in orders:
        payment = Payment.objects.filter(order=order).first()
        
        print(f"Order #{order.id}")
        print(f"  User: {order.user.username if order.user else 'Unknown'}")
        print(f"  Amount: ₹{order.order_amount / 100:.2f}")
        print(f"  Payment Status: {order.payment_status}")
        print(f"  Order Status: {order.order_status}")
        
        if payment:
            print(f"  Transaction ID: {payment.transaction_id or 'Not set'}")
            print(f"  Gateway Order ID: {payment.gateway_order_id or 'Not set'}")
        
        print(f"  Created: {order.created_at}")
        print()

if __name__ == "__main__":
    print("🚀 Order Status Sync Test Script")
    print("=" * 40)
    
    # Show current order summary
    show_order_summary()
    
    # Test status synchronization
    test_order_status_sync()
    
    # Show updated summary
    print("\n📊 Updated Order Status Summary")
    show_order_summary()
