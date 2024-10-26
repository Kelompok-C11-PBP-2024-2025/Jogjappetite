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

]