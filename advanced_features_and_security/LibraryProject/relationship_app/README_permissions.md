# Permissions and Groups (relationship_app)

This file documents the custom permissions, groups, and how to test them.

Permissions added to `Book` model (codenames):

- `can_view` : View a Book instance
- `can_create`: Create a Book instance
- `can_edit` : Edit a Book instance
- `can_delete`: Delete a Book instance

These codenames are defined in `relationship_app.models.Book.Meta.permissions`.

Groups created by the data migration `0002_create_groups_and_permissions.py`:

- `Viewers`: assigned `can_view`.
- `Editors`: assigned `can_view`, `can_create`, `can_edit`.
- `Admins`: assigned all permissions including `can_delete`.

How to test manually:

1. Run migrations:

```powershell
..\env\Scripts\python manage.py makemigrations
..\env\Scripts\python manage.py migrate
```

2. Create test users and assign them to groups using Django admin (`/admin`).

3. Log in as each user and try the views:

- `book_list` (no special permission required for listing)
- `book_create` requires `relationship_app.can_create`
- `book_edit` requires `relationship_app.can_edit`
- `book_delete` requires `relationship_app.can_delete`

Example decorators used in `relationship_app.views`:

```python
@login_required
@permission_required('relationship_app.can_create', raise_exception=True)
def book_create(...):
    ...
```

Notes:

- The migration creates groups and assigns permissions based on the `Book` content type. If you add or change permissions later, update the migration or create a new one.
- You can further customise group-permission assignment in the admin UI.
