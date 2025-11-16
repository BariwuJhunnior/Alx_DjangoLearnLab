from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from datetime import date



from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from .models import Book
from django.urls import reverse


def book_list(request):
    """List available books (no special permission required to view list)."""
    books = Book.objects.select_related('author', 'library').all()
    return render(request, 'relationship_app/book_list.html', {'books': books})


@login_required
@permission_required('relationship_app.can_create', raise_exception=True)
def can_create(request):
    """Simple create view for Book protected by `can_create` permission.

    This is a minimal example — replace with a ModelForm in a real app.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        author_id = request.POST.get('author')
        library_id = request.POST.get('library')
        if title and author_id and library_id:
            Book.objects.create(title=title, author_id=author_id, library_id=library_id)
            return redirect(reverse('relationship_app:book_list'))
    return render(request, 'relationship_app/book_form.html')


@login_required
@permission_required('relationship_app.can_edit', raise_exception=True)
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            book.title = title
            book.save()
            return redirect(reverse('relationship_app:book_list'))
    return render(request, 'relationship_app/book_form.html', {'book': book})


@login_required
@permission_required('relationship_app.can_delete', raise_exception=True)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect(reverse('relationship_app:book_list'))
    return render(request, 'relationship_app/book_confirm_delete.html', {'book': book})


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for CustomUser model that handles creation of 
    regular users and superusers with the new fields.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with email and password.
        """
        if not email:
            raise ValueError('The Email field must be set.')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


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


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Library(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return self.title

    class Meta:
        # Custom permissions for book management
        permissions = (
            ('can_add_book', 'Can add book'),
            ('can_change_book', 'Can change book'),
            ('can_delete_book', 'Can delete book'),
        )

class Librarian(models.Model):
    name = models.CharField(max_length=100)
    library = models.OneToOneField(Library, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# UserProfile to extend the custom user with a role field
class UserProfile(models.Model):
    ADMIN = 'Admin'
    LIBRARIAN = 'Librarian'
    MEMBER = 'Member'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (LIBRARIAN, 'Librarian'),
        (MEMBER, 'Member'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

# Automatically create or update a UserProfile whenever a CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Ensure profile exists; save to trigger updates if needed
        UserProfile.objects.get_or_create(user=instance)
