from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

class AuthenticationViewsTest(TestCase):

    def setUp(self):
        # Create a test user for login tests
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_register_view_get(self):
        response = self.client.get(reverse('authentication:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_view_post_success(self):
        response = self.client.post(reverse('authentication:register'), {
            'username': 'newuser',
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'user_type': 'customer'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('authentication:login'))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_view_post_failure(self):
        response = self.client.post(reverse('authentication:register'), {
            'username': 'newuser',
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass',
            'user_type': 'customer'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The two password fields didn’t match.')
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_register_view_post_missing_fields(self):
        # Missing required fields like 'username' and 'email'
        response = self.client.post(reverse('authentication:register'), {
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertFalse(User.objects.filter(email="newuser@example.com").exists())

    def test_login_view_get(self):
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_success(self):
        response = self.client.post(reverse('authentication:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('explore:show_explore_page'))

    def test_login_view_post_failure(self):
        response = self.client.post(reverse('authentication:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sorry, incorrect username or password. Please try again.')

    def test_login_view_redirect_after_authentication(self):
        # Use a real protected view name that exists in your URL patterns
        redirect_url = reverse('explore:show_explore_page')  # Replace with an actual protected view
        response = self.client.post(
            reverse('authentication:login') + f'?next={redirect_url}',
            {'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertRedirects(response, redirect_url)


    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('authentication:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('explore:show_explore_page'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_view_authenticated_user_redirect(self):
        # Test that an authenticated user is redirected if they try to access the login page
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('authentication:login'))
        self.assertRedirects(response, reverse('explore:show_explore_page'))

    def test_register_view_authenticated_user_redirect(self):
        # Test that an authenticated user is redirected if they try to access the registration page
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('authentication:register'))
        self.assertRedirects(response, reverse('explore:show_explore_page'))
