import datetime

from django.shortcuts import render, get_object_or_404

from blog.models import Post, Category


MAX_POSTS = 5


def filter_posts(queryset):
    return queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.datetime.now(),
    )


def get_posts_queryset():
    return Post.objects.select_related('author', 'location', 'category')


def index(request):
    posts_queryset = get_posts_queryset()
    post_list = filter_posts(posts_queryset)[:MAX_POSTS]
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post_queryset = Post.objects.select_related('location')
    post = get_object_or_404(filter_posts(post_queryset), pk=post_id)
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    posts_queryset = get_posts_queryset()
    post_list = filter_posts(posts_queryset).filter(category=category)
    context = {'category': category, 'post_list': post_list}
    return render(request, 'blog/category.html', context)
