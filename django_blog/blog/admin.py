from django.contrib import admin
from .models import Profile, Post, Comment


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model.
    """
    list_display = ['content_preview', 'author', 'post', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'author']
    search_fields = ['content', 'author__username', 'post__title']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('content', 'author', 'post')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """Return a short preview of the comment content."""
        if obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return '(No content)'

# Set short description for admin display after class definition
setattr(CommentAdmin.content_preview, 'short_description', 'Content Preview')
