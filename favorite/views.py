from django.shortcuts import render

def show_main_favorite(request):
    return render(request,"favorite.html")