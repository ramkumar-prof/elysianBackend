from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .common import SessionOrJWTAuthentication
from ..models import Cart, Product, Variant
from ..serializers import CartSerializer

@api_view(['GET'])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def get_cart_items(request):
    """
    Get cart items for authenticated user or session
    """
    if request.user and request.user.is_authenticated:
        # Get cart items for authenticated user
        cart_items = Cart.objects.filter(user=request.user).select_related('product', 'variant')
    else:
        # Get cart items for session
        session_id = request.session.session_key

        if not session_id:
            return Response({'cart_items': []}, status=status.HTTP_200_OK)
        cart_items = Cart.objects.filter(session_id=session_id).select_related('product', 'variant')
    
    # Calculate pricing for each cart item
    cart_data = []
    total_amount = 0
    
    for cart_item in cart_items:
        original_price = float(cart_item.variant.price)
        discount_percentage = float(cart_item.product.discount)
        discount_amount = (original_price * discount_percentage) / 100
        discounted_price = original_price - discount_amount
        item_total = discounted_price * cart_item.quantity
        
        cart_data.append({
            'cart_id': cart_item.id,
            'product_id': cart_item.product.id,
            'product_name': cart_item.product.name,
            'variant_id': cart_item.variant.id,
            'variant_size': cart_item.variant.size,
            'quantity': cart_item.quantity,
            'price': original_price,
            'discount': discount_percentage,
            'discounted_price': round(discounted_price, 2),
            'item_total': round(item_total, 2)
        })
        total_amount += item_total
    
    return Response({
        'cart_items': cart_data,
        'total_items': len(cart_data),
        'total_amount': round(total_amount, 2)
    }, status=status.HTTP_200_OK)