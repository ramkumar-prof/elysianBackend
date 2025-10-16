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

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
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
        unique_together = [
            ('user', 'product', 'variant'),
            ('session_id', 'product', 'variant')
        ]
    
    def clean(self):
        if not self.user and not self.session_id:
            raise ValidationError("Either user or session_id must be provided")
        if self.user and self.session_id:
            raise ValidationError("Cannot have both user and session_id")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        identifier = self.user.mobile_number if self.user else f"Session: {self.session_id}"
        return f"{identifier} - {self.product.name} ({self.variant.size}) x{self.quantity}"
