# Security Hardening Notes

This file documents the security hardening changes applied to the project to reduce risk from XSS, CSRF and SQL injection attacks.

1. settings.py changes

- `DEBUG = False` (should be False in production)
- `SECURE_BROWSER_XSS_FILTER = True` enables XSS filter in compatible browsers
- `X_FRAME_OPTIONS = 'DENY'` prevents clickjacking via iframes
- `SECURE_CONTENT_TYPE_NOSNIFF = True` prevents MIME sniffing
- `CSRF_COOKIE_SECURE = True` and `SESSION_COOKIE_SECURE = True` ensure cookies are only sent over HTTPS
- CSP settings: `CSP_DEFAULT_SRC`, `CSP_SCRIPT_SRC`, `CSP_STYLE_SRC`, `CSP_IMG_SRC` defined. A middleware sets `Content-Security-Policy` header.

2. Content Security Policy

- Implemented simple middleware at `LibraryProject/security_middleware.py` which constructs the `Content-Security-Policy` header from settings. This avoids adding a dependency on `django-csp` but you may prefer that package for richer features.

3. CSRF protections in templates

- All form templates added/updated in `relationship_app/templates/relationship_app/` include `{% csrf_token %}`.

4. SQL injection / input handling

- Views now use Django `ModelForm` (`relationship_app/forms.py` -> `BookForm`) and ORM operations (`.save()`, `.objects.create()`), avoiding raw SQL and string formatting for queries.

5. Output escaping

- Templates use the `|escape` filter for user-controllable fields when rendering.

6. How to test

- Run migrations and create a superuser:

```powershell
..\env\Scripts\python.exe manage.py makemigrations
..\env\Scripts\python.exe manage.py migrate
..\env\Scripts\python.exe manage.py createsuperuser
```

- Log in to `/admin/`, create users and assign them to groups (we also add a migration that creates Viewers/Editors/Admins groups for the `Book` model).
- Use the app URLs (e.g. `/relationship_app/`) to exercise create/edit/delete views as users with/without permissions.

7. Notes and next steps

- For production, ensure `ALLOWED_HOSTS` is set to your domain(s) and TLS/HTTPS is configured.
- Consider enabling `SECURE_HSTS_SECONDS` and related HSTS settings when serving exclusively over HTTPS.
- Consider using `django-csp` for nonce-based inline script handling if you need inline scripts/styles.
