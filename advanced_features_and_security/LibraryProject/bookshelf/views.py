

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from .models import Book
from django.urls import reverse


def book_list(request):
    """List available books (no special permission required to view list)."""
    books = Book.objects.select_related('author', 'library').all()
    return render(request, 'relationship_app/book_list.html', {'books': books})


@login_required
@permission_required('relationship_app.can_create', raise_exception=True)
def can_create(request):
    """Simple create view for Book protected by `can_create` permission.

    This is a minimal example — replace with a ModelForm in a real app.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        author_id = request.POST.get('author')
        library_id = request.POST.get('library')
        if title and author_id and library_id:
            Book.objects.create(title=title, author_id=author_id, library_id=library_id)
            return redirect(reverse('relationship_app:book_list'))
    return render(request, 'relationship_app/book_form.html')


@login_required
@permission_required('relationship_app.can_edit', raise_exception=True)
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            book.title = title
            book.save()
            return redirect(reverse('relationship_app:book_list'))
    return render(request, 'relationship_app/book_form.html', {'book': book})


@login_required
@permission_required('relationship_app.can_delete', raise_exception=True)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect(reverse('relationship_app:book_list'))
    return render(request, 'relationship_app/book_confirm_delete.html', {'book': book})

