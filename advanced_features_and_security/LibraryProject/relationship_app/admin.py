from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Author, Library, Book, Librarian


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom ModelAdmin for CustomUser.
    Extends Django's default UserAdmin to include custom fields.
    """
    model = CustomUser
    
    # Fields to display in the list view
    list_display = ('email', 'username', 'first_name', 'last_name', 'date_of_birth', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    
    # Fields to search
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    # Ordering
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
        ('Personal Info', {
            'classes': ('collapse',),
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_photo'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')


@admin.register(CustomUser)
class CustomUserAdminRegistration(CustomUserAdmin):
    """Register CustomUser with admin interface."""
    pass


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'library')
    list_filter = ('library', 'author')
    search_fields = ('title', 'author__name')


@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ('name', 'library')
    search_fields = ('name',)
    list_filter = ('library',)
