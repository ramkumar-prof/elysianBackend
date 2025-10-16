from rest_framework import serializers
from .models import RestaurentMenu

class RestaurentMenuSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product.name')
    description = serializers.CharField(source='product.description')
    variants = serializers.SerializerMethodField()
    images_url = serializers.JSONField(source='product.image_urls')
    discount_percentage = serializers.DecimalField(source='product.discount', max_digits=5, decimal_places=2)
    veg = serializers.BooleanField(source='is_veg')
    category = serializers.CharField(source='product.category.name')
    sub_categories = serializers.JSONField(source='product.sub_category')

    class Meta:
        model = RestaurentMenu
        fields = ['id', 'name', 'description', 'variants', 'images_url', 
                 'discount_percentage', 'is_available', 'veg', 'category', 'sub_categories']

    def get_variants(self, obj):
        # Get variants using the foreign key relationship
        variants = obj.product.variants.all()
        result = []
        
        for variant in variants:
            is_default = obj.default_variant and obj.default_variant.id == variant.id
            result.append({
                'size': variant.size,
                'price': float(variant.price),
                'size_description': variant.description,
                'default': is_default
            })
        
        return result
