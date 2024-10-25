from django.urls import path
from explore.views import show_explore_page, show_menus_explore

app_name = 'explore'

urlpatterns = [
    path('', show_explore_page, name='show_explore_page'),
    path('cluster/<str:cluster_name>/', show_menus_explore, name='show_menus_explore'),
]