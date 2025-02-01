from django.urls import path
from django.contrib.auth.views import (
	LogoutView,
	PasswordResetView,
	PasswordResetDoneView,
	PasswordResetCompleteView,
)


from . import views


urlpatterns = [
	path("", views.index, name="operate-index"),
	path("settings/", views.settings, name="operate-settings"),
	path("settings/update_embeddings/", views.settings_update_embeddings, name="operate-settings-update-embeddings"),
    
	path("facesearch/", views.facesearch, name="facesearch"),

	path("login/", views.user_login, name = "user-login"),
    
	path("login/forgot_password/reset/", PasswordResetView.as_view(template_name='app/user/password_reset.html'),name="password-reset"),
	path("login/forgot_password/reset/confirm/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
	path("login/forgot_password/reset/done/", PasswordResetDoneView.as_view(template_name='app/user/password_reset_done.html'), name="password_reset_done"),
	path("login/forgot_password/reset/complete/", PasswordResetCompleteView.as_view(template_name='app/user/password_reset_complete.html'), name="password_reset_complete"),
    
	path('logout/', LogoutView.as_view(template_name='app/user/logout.html'), name='user-logout'),
    
]