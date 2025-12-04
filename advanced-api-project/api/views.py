from django.shortcuts import render
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from .models import Book, Author
from .serializers import BookSerializer
from .filters import BookFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework

import rest_framework.filters as filters

# ---------------------------------------------------------------------------
# Book Views (Generic class-based views)
#
# Each view below uses Django REST Framework's generic views to provide
# CRUD behavior for the `Book` model. Where useful we've overridden
# hooks (for example `create`, `perform_create`, `get_queryset`,
# `perform_update`) to illustrate how to extend default behavior and
# to include small conveniences such as returning a `Location` header
# or enabling simple query-parameter filtering.
# ---------------------------------------------------------------------------


class BookCreateView(generics.CreateAPIView):
  """Create a new Book instance.

  - URL: `POST /books/create/`
  - Serializer: `BookSerializer`
  - Permissions: only authenticated users can create (uses
    `permissions.IsAuthenticated`). If you want to allow anonymous
    creation remove/replace the permission class.

  Customizations / hooks:
  - `create()` is overridden to validate the payload, call
    `perform_create()` and include a `Location` header pointing to
    the created object's detail endpoint (if `reverse` succeeds).
  - `perform_create()` calls `serializer.save()` and is the right
    place to attach additional data (for example, `created_by=request.user`).
  """
  queryset = Book.objects.all()
  serializer_class = BookSerializer
  permission_classes = [IsAuthenticated]

  def create(self, request, *args, **kwargs):
    # standard validation + save flow with explicit response headers
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)
    try:
      # include Location header pointing to the resource's detail URL
      detail_url = reverse('book-detail', kwargs={'pk': serializer.instance.pk})
      headers['Location'] = detail_url
    except Exception:
      # if reverse fails for any reason, we still return the payload
      pass
    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

  def perform_create(self, serializer):
    # Place to attach request-specific data: serializer.save(owner=self.request.user)
    serializer.save()


class BookListView(generics.ListAPIView):
  """Return a list of books.

  - URL: `GET /books/`
  - Permissions: read allowed for everyone, modifications require auth
    (controlled on create/update/delete views).

  Custom filtering:
  - Supports query params `?author=<id>` to filter by author id and
    `?title=<text>` for a case-insensitive title substring match.
  """
  queryset = Book.objects.all()
  serializer_class = BookSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]

  #Add DjangoFilterBacked(if you didn't set it globally in the setting.py file)
  #Add SearchFilter to the list of filter backends
  #AddOrderingFilter to the list of filter backends
  filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

  #Connect your custom filter class
  filterset_class = BookFilter

  #Configure the fields the search should check
  search_fields = ['title', 'author']

  #Specify the fields available for ordering
  ordering_fields = ['title', 'author', 'publication_year', 'id']

  #Optional, Set a default sort order if no 'ordering' parameter is provided, results will be ordered by 'title' ascending
  ordering = ['title']

  

  



  def get_queryset(self):
    # lightweight filtering without extra dependencies
    qs = super().get_queryset()
    request = self.request
    author = request.query_params.get('author')
    title = request.query_params.get('title')
    if author:
      qs = qs.filter(author__id=author)
    if title:
      qs = qs.filter(title__icontains=title)
    return qs


class BookDetailView(generics.RetrieveAPIView):
  """Retrieve a single Book by `pk`.

  - URL: `GET /books/<int:pk>/`
  - Permissions: read allowed for everyone (IsAuthenticatedOrReadOnly).
  """
  queryset = Book.objects.all()
  serializer_class = BookSerializer
  permission_classes = [IsAuthenticatedOrReadOnly]


class BookUpdateView(generics.RetrieveUpdateAPIView):
  """Retrieve and update a Book.

  - URL: `PUT/PATCH /books/<int:pk>/update/`
  - Permissions: requires authentication by default here.

  Hooks:
  - `perform_update()` is available to attach extra behavior when
    saving updates (logging, auditing, or setting fields based on
    `request.user`). We keep it simple and call `serializer.save()`.
  """
  queryset = Book.objects.all()
  serializer_class = BookSerializer
  permission_classes = [IsAuthenticated]

  def perform_update(self, serializer):
    serializer.save()


class BookDeleteView(generics.DestroyAPIView):
  """Delete a Book.

  - URL: `DELETE /books/<int:pk>/delete/`
  - Permissions: requires authentication by default here. Replace
    or refine the permission class to restrict deletes to owners/admins.
  """
  queryset = Book.objects.all()
  serializer_class = BookSerializer
  permission_classes = [IsAuthenticated]

