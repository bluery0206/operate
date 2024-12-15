from django.urls import path
from . import views

urlpatterns = [
	path("", views.index, name="operate-index"),
	path("settings/", views.settings, name="operate-settings")
    

	
]







# from django.urls import path

# # Using django's default
# from django.contrib.auth.views import (
# 	LoginView,
# 	LogoutView,
# 	PasswordResetView,
# 	PasswordResetConfirmView,
# 	PasswordResetDoneView,
# 	PasswordResetCompleteView,
# )
# from .views import user_login

# urlpatterns = [
#     path('logout/', LogoutView.as_view(template_name='user/logout.html'), name='user-logout'),

#     # path('login/', LoginView.as_view(template_name='user/login.html'), name='user-login'),
# 	path("login/", user_login, name = "user-login"),
    
# 	path("login/forgot_password/reset/", PasswordResetView.as_view(
# 			template_name='user/password_reset.html'
# 		), name = "password-reset"
# 	),
# 	path("login/forgot_password/reset/confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(
# 			template_name='user/password_reset_confirm.html'
# 		), name = "password_reset_confirm"
# 	),
# 	path("login/forgot_password/reset/done/", PasswordResetDoneView.as_view(
# 			template_name='user/password_reset_done.html'
# 		), name = "password_reset_done"
# 	),
# 	path("login/forgot_password/reset/complete/", PasswordResetCompleteView.as_view(
# 			template_name='user/password_reset_complete.html'
# 		), name = "password_reset_complete"
# 	),
# ]