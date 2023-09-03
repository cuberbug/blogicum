from typing import Any, Dict

from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import Http404
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import PostForm, CommentForm
from .models import Category, Comment, Post, User


PAGINATE_COUNT: int = 10


def get_general_posts_filter() -> QuerySet[Any]:
    """Фильтр постов для пользователя."""
    return Post.objects.select_related(
        'author',
        'location',
        'category',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class EditContentMixin(LoginRequiredMixin):
    """
    Добавляет проверку авторства для редактирования и удаления.
    Если проверка провалена, то возвращает на страницу поста.
    """

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)


class RedirectionPostMixin:
    """После выполнения перенаправит на страницу поста."""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class RedirectionProfileMixin:
    """После выполнения перенаправит на страницу профиля."""

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostMixin:
    """Базовый миксин для постов."""
    model = Post


class PostFormMixin(PostMixin):
    """Миксин для постов с формой."""
    form_class = PostForm


class PostListMixin(PostMixin):
    """Миксин для страниц со списком постов и пагинацией."""
    paginate_by = PAGINATE_COUNT


class PostListView(PostListMixin, ListView):
    """CBV главной страницы. Выводит список постов."""
    template_name = 'blog/index.html'

    def get_queryset(self) -> QuerySet[Any]:
        return get_general_posts_filter()


class PostDetailView(PostMixin, DetailView):
    """CBV подробная страница поста с комментариями к нему."""
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        """
        Условия фильтрации, если пользователь не является автором поста:
        - пост разрешён к публикации;
        - категория разрешена к публикации;
        - текущее время больше времени публикации.
        """
        if self.get_object().author != self.request.user and (
            self.get_object().is_published is False or
            self.get_object().category.is_published is False or
            self.get_object().pub_date > timezone.now()
        ):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
        return context


class CategoryListView(PostListMixin, ListView):
    """CBV страница категории. Выводит список постов."""
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        return get_general_posts_filter().filter(
            category__slug=self.kwargs['category_slug'],
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'],
        )
        return context


class PostCreateView(
    LoginRequiredMixin,
    PostFormMixin,
    RedirectionProfileMixin,
    CreateView,
):
    """CBV страница создания поста."""
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(
    EditContentMixin,
    PostFormMixin,
    RedirectionPostMixin,
    UpdateView,
):
    """CBV страница редактирования поста."""
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(
    EditContentMixin,
    PostMixin,
    RedirectionProfileMixin,
    DeleteView,
):
    """CBV страница удаления поста."""
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class ProfilePostListView(PostListMixin, ListView):
    """CBV страницы пользователя."""
    template_name = 'blog/profile.html'

    def get_queryset(self) -> QuerySet[Any]:
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return Post.objects.select_related(
            'author',
            'location',
            'category',
        ).filter(
            author=self.author
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class EditProfileUpdateView(
    LoginRequiredMixin,
    RedirectionProfileMixin,
    UpdateView,
):
    """CBV страница редактирования профиля."""
    model = User
    template_name = 'blog/user.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    def get_object(self, queryset=None):
        return self.request.user


class CommentMixin(RedirectionPostMixin):
    """Миксин для комментариев."""
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentFormMixin(CommentMixin):
    """Миксин для комментариев с формой."""
    form_class = CommentForm


class CommentCreateView(LoginRequiredMixin, CommentFormMixin, CreateView):
    """CBV создания комментария"""

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            get_general_posts_filter(),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CommentUpdateView(EditContentMixin, CommentFormMixin, UpdateView):
    """CBV страница редактирования комментария."""
    pass


class CommentDeleteView(EditContentMixin, CommentMixin, DeleteView):
    """CBV страница удаления комментария."""
    pass
