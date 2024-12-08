from django.urls import path, include
from search.views import food_search, resto_search, save_search_history, delete_search_history, get_search_history, show_json

app_name = 'search'

urlpatterns = [
    path("food-search/", food_search, name="food_search"),
    path("resto-search/", resto_search, name="resto_search"),
    path('save-search/', save_search_history, name='save_search_history'),
    path('delete-history/<int:history_id>/', delete_search_history, name='delete_search_history'),
    path('get-search-history/', get_search_history, name='get-search-history'),
    path('show-json/', show_json, name='show_json'),
]