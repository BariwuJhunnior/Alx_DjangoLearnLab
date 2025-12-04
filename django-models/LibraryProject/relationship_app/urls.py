from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import list_books

app_name = 'relationship_app'

urlpatterns = [
    path('', views.list_books, name='list_books'),
    path('books/', views.list_books, name='book-list'),
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library-detail'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('accounts/register/', views.register, name='register'),
    # Role-based views
    path('role/admin/', views.admin_view, name='admin-view'),
    path('role/librarian/', views.librarian_view, name='librarian-view'),
    path('role/member/', views.member_view, name='member-view'),
    # Book management (permission protected)
    path('book/add_book/', views.add_book, name='add_book'),
    path('book/<int:pk>/edit_book/', views.edit_book, name='edit_book'),
    path('book/<int:pk>/delete/', views.delete_book, name='book-delete'),
]