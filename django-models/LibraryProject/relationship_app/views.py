from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView
from .models import Book, Library

# Create your views here.
""" def list_books(request):
  books = Book.objects.all()

  books_list = []
  for book in books:
    book_info = f"Title: {book.title} - Author: {book.author.name}"

    books_list.append(book_info)

  response_text = "\n".join(books_list)

  if not books_list:
    response_text = "No books found in the database!"

  return HttpResponse(response_text, content_type='text/plain')

class LibraryDetailedView(DetailView):
    
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add books to context - use self.get_object() instead of self.object
        library = self.get_object()  # type: ignore[union-attr]
        context['books'] = library.books.all()  # type: ignore[union-attr]
        return context
    
 """


from django.shortcuts import render
from django.views.generic import DetailView, ListView
from .models import Book, Library

def list_books(request):
    """
    A function-based view that lists all books and their authors
    """
    books = Book.objects.all().select_related('author')
    context = {
        'books': books,
        'title': 'All Books'
    }
    return render(request, 'relationship_app/list_books.html', context)

class LibraryDetailView(DetailView):
    """
    A class-based view that displays details for a specific library
    including all books available in that library
    """
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library = self.get_object()
        context['books'] = library.books.all()
        return context