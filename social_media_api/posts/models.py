from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Post(models.Model):
  author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
  title = models.CharField(max_length=200)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta: 
    #This makes sure the latest posts show up first when quering the database
    ordering = ['-created_at']

  def __str__(self):
    return self.title
  
class Like(models.Model):
  #The post that was liked
  post = models.ForeignKey(
      Post,
      on_delete=models.CASCADE,
      related_name='likes' #Allows post.likes.all() to see all the likes
    )
  
  #The user who performed the like
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE,
    related_name='likes_given' #Allows user.likes_given.all() to see all likes they made
  )

  created_at = models.DateTimeField(auto_now_add=True)

  class Meta: 
    #Ensures a user can only like a specific post once
    unique_together = ('user', 'post')
    ordering = ('-created_at',)

  def __str__(self):
    return f"{self.user.username} likes {self.post.title}"

class Comment(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
  author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-created_at']
  
  def __str__(self):
    return f'Comment by {self.author.username} on {self.post.title[:30]}'