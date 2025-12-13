from django.urls import path
from .views import RegisterUserView, UserProfileView
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', ObtainAuthToken.as_view(), name='login'),
    # 3. Profile Management Route (GET/PUT: View and update user profile)
    #    This view will require the user to send their token in the header.
    path('profile/', UserProfileView.as_view(), name='profile'),
]
