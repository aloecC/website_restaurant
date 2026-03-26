from django.contrib.auth import views
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy

from .forms import BerlogaPasswordResetForm, CustomAuthenticationForm
from .views import (
    DeleteProfileView,
    RegisterView,
    UserPasswordChange,
    UserProfileEditView,
    UserProfileView,
    VerifyView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify/", VerifyView.as_view(), name="verify"),
    path(
        "login/",
        LoginView.as_view(template_name="users/login.html", form_class=CustomAuthenticationForm),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="users:login"), name="logout"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("profile/edit/", UserProfileEditView.as_view(), name="edit_profile"),
    path("profile/delete/<str:username>", DeleteProfileView.as_view(), name="delete_profile"),
    path("password-change/", UserPasswordChange.as_view(), name="password_change"),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
