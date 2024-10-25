from django.http import JsonResponse
from django.shortcuts import render
from ratings.models import Menu,Restaurant
from explore.models import ExploreHistory

# Create your views here.
def show_explore_page(request):
    user_profile = request.user.userprofile  # Asumsi bahwa UserProfile terkait dengan User
    # Ambil 5 riwayat terakhir berdasarkan waktu klik
    recent_history = ExploreHistory.objects.filter(user_profile=user_profile).order_by('-clicked_at')[:5]
    
    # Kirim data history ke template
    context = {
        'recent_history': recent_history,
        'menus': Menu.objects.all()  # Asumsi kategori menu
    }
    return render(request,"explore.html")

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


