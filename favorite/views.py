from django.shortcuts import render, get_object_or_404, redirect
from ratings.models import Restaurant
from favorite.models import Favorite
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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
    
