from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .common import SessionOrJWTAuthentication
from ..models import Product, Category, Variant
from ..serializers import CategorySerializer, VariantSerializer

@api_view(['GET'])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def get_categories(request):
    """
    Get all categories
    """
    categories = Category.objects.filter(is_available=True)
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def get_product_variants(request, product_id):
    """
    Get variants for a specific product
    """
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        variants = Variant.objects.filter(product_id=product_id, is_available=True)
        
        variant_data = []
        for variant in variants:
            original_price = float(variant.price)
            discount_percentage = float(product.discount)
            discount_amount = (original_price * discount_percentage) / 100
            discounted_price = original_price - discount_amount
            
            variant_data.append({
                'variant_id': variant.id,
                'price': original_price,
                'discount': discount_percentage,
                'discounted_price': round(discounted_price, 2)
            })
        
        return Response(variant_data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Variant.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def get_product_pricing(request, product_id, variant_id):
    """
    Get price and discount for a specific product variant
    """
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        variant = Variant.objects.get(id=variant_id, product=product, is_available=True)
        
        original_price = float(variant.price)
        discount_percentage = float(product.discount)
        discount_amount = (original_price * discount_percentage) / 100
        final_price = original_price - discount_amount
        
        return Response({
            'product_id': product.id,
            'variant_id': variant.id,
            'original_price': original_price,
            'discount_percentage': discount_percentage,
            'discount_amount': round(discount_amount, 2),
            'final_price': round(final_price, 2),
            'currency': 'INR'
        }, status=status.HTTP_200_OK)
        
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Variant.DoesNotExist:
        return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
