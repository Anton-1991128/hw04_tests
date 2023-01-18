from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.user2 = User.objects.create(username='tom')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)
        self.templates_urls = (
            ('posts:index', None, '/'),
            ('posts:group_list', (
                self.group.slug,), f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user,), f'/profile/{self.user}/'),
            ('posts:post_detail', (self.post.pk,), f'/posts/{self.post.pk}/'),
            ('posts:post_create', None, '/create/'),
            ('posts:post_edit', (
                self.post.id,), f'/posts/{self.post.pk}/edit/'),
        )

    def test_authour_user_urls(self):
        """Проверка доступности  для автора ."""
        for name, args, url in self.templates_urls:
            with self.subTest(url=url):
                response = self.authorized_client_author.get(reverse(
                    name, args=args))
                self.assertEqual(response.status_code, 200)

    def test_authorized_user_urls(self):
        """Проверка доступности  для авторизованного пользователя ."""
        url1 = f'/posts/{self.post.id}/'
        for name, args, url in self.templates_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(reverse(
                    name, args=args))
            if name == 'posts:post_edit':
                self.assertRedirects(response, url1)
            else:
                self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_urls(self):
        """Проверка доступности  для неавторизованного пользователя ."""
        url1 = f'/auth/login/?next=/posts/{self.post.id}/edit/'
        url2 = '/auth/login/?next=/create/'
        for name, args, url in self.templates_urls:
            with self.subTest(url=url):
                response = self.client.get(reverse(
                    name, args=args))
            if name == ('posts:post_create'):
                self.assertRedirects(response, url2)
            elif name == 'posts:post_edit':
                self.assertRedirects(response, url1)
            else:
                self.assertEqual(response.status_code, 200)

    def test_template(self):
        """Проверка шаблонов."""
        templates_url_names = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (self.user,), 'posts/profile.html'),
            ('posts:post_detail', (self.post.pk,), 'posts/post_detail.html'),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
        )
        for name, args, template in templates_url_names:
            with self.subTest(name=name):
                response = self.authorized_client_author.get(
                    reverse(name, args=args))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)

    def test_urls(self):
        """Тест реверс."""
        templates_url_names = (
            ('posts:index', None, '/'),
            ('posts:group_list', (
                self.group.slug,), f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user,), f'/profile/{self.user}/'),
            ('posts:post_detail', (self.post.pk,), f'/posts/{self.post.pk}/'),
            ('posts:post_edit', (
                self.post.id,), f'/posts/{self.post.pk}/edit/'),
            ('posts:post_create', None, '/create/'),
        )
        for name, args, url in templates_url_names:
            with self.subTest(url=url):
                self.assertEqual(reverse(name, args=args), url)

    def test_post_404_exists_at_desired_location(self):
        """Страница /404/ не существует."""
        response = self.client.get('/list/')
        self.assertEqual(response.status_code, 404)
