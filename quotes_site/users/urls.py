from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordChangeDoneView, \
    PasswordChangeView, PasswordResetCompleteView, PasswordResetConfirmView
from django.urls import path, reverse_lazy

from . import views

app_name = "users"

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('sign_up/', views.sign_up_view, name="sign_up"),
    path('password-change/', PasswordChangeView.as_view(
        template_name="users/password_change_form.html",
        success_url="users:password-change-done"),
         name="password_change"),

    path('password_change/done/', PasswordChangeDoneView.as_view(
        template_name="users/password_change_done.html"),
         name="password_change_done"),

    path('password-reset/', PasswordResetView.as_view(
        template_name="users/password_reset.html",
        email_template_name="users/password_reset_email.html",
        success_url=reverse_lazy("users:password_reset_done")),
         name="password_reset"),

    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"),
         name="password_reset_done"),

    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name="users/password_reset_confirm.html",
             success_url=reverse_lazy("users:password_reset_complete")),
         name="password_reset_confirm"),

    path('password_reset/complete',
         PasswordResetCompleteView.as_view(
             template_name="users/password_reset_complete.html"),
         name="password_reset_complete")
]
