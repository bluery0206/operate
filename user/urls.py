from django.urls import path
from . import views

# Using django's default
from django.contrib.auth.views import (
	LoginView,
	LogoutView,
	PasswordResetView,
	PasswordResetConfirmView,
	PasswordResetDoneView,
	PasswordResetCompleteView,
)

urlpatterns = [
    path('login/', LoginView.as_view(template_name='user/login.html'), name='user-login'),
    path('logout/', LogoutView.as_view(template_name='user/logout.html'), name='user-logout'),

	path("login/forgot_password/reset/", PasswordResetView.as_view(
			template_name='user/password_reset.html'
		), name = "password-reset"
	),
	path("login/forgot_password/reset/confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(
			template_name='user/password_reset_confirm.html'
		), name = "password_reset_confirm"
	),
	path("login/forgot_password/reset/done/", PasswordResetDoneView.as_view(
			template_name='user/password_reset_done.html'
		), name = "password_reset_done"
	),
	path("login/forgot_password/reset/complete/", PasswordResetCompleteView.as_view(
			template_name='user/password_reset_complete.html'
		), name = "password_reset_complete"
	),
]