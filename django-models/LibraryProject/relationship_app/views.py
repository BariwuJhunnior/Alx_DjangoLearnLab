from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from .models import Book
from .models import Library



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
    # Use select_related on the books' authors for efficiency
    context['books'] = library.books.all().select_related('author')
    return context
