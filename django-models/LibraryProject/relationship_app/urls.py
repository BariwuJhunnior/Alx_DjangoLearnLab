from django.urls import path
from .views import list_books
from . import views

app_name = 'relationship_app'

urlpatterns = [
    # Root listing (optional)
    path('', views.list_books, name='list_books'),

    # Function-based view for listing all books
    path('books/', views.list_books, name='book-list'),
    
    # Class-based view for library details (expects primary key)
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library-detail'),
]