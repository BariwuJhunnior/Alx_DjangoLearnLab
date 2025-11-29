from rest_framework import serializers
from .models import Book, Author
import datetime

#Book Serializer, Setting the fields to display
class BookSerializer(serializers.ModelSerializer):

  
  
  class Meta:
    model = Book
    fields = ['title', 'author', 'publication_year']

  ##Validation of the 'Publication Year' from the Book Model, to prevent future dates being used as publication date
  def publication_year_Validation(self, data):
    current_year = datetime.date.today().year

    if data > current_year:
      raise serializers.ValidationError("Publication year cannot be in the future!")
    

#Author Serializer, serializing the Author model
class AuthorSerializer(serializers.ModelSerializer):
  # include the author's books using the reverse relation (Book.author)
  books = BookSerializer(many=True, read_only=True)

  class Meta:
    model = Author
    fields = ['id', 'name', 'books']

  