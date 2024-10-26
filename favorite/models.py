from django.db import models
from django.contrib.auth.models import User
from ratings.models import Restaurant

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    notes = models.TextField()  # Field untuk menyimpan alasan
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'restaurant')  # Menghindari duplikasi favorit

    def __str__(self):
        return f"{self.user.username} - {self.restaurant.nama_restoran}"