from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # Post-related URLs
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/create', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/', views.PostEditView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),

    # Comment-related URLs
    path('posts/<int:post_id>/comment',
         views.CommentCreateView.as_view(), name='add_comment'),  # add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<comment_id>/',
         views.EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<comment_id>/',
         views.DeleteCommentView.as_view(), name='delete_comment'),

    # Profile-related URLs
    path('profile/edit/', views.UserEditProfileView.as_view(),
         name='edit_profile'),
    path('profile/<slug:username>/', views.ProfilePostsView.as_view(),
         name='profile'),

    # Category-related URLs
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(),
         name='category_posts'),
]
