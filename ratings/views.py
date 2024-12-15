import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core import serializers
from ratings.forms import AddRatingForm
from ratings.models import Menu, Ratings, Restaurant
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
import logging
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods



def get_restaurant_ratings_by_id(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    restaurant_ratings = Ratings.objects.filter(restaurant_review=restaurant)
    reviewed_menus = Menu.objects.filter(restoran=restaurant)

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


def get_restaurant_ratings_by_id_flutter(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    restaurant_ratings = Ratings.objects.filter(restaurant_review=restaurant)
    reviewed_menus = Menu.objects.filter(restoran=restaurant)

    average_rating = restaurant_ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    reviews_count = restaurant_ratings.count()

    # Format restaurant data
    response_data = {
        'restaurant': {
            'id': restaurant.id,
            'nama_restoran': restaurant.nama_restoran,
            'lokasi': restaurant.lokasi,
            'jenis_suasana': restaurant.jenis_suasana,
            'keramaian_restoran': restaurant.keramaian_restoran,
            'jenis_penyajian': restaurant.jenis_penyajian,
            'ayce_atau_alacarte': restaurant.ayce_atau_alacarte,
            'harga_rata_rata_makanan': restaurant.harga_rata_rata_makanan,
            'gambar': restaurant.gambar,
        },
        'menus': [
            {
                'id': menu.id,
                'nama_menu': menu.nama_menu,
                'harga': menu.harga,
                'categories': [cluster.strip("[]' ") for cluster in menu.get_clusters()]
            } for menu in reviewed_menus
        ],
        'ratings': [
            {
                'id': rating.id,
                'user_initials': rating.user.username[:2].upper(),
                'username': rating.user.username,
                'menu_review': rating.menu_review.nama_menu,
                'rating': rating.rating,
                'pesan_rating': rating.pesan_rating or '',
                'created_at': rating.created_at.strftime('%B %d, %Y')
            } for rating in restaurant_ratings
        ],
        'average_rating': float(average_rating),
        'reviews_count': reviews_count
    }

    return JsonResponse(response_data)


# Hapus rating
@login_required
@require_POST
def delete_rating(request, restaurant_id, rating_id):
    rating = get_object_or_404(Ratings, id=rating_id, restaurant_review_id=restaurant_id)
    
    if request.user == rating.user:
        rating.delete()
        return JsonResponse({'success': True, 'message': 'Rating deleted successfully.'})
    else:
        return JsonResponse({'success': False, 'message': 'You are not authorized to delete this rating.'}, status=403)

# Edit rating yang sudah ada
@login_required
def edit_rating(request, id, rating_id):
    rating = get_object_or_404(Ratings, id=rating_id, restaurant_review_id=id)
    restaurant = get_object_or_404(Restaurant, id=id)

    # Only allow the user who created the rating to edit it
    if request.user != rating.user:
        return JsonResponse({'success': False, 'message': 'You are not allowed to edit this rating.'}, status=403)

    if request.method == 'POST':
        form = AddRatingForm(request.POST, instance=rating, restaurant=restaurant)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True, 
                'message': 'Your rating has been successfully updated.',
                'updated_data': {
                    'rating': rating.rating,
                    'pesan_rating': rating.pesan_rating,
                    'menu_review': rating.menu_review.nama_menu,
                    'date': rating.created_at.strftime('%Y-%m-%d %H:%M')
                }
            })
        else:
            # Sending form errors back as JSON
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'message': 'Please correct the errors below.', 'errors': errors}, status=400)
    else:
        # For a GET request, return the initial form data if needed for pre-filling
        form = AddRatingForm(instance=rating, restaurant=restaurant)
        reviewed_menus = Menu.objects.filter(restoran=restaurant)
        return render(request, 'edit_rating.html', {
            'form': form, 
            'restaurant': restaurant, 
            'rating': rating, 
            'reviewed_menus': reviewed_menus
        })

@login_required
@csrf_exempt 
@require_POST  
def add_rating_ajax(request):
    rating_value = request.POST.get('rating')
    pesan_rating = strip_tags(request.POST.get('pesan_rating'))
    menu_ids = request.POST.getlist('menu_review')  
    restaurant_id = request.POST.get('restaurant_id') 

    # Check if any required field is missing
    if not (rating_value and pesan_rating and menu_ids and restaurant_id):
        return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

    # Validate rating_value as an integer and in the valid range
    try:
        rating_value = int(rating_value)
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid rating value'}, status=400)

    if not 1 <= rating_value <= 5:
        return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5'}, status=400)

    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    for menu_id in menu_ids:
        menu = get_object_or_404(Menu, id=menu_id)

        new_rating = Ratings.objects.create(
            user=user,
            menu_review=menu,
            restaurant_review=restaurant,
            rating=rating_value,
            pesan_rating=pesan_rating
        )

    return JsonResponse({
        'success': True,
        'rating': rating_value,
        'pesan_rating': pesan_rating,
        'user_initials': user.username[:2].upper(),
        'username': user.username,
        'date': new_rating.created_at.strftime('%B %d, %Y'),
    }, status=201)


