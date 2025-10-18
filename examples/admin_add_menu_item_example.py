#!/usr/bin/env python3
"""
Example script demonstrating how to use the Admin Add Menu Item API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_MOBILE = "9876543210"  # Replace with actual admin mobile number
ADMIN_PASSWORD = "admin123"   # Replace with actual admin password

def get_admin_token():
    """Get JWT token for admin user"""
    # First create a session
    session_url = f"{BASE_URL}/api/common/session/"
    session_response = requests.get(session_url)
    
    if session_response.status_code != 200:
        print(f"Failed to create session: {session_response.status_code}")
        return None
    
    # Login to get JWT token
    login_url = f"{BASE_URL}/api/user/login/"
    login_data = {
        "mobile_number": ADMIN_MOBILE,
        "password": ADMIN_PASSWORD
    }
    
    # Use the same session for login
    session = requests.Session()
    session.get(session_url)  # Create session
    
    login_response = session.post(login_url, json=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return None
    
    # Extract access token from cookies
    access_token = login_response.cookies.get('access_token')
    
    if not access_token:
        print("No access token found in login response")
        return None
    
    print("✅ Successfully obtained admin JWT token")
    return access_token

def get_available_data():
    """Get available products, restaurants, and variants for testing"""
    # Create a session for public API access
    session = requests.Session()
    session.get(f"{BASE_URL}/api/common/session/")
    
    # Get menu to see existing structure
    menu_response = session.get(f"{BASE_URL}/api/restaurant/menu/")
    
    if menu_response.status_code == 200:
        menu_data = menu_response.json()
        if menu_data:
            first_item = menu_data[0]
            print(f"📋 Example menu item structure:")
            print(f"   Product ID: {first_item['product_id']}")
            print(f"   Name: {first_item['name']}")
            print(f"   Category: {first_item['category']}")
            print(f"   Variants: {len(first_item['variants'])}")
            
            return {
                'sample_product_id': first_item['product_id'],
                'sample_variants': first_item['variants']
            }
    
    return None

def add_menu_item_example():
    """Example of adding a menu item"""
    print("🚀 Admin Add Menu Item API Example")
    print("=" * 50)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token")
        return
    
    # Get sample data
    sample_data = get_available_data()
    if not sample_data:
        print("❌ Failed to get sample data")
        return
    
    # Example menu item data
    menu_item_data = {
        "product_id": sample_data['sample_product_id'],
        "restaurent_id": 1,  # Assuming restaurant ID 1 exists
        "is_available": True,
        "is_veg": True,
        "default_variant_id": sample_data['sample_variants'][0]['variant_id'] if sample_data['sample_variants'] else None
    }
    
    print(f"\n📝 Adding menu item with data:")
    print(json.dumps(menu_item_data, indent=2))
    
    # Make the API call
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    add_url = f"{BASE_URL}/api/restaurant/admin/menu/add/"
    response = requests.post(add_url, json=menu_item_data, headers=headers)
    
    print(f"\n📡 API Response:")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print("✅ Menu item added successfully!")
        print(f"Menu Item: {result['menu_item']['name']}")
        print(f"Available: {result['menu_item']['is_available']}")
        print(f"Vegetarian: {result['menu_item']['veg']}")
        print(f"Variants: {len(result['menu_item']['variants'])}")
    elif response.status_code == 400:
        error_data = response.json()
        print("❌ Validation error:")
        print(json.dumps(error_data, indent=2))
    elif response.status_code == 401:
        print("❌ Authentication failed - check your credentials")
    elif response.status_code == 403:
        print("❌ Permission denied - user is not admin")
    else:
        print(f"❌ Unexpected error: {response.text}")

def test_permission_denied():
    """Example showing permission denied for non-admin users"""
    print("\n🔒 Testing Permission Denied")
    print("-" * 30)
    
    # Try without authentication
    menu_item_data = {
        "product_id": 1,
        "restaurent_id": 1,
        "is_available": True,
        "is_veg": False
    }
    
    add_url = f"{BASE_URL}/api/restaurant/admin/menu/add/"
    response = requests.post(add_url, json=menu_item_data)
    
    print(f"Without auth - Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly denied access without authentication")
    
    # Try with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.post(add_url, json=menu_item_data, headers=headers)
    
    print(f"Invalid token - Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly denied access with invalid token")

if __name__ == "__main__":
    try:
        add_menu_item_example()
        test_permission_denied()
        print("\n🎉 Example completed!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
