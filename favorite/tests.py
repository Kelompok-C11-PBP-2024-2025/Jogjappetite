from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ratings.models import Restaurant
from favorite.models import Favorite
import json

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

class FavoriteViewsTest(TestCase):
    def setUp(self):
        # Setup user and restaurant
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Pastikan Anda menambahkan nilai default untuk kolom yang bersifat NOT NULL
        self.restaurant = Restaurant.objects.create(
            nama_restoran='Test Restaurant',
            harga_rata_rata_makanan=50000,
            ayce_atau_alacarte='Ala Carte',
            lokasi='Test Location',
            keramaian_restoran=50  # Berikan nilai default untuk kolom NOT NULL ini
        )
        self.client.login(username='testuser', password='testpassword')
    def test_show_main_favorite(self):
        # Test for showing the main favorite page
        Favorite.objects.create(user=self.user, restaurant=self.restaurant, notes="Delicious")
        response = self.client.get(reverse('favorite:favorite_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Favorite Restaurants')
        self.assertContains(response, 'Delicious')

    def test_list_all_restaurants(self):
        # Test for listing all restaurants
        response = self.client.get(reverse('favorite:list_all_restaurants'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.restaurant.nama_restoran)

    def test_add_to_favorite_post(self):
        # Test for adding a restaurant to favorites with POST
        response = self.client.post(
            reverse('favorite:add_to_favorite', args=[self.restaurant.id]),
            {'notes': 'Great Restaurant'},
            follow=True
        )
        self.assertRedirects(response, reverse('favorite:favorite_list_view'))
        self.assertTrue(Favorite.objects.filter(user=self.user, restaurant=self.restaurant).exists())

    def test_add_to_favorite_without_notes(self):
        # Test for trying to add to favorites without notes
        response = self.client.post(
            reverse('favorite:add_to_favorite', args=[self.restaurant.id]),
            {'notes': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please provide a note')

    def test_add_to_favorite_ajax(self):
        # Test for adding to favorites with AJAX
        response = self.client.post(
            reverse('favorite:add_to_favorite_ajax'),
            content_type='application/json',
            data={'restaurant_id': self.restaurant.id, 'notes': 'Nice Restaurant'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Restaurant added to favorites.', 'redirect_url': '/favorite/'})
        self.assertTrue(Favorite.objects.filter(user=self.user, restaurant=self.restaurant).exists())

    def test_add_to_favorite_ajax_without_data(self):
        # Test AJAX request without providing notes or restaurant_id
        response = self.client.post(
            reverse('favorite:add_to_favorite_ajax'),
            content_type='application/json',
            data={}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': 'Restaurant ID and notes are required.'})

    def test_delete_favorite(self):
        # Test for deleting a favorite
        favorite = Favorite.objects.create(user=self.user, restaurant=self.restaurant, notes='Good food')
        response = self.client.post(
            reverse('favorite:delete_favorite'),
            content_type='application/json',
            data={'favorite_id': favorite.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})
        self.assertFalse(Favorite.objects.filter(id=favorite.id).exists())

    def test_edit_favorite_notes(self):
        # Test for editing notes of a favorite
        favorite = Favorite.objects.create(user=self.user, restaurant=self.restaurant, notes='Good food')
        response = self.client.post(
            reverse('favorite:edit_favorite_notes'),
            content_type='application/json',
            data={'favorite_id': favorite.id, 'notes': 'Amazing food'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Notes updated successfully.'})
        favorite.refresh_from_db()
        self.assertEqual(favorite.notes, 'Amazing food')

    def test_unauthenticated_access(self):
        # Test accessing views without authentication
        self.client.logout()
        response = self.client.get(reverse('favorite:favorite_list_view'))
        self.assertRedirects(response, '/auth/login/?next=/favorite/')

        response = self.client.get(reverse('favorite:list_all_restaurants'))
        self.assertRedirects(response, '/auth/login/?next=/favorite/list-all-restaurants/')

