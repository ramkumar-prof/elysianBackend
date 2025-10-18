"""
Django Admin Configuration Documentation
========================================

⚠️  IMPORTANT: Django admin interface is currently DISABLED for security reasons.
    These admin configurations are documented here for reference only.

Current Status:
- Django admin is disabled via DJANGO_ADMIN_ENABLED=False
- Admin URLs return 404 (Not Found)
- Custom admin APIs are used instead: /api/common/admin/

If Django admin is re-enabled in the future, these configurations would provide:

CategoryAdmin:
- List Display: name, type, is_available
- Filters: type, availability status
- Search: by category name

TagAdmin:
- List Display: name, is_available
- Filters: availability status
- Search: by tag name

ProductAdmin:
- List Display: name, category, discount, is_available
- Filters: category, availability status
- Search: by product name

VariantAdmin:
- List Display: product, size, type, price, is_available
- Filters: type, availability status
- Search: by product name, variant size

RestaurentEntityAdmin:
- List Display: name, is_available
- Filters: availability status
- Search: by restaurant name

CartItemAdmin:
- List Display: cart, product, variant, quantity, created_at
- Filters: creation date
- Search: by cart ID, product name

CartAdmin:
- List Display: id, user, session_id, created_at
- Filters: creation date
- Search: by user mobile number, session ID

OrderAdmin:
- List Display: id, user, order_amount_display, payment_status, order_status, created_at
- Filters: payment status, order status, creation date
- Search: by user mobile number, payment ID
- Read-only: created_at, updated_at
- Custom: order_amount_display (formatted currency)

PaymentAdmin:
- List Display: id, order, amount_display, payment_status, payment_method, created_at
- Filters: payment status, payment method, creation date
- Search: by transaction ID, gateway order ID, user mobile number
- Read-only: created_at, updated_at
- Custom: amount_display (formatted currency)

Alternative: Use Custom Admin APIs
==================================
Instead of Django admin, use these secure API endpoints:

Products:
- GET /api/common/admin/products/list/
- POST /api/common/admin/products/add/
- PUT /api/common/admin/products/{id}/update/
- DELETE /api/common/admin/products/{id}/delete/

Variants:
- GET /api/common/admin/variants/list/
- POST /api/common/admin/variants/add/
- PUT /api/common/admin/variants/{id}/update/
- DELETE /api/common/admin/variants/{id}/delete/

Authentication: JWT tokens with IsAdminUser permission required
"""

# Commented out admin registrations (admin interface disabled)
# from django.contrib import admin
# from .models import Category, Tag, Product, Variant, RestaurentEntity, Cart, CartItem, Order, Payment

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'type', 'is_available']
#     list_filter = ['type', 'is_available']
#     search_fields = ['name']

# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ['name', 'is_available']
#     list_filter = ['is_available']
#     search_fields = ['name']

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'category', 'discount', 'is_available']
#     list_filter = ['category', 'is_available']
#     search_fields = ['name']

# @admin.register(Variant)
# class VariantAdmin(admin.ModelAdmin):
#     list_display = ['product', 'size', 'type', 'price', 'is_available']
#     list_filter = ['type', 'is_available']
#     search_fields = ['product__name', 'size']

# @admin.register(RestaurentEntity)
# class RestaurentEntityAdmin(admin.ModelAdmin):
#     list_display = ['name', 'is_available']
#     list_filter = ['is_available']
#     search_fields = ['name']

# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ['cart', 'product', 'variant', 'quantity', 'created_at']
#     list_filter = ['created_at']
#     search_fields = ['cart__id', 'product__name']

# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'session_id', 'created_at']
#     list_filter = ['created_at']
#     search_fields = ['user__mobile_number', 'session_id']

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'order_amount_display', 'payment_status', 'order_status', 'created_at']
#     list_filter = ['payment_status', 'order_status', 'created_at']
#     search_fields = ['user__mobile_number', 'payment_id']
#     readonly_fields = ['created_at', 'updated_at']

#     def order_amount_display(self, obj):
#         return f"₹{obj.order_amount/100:.2f}"
#     order_amount_display.short_description = 'Order Amount'

# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ['id', 'order', 'amount_display', 'payment_status', 'payment_method', 'created_at']
#     list_filter = ['payment_status', 'payment_method', 'created_at']
#     search_fields = ['transaction_id', 'gateway_order_id', 'order__user__mobile_number']
#     readonly_fields = ['created_at', 'updated_at']

#     def amount_display(self, obj):
#         return f"₹{obj.amount/100:.2f}"
#     amount_display.short_description = 'Amount'
