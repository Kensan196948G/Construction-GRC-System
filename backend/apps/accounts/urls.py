"""GRC認証URLルーティング."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import (
    CustomTokenObtainPairView,
    TOTPDisableView,
    TOTPSetupView,
    TOTPVerifyView,
    UserListView,
    UserProfileView,
)

app_name = "accounts"

urlpatterns: list[path] = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("2fa/setup/", TOTPSetupView.as_view(), name="totp-setup"),
    path("2fa/verify/", TOTPVerifyView.as_view(), name="totp-verify"),
    path("2fa/disable/", TOTPDisableView.as_view(), name="totp-disable"),
]
