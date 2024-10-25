from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm 

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('explore:show_explore_page')  
        else:
            messages.info(request, "Sorry, incorrect username or password. Please try again.")
            context = {}
            return render(request, "login.html", context)

    if request.user.is_authenticated:
        return redirect('explore:show_explore_page')  
    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('authentication:login')  
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm() 

    context = {"form": form}
    if request.user.is_authenticated:
        return redirect('explore:show_explore_page')  
    return render(request, "register.html", context)


def logout_user(request):
    logout(request)
    response = redirect('explore:show_explore_page')
    response.delete_cookie('last_login')
    return response
