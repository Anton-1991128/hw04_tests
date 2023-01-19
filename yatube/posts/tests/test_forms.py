from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class Postsform_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            description='Описание ',
            slug='test-slug2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_self_client_create_post(self):
        '''Проверка что гость не может создавать пост'''
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post(self):
        '''Проверка создания поста'''
        Post.objects.get(author=self.user).delete()
        posts_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), 0)
        form_data = {'text': 'Текст тестового поста',
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         )
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])

    def test_can_edit_post(self):
        '''Проверка что можно редактировать пост  '''
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group2.pk}
        post_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), 1)
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True)
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(Post.objects.count(), post_count)
        response_group = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        self.assertEqual(len(response_group.context['page_obj']), 0)
