from django.urls import include,path
from .views import BookList
from .views import BookViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"Book", BookViewSet)


urlpatterns = [
  #Route for the BookList view (ListAPIView)
    path("books/", BookList.as_view(), name="book-list"),
    #Include the router URLs for BookViewSet (all CRUD operations)
    path('', include(router.urls))
]
