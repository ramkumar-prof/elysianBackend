from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.restaurant_list, name='restaurant-list'),
    path('menu/', views.restaurant_menu_list, name='restaurant-menu-list'),
    path('admin/menu/add/', views.admin_add_menu_item, name='admin-add-menu-item'),
    path('admin/menu/list/', views.admin_menu_items_list, name='admin-menu-items-list'),
    path('admin/menu/update/<int:menu_item_id>/', views.admin_update_menu_item, name='admin-update-menu-item'),
    path('admin/menu/delete/<int:menu_item_id>/', views.admin_delete_menu_item, name='admin-delete-menu-item'),
]