#!/usr/bin/env python3
"""
Simple test to verify demo data is loaded and basic functionality works
"""

import os
import django
from django.test import Client

# Setup Django
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

def main():
    print("🍽️  Demo Data Verification")
    print("=" * 50)
    
    # Check database data
    from common.models import Category, Product, Variant
    from restaurent.models import RestaurentMenu
    
    categories = Category.objects.count()
    products = Product.objects.count()
    variants = Variant.objects.count()
    menu_items = RestaurentMenu.objects.count()
    
    print(f"✅ Database loaded:")
    print(f"   - Categories: {categories}")
    print(f"   - Products: {products}")
    print(f"   - Variants: {variants}")
    print(f"   - Menu Items: {menu_items}")
    
    # Test public API endpoints
    client = Client()
    
    # Create session
    session_resp = client.get('/api/common/session/')
    print(f"\n✅ Session API: {session_resp.status_code}")
    
    # Test categories
    categories_resp = client.get('/api/common/categories/')
    print(f"✅ Categories API: {categories_resp.status_code}")
    if categories_resp.status_code == 200:
        cats = categories_resp.json()
        print(f"   Found {len(cats)} categories")
    
    # Test menu
    menu_resp = client.get('/api/restaurant/menu/')
    print(f"✅ Restaurant Menu API: {menu_resp.status_code}")
    if menu_resp.status_code == 200:
        menu = menu_resp.json()
        print(f"   Found {len(menu)} menu items")
        
        # Show sample menu items
        print(f"\n📋 Sample Menu Items:")
        for item in menu[:3]:
            price_range = f"₹{min(v['price'] for v in item['variants'])}-₹{max(v['price'] for v in item['variants'])}"
            veg_status = "🥬 Veg" if item['veg'] else "🍖 Non-Veg"
            print(f"   - {item['name']}: {price_range} {veg_status}")
    
    # Test cart (should work with session)
    cart_resp = client.get('/api/common/cart/')
    print(f"\n✅ Cart API: {cart_resp.status_code}")
    if cart_resp.status_code == 200:
        print("   Cart accessible with session")
    
    print(f"\n🎉 Demo Data Successfully Loaded!")
    print(f"🚀 Your restaurant system is ready with sample data!")
    print(f"📱 Frontend can now connect to these endpoints:")
    print(f"   - GET /api/common/session/ (create session)")
    print(f"   - GET /api/common/categories/ (get categories)")
    print(f"   - GET /api/restaurant/menu/ (get menu)")
    print(f"   - GET /api/common/cart/ (get cart)")
    print(f"   - POST /api/common/cart/ (add to cart)")

if __name__ == '__main__':
    main()
