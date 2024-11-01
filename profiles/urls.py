from django.urls import path
from . import views

urlpatterns = [
	path("personnel/", views.personnels, name="profiles-personnels"),
	path("inmates/", views.inmates, name="profiles-inmates"),

	path("profile/<int:pk>/", views.profile, name="profile"),
	path("profile/<int:pk>/edit/", views.profile_update, name="profile-edit"),
]