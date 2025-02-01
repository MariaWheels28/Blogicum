from django.urls import path, reverse_lazy

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(template_name='blog/index.html'), name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/create', views.PostCreateView.as_view(template_name='blog/create.html'), name='create_post'),
    path('profile/edit/', views.UserEditProfileView.as_view(), name='edit_profile'),
    path('profile/<slug:username>/', views.ProfileListView.as_view(template_name='blog/profile.html'), name='profile'),
    # path('posts/<int:pk>/edit/', views.PostEditView.as_view(), name='edit_post'),
    # path('posts/<int:pk>/delete/', views.PostDelete.as_view(), name='delete_post'),
    # path('posts/<int:post_id>/comment'), views.AddCommentView.as_view(), name='add_comment'),
    # path('posts/<int:post_id>/edit_comment'), views.EditCommentView.as_view(), name='edit_comment'),
    # path('posts/<int:post_id>/delete_comment'), views.DeleteCommentView.as_view(), name='delete_comment'),
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
]
