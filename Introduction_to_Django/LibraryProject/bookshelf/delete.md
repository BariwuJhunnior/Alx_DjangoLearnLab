from bookshelf.models import Book

book = Book.objects.filter(title='Nineteen Eighty-Four')
book.delete()

print(f"Deleted {deleted_count} objects.")
print(f"Deletion details: {details})
