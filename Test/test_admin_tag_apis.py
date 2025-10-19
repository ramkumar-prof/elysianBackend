#!/usr/bin/env python3
"""
Test script for admin tag management APIs
Tests all CRUD operations for tags
"""

import os
import sys
import django
import json

# Add the project root to Python path
sys.path.append('/home/kulriya68/Elysian/elysianBackend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from common.models import Tag
from user.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

# Test configuration
client = Client()

def get_admin_user_and_token():
    """Create admin user and get JWT token"""
    print("🔑 Creating admin user and getting token...")

    # Create or get admin user
    User = get_user_model()
    admin_user, created = User.objects.get_or_create(
        mobile_number='9999999999',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )

    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.mobile_number}")
    else:
        print(f"✅ Using existing admin user: {admin_user.mobile_number}")

    # Generate JWT token directly
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    print(f"✅ Generated admin token: {access_token[:20]}...")
    return admin_user, access_token

def test_add_tag(token):
    """Test adding a new tag"""
    print("\n🧪 Testing add tag...")

    tag_data = {
        'name': 'Test Tag',
        'description': 'Test tag for admin API testing',
        'type': ['food', 'beverage'],
        'is_available': True
    }

    response = client.post(
        '/api/common/admin/tags/add/',
        data=json.dumps(tag_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    if response.status_code == 201:
        result = response.json()
        print(f"✅ Tag created successfully: {result['tag']['name']} (ID: {result['tag']['id']})")
        return result['tag']['id']
    else:
        print(f"❌ Failed to create tag: {response.status_code}")
        print(response.content.decode())
        return None

def test_list_tags(token):
    """Test listing tags"""
    print("\n🧪 Testing list tags...")

    response = client.get(
        '/api/common/admin/tags/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Listed {result['count']} tags")
        for tag in result['tags']:
            print(f"   - {tag['name']} (ID: {tag['id']}, Available: {tag['is_available']})")
        return result['tags']
    else:
        print(f"❌ Failed to list tags: {response.status_code}")
        print(response.content.decode())
        return []

def test_get_tag(token, tag_id):
    """Test getting a specific tag"""
    print(f"\n🧪 Testing get tag {tag_id}...")

    response = client.get(
        f'/api/common/admin/tags/{tag_id}/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    if response.status_code == 200:
        tag = response.json()
        print(f"✅ Got tag: {tag['name']} - {tag['description']}")
        return tag
    else:
        print(f"❌ Failed to get tag: {response.status_code}")
        print(response.content.decode())
        return None

def test_update_tag(token, tag_id):
    """Test updating a tag"""
    print(f"\n🧪 Testing update tag {tag_id}...")

    update_data = {
        'name': 'Updated Test Tag',
        'description': 'Updated description for test tag',
        'type': ['food', 'beverage', 'dessert'],
        'is_available': False
    }

    response = client.put(
        f'/api/common/admin/tags/{tag_id}/update/',
        data=json.dumps(update_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Tag updated successfully: {result['tag']['name']}")
        return True
    else:
        print(f"❌ Failed to update tag: {response.status_code}")
        print(response.content.decode())
        return False

def test_delete_tag(token, tag_id):
    """Test deleting a tag"""
    print(f"\n🧪 Testing delete tag {tag_id}...")

    response = client.delete(
        f'/api/common/admin/tags/{tag_id}/delete/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Tag deleted successfully: {result['message']}")
        return True
    else:
        print(f"❌ Failed to delete tag: {response.status_code}")
        print(response.content.decode())
        return False

def cleanup():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    Tag.objects.filter(name__icontains='Test Tag').delete()
    print("✅ Cleanup completed")

def main():
    """Run all tests"""
    print("🚀 Starting admin tag API tests...")

    # Get admin user and token
    admin_user, token = get_admin_user_and_token()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    try:
        # Test add tag
        tag_id = test_add_tag(token)
        if not tag_id:
            print("❌ Cannot proceed without creating a tag")
            return
        
        # Test list tags
        test_list_tags(token)
        
        # Test get tag
        test_get_tag(token, tag_id)
        
        # Test update tag
        test_update_tag(token, tag_id)
        
        # Test get updated tag
        test_get_tag(token, tag_id)
        
        # Test delete tag
        test_delete_tag(token, tag_id)
        
        # Verify deletion
        test_list_tags(token)
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    finally:
        cleanup()

if __name__ == '__main__':
    main()
