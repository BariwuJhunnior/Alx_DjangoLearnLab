# Custom User Model Implementation Guide

## Overview

This document outlines the implementation of a custom user model extending Django's `AbstractUser` with additional fields and a custom manager.

## Changes Made

### Step 1: Custom User Model Implementation (`models.py`)

#### CustomUserManager

A custom user manager class that extends `BaseUserManager` to handle user creation with the new custom fields.

**Key Methods:**

- `create_user(email, password=None, **extra_fields)`: Creates a regular user with email as the unique identifier
  - Validates that email is provided
  - Normalizes the email address
  - Sets the password securely
- `create_superuser(email, password=None, **extra_fields)`: Creates administrative users
  - Enforces `is_staff=True` and `is_superuser=True`
  - Raises `ValueError` if superuser requirements are not met

#### CustomUser Model

Extends Django's `AbstractUser` with additional fields:

**New Fields:**

- `email` (EmailField): Unique email field for authentication
- `date_of_birth` (DateField): User's date of birth (optional)
- `profile_photo` (ImageField): User's profile photo stored in `media/profile_photos/` (optional)

**Configuration:**

- `USERNAME_FIELD = 'email'`: Uses email instead of username for authentication
- `REQUIRED_FIELDS = ['username']`: Username is still required during user creation via `createsuperuser`
- Custom manager: `objects = CustomUserManager()`
- Ordering: By date joined (newest first)

**Helper Method:**

- `get_profile_photo_url()`: Returns the URL of the profile photo or None if not available

---

### Step 2: Settings Configuration (`settings.py`)

Added the following configuration to use the custom user model:

```python
# Custom User Model
AUTH_USER_MODEL = 'relationship_app.CustomUser'

# Media files configuration for profile photos
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Key Points:**

- `AUTH_USER_MODEL`: Points Django to use `CustomUser` from the `relationship_app` app
- `MEDIA_URL` & `MEDIA_ROOT`: Configure media file storage for uploaded profile photos

---

### Step 3: Admin Interface Configuration (`admin.py`)

#### CustomUserAdmin Class

Extends Django's `UserAdmin` to provide comprehensive admin interface for the custom user model.

**Features:**

1. **List Display**: Shows email, username, full name, date of birth, staff status, and active status
2. **Filters**: By staff status, active status, superuser status, and date joined
3. **Search**: Search by email, username, first name, and last name
4. **Fieldsets**: Organized sections for different types of information:
   - Authentication (email, password, username)
   - Personal Info (name, date of birth, profile photo)
   - Permissions (group assignments and permissions)
   - Important Dates (login and join dates)
5. **Add Fieldsets**: Custom form layout when creating new users
6. **Readonly Fields**: `date_joined` and `last_login` are read-only

#### Registered Models

All models are registered with the admin interface:

- `CustomUser`: With custom admin class
- `Author`, `Library`, `Book`, `Librarian`: With basic admin classes

---

## Database Migrations

Before using the custom user model, you must create and apply migrations:

```bash
# Create migrations for the new custom user model
python manage.py makemigrations

# Apply migrations to the database
python manage.py migrate
```

**Important**: If you have existing data, Django may ask you how to handle the existing `auth.User` model during migration. You have options to:

- Delete the old User table
- Keep it separate
- Follow Django's migration prompts

---

## Creating a Superuser

After migrations are applied, create a superuser:

```bash
python manage.py createsuperuser
```

You'll be prompted for:

- Email
- Username
- Password
- Confirm Password
- (Optional) First Name, Last Name, Date of Birth, Profile Photo

---

## Using the Custom User Model in Your Application

### In Models

When creating foreign keys to the user model, use:

```python
from django.conf import settings

class YourModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

### In Views and Code

Access the custom user model:

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a new user
user = User.objects.create_user(
    email='user@example.com',
    username='username',
    password='password123',
    date_of_birth='1990-01-15',
    first_name='John',
    last_name='Doe'
)

# Upload profile photo
from django.core.files import File
with open('path/to/photo.jpg', 'rb') as f:
    user.profile_photo.save('photo.jpg', File(f))
    user.save()
```

### Authentication

Login with email instead of username:

```python
from django.contrib.auth import authenticate

user = authenticate(
    email='user@example.com',
    password='password123'
)
```

---

## Media Files Configuration

The custom user model supports profile photo uploads. Ensure your URL configuration handles media files:

```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... other patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Dependencies

Ensure you have Pillow installed for image field functionality:

```bash
pip install Pillow
```

---

## Benefits of This Implementation

1. **Centralized User Management**: All user-related data is in one model
2. **Email-Based Authentication**: Uses email as the primary identifier
3. **Extensible**: Easy to add more custom fields in the future
4. **Profile Photos**: Built-in support for user profile images
5. **Custom Manager**: Ensures proper handling of custom fields during user creation
6. **Admin Integration**: Full admin interface support with custom fields
7. **Best Practices**: Follows Django's recommended approach for custom user models

---

## Troubleshooting

### "Table does not exist" Error

- Run migrations: `python manage.py migrate`

### "AUTH_USER_MODEL refers to model 'relationship_app.CustomUser' that has not been installed"

- Ensure `'relationship_app'` is in `INSTALLED_APPS` in settings.py

### Profile photo not uploading

- Verify Pillow is installed: `pip install Pillow`
- Check media URL and ROOT configuration in settings.py
- Ensure media directory has write permissions

---

## File Locations

- **Models**: `relationship_app/models.py`
- **Admin Configuration**: `relationship_app/admin.py`
- **Settings**: `LibraryProject/settings.py`
- **Migrations**: `relationship_app/migrations/` (auto-generated)
