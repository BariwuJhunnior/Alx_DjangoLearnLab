from rest_framework_nested import routers
from django.urls import path, include
from .views import PostViewSet, CommentViewSet

# 1. Initialize the root router (like DefaultRouter)
router = routers.DefaultRouter()

# Register the top-level resource (Posts)
router.register('posts', PostViewSet, basename='post')

# 2. Create the nested router based on the 'posts' resource
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')

# 3. Register the CommentViewSet under the nested router
posts_router.register(r'comments', CommentViewSet, basename='post-commets')

urlpatterns = [
    # Includes all routes from the root router (/posts/, /posts/{pk}/)
    path('', include(router.urls)),
    # Includes all routes from the nested router (/posts/{post_pk}/comments/, etc.)
    path('', include(posts_router.urls))
]
