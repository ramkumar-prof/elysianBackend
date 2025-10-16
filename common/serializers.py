from rest_framework import serializers
from .models import Category, Variant, Product, Tag, Cart

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_available', 'type']

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'size', 'price', 'description', 'is_available', 'type']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'variant', 'quantity', 'session_id', 'created_at', 'updated_at']
