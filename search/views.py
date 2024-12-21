from .models import SearchHistory
from ratings.models import Menu, Restaurant
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
import Levenshtein
import json

@login_required
def get_search_history(request):
    if request.method == 'GET':
        user_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
        history_data = [{'id': item.id, 'query': item.query} for item in user_history]
        return JsonResponse({'success': True, 'history': history_data})
    
def get_search_history_flutter(request):
    if request.method == 'GET':
        user_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]

        # Construct a list that matches your Dart model's expected structure
        history_data = []
        for item in user_history:
            history_data.append({
                "model": "search.searchhistory",
                "pk": item.id,
                "fields": {
                    "user": item.user.id,
                    "query": item.query,
                    "created_at": item.created_at.isoformat(),
                }
            })

        return JsonResponse({
            'success': True,
            'history': history_data
        })


@login_required
def save_search_history(request):
    if request.method == 'GET':
        query = request.GET.get('search_query', '').strip()
        if query:
            user = request.user
            # Limit the history to 5 searches
            user_history = SearchHistory.objects.filter(user=user).order_by('-created_at')
            if query in [item.query for item in user_history]:
                # If the query is already in the history, move it to the top
                user_history.filter(query=query).update(created_at=timezone.now())
            else:
                # Save the new search query in the history
                SearchHistory.objects.create(user=user, query=query)
            
                if len(user_history) >= 5:
                    # Remove the oldest search history item if the limit is exceeded
                    user_history.order_by('created_at').first().delete()

    # Since you don't want redirection, simply let the form submission handle the next action
    return JsonResponse({"success": True, "message": "Search history saved successfully."})

@csrf_exempt
def save_search_history_flutter(request):
    if request.method == 'POST':
        query = request.POST.get('search_query').strip()
        if query:
            user = request.user
            user_history = SearchHistory.objects.filter(user=user).order_by('-created_at')
            if query in [item.query for item in user_history]:
                # If the query is already in the history, move it to the top
                user_history.filter(query=query).update(created_at=timezone.now())
            else:
                # Save the new search query in the history
                SearchHistory.objects.create(user=user, query=query)

                if len(user_history) >= 5:
                    # Remove the oldest search history item if the limit is exceeded
                    user_history.order_by('created_at').first().delete()

            return JsonResponse({"success": True, "message": "Search history saved successfully."})
        else:
            return JsonResponse({"success": False, "message": "No search query provided."})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method."})

@csrf_exempt
def delete_search_history(request, history_id):
    if request.method == "POST":
        # Find the history item that matches the given ID and belongs to the logged-in user
        history_item = get_object_or_404(SearchHistory, id=history_id, user=request.user)
        history_item.delete()
        return JsonResponse({"success": True, "message": "Search history deleted successfully."})
    return JsonResponse({"success": False, "message": "Invalid request."})

def search_food_items(search_query):
    search = search_query.strip().lower()
    matching_menus = []
    found = -1  # Default to not found

    if search:
        all_menus = Menu.objects.all()
        matching_menus = list(Menu.objects.filter(nama_menu__icontains=search))
        found = 2 if matching_menus else -1

        for menu in all_menus:
            distance = Levenshtein.distance(search, menu.nama_menu.lower())
            if distance <= max(1, len(search)/3):
                matching_menus.append(menu)

        if not matching_menus:
            found = 1
            query_words = search.split()

            for menu in all_menus:
                menu_words = menu.nama_menu.lower().split()
                for query_word in query_words:
                    if len(query_word) <= 1:
                        continue
                    for menu_word in menu_words:
                        if len(menu_word) <= 1:
                            continue
                        distance = Levenshtein.distance(query_word, menu_word)
                        if distance <= max(1, len(query_word)/2 - 1):
                            matching_menus.append(menu)
                            break

        matching_menus = list(set(matching_menus))
        if not matching_menus:
            found = 0
    else:
        found = -1  # Empty search query

    return matching_menus, search, found

