from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from django.http import Http404
from django.utils import timezone
from .forms import EditProfileForm

from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category, Comment

User = get_user_model()


def index(request):
    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('location', 'category', 'author')
        .prefetch_related('comments__author'),
        pk=post_id
    )

    # Проверяем, может ли пользователь видеть пост
    if not (post.is_published and 
            post.pub_date <= timezone.now() and 
            post.category.is_published):
        if request.user != post.author:
            raise Http404("Пост не найден")

    form = CommentForm()

    comments = post.comments.all()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    try:
        post_list = category.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),  # Проверка на отложенные посты
            category__is_published=True
        )
    except AttributeError:
        post_list = category.post_set.filter(
            is_published=True,
            pub_date__lte=timezone.now(),  # Проверка на отложенные посты
            category__is_published=True
        )

    # Дальнейшая обработка post_list
    post_list = post_list.select_related(
        'location', 'author'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Для автора показываем все посты
    if request.user == profile_user:
        post_list = Post.objects.filter(
            author=profile_user
        )
    # Для других пользователей - только опубликованные с правильными фильтрами
    else:
        post_list = Post.objects.filter(
            author=profile_user,
            is_published=True,
            pub_date__lte=timezone.now(),  # Важно: фильтр отложенных постов
            category__is_published=True    # Важно: фильтр по опубликованным категориям
        )

    # Общая обработка для обоих случаев
    post_list = post_list.select_related(
        'category', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile_user,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.pk})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id=pk)

    post.delete()

    return redirect('blog:index')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # Проверяем, может ли пользователь видеть пост
    if not (post.is_published and 
            post.pub_date <= timezone.now() and 
            post.category.is_published):
        if request.user != post.author:
            raise Http404("Пост не найден")

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        # ВАЖНО: Должен быть redirect, не render!
        return redirect('blog:post_detail', post_id=post_id)

    # Если форма не валидна, тоже redirect
    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    context_object_name = 'comment'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_delete'] = False
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


@login_required
def delete_comment(request, post_id, pk):
    """Функция для удаления комментария."""
    comment = get_object_or_404(Comment, pk=pk)

    # Проверяем, что пользователь является автором комментария
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    # Для GET запроса показываем страницу подтверждения
    context = {
        'comment': comment,
        'confirm_delete': True,
    }
    return render(request, 'blog/comment.html', context)


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


@login_required
def edit_profile(request):
    """Функция для редактирования профиля"""
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'blog/edit_profile.html', {'form': form})


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'pages/403csrf.html', status=403)


def about(request):
    return render(request, 'pages/about.html')


def rules(request):
    return render(request, 'pages/rules.html')
