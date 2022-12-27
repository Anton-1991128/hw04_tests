from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import User

User = get_user_model()


class TaskURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test__password_change_url_exists_at_desired_location(self):
        """Страница /password_change/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, 200)

    def test_logout_url_tech_exists_at_desired_location(self):
        """Проверка доступности адреса '/auth/password_change/' авторизован'"""
        response = self.authorized_client.get('/auth/logout/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_exists_at_desired_location(self):
        """Проверка доступности адреса /auth/signup/."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)

    def test_about_author_url_tech_exists_at_desired_location(self):
        """Проверка доступности адреса '/auth/login/'"""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)

    def test_about_author_url_uses_correct_template(self):
        """Проверка шаблона для адреса '/users/signup'"""
        response = self.guest_client.get('/auth/signup/')
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_about_tech_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/tech/."""
        response = self.guest_client.get('/auth/login/')
        self.assertTemplateUsed(response, 'users/login.html')

    def test_password_change_url_uses_correct_template(self):
        """Проверка шаблона для адреса '/auth/password_change/'"""
        response = self.authorized_client.get('/auth/password_change/')
        self.assertTemplateUsed(response, 'users/password_change_form.html')

    def test_logout_url_uses_correct_template(self):
        """Проверка шаблона для адреса '/auth/logout/'"""
        response = self.authorized_client.get('/auth/logout/')
        self.assertTemplateUsed(response, 'users/logged_out.html')
