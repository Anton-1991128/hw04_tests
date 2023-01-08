from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class Postsform_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='nouname')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.user = User.objects.create(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_Post(self):
        """Проверка создания поста ."""
        Post_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст',
                     'group': self.group}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.group, form_data['group'])
        self.assertEqual(Post.objects.count(),
                         Post_count + 1,
                         )
        response1 = self.client.post(reverse('posts:post_create'),
                                     data=form_data,
                                     follow=False)
        self.assertEqual(response1.status_code, 302)

    def test_can_edit_post(self):
        '''Проверка что можно редактировать пост  '''
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        self.group2 = Group.objects.create(title='Тестовая группа2',
                                           slug='test-group',
                                           description='Описание')
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group2.id}
        Post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.post.author, self.user)
        self.assertNotEqual(self.post.text, form_data['text'])
        self.assertNotEqual(self.post.group, form_data['group'])
        self.assertEqual(Post.objects.count(), Post_count)
        response1 = self.authorized_client.get('/group/test-slug/')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.status_code, HTTPStatus.OK)

    def test_group_null(self):
        '''Проверяем  что группу можно не указывать'''
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        old_text = self.post
        form_data = {'text': 'Текст записанный в форму',
                     'group': ''}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name2 = 'Пользователь не может оставить поле нулевым'
        self.assertNotEqual(old_text.group, form_data['group'], error_name2)
