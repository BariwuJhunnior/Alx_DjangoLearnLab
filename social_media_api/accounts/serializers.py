from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model
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

    # Create the user instance/object with the remaining validated data
    user = CustomUser.objects.create(**validated_data)

    #Use set_password to hash the password securely before saving
    if password is not None:
      user.set_password(password)
      user.save()

    return user