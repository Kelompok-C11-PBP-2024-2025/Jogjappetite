import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from authentication.models import UserProfile
from .forms import SignUpForm 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

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


# UNTUK FLUTTER
@csrf_exempt
def login_flutter(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Status login sukses.
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "Login sukses!"
                # Tambahkan data lainnya jika ingin mengirim data ke Flutter.
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login gagal, akun dinonaktifkan."
            }, status=401)

    else:
        return JsonResponse({
            "status": False,
            "message": "Login gagal, periksa kembali email atau kata sandi."
        }, status=401)
    
# UNTUK FLUTTER 
@csrf_exempt
def register_flutter(request):
    if request.method == 'POST':
        try:
            # Decode JSON request body
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')
            full_name = data.get('full_name')
            user_type = data.get('user_type')

            # Validate required fields
            if not all([username, email, password1, password2, full_name, user_type]):
                return JsonResponse({
                    "status": False,
                    "message": "All fields are required."
                }, status=400)

            # Check if passwords match
            if password1 != password2:
                return JsonResponse({
                    "status": False,
                    "message": "Passwords do not match."
                }, status=400)

            # Check if username is already taken
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Username already exists."
                }, status=400)

            # Check if email is already taken
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    "status": False,
                    "message": "Email already exists."
                }, status=400)

            # Create the new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Save user profile data
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                full_name=full_name
            )

            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "User created successfully!"
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                "status": False,
                "message": "Invalid JSON data."
            }, status=400)

    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)
