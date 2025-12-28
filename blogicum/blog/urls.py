from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from . import views
from .views_auth import RegistrationView

app_name = "blog"

urlpatterns = [
    # Основные URL блога
    path("", views.index, name="index"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path(
        "category/<slug:category_slug>/",
        views.category_posts,
        name="category_posts",
    ),
    # Профиль - ВАЖНО: сначала специфические URL, потом общие
    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),  # Этот должен быть ПЕРВЫМ
    path(
        "profile/<str:username>/",
        views.profile,
        name="profile",
    ),  # Этот должен быть ПОСЛЕ
    # Посты
    path(
        "posts/create/",
        views.PostCreateView.as_view(),
        name="create_post",
    ),
    path(
        "posts/<int:pk>/edit/",
        views.PostUpdateView.as_view(),
        name="edit_post",
    ),
    path(
        "posts/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
    # Комментарии
    path(
        "posts/<int:post_id>/comment/",
        views.add_comment,
        name="add_comment",
    ),
    path(
        "posts/<int:post_id>/edit_comment/<int:pk>/",
        views.CommentUpdateView.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:pk>/",
        views.delete_comment,  # ← Функция из views.py
        name="delete_comment",
    ),
    # Аутентификация
    path(
        "auth/registration/",
        RegistrationView.as_view(),
        name="registration",
    ),
    path(
        "auth/login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "auth/logout/",
        LogoutView.as_view(template_name="registration/logged_out.html"),
        name="logout",
    ),
    path(
        "auth/password_change/",
        PasswordChangeView.as_view(
            template_name="registration/password_change_form.html"
        ),
        name="password_change",
    ),
    path(
        "auth/password_change/done/",
        PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "auth/password_reset/",
        PasswordResetView.as_view(
            template_name="registration/password_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "auth/password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "auth/reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "auth/reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path('pages/about/', views.about, name='about'),
    path('pages/rules/', views.rules, name='rules'),
]

handler404 = "blog.views.page_not_found"
handler500 = "blog.views.server_error"
handler403 = "blog.views.permission_denied"
