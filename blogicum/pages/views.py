from http.client import HTTPResponse
from typing import Any
from django.shortcuts import render


def about(request: Any) -> HTTPResponse:
    """Возвращает страницу с описанием проекта."""
    template: str = 'pages/about.html'
    return render(request, template)


def rules(request: Any) -> HTTPResponse:
    """Возвращает страницу с правилами."""
    template: str = 'pages/rules.html'
    return render(request, template)
