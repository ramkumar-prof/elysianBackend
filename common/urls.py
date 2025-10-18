from django.urls import path
from .views import common, product, cart, order, admin

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

    # Admin Product Management APIs
    path('admin/products/', admin.admin_list_products, name='admin-list-products'),
    path('admin/products/add/', admin.admin_add_product, name='admin-add-product'),
    path('admin/products/<int:product_id>/', admin.admin_get_product, name='admin-get-product'),
    path('admin/products/<int:product_id>/update/', admin.admin_update_product, name='admin-update-product'),
    path('admin/products/<int:product_id>/delete/', admin.admin_delete_product, name='admin-delete-product'),

    # Admin Variant Management APIs
    path('admin/variants/', admin.admin_list_variants, name='admin-list-variants'),
    path('admin/variants/add/', admin.admin_add_variant, name='admin-add-variant'),
    path('admin/variants/<int:variant_id>/', admin.admin_get_variant, name='admin-get-variant'),
    path('admin/variants/<int:variant_id>/update/', admin.admin_update_variant, name='admin-update-variant'),
    path('admin/variants/<int:variant_id>/delete/', admin.admin_delete_variant, name='admin-delete-variant'),

    # Admin Category Management APIs
    path('admin/categories/', admin.admin_list_categories, name='admin-list-categories'),
    path('admin/categories/add/', admin.admin_add_category, name='admin-add-category'),
    path('admin/categories/<int:category_id>/', admin.admin_get_category, name='admin-get-category'),
    path('admin/categories/<int:category_id>/update/', admin.admin_update_category, name='admin-update-category'),
    path('admin/categories/<int:category_id>/delete/', admin.admin_delete_category, name='admin-delete-category'),
]
