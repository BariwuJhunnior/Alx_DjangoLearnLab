from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from .models import Book
from .forms import BookForm


def book_list(request):
    """List books. Uses ORM safely (no raw SQL)."""
    books = Book.objects.select_related('author', 'library').all()
    return render(request, 'relationship_app/book_list.html', {'books': books})


@login_required
@permission_required('relationship_app.can_create', raise_exception=True)
def book_create(request):
    """Create a Book using a ModelForm to validate input and avoid injection."""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('relationship_app:book_list'))
    else:
        form = BookForm()
    return render(request, 'relationship_app/book_form.html', {'form': form})


@login_required
@permission_required('relationship_app.can_edit', raise_exception=True)
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect(reverse('relationship_app:book_list'))
    else:
        form = BookForm(instance=book)
    return render(request, 'relationship_app/book_form.html', {'form': form, 'book': book})


@login_required
@permission_required('relationship_app.can_delete', raise_exception=True)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect(reverse('relationship_app:book_list'))
    return render(request, 'relationship_app/book_confirm_delete.html', {'book': book})
