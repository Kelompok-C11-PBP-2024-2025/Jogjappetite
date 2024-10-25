from django.http import JsonResponse
from django.shortcuts import render
from ratings.models import Menu,Restaurant
from explore.models import ExploreHistory
from authentication.models import UserProfile

# Create your views here.
def show_explore_page(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        try:
            # Assume UserProfile is related to the logged-in user
            user_profile = UserProfile.objects.get(user=request.user)
            # Fetch recent history based on the logged-in user, ordered by 'clicked_at'
            recent_history = ExploreHistory.objects.filter(user_profile=user_profile).order_by('-clicked_at')[:5]
        except UserProfile.DoesNotExist:
            # If the user has no UserProfile, set recent_history to None
            recent_history = None
    else:
        # If the user is not logged in, recent_history will be None
        recent_history = None
    
    # Pass recent history only if user is logged in, else pass an empty context
    context = {
        'recent_history': recent_history,
        'menus': Menu.objects.all(),  # Assume categories of the menu
    }
    
    return render(request, "explore.html", context)


def show_menus_explore(request, cluster_name):
    
    menus = Menu.objects.filter(cluster__icontains=cluster_name.lower())  

    context = {
        'menus': menus,
        'cluster_name': cluster_name  
    }
    return render(request, 'menu_by_cluster.html', context)

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


