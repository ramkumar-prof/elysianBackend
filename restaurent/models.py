from django.db import models
from common.models import RestaurentEntity, Product, Variant

class RestaurentMenu(models.Model):
    restaurent = models.ForeignKey(RestaurentEntity, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    is_veg = models.BooleanField(default=False)
    default_variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.restaurent.name} - {self.product.name}"
