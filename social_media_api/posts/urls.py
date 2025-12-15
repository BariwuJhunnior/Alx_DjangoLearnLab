from rest_framework_nested import routers
from django.urls import path, include
from .views import PostViewSet, CommentViewSet

#  Initialize the root router (like DefaultRouter)
router = routers.DefaultRouter()

# Register the top-level resource (Posts)
router.register(r'posts', PostViewSet, basename='post')

#  Create the nested router based on the 'posts' resource
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')

#  Register the CommentViewSet under the nested router
posts_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = [
    # Includes all routes from the root router (/posts/, /posts/{pk}/)
    path('', include(router.urls)),
    # Includes all routes from the nested router (/posts/{post_pk}/comments/, etc.)
    path('', include(posts_router.urls)),
    # Dynamic feed endpoint
    path('posts/feed/', PostViewSet.as_view({'get': 'feed'}), name='post-feed'),
    # Like and Unlike endpoints
    path('posts/<int:pk>/like/', PostViewSet.as_view({'post': 'like'}), name='post-like'),
    path('posts/<int:pk>/unlike/', PostViewSet.as_view({'post': 'unlike'}), name='post-unlike'),
]
