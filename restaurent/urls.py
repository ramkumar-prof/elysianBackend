from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.restaurant_menu_list, name='restaurant-menu-list'),
    path('admin/menu/add/', views.admin_add_menu_item, name='admin-add-menu-item'),
]