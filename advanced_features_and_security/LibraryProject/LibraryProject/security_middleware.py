"""Simple middleware that sets a Content-Security-Policy header.

This avoids adding a dependency on `django-csp`. The policy below is
conservative: only resources from same origin are allowed. Adjust the
`CSP_*` variables in settings.py when you need to allow third-party CDN or
inline scripts/styles (use nonces or hashes instead of allowing `'unsafe-inline'`).
"""
from django.conf import settings


class ContentSecurityPolicyMiddleware:
    """Add a Content-Security-Policy header to each response.

    The middleware reads CSP_DEFAULT_SRC, CSP_SCRIPT_SRC, CSP_STYLE_SRC and
    CSP_IMG_SRC from settings and constructs the header. Values should be
    sequences/tuples of strings (e.g. ("'self'", 'https://cdn.example.com')).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        parts = []

        def join_sources(name, key):
            sources = getattr(settings, key, None)
            if sources:
                parts.append(f"{name} {' '.join(sources)}")

        join_sources('default-src', 'CSP_DEFAULT_SRC')
        join_sources('script-src', 'CSP_SCRIPT_SRC')
        join_sources('style-src', 'CSP_STYLE_SRC')
        join_sources('img-src', 'CSP_IMG_SRC')

        if parts:
            header_value = '; '.join(parts)
            # Do not override if already set elsewhere
            if 'Content-Security-Policy' not in response:
                response['Content-Security-Policy'] = header_value

        return response
