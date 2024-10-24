from django.shortcuts import render
from ratings.models import Menu,Restaurant

# Create your views here.
def show_explore_page(request):
    return render(request,"explore.html")

def show_menus_explore(request, cluster_name):
    
    menus = Menu.objects.filter(cluster__icontains=cluster_name.lower())  

    context = {
        'menus': menus,
        'cluster_name': cluster_name  
    }
    return render(request, 'menu_by_cluster.html', context)



