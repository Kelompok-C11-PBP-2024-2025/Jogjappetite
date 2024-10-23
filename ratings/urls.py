from django.urls import path, include

from ratings.views import get_menus, get_restaurants, get_restaurant_ratings_by_id, add_rating,edit_rating, delete_rating
app_name = 'ratings'


urlpatterns = [
    path('restaurants/<int:id>/', get_restaurant_ratings_by_id, name='get_restaurant_ratings_by_id'),
    path('restaurants/<int:id>/add-rating/', add_rating, name='add_rating'),  # New route for adding a rating
    path('ratings/<int:rating_id>/edit/', edit_rating, name='edit_rating'),
    path('ratings/<int:rating_id>/delete/', delete_rating, name='delete_rating'),
]