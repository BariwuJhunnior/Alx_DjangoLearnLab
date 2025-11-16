from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, UserProfile, Author, Library, Book, Librarian


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin interface for the CustomUser model.
    Extends Django's default UserAdmin to include custom fields.
    """
    
    # Fields to display in the user list view
    list_display = ('email', 'username', 'first_name', 'last_name', 'date_of_birth', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_photo')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'date_of_birth'),
        }),
    )
    
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    readonly_fields = ('last_login', 'date_joined')


class UserProfileInline(admin.StackedInline):
    """
    Inline admin interface for UserProfile to allow editing 
    user roles alongside user information.
    """
    model = UserProfile
    extra = 0
    fields = ('role',)





class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserProfile model.
    """
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__email', 'user__username')


# Register your models here
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Author)
admin.site.register(Library)
admin.site.register(Book)
admin.site.register(Librarian)
