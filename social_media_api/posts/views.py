from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from .pagination import StandardResultsSetPagination
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework import status
from django.db import IntegrityError # To catch the unique_together constraint
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

#Helper function to create a notification (we'll implement this logic directly for now)
def create_notification(recipient, actor, verb, target):
  #Get the ContentType of the target object
  target_content_type = ContentType.objects.get_for_model(target)

  Notification.objects.create(
    recipient=recipient,
    actor=actor,
    verb=verb,
    target=target
  )

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
  @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
  def feed(self,request):
    # 1. Get the list of users the current user follows
    # request.user.following.all() returns a QuerySet of User objects
    following_users = request.user.following.all()

    # 2. Filter posts to include only those authored by followed users
    # We use the author field's reverse relationship: author__in
    feed_posts = Post.objects.filter(author__in=following_users).order_by('-created_at')

    # 3. Apply your existing pagination
    page = self.paginate_queryset(feed_posts)
    if page is not None:
      serializer = self.get_serializer(page, many=True)
      return self.get_paginated_response(serializer.data)
    
    # 4. If no pagination is applied (unlikely), serialize and return
    serializer = self.get_serializer(feed_posts, many=True)
    return Response(serializer.data)
  
  #Documentation for LIKE Action
  @extend_schema(
      summary='Like a Post',
      description='Allows an authenticated user to like the specified post(by {pk}). If successfull, generates a notification for the post author.',
      request=None, #POST body is empty
      responses= {
        201: {'detail': 'Post liked successfully.'},
        400: {'detail': 'You have already liked this post' or 'You cannot like you own post.'},
        401: {'detail': 'Authentication credentials were not provided.'}
      }
  )
  # Custom Action 1: LIKE POST
  # Mapped to: /posts/{post_id}/like/ (POST request)
  @action(detail=True, methods=['post'])
  def like(self, request, pk=None):
    #1. Get the post object being liked
    post = self.get_object()
    user = request.user

    #2. Prevent liking your own post
    if post.author == user:
      return Response(
        {'detail': 'You cannot like your own post.'},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    #3. Create the like object
    try:
      Like.objects.create(post=post, user=user)
    except IntegrityError:
      #Handles the unique_together constraint (already liked)
      return Response(
        {'detail': 'You have already liked this post.'},
        status=status.HTTP_400_BAD_REQUEST
      )

    #4. Generate Notification
    #Notify the author of the post (recipient) that the user (actor) liked their post(target)
    create_notification(
      recipient=post.author,
      actor=user,
      verb='liked your post',
      target=post
    )

    return Response({'detail': 'Post like successfully.'}, status=status.HTTP_201_CREATED)
  
  #Documentation for UNLIKE Action
  @extend_schema(
      summary='Unlike a Post',
      description='Allows an authenticated user to remove their like from the specified post(by {pk}).',
      request=None, #POST body is empty
      responses= {
        201: {'detail': 'Post unliked successfully.'},
        400: {'detail': 'You have not liked this post yet.'},
        401: {'detail': 'Authentication credentials were not provided.'}
      }
  )
  # Custom Action 2: UNLIKE POST
  # Mapped to: /posts/{post_id}/unlike/ (POST request)
  @action(detail=True, methods=['post'])
  def unlike(self, request, pk=None):
    #1. Get the post object
    post = self.get_object()
    user = request.user

    #2. Delete the like object
    deleted_count, _ = Like.objects.filter(post=post, user=user).delete()

    if deleted_count == 0:
      return Response(
        {'detail': 'You have not liked this post yet.'},
        status=status.HTTP_400_BAD_REQUEST
      )

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

    comment = serializer.save(author=self.request.user, post=post)

    #Check if commenter is NOT the post author
    if post.author != self.request.user:
      # 3. Generate Notification
      # Recipient is the post author
      # Actor is the commenter (request.user)
      # Target is the comment itself
      create_notification(recipient=post.author, actor=self.request.user, verb='commented on your post', target=comment)

    return Response({'detail': 'Post unliked successfully.'}, status=status.HTTP_200_OK)
