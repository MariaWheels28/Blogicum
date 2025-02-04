from http import HTTPStatus

from django.views.generic import TemplateView
from django.shortcuts import render


class PageAbout(TemplateView):
    template_name = 'pages/about.html'


class PageRules(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=HTTPStatus.NOT_FOUND)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=HTTPStatus.FORBIDDEN)


def server_error(request):
    return render(
        request, 'pages/500.html', status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
