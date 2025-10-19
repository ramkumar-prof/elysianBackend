"""
Admin-only views for managing products and variants
"""

from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.conf import settings
import os
import json

from common.views.common import JWTOnlyAuthentication
from user.permissions import IsAdminUser
from ..models import Product, Variant, Category, Tag
from ..serializers import AdminProductSerializer, AdminProductWithVariantsSerializer, AdminVariantSerializer, AdminCategorySerializer, AdminTagSerializer, ProductSerializer
from common.utils.common_utils import get_rel_path


# Product Admin APIs
@api_view(['POST'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_add_product(request):
    """
    Admin-only API endpoint to add new products with variants

    Required fields:
    - name: Product name
    - category: Category ID
    - variants: Array of variant objects with fields:
      - size: Variant size (required)
      - price: Variant price (required, must be > 0)
      - is_available: Boolean (required)
      - description: Variant description (optional)
      - type: Variant type (optional)

    Optional fields:
    - description: Product description
    - image_urls: Array of image URLs (defaults to empty list)
    - discount: Discount percentage (0-100, defaults to 0)
    - is_available: Boolean (default: True)
    - sub_category: Array of subcategory tags (defaults to empty list)

    Example request:
    {
        "name": "chai",
        "description": "chai masala with milk",
        "discount": "0",
        "is_available": true,
        "category": 4,
        "sub_category": ["beverages"],
        "variants": [
            {
                "size": "regular",
                "price": "30",
                "description": "approx 150 ml",
                "is_available": true,
                "type": ""
            }
        ]
    }
    """
    serializer = AdminProductWithVariantsSerializer(data=request.data)

    if serializer.is_valid():
        try:
            product = serializer.save()
            response_serializer = ProductSerializer(product)
            return Response({
                'message': 'Product created successfully',
                'product': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({
                'error': 'Database integrity error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_update_product(request, product_id):
    """
    Admin-only API endpoint to update existing products with variant management

    PUT: Full update (all fields required including variants)
    PATCH: Partial update (only provided fields updated)

    When variants are provided, all existing variants are replaced with the new ones.
    At least one variant must be provided if variants field is included.

    Example request:
    {
        "id": 1,
        "name": "chai",
        "description": "chai masala with milk",
        "discount": "0",
        "is_available": true,
        "category": 4,
        "sub_category": ["beverages"],
        "variants": [
            {
                "size": "regular",
                "price": "30",
                "description": "approx 150 ml",
                "is_available": true,
                "type": ""
            }
        ]
    }
    """
    product = get_object_or_404(Product, id=product_id)

    # Use partial=True for PATCH requests
    partial = request.method == 'PATCH'

    # Check if variants are provided in the request
    if 'variants' in request.data:
        # Use the variant-aware serializer
        serializer = AdminProductWithVariantsSerializer(product, data=request.data, partial=partial)
    else:
        # Use the regular product serializer (no variant changes)
        serializer = AdminProductSerializer(product, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated_product = serializer.save()
            response_serializer = ProductSerializer(updated_product)
            return Response({
                'message': 'Product updated successfully',
                'product': response_serializer.data
            }, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({
                'error': 'Database integrity error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_delete_product(request, product_id):
    """
    Admin-only API endpoint to delete products
    
    Note: This will also delete all associated variants due to CASCADE relationship
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Store product info for response
    product_name = product.name
    variant_count = product.variants.count()
    
    try:
        product.delete()
        return Response({
            'message': f'Product "{product_name}" deleted successfully',
            'details': f'Also deleted {variant_count} associated variants'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Failed to delete product',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_get_product(request, product_id):
    """
    Admin-only API endpoint to get detailed product information
    """
    product = get_object_or_404(Product, id=product_id)
    serializer = ProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_list_products(request):
    """
    Admin-only API endpoint to list all products with filtering options
    
    Query parameters:
    - category: Filter by category ID
    - is_available: Filter by availability (true/false)
    - search: Search in product name and description
    """
    products = Product.objects.select_related('category').prefetch_related('variants')
    
    # Apply filters
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    is_available = request.GET.get('is_available')
    if is_available is not None:
        is_available_bool = is_available.lower() == 'true'
        products = products.filter(is_available=is_available_bool)
    
    search = request.GET.get('search')
    if search:
        products = products.filter(
            name__icontains=search
        ) | products.filter(
            description__icontains=search
        )
    
    serializer = ProductSerializer(products, many=True)
    return Response({
        'count': products.count(),
        'products': serializer.data
    }, status=status.HTTP_200_OK)


# Variant Admin APIs
@api_view(['POST'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_add_variant(request):
    """
    Admin-only API endpoint to add new variants
    
    Required fields:
    - product: Product ID
    - size: Variant size
    - price: Variant price
    - type: Variant type
    
    Optional fields:
    - description: Variant description
    - is_available: Boolean (default: True)
    """
    serializer = AdminVariantSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            variant = serializer.save()
            return Response({
                'message': 'Variant created successfully',
                'variant': AdminVariantSerializer(variant).data
            }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({
                'error': 'Database integrity error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_update_variant(request, variant_id):
    """
    Admin-only API endpoint to update existing variants
    
    PUT: Full update (all fields required)
    PATCH: Partial update (only provided fields updated)
    """
    variant = get_object_or_404(Variant, id=variant_id)
    
    # Use partial=True for PATCH requests
    partial = request.method == 'PATCH'
    serializer = AdminVariantSerializer(variant, data=request.data, partial=partial)
    
    if serializer.is_valid():
        try:
            updated_variant = serializer.save()
            return Response({
                'message': 'Variant updated successfully',
                'variant': AdminVariantSerializer(updated_variant).data
            }, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({
                'error': 'Database integrity error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_delete_variant(request, variant_id):
    """
    Admin-only API endpoint to delete variants
    """
    variant = get_object_or_404(Variant, id=variant_id)
    
    # Store variant info for response
    variant_info = f"{variant.product.name} - {variant.size} - {variant.type}"
    
    try:
        variant.delete()
        return Response({
            'message': f'Variant "{variant_info}" deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Failed to delete variant',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_get_variant(request, variant_id):
    """
    Admin-only API endpoint to get detailed variant information
    """
    variant = get_object_or_404(Variant, id=variant_id)
    serializer = AdminVariantSerializer(variant)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_list_variants(request):
    """
    Admin-only API endpoint to list all variants with filtering options
    
    Query parameters:
    - product: Filter by product ID
    - is_available: Filter by availability (true/false)
    - type: Filter by variant type
    """
    variants = Variant.objects.select_related('product')
    
    # Apply filters
    product_id = request.GET.get('product')
    if product_id:
        variants = variants.filter(product_id=product_id)
    
    is_available = request.GET.get('is_available')
    if is_available is not None:
        is_available_bool = is_available.lower() == 'true'
        variants = variants.filter(is_available=is_available_bool)
    
    variant_type = request.GET.get('type')
    if variant_type:
        variants = variants.filter(type__icontains=variant_type)
    
    serializer = AdminVariantSerializer(variants, many=True)
    return Response({
        'count': variants.count(),
        'variants': serializer.data
    }, status=status.HTTP_200_OK)


# Category Admin APIs
@api_view(['POST'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_add_category(request):
    """
    Admin-only API endpoint to add new categories

    Required fields:
    - name: Category name (unique)
    - description: Category description
    - type: Array of category types
    - is_available: Boolean (default: True)
    """
    serializer = AdminCategorySerializer(data=request.data)

    if serializer.is_valid():
        try:
            category = serializer.save()
            return Response({
                'message': 'Category created successfully',
                'category': serializer.data
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({
                'error': 'A category with this name already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'error': 'Invalid data provided',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_update_category(request, category_id):
    """
    Admin-only API endpoint to update existing categories

    PUT: Full update (all fields required)
    PATCH: Partial update (only provided fields updated)
    """
    category = get_object_or_404(Category, id=category_id)

    # Use partial=True for PATCH requests
    partial = request.method == 'PATCH'
    serializer = AdminCategorySerializer(category, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            updated_category = serializer.save()
            return Response({
                'message': 'Category updated successfully',
                'category': serializer.data
            }, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({
                'error': 'A category with this name already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'error': 'Invalid data provided',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_delete_category(request, category_id):
    """
    Admin-only API endpoint to delete categories
    """
    category = get_object_or_404(Category, id=category_id)

    # Check if category has associated products
    if category.product_set.exists():
        return Response({
            'error': 'Cannot delete category with associated products',
            'products_count': category.product_set.count()
        }, status=status.HTTP_400_BAD_REQUEST)

    category_name = category.name
    category.delete()

    return Response({
        'message': f'Category "{category_name}" deleted successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_get_category(request, category_id):
    """
    Admin-only API endpoint to get detailed category information
    """
    category = get_object_or_404(Category, id=category_id)
    serializer = AdminCategorySerializer(category)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_list_categories(request):
    """
    Admin-only API endpoint to list all categories with filtering options

    Query parameters:
    - is_available: Filter by availability (true/false)
    - search: Search in category name and description
    """
    categories = Category.objects.all()

    # Filter by availability
    is_available = request.GET.get('is_available')
    if is_available is not None:
        is_available = is_available.lower() == 'true'
        categories = categories.filter(is_available=is_available)

    # Search functionality
    search = request.GET.get('search')
    if search:
        categories = categories.filter(
            name__icontains=search
        ) | categories.filter(
            description__icontains=search
        )

    serializer = AdminCategorySerializer(categories, many=True)
    return Response({
        'count': categories.count(),
        'categories': serializer.data
    }, status=status.HTTP_200_OK)


# Tag Admin APIs
@api_view(['POST'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_add_tag(request):
    """
    Admin-only API endpoint to add new tags

    Required fields:
    - name: Tag name (unique)
    - description: Tag description
    - type: Array of tag types
    - is_available: Boolean (default: True)
    """
    serializer = AdminTagSerializer(data=request.data)

    if serializer.is_valid():
        try:
            tag = serializer.save()
            return Response({
                'message': 'Tag created successfully',
                'tag': serializer.data
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({
                'error': 'A tag with this name already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'error': 'Invalid data provided',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_update_tag(request, tag_id):
    """
    Admin-only API endpoint to update existing tags

    PUT: Full update (all fields required)
    PATCH: Partial update (only provided fields updated)
    """
    tag = get_object_or_404(Tag, id=tag_id)

    # Use partial=True for PATCH requests
    partial = request.method == 'PATCH'
    serializer = AdminTagSerializer(tag, data=request.data, partial=partial)

    if serializer.is_valid():
        try:
            tag = serializer.save()
            return Response({
                'message': 'Tag updated successfully',
                'tag': serializer.data
            }, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({
                'error': 'A tag with this name already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'error': 'Invalid data provided',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_delete_tag(request, tag_id):
    """
    Admin-only API endpoint to delete tags
    """
    tag = get_object_or_404(Tag, id=tag_id)

    # Check if tag is used in any products' sub_category field
    products_using_tag = Product.objects.filter(sub_category__contains=[tag.name])
    if products_using_tag.exists():
        return Response({
            'error': 'Cannot delete tag that is used in products',
            'products_count': products_using_tag.count()
        }, status=status.HTTP_400_BAD_REQUEST)

    tag_name = tag.name
    tag.delete()

    return Response({
        'message': f'Tag "{tag_name}" deleted successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_get_tag(request, tag_id):
    """
    Admin-only API endpoint to get detailed tag information
    """
    tag = get_object_or_404(Tag, id=tag_id)
    serializer = AdminTagSerializer(tag)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_list_tags(request):
    """
    Admin-only API endpoint to list all tags with filtering options

    Query parameters:
    - is_available: Filter by availability (true/false)
    - search: Search in tag name and description
    """
    tags = Tag.objects.all()

    # Filter by availability
    is_available = request.GET.get('is_available')
    if is_available is not None:
        is_available = is_available.lower() == 'true'
        tags = tags.filter(is_available=is_available)

    # Search functionality
    search = request.GET.get('search')
    if search:
        tags = tags.filter(
            name__icontains=search
        ) | tags.filter(
            description__icontains=search
        )

    serializer = AdminTagSerializer(tags, many=True)
    return Response({
        'count': tags.count(),
        'tags': serializer.data
    }, status=status.HTTP_200_OK)


# Product Image Upload API
@api_view(['POST'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_upload_product_image(request):
    """
    Admin-only API endpoint to upload images for products

    Required fields:
    - product_id: ID of the product to upload image for
    - image: Image file to upload

    Optional fields:
    - default: Boolean (if true, saves as 'main' filename)
    - Note: Images are saved in random folder names for organization
    """
    try:
        # Get product_id from request
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({
                'error': 'product_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate product exists
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'error': f'Product with id {product_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get image file from request
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({
                'error': 'image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_extension = os.path.splitext(image_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return Response({
                'error': f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get optional parameters
        is_default = request.data.get('default', 'false').lower() == 'true'
        # get relative path (includes random folder for non-default images)
        rel_path = get_rel_path(product_id, product.name, is_default)

        # Determine filename
        if is_default:
            filename = f"main{file_extension}"
        else:
            # Use original filename or generate one
            original_name = os.path.splitext(image_file.name)[0]
            filename = f"{original_name}{file_extension}"

        # Create full directory path
        full_dir_path = os.path.join(settings.MEDIA_ROOT, rel_path)

        # Create directory if it doesn't exist
        os.makedirs(full_dir_path, exist_ok=True)

        # Save file
        file_path = os.path.join(full_dir_path, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # Create API URL for the image
        image_url = f"/api/common/{rel_path}/{filename}"

        # Update product's image_urls field - always maintain as list
        if isinstance(product.image_urls, list):
            current_urls = product.image_urls
        elif isinstance(product.image_urls, str):
            try:
                current_urls = json.loads(product.image_urls) if product.image_urls else []
            except (json.JSONDecodeError, TypeError):
                current_urls = []
        else:
            current_urls = []

        # If this is a default image, remove any existing main images
        if is_default:
            current_urls = [url for url in current_urls if '/main.' not in url]

        # Add new image URL if not already present
        if image_url not in current_urls:
            current_urls.append(image_url)

        # Always save as list (never JSON string)
        product.image_urls = current_urls
        product.save()

        # Extract folder identifier from the URL for response
        # URL format: /api/common/images/products/<product_name_id>/<folder_id>/<filename>
        url_parts = image_url.split('/')
        if len(url_parts) >= 6:
            folder_id = url_parts[5]  # Get the folder identifier part
        else:
            folder_id = "main"  # Default fallback

        return Response({
            'message': 'Image uploaded successfully',
            'image_url': image_url,
            'product_name': product.name,
            'is_default': is_default,
            'folder_id': folder_id,
            'total_images': len(current_urls)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Failed to upload image: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Product Image Delete API
@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_delete_product_image(request):
    """
    Admin-only API endpoint to delete images from products

    Required fields:
    - product_id: ID of the product to delete image from
    - image_url: URL of the image to delete (from product.image_urls)

    This API will:
    1. Remove the image URL from product.image_urls
    2. Delete the physical file and directory from media storage
    3. Clean up empty parent directories if needed
    """
    try:
        # Get required fields
        product_id = request.data.get('product_id')
        image_url = request.data.get('image_url')

        # Validate required fields
        if not product_id:
            return Response({
                'error': 'product_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not image_url:
            return Response({
                'error': 'image_url is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Parse current image URLs - handle both JSON string and Python list formats
        if isinstance(product.image_urls, list):
            current_images = product.image_urls
        elif isinstance(product.image_urls, str):
            try:
                current_images = json.loads(product.image_urls)
            except (json.JSONDecodeError, TypeError):
                current_images = []
        else:
            current_images = []

        # Check if image URL exists in product
        if image_url not in current_images:
            return Response({
                'error': 'Image URL not found in product images'
            }, status=status.HTTP_404_NOT_FOUND)

        # Convert image URL to file path
        # URL format: /api/common/images/products/<product_name_id>/<random_folder>/<image_name>
        # File path: media/images/products/<product_name_id>/<random_folder>/<image_name>
        if image_url.startswith('/api/common/images/'):
            file_path = image_url.replace('/api/common/images/', 'media/images/')
            full_file_path = os.path.join(settings.MEDIA_ROOT, file_path.replace('media/', ''))
        else:
            return Response({
                'error': 'Invalid image URL format'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete physical file if it exists
        file_deleted = False
        if os.path.exists(full_file_path):
            try:
                os.remove(full_file_path)
                file_deleted = True
            except OSError as e:
                return Response({
                    'error': f'Failed to delete file: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Clean up empty directories
        # Get the random folder directory containing the file
        random_folder_dir = os.path.dirname(full_file_path)
        try:
            # Remove random folder directory if it's empty
            if os.path.exists(random_folder_dir) and not os.listdir(random_folder_dir):
                os.rmdir(random_folder_dir)

                # Also try to remove parent product directory if it's empty
                product_dir = os.path.dirname(random_folder_dir)
                if os.path.exists(product_dir) and not os.listdir(product_dir):
                    os.rmdir(product_dir)
        except OSError:
            # Directory not empty or other error, continue anyway
            pass

        # Remove URL from product image_urls
        current_images.remove(image_url)

        # Always save as list (never JSON string)
        product.image_urls = current_images
        product.save()

        return Response({
            'message': 'Image deleted successfully',
            'deleted_image_url': image_url,
            'product_name': product.name,
            'file_deleted': file_deleted,
            'remaining_images': len(current_images),
            'updated_image_urls': current_images
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Failed to delete image: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
