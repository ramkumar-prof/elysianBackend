"""
Django Admin Configuration Documentation - Restaurant Module
===========================================================

⚠️  IMPORTANT: Django admin interface is currently DISABLED for security reasons.
    These admin configurations are documented here for reference only.

Current Status:
- Django admin is disabled via DJANGO_ADMIN_ENABLED=False
- Admin URLs return 404 (Not Found)
- Custom admin APIs are used instead: /api/restaurant/admin/

If Django admin is re-enabled in the future, these configurations would provide:

RestaurentMenuAdmin:
- List Display: restaurent, product, is_available, is_veg, default_variant
- Filters: availability status, vegetarian status, restaurant
- Search: by product name, restaurant name
- Autocomplete: product, restaurant, default_variant fields
- Optimization: Uses select_related for efficient database queries

Alternative: Use Custom Admin APIs
==================================
Instead of Django admin, use these secure API endpoints:

Restaurant Menu Management:
- GET /api/restaurant/admin/menu/list/
- POST /api/restaurant/admin/menu/add/
- PUT /api/restaurant/admin/menu/{id}/update/
- DELETE /api/restaurant/admin/menu/{id}/delete/

Authentication: JWT tokens with IsAdminUser permission required
"""

# Commented out admin registrations (admin interface disabled)
# from django.contrib import admin
# from .models import RestaurentMenu

# @admin.register(RestaurentMenu)
# class RestaurentMenuAdmin(admin.ModelAdmin):
#     list_display = ['restaurent', 'product', 'is_available', 'is_veg', 'default_variant']
#     list_filter = ['is_available', 'is_veg', 'restaurent']
#     search_fields = ['product__name', 'restaurent__name']
#     autocomplete_fields = ['product', 'restaurent', 'default_variant']

#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related(
#             'restaurent', 'product', 'default_variant'
#         )
