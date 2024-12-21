from django.urls import path, include
from search.views import *

app_name = 'search'

urlpatterns = [
    path("food-search/", food_search, name="food_search"),
    path("resto-search/", resto_search, name="resto_search"),
    path("food-search-flutter/", food_search_flutter, name="food_search_flutter"),
    path("resto-search-flutter/", resto_search_flutter, name="resto_search_flutter"),
    path('save-search/', save_search_history, name='save_search_history'),
    path('save-search-history-flutter/', save_search_history_flutter, name='save_search_history_flutter'),
    path('delete-history/<int:history_id>/', delete_search_history, name='delete_search_history'),
    path('get-search-history/', get_search_history, name='get-search-history'),
    path('get-search-history-flutter/', get_search_history_flutter, name='get_search_history_flutter'),
    path('get-random-restaurant-flutter/', get_random_restaurant_flutter, name='get_random_restaurant_flutter'), 
    path('json/', show_json, name='show_json'),
]