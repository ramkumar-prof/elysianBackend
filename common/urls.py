from django.urls import path
from .views import common, product, cart

urlpatterns = [
    # Common views
    path('images/<path:image_path>', common.serve_image, name='serve-image'),
    path('session/', common.get_or_create_session, name='get-or-create-session'),
    
    # Product views
    path('categories/', product.get_categories, name='get-categories'),
    path('products/<int:product_id>/variants/', product.get_product_variants, name='get-product-variants'),
    path('products/<int:product_id>/variants/<int:variant_id>/pricing/', product.get_product_pricing, name='get-product-pricing'),
    
    # Cart views
    path('cart/', cart.get_cart_items, name='get-cart-items'),
]
