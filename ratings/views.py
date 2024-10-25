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


logger = logging.getLogger(__name__)

# Menampilkan ratings untuk restoran tertentu
def get_restaurant_ratings_by_id(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    restaurant_ratings = Ratings.objects.filter(restaurant_review=restaurant)
    reviewed_menus = Menu.objects.filter(restoran=restaurant)

    # Hitung average rating
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

# Menambahkan rating melalui POST request
@login_required
@csrf_exempt
@require_POST
def add_rating(request, restaurant_id):
    if request.method == "POST":
        # Ambil data dari form
        rating_value = request.POST.get('rating')
        pesan_rating = request.POST.get('pesan_rating')
        menu_ids = request.POST.getlist('menu_review')  # Bisa review beberapa menu

        # Dapatkan objek Restaurant
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        # Proses setiap menu yang di-review
        for menu_id in menu_ids:
            menu = get_object_or_404(Menu, id=menu_id)

            # Simpan rating di database
            rating = Ratings.objects.create(
                user=request.user,
                menu_review=menu,
                restaurant_review=restaurant,
                rating=rating_value,
                pesan_rating=pesan_rating,
            )

        # Jika request AJAX, kirim respons JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'user_initials': request.user.username[:2].upper(),
                'username': request.user.username,
                'date': rating.created_at.strftime('%B %d, %Y'),
                'rating': rating.rating,
                'pesan_rating': rating.pesan_rating,
            }, status=201)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# Hapus rating
@login_required
@require_POST
def delete_rating(request, restaurant_id, rating_id):
    rating = get_object_or_404(Ratings, id=rating_id, restaurant_review_id=restaurant_id)
    
    # Hanya izinkan user yang membuat rating untuk menghapusnya
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

    # Hanya izinkan user yang membuat rating untuk mengeditnya
    if request.user != rating.user:
        return HttpResponseForbidden('You are not allowed to edit this rating.')

    if request.method == 'POST':
        form = AddRatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            return redirect('ratings:get_restaurant_ratings_by_id', id=id)
    else:
        form = AddRatingForm(instance=rating)

    reviewed_menus = Menu.objects.filter(restoran=restaurant)
    return render(request, 'edit_rating.html', {
        'form': form, 
        'restaurant': restaurant, 
        'rating': rating, 
        'reviewed_menus': reviewed_menus
    })


@csrf_exempt 
@require_POST  
def add_rating_ajax(request):
    rating_value = request.POST.get('rating')
    pesan_rating = strip_tags(request.POST.get('pesan_rating'))
    menu_ids = request.POST.getlist('menu_review')  
    restaurant_id = request.POST.get('restaurant_id') 

    if not (rating_value and pesan_rating and menu_ids and restaurant_id):
        return JsonResponse({'success': False, 'error': 'Missing fields'}, status=400)

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
    
    # Kembalikan data dalam format JSON
    return JsonResponse(data, safe=False)




def show_main_page(request):
    # Fetch the latest ratings, you can modify the limit as needed
    latest_ratings = Ratings.objects.order_by('-created_at')[:10]  # Or adjust the query
    
    # Pass additional info like user initials and the range for stars
    context = {
        'latest_ratings': latest_ratings,
        'star_range': range(1, 6),  # For displaying star ratings
    }
    return render(request, 'ratings_main_page.html', context)


def restaurant_detail(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    return render(request, 'restaurant_detail.html', {'restaurant': restaurant})