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

@login_required
def get_search_history(request):
    if request.method == 'GET':
        user_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
        history_data = [{'id': item.id, 'query': item.query} for item in user_history]
        return JsonResponse({'success': True, 'history': history_data})

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
@login_required
def delete_search_history(request, history_id):
    if request.method == "POST":
        # Find the history item that matches the given ID and belongs to the logged-in user
        history_item = get_object_or_404(SearchHistory, id=history_id, user=request.user)
        history_item.delete()
        return JsonResponse({"success": True, "message": "Search history deleted successfully."})
    return JsonResponse({"success": False, "message": "Invalid request."})

def food_search(request):
    if request.method == 'GET':
        search = request.GET.get('search_query', '').strip().lower()
        if search:
            all_menus = Menu.objects.all()
            matching_menus = list(Menu.objects.filter(nama_menu__icontains=search))
            found = 2

            for menu in all_menus:
                distance = Levenshtein.distance(search.lower(), menu.nama_menu.lower())
                if distance <= max(1, len(search)/3):
                    matching_menus.append(menu)

            if(matching_menus == []):
                found = 1
                # Split the search query into individual words
                query_words = search.split()

                for menu in all_menus:
                    # Split the menu name into individual words
                    menu_words = menu.nama_menu.lower().split()

                    # Check for close matches between query words and menu words
                    found_match = False
                    for query_word in query_words:
                        if(len(query_word) == 1):
                            continue
                        for menu_word in menu_words:
                            if(len(menu_word) == 1):
                                continue
                            distance = Levenshtein.distance(query_word, menu_word)
                            if distance <= max(1, len(query_word)/2 - 1):  # Adjust threshold as needed
                                matching_menus.append(menu)
                                found_match = True
                                break
                        if found_match:
                            break

            # Remove duplicates if any were added multiple times
            matching_menus = list(set(matching_menus))
            if(matching_menus == []):
                found = 0
        else:
            matching_menus = []
            found = -1

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
        search = request.GET.get('search_query', '').strip().lower()
        if search:
            all_restaurants = Restaurant.objects.all()
            matching_restaurants = list(Restaurant.objects.filter(nama_restoran__icontains=search))
            found = 2

            for restaurant in all_restaurants:
                distance = Levenshtein.distance(search.lower(), restaurant.nama_restoran.lower())
                if distance <= max(1, len(search) / 3):
                    matching_restaurants.append(restaurant)

            if matching_restaurants == []:
                found = 1
                query_words = search.split()

                for restaurant in all_restaurants:
                    restaurant_words = restaurant.nama_restoran.lower().split()

                    found_match = False
                    for query_word in query_words:
                        if len(query_word) == 1:
                            continue
                        for restaurant_word in restaurant_words:
                            if len(restaurant_word) == 1:
                                continue
                            distance = Levenshtein.distance(query_word, restaurant_word)
                            if distance <= max(1, len(query_word) / 2 - 1):
                                matching_restaurants.append(restaurant)
                                found_match = True
                                break
                        if found_match:
                            break

            matching_restaurants = list(set(matching_restaurants))
            if matching_restaurants == []:
                found = 0
        else:
            matching_restaurants = []
            found = -1

        context = {
            'restaurants': matching_restaurants,
            'search': search,
            'found': found
        }

        return render(request, 'resto_search.html', context)
    else:
        return render(request, 'resto_search.html', {'restaurants': []})

@login_required
def show_json(request):
    data = SearchHistory.objects.filter(user=request.user)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")