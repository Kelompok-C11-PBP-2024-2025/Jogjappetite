from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ratings.models import Restaurant
from favorite.models import Favorite
import json  # Tambahkan impor ini

class FavoriteTests(TestCase):
    def setUp(self):
        # Buat user dan login
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # Buat restoran
        self.restaurant = Restaurant.objects.create(
            nama_restoran='Test Restaurant',
            harga_rata_rata_makanan=50000,
            lokasi='Test Location',
            ayce_atau_alacarte='Ala Carte',
            gambar='path/to/image.jpg',
            keramaian_restoran=3
        )

    def test_add_favorite(self):
        response = self.client.post(reverse('favorite:add_to_favorite', args=[self.restaurant.id]), {
            'notes': 'Great food!'
        })
        self.assertEqual(response.status_code, 302)  # Redirected
        self.assertTrue(Favorite.objects.filter(user=self.user, restaurant=self.restaurant).exists())

    def test_add_favorite_without_notes(self):
        response = self.client.post(reverse('favorite:add_to_favorite', args=[self.restaurant.id]), {
            'notes': ''
        })
        self.assertEqual(response.status_code, 200)  # Tetap di halaman form
        self.assertContains(response, "Please provide a note")

    def test_delete_favorite(self):
        favorite = Favorite.objects.create(user=self.user, restaurant=self.restaurant, notes='Delicious food')
        response = self.client.post(reverse('favorite:delete_favorite'), json.dumps({'favorite_id': favorite.id}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Favorite.objects.filter(id=favorite.id).exists())

    def test_show_favorite_page(self):
        Favorite.objects.create(user=self.user, restaurant=self.restaurant, notes='Delicious food')
        response = self.client.get(reverse('favorite:favorite_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Favorite Restaurants')

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse('favorite:favorite_list_view'))
        self.assertEqual(response.status_code, 302)  # Redirected to login
        self.assertRedirects(response, '/auth/login/?next=/favorite/')
