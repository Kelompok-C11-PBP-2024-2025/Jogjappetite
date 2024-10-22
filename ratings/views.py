from django.http import HttpResponse
from django.core import serializers
from ratings.models import Menu, Restaurant

def get_menus(request):
    data = Menu.objects.all() 
    return HttpResponse(
        serializers.serialize("json", data),  
        content_type="application/json"  
    )
def get_restaurants(request):
    data = Restaurant.objects.all() 
    return HttpResponse(
        serializers.serialize("json", data),  
        content_type="application/json"  
    )
