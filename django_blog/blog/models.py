from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Post(models.Model):
  title = models.CharField(max_length=200)
  content = models.TextField()
  published_date = models.DateTimeField(auto_now_add=True)
  author = models.ForeignKey(User, on_delete=models.CASCADE)

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
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance whenever a new User is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile instance whenever the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()