from django.utils import timezone
from django.db import models
from ratings.models import Menu, Restaurant
from authentication.models import UserProfile

class ExploreHistory(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='explore_history')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_history')
    clicked_at = models.DateTimeField(default=timezone.now)
    