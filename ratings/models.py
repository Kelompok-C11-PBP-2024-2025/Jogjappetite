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
    restoran = models.ForeignKey(Restaurant, on_delete=models.CASCADE)  # This references the id field in Restaurant
    cluster = models.CharField(max_length=255)
    harga = models.IntegerField()

    def get_clusters(self):
        return self.cluster.split(',')
