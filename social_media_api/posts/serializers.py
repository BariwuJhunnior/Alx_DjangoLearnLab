from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class PostSerializer(serializers.ModelSerializer):
  # We use a read-only field for the author
    # This field will be displayed in the API output but cannot be set by the user
  author = serializers.ReadOnlyField(source='author.username')

  # We'll come back to nested comment data later, but for now, let's focus on the basics.


  class Meta:
    model = Post
    fields = ('id', 'author', 'title', 'content', 'created_at', 'updated_at')
    read_only_fields = ('author', 'created_at', 'updated_at')


class CommentSerializer(serializers.ModelSerializer):
  # The author should be displayed as a username, just like the PostSerializer
  author = serializers.ReadOnlyField(source='author.username')

  # We will also include the post field to ensure the comment is linked to the correct post when being created.
  class Meta:
    model = Comment
    fields = ('id', 'post', 'author', 'content', 'created_at', 'updated_at')

    read_only_fields = ('author', 'created_at', 'updated_at')