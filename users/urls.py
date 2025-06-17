from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, 
    UserLoginView,
    GoogleLoginView,
    CheckTokenView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login-with-google/', GoogleLoginView.as_view(), name='login_with_google'),
    path('check-token/', CheckTokenView.as_view(), name='check_token'),
]