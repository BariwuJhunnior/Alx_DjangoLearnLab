from bookshelf.models import Book

deleted_count, details = Book.objects.filter(title='Nineteen Eighty-Four').delete()

print(f"Deleted {deleted_count} objects.")
print(f"Deletion details: {details})