@csrf_exempt 
def add_rating_flutter(request):
    try:
        # Extract data from request
        rating_value = request.POST.get('rating')
        pesan_rating = strip_tags(request.POST.get('pesan_rating'))
        menu_id = request.POST.get('menu_review')  # Single menu_id instead of list
        restaurant_id = request.POST.get('restaurant_id')

        # Validate required fields
        if not all([rating_value, pesan_rating, menu_id, restaurant_id]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required: rating, pesan_rating, menu_review, restaurant_id'
            }, status=400)

        # Validate rating value
        try:
            rating_value = int(rating_value)
            if not 1 <= rating_value <= 5:
                raise ValueError
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Rating must be an integer between 1 and 5'
            }, status=400)

        # Get restaurant and menu objects
        try:
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)
            menu = get_object_or_404(Menu, id=menu_id)
        except:
            return JsonResponse({
                'success': False,
                'error': 'Invalid restaurant or menu ID'
            }, status=404)

        # Check if user has already rated this menu
        existing_rating = Ratings.objects.filter(
            user=request.user,
            menu_review=menu
        ).first()

        if existing_rating:
            return JsonResponse({
                'success': False,
                'error': 'You have already rated this menu item'
            }, status=400)

        # Create new rating
        new_rating = Ratings.objects.create(
            user=request.user,
            menu_review=menu,
            restaurant_review=restaurant,
            rating=rating_value,
            pesan_rating=pesan_rating
        )

        # Return success response with rating details
        return JsonResponse({
            'success': True,
            'rating': {
                'id': new_rating.id,
                'rating': rating_value,
                'pesan_rating': pesan_rating,
                'user_initials': request.user.username[:2].upper(),
                'username': request.user.username,
                'menu_review': menu.nama_menu,
                'created_at': new_rating.created_at.strftime('%B %d, %Y'),
            }
        }, status=201)

    except Exception as e:
        # Log the error here if needed
        print(f"Error in add_rating_flutter: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred'
        }, status=500)

