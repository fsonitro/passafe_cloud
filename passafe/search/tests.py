from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from password_vault.models import PasswordEntry

class SearchViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='password123')
        # Create a test PasswordEntry
        self.entry = PasswordEntry.objects.create(
            user=self.user,
            title='Test Entry',
            username='testuser_entry',
            created_at=timezone.now()
        )

    def test_login_required(self):
        # When not logged in, should redirect to login
        search_url = reverse('search:search_entries')  # Include namespace 'search:'
        response = self.client.get(f'{search_url}?q=Test')
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 301])

    def test_search_returns_results(self):
        # Login and perform a search
        self.client.login(username='testuser', password='password123')
        search_url = reverse('search:search_entries')  # Include namespace 'search:'
        response = self.client.get(f'{search_url}?q=Test')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Test Entry')
