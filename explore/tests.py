from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from explore.models import Bookmark
from ratings.models import Menu, Restaurant

class ExploreViewsTest(TestCase):

    def setUp(self):
        # Setup user, restaurant, and menu for tests
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.restaurant = Restaurant.objects.create(
            nama_restoran='Test Restaurant',
            lokasi='Test Location',
            jenis_suasana='Casual',
            keramaian_restoran=3,
            jenis_penyajian='Dine-in',
            ayce_atau_alacarte='A la carte',
            harga_rata_rata_makanan=50000,
            gambar='https://example.com/restaurant.jpg'
        )
        self.menu = Menu.objects.create(
            nama_menu='Test Menu',
            restoran=self.restaurant,
            cluster='Asian',
            harga=20000
        )
        self.bookmark_url = reverse('explore:toggle_bookmark', args=[self.menu.id])
        self.bookmarks_url = reverse('explore:get_user_bookmarks')

    def test_show_explore_page(self):
        response = self.client.get(reverse('explore:show_explore_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'explore.html')

    def test_show_menus_explore(self):
        response = self.client.get(reverse('explore:show_menus_explore', args=['asian']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu_by_cluster.html')
        self.assertContains(response, self.menu.nama_menu)

    def test_toggle_bookmark_login_required(self):
        # Test that bookmark requires login
        response = self.client.post(self.bookmark_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Log in and bookmark
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.bookmark_url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'bookmarked', 'message': 'Menu bookmarked successfully'})

        # Test unbookmark
        response = self.client.post(self.bookmark_url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'unbookmarked', 'message': 'Bookmark removed successfully'})

    def test_get_user_bookmarks(self):
        # Test retrieving bookmarks
        self.client.login(username='testuser', password='password')
        
        # Create a bookmark
        Bookmark.objects.create(user=self.user, menu=self.menu)
        
        response = self.client.get(self.bookmarks_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookmarks', response.json())
        self.assertEqual(len(response.json()['bookmarks']), 1)
        self.assertEqual(response.json()['bookmarks'][0]['name'], 'Test Menu')

    def test_menu_details(self):
        response = self.client.get(reverse('explore:menu_details', args=[self.menu.id]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'name': self.menu.nama_menu,
            'restaurant': self.restaurant.nama_restoran,
            'price': self.menu.harga
        })

    def test_toggle_bookmark_invalid_menu(self):
        self.client.login(username='testuser', password='password')
        invalid_bookmark_url = reverse('explore:toggle_bookmark', args=[999])  # Non-existent menu ID
        response = self.client.post(invalid_bookmark_url)
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'Menu not found'})
