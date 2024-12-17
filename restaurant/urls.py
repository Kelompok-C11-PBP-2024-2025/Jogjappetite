from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('customer/', views.customer_restaurant_list, name='customer_restaurant_list'),
    path('owner/', views.owner_restaurant_list, name='owner_restaurant_list'),
    path('owner/add/', views.add_restaurant, name='add_restaurant'),
    path('owner/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('owner/<int:pk>/delete/', views.delete_restaurant, name='delete_restaurant'),
    path('owner/<int:pk>/edit/', views.edit_restaurant, name='edit_restaurant'),

    path('api/get-data/', views.api_restaurant_list, name='api_restaurant_list'),
    path('api/owner/add/', views.api_add_restaurant, name='api_add_restaurant'),
    path('api/owner/<int:pk>/', views.api_restaurant_detail, name='api_restaurant_detail'),
    path('api/owner/<int:pk>/delete/', views.api_delete_restaurant, name='api_delete_restaurant'),
    path('api/owner/<int:pk>/edit/', views.api_edit_restaurant, name='api_edit_restaurant'),
]