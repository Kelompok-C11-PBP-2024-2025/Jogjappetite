from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RestaurantForm
from ratings.models import Menu, Ratings, Restaurant
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .decorators import user_is_owner, user_is_customer
from django.http import JsonResponse
from authentication.models import UserProfile

@login_required
@user_is_customer
def customer_restaurant_list(request):
    per_page = request.GET.get('per_page', 12)
    restaurants = Restaurant.objects.all().annotate(
        average_rating=Avg('menu__ratings__rating'),
        rating_count=Count('menu__ratings')
    )

    paginator = Paginator(restaurants, per_page)
    page_number = request.GET.get('page')
    try:
        restaurants_page = paginator.page(page_number)
    except PageNotAnInteger:
        restaurants_page = paginator.page(1)
    except EmptyPage:
        restaurants_page = paginator.page(paginator.num_pages)

    return render(request, 'customer_restaurant_list.html', {'restaurants': restaurants_page, 'per_page': per_page})

# List restoran
@login_required
@user_is_owner
def owner_restaurant_list(request):
    per_page = request.GET.get('per_page', 12)
    restaurants = Restaurant.objects.all().annotate(
        average_rating=Avg('menu__ratings__rating'),
        rating_count=Count('menu__ratings')
    )

    paginator = Paginator(restaurants, per_page)
    page_number = request.GET.get('page')
    try:
        restaurants_page = paginator.page(page_number)
    except PageNotAnInteger:
        restaurants_page = paginator.page(1)
    except EmptyPage:
        restaurants_page = paginator.page(paginator.num_pages)

    return render(request, 'owner_restaurant_list.html', {'restaurants': restaurants_page, 'per_page': per_page})

# Menambahkan Restoran Baru
@login_required
@user_is_owner
def add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Restaurant added successfully!'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'message': 'Error adding restaurant.', 'errors': errors}, status=400)
    else:
        form = RestaurantForm()
    return render(request, 'restaurant_add.html', {'form': form})


# Menghapus Restoran
@login_required
@user_is_owner
def delete_restaurant(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        restaurant.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, 'Restoran berhasil dihapus.')
        return redirect('restaurant:owner_restaurant_list')

    return redirect('restaurant:owner_restaurant_list')

# Mengedit Restoran
@login_required
@user_is_owner
def edit_restaurant(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    print(restaurant)

    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('restaurant:restaurant_detail',pk=pk)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = RestaurantForm(instance=restaurant)

    return render(request, 'restaurant_edit.html', {'form': form, 'restaurant': restaurant})


# Melihat Statistik Restoran
@login_required
@user_is_owner
def restaurant_detail(request,pk):

    restaurants = Restaurant.objects.filter(pk=pk).annotate(
        average_rating=Avg('menu__ratings__rating'),
        rating_count=Count('menu__ratings')
    )

    reviews = Ratings.objects.filter(menu_review__restoran__pk=pk).select_related('menu_review', 'user').all()

    return render(request, 'restaurant_detail.html', {
        'restaurant': restaurants[0],
        'reviews': reviews
    })

# API List restoran untuk owner
@login_required
def api_restaurant_list(request):
    per_page = request.GET.get('per_page', 12)
    restaurants = Restaurant.objects.all().annotate(
        average_rating=Avg('menu__ratings__rating'),
        rating_count=Count('menu__ratings')
    )

    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.user_type == 'restaurant':
        profile_type = 'owner'
    else:
        profile_type = 'customer'

    paginator = Paginator(restaurants, per_page)
    page_number = request.GET.get('page')
    try:
        restaurants_page = paginator.page(page_number)
    except PageNotAnInteger:
        restaurants_page = paginator.page(1)

    data = [{
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
        } for restaurant in restaurants_page.object_list]

    return JsonResponse({
        'profile_type': profile_type,
        'restaurants': data,
        'per_page': int(per_page),
        'page': int(page_number),
        'total_pages': paginator.num_pages,
        'total_restaurants': paginator.count,
        'statusCode': 200
    })

# API Menambahkan Restoran Baru
@login_required
@user_is_owner
def api_add_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Restaurant added successfully!'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'message': 'Error adding restaurant.', 'errors': errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

# API Menghapus Restoran
@login_required
@user_is_owner
def api_delete_restaurant(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        restaurant.delete()
        return JsonResponse({'success': True, 'message': 'Restaurant deleted successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

# API Mengedit Restoran
@login_required
@user_is_owner
def api_edit_restaurant(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Restaurant updated successfully!'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

# API Melihat Statistik Restoran
@login_required
@user_is_owner
def api_restaurant_detail(request, pk):
    restaurant = Restaurant.objects.filter(pk=pk).annotate(
        average_rating=Avg('menu__ratings__rating'),
        rating_count=Count('menu__ratings')
    ).first()

    if not restaurant:
        return JsonResponse({'success': False, 'message': 'Restaurant not found.'}, status=404)

    reviews = Ratings.objects.filter(menu_review__restoran__pk=pk).select_related('menu_review', 'user').all()

    reviews_data = [{
        'id': review.id,
        'user_initials': review.user.username[:2].upper(),
        'username': review.user.username,
        'menu_review': review.menu_review.nama_menu,
        'rating': review.rating,
        'pesan_rating': review.pesan_rating,
        'created_at': review.created_at.strftime('%B %d, %Y')
    } for review in reviews]

    data = {
        'id': restaurant.id,
        'nama_restoran': restaurant.nama_restoran,
        'lokasi': restaurant.lokasi,
        'jenis_suasana': restaurant.jenis_suasana,
        'keramaian_restoran': restaurant.keramaian_restoran,
        'jenis_penyajian': restaurant.jenis_penyajian,
        'ayce_atau_alacarte': restaurant.ayce_atau_alacarte,
        'harga_rata_rata_makanan': restaurant.harga_rata_rata_makanan,
        'gambar': restaurant.gambar,
        'average_rating': float(restaurant.average_rating) if restaurant.average_rating else 0.0,
        'rating_count': restaurant.rating_count,
        'reviews': reviews_data
    }

    return JsonResponse({'success': True, 'restaurant': data})