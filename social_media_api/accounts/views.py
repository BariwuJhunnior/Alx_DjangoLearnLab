from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action 
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from drf_spectacular.utils import extend_schema
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification

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


class CustomUserViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
  queryset = CustomUser.objects.all()
  @extend_schema(summary='Follow a specific user.', description="Allows the authenticated user to add the user specified by the ID in the URL to their 'following' list. Requires authentication.", responses={
    200: {'description': 'Successfully followed the user.'},
    400: {'description': 'Cannot follow yourself.'},
    401: {'description': 'Authentication credentials were not provided.'},
    404: {'description': 'User nto found.'},
  })
  # Custom Action 1: FOLLOW
  # Mapped to: /users/{user_id}/follow/
  @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
  def follow(self, request, pk=None):
    # The user to be followed is the one specified in the URL (pk)
    try:
      user_to_follow = self.get_object() #Fetches the user based on the URL's pk
    except:
      return Response({'detail': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)
    
    # The user performing the action is the logged-in user
    follower = request.user

    if follower == user_to_follow:
      return Response({'detail': 'You cannot follow yourself!'}, status=status.HTTP_400_BAD_REQUEST)
    
    #Add the relationship to the 'following' M2M field
    follower.following.add(user_to_follow)

    #Generate Notification
    # Recipient is the person being followed (user_to_follow)
    # Actor is the person who followed (follower)
    # Target is the actor, as the notification is about the new follower
    create_notification(
      recipient=user_to_follow,
      actor=follower,
      verb='started following you',
      target=follower
    )

    return Response({'detail': f'Successfully followed {user_to_follow.username}.'}, status=status.HTTP_200_OK)

  @extend_schema(summary='Unfollow a specific user.', description="Allows the authenticated user to remove the user specified by the ID in the URL from their 'following' list. Requires authentication.", responses={200: {'description': 'Succesfully unfollowed the user.'}, 401: {'description': 'Authentication credentials were not provided.'}, 404: {'description': 'User not found.'}})
  # Custom Action 2: UNFOLLOW
  # Mapped to: /users/{user_id}/unfollow/
  @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
  def unfollow(self, request, pk=None):
    #The user to be unfollowed is the one specified in the URL (pk)
    try:
      user_to_unfollow = self.get_object() #Fetches the user based on the URL's pk
    except:
      return Response({'detail': 'User nto found!'}, status=status.HTTP_404_NOT_FOUND)
    
    #The user performing the action is the logged-in user
    follower = request.user

    #Remove the relationship from the 'following' M2M field
    follower.following.remove(user_to_unfollow)

    return Response({'detail': f'Successfully unfollowed {user_to_unfollow.username}.'}, status=status.HTTP_200_OK)


# Create your views here.
class RegisterUserView(generics.CreateAPIView):
  # This view will use our custom serializer
  serializer_class = CustomUserSerializer

  # Allow any user to access this view (they don't need to be logged in to register)
  permission_classes = (permissions.AllowAny,)

  # Override the create method to also generate a token upon successful registration
  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # This calls the secure create method we defined in the serializer
    self.perform_create(serializer)

    # --- Token Generation ---
    # Get the newly created user instance
    user = serializer.instance

    # Create a new token linked to the user
    token, created = Token.objects.get_or_create(user=user)

    # --- Response ---
    # The API response will contain the user data AND the new token
    return Response({
      'user': serializer.data,
      'token': token.key
    },status=201)

class CustomLoginView(APIView):
    """Custom login view that returns user data along with the token"""
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, *args, **kwargs):
        # Get username and password from request data
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=400)
        
        # Authenticate the user
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)
        
        # Get or create token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data along with token
        return Response({
            'user': CustomUserSerializer(user).data,
            'token': token.key
        })

class UserProfileView(generics.RetrieveUpdateAPIView):
  """
  Allows authenticated users to view (GET) and update (PUT/PATCH) their own profile.
  Requires Token Authentication.
  """
  serializer_class = CustomUserSerializer
  permission_classes = (permissions.IsAuthenticated,)

  # We don't user queryset because we are overriding get_object

  def get_object(self):
    """
      Overrides the default behavior to ensure we ONLY return the currently 
      authenticated user (request.user), regardless of what is in the URL.
    """    
    return self.request.user