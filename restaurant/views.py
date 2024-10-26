from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RestaurantForm
from ratings.models import Menu, Ratings, Restaurant
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .decorators import user_is_owner, user_is_customer


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
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.save()
            # messages.success(request, 'Restoran berhasil ditambahkan!')
            return redirect('restaurant:owner_restaurant_list')
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
            return redirect('restaurant:owner_restaurant_list')
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