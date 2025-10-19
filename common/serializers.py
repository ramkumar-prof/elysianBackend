from rest_framework import serializers
from .models import Category, Tag, Variant, Product, Cart, CartItem, Order, Payment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_available', 'type']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'is_available', 'type']

class AdminCategorySerializer(serializers.ModelSerializer):
    """Admin serializer for category CRUD operations"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_available', 'type']

    def validate_name(self, value):
        """Validate that category name is unique"""
        if Category.objects.filter(name__iexact=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value

    def validate_type(self, value):
        """Validate that type is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Type must be a list.")
        return value

class AdminTagSerializer(serializers.ModelSerializer):
    """Admin serializer for tag CRUD operations"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'is_available', 'type']

    def validate_name(self, value):
        """Validate that tag name is unique"""
        if Tag.objects.filter(name__iexact=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("A tag with this name already exists.")
        return value

    def validate_type(self, value):
        """Validate that type is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Type must be a list.")
        return value

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['id', 'size', 'price', 'description', 'is_available', 'type']

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model with category details"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    variants = VariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_urls', 'discount', 'is_available',
                 'category', 'category_name', 'sub_category', 'variants']

# Admin serializers for CRUD operations
class AdminProductSerializer(serializers.ModelSerializer):
    """Admin serializer for all product operations with exact DB fields"""
    variants = VariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_urls', 'discount', 'is_available',
                 'category', 'sub_category', 'variants']

    def validate_category(self, value):
        """Validate that category exists and is available"""
        if not value.is_available:
            raise serializers.ValidationError("Cannot assign product to an unavailable category.")
        return value

    def validate_discount(self, value):
        """Validate discount is within acceptable range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100.")
        return value


class AdminProductWithVariantsSerializer(serializers.ModelSerializer):
    """Admin serializer for product operations with variant management"""
    variants = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True,
        help_text="List of variant objects with fields: size, price, description, is_available, type"
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_urls', 'discount', 'is_available',
                 'category', 'sub_category', 'variants']

    def validate_category(self, value):
        """Validate that category exists and is available"""
        if not value.is_available:
            raise serializers.ValidationError("Cannot assign product to an unavailable category.")
        return value

    def validate_discount(self, value):
        """Validate discount is within acceptable range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100.")
        return value

    def validate_variants(self, value):
        """Validate variants data"""
        if not value:
            raise serializers.ValidationError("At least one variant is required.")

        if len(value) == 0:
            raise serializers.ValidationError("At least one variant is required.")

        # Validate each variant
        for i, variant_data in enumerate(value):
            # Required fields
            required_fields = ['size', 'price', 'is_available']
            for field in required_fields:
                if field not in variant_data:
                    raise serializers.ValidationError(f"Variant {i+1}: '{field}' is required.")

            # Validate price
            try:
                price = float(variant_data['price'])
                if price <= 0:
                    raise serializers.ValidationError(f"Variant {i+1}: Price must be greater than 0.")
            except (ValueError, TypeError):
                raise serializers.ValidationError(f"Variant {i+1}: Price must be a valid number.")

            # Validate is_available
            if not isinstance(variant_data['is_available'], bool):
                raise serializers.ValidationError(f"Variant {i+1}: is_available must be a boolean.")

            # Set defaults for optional fields
            variant_data.setdefault('description', '')
            variant_data.setdefault('type', '')

        # Check for duplicate size+type combinations
        size_type_combinations = []
        for variant_data in value:
            combination = (variant_data['size'], variant_data.get('type', ''))
            if combination in size_type_combinations:
                raise serializers.ValidationError(
                    f"Duplicate variant found: size '{variant_data['size']}' with type '{variant_data.get('type', '')}'"
                )
            size_type_combinations.append(combination)

        return value

    def create(self, validated_data):
        """Create product with variants"""
        variants_data = validated_data.pop('variants')

        # Ensure image_urls is always a list
        if 'image_urls' not in validated_data:
            validated_data['image_urls'] = []

        # Create product
        product = Product.objects.create(**validated_data)

        # Create variants
        for variant_data in variants_data:
            Variant.objects.create(product=product, **variant_data)

        return product

    def update(self, instance, validated_data):
        """Update product and manage variants"""
        variants_data = validated_data.pop('variants', None)

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update variants if provided
        if variants_data is not None:
            # Delete all existing variants
            instance.variants.all().delete()

            # Create new variants
            for variant_data in variants_data:
                Variant.objects.create(product=instance, **variant_data)

        return instance


class AdminVariantSerializer(serializers.ModelSerializer):
    """Admin serializer for creating/updating variants"""
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Variant
        fields = ['id', 'product', 'product_name', 'size', 'price', 'description',
                 'is_available', 'type']

    def validate_product(self, value):
        """Validate that product exists and is available"""
        if not value.is_available:
            raise serializers.ValidationError("Cannot create variant for an unavailable product.")
        return value

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate(self, data):
        """Cross-field validation for variant uniqueness"""
        product = data.get('product')
        size = data.get('size')
        variant_type = data.get('type')

        # Check for duplicate variants (same product, size, and type)
        if product and size and variant_type:
            existing_variant = Variant.objects.filter(
                product=product,
                size=size,
                type=variant_type
            )

            # Exclude current instance if updating
            if self.instance:
                existing_variant = existing_variant.exclude(id=self.instance.id)

            if existing_variant.exists():
                raise serializers.ValidationError(
                    f"A variant with size '{size}' and type '{variant_type}' already exists for this product."
                )

        return data

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