def search_restaurants(search_query):
    search = search_query.strip().lower()
    matching_restaurants = []
    found = -1

    if search:
        all_restaurants = Restaurant.objects.all()
        matching_restaurants = list(Restaurant.objects.filter(nama_restoran__icontains=search))
        found = 2 if matching_restaurants else -1

        for restaurant in all_restaurants:
            distance = Levenshtein.distance(search, restaurant.nama_restoran.lower())
            if distance <= max(1, len(search)/3):
                matching_restaurants.append(restaurant)

        if not matching_restaurants:
            found = 1
            query_words = search.split()

            for restaurant in all_restaurants:
                restaurant_words = restaurant.nama_restoran.lower().split()
                for query_word in query_words:
                    if len(query_word) <= 1:
                        continue
                    for restaurant_word in restaurant_words:
                        if len(restaurant_word) <= 1:
                            continue
                        distance = Levenshtein.distance(query_word, restaurant_word)
                        if distance <= max(1, len(query_word)/2 - 1):
                            matching_restaurants.append(restaurant)
                            break

        matching_restaurants = list(set(matching_restaurants))
        if not matching_restaurants:
            found = 0
    else:
        found = -1

    return matching_restaurants, search, found

def food_search(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_query', '')
        matching_menus, search, found = search_food_items(search_query)

        context = {
            'menus': matching_menus,
            'search': search,
            'found': found
        }

        return render(request, 'food_search.html', context)
    else:
        return render(request, 'food_search.html', {'menus': []})

def resto_search(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_query', '')
        matching_restaurants, search, found = search_restaurants(search_query)

        context = {
            'restaurants': matching_restaurants,
            'search': search,
            'found': found
        }

        return render(request, 'resto_search.html', context)
    else:
        return render(request, 'resto_search.html', {'restaurants': []})

@csrf_exempt
def food_search_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        search_query = data.get('search_query', '')
        matching_menus, search, found = search_food_items(search_query)

        # Serialize the menus into dictionaries
        menus_data = []
        for menu in matching_menus:
            menus_data.append({
                'id': menu.id,
                'nama_menu': menu.nama_menu,
                'harga': menu.harga,
                'categories': [cluster.strip("[]' ") for cluster in menu.get_clusters()]
            })

        context = {
            'menus': menus_data,
            'search': search,
            'found': found
        }
        return JsonResponse(context)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def resto_search_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        search_query = data.get('search_query', '')
        matching_restaurants, search, found = search_restaurants(search_query)

        # Serialize the restaurants into dictionaries
        restaurants_data = []
        for restaurant in matching_restaurants:
            restaurants_data.append({
                'id': restaurant.id,
                'nama_restoran': restaurant.nama_restoran,
                'lokasi': restaurant.lokasi,
                'jenis_suasana': restaurant.jenis_suasana,
                'keramaian_restoran': restaurant.keramaian_restoran,
                'jenis_penyajian': restaurant.jenis_penyajian,
                'ayce_atau_alacarte': restaurant.ayce_atau_alacarte,
                'harga_rata_rata_makanan': restaurant.harga_rata_rata_makanan,
                'gambar': restaurant.gambar,
            })

        context = {
            'restaurants': restaurants_data,
            'search': search,
            'found': found
        }

        return JsonResponse(context)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

def show_json(request):
    data = SearchHistory.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def get_random_restaurant_flutter(request):
    Restaurant.objects.all()
    # randomize 6 restaurants
    random_restaurants = Restaurant.objects.order_by('?')[:6]
    response_data = []
    for restaurant in random_restaurants:
        response_data.append({
            'id': restaurant.id,
            'nama_restoran': restaurant.nama_restoran,
            'lokasi': restaurant.lokasi,
            'jenis_suasana': restaurant.jenis_suasana,
            'keramaian_restoran': restaurant.keramaian_restoran,
            'jenis_penyajian': restaurant.jenis_penyajian,
            'ayce_atau_alacarte': restaurant.ayce_atau_alacarte,
            'harga_rata_rata_makanan': restaurant.harga_rata_rata_makanan,
            'gambar': restaurant.gambar,
        })

    return JsonResponse(response_data, safe=False)