from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Restaurant, Menu, Ratings

class RatingsViewsTest(TestCase):
    def setUp(self):
        # Setup initial data
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.restaurant = Restaurant.objects.create(
            nama_restoran='Test Restaurant',
            lokasi='Yogyakarta',
            jenis_suasana='Casual',
            keramaian_restoran=3,
            jenis_penyajian='Dine-in',
            ayce_atau_alacarte='A la Carte',
            harga_rata_rata_makanan=50000,
            gambar='http://example.com/image.jpg'
        )
        self.menu = Menu.objects.create(
            nama_menu='Nasi Goreng',
            restoran=self.restaurant,
            cluster='Main Course',
            harga=30000
        )
        self.rating = Ratings.objects.create(
            user=self.user,
            menu_review=self.menu,
            restaurant_review=self.restaurant,
            rating=4,
            pesan_rating='Enak sekali!'
        )

    def test_get_restaurant_ratings_by_id(self):
        # Kirim request ke view
        response = self.client.get(reverse('ratings:get_restaurant_ratings_by_id', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        
        # Verifikasi bahwa nama restoran ada di halaman
        self.assertContains(response, 'Test Restaurant')

        # Cek bahwa `pesan_rating` muncul di context respons
        context_ratings = response.context['restaurant_ratings']
        self.assertTrue(any(rating.pesan_rating == 'Enak sekali!' for rating in context_ratings))

    def test_add_rating_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ratings:add_rating', args=[self.restaurant.id]), {
            'rating': '5',  # Pastikan tipe data sesuai dengan respons JSON
            'pesan_rating': 'Mantap!',
            'menu_review': [self.menu.id]  # Menu ID dalam bentuk list sesuai dengan views
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')  # Tambahkan header AJAX

        # Verifikasi seluruh data dalam JSON respons
        expected_response = {
            'success': True,
            'user_initials': 'TE',           # Inisial dari 'testuser'
            'username': 'testuser',
            'date': response.json().get('date'),  # Gunakan nilai tanggal dari respons
            'rating': '5',                   # Ubah tipe data ke string agar sesuai dengan respons
            'pesan_rating': 'Mantap!',
        }
        
        self.assertJSONEqual(str(response.content, encoding='utf8'), expected_response)

    def test_add_rating_unauthenticated(self):
        response = self.client.post(reverse('ratings:add_rating', args=[self.restaurant.id]), {
            'rating': 5,
            'pesan_rating': 'Mantap!',
            'menu_review': [self.menu.id]
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')  # Tambahkan header AJAX
        # Cek jika terjadi redirect ke halaman login untuk user yang tidak terotentikasi
        self.assertEqual(response.status_code, 302)

    def test_delete_rating_authorized(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ratings:delete_rating', args=[self.restaurant.id, self.rating.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': True, 'message': 'Rating deleted successfully.'})

    def test_delete_rating_unauthorized(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        self.client.login(username='otheruser', password='password')
        response = self.client.post(reverse('ratings:delete_rating', args=[self.restaurant.id, self.rating.id]))
        self.assertEqual(response.status_code, 403)

    def test_show_json(self):
        response = self.client.get(reverse('ratings:show_json', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Restaurant', str(response.content))
