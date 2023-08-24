from http.client import HTTPResponse

from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Category, Post


def post_filter(self):
    """Фильтр для постов: время и флаги публикации"""
    return self.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


def index(request) -> HTTPResponse:
    """
    Рендер главной страницы.
    Вывод постов отсортирован по дате от новых к старым.
    Фильтрация по флагам, дате и количеству.
    """
    POSTS_COUNT: int = 5
    template: str = 'blog/index.html'
    post_list = post_filter(
        Post.objects.select_related(
            'category',
        )
    )[:POSTS_COUNT]

    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request, id: int) -> HTTPResponse:
    """
    Принимает id в качестве порядкового номера записи поста.
    Возвращает подробную страницу если по номеру поста есть запись.
    Фильтрация по флагам и времени.
    """
    template: str = 'blog/detail.html'
    post = get_object_or_404(
        post_filter(Post.objects),
        pk=id
    )

    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug: str) -> HTTPResponse:
    """
    Рендер страницы категории.
    Вывод постов отсортирован по дате от новых к старым.
    Фильтрация по флагу, времени и принятой категории.
    """
    template: str = 'blog/category.html'
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug,
    )
    post_list = post_filter(category.posts)

    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, template, context)
