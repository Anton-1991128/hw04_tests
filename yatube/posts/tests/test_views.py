from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Post, Group, User

User = get_user_model()


class PostsView_html_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostsView_html_Tests.user)

    def test_post_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_title_0 = first_object.text
        task_text_0 = first_object.author
        task_slug_0 = first_object.group
        self.assertEqual(task_title_0, self.post.text)
        self.assertEqual(task_text_0, self.post.author)
        self.assertEqual(task_slug_0, self.post.group)

    def test_group__show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.context['group'], self.post.group)

    def test_view_profile_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(response.context['author'], self.user)

    def test_view_post_detail_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertEqual(response.context['post'], self.post)

    def test_view_create_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_view_edite_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_view_correct_template(self):
        """вьюшка-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
            'posts/post_detail.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_author_correct_template_author(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse
            ('posts:post_edit', kwargs={'post_id': '1'}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')


class PostsPAGINATOR_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
            id=1
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            id=1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user)
        self.bilk_post: list = []
        for i in range(12):
            self.bilk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(self.bilk_post)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
