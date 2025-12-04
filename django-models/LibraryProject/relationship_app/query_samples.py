from .models import Author, Book, Library, Librarian

def get_books_by_author(author_name):
    """
    Query all books by a specific author using ForeignKey relationship
    """
    # Method 1: Get the author first, then filter books
    author = Author.objects.get(name=author_name)
    books = Book.objects.filter(author=author)
    return books

    # Method 2: Using direct filter with author_id
    # books = Book.objects.filter(author_id=author_id)
    # return books

def get_library_books(library_id):
    """
    List all books in a library
    Note: Since there's no direct relationship between Library and Book in the models,
    this is just a placeholder. You would need to add a relationship or 
    implement intermediary logic to track books in a library.
    """
    library = Library.objects.get(id=library_id)
    # In a real application, you would need to add a relationship between Library and Book
    books = library.books.all()

    return []

def get_library_librarian(library):
    """
    Retrieve the librarian for a library using OneToOne relationship
    """
    # Method 1: From Library to Librarian
    library = Librarian.objects.get(library='')

    try:
        librarian = library.name
        return librarian
    except Librarian.DoesNotExist:
        return None

    # Method 2: Direct query on Librarian
    # librarian = Librarian.objects.get(library_id=library_id)
    # return librarian

def get_library_by_name(library_name):
    """
    Retrieve a library by its name
    """
    try:
        library = Library.objects.get(name=library_name)
        return library
    except Library.DoesNotExist:
        return None
