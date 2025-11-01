from bookshelf.models import Book

#Retrieve the book object with the current title #'1984'

book = Book.objects.get(title='1984')

book.title = 'Nineteen Eighty-Four'

book.save(update_field=['title'])

print("Book title updated successfully to 'Nineteen Eighty-Four'. ")
