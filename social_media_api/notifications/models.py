from django.db import models
from django.conf import settings
#Required import for GenericForeignKey
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Notification(models.Model):
  #The user who receives the notification
  recipient = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='notifications'
  )

  #The user who triggered the action (e.g., the new follower or the user who liked the post)
  actor = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='actions_made'
  )

  # Text describing the action (e.g., 'followed you', 'liked your post')
  verb = models.CharField(max_length=255)

  # Fields for the Generic Foreign Key (pointing to the object that was acted upon)
  content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField()
  target = GenericForeignKey('content_type', 'object_id')

  #Status and Metadata
  timestamp = models.DateTimeField(auto_now_add=True)
  is_read = models.BooleanField(default=False)

  class Meta: 
    ordering = ('-timestamp',)

  def __str__(self):
    return f"{self.recipient.username}: {self.actor.username} {self.verb} {self.target}"
