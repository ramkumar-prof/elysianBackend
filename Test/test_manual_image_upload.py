#!/usr/bin/env python
"""
Manual test script for admin product image upload API with existing products
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

def get_admin_user():
    """Get admin user"""
    User = get_user_model()
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ No admin user found. Please create an admin user first.")
        return None
    return admin_user

def get_jwt_token(user):
    """Generate JWT token for user"""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def create_test_image(filename="test_image.jpg", format="JPEG"):
    """Create a test image file"""
    # Create a simple test image
    image = Image.new('RGB', (200, 200), color='blue')
    image_io = BytesIO()
    image.save(image_io, format=format)
    image_io.seek(0)
    
    return SimpleUploadedFile(
        filename,
        image_io.getvalue(),
        content_type=f'image/{format.lower()}'
    )

def test_upload_to_existing_product():
    """Test uploading image to an existing product"""
    print("🧪 Testing image upload to existing product...")
    
    # Get existing product
    product = Product.objects.first()
    if not product:
        print("❌ No existing products found")
        return False
    
    print(f"📦 Using product: {product.name} (ID: {product.id})")
    print(f"   Current images: {product.image_urls}")
    
    # Get admin user
    admin_user = get_admin_user()
    if not admin_user:
        return False
    
    admin_token = get_jwt_token(admin_user)
    client = Client()
    
    # Create test image
    test_image = create_test_image("new_main_image.jpg")
    
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
        print(f"✅ Image uploaded successfully!")
        print(f"   Image URL: {response_data.get('image_url')}")
        print(f"   Product: {response_data.get('product_name')}")
        print(f"   Is Default: {response_data.get('is_default')}")
        print(f"   Total Images: {response_data.get('total_images')}")
        
        # Verify product was updated
        product.refresh_from_db()
        print(f"   Updated image_urls: {product.image_urls}")
        
        # Check if file exists
        image_url = response_data.get('image_url')
        if image_url:
            # Convert URL to file path
            file_path = image_url.replace('/api/common/images/', 'media/images/')
            full_path = os.path.join('/home/kulriya68/Elysian/elysianBackend', file_path)
            if os.path.exists(full_path):
                print(f"✅ File exists at: {full_path}")
                file_size = os.path.getsize(full_path)
                print(f"   File size: {file_size} bytes")
            else:
                print(f"❌ File not found at: {full_path}")
        
        return True
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        return False

def test_upload_additional_image():
    """Test uploading additional image to existing product"""
    print("\n🧪 Testing additional image upload...")
    
    # Get existing product
    product = Product.objects.first()
    if not product:
        print("❌ No existing products found")
        return False
    
    print(f"📦 Using product: {product.name} (ID: {product.id})")
    
    # Get admin user
    admin_user = get_admin_user()
    if not admin_user:
        return False
    
    admin_token = get_jwt_token(admin_user)
    client = Client()
    
    # Create test image
    test_image = create_test_image("additional_view.png", "PNG")
    
    # Test data
    data = {
        'product_id': product.id,
        'default': 'false',
        'image_number': '3',
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
        print(f"✅ Additional image uploaded successfully!")
        print(f"   Image URL: {response_data.get('image_url')}")
        print(f"   Image Number: {response_data.get('image_number')}")
        print(f"   Total Images: {response_data.get('total_images')}")
        
        # Verify product was updated
        product.refresh_from_db()
        print(f"   Updated image_urls: {product.image_urls}")
        
        return True
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        return False

def show_directory_structure():
    """Show the created directory structure"""
    print("\n📁 Directory structure created:")
    
    products_dir = '/home/kulriya68/Elysian/elysianBackend/media/images/products'
    if os.path.exists(products_dir):
        for item in os.listdir(products_dir):
            item_path = os.path.join(products_dir, item)
            if os.path.isdir(item_path):
                print(f"   📂 {item}/")
                for subitem in os.listdir(item_path):
                    subitem_path = os.path.join(item_path, subitem)
                    if os.path.isdir(subitem_path):
                        print(f"      📂 {subitem}/")
                        for file in os.listdir(subitem_path):
                            file_path = os.path.join(subitem_path, file)
                            if os.path.isfile(file_path):
                                size = os.path.getsize(file_path)
                                print(f"         📄 {file} ({size} bytes)")
                    else:
                        size = os.path.getsize(subitem_path)
                        print(f"      📄 {subitem} ({size} bytes)")

def main():
    """Run manual tests"""
    print("🚀 Manual Test: Admin Product Image Upload API")
    print("=" * 50)
    
    try:
        # Show existing products
        products = Product.objects.all()[:3]
        print(f"📦 Available products ({len(products)} shown):")
        for product in products:
            print(f"   - {product.name} (ID: {product.id}) - Images: {len(product.image_urls or [])}")
        
        if not products:
            print("❌ No products found. Please create some products first.")
            return
        
        # Run tests
        success1 = test_upload_to_existing_product()
        success2 = test_upload_additional_image()
        
        # Show directory structure
        show_directory_structure()
        
        if success1 and success2:
            print("\n🎉 All manual tests passed!")
        else:
            print("\n❌ Some tests failed.")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
