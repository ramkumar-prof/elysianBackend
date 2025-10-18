"""
Django Admin Configuration Documentation - User Module
======================================================

⚠️  IMPORTANT: Django admin interface is currently DISABLED for security reasons.
    These admin configurations are documented here for reference only.

Current Status:
- Django admin is disabled via DJANGO_ADMIN_ENABLED=False
- Admin URLs return 404 (Not Found)
- Custom admin APIs are used instead: /api/user/

If Django admin is re-enabled in the future, these configurations would provide:

AddressInline:
- Type: TabularInline (inline editing within user form)
- Model: Address
- Fields: name, address, city, state, pincode, is_default
- Extra: 0 (no extra empty forms)

CustomUserAdmin:
- Extends: Django's built-in UserAdmin
- List Display: mobile_number, email, first_name, last_name, is_staff, is_active
- Filters: staff status, active status, join date
- Search: by mobile number, email, first name, last name
- Ordering: by mobile number
- Fieldsets: Organized form sections for editing users
  * Basic: mobile_number, password
  * Personal info: first_name, last_name, email
  * Permissions: is_active, is_staff, is_superuser, groups, user_permissions
  * Important dates: last_login, date_joined
- Add Fieldsets: Form layout for creating new users
- Inlines: Includes AddressInline for managing user addresses

AddressAdmin:
- List Display: user, name, city, state, pincode, is_default, created_at
- Filters: default status, state, city, creation date
- Search: by user mobile number, name, address, city, pincode
- Ordering: by creation date (newest first)

Alternative: Use Custom Admin APIs
==================================
Instead of Django admin, use these secure API endpoints:

User Management:
- GET /api/user/profile/                    # Get user profile (with admin fields for staff/superuser)
- PUT /api/user/profile/update/             # Update user profile
- GET /api/user/addresses/                  # Get user addresses
- POST /api/user/addresses/add/             # Add new address
- PUT /api/user/addresses/{id}/update/      # Update address
- DELETE /api/user/addresses/{id}/delete/   # Delete address

Authentication: JWT tokens required
Admin Features: is_staff and is_superuser fields shown conditionally for admin users
"""

# Commented out admin registrations (admin interface disabled)
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser, Address

# class AddressInline(admin.TabularInline):
#     model = Address
#     extra = 0
#     fields = ('name', 'address', 'city', 'state', 'pincode', 'is_default')

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('mobile_number', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
#     list_filter = ('is_staff', 'is_active', 'date_joined')
#     fieldsets = (
#         (None, {'fields': ('mobile_number', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('mobile_number', 'password1', 'password2', 'is_staff', 'is_active')}
#         ),
#     )
#     search_fields = ('mobile_number', 'email', 'first_name', 'last_name')
#     ordering = ('mobile_number',)
#     inlines = [AddressInline]

# @admin.register(Address)
# class AddressAdmin(admin.ModelAdmin):
#     list_display = ('user', 'name', 'city', 'state', 'pincode', 'is_default', 'created_at')
#     list_filter = ('is_default', 'state', 'city', 'created_at')
#     search_fields = ('user__mobile_number', 'name', 'address', 'city', 'pincode')
#     ordering = ('-created_at',)

# admin.site.register(CustomUser, CustomUserAdmin)
