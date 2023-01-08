from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.conf import settings

from ..models import Post, Group, User


class PostsView_html_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
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
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(response.context['group'], self.post.group)

    def test_view_profile_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', args=(self.user.username,)))
        self.assertEqual(response.context['author'], self.user)

    def test_view_post_detail_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.id,)))
        self.assertEqual(response.context['post'], self.post)

    def test_view_create_correct_context(self):
        """Шаблон post_create и post_edit сформирован с  контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        response1 = self.authorized_client_author.get(
            reverse('posts:post_edit', args=(self.post.id,)))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                form_field1 = response1.context.get('form').fields.get(value)
                self.assertIsInstance(form_field1, expected)

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
        cls.user = User.objects.create(username='fedorov')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
            id=1
        )
        cls.bilk_post: list = []
        for title in range(13):
            cls.bilk_post.append(Post(text=f'Тестовый текст {title}',
                                 group=cls.group,
                                 author=cls.user))
        Post.objects.bulk_create(cls.bilk_post)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(
            response.context['page_obj']), settings.POSTS_COUNT)

    def test_second_page_contains_three_records(self):
        X = 13-10
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), X)
