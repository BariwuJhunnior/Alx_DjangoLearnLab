from django.urls import path, include
from django.contrib.auth import views as auth_views # import built-in views
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.profile_management, name='profile'), # Uses @login_required view

    # --- Built-in Authentication Views (Step 1) ---
    # These views handle the logic but look for specific templates (registration/login.html, etc.)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),

    # Optional: Include Django's default password change/reset views
    path('', include('django.contrib.auth.urls')),
]
