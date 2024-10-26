from django.shortcuts import render, redirect
from ratings.models import Menu,Restaurant
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import SearchHistory
from django.contrib.auth.decorators import login_required
import Levenshtein

@login_required
def search_history_view(request):
    # Fetch user search history (maximum of 5)
    user_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, 'your_template.html', {'user_history': user_history})

@login_required
def save_search_history(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        if query:
            # Save the new search query in the history
            user = request.user
            SearchHistory.objects.create(user=user, query=query)

            # Limit the history to 5 searches
            user_history = SearchHistory.objects.filter(user=user).order_by('-created_at')
            if user_history.count() > 5:
                user_history.order_by('created_at').first().delete()

            # Redirect based on the action button clicked
            if 'food_search' in request.GET:
                return redirect('food_search')  # Replace with your actual URL or logic
            elif 'resto_search' in request.GET:
                return redirect('resto_search')  # Replace with your actual URL or logic

    return redirect('your_template')  # If no valid action, redirect to default search template

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
        search = request.GET.get('search', '').strip()
        if search:
            all_menus = Menu.objects.all()
            matching_menus = []

            for menu in all_menus:
                distance = Levenshtein.distance(search.lower(), menu.name.lower())
                if distance <= 3:  # Adjust the threshold based on your preference for "closeness"
                    matching_menus.append((menu, distance))

            # Sort by distance in ascending order (closer matches come first)
            matching_menus = sorted(matching_menus, key=lambda x: x[1])
            # Extract only the menu objects from the list
            menus = [menu[0] for menu in matching_menus]
        else:
            menus = []

        context = {
            'menus': menus,
            'search': search
        }

        return render(request, 'food_search.html', context)
    else:
        return render(request, 'food_search.html', {'menus': []})
    
def resto_search(request):
    if request.method == 'GET':
        search = request.GET.get('search', '').strip()
        if search:
            all_restaurants = Restaurant.objects.all()
            matching_restaurants = []

            for restaurant in all_restaurants:
                distance = Levenshtein.distance(search.lower(), restaurant.name.lower())
                if distance <= 3:  # Adjust the threshold as needed
                    matching_restaurants.append((restaurant, distance))

            # Sort by distance in ascending order (closest matches first)
            matching_restaurants = sorted(matching_restaurants, key=lambda x: x[1])
            # Extract only restaurant objects from the list
            restaurants = [restaurant[0] for restaurant in matching_restaurants]
        else:
            restaurants = []

        context = {
            'restaurants': restaurants,
            'search': search
        }

        return render(request, 'resto_search.html', context)
    else:
        return render(request, 'resto_search.html', {'restaurants': []})