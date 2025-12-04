from django.urls import include,path
from .views import BookList
from .views import BookViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r"Book", BookViewSet)


urlpatterns = [
  #Route for the BookList view (ListAPIView)
    path("books/", BookList.as_view(), name="book-list"),
    # Token authentication endpoint
    path("token/", obtain_auth_token, name="obtain-token"),
    #Include the router URLs for BookViewSet (all CRUD operations)
    path('', include(router.urls))
]
