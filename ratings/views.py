from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from ratings.models import Menu, Ratings, Restaurant

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

def show_main(request):
    ratings = Ratings.objects.all().order_by('-id')
    context = {
        "ratings": ratings
    }
    return render(request, "ratings.html", context)

def show_json(request):
    data = Ratings.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def get_menu_rating(request):
    data = Menu.objects.all()
    return HttpResponse

def get_menu_rating_by_id(request, id):
    data = Ratings.objects.filter(menu_id=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def get_restaurant_rating(request, id):
    data = Ratings.objects.filter(restaurant_id=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def get_latest_restaurant_rating(request, id):
    latest_ratings = Ratings.objects.filter(restaurant_id=id).order_by('-id')[:1]
    data = []
    for p in latest_ratings:
        each_data = {
            "id": p.id,
            "namalengkap": p.user.userprofile.namalengkap,
            "rating": p.rating,
            "pesan_rating": p.pesan_ratingm
        }