#!/usr/bin/env python
"""
Test script for admin product image upload API
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image

# Setup Django environment
sys.path.append('/home/kulriya68/Elysian/elysianBackend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elysianBackend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken
from common.models import Product, Category
import json

def get_test_users():
    """Get or create test users"""
    User = get_user_model()
    
    # Get admin user
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ No admin user found. Please create an admin user first.")
        return None, None
    
    # Get regular user
    regular_user = User.objects.filter(is_staff=False).first()
    if not regular_user:
        print("❌ No regular user found. Please create a regular user first.")
        return admin_user, None
    
    return admin_user, regular_user

def get_jwt_token(user):
    """Generate JWT token for user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def create_test_image(filename="test_image.jpg", format="JPEG"):
    """Create a test image file"""
    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    image_io = BytesIO()
    image.save(image_io, format=format)
    image_io.seek(0)
    
    return SimpleUploadedFile(
        filename,
        image_io.getvalue(),
        content_type=f'image/{format.lower()}'
    )

def create_test_data():
    """Create test category and product"""
    # Create test category
    category, created = Category.objects.get_or_create(
        name='Test Category for Image Upload',
        defaults={
            'description': 'Test category for image upload testing',
            'is_available': True,
            'type': 'test'
        }
    )
    
    # Create test product
    product, created = Product.objects.get_or_create(
        name='Test Product for Image Upload',
        defaults={
            'description': 'Test product for image upload testing',
            'category': category,
            'image_urls': [],
            'discount': 0.00,
            'is_available': True,
            'sub_category': []
        }
    )
    
    return category, product

def cleanup_test_data():
    """Clean up test data"""
    # Delete test products and categories
    Product.objects.filter(name__contains='Test Product for Image Upload').delete()
    Category.objects.filter(name__contains='Test Category for Image Upload').delete()

def test_image_upload_success():
    """Test successful image upload"""
    print("\n🧪 Testing successful image upload...")
    
    client = Client()
    admin_user, _ = get_test_users()
    if not admin_user:
        return False
    
    admin_token = get_jwt_token(admin_user)
    category, product = create_test_data()
    
    # Create test image
    test_image = create_test_image("test_product.jpg")
    
    # Test data
    data = {
        'product_id': product.id,
        'default': 'true',
        'image': test_image
    }
    
    # Make request
    response = client.post(
        '/api/common/admin/products/upload-image/',
        data=data,
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response.status_code == 201:
        response_data = response.json()
        print(f"✅ Image uploaded successfully")
        print(f"   Image URL: {response_data.get('image_url')}")
        print(f"   Product: {response_data.get('product_name')}")
        print(f"   Is Default: {response_data.get('is_default')}")
        print(f"   Total Images: {response_data.get('total_images')}")
        
        # Verify product was updated
        product.refresh_from_db()
        if product.image_urls and len(product.image_urls) > 0:
            print(f"✅ Product image_urls updated: {product.image_urls}")
            return True
        else:
            print(f"❌ Product image_urls not updated")
            return False
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        return False

def test_image_upload_non_default():
    """Test non-default image upload"""
    print("\n🧪 Testing non-default image upload...")
    
    client = Client()
    admin_user, _ = get_test_users()
    if not admin_user:
        return False
    
    admin_token = get_jwt_token(admin_user)
    category, product = create_test_data()
    
    # Create test image
    test_image = create_test_image("side_view.png", "PNG")
    
    # Test data
    data = {
        'product_id': product.id,
        'default': 'false',
        'image_number': '2',
        'image': test_image
    }
    
    # Make request
    response = client.post(
        '/api/common/admin/products/upload-image/',
        data=data,
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response.status_code == 201:
        response_data = response.json()
        print(f"✅ Non-default image uploaded successfully")
        print(f"   Image URL: {response_data.get('image_url')}")
        print(f"   Image Number: {response_data.get('image_number')}")
        print(f"   Is Default: {response_data.get('is_default')}")
        return True
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        return False

def test_image_upload_unauthorized():
    """Test unauthorized access"""
    print("\n🧪 Testing unauthorized access...")
    
    client = Client()
    _, regular_user = get_test_users()
    if not regular_user:
        return False
    
    regular_token = get_jwt_token(regular_user)
    category, product = create_test_data()
    
    # Create test image
    test_image = create_test_image("unauthorized.jpg")
    
    # Test data
    data = {
        'product_id': product.id,
        'image': test_image
    }
    
    # Make request with regular user token
    response = client.post(
        '/api/common/admin/products/upload-image/',
        data=data,
        HTTP_AUTHORIZATION=f'Bearer {regular_token}'
    )
    
    if response.status_code == 403:
        print(f"✅ Unauthorized access correctly blocked")
        return True
    else:
        print(f"❌ Expected 403, got {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        return False

def test_image_upload_invalid_product():
    """Test upload with invalid product ID"""
    print("\n🧪 Testing upload with invalid product ID...")
    
    client = Client()
    admin_user, _ = get_test_users()
    if not admin_user:
        return False
    
    admin_token = get_jwt_token(admin_user)
    
    # Create test image
    test_image = create_test_image("invalid_product.jpg")
    
    # Test data with non-existent product ID
    data = {
        'product_id': 99999,
        'image': test_image
    }
    
    # Make request
    response = client.post(
        '/api/common/admin/products/upload-image/',
        data=data,
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response.status_code == 404:
        print(f"✅ Invalid product ID correctly handled")
        return True
    else:
        print(f"❌ Expected 404, got {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        return False

def test_image_upload_missing_fields():
    """Test upload with missing required fields"""
    print("\n🧪 Testing upload with missing fields...")
    
    client = Client()
    admin_user, _ = get_test_users()
    if not admin_user:
        return False
    
    admin_token = get_jwt_token(admin_user)
    
    # Test missing product_id
    test_image = create_test_image("missing_fields.jpg")
    data = {'image': test_image}
    
    response = client.post(
        '/api/common/admin/products/upload-image/',
        data=data,
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response.status_code == 400:
        print(f"✅ Missing product_id correctly handled")
    else:
        print(f"❌ Expected 400 for missing product_id, got {response.status_code}")
        return False
    
    # Test missing image
    category, product = create_test_data()
    data = {'product_id': product.id}
    
    response = client.post(
        '/api/common/admin/products/upload-image/',
        data=data,
        HTTP_AUTHORIZATION=f'Bearer {admin_token}'
    )
    
    if response.status_code == 400:
        print(f"✅ Missing image file correctly handled")
        return True
    else:
        print(f"❌ Expected 400 for missing image, got {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Admin Product Image Upload API Tests...")
    print("=" * 60)
    
    try:
        # Setup
        cleanup_test_data()
        
        # Run tests
        tests = [
            test_image_upload_success,
            test_image_upload_non_default,
            test_image_upload_unauthorized,
            test_image_upload_invalid_product,
            test_image_upload_missing_fields
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with error: {str(e)}")
            finally:
                cleanup_test_data()  # Clean up after each test
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("❌ Some tests failed. Please check the implementation.")
        
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup_test_data()

if __name__ == '__main__':
    main()