def show_json(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    
    ratings = Ratings.objects.filter(restaurant_review=restaurant)

    data = []
    for rating in ratings:
        data.append({
            'id': rating.id,
            'user_initials': rating.user.username[:2].upper(),  
            'username': rating.user.username, 
            'menu_review': rating.menu_review.nama_menu, 
            'restaurant_review': rating.restaurant_review.nama_restoran if rating.restaurant_review else None,  
            'rating': rating.rating,
            'pesan_rating': rating.pesan_rating or 'No message provided.',  # Pesan rating (jika kosong, tampilkan pesan default)
            'created_at': rating.created_at.strftime('%B %d, %Y')  # Format tanggal
        })

    return JsonResponse(data, safe=False)

def show_main_page(request):
    latest_ratings = Ratings.objects.order_by('-created_at')[:8]
    
    if request.user.is_authenticated:
        user_ratings = Ratings.objects.filter(user=request.user)
    else:
        user_ratings = None
    highest_rated_restaurants = Restaurant.objects.annotate(average_rating=Avg('ratings__rating')).order_by('-average_rating')[:6]

    context = {
        'latest_ratings': latest_ratings,
        'user_ratings': user_ratings,  
        'star_range': range(1, 6),  
        'highest_rated_restaurants': highest_rated_restaurants,  
    }
    return render(request, 'ratings_main_page.html', context)


def show_main_page_flutter(request):
    try:
        # Get latest 8 ratings
        latest_ratings = Ratings.objects.order_by('-created_at')[:8]
        latest_ratings_data = [{
            'id': rating.id,
            'user_initials': rating.user.username[:2].upper(),
            'username': rating.user.username,
            'menu_review': rating.menu_review.nama_menu,
            'restaurant_review': rating.restaurant_review.nama_restoran if rating.restaurant_review else None,
            'rating': rating.rating,
            'pesan_rating': rating.pesan_rating or 'No message provided.',
            'created_at': rating.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for rating in latest_ratings]

        # Get user ratings if authenticated
        user_ratings_data = None
        if request.user.is_authenticated:
            user_ratings = Ratings.objects.filter(user=request.user)
            user_ratings_data = [{
                'id': rating.id,
                'user_initials': rating.user.username[:2].upper(),
                'username': rating.user.username,
                'menu_review': rating.menu_review.nama_menu,
                'restaurant_review': rating.restaurant_review.nama_restoran if rating.restaurant_review else None,
                'rating': rating.rating,
                'pesan_rating': rating.pesan_rating or 'No message provided.',
                'created_at': rating.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for rating in user_ratings]

        # Get top 6 highest rated restaurants
        highest_rated_restaurants = Restaurant.objects.annotate(
            average_rating=Avg('ratings__rating')
        ).order_by('-average_rating')[:6]

        highest_rated_data = [{
            'id': restaurant.id,
            'nama_restoran': restaurant.nama_restoran,
            'lokasi': restaurant.lokasi,
            'gambar': restaurant.gambar,
            'jenis_suasana': restaurant.jenis_suasana,
            'keramaian_restoran': restaurant.keramaian_restoran,
            'jenis_penyajian': restaurant.jenis_penyajian,
            'ayce_atau_alacarte': restaurant.ayce_atau_alacarte,
            'harga_rata_rata_makanan': restaurant.harga_rata_rata_makanan,
            'average_rating': float(restaurant.average_rating) if restaurant.average_rating else 0.0
        } for restaurant in highest_rated_restaurants]

        response_data = {
            'latest_ratings': latest_ratings_data,
            'user_ratings': user_ratings_data,
            'highest_rated_restaurants': highest_rated_data,
            'is_authenticated': request.user.is_authenticated
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
    

@login_required
def user_ratings_all(request):
    user_ratings = Ratings.objects.filter(user=request.user)

    context = {
        'user_ratings': user_ratings,
        'star_range': range(1, 6),  
    }

    return render(request, 'user_ratings_all.html', context)

@csrf_exempt
def edit_rating_flutter(request, restaurant_id, rating_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST requests are allowed.'}, status=405)
    
    # Since we are sending data as form-data, we use request.POST
    rating_value = request.POST.get('rating')
    pesan_rating = strip_tags(request.POST.get('pesan_rating', ''))
    menu_id = request.POST.get('menu_review')

    # Validate required fields
    if rating_value is None or pesan_rating is None or menu_id is None:
        return JsonResponse({
            'success': False,
            'error': 'Missing fields: rating, pesan_rating, and menu_review are required.'
        }, status=400)

    # Validate rating value
    try:
        rating_value = int(rating_value)
        if not 1 <= rating_value <= 5:
            return JsonResponse({
                'success': False,
                'error': 'Rating must be an integer between 1 and 5.'
            }, status=400)
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'error': 'Rating must be a valid integer.'
        }, status=400)

    # Get the rating object
    rating = get_object_or_404(Ratings, id=rating_id, restaurant_review_id=restaurant_id)

    # Ensure the logged-in user owns this rating (you need to ensure request.user is correctly set)
    if request.user != rating.user:
        return JsonResponse({
            'success': False,
            'error': 'You are not allowed to edit this rating.'
        }, status=403)

    # Verify that the menu belongs to the given restaurant
    menu = get_object_or_404(Menu, id=menu_id)
    if menu.restoran_id != restaurant_id:
        return JsonResponse({'success': False, 'error': 'The selected menu does not belong to the given restaurant.'}, status=400)

    # Update the rating object
    rating.rating = rating_value
    rating.pesan_rating = pesan_rating
    rating.menu_review = menu
    rating.save()

    # Return success response with updated data
    return JsonResponse({
        'success': True,
        'message': 'Rating successfully updated.',
        'updated_data': {
            'id': rating.id,
            'rating': rating.rating,
            'pesan_rating': rating.pesan_rating,
            'menu_review': rating.menu_review.nama_menu,
            'date': rating.created_at.strftime('%Y-%m-%d %H:%M'),
            'user_initials': rating.user.username[:2].upper(),
            'username': rating.user.username,
        }
    }, status=200)


@csrf_exempt
def delete_rating_flutter(request, restaurant_id, rating_id):
    rating = get_object_or_404(Ratings, id=rating_id, restaurant_review_id=restaurant_id)

    # Delete the rating
    rating.delete()
    return JsonResponse({'success': True, 'message': 'Rating deleted successfully.'}, status=200)
