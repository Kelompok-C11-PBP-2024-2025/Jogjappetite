from django.urls import path
from explore.views import show_explore_page

app_name = 'favorite'

url_patterns = [
    path('',show_explore_page,name="ucup"),
]
