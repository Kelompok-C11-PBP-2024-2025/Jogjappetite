from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    path('restaurants/<int:id>/', views.get_restaurant_ratings_by_id, name='get_restaurant_ratings_by_id'),
    path('add-rating/<int:restaurant_id>/', views.add_rating, name='add_rating'),
    path('restaurants/<int:id>/<int:rating_id>/edit/', views.edit_rating, name='edit_rating'),
    path('restaurants/<int:restaurant_id>/<int:rating_id>/delete/', views.delete_rating, name='delete_rating'),
    path('add-rating-ajax/', views.add_rating_ajax, name='add_rating_ajax'),
    path('restaurants/<int:restaurant_id>/ratings/json/', views.show_json, name='show_json'),
    path('', views.show_main_page, name='show_main_page'),

]
