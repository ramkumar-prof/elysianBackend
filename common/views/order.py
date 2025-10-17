from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import uuid

from ..models import Cart, Order, Payment, Product, Variant
from ..serializers import OrderSerializer, PaymentSerializer
from user.models import Address
from ..utils.payment_utils import initiate_payment, get_payment_status
from common.views.common import JWTOnlyAuthentication


@api_view(['POST'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def checkout(request):
    """
    Process checkout for all cart items of the user
    Creates order and initiates payment
    """
    address_id = request.data.get('address_id')

    # Validate required fields
    if not address_id:
        return Response({
            'error': 'address_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Verify address belongs to the user
    try:
        address = Address.objects.get(id=address_id, user=request.user)
    except Address.DoesNotExist:
        return Response({
            'error': 'Address not found or does not belong to user'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Get user's cart
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return Response({
                'error': 'Cart not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all cart items for the user's cart
        cart_items = cart.items.select_related('product', 'variant')

        if not cart_items.exists():
            return Response({
                'error': 'Cart is empty'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate total amount and prepare order items
        total_amount = 0
        order_items = []
        
        for cart_item in cart_items:
            # Calculate item total (price * quantity - discount)
            item_price = int(cart_item.variant.price * 100)  # Convert to paisa
            item_discount = int(cart_item.product.discount * cart_item.quantity * 100)  # Convert to paisa
            item_total = (item_price * cart_item.quantity) - item_discount
            
            total_amount += item_total
            
            # Prepare order item data
            order_items.append({
                'product': cart_item.product.id,
                'variant': cart_item.variant.id,
                'quantity': cart_item.quantity,
                'price': item_price,
                'discount': item_discount,
                'product_name': cart_item.product.name,
                'variant_size': cart_item.variant.size,
                'variant_type': cart_item.variant.type
            })
        
        # Format delivery address from the verified address object
        delivery_address = f"{address.address}, {address.city}, {address.state} - {address.pincode}"
        
        # Create order and payment in a transaction
        with transaction.atomic():
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
            
            # Generate unique order ID for payment gateway
            gateway_order_id = f"ORDER_{order.id}_{uuid.uuid4().hex[:8]}"
            
            # Prepare callback URL
            callback_url = f"http://localhost:4200/order/status/{order.id}"
            
            try:
                # Initiate payment using payment_utils
                payment_response = initiate_payment(
                    amount=total_amount,
                    order_id=gateway_order_id,
                    callback_url=callback_url
                )
                
                # Extract data from payment response
                # Note: Adjust these field names based on actual PhonePe response structure
                gateway_response_order_id = getattr(payment_response, 'order_id', gateway_order_id)
                payment_state = getattr(payment_response, 'state', 'PENDING')
                redirect_url = getattr(payment_response, 'redirect_url', '')
                expire_at = getattr(payment_response, 'expire_at', '')
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    amount=total_amount,
                    transaction_id=gateway_order_id,
                    gateway_order_id=gateway_response_order_id,
                    payment_status=payment_state,
                    payment_method='UPI',  # Default, will be updated based on user selection
                    additional_info={
                        'redirect_url': redirect_url,
                        'expire_at': expire_at,
                        'callback_url': callback_url
                    }
                )
                
                # Update order with payment ID
                order.payment_id = payment.id
                order.save()
                
                # Clear cart items after successful order creation
                cart_items.delete()
                
                return Response({
                    'success': True,
                    'order_id': order.id,
                    'redirect_url': redirect_url,
                    'message': 'Order created successfully'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as payment_error:
                # If payment initiation fails, mark order as failed
                order.payment_status = 'FAILED'
                order.save()
                
                return Response({
                    'error': 'Payment initiation failed',
                    'details': str(payment_error)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
    except Exception as e:
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
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if order payment status is pending and update from gateway
    if order.payment_status == 'PENDING':
        try:
            # Get latest payment status from gateway
            gateway_response = get_payment_status(str(order.id))

            if gateway_response and hasattr(gateway_response, 'data'):
                gateway_data = gateway_response.data

                # Update order payment status based on gateway response
                if hasattr(gateway_data, 'state'):
                    gateway_status = gateway_data.state

                    # Map gateway status to our status
                    status_mapping = {
                        'COMPLETED': 'COMPLETED',
                        'FAILED': 'FAILED',
                        'PENDING': 'PENDING'
                    }

                    new_payment_status = status_mapping.get(gateway_status, 'PENDING')

                    # Update order if status changed
                    if order.payment_status != new_payment_status:
                        order.payment_status = new_payment_status

                        # Update order status based on payment status
                        if new_payment_status == 'COMPLETED':
                            order.order_status = 'CONFIRMED'
                        elif new_payment_status == 'FAILED':
                            order.order_status = 'CANCELLED'

                        order.save()

                        # Update associated payment record
                        payment = Payment.objects.filter(order=order).first()
                        if payment:
                            payment.payment_status = new_payment_status

                            # Update additional info with latest gateway data
                            if hasattr(gateway_data, 'transaction_id'):
                                payment.transaction_id = gateway_data.transaction_id

                            # Update additional_info with gateway response
                            additional_info = payment.additional_info or {}
                            additional_info.update({
                                'last_checked': timezone.now().isoformat(),
                                'gateway_response': str(gateway_data)
                            })
                            payment.additional_info = additional_info
                            payment.save()

        except Exception as e:
            # Log error but don't fail the request
            print(f"Error checking payment status: {str(e)}")

    # Serialize and return updated data
    serializer = OrderSerializer(order)

    # Get associated payments
    payments = Payment.objects.filter(order=order)
    payment_serializer = PaymentSerializer(payments, many=True)

    return Response({
        'order': serializer.data,
        'payments': payment_serializer.data,
        'status_updated': order.payment_status != 'PENDING'  # Indicate if status was checked/updated
    }, status=status.HTTP_200_OK)
