from django.urls import path
from .views import (RegisterView, MyTokenObtainPairView, 
                    ProfileView,ProfileUpdateView, PasswordUpdateView,
                    PasswordResetRequestView, PasswordResetConfirmView,
                    UserListView, TopUsersView, UserDetailView, BadgeListView
                    )
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:id>/", UserDetailView.as_view(), name="user-detail"),
    path('top-users/', TopUsersView.as_view(), name='top-users'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/password/', PasswordUpdateView.as_view(), name='password-update'),

    # Password reset request
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("badges/", BadgeListView.as_view(), name="badges"),

]
