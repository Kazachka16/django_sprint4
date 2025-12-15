from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Существующие статические страницы
    path('about/', views.StaticPageDetailView.as_view(),
         {'slug': 'about'}, name='about'),
    path('rules/', views.StaticPageDetailView.as_view(),
         {'slug': 'rules'}, name='rules'),

    # CRUD для страниц
    path('', views.StaticPageListView.as_view(), name='page_list'),
    path('create/', views.StaticPageCreateView.as_view(), name='page_create'),
    path('<slug:slug>/', views.StaticPageDetailView.as_view(),
         name='page_detail'),
    path('<slug:slug>/edit/', views.StaticPageUpdateView.as_view(),
         name='page_edit'),
    path('<slug:slug>/delete/', views.StaticPageDeleteView.as_view(),
         name='page_delete'),
]
