from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Post(models.Model):
    """
    Blog post model for storing user-generated content.
    """
    id = models.AutoField(primary_key=True)  # Explicitly define primary key for type checking
    title = models.CharField(max_length=200, help_text="Title of the blog post")
    content = models.TextField(help_text="Content of the blog post")
    published_date = models.DateTimeField(auto_now_add=True, help_text="Date when the post was published")
    updated_date = models.DateTimeField(auto_now=True, help_text="Date when the post was last updated")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', help_text="Author of the post")
    is_published = models.BooleanField(default=True, help_text="Whether the post is published")
    
    class Meta:
        ordering = ['-published_date']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the URL to access a particular post instance."""
        from django.urls import reverse
        return reverse('post_detail', args=[str(self.id)])
    
    @property
    def content_snippet(self):
        """Return a snippet of the post content for previews."""
        return self.content[:200] + '...' if len(self.content) > 200 else self.content

class Profile(models.Model):
    """
    Extended user profile information.
    This model extends the built-in User model with additional fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, help_text="Upload a profile picture")
    website = models.URLField(blank=True, help_text="Your personal website or blog")
    location = models.CharField(max_length=100, blank=True, help_text="Your location")
    birth_date = models.DateField(blank=True, null=True, help_text="Your date of birth")
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

@receiver(post_save, sender=User)
def create_user_profile(_sender, instance, created, **_kwargs):
    """Create a Profile instance whenever a new User is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(_sender, instance, **_kwargs):
    """Save the Profile instance whenever the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()