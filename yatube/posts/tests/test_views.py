from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..forms import PostForm
from ..models import Post, Group, User

TEST_OF_POST: int = 13


class PostsView_html_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.user2 = User.objects.create(username='tom')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.group2 = Group.objects.create(
            title='Тестовый2 ',
            description='Тестовый2 ',
            slug='test-slug2',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

    def context_post_or_page_obj(self, response, bool=False):
        """Проверка содержимого контекста поста."""
        if bool:
            post = response.context['post']
        else:
            post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post, self.post)

    def test_post_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        return self.context_post_or_page_obj(response)

    def test_group__show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(response.context['group'], self.post.group)
        return self.context_post_or_page_obj(response)

    def test_view_profile_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', args=(self.user.username,)))
        self.assertEqual(response.context['author'], self.user)
        return self.context_post_or_page_obj(response)

    def test_view_post_detail_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.id,)))
        return self.context_post_or_page_obj(response, bool=True)

    def test_view_create_correct_context(self):
        """Шаблон post_create и post_edit сформирован с  контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        name_args = (
            ('posts:post_create', None,),
            ('posts:post_edit', (self.post.id,)),
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(
                    reverse('posts:post_create'))
                response1 = self.authorized_client_author.get(
                    reverse('posts:post_edit', args=(self.post.id,)))
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                form_field1 = response1.context.get('form').fields.get(value)
                self.assertIsInstance(form_field1, expected)
        for name, args in name_args:
            with self.subTest(name=name):
                response2 = self.authorized_client_author.get(
                    reverse(name, args=args))
                self.assertIsInstance(response2.context['form'], PostForm)
                self.assertIn('form', response.context)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        response = self.authorized_client_author.get(reverse(
            'posts:group_list', args={self.group2.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)
        post = Post.objects.first()
        self.assertEqual(post.group, self.post.group)
        response_group = self.authorized_client_author.get(reverse(
            'posts:group_list', args={self.group.slug}))
        group_post = response_group.context['group']
        post2 = group_post.posts.first()
        self.assertEqual(post, post2)


class PostsPAGINATOR_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='fedorov')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.bilk_post: list = []
        for title in range(TEST_OF_POST):
            cls.bilk_post.append(Post(text=f'Тестовый текст {title}',
                                      group=cls.group,
                                      author=cls.user))
        Post.objects.bulk_create(cls.bilk_post)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_contains_ten_records_three_records(self):
        templates_url_names = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user,)),
        )
        pages = (
            ('?page=1', 10),
            ('?page=2', 3),
        )
        for name, args in templates_url_names:
            for page, total in pages:
                with self.subTest(page=page):
                    response = self.authorized_client.get(reverse(
                        name, args=args) + page)
                    self.assertEqual(len(response.context['page_obj']), total)
