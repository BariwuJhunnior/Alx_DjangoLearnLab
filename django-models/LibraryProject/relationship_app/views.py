
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from .models import Book
from .models import Library
from django.contrib.auth import login


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
    context['books'] = library.objects.all().select_related('author')
    return context


def register(request):
  """Simple user registration view using Django's UserCreationForm."""
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      username = form.cleaned_data.get('username')
      raw_password = form.cleaned_data.get('password1')
      user = authenticate(username=username, password=raw_password)
      if user is not None:
        login(request, user)
        return redirect('relationship_app:book-list')
  else:
    form = UserCreationForm()
  return render(request, 'relationship_app/register.html', {'form': form})
