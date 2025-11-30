from django.urls import path
from .views import (RegisterView, MyTokenObtainPairView, 
                    ProfileView,ProfileUpdateView, PasswordUpdateView,
                    PasswordResetRequestView, PasswordResetConfirmView
                    )
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/password/', PasswordUpdateView.as_view(), name='password-update'),

    # Password reset request
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
