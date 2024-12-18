from django.urls import path
from django.contrib.auth.views import (
	LoginView,
	LogoutView,
	PasswordResetView,
	PasswordResetConfirmView,
	PasswordResetDoneView,
	PasswordResetCompleteView,
)

from . import views



urlpatterns = [
	path("", views.index, name="operate-index"),
	path("settings/", views.settings, name="operate-settings"),

	# path('login/', LoginView.as_view(template_name='user/login.html'), name='user-login'),
	path("login/", views.user_login, name = "user-login"),
    
	path("login/forgot_password/reset/", PasswordResetView.as_view(
		template_name='app/base_public.html'), 	name="password-reset"),
	path("login/forgot_password/reset/confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(
		template_name='app/base_public.html'), name="password-reset-confirm"),
	path("login/forgot_password/reset/done/", PasswordResetDoneView.as_view(
		template_name='app/base_public.html'), name="password-reset-done"),
	path("login/forgot_password/reset/complete/", PasswordResetCompleteView.as_view(
		template_name='app/base_public.html'), name="password-reset-complete"),
    
	path('logout/', LogoutView.as_view(template_name='app/base_public.html'), name='user-logout'),
]