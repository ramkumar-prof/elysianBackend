from rest_framework import serializers
from .models import Category, Variant, Product, Tag, Cart, CartItem, Order, Payment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_available', 'type']

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'size', 'price', 'description', 'is_available', 'type']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'variant', 'quantity', 'created_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'items', 'created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    transaction_id = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'items', 'order_amount',
            'payment_status', 'order_status', 'delivery_address',
            'transaction_id', 'payment_method', 'updated_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'payment_method', 'created_at', 'updated_at']

    def _get_latest_payment(self, obj):
        """
        Helper method to get the latest payment for the order.
        Caches the result to avoid multiple database calls.
        """
        if not hasattr(obj, '_cached_payment'):
            obj._cached_payment = obj.payments.first()  # Get the most recent payment (ordered by -created_at)
        return obj._cached_payment

    def get_transaction_id(self, obj):
        """
        Get the transaction_id from the associated payment.
        Returns the transaction_id of the most recent payment for this order.
        """
        payment = self._get_latest_payment(obj)
        return payment.transaction_id if payment else None

    def get_payment_method(self, obj):
        """
        Get the payment_method from the associated payment.
        Returns the payment_method of the most recent payment for this order.
        """
        payment = self._get_latest_payment(obj)
        return payment.payment_method if payment else None


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'transaction_id', 'gateway_order_id',
            'payment_status', 'payment_method', 'additional_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
