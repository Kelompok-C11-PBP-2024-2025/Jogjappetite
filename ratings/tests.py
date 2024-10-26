from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Restaurant, Menu, Ratings
from .forms import AddRatingForm  
from django.utils.html import escape


class RatingsViewsTest(TestCase):
    def setUp(self):
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
        response = self.client.get(reverse('ratings:get_restaurant_ratings_by_id', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')
        context_ratings = response.context['restaurant_ratings']
        self.assertTrue(any(rating.pesan_rating == 'Enak sekali!' for rating in context_ratings))

    def test_main_page_highest_rated_restaurants(self):
        response = self.client.get(reverse('ratings:show_main_page'))
        self.assertEqual(response.status_code, 200)
        highest_rated_restaurants = response.context['highest_rated_restaurants']
        self.assertIn(self.restaurant, highest_rated_restaurants) 

    def test_delete_nonexistent_rating(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ratings:delete_rating', args=[self.restaurant.id, 999]))
        self.assertEqual(response.status_code, 404) 

    def test_json_data_structure(self):
        response = self.client.get(reverse('ratings:show_json', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIsInstance(json_data, list)  
        self.assertTrue(all('id' in entry and 'username' in entry for entry in json_data)) 

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

    def test_edit_rating_unauthorized(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        self.client.login(username='otheruser', password='password')
        response = self.client.post(reverse('ratings:edit_rating', args=[self.restaurant.id, self.rating.id]), {
            'rating': 3,
            'pesan_rating': 'Not allowed to edit!'
        })
        self.assertEqual(response.status_code, 403)

    def test_show_json(self):
        response = self.client.get(reverse('ratings:show_json', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Restaurant', str(response.content))

    def test_show_main_page(self):
        response = self.client.get(reverse('ratings:show_main_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ratings_main_page.html')

    def test_user_ratings_all_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('ratings:user_ratings_all'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enak sekali!')

    def test_user_ratings_all_unauthenticated(self):
        response = self.client.get(reverse('ratings:user_ratings_all'))
        self.assertEqual(response.status_code, 302)  

    def test_add_rating_ajax_missing_fields(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ratings:add_rating_ajax'), {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'success': False, 'error': 'Missing fields'})

    def test_add_rating_ajax_unauthorized(self):
        response = self.client.post(reverse('ratings:add_rating_ajax'), {
            'rating': '5',
            'pesan_rating': 'Great!',
            'menu_review': [self.menu.id],
            'restaurant_id': self.restaurant.id
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 401)

    def test_get_clusters_method(self):
        clusters = self.menu.get_clusters()
        self.assertIn('Main Course', clusters)

    def test_menu_str_method(self):
        self.assertEqual(str(self.menu), 'Nasi Goreng')

    def test_unauthorized_edit_rating(self):
        response = self.client.post(reverse('ratings:edit_rating', args=[self.restaurant.id, self.rating.id]), {
            'rating': 3,
            'pesan_rating': 'Attempted unauthorized edit'
        })
        self.assertEqual(response.status_code, 302)  

    def test_create_rating_invalid_restaurant(self):
        self.client.login(username='testuser', password='password')

        response = self.client.post(reverse('ratings:add_rating_ajax'), {
            'restaurant_id': 999, 
            'menu_review': [self.menu.id],
            'rating': 3,
            'pesan_rating': 'Okay'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 404)
class AddRatingFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.restaurant1 = Restaurant.objects.create(
            nama_restoran='Test Restaurant 1',
            lokasi='Yogyakarta',
            jenis_suasana='Casual',
            keramaian_restoran=3,
            jenis_penyajian='Dine-in',
            ayce_atau_alacarte='A la Carte',
            harga_rata_rata_makanan=50000,
            gambar='http://example.com/image.jpg'
        )
        self.restaurant2 = Restaurant.objects.create(
            nama_restoran='Test Restaurant 2',
            lokasi='Jakarta',
            jenis_suasana='Formal',
            keramaian_restoran=5,
            jenis_penyajian='Takeout',
            ayce_atau_alacarte='A la Carte',
            harga_rata_rata_makanan=80000,
            gambar='http://example.com/image2.jpg'
        )
        self.menu1 = Menu.objects.create(
            nama_menu='Nasi Goreng',
            restoran=self.restaurant1,
            cluster='Main Course',
            harga=30000
        )
        self.menu2 = Menu.objects.create(
            nama_menu='Mie Goreng',
            restoran=self.restaurant2,
            cluster='Main Course',
            harga=25000
        )

    def test_form_initialization_without_restaurant(self):
        form = AddRatingForm()
        self.assertIn('menu_review', form.fields)  

    def test_form_initialization_with_restaurant(self):
        form = AddRatingForm(restaurant=self.restaurant1)
        menu_ids = [menu.id for menu in form.fields['menu_review'].queryset]
        self.assertIn(self.menu1.id, menu_ids) 
        self.assertNotIn(self.menu2.id, menu_ids)  

    def test_form_valid_data(self):
        form_data = {
            'menu_review': self.menu1.id,
            'rating': 4,
            'pesan_rating': 'Delicious!'
        }
        form = AddRatingForm(data=form_data, restaurant=self.restaurant1)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        form_data = {
            'menu_review': self.menu1.id,
            'rating': 6, 
            'pesan_rating': ''
        }
        form = AddRatingForm(data=form_data, restaurant=self.restaurant1)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)  