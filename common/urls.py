from django.urls import path
from .views import common, product, cart, order

urlpatterns = [
    # Common views
    path('images/<path:image_path>', common.serve_image, name='serve-image'),
    path('session/', common.get_or_create_session, name='get-or-create-session'),
    
    # Product views
    path('categories/', product.get_categories, name='get-categories'),
    path('products/<int:product_id>/variants/', product.get_product_variants, name='get-product-variants'),
    path('products/<int:product_id>/variants/<int:variant_id>/pricing/', product.get_product_pricing, name='get-product-pricing'),
    
    # Cart views
    path('cart/', cart.cart_view, name='cart'),

    # Order views
    path('checkout/', order.checkout, name='checkout'),
    path('orders/', order.get_user_orders, name='get-user-orders'),
    path('orders/<int:order_id>/', order.get_order_details, name='get-order-details'),
]
