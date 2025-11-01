from bookshelf.models import Book

#Retrieve and display all attributes book
books = Book.objects.get(title='1984')
