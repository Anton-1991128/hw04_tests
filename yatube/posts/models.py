from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField('заголовок', max_length=200)
    slug = models.SlugField('группы', max_length=100, unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы "

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        verbose_name='автор поста'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа постов',
        related_name='posts'
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "пост"
        verbose_name_plural = "посты"

    def __str__(self):
        return self.text[:15]
