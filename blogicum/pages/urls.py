from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.PageAbout.as_view(), name='about'),
    path('rules/', views.PageRules.as_view(), name='rules'),
]
