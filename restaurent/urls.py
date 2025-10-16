from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.restaurant_menu_list, name='restaurant-menu-list'),
]