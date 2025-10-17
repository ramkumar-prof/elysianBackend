#!/usr/bin/env python3
"""
Test script to verify the new cart structure functionality
Run this after applying the migration to test the new cart system
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

from common.models import Cart, CartItem, Product, Variant
from django.contrib.auth import get_user_model

User = get_user_model()

def test_cart_restructure():
    """Test the new cart structure"""
    
    print("🧪 Testing Cart Restructure")
    print("=" * 40)
    
    # Test 1: Check model structure
    print("\n1. 📋 Testing Model Structure")
    print("-" * 30)
    
    # Check Cart model fields
    cart_fields = [field.name for field in Cart._meta.fields]
    print(f"Cart fields: {cart_fields}")
    
    expected_cart_fields = ['id', 'user', 'session_id', 'created_at', 'updated_at']
    missing_fields = set(expected_cart_fields) - set(cart_fields)
    extra_fields = set(cart_fields) - set(expected_cart_fields)
    
    if not missing_fields and not extra_fields:
        print("✅ Cart model structure is correct")
    else:
        if missing_fields:
            print(f"❌ Missing fields in Cart: {missing_fields}")
        if extra_fields:
            print(f"⚠️  Extra fields in Cart: {extra_fields}")
    
    # Check CartItem model fields
    cart_item_fields = [field.name for field in CartItem._meta.fields]
    print(f"CartItem fields: {cart_item_fields}")
    
    expected_cart_item_fields = ['id', 'cart', 'product', 'variant', 'quantity', 'created_at', 'updated_at']
    missing_item_fields = set(expected_cart_item_fields) - set(cart_item_fields)
    extra_item_fields = set(cart_item_fields) - set(expected_cart_item_fields)
    
    if not missing_item_fields and not extra_item_fields:
        print("✅ CartItem model structure is correct")
    else:
        if missing_item_fields:
            print(f"❌ Missing fields in CartItem: {missing_item_fields}")
        if extra_item_fields:
            print(f"⚠️  Extra fields in CartItem: {extra_item_fields}")
    
    # Test 2: Test cart creation and helper methods
    print("\n2. 🛒 Testing Cart Helper Methods")
    print("-" * 30)
    
    # Get or create a test user
    user = User.objects.first()
    if not user:
        print("❌ No users found. Create a user first to test cart functionality.")
        return
    
    print(f"Testing with user: {user.mobile_number}")
    
    # Test cart creation
    cart = Cart.get_or_create_for_user(user)
    print(f"✅ Cart created/retrieved: {cart}")
    
    # Test cart items property
    initial_items = cart.cart_items.count()
    print(f"Initial cart items: {initial_items}")
    
    # Test 3: Test cart item operations (if products exist)
    print("\n3. 📦 Testing Cart Item Operations")
    print("-" * 30)
    
    products = Product.objects.filter(is_available=True)[:2]
    if not products:
        print("❌ No products found. Create products to test cart item operations.")
        return
    
    for product in products:
        variants = Variant.objects.filter(product=product, is_available=True)[:1]
        if variants:
            variant = variants[0]
            print(f"Testing with product: {product.name}, variant: {variant.size}")
            
            # Test add item
            cart_item = cart.add_item(product, variant, quantity=2)
            print(f"✅ Added item: {cart_item}")
            
            # Test update quantity
            updated_item = cart.update_item_quantity(product, variant, 3)
            print(f"✅ Updated quantity: {updated_item.quantity}")
            
            break
    
    # Test cart items count
    final_items = cart.cart_items.count()
    total_quantity = cart.get_total_items()
    print(f"Final cart items: {final_items}")
    print(f"Total quantity: {total_quantity}")
    
    # Test 4: Test cart clearing
    print("\n4. 🧹 Testing Cart Clearing")
    print("-" * 30)
    
    if final_items > 0:
        cart.clear()
        cleared_items = cart.cart_items.count()
        print(f"✅ Cart cleared. Items after clear: {cleared_items}")
    else:
        print("ℹ️  No items to clear")
    
    # Test 5: Test session cart
    print("\n5. 🔐 Testing Session Cart")
    print("-" * 30)
    
    session_cart = Cart.get_or_create_for_session("test_session_123")
    print(f"✅ Session cart created: {session_cart}")
    
    # Test 6: Check database constraints
    print("\n6. 🔒 Testing Database Constraints")
    print("-" * 30)
    
    try:
        # Test unique constraint on CartItem
        if products and Variant.objects.filter(product=products[0]).exists():
            product = products[0]
            variant = Variant.objects.filter(product=product)[0]
            
            # Add item twice to test unique constraint
            CartItem.objects.create(cart=cart, product=product, variant=variant, quantity=1)
            try:
                CartItem.objects.create(cart=cart, product=product, variant=variant, quantity=1)
                print("❌ Unique constraint not working - duplicate items allowed")
            except Exception as e:
                print("✅ Unique constraint working - duplicate items prevented")

            # Clean up test item
            CartItem.objects.filter(cart=cart, product=product, variant=variant).delete()
        
    except Exception as e:
        print(f"⚠️  Error testing constraints: {str(e)}")
    
    print("\n🎉 Cart Restructure Test Complete!")
    print("=" * 40)

def show_cart_summary():
    """Show summary of current cart data"""
    
    print("\n📊 Cart System Summary")
    print("=" * 30)
    
    total_carts = Cart.objects.count()
    total_cart_items = CartItem.objects.count()
    
    print(f"Total Carts: {total_carts}")
    print(f"Total Cart Items: {total_cart_items}")
    
    if total_carts > 0:
        print("\nCart Details:")
        for cart in Cart.objects.all()[:5]:  # Show first 5 carts
            items_count = cart.cart_items.count()
            total_quantity = cart.get_total_items()
            identifier = cart.user.mobile_number if cart.user else f"Session: {cart.session_id}"
            print(f"  - {identifier}: {items_count} items, {total_quantity} total quantity")
    
    if total_cart_items > 0:
        print("\nSample Cart Items:")
        for item in CartItem.objects.all()[:5]:  # Show first 5 items
            print(f"  - Cart {item.cart.id}: {item.product.name} ({item.variant.size}) x{item.quantity}")

if __name__ == "__main__":
    print("🚀 Cart Restructure Test Script")
    print("=" * 40)
    
    # Show current state
    show_cart_summary()
    
    # Run tests
    test_cart_restructure()
    
    # Show final state
    show_cart_summary()
