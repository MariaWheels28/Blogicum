import datetime
from typing import Optional, Type

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q, QuerySet
from django.conf import settings
from django.utils import timezone


from blog.models import Post, Category, Comment
from .forms import PostForm, UserEditProfileForm, CategoryForm, CommentForm


User = get_user_model()

PAGINATE_BY = settings.PAGINATE_BY
NOW = timezone.now()


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для проверки, является ли данный пользователь автором объекта."""

    def test_func(self) -> bool:
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self) -> HttpResponseRedirect:
        post_id: Optional[int] = self.kwargs.get('post_id')
        if post_id:
            return redirect(reverse('blog:post_detail',
                                    kwargs={'post_id': post_id}))
        return redirect('blog:index')


def get_post_queryset(self) -> QuerySet[Post]:
    """Возвращает отфильтрованный набор постов."""
    return Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=NOW
    ).order_by('-pub_date')


def get_comment_object(self) -> Comment:
    """Возвращает отфильтрованный об сообщения."""
    return get_object_or_404(
        Comment.objects.select_related('post'),
        id=self.kwargs['comment_id'],
        post__is_published=True,
        post__category__is_published=True,
        post__pub_date__lte=NOW
    )


def annotate_count_comments(queryset) -> QuerySet:
    """Возвращает отфильтрованныe об сообщения."""
    return queryset.annotate(comment_count=Count('comments'))


# Post-related views
class PostListView(ListView):
    """View списка постов, доступных для просмотра."""

    model: Type[Post] = Post
    template_name: str = 'blog/index.html'
    paginate_by: int = PAGINATE_BY

    def get_queryset(self) -> QuerySet[Post]:
        return annotate_count_comments(get_post_queryset(self).select_related(
            'author', 'category', 'location'))


class PostDetailView(DetailView):
    """View детального отображения поста."""

    model: Type[Post] = Post
    template_name: str = 'blog/detail.html'

    def get_queryset(self) -> QuerySet[Post]:
        queryset = Post.objects.select_related('author', 'category',
                                               'location').prefetch_related(
            Prefetch('comments',
                     queryset=Comment.objects.order_by('created_at'))
        )
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_published=True) | Q(author=self.request.user)
            )
        return queryset.filter(is_published=True, category__is_published=True)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self, queryset: Optional[QuerySet[Post]] = None) -> Post:
        queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.kwargs['post_id'])


class PostCreateView(LoginRequiredMixin, CreateView):
    """View создания нового поста."""

    model: Type[Post] = Post
    template_name: str = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form) -> HttpResponseRedirect:
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        username: str = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostEditView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """View редактирования существующего поста."""

    model: Type[Post] = Post
    form_class = PostForm
    template_name: str = 'blog/create.html'
    pk_url_kwarg: str = 'post_id'

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """View удаления поста."""

    model: Type[Post] = Post
    success_url: str = reverse_lazy('blog:index')
    template_name: str = 'blog/create.html'
    pk_url_kwarg: str = 'post_id'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        form = PostForm(instance=post)
        context['form'] = form
        return context


# Comment-related views
class CommentCreateView(LoginRequiredMixin, CreateView):
    """View добавления комментария к посту."""

    model: Type[Comment] = Comment
    form_class = CommentForm
    template_name: str = 'blog/comment.html'

    def get_queryset(self) -> QuerySet[Post]:
        return annotate_count_comments(get_post_queryset(self).select_related(
            'author', 'category', 'location'))

    def form_valid(self, form) -> HttpResponseRedirect:
        post = get_object_or_404(get_post_queryset(self),
                                 id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        form.save()

        return redirect(post.get_absolute_url())

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


class EditCommentView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """View редактирования комментария."""

    model: Type[Comment] = Comment
    form_class = CommentForm
    template_name: str = 'blog/comment.html'

    def get_object(self, queryset=None) -> Comment:
        return get_comment_object(self)

    def get_success_url(self) -> str:
        return self.object.post.get_absolute_url()


class DeleteCommentView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """View удаления комментария."""

    model: Type[Comment] = Comment
    template_name: str = 'blog/comment.html'

    def get_object(self, queryset=None) -> Comment:
        return get_comment_object(self)

    def get_success_url(self) -> str:
        return self.object.post.get_absolute_url()


# Profile-related viws
class UserEditProfileView(LoginRequiredMixin, UpdateView):
    """View редактирования профиля пользователя."""

    model = User
    form_class = UserEditProfileForm
    template_name: str = 'blog/user.html'
    context_object_name: str = 'profile'

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={'username':
                                               self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user


class ProfilePostsView(ListView):
    """View отображения постов конкретного пользователя."""

    model: Type[Post] = Post
    template_name: str = 'blog/profile.html'
    ordering: str = '-pub_date'
    paginate_by: int = PAGINATE_BY

    def get_queryset(self) -> QuerySet[Post]:
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return annotate_count_comments(
            Post.objects.filter(author=user).order_by('-pub_date')
        )

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


# Category-related views
class CategoryPostsView(ListView):
    """View отображения постов конкретной категории."""

    model: Type[Post] = Post
    form_class = CategoryForm
    template_name: str = 'blog/category.html'
    paginate_by: int = PAGINATE_BY

    def get_queryset(self) -> QuerySet[Post]:
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return annotate_count_comments(get_post_queryset(self).filter(
            category=self.category).select_related(
                'author', 'location'))

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
