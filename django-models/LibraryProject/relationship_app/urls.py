from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'relationship_app'

urlpatterns = [
    path('', views.list_books, name='list_books'),
    path('books/', views.list_books, name='book-list'),
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library-detail'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('accounts/register/', views.register, name='register'),
]