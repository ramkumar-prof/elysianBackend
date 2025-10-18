"""
Admin-only views for managing products and variants
"""

from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from common.views.common import JWTOnlyAuthentication
from user.permissions import IsAdminUser
from ..models import Product, Variant, Category
from ..serializers import AdminProductSerializer, AdminVariantSerializer, AdminCategorySerializer, ProductSerializer


# Product Admin APIs
@api_view(['POST'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_add_product(request):
    """
    Admin-only API endpoint to add new products
    
    Required fields:
    - name: Product name
    - category: Category ID
    
    Optional fields:
    - description: Product description
    - image_urls: Array of image URLs
    - discount: Discount percentage (0-100)
    - is_available: Boolean (default: True)
    - sub_category: Array of subcategory tags
    """
    serializer = AdminProductSerializer(data=request.data)
    
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
    Admin-only API endpoint to update existing products
    
    PUT: Full update (all fields required)
    PATCH: Partial update (only provided fields updated)
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Use partial=True for PATCH requests
    partial = request.method == 'PATCH'
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
