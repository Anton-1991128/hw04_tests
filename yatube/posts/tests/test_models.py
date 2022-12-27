from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='Тестовый слаг',
                                          description='Тестовое описание',)
        self.post = Post.objects.create(author=self.user,
                                        text='Тестовое описание поста',)

    def test_models_have_correct_object_names_Post(self):
        '''Проверка длины __str__ post'''
        error_name = f"Вывод не имеет {15} символов"
        self.assertEqual(self.post.__str__(),
                         self.post.text[:15],
                         error_name)

    def test_models_have_correct_object_names_Post(self):
        '''Проверка титл у групп'''
        self.assertEqual(self.group.__str__(),
                         self.group.title)
