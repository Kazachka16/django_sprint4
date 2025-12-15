from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import StaticPage


def csrf_failure(request, reason=''):
    """Обработчик ошибки CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


def permission_denied(request, exception):
    """Обработчик ошибки 403 (доступ запрещен)."""
    return render(request, 'pages/403.html', status=403)


def page_not_found(request, exception):
    """Обработчик ошибки 404 (страница не найдена)."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Обработчик ошибки 500 (ошибка сервера)."""
    return render(request, 'pages/500.html', status=500)


class StaticPageListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Список всех статичных страниц (только для админов)."""
    model = StaticPage
    template_name = 'pages/staticpage_list.html'
    permission_required = 'pages.view_staticpage'
    context_object_name = 'pages'


class StaticPageDetailView(DetailView):
    """Детальное отображение статичной страницы."""
    model = StaticPage
    template_name = 'pages/staticpage_detail.html'
    context_object_name = 'page'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Для неавторизованных пользователей показываем только опубликованные
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True)
        return queryset


class StaticPageCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView
):
    """Создание новой статичной страницы."""
    model = StaticPage
    fields = ['title', 'slug', 'content', 'is_published']
    template_name = 'pages/staticpage_form.html'
    permission_required = 'pages.add_staticpage'
    success_url = reverse_lazy('pages:page_list')


class StaticPageUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView
):
    """Редактирование статичной страницы."""
    model = StaticPage
    fields = ['title', 'slug', 'content', 'is_published']
    template_name = 'pages/staticpage_form.html'
    permission_required = 'pages.change_staticpage'

    def get_success_url(self):
        return reverse_lazy(
            'pages:page_detail',
            kwargs={'slug': self.object.slug}
        )


class StaticPageDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView
):
    """Удаление статичной страницы."""
    model = StaticPage
    template_name = 'pages/staticpage_confirm_delete.html'
    permission_required = 'pages.delete_staticpage'
    success_url = reverse_lazy('pages:page_list')
