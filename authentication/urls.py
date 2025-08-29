from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, ProfileView, LogoutView,
    PasswordChangeView, PasswordResetRequestView,
    PasswordResetConfirmView, AccountDeletionView, UserListView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("account/", AccountDeletionView.as_view(), name="account_deletion"),
    path("users/", UserListView.as_view(), name="user_list"),
]

