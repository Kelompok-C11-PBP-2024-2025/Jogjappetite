from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SearchHistory
from ratings.models import Menu, Restaurant
from django.utils import timezone

class SearchViewsTest(TestCase):

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass')

        # Log in the test user
        self.client.login(username='testuser1', password='testpass')

        # Create SearchHistory entries for user1
        for i in range(5):
            SearchHistory.objects.create(user=self.user1, query=f"test query {i}")

        # Create Restaurants
        self.restaurant1 = Restaurant.objects.create(
            nama_restoran='Test Restaurant',
            lokasi='Test Location',
            jenis_suasana='Cozy',
            keramaian_restoran=3,
            jenis_penyajian='Self-service',
            ayce_atau_alacarte='Ala Carte',
            harga_rata_rata_makanan=10000,
            gambar='http://example.com/image.jpg'
        )
        self.restaurant2 = Restaurant.objects.create(
            nama_restoran='Another Restaurant',
            lokasi='Another Location',
            jenis_suasana='Casual',
            keramaian_restoran=5,
            jenis_penyajian='Waiter service',
            ayce_atau_alacarte='All You Can Eat',
            harga_rata_rata_makanan=20000,
            gambar='http://example.com/image2.jpg'
        )

        # Create Menus
        self.menu1 = Menu.objects.create(
            nama_menu='Test Menu 1',
            restoran=self.restaurant1,
            cluster='cluster1,cluster2',
            harga=15000
        )
        self.menu2 = Menu.objects.create(
            nama_menu='Another Menu',
            restoran=self.restaurant2,
            cluster='cluster3',
            harga=20000
        )

    def test_get_search_history(self):
        # Test getting search history for logged-in user
        response = self.client.get(reverse('search:get-search-history'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(len(response.json()['history']), 5)

    def test_get_search_history_no_entries(self):
        # Clear history
        SearchHistory.objects.filter(user=self.user1).delete()
        response = self.client.get(reverse('search:get-search-history'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(len(response.json()['history']), 0)

    def test_get_search_history_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('search:get-search-history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_save_search_history_new_query(self):
        # Save a new search query
        response = self.client.get(reverse('search:save_search_history'), {'search_query': 'new test query'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(SearchHistory.objects.filter(user=self.user1, query='new test query').exists())
        self.assertEqual(SearchHistory.objects.filter(user=self.user1).count(), 5)  # Oldest should be deleted

    def test_save_search_history_existing_query(self):
        # Update existing query's created_at
        response = self.client.get(reverse('search:save_search_history'), {'search_query': 'test query 2'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        updated_entry = SearchHistory.objects.get(user=self.user1, query='test query 2')
        self.assertTrue((timezone.now() - updated_entry.created_at).seconds < 5)
        self.assertEqual(SearchHistory.objects.filter(user=self.user1).count(), 5)

    def test_save_search_history_no_query(self):
        # Try to save empty query
        response = self.client.get(reverse('search:save_search_history'), {'search_query': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(SearchHistory.objects.filter(user=self.user1).count(), 5)

    def test_save_search_history_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('search:save_search_history'), {'search_query': 'test'})
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_delete_search_history_valid(self):
        history_item = SearchHistory.objects.filter(user=self.user1).first()
        response = self.client.post(reverse('search:delete_search_history', args=[history_item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertFalse(SearchHistory.objects.filter(id=history_item.id).exists())

    def test_delete_search_history_invalid_id(self):
        response = self.client.post(reverse('search:delete_search_history', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_search_history_not_owned(self):
        other_history_item = SearchHistory.objects.create(user=self.user2, query='other user query')
        response = self.client.post(reverse('search:delete_search_history', args=[other_history_item.id]))
        self.assertEqual(response.status_code, 404)

    def test_delete_search_history_get_request(self):
        history_item = SearchHistory.objects.filter(user=self.user1).first()
        response = self.client.get(reverse('search:delete_search_history', args=[history_item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], "Invalid request.")
        self.assertTrue(SearchHistory.objects.filter(id=history_item.id).exists())

    def test_food_search_exact_match(self):
        response = self.client.get(reverse('search:food_search'), {'search_query': 'Test Menu 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Menu 1')
        self.assertEqual(response.context['found'], 2)

    def test_food_search_approximate_match(self):
        response = self.client.get(reverse('search:food_search'), {'search_query': 'Test Menu'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Menu 1')
        self.assertIn(response.context['found'], [1, 2])

    def test_food_search_no_match(self):
        response = self.client.get(reverse('search:food_search'), {'search_query': 'Nonexistent Menu'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Menu 1')
        self.assertEqual(len(response.context['menus']), 0)
        self.assertEqual(response.context['found'], 0)

    def test_food_search_empty_query(self):
        response = self.client.get(reverse('search:food_search'), {'search_query': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['menus']), 0)
        self.assertEqual(response.context['found'], -1)

    def test_food_search_non_get_request(self):
        response = self.client.post(reverse('search:food_search'), {'search_query': 'Test Menu 1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['menus']), 0)

    def test_resto_search_exact_match(self):
        response = self.client.get(reverse('search:resto_search'), {'search_query': 'Test Restaurant'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')
        self.assertEqual(response.context['found'], 2)

    def test_resto_search_approximate_match(self):
        response = self.client.get(reverse('search:resto_search'), {'search_query': 'Test Rest'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Restaurant')
        self.assertIn(response.context['found'], [1, 2])

    def test_resto_search_no_match(self):
        response = self.client.get(reverse('search:resto_search'), {'search_query': 'Nonexistent Restaurant'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Restaurant')
        self.assertEqual(len(response.context['restaurants']), 0)
        self.assertEqual(response.context['found'], 0)

    def test_resto_search_empty_query(self):
        response = self.client.get(reverse('search:resto_search'), {'search_query': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['restaurants']), 0)
        self.assertEqual(response.context['found'], -1)

    def test_resto_search_non_get_request(self):
        response = self.client.post(reverse('search:resto_search'), {'search_query': 'Test Restaurant'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['restaurants']), 0)

class MenuModelTest(TestCase):
    def test_get_clusters(self):
        restaurant = Restaurant.objects.create(
            nama_restoran='Test Restaurant',
            lokasi='Test Location',
            jenis_suasana='Cozy',
            keramaian_restoran=3,
            jenis_penyajian='Self-service',
            ayce_atau_alacarte='Ala Carte',
            harga_rata_rata_makanan=10000,
            gambar='http://example.com/image.jpg'
        )
        menu = Menu.objects.create(
            nama_menu='Test Menu',
            restoran=restaurant,
            cluster='cluster1,cluster2,cluster3',
            harga=15000
        )
        clusters = menu.get_clusters()
        self.assertEqual(clusters, ['cluster1', 'cluster2', 'cluster3'])
