from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    type = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    type = models.JSONField(default=list)  # Array of types
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_urls = models.JSONField(default=list)  # Array of image URLs
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.JSONField(default=list)  # Array of tags
    
    def __str__(self):
        return self.name

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    type = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.type}"

class RestaurentEntity(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('cart', 'product', 'variant')
        ]

    def __str__(self):
        return f"CartItem - Cart {self.cart.id} - {self.product.name} ({self.variant.size})"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(user__isnull=False) & models.Q(session_id__isnull=True)) |
                    (models.Q(user__isnull=True) & models.Q(session_id__isnull=False))
                ),
                name='cart_user_or_session_required'
            )
        ]

    def clean(self):
        if not self.user and not self.session_id:
            raise ValidationError("Either user or session_id must be provided")
        if self.user and self.session_id:
            raise ValidationError("Cannot have both user and session_id")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def cart_items(self):
        """Get all cart items for this cart"""
        return self.items.all()

    def add_item(self, product, variant, quantity=1):
        """Add or update item in cart"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def remove_item(self, product, variant):
        """Remove item from cart"""
        CartItem.objects.filter(
            cart=self,
            product=product,
            variant=variant
        ).delete()

    def update_item_quantity(self, product, variant, quantity):
        """Update item quantity in cart"""
        try:
            cart_item = CartItem.objects.get(
                cart=self,
                product=product,
                variant=variant
            )
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            return None

    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()

    def get_total_items(self):
        """Get total number of items in cart"""
        return self.cart_items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create cart for authenticated user"""
        cart, created = cls.objects.get_or_create(
            user=user,
            defaults={'session_id': None}
        )
        return cart

    @classmethod
    def get_or_create_for_session(cls, session_id):
        """Get or create cart for session"""
        cart, created = cls.objects.get_or_create(
            session_id=session_id,
            defaults={'user': None}
        )
        return cart

    def __str__(self):
        identifier = self.user.mobile_number if self.user else f"Session: {self.session_id}"
        return f"Cart - {identifier}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PREPARING', 'Preparing'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.JSONField(default=list)  # Array of {product, variant, quantity, price, discount}
    order_amount = models.PositiveIntegerField()  # Amount in paisa
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    delivery_address = models.TextField()  # String formed from address fields
    additional_info = models.JSONField(default=dict)  # Extra data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.mobile_number} - ₹{self.order_amount/100:.2f}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('WALLET', 'Wallet'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.PositiveIntegerField()  # Amount in paisa
    transaction_id = models.CharField(max_length=255, unique=True)
    gateway_order_id = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    additional_info = models.JSONField(default=dict)  # Extra data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order.id} - ₹{self.amount/100:.2f} - {self.payment_status}"
