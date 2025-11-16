from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.core.validators import MinValueValidator

# Create your models here.
class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with additional fields.
    """
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True, 
                                     validators=[MinValueValidator(date(1900, 1, 1))])
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"
    
    def get_age(self):
        """Calculate user's age based on date of birth."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None