from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .pagination import StandardResultsSetPagination
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
  # Base queryset(all posts)
  queryset = Post.objects.all()
  serializer_class = PostSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]

  #1. Enable Search Filter
  filter_backends = [SearchFilter]

  #2. Define which fields to search on
  #Fill in the required fields here based on the task description
  search_fileds = ['title', 'content']

  #Apply the custom pagination class
  pagination_class = StandardResultsSetPagination

  # 4. CRITICAL: We need to override the create method to automatically set the author without relying on the user to submit it.
  def perform_create(self, serializer):
    serializer.save(author=self.request.user)

  #Documentation of Dynamic Content Feed
  @extend_schema(summary='Get personalized content feed.', description="Retrieves a paginated list of posts authored ONLY by users the current authenticated user is following. Results are ordered by most recent first.", responses={200: PostSerializer(many=True), 401: {'description': "Authentication credentials were not provided."}})
  # Dynamic Content Feed
  # Mapped to: /posts/feed/
  @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
  def feed(self,request):
    # 1. Get the list of users the current user follows
    # request.user.following.all() returns a QuerySet of User objects
    followed_users = request.user.following.all()

    # 2. Filter posts to include only those authored by followed users
    # We use the author field's reverse relationship: author__in
    feed_posts = Post.objects.filter(author__in=followed_users).order_by('-created_at')

    # 3. Apply your existing pagination
    page = self.paginate_queryset(feed_posts)
    if page is not None:
      serializer = self.get_serializer(page, many=True)
      return self.get_paginated_response(serializer.data)
    
    # 4. If no pagination is applied (unlikely), serialize and return
    serializer = self.get_serializer(feed_posts, many=True)
    return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
  # This will be refined later for nesting, but for now, we get all comments
  # We will remove the static 'queryset = Comment.objects.all()' - Step 1 of implementing nested comments
  serializer_class = CommentSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]

  #Apply the custom pagination class
  pagination_class = StandardResultsSetPagination

  @extend_schema(
      summary='Creates a comment on a specific post.',
      request=CommentSerializer,
      responses={
        201: CommentSerializer,
        401: {'description': 'User is not Logged in.'}
      },
      description='The author and post fields are set automatically by the server based on the logged-in user and the post_pk in the URL.'
  )


  # Step 2 of implementing nested comments: Override get_queryset to filter comments by post if post_pk is provided
  def get_queryset(self):
    # The 'post_pk' comes from the URL, which the router will provide when nested routing is set up.
    post_pk = self.kwargs.get('post_pk')
    if post_pk:
      #Filter comments to only include those related to the specified post
      return Comment.objects.filter(post_pk=post_pk).order_by('created_at')
    # If no post_pk is provided, return all comments
    return Comment.objects.all().order_by('-created_at')

  # We override perform_create for the same reason: to set the author automatically.
  #Modify perfome_create to automatically set the post ID from the URL if post_pk is provided
  def perform_create(self, serializer):
    post_pk = self.kwargs.get('post_pk')
    #Check if post exists before saving
    try:
      post = Post.objects.get(pk=post_pk)
    except Post.DoesNotExist:
      raise ValidationError({'post': 'Post not found!'})

    # We save the instance, setting both the author and the post
    serializer.save(author=self.request.user, post=post)

  