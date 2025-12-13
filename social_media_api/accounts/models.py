from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
  # A short, optional description about the user.
  bio = models.TextField(blank=True, max_length=500)

  # An Optional field for a profile picture
  profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)


  # A Many-to-Many field for following other users.
    # We reference 'self' because a user follows another user.
    # symmetrical=False is key here: if I follow you, it doesn't mean you automatically follow me back.
  followers = models.ManyToManyField(
    'self',
    symmetrical=False,
    related_name='following', 
    blank=True
  )

  #Optional method to get user's full name
  def __str__(self):
    return self.username