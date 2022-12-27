from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta():
        model = Post
        fields = ('text', 'group')
        labels = {'text': 'Тут ваш текст',
                  'group': 'Выберите группу'}
