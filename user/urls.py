from django.urls import path
from . import views

urlpatterns = [
	path("login/", views.home, name="user-login"),
	path("login/forgot_password/get_email/", views.home, name="forgot-password"),
	path("login/forgot_password/email_confirm/", views.home, name="email-confirm"),
	path("login/forgot_password/password_change/", views.home, name="password-change"),
	path("login/forgot_password/password_change/successful/", views.home, name="successful"),

	path("<str:username>/", views.user, name="user"),
]