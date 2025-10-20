from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import uuid
import logging

from ..models import Cart, Order, Payment, Product, Variant
from ..serializers import OrderSerializer, PaymentSerializer
from user.models import Address
from ..utils.payment_utils import initiate_payment, get_payment_status
from common.views.common import JWTOnlyAuthentication

# Configure logger for checkout operations
logger = logging.getLogger(__name__)


@api_view(['POST'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def checkout(request):
    """
    Process checkout for all cart items of the user
    Creates order and initiates payment
    """
    user_id = getattr(request.user, 'id', 'anonymous')
    logger.info(f"🛒 Checkout initiated for user {user_id}")

    address_id = request.data.get('address_id')

    # Validate required fields
    if not address_id:
        logger.warning(f"❌ Checkout failed for user {user_id}: address_id is required")
        return Response({
            'error': 'address_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Verify address belongs to the user
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        logger.info(f"✅ Address {address_id} validated for user {user_id}")
    except Address.DoesNotExist:
        logger.error(f"❌ Address {address_id} not found or does not belong to user {user_id}")
        return Response({
            'error': 'Address not found or does not belong to user'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Get user's cart
        cart = Cart.objects.filter(user=request.user).first()
        logger.info(f"🛒 Fetching cart for user {user_id}")

        if not cart:
            logger.warning(f"❌ No cart found for user {user_id}")
            return Response({
                'error': 'Cart not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all cart items for the user's cart
        cart_items = cart.items.select_related('product', 'variant')
        cart_items_count = cart_items.count()
        logger.info(f"📦 Found {cart_items_count} items in cart for user {user_id}")

        if not cart_items.exists():
            logger.warning(f"❌ Cart is empty for user {user_id}")
            return Response({
                'error': 'Cart is empty'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate total amount and prepare order items
        total_amount = 0
        order_items = []
        logger.info(f"💰 Calculating order total for user {user_id}")

        for cart_item in cart_items:
            item_price = cart_item.variant.price * 100
            per_item = item_price - item_price * cart_item.product.discount / 100
            item_total = per_item * cart_item.quantity # conver to paisa

            total_amount += item_total
            logger.debug(f"📦 Item: {cart_item.product.name} x{cart_item.quantity} = ₹{item_total/100:.2f}")

            # Prepare order item data
            order_items.append({
                'product': cart_item.product.id,
                'variant': cart_item.variant.id,
                'quantity': cart_item.quantity,
                'price': int(item_price),
                'discount': int(cart_item.product.discount),
                'product_name': cart_item.product.name,
                'variant_size': cart_item.variant.size,
                'variant_type': cart_item.variant.type
            })

        logger.info(f"💰 Total order amount: ₹{total_amount/100:.2f} for user {user_id}")

        # Format delivery address from the verified address object
        delivery_address = f"{address.address}, {address.city}, {address.state} - {address.pincode}"
        logger.info(f"📍 Delivery address set for user {user_id}: {delivery_address[:50]}...")
        
        # Create order and payment in a transaction
        logger.info(f"🔄 Starting transaction for user {user_id}")
        try:
            with transaction.atomic():
                logger.info(f"📝 Creating order for user {user_id}")
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    items=order_items,
                    order_amount=total_amount,
                    payment_status='PENDING',
                    order_status='PENDING',
                    delivery_address=delivery_address,
                    additional_info={
                        'address_id': address_id,
                        'total_items': len(order_items)
                    }
                )
                logger.info(f"✅ Order {order.id} created successfully for user {user_id}")

                # Generate unique order ID for payment gateway
                gateway_order_id = f"ORDER_{order.id}_{uuid.uuid4().hex[:8]}"
                logger.info(f"🔑 Generated gateway order ID: {gateway_order_id}")

                # Prepare callback URL
                callback_url = f"http://localhost:4200/order/status/{order.id}"
                logger.info(f"🔗 Callback URL set: {callback_url}")

                # Initiate payment using payment_utils
                logger.info(f"💳 Initiating payment for order {order.id}, amount: ₹{total_amount/100:.2f}")
                payment_response = initiate_payment(
                    amount=total_amount,
                    order_id=gateway_order_id,
                    callback_url=callback_url
                )
                logger.info(f"✅ Payment initiated successfully for order {order.id}")

                # Extract data from payment response
                # Note: Adjust these field names based on actual PhonePe response structure
                gateway_response_order_id = getattr(payment_response, 'order_id', gateway_order_id)
                payment_state = getattr(payment_response, 'state', 'PENDING')
                redirect_url = getattr(payment_response, 'redirect_url', '')
                expire_at = getattr(payment_response, 'expire_at', '')

                logger.info(f"📊 Payment response - State: {payment_state}, Redirect URL: {redirect_url[:50] if redirect_url else 'None'}...")

                # Create payment record
                logger.info(f"💾 Creating payment record for order {order.id}")
                payment = Payment.objects.create(
                    order=order,
                    amount=total_amount,
                    transaction_id='',
                    gateway_order_id=gateway_order_id,
                    payment_status=payment_state,
                    payment_method='',  # Default, will be updated based on user selection
                    additional_info={
                        'redirect_url': redirect_url,
                        'expire_at': expire_at,
                        'callback_url': callback_url
                    }
                )
                logger.info(f"✅ Payment record {payment.id} created for order {order.id}")

                # Update order with payment ID
                order.payment_id = payment.id
                order.save()
                logger.info(f"🔗 Order {order.id} linked to payment {payment.id}")

                # Clear cart items after successful order creation
                cart_items.delete()
                logger.info(f"🧹 Cleared {cart_items_count} cart items for user {user_id}")

                logger.info(f"🎉 Checkout completed successfully for user {user_id}, order {order.id}")
                return Response({
                    'success': True,
                    'order_id': order.id,
                    'redirect_url': redirect_url,
                    'message': 'Order created successfully'
                }, status=status.HTTP_201_CREATED)

        except Exception as payment_error:
            # If payment initiation fails or any other error occurs
            logger.error(f"❌ Payment initiation failed for user {user_id}: {str(payment_error)}")
            logger.error(f"🔍 Payment error details: {type(payment_error).__name__}: {payment_error}")
            return Response({
                'error': 'Payment initiation failed',
                'details': str(payment_error)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"❌ Checkout failed for user {user_id}: {str(e)}")
        logger.error(f"🔍 Checkout error details: {type(e).__name__}: {e}")
        return Response({
            'error': 'Checkout failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def get_user_orders(request):
    """
    Get all orders for the authenticated user
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    
    return Response({
        'orders': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def get_order_details(request, order_id):
    """
    Get specific order details for the authenticated user
    Checks payment gateway for latest status if order is pending
    """
    user_id = getattr(request.user, 'id', 'anonymous')
    logger.info(f"📋 Fetching order details for order {order_id}, user {user_id}")

    order = get_object_or_404(Order, id=order_id, user=request.user)
    # get payment status
    payment = get_object_or_404(Payment, order=order)
    logger.info(f"📊 Current order status: {order.order_status}, payment status: {order.payment_status}")

    # Check if order payment status is pending and update from gateway
    if order.payment_status == 'PENDING':
        logger.info(f"🔄 Checking payment status from gateway for order {order_id}")
        try:
            # Get latest payment status from gateway
            gateway_response = get_payment_status(str(payment.gateway_order_id))
            logger.info(f"📡 Gateway response received for order {order_id}: {gateway_response}")
            print("Payment status response: ", gateway_response)

            # Handle both dictionary responses (our error format) and PhonePe response objects
            if gateway_response:
                logger.info(f"📊 Updating payment status from gateway for order {order_id}")
                payment.payment_status = gateway_response.state

                if len(gateway_response.payment_details) > 0:
                    payment_details = gateway_response.payment_details[0]
                    payment.transaction_id = payment_details.transaction_id
                    payment.payment_method = payment_details.payment_mode.value
                    additional_info = {
                        "timestamp": payment_details.timestamp,
                        "error_code": payment_details.error_code,
                        "error_detail": payment_details.detailed_error_code
                    }
                    payment.additional_info = additional_info
                    logger.info(f"💳 Payment details updated - Transaction ID: {payment_details.transaction_id}, Method: {payment_details.payment_mode.value}")

                payment.save()
                order.payment_status = payment.payment_status
                logger.info(f"📊 Payment status updated to: {payment.payment_status}")

                if order.payment_status == 'COMPLETED':
                    order.order_status = 'CONFIRMED'
                    logger.info(f"✅ Order {order_id} confirmed - payment completed")
                elif order.payment_status == 'FAILED':
                    order.order_status = 'CANCELLED'
                    logger.warning(f"❌ Order {order_id} cancelled - payment failed")

                order.save()
                logger.info(f"📊 Order status updated to: {order.order_status}")
            else:
                logger.warning(f"⚠️ No valid gateway response received for order {order_id}")

        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"❌ Error checking payment status for order {order_id}: {str(e)}")
            logger.error(f"🔍 Payment status check error details: {type(e).__name__}: {e}")
            print(f"Error checking payment status: {str(e)}")

    # Serialize and return updated data
    serializer = OrderSerializer(order)
    return Response({
        'order': serializer.data,
        'status_updated': order.payment_status != 'PENDING'  # Indicate if status was checked/updated
    }, status=status.HTTP_200_OK)
