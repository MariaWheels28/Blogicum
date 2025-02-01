import datetime

from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import get_user_model


from blog.models import Post, Category
from .forms import PostForm, UserEditProfileForm, CategoryForm


User = get_user_model()


MAX_POSTS = 5


def filter_posts(queryset):
    return queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.datetime.now(),
    )


def get_posts_queryset():
    return Post.objects.select_related('author', 'location', 'category')


class PostListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10


# def index(request):
#     posts_queryset = get_posts_queryset()
#     post_list = filter_posts(posts_queryset)[:MAX_POSTS]
#     context = {'post_list': post_list}
#     return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post_queryset = Post.objects.select_related('location')
    post = get_object_or_404(filter_posts(post_queryset), pk=post_id)
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


# def category_posts(request, category_slug):
#     category = get_object_or_404(
#         Category,
#         slug=category_slug,
#         is_published=True,
#     )
#     posts_queryset = get_posts_queryset()
#     post_list = filter_posts(posts_queryset).filter(category=category)
#     context = {'category': category, 'post_list': post_list}
#     return render(request, 'blog/category.html', context)


class CategoryPostsView(ListView):
    model = Post
    form_class = CategoryForm
    template_name = 'blog/category.html'
    paginate_by = 10
    context_object_name = 'page_obj'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        return Post.objects.filter(category=self.category, is_published=True).select_related('author', 'location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class ProfileListView(LoginRequiredMixin, ListView):
    model = User
    ordering = '-pub_date'
    paginate_by = 10
    context_object_name = 'profile'

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(author=user).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
        return context


class UserEditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditProfileForm
    template_name = 'blog/user.html'
    context_object_name = 'profile'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user
