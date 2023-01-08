from django.test import TestCase

from ..models import Group, Post, User


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

    def test_text_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        # Получаем из свойста класса Task значение verbose_name для title
        verbose = Post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст поста')

    def test_models_have_correct_object_names_Group(self):
        '''Проверка титл у групп'''
        self.assertEqual(self.group.__str__(),
                         self.group.title)

    def test_Group_title_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        # Получаем из свойста класса Group значение verbose_name для title
        verbose = Group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'заголовок')
