from django.http import HttpResponse
from django.shortcuts import render


def about(request) -> HttpResponse:
    """Возвращает страницу с описанием проекта."""
    template: str = 'pages/about.html'
    return render(request, template)


def rules(request) -> HttpResponse:
    """Возвращает страницу с правилами."""
    template: str = 'pages/rules.html'
    return render(request, template)


def csrf_failure(request, reason='') -> HttpResponse:
    """Рендер страницы для 403 ошибки."""
    template: str = 'pages/403csrf.html'
    return render(request, template, status=403)


def page_not_found(request, exception) -> HttpResponse:
    """Рендер страницы для 404 ошибки."""
    template: str = 'pages/404.html'
    return render(request, template, status=404)


def server_error(request) -> HttpResponse:
    """Рендер страницы для 500 ошибки."""
    template: str = 'pages/500.html'
    return render(request, template, status=500)
