from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core import serializers
from ratings.models import Menu, Ratings, Restaurant
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import RatingForm
from django.contrib.auth.decorators import login_required

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

def get_restaurant_ratings_by_id(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    restaurant_ratings = Ratings.objects.filter(restaurant_review=restaurant)
    reviewed_menus = Menu.objects.filter(restoran=restaurant)

    for menu in reviewed_menus:
        menu.cleaned_clusters = [cluster.strip("[]' ") for cluster in menu.get_clusters()]
    
    context = {
        'restaurant': restaurant,
        'restaurant_ratings': restaurant_ratings,
        'reviewed_menus': reviewed_menus,
    }
    return render(request, 'restaurant_ratings.html', context)

@login_required
def add_rating(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.restaurant_review = restaurant  # Assuming you're adding a restaurant rating
            rating.user = request.user  # Assuming user must be logged in
            rating.save()
            return redirect('ratings:get_restaurant_ratings_by_id', id=id)  # Redirect back to the restaurant's ratings
    else:
        form = RatingForm()
    
    return render(request, 'add_rating.html', {'form': form, 'restaurant': restaurant})

@csrf_exempt
def delete_rating(request, rating_id):
    rating = get_object_or_404(Ratings, id=rating_id)
    rating.delete()
    return JsonResponse({'success': True, 'message': 'Rating deleted successfully'})

@csrf_exempt
def edit_rating(request, rating_id):
    rating = get_object_or_404(Ratings, id=rating_id)

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Rating updated successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    form = RatingForm(instance=rating)
    return render(request, 'add_rating.html', {'form': form})