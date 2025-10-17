from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register-user'),
    path('login/', views.login_user, name='login-user'),
    path('logout/', views.logout_user, name='logout-user'),
    path('refresh/', views.refresh_token, name='refresh-token'),
    path('me/', views.get_current_user, name='current-user'),
    path('me/update/', views.update_current_user, name='update-current-user'),
    path('addresses/', views.get_user_addresses, name='user-addresses'),
    path('addresses/add/', views.add_user_address, name='add-user-address'),
    path('addresses/<int:address_id>/update/', views.update_user_address, name='update-user-address'),
    path('addresses/<int:address_id>/delete/', views.delete_user_address, name='delete-user-address'),
]
