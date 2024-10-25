from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core import serializers
from ratings.forms import AddRatingForm
from ratings.models import Menu, Ratings, Restaurant
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg



def get_restaurant_ratings_by_id(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    restaurant_ratings = Ratings.objects.filter(restaurant_review=restaurant)
    reviewed_menus = Menu.objects.filter(restoran=restaurant)

    # Calculate average rating
    average_rating = restaurant_ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    for menu in reviewed_menus:
        menu.cleaned_clusters = [cluster.strip("[]' ") for cluster in menu.get_clusters()]
    
    reviews_count = restaurant_ratings.count()
    
    context = {
        'restaurant': restaurant,
        'restaurant_ratings': restaurant_ratings,
        'reviewed_menus': reviewed_menus,
        'average_rating': average_rating,
        'rating_range': range(1, 6),
        'reviews_count': reviews_count,
    }
    
    return render(request, 'restaurant_ratings.html', context)

@login_required
def add_rating(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    if request.method == 'POST':
        form = AddRatingForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.restaurant_review = restaurant
            rating.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = AddRatingForm(restaurant=restaurant)
    return render(request, 'add_rating.html', {'form': form, 'restaurant': restaurant})

@login_required
@csrf_exempt
def delete_rating(request, id, rating_id):  # Now accepts both restaurant id and rating id
    rating = get_object_or_404(Ratings, id=rating_id, restaurant_review_id=id)  # Ensure the rating belongs to the restaurant
    if request.method == 'POST':
        rating.delete()
        return JsonResponse({'success': True, 'message': 'Rating deleted successfully'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def edit_rating(request, id, rating_id):
    rating = get_object_or_404(Ratings, id=rating_id)
    restaurant = get_object_or_404(Restaurant, id=id)  # Fetch the restaurant object
    
    # Filter the menus to only show those related to the restaurant with the given id
    menus = Menu.objects.filter(restoran=restaurant)
    
    if request.method == 'POST':
        form = AddRatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Rating updated successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    # Pre-populate the form with existing rating data for editing
    form = AddRatingForm(instance=rating)
    return render(request, 'edit_rating.html', {'form': form, 'restaurant': restaurant, 'rating': rating, 'menus': menus})


def get_ratings_json(request, restaurant_id):
    # Fetch all ratings related to the given restaurant
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    ratings = Ratings.objects.filter(restaurant_review=restaurant)
    ratings_json = serializers.serialize('json', ratings)

    return JsonResponse(ratings_json, safe=False)



def create_rating_ajax(request, id):
    if request.method == "POST":
        restaurant = get_object_or_404(Restaurant, id=id)
        rating_value = request.POST.get('rating')
        review_message = request.POST.get('pesan_rating')
        menu_review_id = request.POST.get('menu_review')  # Get menu_review from form

        try:
            menu_review = Menu.objects.get(id=menu_review_id)  # Fetch the Menu instance
        except Menu.DoesNotExist:
            return JsonResponse({"success": False, "error": "Menu not found"}, status=400)

        # Create the rating
        rating = Ratings.objects.create(
            restaurant_review=restaurant,
            user=request.user,
            menu_review=menu_review,  # Include the menu_review in the rating
            rating=rating_value,
            pesan_rating=review_message
        )

        # Save the rating
        rating.save()

        # Return success response
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)
