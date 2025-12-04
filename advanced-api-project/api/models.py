from django.db import models
from django.contrib.auth.models import User

# Create your models here.

##An Author model object, creating an instance of an Author model with 'name' as it's only parameter
class Author(models.Model):
  name = models.CharField(max_length=50)

#Book Object, creating an instance of a book model with 'title', 'publication_year', 'author - Foreign Key from the Author's Model'
class Book(models.Model):
  title = models.CharField(max_length=200)
  publication_year = models.DateField(null=True, blank=True)
  author = models.ForeignKey(Author, on_delete=models.CASCADE)

  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.title