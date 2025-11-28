from rest_framework import serializers
from .models import Book, Author
import datetime

#Book Serializer, Setting the fields to display
class BookSerializer(serializers.ModelSerializer):

  
  
  class Meta:
    model = Book
    fields = '__all__'

  ##Validation of the 'Publication Year' from the Book Model, to prevent future dates being used as publication date
  def publication_date_Validation(self, data):
    current_year = datetime.date.today().year

    if data > current_year:
      raise serializers.ValidationError("Publication year cannot be in the future!")
    

#Author Serializer, serializing the Author model
class AuthorSerializer(serializers.ModelSerializer):
  author = serializers.CharField(source='Author.name', read_only=True, many=True)

  class Meta:
    model = Author
    fields = ['id', 'name', 'author']

  