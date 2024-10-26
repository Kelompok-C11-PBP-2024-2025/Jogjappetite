from django.utils import timezone
from django.db import models
from ratings.models import Menu, Restaurant
from authentication.models import UserProfile
from django.contrib.auth.models import User

class Bookmark(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
        added_on = models.DateTimeField(auto_now_add=True)

        class Meta:
            unique_together = ('user', 'menu')  # User hanya bisa bookmark menu satu kali

        def __str__(self):
            return f"{self.user.username} bookmarked {self.menu.nama_menu}"