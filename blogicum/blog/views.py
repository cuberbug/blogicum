from typing import Any, Dict
from django.db import models
from django.db.models import Count
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import PostForm, CommentForm
from .models import Category, Comment, Post, User


def get_filtered_posts():
    """Фильтр для постов: время и флаги публикации."""
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


class PostListView(ListView):
    """CBV главной страницы. Выводит список постов."""
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return get_filtered_posts()


class PostDetailView(DetailView):
    """CBV подробная страница поста с комментариями к нему."""
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    # def get_object(self, queryset=None):
    #     return get_object_or_404(
    #         Post,
    #         pub_date__lte=timezone.now(),
    #         is_published=True,
    #         category__is_published=True,
    #         pk=self.kwargs['post_id'],
    #     )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
        return context


class CategoryListView(ListView):
    """CBV страница категории. Выводит список постов."""
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return get_filtered_posts().filter(
            category__slug=self.kwargs['category_slug'],
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'],
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV страница создания поста."""
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """CBV страница редактирования поста."""
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """CBV страница удаления поста."""
    template_name = 'blog/create.html'
    model = Post
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': username}
        )

    # def dispatch(self, request, *args, **kwargs):
    #     if self.get_object().author != request.user:
    #         return redirect('blog:post_detail', pk=self.kwargs['post_id'])
    #     return super().dispatch(request, *args, **kwargs)

    # def get_object(self, queryset=None):
    #     return get_object_or_404(
    #         Post.objects.select_related('author', 'location'),
    #         pub_date__lte=timezone.now(),
    #         is_published=True,
    #         category__is_published=True,
    #         pk=self.kwargs['post_id'],
    #     )


class ProfileListView(LoginRequiredMixin, ListView):
    """CBV страницы пользователя."""
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return get_filtered_posts().filter(author=self.author)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )
        context['profile'] = profile
        return context


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    """CBV страница редактирования профиля."""
    model = User
    template_name = 'blog/user.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    # def get_object(self, queryset=None):
    #     return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class CommentMixin(LoginRequiredMixin):
    """Миксин для комментариев."""
    model = Comment
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={
                'post_id': self.kwargs['post_id'],
            }
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentCreateView(CommentMixin, CreateView):
    """CBV создания комментария"""
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            get_filtered_posts(Post.objects),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': post_id}
        )


class CommentUpdateView(CommentMixin, UpdateView):
    """CBV страница редактирования комментария."""
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    # def dispatch(self, request, *args, **kwargs):
    #     get_object_or_404(
    #         Comment.objects.select_related('post'),
    #         post_id=self.kwargs['post_id'],
    #         id=self.kwargs['comment_id'],
    #         author=request.user,
    #     )
    #     return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(CommentMixin, DeleteView):
    """CBV страница удаления комментария."""
    template_name = 'blog/comment.html'
    # success_url = reverse_lazy('blog:index')

    # def dispatch(self, request, *args, **kwargs):
    #     get_object_or_404(
    #         Comment,
    #         id=kwargs['comment_id'],
    #         author=request.user,
    #     )
    #     return super().dispatch(request, *args, **kwargs)
