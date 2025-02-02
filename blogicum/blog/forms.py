from django import forms

from .models import Post, Comment, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {'pub_date': forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local',
                                            'class': 'form-control'})}

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['image'].widget.attrs.update({'class': 'form-control'})


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        text = forms.CharField(
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            label='Your comment'
        )


class UserEditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class':
                                                       'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
