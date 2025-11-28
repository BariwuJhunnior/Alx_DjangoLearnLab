from django.db import models

# Create your models here.

##An Author model object, creating an instance of an Author model with 'name' as it's only parameter
class Author(models.Model):
  name = models.CharField(max_length=50)

#Book Object, creating an instance of a book model with 'title', 'publication_year', 'author - Foreign Key from the Author's Model'
class Book(models.Model):
  title = models.CharField(max_length=200)
  publication_year = models.DateField(auto_now_add=True)
  author = models.ForeignKey(Author, on_delete=models.CASCADE)
