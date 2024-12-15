from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    path('restaurants/<int:id>/', views.get_restaurant_ratings_by_id, name='get_restaurant_ratings_by_id'),

    path('restaurants/<int:id>/<int:rating_id>/edit/', views.edit_rating, name='edit_rating'),
    path('restaurants/<int:restaurant_id>/<int:rating_id>/delete/', views.delete_rating, name='delete_rating'),

    path('add-rating-ajax/', views.add_rating_ajax, name='add_rating_ajax'),
    path('restaurants/<int:restaurant_id>/json/', views.show_json, name='show_json'),
    
    path('', views.show_main_page, name='show_main_page'),
    path('my-ratings/', views.user_ratings_all, name='user_ratings_all'),

    # FLUTTER
    path('restaurants/flutter/<int:id>/', views.get_restaurant_ratings_by_id_flutter, name='get_restaurant_ratings_by_id_flutter'),
    path('api/main-page/', views.show_main_page_flutter, name='show_main_page_flutter'),
    path('add-rating-flutter/', views.add_rating_flutter, name='add_rating_flutter'),
    path(
        'edit-rating-flutter/<int:restaurant_id>/<int:rating_id>/',
        views.edit_rating_flutter,
        name='edit_rating_flutter',
    ),
    path(
        'delete-rating-flutter/<int:restaurant_id>/<int:rating_id>/',
        views.delete_rating_flutter,
        name='delete_rating_flutter',
    )


]
