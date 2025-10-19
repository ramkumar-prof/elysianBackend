from rest_framework import serializers
from django.db import IntegrityError
from .models import RestaurentMenu
from common.models import Product, Variant, RestaurentEntity

class RestaurentMenuSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product.name')
    description = serializers.CharField(source='product.description')
    variants = serializers.SerializerMethodField()
    images_url = serializers.JSONField(source='product.image_urls')
    discount_percentage = serializers.DecimalField(source='product.discount', max_digits=5, decimal_places=2)
    veg = serializers.BooleanField(source='is_veg')
    category = serializers.CharField(source='product.category.name')
    sub_categories = serializers.JSONField(source='product.sub_category')
    product_id = serializers.IntegerField(source='product.id')

    class Meta:
        model = RestaurentMenu
        fields = ['id', 'name', 'description', 'variants', 'images_url', 
                 'discount_percentage', 'is_available', 'veg', 'category', 'sub_categories', 'product_id']

    def get_variants(self, obj):
        # Get only available variants using the foreign key relationship
        variants = obj.product.variants.filter(is_available=True)
        result = []

        for variant in variants:
            is_default = obj.default_variant and obj.default_variant.id == variant.id
            result.append({
                'variant_id': variant.id,
                'size': variant.size,
                'price': float(variant.price),
                'size_description': variant.description,
                'default': is_default
            })

        return result


class AddMenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for adding new menu items to restaurant
    """
    product_id = serializers.IntegerField()
    restaurent_id = serializers.IntegerField()
    default_variant_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = RestaurentMenu
        fields = ['product_id', 'restaurent_id', 'is_available', 'is_veg', 'default_variant_id']

    def validate_product_id(self, value):
        """Validate that the product exists"""
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product with this ID does not exist.")
        return value

    def validate_restaurent_id(self, value):
        """Validate that the restaurant exists"""
        try:
            RestaurentEntity.objects.get(id=value)
        except RestaurentEntity.DoesNotExist:
            raise serializers.ValidationError("Restaurant with this ID does not exist.")
        return value

    def validate_default_variant_id(self, value):
        """Validate that the variant exists and belongs to the product"""
        if value is not None:
            try:
                Variant.objects.get(id=value)
            except Variant.DoesNotExist:
                raise serializers.ValidationError("Variant with this ID does not exist.")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        product_id = attrs.get('product_id')
        restaurent_id = attrs.get('restaurent_id')
        default_variant_id = attrs.get('default_variant_id')

        # Check if menu item already exists for this restaurant and product
        if RestaurentMenu.objects.filter(
            product_id=product_id,
            restaurent_id=restaurent_id
        ).exists():
            raise serializers.ValidationError(
                "This product is already in the restaurant's menu."
            )

        # If default_variant_id is provided, ensure it belongs to the product
        if default_variant_id:
            try:
                variant = Variant.objects.get(id=default_variant_id)
                if variant.product_id != product_id:
                    raise serializers.ValidationError(
                        "The default variant must belong to the specified product."
                    )
            except Variant.DoesNotExist:
                raise serializers.ValidationError("Variant with this ID does not exist.")

        return attrs

    def create(self, validated_data):
        """Create new menu item with duplicate protection"""
        product_id = validated_data.pop('product_id')
        restaurent_id = validated_data.pop('restaurent_id')
        default_variant_id = validated_data.pop('default_variant_id', None)

        try:
            menu_item = RestaurentMenu.objects.create(
                product_id=product_id,
                restaurent_id=restaurent_id,
                default_variant_id=default_variant_id,
                **validated_data
            )
            return menu_item
        except IntegrityError:
            # Handle race condition where duplicate was created between validation and creation
            raise serializers.ValidationError(
                "This product is already in the restaurant's menu. Please refresh and try again."
            )
