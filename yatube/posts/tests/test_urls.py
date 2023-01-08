from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
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
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author.force_login(self.user)

    def test_unauthorized_user_urls_status_code(self):
        """Проверка status_code для неавторизованного пользователя."""
        field_urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): HTTPStatus.OK,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse('posts:post_create'): HTTPStatus.FOUND,
        }
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_client_urls_status_code(self):
        """status_code для авторизованного пользователя и автора поста."""
        field_urls_code = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): HTTPStatus.OK,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
        }
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.authorized_client.get(url).status_code
                self.assertEqual(status_code, response_code)
        for url, response_code in field_urls_code.items():
            with self.subTest(url=url):
                status_code = self.authorized_client_author.get(
                    url).status_code
                self.assertEqual(status_code, response_code)

    def test_Post_404_exists_at_desired_location(self):
        """Страница /404/ не существует."""
        response = self.authorized_client.get('/list/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)
