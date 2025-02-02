import datetime

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView, View
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch


from blog.models import Post, Category, Comment
from .forms import PostForm, UserEditProfileForm, CategoryForm, CommentForm


User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    """post = self.get_object() return self.request.user == post.author"""

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:index')


# Post-related views
class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.datetime.now()
        ).select_related('author', 'category', 'location').annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True
        ).select_related('author', 'category', 'location').prefetch_related(
            Prefetch('comments',
                     queryset=Comment.objects.order_by('created_at')))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.kwargs['pk'])


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostEditView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return super().get_queryset()

    def dispatch(self, request, *args, **kwargs):
        request.session['return_to'] = request.META.get('HTTP_REFERER')
        return super().dispatch(request, *args, **kwargs)


# Comment-related views
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.datetime.now()
        ).select_related('author', 'category', 'location')

    def form_valid(self, form):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.datetime.now()
        )
        form.instance.author = self.request.user
        form.instance.post = post
        form.save()

        messages.success(self.request, "Ваш комментарий успешно добавлен.")
        return redirect(post.get_absolute_url())

    def get_success_url(self):
        return self.object.post.get_absolute_url()


class EditCommentView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment.objects.select_related('post'),
            pk=self.kwargs['comment_id'],
            post__is_published=True,
            post__category__is_published=True,
            post__pub_date__lte=datetime.datetime.now()
        )

    def get_success_url(self):
        return self.object.post.get_absolute_url()


class DeleteCommentView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment.objects.select_related('post'),
            pk=self.kwargs['comment_id'],
            post__is_published=True,
            post__category__is_published=True,
            post__pub_date__lte=datetime.datetime.now()
        )

    def get_success_url(self):
        return self.object.post.get_absolute_url()

    def post(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        comment.delete()
        messages.success(request, 'Комментарий удалён!')
        return redirect('blog:post_detail', pk=post_id)


# Profile-related viwes
class UserEditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditProfileForm
    template_name = 'blog/user.html'
    context_object_name = 'profile'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username':
                                               self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user


class ProfilePostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    ordering = '-pub_date'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(author=user).order_by('-pub_date').annotate(
            comment_count=Count('comments')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


# Category-related views
class CategoryPostsView(ListView):
    model = Post
    form_class = CategoryForm
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return Post.objects.filter(
            category=self.category,
            is_published=True,
            pub_date__lte=datetime.datetime.now()
        ).select_related('author', 'location'
                         ).annotate(comment_count=Count('comments')
                                    ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
