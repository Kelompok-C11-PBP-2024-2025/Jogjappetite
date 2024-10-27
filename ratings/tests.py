from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Restaurant, Menu, Ratings
from django.utils.html import escape
from django.http import JsonResponse


class RatingsViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
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

    def test_delete_rating_authorized(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ratings:delete_rating', args=[self.restaurant.id, self.rating.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': True, 'message': 'Rating deleted successfully.'})

    def test_delete_rating_unauthorized(self):
        self.client.login(username='otheruser', password='password')
        response = self.client.post(reverse('ratings:delete_rating', args=[self.restaurant.id, self.rating.id]))
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': False, 'message': 'You are not authorized to delete this rating.'})

    def test_edit_rating_authorized(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(
            reverse('ratings:edit_rating', args=[self.restaurant.id, self.rating.id]), 
            {
                'rating': 5,
                'pesan_rating': 'Updated review',
                'menu_review': self.menu.id  # Include required menu field if needed
            }
        )
        # Expecting 200 OK for successful edit
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'success': True, 
            'message': 'Your rating has been successfully updated.',
            'updated_data': {
                'rating': 5,
                'pesan_rating': 'Updated review',
                'menu_review': 'Nasi Goreng',
                'date': self.rating.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })


    def test_edit_rating_unauthorized(self):
        self.client.login(username='otheruser', password='password')
        response = self.client.post(reverse('ratings:edit_rating', args=[self.restaurant.id, self.rating.id]), {
            'rating': 3,
            'pesan_rating': 'Unauthorized edit attempt'
        })
        self.assertEqual(response.status_code, 403)

    def test_add_rating_ajax_missing_fields(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ratings:add_rating_ajax'), {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': False, 'error': 'Missing fields'})

    def test_add_rating_ajax_unauthorized(self):
        """Test unauthorized access for add_rating_ajax"""
        response = self.client.post(reverse('ratings:add_rating_ajax'), {
            'rating': 5,
            'pesan_rating': 'Great!',
            'menu_review': [self.menu.id],
            'restaurant_id': self.restaurant.id
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)  # Expect a redirect to login
        # Optionally, verify that the redirect URL is to the login page
        self.assertIn('/login', response.url)

    def test_show_json_structure(self):
        response = self.client.get(reverse('ratings:show_json', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIsInstance(json_data, list)
        self.assertTrue(all('id' in entry and 'username' in entry for entry in json_data))

    def test_show_main_page_content(self):
        response = self.client.get(reverse('ratings:show_main_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')
        self.assertTemplateUsed(response, 'ratings_main_page.html')

    def test_user_ratings_all_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('ratings:user_ratings_all'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enak sekali!')

    def test_user_ratings_all_unauthenticated(self):
        response = self.client.get(reverse('ratings:user_ratings_all'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    def test_add_rating_ajax_invalid_rating_value(self):
        """Test add_rating_ajax with non-integer or out-of-range rating values"""
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ratings:add_rating_ajax'), {
            'rating': 'five',  # Invalid non-integer rating
            'pesan_rating': 'Great!',
            'menu_review': [self.menu.id],
            'restaurant_id': self.restaurant.id
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('ratings:add_rating_ajax'), {
            'rating': 6,  # Out of range
            'pesan_rating': 'Amazing!',
            'menu_review': [self.menu.id],
            'restaurant_id': self.restaurant.id
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_show_json_no_ratings(self):
        """Test show_json returns empty list when no ratings exist for restaurant"""
        Ratings.objects.all().delete()  # Remove all ratings
        response = self.client.get(reverse('ratings:show_json', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), [])

    def test_delete_rating_get_request(self):
        """Test delete_rating with GET request instead of POST"""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('ratings:delete_rating', args=[self.restaurant.id, self.rating.id]))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_edit_rating_get_request(self):
        """Test edit_rating with GET request instead of POST"""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('ratings:edit_rating', args=[self.restaurant.id, self.rating.id]))
        self.assertEqual(response.status_code, 200)  # Should display the edit form

    def test_user_ratings_all_unauthenticated(self):
        """Test redirect or forbidden for unauthenticated access to user_ratings_all"""
        response = self.client.get(reverse('ratings:user_ratings_all'))
        self.assertEqual(response.status_code, 302)  # Redirect to login if unauthenticated

    def test_add_rating_ajax_invalid_menu_or_restaurant_id(self):
        """Test add_rating_ajax with invalid menu or restaurant IDs"""
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ratings:add_rating_ajax'), {
            'rating': 4,
            'pesan_rating': 'Great food!',
            'menu_review': [99999],  # Nonexistent menu ID
            'restaurant_id': self.restaurant.id
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)  # Should return Not Found

        response = self.client.post(reverse('ratings:add_rating_ajax'), {
            'rating': 4,
            'pesan_rating': 'Great food!',
            'menu_review': [self.menu.id],
            'restaurant_id': 99999  # Nonexistent restaurant ID
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)  # Should return Not Found

    def test_edit_rating_max_length_pesan_rating(self):
        """Test edit_rating with maximum length pesan_rating"""
        self.client.login(username='testuser', password='password')
        max_length_message = 'A' * 255  # Assuming max length is 255 characters
        response = self.client.post(reverse('ratings:edit_rating', args=[self.restaurant.id, self.rating.id]), {
            'rating': 5,
            'pesan_rating': max_length_message,
            'menu_review': self.menu.id
        })
        self.assertEqual(response.status_code, 200)  # Should allow max length message
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
            'success': True,
            'message': 'Your rating has been successfully updated.',
            'updated_data': {
                'rating': 5,
                'pesan_rating': max_length_message,
                'menu_review': 'Nasi Goreng',
                'date': self.rating.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })