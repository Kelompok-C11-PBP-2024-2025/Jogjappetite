from django.db import models
from django.contrib.auth.models import User


from ratings.models import Menu, Restaurant

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=10)
