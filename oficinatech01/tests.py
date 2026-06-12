from django.contrib.auth.models import User
from django.test import TestCase


class AuthFlowTests(TestCase):
    def test_login_page_renders_login_form(self):
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password"')

    def test_invalid_login_shows_error_message(self):
        response = self.client.post('/login/', {
            'email': 'naoexiste@example.com',
            'password': 'senhaerrada',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'E-mail ou senha incorretos')

    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=/dashboard/', response['Location'])
