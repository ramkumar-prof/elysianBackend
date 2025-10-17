from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .common import SessionOrJWTAuthentication
from ..models import Cart, CartItem, Product, Variant
from ..serializers import CartSerializer, CartItemSerializer

@api_view(['GET', 'POST'])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def cart_view(request):
    """
    Combined cart view:
    GET: Get cart items for authenticated user or session
    POST: Add item to cart (requires authentication)
    """
    if request.method == 'GET':
        return get_cart_items(request)
    elif request.method == 'POST':
        return add_to_cart(request)


def get_cart_items(request):
    """
    Get cart items for authenticated user or session
    """
    # Get or create cart for user/session
    cart = None
    if request.user and request.user.is_authenticated:
        # Get cart for authenticated user
        cart = Cart.objects.filter(user=request.user).first()
    else:
        # Get cart for session
        session_id = request.session.session_key
        if not session_id:
            return Response({'cart_items': []}, status=status.HTTP_200_OK)
        cart = Cart.objects.filter(session_id=session_id).first()

    if not cart:
        return Response({'cart_items': []}, status=status.HTTP_200_OK)

    # Get cart items for this cart
    cart_items = cart.items.select_related('product', 'variant')

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
            'cart_item_id': cart_item.id,
            'cart_id': cart_item.cart.id,
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


def add_to_cart(request):
    """
    Add/Update/Remove item in cart
    Params:
        - variant_id (required): ID of the product variant
        - quantity (required):
            * Positive integer: Add/update item with this quantity
            * 0: Remove item from cart
            * Negative: Returns error
        - product_id (optional): Can be derived from variant

    Returns unified response format same as GET cart endpoint plus message field
    """
    # Allow both authenticated users and session-based users
    # No authentication check needed as SessionOrJWTAuthentication handles this

    try:
        # Get request data
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity', 1)

        # Validate required fields - variant_id is required, product_id can be derived
        if not variant_id:
            return Response({
                'message': 'variant_id is required',
                'cart_items': [],
                'total_items': 0,
                'total_amount': 0
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity < 0:
                return Response({
                    'message': 'quantity cannot be negative',
                    'cart_items': [],
                    'total_items': 0,
                    'total_amount': 0
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                'message': 'quantity must be a valid integer',
                'cart_items': [],
                'total_items': 0,
                'total_amount': 0
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get or validate product and variant
        try:
            # Get variant first
            variant = Variant.objects.select_related('product').get(id=variant_id, is_available=True)
            product = variant.product

            # If product_id was provided, validate it matches
            if product_id and product.id != int(product_id):
                return Response({
                    'message': 'Product ID does not match variant\'s product',
                    'cart_items': [],
                    'total_items': 0,
                    'total_amount': 0
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if product is available
            if not product.is_available:
                return Response({
                    'message': 'Product not available',
                    'cart_items': [],
                    'total_items': 0,
                    'total_amount': 0
                }, status=status.HTTP_404_NOT_FOUND)

        except Variant.DoesNotExist:
            return Response({
                'message': 'Variant not found or not available',
                'cart_items': [],
                'total_items': 0,
                'total_amount': 0
            }, status=status.HTTP_404_NOT_FOUND)

        # Get or create cart for user or session
        cart = None
        if request.user and request.user.is_authenticated:
            # Get cart for authenticated user
            cart = Cart.get_or_create_for_user(request.user)
        else:
            # Get cart for session user
            if not request.session.session_key:
                request.session.create()
            session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_id=session_id,
                user=None
            )

        # Handle cart item creation/update/deletion based on quantity
        if quantity == 0:
            # Remove item from cart if quantity is 0
            try:
                cart_item = CartItem.objects.get(
                    cart=cart,
                    product=product,
                    variant=variant
                )
                cart_item.delete()
                message = 'Item removed from cart successfully'
            except CartItem.DoesNotExist:
                # Item doesn't exist, nothing to remove
                message = 'Item was not in cart'
        else:
            # Add or update item in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                defaults={'quantity': quantity}
            )

            if not created:
                # Update existing item quantity
                cart_item.quantity = quantity
                cart_item.save()

            message = 'Item added to cart successfully'

        # Return same format as GET cart endpoint with success message
        # Get cart items for this cart
        cart_items = cart.items.select_related('product', 'variant')

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
                'cart_item_id': cart_item.id,
                'cart_id': cart_item.cart.id,
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
            'message': message,
            'cart_items': cart_data,
            'total_items': len(cart_data),
            'total_amount': round(total_amount, 2)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message': f'Failed to add item to cart: {str(e)}',
            'cart_items': [],
            'total_items': 0,
            'total_amount': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


