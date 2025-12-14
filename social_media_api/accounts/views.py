from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import CustomUserSerializer

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