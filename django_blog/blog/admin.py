from django.contrib import admin
from .models import Profile, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for Post model.
    """
    list_display = ['title', 'author', 'published_date', 'is_published']
    list_filter = ['is_published', 'published_date', 'author']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'published_date'
    ordering = ['-published_date']
    readonly_fields = ['published_date', 'updated_date']
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'content', 'author')
        }),
        ('Publication Details', {
            'fields': ('is_published', 'published_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for Profile model.
    """
    list_display = ['user', 'location', 'website', 'birth_date']
    list_filter = ['location', 'birth_date']
    search_fields = ['user__username', 'bio', 'location', 'website']
    readonly_fields = ['user']
