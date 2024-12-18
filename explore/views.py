import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from ratings.models import Menu,Restaurant

from authentication.models import UserProfile
from django.views.decorators.http import require_http_methods,require_POST
from django.contrib.auth.decorators import login_required
from .models import Bookmark

# Create your views here.
def show_explore_page(request):
    
    
    return render(request, "explore.html")



@login_required
def toggle_bookmark(request, menu_id):
    user = request.user
    try:
        menu = get_object_or_404(Menu, id=menu_id)
        
    except Menu.DoesNotExist:
        print("Menu not found")  # Log jika menu tidak ditemukan
        return JsonResponse({'status': 'error', 'message': 'Menu not found'}, status=404)

    # Cek apakah bookmark sudah ada
    bookmark, created = Bookmark.objects.get_or_create(user=user, menu=menu)

    if not created:
        # Jika bookmark sudah ada, hapus bookmark
        bookmark.delete()
        print(f"Bookmark removed for user: {user.username}, menu: {menu.nama_menu}")
        return JsonResponse({'status': 'unbookmarked', 'message': 'Bookmark removed successfully'})
    
    # Jika bookmark baru dibuat
    print(f"Bookmark created for user: {user.username}, menu: {menu.nama_menu}")
    return JsonResponse({'status': 'bookmarked', 'message': 'Menu bookmarked successfully'})



def show_menus_explore(request, cluster_name):
    menus = Menu.objects.filter(cluster__icontains=cluster_name.lower())
    
    # Cek apakah user sudah login
    if request.user.is_authenticated:
        user_bookmarks = Bookmark.objects.filter(user=request.user).values_list('menu_id', flat=True)
    else:
        user_bookmarks = []  # Jika user belum login, tidak ada bookmark

    context = {
        'menus': menus,
        'cluster_name': cluster_name,
        'user_bookmarks': user_bookmarks,
    }
    
    return render(request, 'menu_by_cluster.html', context)

def cluster_menus(request, cluster_name):
    try:
        # Sesuaikan dengan field yang ada di model Menu Anda
        menus = Menu.objects.filter(cluster__icontains=cluster_name.lower())
        data = [{
            'id': menu.id,
            'name': menu.nama_menu,
            'restaurant': menu.restoran.nama_restoran,
            'price': menu.harga,
            # 'image_url': menu.image_url jika ada
        } for menu in menus]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# New view to handle AJAX requests for menu details
def menu_details(request, menu_id):
    try:
        menu = Menu.objects.get(id=menu_id)
        data = {
            'name': menu.nama_menu,
            'restaurant': menu.restoran.nama_restoran,
            'price': menu.harga,
            # 'image_url': menu.image_url,  # Make sure this field exists in your model
        }
        return JsonResponse(data)
    except Menu.DoesNotExist:
        return JsonResponse({'error': 'Menu not found'}, status=404)
@login_required
def get_user_bookmarks(request):
    user = request.user
    bookmarks = Bookmark.objects.filter(user=user)
    
    # Tambahkan log untuk memeriksa data bookmark
    print("Bookmarks for user:", bookmarks)

    bookmarks_data = [
        {
            'name': bookmark.menu.nama_menu,
            'restaurant': bookmark.menu.restoran.nama_restoran,
            'price': bookmark.menu.harga,
            'id': bookmark.menu.id
        }
        for bookmark in bookmarks
    ]
    return JsonResponse({'bookmarks': bookmarks_data})

def get_restaurant_details(request, restaurant_name):
    try:
        restaurant = Restaurant.objects.get(nama_restoran=restaurant_name)
        data = {
            'nama_restoran': restaurant.nama_restoran,
            'lokasi': restaurant.lokasi,
            'jenis_suasana': restaurant.jenis_suasana,
            'harga_rata_rata_makanan': restaurant.harga_rata_rata_makanan,
            'gambar': restaurant.gambar
        }
        return JsonResponse(data)
    except Restaurant.DoesNotExist:
        return JsonResponse({'error': 'Restaurant not found'}, status=404)
