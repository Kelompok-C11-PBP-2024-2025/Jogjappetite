from django.urls import path
from favorite.views import show_main_favorite

app_name = 'favorite'

urlpatterns = [
    path('', show_main_favorite, name='show_main_favorite'),
]
