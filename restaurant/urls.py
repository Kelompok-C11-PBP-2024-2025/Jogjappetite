from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.owner_restaurant_list, name='owner_restaurant_list'),
    path('add/', views.add_restaurant, name='add_restaurant'),
    path('<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('<int:pk>/delete/', views.delete_restaurant, name='delete_restaurant'),
    path('<int:pk>/edit/', views.edit_restaurant, name='edit_restaurant'),

]