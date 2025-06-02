from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import Author


class RegistrationTests(APITestCase):
    """Tests for user registration"""

    def test_register_creates_user(self):
        """Test that POST to register creates a new user"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'display_name': 'New User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Author.objects.filter(username='newuser').exists())

    def test_register_user_not_approved_by_default(self):
        """New users should not be approved automatically"""
        url = reverse('register')
        data = {
            'username': 'pendinguser',
            'email': 'pending@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        self.client.post(url, data, format='json')
        user = Author.objects.get(username='pendinguser')
        self.assertFalse(user.is_approved)

    def test_register_with_mismatched_passwords_fails(self):
        """Registration should fail if passwords don't match"""
        url = reverse('register')
        data = {
            'username': 'baduser',
            'email': 'bad@example.com',
            'password': 'testpass123',
            'password2': 'differentpass',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_duplicate_username_fails(self):
        """Can't register with a username that already exists"""
        Author.objects.create_user(username='existing', password='pass', email='e@e.com')
        url = reverse('register')
        data = {
            'username': 'existing',
            'email': 'other@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """Tests for JWT login"""

    def setUp(self):
        self.user = Author.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com',
            is_approved=True
        )

    def test_login_returns_tokens(self):
        """Successful login should return access and refresh tokens"""
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_wrong_password_fails(self):
        """Wrong password should return 401"""
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorTests(APITestCase):
    """Tests for author endpoints"""

    def setUp(self):
        self.user = Author.objects.create_user(
            username='authuser',
            password='pass123',
            email='auth@test.com',
            is_approved=True
        )
        self.client.force_authenticate(user=self.user)

    def test_get_current_user(self):
        """Should return the logged in user's data"""
        url = reverse('current_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'authuser')

    def test_list_authors_is_public(self):
        """Anyone should be able to see the list of authors"""
        self.client.logout()
        url = reverse('author_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
