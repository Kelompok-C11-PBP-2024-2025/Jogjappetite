from django.urls import path, include
from search.views import *

app_name = 'search'

urlpatterns = [
    path("food-search/", food_search, name="food_search"),
    path("resto-search/", resto_search, name="resto_search"),
    path('search/', search_view, name='search_view'),
    path('save-search/', save_search, name='save_search'),
    path('delete-history/<int:history_id>/', delete_search_history, name='delete_search_history'),
]