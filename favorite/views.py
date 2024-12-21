from django.shortcuts import render, get_object_or_404, redirect
from ratings.models import Restaurant
from favorite.models import Favorite
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

# View untuk menampilkan daftar restoran dalam halaman favorite
from django.db.models import Avg, Count

@login_required(login_url="authentication:login")
def show_main_favorite(request):
    # Mengambil restoran yang ada di daftar favorit pengguna dengan annotasi untuk rating
    favorites = Favorite.objects.filter(user=request.user).select_related('restaurant').annotate(
        average_rating=Avg('restaurant__menu__ratings__rating'),
        rating_count=Count('restaurant__menu__ratings')
    )

    # Membuat daftar restoran beserta atribut yang diperlukan
    restaurants = [{
        'restaurant': favorite.restaurant,
        'favorite_id': favorite.id,
        'notes': favorite.notes,
        'average_rating': favorite.average_rating or 0.0,  # Jika tidak ada rating, set nilai default ke 0.0
        'rating_count': favorite.rating_count
    } for favorite in favorites]

    context = {
        'restaurants': restaurants,
    }

    return render(request, 'favorite.html', context)


@login_required(login_url="authentication:login")
def list_all_restaurants(request):
    # Mengambil semua restoran dari model Restaurant
    restaurants = Restaurant.objects.all()
    context = {
        'restaurants': restaurants,
    }
    return render(request, 'all_restaurants.html', context)

# View untuk menambahkan restoran ke favorit
@login_required(login_url="authentication:login")
def add_to_favorite(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        notes = request.POST.get('notes', '').strip()
        if not notes:
            return render(request, 'add_favorite_form.html', {
                'restaurant': restaurant,
                'error_message': "Please provide a note for adding this restaurant to your favorites."
            })

        # Cek apakah restoran sudah ada di daftar favorit pengguna
        if not Favorite.objects.filter(user=request.user, restaurant=restaurant).exists():
            Favorite.objects.create(user=request.user, restaurant=restaurant, notes=notes)

        return redirect('favorite:favorite_list_view')

    return render(request, 'add_favorite_form.html', {'restaurant': restaurant})

@login_required(login_url="authentication:login")
@require_POST
def add_to_favorite_ajax(request):
    import json

    # Mengambil data dari request body
    try:
        data = json.loads(request.body)
        restaurant_id = data.get('restaurant_id')
        notes = data.get('notes', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})

    if not restaurant_id or not notes:
        return JsonResponse({'success': False, 'message': 'Restaurant ID and notes are required.'})

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Cek apakah restoran sudah ada di daftar favorit pengguna
    if not Favorite.objects.filter(user=request.user, restaurant=restaurant).exists():
        Favorite.objects.create(user=request.user, restaurant=restaurant, notes=notes)
        return JsonResponse({'success': True, 'message': 'Restaurant added to favorites.', 'redirect_url': '/favorite/'})
    else:
        return JsonResponse({'success': False, 'message': 'Restaurant is already in favorites.'})
    
@login_required(login_url="authentication:login")
@require_POST
def delete_favorite(request):
    import json
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            favorite_id = data.get('favorite_id', None)

            if not favorite_id:
                return JsonResponse({'success': False, 'message': 'Favorite ID is required.'})

            # Cari berdasarkan ID favorit dan pengguna yang sedang login
            favorite = Favorite.objects.get(id=favorite_id, user=request.user)
            favorite.delete()
            return JsonResponse({'success': True})
        except Favorite.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Favorite not found.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
@login_required(login_url="authentication:login")
@require_POST
def edit_favorite_notes(request):
    import json
    if request.method == "POST":
        data = json.loads(request.body)
        favorite_id = data.get('favorite_id', None)
        new_notes = data.get('notes', '').strip()

        if not favorite_id or not new_notes:
            return JsonResponse({'success': False, 'message': 'Favorite ID and new notes are required.'})

        try:
            # Cari berdasarkan ID favorit dan pengguna yang sedang login
            favorite = Favorite.objects.get(id=favorite_id, user=request.user)
            favorite.notes = new_notes
            favorite.save()
            return JsonResponse({'success': True, 'message': 'Notes updated successfully.'})
        except Favorite.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Favorite not found.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
def show_json(request):
    # Pastikan user login
    favorites = Favorite.objects.filter(user=request.user).select_related('restaurant')
    
    # Format data agar sesuai dengan model di Flutter
    data = [
        {
            "model": "favorite.favorite",
            "pk": favorite.id,
            "fields": {
                "user": favorite.user.id,
                "restaurant": favorite.restaurant.id,
                "notes": favorite.notes,
                "created_at": favorite.created_at.isoformat()
            }
        }
        for favorite in favorites
    ]
    
    return JsonResponse(data, safe=False)

@csrf_exempt
def show_main_favorite_flutter(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('restaurant')
    data = [
        {
            "id": fav.id,
            "user": fav.user.username,
            "restaurant": {
                "id": fav.restaurant.id,
                "nama_restoran": fav.restaurant.nama_restoran,
                "lokasi": fav.restaurant.lokasi,
                "average_rating": fav.restaurant.ratings_set.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0,
                "gambar": fav.restaurant.gambar,
            },
            "notes": fav.notes,
            "created_at": fav.created_at,
        }
        for fav in favorites
    ]
    return JsonResponse(data, safe=False)

def show_all_restaurants_flutter(request):
    restaurants = Restaurant.objects.annotate(
        average_rating=Avg('ratings__rating')
    )
    data = [
        {
            "id": restaurant.id,
            "nama_restoran": restaurant.nama_restoran,
            "lokasi": restaurant.lokasi,
            "gambar": restaurant.gambar or "",
            "average_rating": restaurant.average_rating or 0.0,
        }
        for restaurant in restaurants
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required(login_url="authentication:login")  # Pastikan user login terlebih dahulu
def add_favorite_flutter(request):
    if request.method == "POST":
        try:
            # Ambil data JSON dari request
            data = json.loads(request.body)

            restaurant_id = data.get('restaurant_id')  # ID restoran yang akan ditambahkan
            notes = data.get('notes')  # Catatan dari user

            # Validasi data
            if not restaurant_id or not notes:
                return JsonResponse(
                    {"success": False, "message": "Restaurant ID and notes are required."},
                    status=400,
                )

            # Ambil restoran dari database
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)

            # Cek apakah restoran sudah ada di daftar favorit pengguna
            if Favorite.objects.filter(user=request.user, restaurant=restaurant).exists():
                return JsonResponse(
                    {"success": False, "message": "Restaurant already added to favorites."},
                    status=400,
                )

            # Tambahkan restoran ke daftar favorit
            Favorite.objects.create(
                user=request.user,
                restaurant=restaurant,
                notes=notes,
            )

            return JsonResponse(
                {"success": True, "message": "Favorite berhasil ditambahkan!"},
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Invalid JSON data."},
                status=400,
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method."},
            status=405,
        )