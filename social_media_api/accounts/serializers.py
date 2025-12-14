from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token

class CustomUserSerializer(serializers.ModelSerializer):
  # 'write_only=True' is crucial for the password! 
    # It ensures the password is accepted for creating the user 
    # but is never sent back in the API response (security first!).
  password = serializers.CharField(write_only=True, max_length=128, required=True, min_length=8)

  class Meta:
    model = CustomUser
    fields = ['id', 'username', 'email', 'bio', 'profile_picture', 'followers', 'password']
    read_only_fields = ['id']
   
  followers_count = serializers.SerializerMethodField()
  
  def get_followers_count(self, obj):
    return obj.followers.count()


  # Override the default 'create' method to correctly hash the password
  def create(self, validated_data):
    password = validated_data.pop('password', None)

    # Use Django's recommended create_user method for secure user creation
    user = get_user_model().objects.create_user(password=password, **validated_data)

    # create an auth token for the newly registered user
    Token.objects.create(user=user)

    return user


class LoginSerializer(serializers.Serializer):
  username = serializers.CharField(required=True)
  password = serializers.CharField(write_only=True, required=True)

  def validate(self, attrs):
    username = attrs.get('username')
    password = attrs.get('password')

    user = authenticate(username=username, password=password)
    if not user:
      raise serializers.ValidationError('Invalid credentials')

    token, _ = Token.objects.get_or_create(user=user)
    return {'token': token.key, 'user': user}