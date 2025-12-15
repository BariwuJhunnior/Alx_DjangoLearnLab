from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import NotificationViewSet

router = DefaultRouter()

#Register the NotificationViewSet
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('/notifications/', NotificationViewSet.as_view(), name='notifications'),
    path('/posts/<int:pk>/like/', NotificationViewSet.as_view({'notification': 'like'}), name='like'),
    path('/posts/<int:pk>/unlike', NotificationViewSet.as_view({'notification': 'unlike'}),)
]
