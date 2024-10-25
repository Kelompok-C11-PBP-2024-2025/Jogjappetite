from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    nama_restoran = models.CharField(max_length=255)
    lokasi = models.CharField(max_length=255)
    jenis_suasana = models.CharField(max_length=255)
    keramaian_restoran = models.IntegerField()
    jenis_penyajian = models.CharField(max_length=255)
    ayce_atau_alacarte = models.CharField(max_length=255)
    harga_rata_rata_makanan = models.IntegerField()
    gambar = models.URLField()


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    nama_menu = models.CharField(max_length=255)
    restoran = models.ForeignKey(Restaurant, on_delete=models.CASCADE)  
    cluster = models.CharField(max_length=255)
    harga = models.IntegerField()

    def get_clusters(self):
        return self.cluster.split(',')
    def __str__(self):
        return self.nama_menu 

class Ratings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_review = models.ForeignKey(Menu, on_delete=models.CASCADE)
    restaurant_review = models.ForeignKey(Restaurant, on_delete=models.CASCADE, blank=True, null=True)
    rating = models.IntegerField(default=1, choices=((i,i) for i in range(1, 6)))
    pesan_rating = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
