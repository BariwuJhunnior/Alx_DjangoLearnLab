from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Notification
from .serializers import NotificationSerializer

from drf_spectacular.utils import extend_schema
from .serializers import NotificationSerializer

# Create your views here.
class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  serializer_class = NotificationSerializer
  permission_classes = [IsAuthenticated]

  #Only Show notifications meant for the current user
  def get_queryset(self):
    return Notification.objects.filter(recipient=self.request.user).select_related('actor').order_by('-timestamp')
  
  @extend_schema(
        summary="Fetch User Notifications",
        description="Retrieves a paginated list of all notifications targeted at the authenticated user. Results are ordered by most recent first and are filtered to show only the recipient's notifications.",
        # The response structure is defined by the NotificationSerializer
        responses={
            200: NotificationSerializer(many=True),
            401: {"description": "Authentication credentials were not provided."}
        }
    )
  def list(self, request, *args, **kwargs):
    """
    Overrides the default list method to apply documentation.
    Note: The actual listing logic is handled by mixins.ListModelMixin.
    """
    return super().list(request, *args, **kwargs)
  
  #Documentation for LIKE Action
  @extend_schema(
      summary='Mark All Notifications as Read',
      description='Updates the `is_read` status to `True` for all unread notifications belonging to the authenticated user.',
      request=None, #POST body is empty
      responses= {
        201: {'detail': 'Marked {count} notifications as read.'},
        401: {'detail': 'Authentication credentials were not provided.'}
      }
  )
  #Custom action to mark selected notifications are read
  @action(detail=False, methods=['post'])
  def mark_all_as_read(self, request):
    # Update all unread notifications for the current user
    unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    count = unread_notifications.update(is_read=True)
    return Response({'details': f'Marked {count} notifications as read.'}, status=status.HTTP_200_OK)
