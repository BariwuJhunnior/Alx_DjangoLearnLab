# advanced-api-project — API Views Documentation

This README documents the `Book` views implemented in `api/views.py`, how they are configured, and the custom hooks or settings used to extend their default behavior.

**Overview**

- The API exposes CRUD endpoints for the `Book` model via Django REST Framework generic views.
- Views are implemented in `api/views.py` and routed in `api/urls.py`.

**Endpoints** (as configured in `api/urls.py`)

- `GET  /books/` — List all books (`BookListView`) (supports `?author=<id>` and `?title=<text>` filters)
- `POST /books/create/` — Create a new book (`BookCreateView`)
- `GET  /books/<int:pk>/` — Retrieve a book (`BookDetailView`)
- `PUT/PATCH /books/<int:pk>/update/` — Update a book (`BookUpdateView`)
- `DELETE /books/<int:pk>/delete/` — Delete a book (`BookDeleteView`)

**View configuration and custom behavior**

- `BookCreateView` (subclass of `generics.CreateAPIView`)

  - `serializer_class`: `api.serializers.BookSerializer`
  - `permission_classes`: `IsAuthenticated` (only authenticated users can create)
  - Overrides `create()` to validate input, call `perform_create()`, and add a `Location` header to the response pointing to the created resource's detail URL (if `reverse` succeeds).
  - `perform_create()` calls `serializer.save()` and is the recommended place to attach request-specific data (for example `serializer.save(created_by=self.request.user)`).

- `BookListView` (subclass of `generics.ListAPIView`)

  - `permission_classes`: `IsAuthenticatedOrReadOnly` (anyone can read)
  - Implements `get_queryset()` to provide lightweight query-parameter filtering:
    - `?author=<id>` filters books by author id.
    - `?title=<text>` performs a case-insensitive substring match on the title.
  - This approach avoids adding external filter dependencies for small projects. For more powerful filtering, consider `django-filter` + `DjangoFilterBackend`.

- `BookDetailView` (subclass of `generics.RetrieveAPIView`)

  - Read-only detail retrieval. Uses `IsAuthenticatedOrReadOnly`.

- `BookUpdateView` (subclass of `generics.RetrieveUpdateAPIView`)

  - `permission_classes`: `IsAuthenticated` (requires authentication)
  - `perform_update()` is available for attaching additional behavior when saving updates (e.g., audit logging). Currently calls `serializer.save()`.

- `BookDeleteView` (subclass of `generics.DestroyAPIView`)
  - `permission_classes`: `IsAuthenticated` (requires authentication)
  - For stricter delete rules (only owner/admin), implement a custom permission class and apply it here.

**Custom hooks used**

- `create(self, request, *args, **kwargs)` in `BookCreateView` — to get full control of response headers and to ensure `Location` is returned.
- `perform_create(self, serializer)` in `BookCreateView` — recommended extension point for setting fields from `request`.
- `get_queryset(self)` in `BookListView` — lightweight query-parameter filtering.
- `perform_update(self, serializer)` in `BookUpdateView` — hook to add behavior during updates.

**Notes & recommendations**

- The `BookSerializer` contains a publication-year validation helper. Ensure it uses the DRF field validation hook name `validate_<fieldname>(self, value)` so DRF calls it automatically.
- Consider adding `related_name='books'` to the `Book.author` ForeignKey in `api/models.py`. That makes reverse lookups clearer (use `author.books` instead of `author.book_set`) and lets you remove `source='book_set'` when nesting serializers.
- For more robust filtering and sorting, add `django-filter` and use `filter_backends` + `DjangoFilterBackend`.

**Example curl commands**

```powershell
# List books
curl http://127.0.0.1:8000/api/books/

# Create a book (replace with a valid author id)
curl -X POST http://127.0.0.1:8000/api/books/create/ -H "Content-Type: application/json" -d '{"title":"My Book","publication_year":"2020-01-01","author":1}'

# Retrieve a book
curl http://127.0.0.1:8000/api/books/1/

# Update a book
curl -X PUT http://127.0.0.1:8000/api/books/1/update/ -H "Content-Type: application/json" -d '{"title":"Updated Title","publication_year":"2020-01-01","author":1}'

# Delete a book
curl -X DELETE http://127.0.0.1:8000/api/books/1/delete/
```

**Where to go next**

- Add `path('api/', include('api.urls'))` to the project `advanced_api_project/urls.py` to expose the routes under `/api/`.
- Add unit tests in `api/tests.py` to verify permissions, create/update/delete behavior, and filters.
- If you want, I can implement a custom permission to restrict updates/deletes to object owners or admins.

---

Generated on: 2025-11-28
