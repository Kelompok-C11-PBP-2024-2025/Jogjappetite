from django.urls import path
from authentication.views import *

app_name = 'authentication'

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),

    # untuk flutter
    path('login-flutter/', login_flutter, name='login-flutter'), 
    path('register-flutter/', register_flutter, name='register-flutter')
]