from django.urls import path, include

from ratings.views import get_menus, get_restaurants
app_name = 'ratings'

urlpatterns = [
    path('menus/', get_menus, name='get_menus'),  # Route untuk http://localhost:8000/api/menus
    path('restaurants/', get_restaurants, name='get_restaurants'),  # Route untuk http://localhost:8000/api/restaurants
]