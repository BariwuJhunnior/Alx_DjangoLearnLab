from rest_framework import serializers
from .models import Notification
from django.contrib.contenttypes.models import ContentType

class NotificationSerializer(serializers.ModelSerializer):
  #this field displays the target object's model name
  target_type = serializers.SerializerMethodField()

  # This field provides a basic string representation of the target object
  target_object_representation = serializers.CharField(source='target')

  class Meta:
    model = Notification
    fields = [
      'id',
      'actor',
      'verb',
      'timestamp',
      'is_read',
      'target_type',
      'object_id',  #Useful for client-side routing
      'target_object_representation'
    ]

    read_only_fields = fields

  
  def get_target_type(self, obj):
    return obj.content_type.model