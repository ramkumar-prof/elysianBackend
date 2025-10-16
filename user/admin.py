from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('name', 'address', 'city', 'state', 'pincode', 'is_default')

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('mobile_number', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_number', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('mobile_number', 'email', 'first_name', 'last_name')
    ordering = ('mobile_number',)
    inlines = [AddressInline]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'city', 'state', 'pincode', 'is_default', 'created_at')
    list_filter = ('is_default', 'state', 'city', 'created_at')
    search_fields = ('user__mobile_number', 'name', 'address', 'city', 'pincode')
    ordering = ('-created_at',)

admin.site.register(CustomUser, CustomUserAdmin)
