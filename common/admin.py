from django.contrib import admin
from .models import Category, Tag, Product, Variant, RestaurentEntity, Cart, CartItem, Order, Payment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_available']
    list_filter = ['type', 'is_available']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_available']
    list_filter = ['is_available']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'discount', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'type', 'price', 'is_available']
    list_filter = ['type', 'is_available']
    search_fields = ['product__name', 'size']


@admin.register(RestaurentEntity)
class RestaurentEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_available']
    list_filter = ['is_available']
    search_fields = ['name']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['cart__id', 'product__name']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__mobile_number', 'session_id']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_amount_display', 'payment_status', 'order_status', 'created_at']
    list_filter = ['payment_status', 'order_status', 'created_at']
    search_fields = ['user__mobile_number', 'payment_id']
    readonly_fields = ['created_at', 'updated_at']

    def order_amount_display(self, obj):
        return f"₹{obj.order_amount/100:.2f}"
    order_amount_display.short_description = 'Order Amount'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount_display', 'payment_status', 'payment_method', 'created_at']
    list_filter = ['payment_status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'gateway_order_id', 'order__user__mobile_number']
    readonly_fields = ['created_at', 'updated_at']

    def amount_display(self, obj):
        return f"₹{obj.amount/100:.2f}"
    amount_display.short_description = 'Amount'
