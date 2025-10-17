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
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'items', 'order_amount', 'payment_id',
            'payment_status', 'order_status', 'delivery_address',
            'additional_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'transaction_id', 'gateway_order_id',
            'payment_status', 'payment_method', 'additional_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
