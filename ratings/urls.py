from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    path('restaurants/<int:id>/', views.get_restaurant_ratings_by_id, name='get_restaurant_ratings_by_id'),
    path('restaurants/<int:id>/add-rating/', views.add_rating, name='add_rating'),
    path('restaurants/<int:id>/<int:rating_id>/edit/', views.edit_rating, name='edit_rating'),
    path('restaurants/<int:id>/<int:rating_id>/delete/', views.delete_rating, name='delete_rating'),
    path('restaurants/<int:id>/<int:rating_id>/edit/', views.edit_rating, name='edit_rating'),
    path('ratings/show_json/<int:restaurant_id>/', views.get_ratings_json, name='show_json'),

]
