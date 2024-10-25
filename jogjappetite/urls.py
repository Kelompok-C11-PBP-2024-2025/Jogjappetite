"""
URL configuration for jogjappetite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('ratings/', include('ratings.urls')),  # Mengarahkan ke URLs di aplikasi 'ratings'
    path('search/', include('search.urls')),
    path('explore/', include('explore.urls')),
=======
    path('ratings/', include('ratings.urls')),   # Mengarahkan ke URLs di aplikasi 'ratings'
    path('favorite', include('favorite.urls')),  # Mengarahkan URLs di aplikasi 'favorite'
     path('restaurant/', include('restaurant.urls')), # mengarahkan ke URLs di aplikasi 'restaurant'

    path('ratings/', include('ratings.urls')), 
    path('', include('explore.urls')),  
>>>>>>> 3845a634fa579fae62a00f1ede9eba78e8c3a877
    path('auth/', include('authentication.urls')),
]
