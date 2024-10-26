from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationViewsTest(TestCase):

    def setUp(self):
        # Create a test user for login tests
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_register_view_get(self):
        # Test the GET request for the register view
        response = self.client.get(reverse('authentication:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_view_post_success(self):
        # Test the POST request for successful registration
        response = self.client.post(reverse('authentication:register'), {
            'username': 'newuser',
            'full_name': 'New User',  # Include all required fields
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'user_type': 'customer'  # Ensure this is a valid choice
        })
        # Check if redirected after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('authentication:login'))
        # Check if the new user was created
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_view_post_failure(self):
        # Test the POST request for failed registration due to password mismatch
        response = self.client.post(reverse('authentication:register'), {
            'username': 'newuser',
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass',  # Mismatching passwords
            'user_type': 'customer'
        })
        # Check for a 200 response, meaning the form was re-rendered with errors
        self.assertEqual(response.status_code, 200)
        # Check for a specific error message next to the password fields
        self.assertContains(response, 'The two password fields didn’t match.')
        # Ensure that no new user was created
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_login_view_get(self):
        # Test the GET request for the login view
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_success(self):
        # Test the POST request for a successful login
        response = self.client.post(reverse('authentication:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Check if redirected after successful login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('explore:show_explore_page'))

    def test_login_view_post_failure(self):
        # Test the POST request for failed login
        response = self.client.post(reverse('authentication:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'  # Incorrect password
        })
        # Check for a 200 response, meaning the form was re-rendered with errors
        self.assertEqual(response.status_code, 200)
        # Check for an error message indicating incorrect credentials
        self.assertContains(response, 'Sorry, incorrect username or password. Please try again.')

    def test_logout_view(self):
        # Log in the user
        self.client.login(username='testuser', password='testpass123')
        # Test the logout functionality
        response = self.client.get(reverse('authentication:logout'))
        # Check if redirected after logout
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('explore:show_explore_page'))
        # Ensure the session has been cleared
        self.assertNotIn('_auth_user_id', self.client.session)
