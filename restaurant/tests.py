from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from authentication.models import UserProfile
from ratings.models import Restaurant, Ratings, Menu
from restaurant.forms import RestaurantForm

class RestaurantViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users for testing
        self.owner_user = User.objects.create_user(username='owner', password='password')
        self.customer_user = User.objects.create_user(username='customer', password='password')
        
        # Assign user profiles
        UserProfile.objects.create(user=self.owner_user, user_type='restaurant')
        UserProfile.objects.create(user=self.customer_user, user_type='customer')

        # Sample restaurant for testing
        self.restaurant = Restaurant.objects.create(
            nama_restoran="Sample Restaurant",
            lokasi="Sample Location",
            jenis_suasana="Casual",
            keramaian_restoran=3,
            jenis_penyajian="Dine-In",
            ayce_atau_alacarte="Alacarte",
            harga_rata_rata_makanan=100000,
            gambar="sample.jpg"
        )

    def test_customer_restaurant_list_view(self):
        self.client.login(username='customer', password='password')
        response = self.client.get(reverse('restaurant:customer_restaurant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customer_restaurant_list.html')
        self.assertIn('restaurants', response.context)

    def test_owner_restaurant_list_view(self):
        self.client.login(username='owner', password='password')
        response = self.client.get(reverse('restaurant:owner_restaurant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'owner_restaurant_list.html')
        self.assertIn('restaurants', response.context)

    def test_add_restaurant_view(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(reverse('restaurant:add_restaurant'), {
            'nama_restoran': "New Restaurant",
            'lokasi': "New Location",
            'jenis_suasana': "Cozy",
            'keramaian_restoran': 2,
            'jenis_penyajian': "Takeout",
            'ayce_atau_alacarte': "AYCE",
            'harga_rata_rata_makanan': 120000,
            'gambar': "new.jpg"
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Restaurant added successfully!'})

    def test_edit_restaurant_view(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(reverse('restaurant:edit_restaurant', args=[self.restaurant.pk]), {
            'nama_restoran': "Updated Restaurant",
            'lokasi': "Updated Location",
            'jenis_suasana': "Chic",
            'keramaian_restoran': 4,
            'jenis_penyajian': "Dine-In",
            'ayce_atau_alacarte': "Alacarte",
            'harga_rata_rata_makanan': 150000,
            'gambar': "updated.jpg"
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})
        updated_restaurant = Restaurant.objects.get(pk=self.restaurant.pk)
        self.assertEqual(updated_restaurant.nama_restoran, "Updated Restaurant")

    def test_delete_restaurant_view(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(reverse('restaurant:delete_restaurant', args=[self.restaurant.pk]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})
        self.assertFalse(Restaurant.objects.filter(pk=self.restaurant.pk).exists())



    def test_add_restaurant_view_invalid_data(self):
        self.client.login(username='owner', password='password')
        response = self.client.post(reverse('restaurant:add_restaurant'), {
            'nama_restoran': "",  # invalid empty name
            'lokasi': "New Location",
            'jenis_suasana': "Cozy",
            'keramaian_restoran': 2,
            'jenis_penyajian': "Takeout",
            'ayce_atau_alacarte': "AYCE",
            'harga_rata_rata_makanan': 120000,
            'gambar': "new.jpg"
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json())


class DecoratorTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users for testing
        self.owner_user = User.objects.create_user(username='owner', password='password')
        self.customer_user = User.objects.create_user(username='customer', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        
        # Assign user profiles with specific types
        UserProfile.objects.create(user=self.owner_user, user_type='restaurant')
        UserProfile.objects.create(user=self.customer_user, user_type='customer')
        UserProfile.objects.create(user=self.other_user, user_type='other')

    def test_user_is_owner_decorator_with_owner(self):
        self.client.login(username='owner', password='password')
        response = self.client.get(reverse('restaurant:owner_restaurant_list'))
        self.assertEqual(response.status_code, 200)

    def test_user_is_owner_decorator_with_non_owner(self):
        self.client.login(username='customer', password='password')
        response = self.client.get(reverse('restaurant:owner_restaurant_list'))
        self.assertRedirects(response, reverse('explore:show_explore_page'))

        self.client.login(username='other', password='password')
        response = self.client.get(reverse('restaurant:owner_restaurant_list'))
        self.assertRedirects(response, reverse('explore:show_explore_page'))

    def test_user_is_customer_decorator_with_customer(self):
        self.client.login(username='customer', password='password')
        response = self.client.get(reverse('restaurant:customer_restaurant_list'))
        self.assertEqual(response.status_code, 200)

    def test_user_is_customer_decorator_with_non_customer(self):
        self.client.login(username='owner', password='password')
        response = self.client.get(reverse('restaurant:customer_restaurant_list'))
        self.assertRedirects(response, reverse('explore:show_explore_page'))

        self.client.login(username='other', password='password')
        response = self.client.get(reverse('restaurant:customer_restaurant_list'))
        self.assertRedirects(response, reverse('explore:show_explore_page'))
class RestaurantFormTests(TestCase):
    def setUp(self):
        # Valid data for the form
        self.valid_data = {
            'nama_restoran': "Sample Restaurant",
            'lokasi': "Sample Location",
            'jenis_suasana': "Casual",
            'keramaian_restoran': 3,
            'jenis_penyajian': "Dine-In",
            'ayce_atau_alacarte': "Alacarte",
            'harga_rata_rata_makanan': 100000,
            'gambar': "sample.jpg"
        }
        
    def test_restaurant_form_valid_data(self):
        """Test the form with valid data."""
        form = RestaurantForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_restaurant_form_empty_name(self):
        """Test the form with an empty restaurant name."""
        invalid_data = self.valid_data.copy()
        invalid_data['nama_restoran'] = ""
        form = RestaurantForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nama_restoran', form.errors)

    def test_restaurant_form_invalid_crowd_level(self):
        """Test the form with an invalid crowd level (non-integer value)."""
        invalid_data = self.valid_data.copy()
        invalid_data['keramaian_restoran'] = "Many"  # Invalid non-integer
        form = RestaurantForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('keramaian_restoran', form.errors)

    def test_restaurant_form_missing_required_fields(self):
        """Test the form with missing required fields."""
        invalid_data = {}  # Empty form data
        form = RestaurantForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        required_fields = ['nama_restoran', 'lokasi', 'jenis_suasana', 
                           'keramaian_restoran', 'jenis_penyajian', 
                           'ayce_atau_alacarte', 'harga_rata_rata_makanan', 'gambar']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_restaurant_form_widgets(self):
        """Test that the form widgets are correctly set."""
        form = RestaurantForm()
        self.assertEqual(form.fields['nama_restoran'].widget.attrs['placeholder'], 'Enter restaurant name')
        self.assertEqual(form.fields['lokasi'].widget.attrs['placeholder'], 'Enter restaurant location')
        self.assertEqual(form.fields['jenis_suasana'].widget.attrs['placeholder'], 'Enter restaurant ambiance type')
        self.assertEqual(form.fields['keramaian_restoran'].widget.attrs['placeholder'], 'Enter crowd level of the restaurant')
        self.assertEqual(form.fields['jenis_penyajian'].widget.attrs['placeholder'], 'Enter serving type')
        self.assertEqual(form.fields['ayce_atau_alacarte'].widget.attrs['placeholder'], 'Enter AYCE or Alacarte')
        self.assertEqual(form.fields['harga_rata_rata_makanan'].widget.attrs['placeholder'], 'Enter average food price')
        self.assertEqual(form.fields['gambar'].widget.attrs['placeholder'], 'Upload restaurant image')
