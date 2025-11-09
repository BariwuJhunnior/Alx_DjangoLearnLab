from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_books, name='list_books')
]

from django.urls import path
from . import views

app_name = 'relationship_app'

urlpatterns = [
    # Function-based view for listing all books
    path('books/', views.list_books, name='book-list'),
    
    # Class-based view for library details
    path('library/', views.list_books, name='list_books'),
]