from django.db import models
from common.models import RestaurentEntity, Product, Variant

class RestaurentMenu(models.Model):
    restaurent = models.ForeignKey(RestaurentEntity, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    is_veg = models.BooleanField(default=False)
    default_variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        # Ensure no duplicate menu items for the same restaurant and product
        unique_together = ['restaurent', 'product']
        verbose_name = 'Restaurant Menu Item'
        verbose_name_plural = 'Restaurant Menu Items'

    def __str__(self):
        return f"{self.restaurent.name} - {self.product.name}"
